const { apiRequest, saveTokens, getTokenInfo } = require("../../utils/request");

Page({
  data: {
    loading: false,
    saving: false,
    error: "",
    settings: null,
    formValue: ""
  },

  onShow() {
    this.loadSettings();
  },

  onPullDownRefresh() {
    this.loadSettings().finally(() => wx.stopPullDownRefresh());
  },

  async loadSettings() {
    const app = getApp();
    this.setData({ loading: true, error: "" });
    try {
      await app.ensureSession();
      const data = await apiRequest({ url: "/api/client/profile/settings", method: "GET" });
      this.setData({ loading: false, settings: data || null, formValue: data && data.public_name || "" });
    } catch (error) {
      this.setData({ loading: false, error: error && error.message || "加载失败" });
    }
  },

  onInput(event) {
    this.setData({ formValue: String(event.detail.value || "") });
  },

  async save() {
    const publicName = String(this.data.formValue || "").trim();
    if (!publicName) return wx.showToast({ title: "请输入发言昵称", icon: "none" });
    if (this.data.saving) return;
    this.setData({ saving: true });
    try {
      const data = await apiRequest({ url: "/api/client/profile/public-name", method: "POST", data: { public_name: publicName } });
      const nextPublicName = data && data.public_name || publicName;
      const app = getApp();
      app.globalData.client = { ...(app.globalData.client || {}), publicName: nextPublicName };
      const tokenInfo = getTokenInfo();
      saveTokens({ access_token: tokenInfo.accessToken, refresh_token: tokenInfo.refreshToken, user_id: tokenInfo.userId, username: tokenInfo.username, display_name: tokenInfo.displayName, public_name: nextPublicName });
      this.setData({ saving: false, settings: { ...(this.data.settings || {}), public_name: nextPublicName }, formValue: nextPublicName });
      wx.showToast({ title: "昵称已更新", icon: "success" });
    } catch (error) {
      this.setData({ saving: false });
      wx.showToast({ title: error && error.message || "保存失败", icon: "none" });
    }
  }
});