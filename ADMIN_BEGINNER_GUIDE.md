# 管理员小白操作指南（新版）

目标：不改代码，直接在网页里完成后台管理、知识库上传、接口配置和基本排错。

## 1. 一键启动后端

在 `D:\桌面\codex工作目录1\毕设\backend` 打开 PowerShell，执行：

```powershell
.\start_backend.ps1
```

如果你要“重启后端”：

```powershell
.\restart_backend.ps1
```

启动成功标志：终端出现 `Application startup complete`。

更简单（推荐）：在项目根目录 `D:\桌面\codex工作目录1\毕设` 执行：

```powershell
.\start_local_stack.ps1 -Restart
```

它会一次性拉起：
- 前端网页：`http://127.0.0.1:5173/index.html`
- 后端接口：`http://127.0.0.1:8000/docs`

停止服务：

```powershell
.\stop_local_stack.ps1
```

## 2. 打开可视化管理台（推荐）

浏览器打开：

```text
https://rag.yyaxx.cc/studio/
```

登录账号：
- ?????? `backend/.env` ?? `ADMIN_USERNAME` / `ADMIN_PASSWORD` ??
- ????????????????

## 3. 你每天会用到的按钮

1. `状态与自检`
- 先点“刷新状态”再点“运行自检”。
- 如果有红色失败项，先处理失败项再上传文档。

2. `接口配置`
- 可直接填 `WECHAT_* / QA_* / EMBEDDING_* / RERANK_* / QDRANT_*` 等。
- 可先点“填充硅基流动推荐”，再补 Key 和微信参数。
- 保存后会写入 `backend/.env`。
- 注意：保存后建议重启后端一次才会完全生效。

3. `知识库管理`
- 新建知识库（例如“教务处知识库”）。
- 可以删除旧知识库。

4. `文档上传`
- 选择目标知识库后上传文件（pdf/docx/txt/md）。
- 上传后去“任务中心”查看是否处理成功。

5. `任务中心`
- 失败任务可直接点“重试”。

6. `问答调试`
- 直接输入问题，检查回答和 citations（引用来源）。

7. `运维动作`
- “高质量回灌”：把高质量帖子同步进知识库。
- “过期清理”：清掉超过 N 天未录用帖子。

## 4. 备用方案（Swagger 文档）

如果你暂时不用可视化台，也可以用：

```text
http://127.0.0.1:8000/docs
```

## 5. 你现在这种前端测试（127.0.0.1:5173）怎么连后端

你当前用户端是 `http://127.0.0.1:5173`，评论/发帖会请求后端 API。

默认规则：
- 本地开发端口（5173/5500）会自动连 `http://127.0.0.1:8000`。

如果你要改为连服务器后端，可直接在地址后加参数：

```text
http://127.0.0.1:5173/?apiBase=https://rag-user.yyaxx.cc
```

当前已部署的服务器后端可用地址：
- `https://rag-user.yyaxx.cc`
- `https://rag.yyaxx.cc/studio/`
- `https://rag.yyaxx.cc/healthz`

## 6. 常见故障

1. 打不开 `127.0.0.1:8000`
- 说明后端没启动，先执行 `.\start_backend.ps1`。

2. 显示 `failed to locate pyvenv.cfg`
- 不要直接用系统 `python`，必须用项目脚本启动。

3. 上传文档后没有结果
- 先看“任务中心”是否失败。
- 失败就点重试，或看错误信息。

4. 配置改了但没生效
- 保存后重启后端：`.\restart_backend.ps1`。

## 7. 安全提醒（教务数据）

- 教务接口必须走后端，不要在前端暴露账号密码。
- 管理员 token 不要发到群里，不要写进公开仓库。
- 生产环境请更换默认管理员账号密码，并启用 HTTPS。

## 8. 微信真实登录（小程序）

后端已支持：
- `POST /api/client/auth/wechat/login`：用 `wx.login` 的 `code` 登录/注册用户。
- `POST /api/client/auth/wechat/bind`：把当前账号绑定微信身份。

你需要在管理台 `接口配置` 填：
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `WECHAT_CODE2SESSION_URL`（默认已填）

开发调试说明：
- `WECHAT_MOCK_ENABLED=true` 时，未配置 AppID/Secret 也能本地演示（不会走真实微信）。
- 上线前请改为 `WECHAT_MOCK_ENABLED=false`，强制走真实微信。

## 9. 硅基流动模型推荐（已按性价比给你设好默认）

- QA：`Qwen/Qwen3.5-9B`（成本适中，效果明显好于超小模型）
- Embedding：`BAAI/bge-m3`（中文检索稳定，1024 维）
- Rerank：`Qwen/Qwen3-Reranker-0.6B`（便宜，足够做深度检索重排）

统一接口基址：
- `https://api.siliconflow.cn/v1`
