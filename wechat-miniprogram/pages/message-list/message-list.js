const { apiRequest } = require("../../utils/request");
const { normalizePostId } = require("../../utils/ui");

const TYPE_CONFIG = {
  likes: {
    title: "收到的赞",
    brow: "消息中心 · 点赞提醒",
    subtitle: "查看谁赞了你的帖子，并直接回到原帖继续互动。"
  },
  saved: {
    title: "收藏列表",
    brow: "消息中心 · 收藏清单",
    subtitle: "这里集中查看你已经收藏的帖子，方便回看和继续补充。"
  }
};

Page({
  data: {
    type: "likes",
    config: TYPE_CONFIG.likes,
    items: [],
    loading: false,
    error: ""
  },

  onLoad(query) {
    const type = String(query.type || "likes") === "saved" ? "saved" : "likes";
    const config = TYPE_CONFIG[type];
    wx.setNavigationBarTitle({ title: config.title });
    this.setData({ type, config });
  },

  onShow() {
    const app = getApp();
    app.ensureSession().finally(() => {
      this.loadItems();
    });
  },

  onPullDownRefresh() {
    this.loadItems().finally(() => wx.stopPullDownRefresh());
  },

  async loadItems() {
    const safeType = this.data.type === "saved" ? "saved" : "likes";
    const url = safeType === "saved" ? "/api/client/messages/saved" : "/api/client/messages/likes";
    this.setData({ loading: true, error: "" });
    try {
      const data = await apiRequest({ url, method: "GET" });
      this.setData({
        items: Array.isArray(data && data.items) ? data.items : [],
        loading: false
      });
      await apiRequest({
        url: "/api/client/messages/mark-read",
        method: "POST",
        data: { type: safeType }
      });
    } catch (error) {
      this.setData({
        items: [],
        loading: false,
        error: error && error.message || "加载消息失败"
      });
    }
  },

  openPost(event) {
    const id = normalizePostId(event.currentTarget.dataset.id || event.currentTarget.dataset.postId || "");
    const title = event.currentTarget.dataset.title || "帖子详情";
    if (!id) {
      return;
    }
    wx.navigateTo({
      url: `/pages/post/post?id=${encodeURIComponent(id)}&title=${encodeURIComponent(title)}`
    });
  }
});
