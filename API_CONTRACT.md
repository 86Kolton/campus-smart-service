# 客户端前后端对接接口草案

说明：当前前端已在 `app.js` 的 `API_CONFIG.endpoints` 与 `apiAdapter` 中预留接口，后端可按下列结构对接。

## 1. 首页/帖子流

### GET `/api/client/feed/list`
- query: `filter` (`all|canteen|study|academic`)
- response:
```json
{
  "items": [
    {
      "id": "p-1",
      "category": "study",
      "author": "@清晨图书馆人",
      "avatar": "图书",
      "level": "Lv.4",
      "time": "刚刚",
      "title": "...",
      "content": "...",
      "tags": ["#自习室"],
      "likes": 63,
      "comments": 18,
      "liked": false,
      "commented": false,
      "adopted": true,
      "image_url": "/uploads/posts/20260407120000_xxx.jpg"
    }
  ]
}
```

### POST `/api/client/feed/like`
- body:
```json
{ "post_id": "p-1", "liked": true }
```
- response:
```json
{ "liked": true, "likes": 64 }
```

### GET `/api/client/feed/comments`
- query: `post_id`, `page`, `page_size`
- response:
```json
{
  "page": 1,
  "page_size": 20,
  "total": 52,
  "has_more": true,
  "items": [
    {
      "id": "c-1001",
      "author": "@夜读组",
      "content": "评论内容",
      "time": "刚刚",
      "created_at": "2026-04-06T23:45:00+08:00",
      "parent_comment_id": "c-1000",
      "reply_to_author": "@不儿"
    }
  ]
}
```

### POST `/api/client/feed/comment/create`
- body:
```json
{
  "post_id": "p-1",
  "content": "评论内容",
  "client_id": "local-xxx",
  "reply_to_comment_id": "c-1000",
  "reply_to_author": "@不儿"
}
```
- response:
```json
{
  "id": "c-1002",
  "author": "@我",
  "content": "评论内容",
  "time": "刚刚",
  "created_at": "2026-04-06T23:46:00+08:00",
  "image_url": "/uploads/comments/20260407120100_xxx.jpg"
}
```

### POST `/api/client/feed/post/create`
- body:
```json
{
  "category": "study",
  "title": "A1-307 晚间自习反馈",
  "content": "19:00 后空位较多",
  "tags": ["自习室", "夜间学习"]
}
```
- 限流：同一用户 `30 分钟内最多 3 帖`，超过返回 `429 detail=post_rate_limit_30m_3`

### POST `/api/client/feed/post/create-with-image`
- `multipart/form-data`:
  - `category`, `title`, `content`, `tags`(json字符串或逗号分隔)
  - `image`（<=1MB，png/jpeg/webp/gif）

### POST `/api/client/feed/comment/create-with-image`
- `multipart/form-data`:
  - `post_id`, `content`, `client_id`
  - `reply_to_comment_id`（可选）
  - `reply_to_author`（可选）
  - `image`（<=1MB，png/jpeg/webp/gif）

### GET `/api/client/home/hot-topics`
- response:
```json
{ "items": [{ "id": "hot-1", "title": "二食堂错峰窗口实测", "heat": "9.8k" }] }
```

## 2. 搜索

### GET `/api/client/search/posts`
- query: `q`, `sort` (`hot|latest`), `page`, `page_size`
- response:
```json
{
  "page": 1,
  "page_size": 30,
  "total": 128,
  "has_more": true,
  "items": [
    {
      "id": "m-1",
      "title": "二食堂错峰窗口实测",
      "snippet": "...",
      "content": "...",
      "meta": "食堂 · 当日更新",
      "updated_at": "2026-04-06 19:12",
      "hot_score": 98,
      "likes": 214,
      "comments": 52,
      "keywords": ["食堂", "排队"]
    }
  ]
}
```

### GET `/api/client/search/recent`
- response:
```json
{ "keywords": ["二食堂", "自习室"] }
```

### POST `/api/client/search/recent`
- body:
```json
{ "keyword": "二食堂" }
```

## 3. 知识库问答

### POST `/api/client/knowledge/ask`
- body:
```json
{
  "query": "今晚哪里自习安静？",
  "deep_thinking": true,
  "history": [
    { "role": "user", "text": "..." },
    { "role": "assistant", "text": "..." }
  ]
}
```
- response:
```json
{
  "answer": "推荐 A1-307 与 A2-402。",
  "route": "cloud",
  "route_label": "智能路由 · 向量检索",
  "source": "来源：后端知识库",
  "rerank_used": true,
  "citations": [
    {
      "id": "kb1_doc2_chunk_8",
      "title": "kb1_doc2_chunk_8",
      "jump_url": "/api/admin/documents?kb_id=1",
      "source_type": "document"
    }
  ]
}
```

## 6. 教务预留接口（需 `X-Edu-Session`）

### GET `/api/client/edu/overview`
### GET `/api/client/edu/grades?term=...`
### GET `/api/client/edu/exams`
### GET `/api/client/edu/schedule?week_no=1`
### GET `/api/client/edu/free-classrooms?campus=七一路校区`

- request header:
```http
X-Edu-Session: <session-token>
```
- `X-Edu-Session` 缺失返回 `401 detail=edu_session_required`

## 7. RAG 自进化接口（管理端）

管理端除登录外均需要：
```http
Authorization: Bearer <admin-access-token>
```

### POST `/api/admin/rag/evolution/sync-high-quality-posts`
- 作用：扫描高质量帖子并写入向量库/回退检索缓存
- response 示例：
```json
{
  "synced_posts": 12,
  "skipped_posts": 4,
  "kb_id": 1
}
```

### POST `/api/admin/feed/adopt-comment`
- body:
```json
{
  "post_id": "p-1",
  "comment_id": "c-1",
  "prune_other_comments": true,
  "hard_delete": false
}
```
- 说明：用于“AI已录用”场景，保留录用评论作者信息并处理其余评论（隐藏或硬删）。

### GET `/api/admin/feed/adoptions`
- 说明：查看“AI已录用”沉淀记录（保留帖子标题、贴主、被录用回复作者及内容）。

### POST `/api/admin/maintenance/cleanup-stale-posts?days=7`
- 说明：清理 `7 天未录用` 帖子及其附属评论/图片，防止存储膨胀。
- 当前实现：服务启动后每 6 小时自动执行一次，同步保留手工触发接口。

## 4. 消息中心

### GET `/api/client/messages/unread-count`
- response:
```json
{ "likes_unread": 12, "saved_unread": 3 }
```

### GET `/api/client/messages/likes`
### GET `/api/client/messages/saved`
- response:
```json
{
  "items": [
    {
      "id": "l-1",
      "main": "@xxx 赞了你：...",
      "meta": "2 分钟前 · 来自帖子互动",
      "post_id": "p-1",
      "source_type": "feed"
    }
  ]
}
```

### POST `/api/client/messages/mark-read`
- body:
```json
{ "type": "likes" }
```

`type` 支持：`likes | saved | all`

## 5. 我的页摘要

### GET `/api/client/profile/summary`
- response:
```json
{
  "name": "赵毅",
  "meta": "河北大学 · 软件工程 2022 级",
  "bind_state": "已绑定微信身份",
  "posts": 28,
  "likes": 176
}
```

## 错误码建议
- `401/403`: 鉴权失败（前端已细分提示）
- `408/超时`: 请求超时（前端已细分提示）
- `5xx`: 服务异常（前端已细分提示）

`/api/client/knowledge/ask` 细分错误：
- `408` + `detail=qa_timeout`
- `401/403` + `detail=qa_auth_failed`
- `502` + `detail=qa_provider_5xx` 或 `qa_provider_http_xxx`
- `500` + `detail=qa_pipeline_failed`

## 8. 后台可视化运维（新增）

### 页面入口
- `GET /studio/`
- 用途：类似 RAGFlow 的可视化后台，覆盖登录、配置、知识库、上传、任务、日志、自检。

### DevTools 接口（管理端）
- `GET /api/admin/devtools/status`
- `POST /api/admin/devtools/self-check`
- `GET /api/admin/devtools/config`
- `POST /api/admin/devtools/config`

说明：
- `POST /api/admin/devtools/config` 会写入 `backend/.env`。
- 修改配置后建议重启后端让新配置完全生效。
- Embedding 已支持外部 provider 配置（`EMBEDDING_PROVIDER/BASE_URL/API_KEY/MODEL/DIM/TIMEOUT_SECONDS`）。

