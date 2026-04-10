# Contributing

感谢你关注这个项目。

## 提交前建议

1. 先阅读根目录 `README.md` 与 `backend/README.md`
2. 明确改动范围，不要把无关文件一起提交
3. 不要提交任何真实密钥、数据库、上传文件和私有恢复资料

## 分支与提交建议

- 功能开发：`feat/<name>`
- 问题修复：`fix/<name>`
- 文档改动：`docs/<name>`
- 重构整理：`refactor/<name>`

提交信息建议清晰描述意图，例如：

- `feat: add admin config validation`
- `fix: tighten document upload rules`
- `docs: improve open source README`

## 本地验证

在提交前，至少完成你改动相关的验证。

后端验证：

```powershell
.\backend\run_tests.ps1
```

必要时补充：

- 手工验证关键页面
- 管理后台登录与基础操作验证
- 小程序接口链路验证

## Pull Request 建议

- 说明改动目的
- 说明影响范围
- 说明验证方式
- 如果涉及 UI，请附截图或录屏
- 如果涉及配置，请说明新增环境变量

## 安全与数据边界

请勿在公开提交中包含以下内容：

- `backend/.env`
- 数据库文件
- 生产环境地址的敏感访问方式
- 服务器账户密码
- 第三方平台真实 Token / Secret / API Key

安全漏洞请不要直接公开提交，先参考 [SECURITY.md](SECURITY.md)。
