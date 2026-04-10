# 后端 + RAG 总体规划（单机版，适配 16vCPU / 15GiB / 无GPU）

> 适用项目：校园智慧服务平台（客户端已完成 UI，待后端联调）

## 0. 目标与约束

- 目标：先稳定跑通“可用 RAG + 完整业务 API”，再做性能优化
- 约束：无 GPU、系统盘 50G、当前尚未正式 API
- 你提出的要求：
  - 需要“EMM 切块模型”
  - 需要“正常问答模型（走外部 API）”
  - Embedding 在本机运行
  - 后续可能增加 rerank 模型（可外部 API）

本方案将“切块模型”和“问答模型”完全解耦，便于替换。

---

## 1. 推荐技术栈（可落地）

### 1.1 服务层

- API 网关：Nginx
- 应用后端：FastAPI + Uvicorn/Gunicorn
- 异步任务：Celery + Redis
- 关系库：PostgreSQL
- 向量库：Qdrant
- 对象存储（可选）：MinIO（存原始文档）

### 1.2 RAG 层

- 文档解析：Unstructured / Docling（二选一）
- 切块策略：
  - `EMM-Chunker`（你的切块模型，独立服务）
  - fallback：规则分块 + 语义合并
- 向量模型（本机）：`BAAI/bge-m3`（或轻量中文 embedding）
- 重排模型（后续）：先预留 `rerank_provider`，可接 API
- 问答模型（固定外部 API）：在 `model-gateway` 内做统一封装

---

## 2. 架构设计（分层）

1. 数据接入层：上传/抓取文档、版本管理
2. 预处理层：清洗 -> 切块（EMM）-> 元数据标注
3. 索引层：Embedding -> 写入 Qdrant（带租户/文档ID/chunkID）
4. 检索层：召回（向量+关键词）-> 重排 -> 上下文压缩
5. 生成层：外部问答 API 生成 + 引用片段回传
6. 观测层：日志、指标、链路、告警

---

## 3. “EMM 切块模型 + QA 模型”接口约定

## 3.1 EMM 切块接口（建议）

- POST `/internal/rag/chunk`
- 入参：
```json
{
  "doc_id": "doc_001",
  "text": "长文本...",
  "lang": "zh",
  "max_tokens": 380,
  "overlap_tokens": 60,
  "strategy": "emm"
}
```
- 出参：
```json
{
  "chunks": [
    {"chunk_id":"doc_001_0001","text":"...","token_count":312,"section":"第1章"}
  ]
}
```

## 3.2 QA 生成接口（建议）

- POST `/internal/rag/generate`
- 入参：
```json
{
  "query": "今晚哪里自习安静？",
  "contexts": ["chunk1...","chunk2..."],
  "model": "qa-default",
  "temperature": 0.2
}
```
- 出参：
```json
{
  "answer": "...",
  "citations": [{"chunk_id":"doc_001_0001"}],
  "usage": {"prompt_tokens": 1024, "completion_tokens": 180}
}
```

## 3.3 Rerank 接口（预留，可后接）

- POST `/internal/rag/rerank`
- 入参：
```json
{
  "query": "今晚哪里自习安静？",
  "candidates": [
    {"chunk_id":"doc_001_0001","text":"..."},
    {"chunk_id":"doc_001_0002","text":"..."}
  ],
  "top_k": 8,
  "provider": "none"
}
```
- 出参：
```json
{
  "items": [
    {"chunk_id":"doc_001_0002","score":0.93},
    {"chunk_id":"doc_001_0001","score":0.88}
  ]
}
```

---

## 4. 与现有前端对接范围

你前端已经预留了完整 endpoint 字段，后端按 `API_CONTRACT.md` 对接即可。

关键模块：

1. 首页/帖子：`feed/list`, `feed/like`, `feed/comments`, `feed/comment/create`
2. 搜索：`search/posts`, `search/recent`
3. 消息中心：`messages/unread-count`, `messages/likes`, `messages/saved`, `messages/mark-read`
4. 知识库：`knowledge/ask`
5. 我的：`profile/summary`

---

## 5. 定量容量规划（基于当前机器）

## 5.1 并发建议（首版）

- API 并发：20~60（轻查询）
- RAG 问答并发（外部 API）：8~20
- 本机 Embedding 并发（CPU）：2~6（建议队列化）

## 5.2 数据规模建议

- 首期向量 chunk 目标：5万~20万条
- Qdrant 单机可先支持该规模（按 metadata 精简）
- 预留空间：至少 15G 给向量索引与文档副本

## 5.3 延迟目标（首版 SLA）

- 普通业务 API：P95 < 300ms
- RAG 检索链路：P95 < 800ms
- RAG 完整回答（外部 QA API）：P95 2~6s
- 批量导入阶段（Embedding 本机 CPU）：
  - 常见现象：CPU 拉高，接口延迟抖动
  - 建议策略：离线索引任务与在线 API 分离 worker

## 5.4 “本地 Embedding 会不会卡”定量结论

- 会卡的场景：
  - 你把 Embedding 和在线 API 放同一进程同步跑
  - 一次性大批量入库（例如 >1万 chunk）且不做限流
- 不会明显卡的场景：
  - 使用异步队列（Celery）+ 独立 embedding worker
  - 每批 16~64 条、并发 2~4、峰值错开到夜间
- 在你当前机器（16vCPU/15GiB）下，建议把 Embedding 任务内存上限控制在 6~8GiB，给 API/Qdrant 预留足够余量。

---

## 6. 部署与环境规划

建议采用 `docker compose` 单机编排：

- `nginx`
- `backend-api`
- `worker`
- `redis`
- `postgres`
- `qdrant`
- `model-gateway`（封装 EMM + QA）
- `embedding-worker`（仅本地 embedding）

目录建议：

- `/opt/campus-rag/backend`
- `/opt/campus-rag/data/postgres`
- `/opt/campus-rag/data/qdrant`
- `/opt/campus-rag/data/minio`
- `/opt/campus-rag/backups`

---

## 7. 后期维护方案（你后面长期要做的）

## 7.1 日常运维（日）

1. 检查服务状态（容器/进程）
2. 检查错误日志（5xx、超时、鉴权失败）
3. 检查磁盘与内存

## 7.2 周期运维（周）

1. Postgres 备份验证（可恢复演练）
2. Qdrant 快照备份与回放检查
3. 热门问题命中率与无答案问题复盘
4. 分块质量抽检（EMM 切块是否过碎/过大）

## 7.3 月度优化（月）

1. 重建索引（如 metadata 改动）
2. 评测集回归（准确率、引用正确率、拒答率）
3. 模型版本升级灰度（EMM/Embedding/QA）

---

## 8. 安全与可维护配置（上线前必须）

1. 关闭 root 密码登录，改 SSH key
2. 仅放行必要端口（80/443/22白名单）
3. API 鉴权（JWT + 刷新机制）
4. 限流（IP + 用户）
5. 审计日志（谁在什么时候问了什么）
6. 文档脱敏（手机号/学号等）

---

## 9. 开源参考（优先看这些）

- RAGFlow（可参考其工程化结构）
- LlamaIndex（检索编排与解析组件）
- Qdrant（向量库与快照）
- FlagEmbedding（BGE 系列）

> 注意：当前服务器无 GPU，不建议照搬重型全家桶部署。

---

## 10. 分阶段实施计划

### Phase A（1~2天）

- 完成基础 API（帖子、消息、搜索、个人）
- RAG 打通最小闭环（上传文档 -> 切块 -> 检索 -> 回答）

### Phase B（2~4天）

- 接入 EMM 切块服务
- 接入问答模型网关（外部 API）
- 预留 rerank provider 接口（先置空实现）
- 增加评测与日志看板

### Phase C（1~2天）

- 安全加固 + 备份 + 监控告警
- 压测与参数调优

---

## 11. 你下一步最该先做的三件事

1. 先把服务器 SSH 安全改掉（root 密码登录关闭）
2. 确认外部 QA API 供应商与鉴权方式（模型名、限流、计费）
3. 确认 EMM 模型的具体名称/仓库（我可按你给定模型直接接入）
