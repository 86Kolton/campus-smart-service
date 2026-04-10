# 校园智服平台

一个面向高校场景的校园综合服务项目，包含用户端 Web、管理后台、FastAPI 后端，以及微信小程序端。项目聚焦校园问答、校务信息检索、校园互动社区、跑腿任务和后台知识库运营。

## 项目组成

- `app.js` + `index.html` + `styles.css`
  - 用户端 Web 页面
- `backend/`
  - FastAPI 后端、管理端接口、RAG 问答链路、测试脚本
- `wechat-miniprogram/`
  - 微信小程序前端
- `e2e/`
  - 端到端测试脚本

## 核心能力

- 校园资讯流、发帖、评论、点赞、收藏
- 跑腿任务发布与互动
- 校园知识库问答，支持检索、引用和深度问答分支
- 后台知识库管理、文档上传、任务追踪、日志查看
- 微信小程序与 Web/后端联动

## 技术栈

- 前端：原生 HTML / CSS / JavaScript
- 后端：FastAPI
- 数据层：SQLite（单机恢复基线），支持扩展到 PostgreSQL
- 异步任务：Celery + Redis
- 检索增强生成：Embedding / Rerank / 外部 QA Provider
- 测试：Pytest + Playwright

## 本地启动

### 1. 用户端

直接打开根目录静态页面，或结合后端接口联调。

### 2. 后端

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Windows 环境也可以直接运行：

```powershell
.\backend\start_backend.ps1
```

### 3. 测试

```powershell
.\backend\run_tests.ps1
```

## 环境变量

后端环境变量模板见：

- `backend/.env.example`

注意：

- 不要把真实 `backend/.env`、数据库文件、上传文件和私有运维资料提交到公开仓库
- 生产环境应关闭 mock 和 demo 数据开关

## 适用场景

- 高校校园服务聚合平台
- 校园知识库问答与信息检索
- 校园社区和二手/求助/跑腿类服务
- 管理端运营与内容治理

## 仓库说明

这个公开仓库保留项目源码、测试代码和示例知识库，不包含生产密钥、生产数据库和私有部署恢复资料。
