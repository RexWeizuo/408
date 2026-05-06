# 408 学习系统

408 计算机考研学习系统，含考纲知识点、选择题刷题、LION 知识点层级问答、艾宾浩斯复习调度。

## 快速启动

### 1. 安装后端依赖（仅需一次）

```bash
pip install -r requirements.txt
```

### 2. 构建前端（仅需一次，或前端代码改动后）

```bash
cd D:\study\408\frontend
npm install
npm run build
```

### 3. 启动（之后每天只需这一步）

```bash
cd D:\study\408\app
uv run uvicorn main:app --port 4081
```

浏览器访问 `http://localhost:4081`

API 文档：`http://localhost:4081/docs`

## 技术栈

- 后端：FastAPI + SQLAlchemy + aiosqlite（异步 SQLite）
- 前端：Vue 3 + Vue Router + Pinia + ECharts + Tailwind CSS
- 数据库：SQLite（`408_study.db` 位于项目根目录）
