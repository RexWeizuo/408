# 408 计算机考研学习系统

408 计算机考研学习系统，含考纲知识点、选择题刷题、LION 知识点层级问答、艾宾浩斯复习调度。

## 快速启动

> **前提：** 四个项目共用 `D:\study\.venv` 虚拟环境。如果还没安装过，先执行一次环境安装：
> ```powershell
> cd D:\study
> uv venv .venv
> # 然后进入各项目的 app 目录，pip install -r requirements.txt 安装依赖
> ```

### 开发模式（推荐，改代码自动刷新）

打开**两个**终端窗口：

**终端 1 — 前端 dev server：**
```powershell
cd D:\study\408\frontend
npm install        # 仅第一次运行
npm run dev        # 启动后访问 http://localhost:4080
```

**终端 2 — 后端：**
```powershell
cd D:\study\408\app
# 激活共用虚拟环境
..\..\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --port 4081 --reload
```

前端会自动把 `/api` 请求代理到后端 `localhost:4081`。

### 生产模式（部署用）

```powershell
# 1. 构建前端（每次改前端代码后执行）
cd D:\study\408\frontend
npm run build

# 2. 启动后端（提供静态前端 + API）
cd D:\study\408\app
..\..\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --port 4081
```

浏览器访问 `http://localhost:4081`

## 端口说明

| 服务 | 端口 |
|------|------|
| 后端 API | 4081 |
| 前端 dev server | 4080（仅开发时用） |

## 技术栈

- 后端：FastAPI + SQLAlchemy + aiosqlite（异步 SQLite）
- 前端：Vue 3 + Vue Router + Pinia + ECharts + Tailwind CSS
- 数据库：SQLite（`408_study.db` 位于项目根目录）

## 项目结构

```
408/
├── app/              # 后端 FastAPI 应用
│   ├── main.py       # 入口
│   ├── config.py     # 配置
│   ├── database.py   # 数据库连接
│   ├── models.py     # ORM 模型
│   ├── schemas.py    # Pydantic 模式
│   └── routes/       # API 路由
├── frontend/         # 前端 Vue 3 项目
├── requirements.txt  # Python 依赖
└── 408_study.db      # SQLite 数据库（运行时生成）
```
