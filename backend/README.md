# Backend 落地骨架（FastAPI + PostgreSQL + RAG）

该目录已经落地以下能力：

- 客户端 API：`/api/client/*`
- 管理端 API：`/api/admin/*`
- RAG 问答链路骨架：`上传 -> 切块 -> embedding -> 检索 -> QA`
- 异步任务骨架：Celery + Redis

## 1. 当前已实现接口

### 1.1 客户端
- `GET /api/client/feed/list`
- `POST /api/client/feed/like`
- `POST /api/client/feed/post/create`
- `POST /api/client/feed/post/create-with-image`
- `GET /api/client/feed/comments`
- `POST /api/client/feed/comment/create`
- `POST /api/client/feed/comment/create-with-image`
- `GET /api/client/home/hot-topics`
- `GET /api/client/search/posts`
- `GET /api/client/search/recent`
- `POST /api/client/search/recent`
- `GET /api/client/messages/unread-count`
- `GET /api/client/messages/likes`
- `GET /api/client/messages/saved`
- `POST /api/client/messages/mark-read`（`likes|saved|all`）
- `GET /api/client/profile/summary`
- `POST /api/client/knowledge/ask`
- 知识库问答支持 `deep_thinking` 参数（开启后才走深度检索/Rerank分支）
- `GET /api/client/edu/overview`（需 `X-Edu-Session`）
- `GET /api/client/edu/grades`（需 `X-Edu-Session`）
- `GET /api/client/edu/exams`（需 `X-Edu-Session`）
- `GET /api/client/edu/schedule`（需 `X-Edu-Session`）
- `GET /api/client/edu/free-classrooms`（需 `X-Edu-Session`）

### 1.2 管理端
- `POST /api/admin/auth/login`
- `GET /api/admin/dashboard/summary`
- `GET /api/admin/kb`
- `POST /api/admin/kb`
- `DELETE /api/admin/kb/{kb_id}`
- `GET /api/admin/documents`
- `POST /api/admin/documents/upload`
- `GET /api/admin/tasks`
- `POST /api/admin/tasks/{task_id}/retry`
- `GET /api/admin/logs/qa`
- `POST /api/admin/rag/evolution/sync-high-quality-posts`
- `POST /api/admin/feed/adopt-comment`
- `GET /api/admin/feed/adoptions`
- `POST /api/admin/maintenance/cleanup-stale-posts`
- `GET /api/admin/devtools/status`
- `POST /api/admin/devtools/self-check`
- `GET /api/admin/devtools/config`
- `POST /api/admin/devtools/config`

除 `/api/admin/auth/login` 外，其余 `/api/admin/*` 均需 `Authorization: Bearer <token>`。

## 2. 数据层现状

### 2.1 已切到 PostgreSQL（第一版）
- 帖子：`PostService`
- 评论：`CommentService`
- 消息：`MessageService`
- 知识库：`KnowledgeBaseService`
- 搜索：`SearchService`（基于 PostgreSQL 帖子数据）
- 文档：`DocumentService`
- 任务：`TaskService`
- QA 日志：`QAService` + `/api/admin/logs/qa`
- 最近搜索词：`RecentSearchKeyword`
- 帖子图片附件：`PostAsset`
- 评论图片附件：`CommentAsset`
- 录用沉淀：`PostAdoption`
- 发帖限流：同一用户 30 分钟最多 3 帖
- 图片约束：帖子/评论图片最大 1MB（png/jpeg/webp/gif）
- 自动清理：服务启动后每 6 小时自动清理一次“7天未录用帖子”

### 2.2 当前仍为本地回退缓存（非主存储）
- RAG fallback chunk 缓存（用于 Qdrant 不可用时兜底）

## 3. 启动方式

### 3.1 Docker（推荐）

1. 复制环境变量：

```bash
cp .env.example .env
```

2. 启动：

```bash
docker compose up --build
```

3. 打开文档：

```text
http://127.0.0.1:8000/docs
```

4. 打开可视化后台：

```text
http://127.0.0.1:8000/studio/
```

### 3.2 本地 Python 直跑

```bash
../.venv/Scripts/python.exe -m pip install -r requirements.txt
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

或使用一键启动脚本（Windows）：

```powershell
.\start_backend.ps1
```

### 3.3 本地测试（Windows）

为避免系统全局 `python` 环境干扰，建议统一用项目根目录 `.venv`：

```powershell
.\run_tests.ps1
```

仅跑 `pytest`（跳过 smoke）：

```powershell
.\run_tests.ps1 -SkipSmoke
```

## 4. 前端联调

当前 `app.js` 已切到真实 API 模式：

- `API_CONFIG.enabled = true`
- `API_CONFIG.baseUrl = 'http://127.0.0.1:8000'`

## 5. RAG 对接占位点

- EMM 切块：`app/rag/chunker/emm_chunker.py`
- Embedding：`app/services/embedding_service.py`
- 向量库：`app/services/qdrant_service.py`
- QA 外部 API：`app/services/qa_provider.py`
- Rerank：`app/services/rerank_provider.py`

Embedding 现已支持两种模式：
- `EMBEDDING_PROVIDER=local_stub`：本地占位向量（离线演示）
- `EMBEDDING_PROVIDER=openai_compatible`：走外部 Embedding API（`/embeddings`）

外部 Embedding 相关环境变量：
- `EMBEDDING_BASE_URL`
- `EMBEDDING_API_KEY`
- `EMBEDDING_MODEL`
- `EMBEDDING_DIM`
- `EMBEDDING_TIMEOUT_SECONDS`

## 6. 注意

- 启动时会自动建表并注入首批种子数据（仅首次）。
- `.env.example` 默认是本地开发配置（SQLite）；`docker-compose` 会自动覆盖为容器内 PostgreSQL 配置。
- 上传文件会落地到 `backend/data/uploads`（Docker 下有卷保留）。
- 小白操作手册见项目根目录：[ADMIN_BEGINNER_GUIDE.md](../ADMIN_BEGINNER_GUIDE.md)
