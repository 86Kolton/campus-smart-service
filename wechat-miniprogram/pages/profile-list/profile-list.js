const { apiRequest } = require("../../utils/request");
const { decodeRouteText, normalizePostId } = require("../../utils/ui");

const MODE_CONFIG = {
  my: {
    title: "我的帖子",
    brow: "个人内容 · 发布记录",
    subtitle: "查看自己发过的校园帖子、跑腿需求和互动状态。",
    emptyText: "你还没有发布过内容，首页发帖和跑腿需求都会出现在这里。"
  },
  liked: {
    title: "我的点赞",
    brow: "个人内容 · 互动记录",
    subtitle: "集中查看你点过赞的帖子，方便回看和继续评论。",
    emptyText: "你还没有点赞过帖子，看到有价值的信息可以先点个赞。"
  }
};

function parseNumericId(rawId = "") {
  const match = String(rawId || "").match(/(\d+)$/);
  return match ? Number(match[1]) : 0;
}

function normalizeFeedItem(item = {}) {
  return {
    ...item,
    id: normalizePostId(item.id || ""),
    source_type: "feed",
    metaLine: `${item.time} · 点赞 ${item.likes} · 评论 ${item.comments}`,
    actionText: "进入原帖",
    locationText: ""
  };
}

function normalizeErrandItem(item = {}) {
  return {
    id: String(item.id || ""),
    title: String(item.title || "跑腿任务"),
    content: String(item.note || `${item.pickup_location || ""} → ${item.destination || ""}`),
    tags: item.tag ? [`#${item.tag}`] : [],
    source_type: "errand",
    metaLine: `${item.status_label || "待处理"} · ${item.reward || ""} · ${item.time || ""}`,
    actionText: "查看任务",
    locationText: `${item.pickup_location || ""} → ${item.destination || ""}`,
    sortNumber: parseNumericId(item.id),
    created_at: item.created_at || ""
  };
}

Page({
  data: {
    mode: "my",
    config: MODE_CONFIG.my,
    items: [],
    loading: false,
    error: ""
  },

  onLoad(query) {
    const mode = String(query.mode || "my") === "liked" ? "liked" : "my";
    const config = MODE_CONFIG[mode];
    wx.setNavigationBarTitle({ title: config.title });
    this.setData({ mode, config });
  },

  onShow() {
    const app = getApp();
    app.ensureSession().finally(() => this.loadItems());
  },

  onPullDownRefresh() {
    this.loadItems().finally(() => wx.stopPullDownRefresh());
  },

  async loadItems() {
    this.setData({ loading: true, error: "" });
    try {
      if (this.data.mode === "liked") {
        const data = await apiRequest({ url: "/api/client/profile/liked-posts", method: "GET" });
        this.setData({ items: Array.isArray(data && data.items) ? data.items.map(normalizeFeedItem) : [], loading: false });
        return;
      }

      const [postsRes, errandsRes] = await Promise.all([
        apiRequest({ url: "/api/client/profile/my-posts", method: "GET" }),
        apiRequest({ url: "/api/client/errands/my", method: "GET" })
      ]);
      const posts = Array.isArray(postsRes && postsRes.items) ? postsRes.items.map(normalizeFeedItem) : [];
      const errands = Array.isArray(errandsRes && errandsRes.items) ? errandsRes.items.map(normalizeErrandItem) : [];
      const items = posts.concat(errands).sort((left, right) => parseNumericId(right.id) - parseNumericId(left.id));
      this.setData({ items, loading: false });
    } catch (error) {
      this.setData({ items: [], loading: false, error: error && error.message || "加载列表失败" });
    }
  },

  retry() {
    this.loadItems();
  },

  openPost(event) {
    const id = String(event.currentTarget.dataset.id || "");
    const sourceType = String(event.currentTarget.dataset.sourceType || "feed");
    const title = decodeRouteText(event.currentTarget.dataset.title || "帖子详情", "帖子详情");
    if (!id) return;
    if (sourceType === "errand") {
      wx.navigateTo({ url: `/pages/errand/errand?focus=${encodeURIComponent(id)}` });
      return;
    }
    wx.navigateTo({ url: `/pages/post/post?id=${encodeURIComponent(normalizePostId(id))}&title=${encodeURIComponent(title)}` });
  }
});