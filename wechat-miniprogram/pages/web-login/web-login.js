const { apiRequest } = require("../../utils/request");

Page({
  data: {
    loading: true,
    error: "",
    code: "",
    expiresIn: 0,
    expiresAt: ""
  },

  onLoad() {
    this.generateCode();
  },

  onPullDownRefresh() {
    this.generateCode().finally(() => wx.stopPullDownRefresh());
  },

  async generateCode() {
    this.setData({ loading: true, error: "" });
    try {
      const app = getApp();
      await app.ensureSession();
      const result = await apiRequest({ url: "/api/client/auth/web-login-code", method: "POST" });
      const code = String((result && result.code) || "").trim();
      if (!code) {
        throw new Error("未获取到登录码");
      }
      this.setData({
        loading: false,
        code,
        expiresIn: Number((result && result.expires_in) || 0),
        expiresAt: String((result && result.expires_at) || "")
      });
    } catch (error) {
      const raw = String((error && error.message) || "");
      const message = raw.includes("wechat_bind_required")
        ? "请先在“我的”页完成微信登录/绑定，再生成网页登录码"
        : (raw || "生成登录码失败");
      this.setData({
        loading: false,
        error: message,
        code: "",
        expiresIn: 0,
        expiresAt: ""
      });
    }
  },

  copyCode() {
    const code = String(this.data.code || "").trim();
    if (!code) {
      wx.showToast({ title: "当前没有可复制的登录码", icon: "none" });
      return;
    }
    wx.setClipboardData({
      data: code,
      success: () => {
        wx.showToast({ title: "登录码已复制", icon: "none" });
      }
    });
  }
});
