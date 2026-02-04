import asyncio
import io
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

# 加载环境变量（必须在读取配置前）
load_dotenv()

from .config import DB_PATH, UPLOAD_DIR
from .db import init_db, save_history, fetch_all_history, delete_history, fetch_stored_name
from .schemas import PredictResult

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("ai-image-app")

app = FastAPI(title="AI 智能图像识别与管理系统")

# 允许跨域访问（开发阶段放开所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 标准化错误响应

def build_error(message: str, code: str):
    return {"message": message, "detail": message, "code": code}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTP 异常：%s | %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error(str(exc.detail), "HTTP_ERROR"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("参数校验失败：%s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            **build_error("参数校验失败", "VALIDATION_ERROR"),
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("服务器内部异常：%s", exc)
    return JSONResponse(
        status_code=500,
        content=build_error("服务器内部错误", "INTERNAL_ERROR"),
    )


@app.on_event("startup")
def on_startup():
    # 启动时初始化数据库与上传目录
    init_db(DB_PATH)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("服务启动，数据库：%s", DB_PATH)
    logger.info("上传目录：%s", UPLOAD_DIR)


@app.get("/")
def root():
    # 根路径提示，避免直接访问时返回 404
    return {
        "message": "后端服务已启动，请访问 /docs 查看接口文档",
        "endpoints": ["POST /predict", "GET /history", "DELETE /history/{id}"],
    }


@app.post("/predict", response_model=PredictResult)
async def predict(file: UploadFile = File(...)):
    # 基础校验：必须上传文件
    if not file:
        raise HTTPException(status_code=400, detail="未上传文件")

    # 基础校验：必须是图片类型
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="文件格式错误，仅支持图片")

    # 读取文件并用 Pillow 验证
    try:
        image_bytes = await file.read()
        # 使用 Pillow 验证图片是否可解析
        Image.open(io.BytesIO(image_bytes)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="图片解析失败，请上传有效图片")

    # 生成存储文件名并写入磁盘
    suffix = Path(file.filename).suffix.lower()
    stored_name = f"{uuid4().hex}{suffix}"
    stored_path = UPLOAD_DIR / stored_name
    stored_path.write_bytes(image_bytes)

    # 模拟深度学习推理耗时
    start_time = time.perf_counter()
    await asyncio.sleep(2)
    duration_ms = (time.perf_counter() - start_time) * 1000

    # 这里模拟模型输出结果
    label = "示例物体"
    confidence = 0.93

    created_at = datetime.now(timezone.utc).isoformat()
    record_id = save_history(DB_PATH, file.filename, stored_name, label, confidence, created_at)

    logger.info(
        "识别完成：filename=%s, label=%s, confidence=%.2f, duration_ms=%.2f",
        file.filename,
        label,
        confidence,
        duration_ms,
    )

    return PredictResult(
        id=record_id,
        filename=file.filename,
        label=label,
        confidence=confidence,
        created_at=created_at,
    )


@app.get("/history", response_model=list[PredictResult])
def get_history():
    return fetch_all_history(DB_PATH)


@app.delete("/history/{record_id}")
def remove_history(record_id: int):
    # 先获取存储文件名
    stored_name = fetch_stored_name(DB_PATH, record_id)
    if stored_name is None:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 删除数据库记录
    if not delete_history(DB_PATH, record_id):
        raise HTTPException(status_code=404, detail="记录不存在")

    # 同步删除本地文件
    if stored_name:
        file_path = UPLOAD_DIR / stored_name
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                logger.warning("删除本地图片失败：%s", file_path)

    return {"message": "删除成功"}
