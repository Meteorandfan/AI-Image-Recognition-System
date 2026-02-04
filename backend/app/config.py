import os
from pathlib import Path

# 项目根目录（backend）
BASE_DIR = Path(__file__).resolve().parents[1]


# 解析路径，支持相对路径与绝对路径
def resolve_path(value: str | None, default: Path) -> Path:
    if value is None or value.strip() == "":
        path = default
    else:
        path = Path(value)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return path


# 读取环境变量配置
DB_PATH = resolve_path(os.getenv("DB_PATH"), BASE_DIR / "predict_history.db")
UPLOAD_DIR = resolve_path(os.getenv("UPLOAD_DIR"), BASE_DIR / "uploads")

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
