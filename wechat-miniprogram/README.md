# 微信小程序客户端（可直接导入）

## 目录
- `app.json` / `app.js` / `app.wxss`
- `pages/home` 首页
- `pages/search` 论坛搜索
- `pages/knowledge` 知识库问答（带来源回溯）
- `pages/profile` 我的
- `pages/post` 帖子详情 + 评论

## 导入步骤（微信开发者工具）
1. 打开微信开发者工具，选择导入项目。
2. 项目目录选择：`D:\桌面\codex工作目录1\毕设\wechat-miniprogram`
3. AppID 可先用测试号（默认 `touristappid`）。
4. 本地联调阶段，可在右上角“详情”里勾选“不校验合法域名”。

## 接口配置
- 默认 API 地址：`https://rag-user.yyaxx.cc`
- 小程序会优先走服务器域名，不再以本地数据作为正式数据源。
- 如果历史缓存里还是旧 IP 或旧域名，启动后会自动迁移到 `https://rag-user.yyaxx.cc`。
- 运行时不再在界面暴露服务地址。

## 小程序后台合法域名配置
在微信公众平台的小程序后台配置：
1. 进入“小程序后台 -> 开发管理 -> 开发设置 -> 服务器域名”。
2. 在 `request 合法域名` 中新增：`https://rag-user.yyaxx.cc`
3. 如果后续要支持图片上传/下载，也把同域名加入 `uploadFile` 和 `downloadFile`。
4. 保存后重新上传体验版，并在真机环境验证接口请求是否命中该域名。

## 登录方式
- 默认使用客户端会话自动登录。
- 也可在“我的”页点击“微信登录/绑定”，通过 `wx.login` 对接 `/api/client/auth/wechat/login`。

## 常用接口
- `/api/client/feed/list`
- `/api/client/feed/comment/create`
- `/api/client/search/posts`
- `/api/client/knowledge/ask`
- `/api/client/profile/summary`
- `/api/client/messages/unread-count`

