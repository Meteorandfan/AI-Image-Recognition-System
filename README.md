[README.md](https://github.com/user-attachments/files/25069821/README.md)
# AI 智能图像识别与管理系统（演示项目）

本项目是一个完整的前后端分离演示：
- 后端：FastAPI + SQLite（记录识别历史）
- 前端：Vue 3（Vite + Composition API）+ Element Plus

适合用于：
- 作为 AI 图像识别系统的原型与演示
- 训练前后端协作与 API 规范化能力
- GitHub 作品集展示

## 目录结构

```
backend/
   app/        逻辑代码
   uploads/    图片存储
   main.py     入口文件
frontend/
   src/        源码
   public/     静态资源
```

## 功能清单

后端：
- 图片上传与格式校验
- 模拟推理耗时（2 秒）
- 识别结果与历史记录持久化（SQLite）
- 删除记录时同步删除本地图片
- 统一异常处理与日志记录
- UTC 时间存储

前端：
- 拖拽/点击上传
- 上传前大小与格式校验
- 加载状态提示
- 历史记录表格 + 空状态提示
- 删除二次确认
- 本地时区时间展示

## 运行前提

- Python 3.10+（建议 3.11）
- Node.js 18+（建议 LTS）
- npm 9+

## 后端启动

1. 进入后端目录：

   ```bash
   cd backend
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 启动服务：

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

后端 API：
- `POST /predict`：上传图片并返回识别结果
- `GET /history`：获取历史记录
- `DELETE /history/{id}`：删除指定记录

> SQLite 数据库文件会自动生成在 backend 目录下：`predict_history.db`
> 环境变量配置位于 backend/.env（可调整数据库路径与上传目录）

后端接口文档：
- http://127.0.0.1:8000/docs

## 前端启动

1. 进入前端目录：

   ```bash
   cd frontend
   ```

2. 安装依赖：

   ```bash
   npm install
   ```

3. 启动开发环境：

   ```bash
   npm run dev
   ```

前端默认通过 Vite 代理访问后端：`/api` → `http://127.0.0.1:8000`

## 功能说明

- 支持图片拖拽/点击上传
- 上传后模拟 2 秒推理延迟，展示加载状态
- 展示识别结果与历史记录
- 支持删除历史记录（同时删除本地图片）

## 备注

- 本项目为演示用途，识别结果为模拟返回值
- 若需接入真实模型，可在后端 `POST /predict` 中替换推理逻辑

## 环境变量说明（backend/.env）

- `APP_HOST`：后端监听地址
- `APP_PORT`：后端端口
- `DB_PATH`：数据库文件路径
- `UPLOAD_DIR`：图片存储目录

## 注意事项（重要）

1. 当前识别结果为模拟输出（固定置信度/标签）。要实现“真实识别”，必须接入 AI 模型。
2. 建议使用同一个 Python 环境运行与安装依赖，避免“缺少包”的报错。
3. Windows 下如果 npm 报错 `ts-node/esm`，先执行：`$env:NODE_OPTIONS=""` 再运行 npm。
4. 如果前端端口被占用，Vite 会自动切换到 5174、5175 等，请以终端提示为准。

## 常见问题

- Q：访问后端根路径提示 Not Found？
  - A：已提供 `/` 提示与 `/docs` 文档页，请访问 http://127.0.0.1:8000/docs

- Q：每次识别都是 93%？
  - A：这是演示逻辑，未接入真实模型。


## 一键复现流程（下载方式）

1. 克隆仓库：
   - `git clone <你的仓库地址>`
2. 启动后端：
   - `cd backend`
   - `pip install -r requirements.txt`
   - `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
3. 启动前端：
   - `cd frontend`
   - `npm install`
   - `npm run dev`
