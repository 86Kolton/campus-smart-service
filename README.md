# 校园智服平台

<p align="center">
  <img src="docs/assets/github-hero.svg" alt="校园智服平台 GitHub 展示图" width="100%">
</p>

<p align="center">
  <a href="https://github.com/86Kolton/campus-smart-service/actions/workflows/ci.yml"><img src="https://github.com/86Kolton/campus-smart-service/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/86Kolton/campus-smart-service/releases"><img src="https://img.shields.io/github/v/release/86Kolton/campus-smart-service?color=0f766e" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/License-MIT-0f766e.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Backend-FastAPI-0ea5e9.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/Client-WeChat%20Mini%20Program-22c55e.svg" alt="WeChat Mini Program">
  <img src="https://img.shields.io/badge/Capability-RAG%20%2B%20Campus%20QA-f59e0b.svg" alt="RAG and Campus QA">
</p>

> 面向高校校园场景的综合服务项目，整合 Web 用户端、微信小程序、FastAPI 后端、管理后台 Studio，以及 RAG 知识库问答链路。

## 公开入口

- 版本发布：[GitHub Releases](https://github.com/86Kolton/campus-smart-service/releases)
- 项目概览：[docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md)
- 协作讨论：[GitHub Discussions](https://github.com/86Kolton/campus-smart-service/discussions)

## 项目定位

- 面向高校场景的“校园综合服务 + AI 智能问答”混合型系统
- 主要服务学生用户与内容运营管理员
- Web 用户端、微信小程序和管理后台共用一套 FastAPI 后端与 RAG 能力

## 项目亮点

- 校园社区内容流：发帖、评论、点赞、收藏、消息提醒
- 校园服务场景：跑腿任务、个人主页、搜索与消息列表
- 校园知识问答：文档导入、切块、Embedding、检索、引用回溯
- 管理端运营工具：知识库管理、文档上传、任务追踪、配置调试、日志查看
- 多端协同：Web 用户端、后台管理端、微信小程序共用核心后端

## 机制亮点

- 社区驱动的知识库自进化：高质量帖子可经过筛选、审核、去重和向量化后回灌知识库
- 隐私与智能双轨路由：敏感教务类查询走本地业务链路，校园经验类问答走 RAG 检索与生成
- 混合检索与查询扩展：向量检索、关键词召回、查询改写和重排组合工作
- 多端统一交付：用户端、管理端、小程序共享一套 API 与核心服务

## 系统架构

```mermaid
flowchart LR
    A["Web 用户端"] --> D["FastAPI 后端"]
    B["微信小程序"] --> D
    C["管理后台 / Studio"] --> D
    D --> E["业务服务层"]
    E --> F[("SQLite / PostgreSQL")]
    E --> G[("Redis / Celery")]
    E --> H[("Qdrant / 向量检索")]
    E --> I["Embedding / Rerank / QA Provider"]
```

## 功能地图

| 模块 | 说明 | 关键目录 |
| --- | --- | --- |
| Web 用户端 | 校园社区、搜索、问答、互动页面 | `index.html` `app.js` `styles.css` |
| 后端 API | 用户端接口、管理端接口、认证、任务、服务编排 | `backend/app/` |
| RAG 问答链路 | 文档解析、切块、向量化、检索、问答 | `backend/app/rag/` `backend/app/services/` |
| 管理后台 | 知识库上传、任务重试、配置与日志查看 | `backend/app/static/studio/` |
| 微信小程序 | 校园业务移动端入口 | `wechat-miniprogram/` |
| 自动化测试 | E2E 与接口级回归 | `backend/tests/` `e2e/` |

## 仓库结构

```text
.
|- backend/                  # FastAPI 后端、管理接口、RAG 链路、测试脚本
|- wechat-miniprogram/       # 微信小程序客户端
|- e2e/                      # Playwright 端到端脚本
|- docs/                     # GitHub 展示资源与项目概览
|- index.html                # Web 用户端入口
|- app.js                    # Web 用户端核心逻辑
|- styles.css                # Web 用户端样式
|- CHANGELOG.md              # 版本说明与发布记录
|- CONTRIBUTING.md           # 贡献说明
|- CODE_OF_CONDUCT.md        # 社区行为准则
|- SUPPORT.md                # 使用支持与提问分流
|- SECURITY.md               # 安全披露说明
`- LICENSE                   # 开源许可证
```

## 快速开始

### 1. 准备环境

- Python 3.11+
- Node.js 18+
- Windows PowerShell 或等价终端
- 可选：Redis、Qdrant、外部模型服务

### 2. 克隆并安装依赖

```powershell
git clone https://github.com/86Kolton/campus-smart-service.git
cd campus-smart-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
```

### 3. 配置后端环境变量

```powershell
Copy-Item .\backend\.env.example .\backend\.env
```

然后按需填写：

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `JWT_SECRET`
- `QA_*`
- `EMBEDDING_*`
- `RERANK_*`
- `WECHAT_*`

### 4. 启动后端

```powershell
.\backend\start_backend.ps1
```

或在项目根目录一键拉起本地联调栈：

```powershell
.\start_local_stack.ps1 -Restart
```

### 5. 运行测试

```powershell
.\backend\run_tests.ps1
```

### 6. 导入微信小程序

- 打开微信开发者工具
- 选择 `wechat-miniprogram/`
- 使用自己的 `AppID` 或测试号导入
- 配置合法域名与 API 地址

## 公共仓库边界

这个公开仓库只保留：

- 源代码
- 示例知识库数据
- 开发与测试脚本
- GitHub 展示与协作说明

这个公开仓库不会保留：

- 真实 `backend/.env`
- 生产数据库
- 上传文件与私有运行数据
- 私有运维恢复资料
- 服务器账户密码、API Key、私有证书

## 协作与治理

- 贡献说明：[CONTRIBUTING.md](CONTRIBUTING.md)
- 社区行为准则：[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 使用支持与提问分流：[SUPPORT.md](SUPPORT.md)
- 安全披露流程：[SECURITY.md](SECURITY.md)
- 仓库讨论区：[GitHub Discussions](https://github.com/86Kolton/campus-smart-service/discussions)

## 后续扩展方向

- 增加 Docker 一键开发环境与更完整的生产部署模板
- 扩充 GitHub Actions 自动化测试和依赖更新
- 增加截图、演示 GIF 与版本发布说明
- 将 Web 用户端和管理后台逐步模块化、组件化

## 相关文档

- [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md)
- [backend/README.md](backend/README.md)
- [wechat-miniprogram/README.md](wechat-miniprogram/README.md)
- [ADMIN_BEGINNER_GUIDE.md](ADMIN_BEGINNER_GUIDE.md)
- [API_CONTRACT.md](API_CONTRACT.md)

## 许可证

本项目采用 [MIT License](LICENSE) 开源。
