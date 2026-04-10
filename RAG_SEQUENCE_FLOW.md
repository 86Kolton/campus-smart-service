# 知识库上传到问答返回的完整时序图

这份文档回答两个问题：
- 知识库是怎么被处理的
- 用户提问后答案是怎么回来的

## 1. 文档上传链路

```mermaid
sequenceDiagram
    participant Admin as 管理员后台
    participant API as 后端API
    participant DB as PostgreSQL
    participant File as 文件存储
    participant Task as Celery任务
    participant Parser as 文档解析器
    participant Chunker as EMM切块服务
    participant Embed as Embedding服务
    participant Qdrant as Qdrant

    Admin->>API: 上传文档到某知识库
    API->>File: 保存原始文件
    API->>DB: 写入 knowledge_documents(status=uploaded)
    API->>DB: 写入 ingest_tasks(status=pending)
    API-->>Admin: 返回“上传成功，处理中”

    Task->>DB: 任务状态改为 running
    Task->>Parser: 解析 PDF/DOCX/TXT
    Parser-->>Task: 返回纯文本
    Task->>DB: 文档状态改为 parsing/chunking
    Task->>Chunker: 调用 EMM 切块
    Chunker-->>Task: 返回 chunks
    Task->>DB: 更新 chunk 数
    Task->>Embed: 对 chunks 做 embedding
    Embed-->>Task: 返回向量
    Task->>Qdrant: 写入 chunk + vector + metadata
    Task->>DB: 文档状态改为 indexed
    Task->>DB: 任务状态改为 success
```

## 2. 用户问答链路

```mermaid
sequenceDiagram
    participant Client as 前端客户端
    participant API as 后端API
    participant DB as PostgreSQL
    participant Embed as Query Embedding
    participant Qdrant as Qdrant
    participant Rerank as Rerank Provider
    participant QA as 外部QA API

    Client->>API: 提问 /api/client/knowledge/ask
    API->>DB: 记录问题日志(status=pending)
    API->>Embed: 对用户问题做 embedding
    Embed-->>API: 返回 query vector
    API->>Qdrant: 相似检索 topK
    Qdrant-->>API: 返回候选 chunks
    API->>Rerank: 可选，重排候选 chunks
    Rerank-->>API: 返回排序后 chunks
    API->>QA: 发送 query + contexts
    QA-->>API: 返回 answer
    API->>DB: 写 qa_logs(status=success)
    API-->>Client: 返回答案 + 引用片段
```

## 3. 如果没有 rerank

那就走这条：

```text
query -> embedding -> qdrant检索 -> 直接发QA API -> 返回答案
```

系统也能正常工作，只是命中精度可能差一点。

## 4. 失败时会卡在哪

上传链路可能失败点：
- 文档解析失败
- EMM 切块服务失败
- embedding 失败
- Qdrant 写入失败

问答链路可能失败点：
- query embedding 失败
- Qdrant 检索失败
- 外部 QA API 超时
- rerank API 失败

所以后台一定要把失败点显示出来，不然你根本查不动。

## 5. 小白版理解

你可以把上传流程理解成：

1. 先把书放进仓库
2. 把书拆成小段
3. 给每一段编号和做向量
4. 放进检索仓库

把问答流程理解成：

1. 用户提问题
2. 系统先去仓库里找相关段落
3. 找到后交给外部大模型整理成一句完整回答

所以你的服务器主要是在“找资料”，不是在“自己当大模型回答一切”。
