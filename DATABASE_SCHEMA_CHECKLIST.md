# 数据库表设计清单

目标：把业务数据放 PostgreSQL，把向量数据放 Qdrant。

## 1. PostgreSQL 负责什么

PostgreSQL 存：
- 用户
- 帖子
- 评论
- 消息中心
- 知识库
- 文档
- 任务状态
- 问答日志

Qdrant 不存这些业务主数据，只存知识块向量。

## 2. 核心表

## 2.1 `users`

```text
id                  bigint pk
username            varchar
display_name        varchar
password_hash       varchar
role                varchar           -- admin / client
status              varchar           -- active / disabled
created_at          timestamp
updated_at          timestamp
```

作用：管理员和普通用户账号。

## 2.2 `posts`

```text
id                  bigint pk
author_id           bigint
category            varchar
title               varchar
content             text
tags_json           jsonb
likes_count         int
comments_count      int
adopted             boolean
status              varchar           -- published / hidden
created_at          timestamp
updated_at          timestamp
```

作用：首页帖子、搜索帖子来源。

## 2.3 `comments`

```text
id                  bigint pk
post_id             bigint
author_id           bigint
content             text
status              varchar           -- visible / deleted
created_at          timestamp
updated_at          timestamp
```

作用：评论抽屉。

## 2.4 `post_likes`

```text
id                  bigint pk
post_id             bigint
user_id             bigint
created_at          timestamp
```

作用：点赞记录。

## 2.5 `message_notifications`

```text
id                  bigint pk
receiver_user_id    bigint
type                varchar           -- likes / saved
source_post_id      bigint
source_user_id      bigint
content             varchar
is_read             boolean
created_at          timestamp
```

作用：消息中心“收到的赞/马住列表”。

## 2.6 `knowledge_bases`

```text
id                  bigint pk
name                varchar
description         text
status              varchar           -- active / disabled
visibility          varchar           -- private / public
doc_count           int
chunk_count         int
created_by          bigint
created_at          timestamp
updated_at          timestamp
```

作用：一个知识库就是一个集合，比如“教务知识库”“图书馆知识库”。

## 2.7 `knowledge_documents`

```text
id                  bigint pk
kb_id               bigint
file_name           varchar
file_ext            varchar
file_size           bigint
storage_path        varchar
mime_type           varchar
status              varchar           -- uploaded / parsing / chunking / embedding / indexed / failed
chunk_count         int
error_message       text
uploaded_by         bigint
created_at          timestamp
updated_at          timestamp
```

作用：每一个上传文件的状态追踪。

## 2.8 `ingest_tasks`

```text
id                  bigint pk
kb_id               bigint
document_id         bigint
task_type           varchar           -- parse / chunk / embed / index
status              varchar           -- pending / running / success / failed
retry_count         int
error_message       text
started_at          timestamp
finished_at         timestamp
created_at          timestamp
```

作用：异步任务追踪。

## 2.9 `qa_logs`

```text
id                  bigint pk
user_id             bigint
kb_id               bigint
query_text          text
retrieved_chunks    jsonb
rerank_used         boolean
answer_text         text
model_name          varchar
latency_ms          int
status              varchar           -- success / failed
error_message       text
created_at          timestamp
```

作用：看问答记录、做论文分析、排错。

## 3. Qdrant 里存什么

每个 chunk 一条记录，推荐 metadata：

```json
{
  "chunk_id": "kb1_doc8_chunk12",
  "kb_id": 1,
  "document_id": 8,
  "document_name": "教务通知.pdf",
  "section": "选课说明",
  "text": "具体文本内容",
  "token_count": 312
}
```

向量本身也在 Qdrant。

## 4. 表之间关系

```text
users 1 --- n posts
users 1 --- n comments
posts 1 --- n comments
posts 1 --- n post_likes
users 1 --- n message_notifications
knowledge_bases 1 --- n knowledge_documents
knowledge_documents 1 --- n ingest_tasks
knowledge_bases 1 --- n qa_logs
users 1 --- n qa_logs
```

## 5. 你最先建哪些表

第一阶段先建：
- `users`
- `posts`
- `comments`
- `message_notifications`
- `knowledge_bases`
- `knowledge_documents`
- `ingest_tasks`
- `qa_logs`

`post_likes` 可以一起建，但不是最卡主流程的表。

## 6. 小白最容易搞错的点

1. 不要把 chunk 文本全塞 PostgreSQL 再做向量检索。
原因：你后面检索会很痛苦，性能也差。

2. 不要让 Qdrant 成为唯一数据源。
原因：业务信息、任务状态、上传记录还是要放 PostgreSQL。

3. 文档状态一定要单独字段化。
原因：不然你以后根本不知道文档卡在哪一步。
