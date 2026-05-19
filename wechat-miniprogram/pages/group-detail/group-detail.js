const { apiRequest } = require("../../utils/request");
const { normalizePostId } = require("../../utils/ui");

function decodeRouteText(value = "", fallback = "") {
  try {
    return decodeURIComponent(String(value || "")) || fallback;
  } catch (error) {
    return String(value || "") || fallback;
  }
}

function normalizeSearchItem(item = {}, index = 0) {
  return {
    id: normalizePostId(item.id || `group-detail-${index + 1}`),
    title: String(item.title || "相关帖子"),
    snippet: String(item.snippet || item.content || ""),
    meta: String(item.meta || "论坛帖子"),
    likes: Number(item.likes || 0),
    comments: Number(item.comments || 0)
  };
}

Page({
  data: {
    group: {
      id: "",
      title: "跨校小组",
      query: "跨校 互助 组队",
      members: "0",
      online: "0",
      tags: []
    },
    joined: false,
    posts: [],
    loading: false,
    error: ""
  },

  onLoad(query = {}) {
    const tags = decodeRouteText(query.tags || "", "")
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item);
    const group = {
      id: decodeRouteText(query.id || "", ""),
      title: decodeRouteText(query.title || "", "跨校小组"),
      query: decodeRouteText(query.query || "", "跨校 互助 组队"),
      members: decodeRouteText(query.members || "", "0"),
      online: decodeRouteText(query.online || "", "0"),
      tags
    };
    this.setData({
      group,
      joined: String(query.joined || "") === "1"
    });
    wx.setNavigationBarTitle({ title: group.title || "小组详情" });
    if (String(query.joined || "") === "1") {
      setTimeout(() => {
        wx.showToast({ title: "已加入小组", icon: "success" });
      }, 120);
    }
    const app = getApp();
    app.ensureSession().finally(() => {
      this.loadMatches();
    });
  },

  onPullDownRefresh() {
    this.loadMatches().finally(() => wx.stopPullDownRefresh());
  },

  async loadMatches() {
    const group = this.data.group || {};
    const safeQuery = String(group.query || group.title || "跨校 互助 组队").trim();
    this.setData({ loading: true, error: "" });
    try {
      const data = await apiRequest({
        url: `/api/client/search/posts?q=${encodeURIComponent(safeQuery)}&sort=hot&page=1&page_size=10`,
        method: "GET"
      });
      const posts = Array.isArray(data && data.items)
        ? data.items.map((item, index) => normalizeSearchItem(item, index))
        : [];
      this.setData({ posts, loading: false });
    } catch (error) {
      this.setData({
        posts: [],
        loading: false,
        error: error && error.message || "加载小组帖子失败"
      });
    }
  },

  openComposer() {
    const group = this.data.group || {};
    const tags = ["跨校", "互助", "组队"].concat(group.tags || [], group.title || []).filter((item) => item);
    wx.navigateTo({
      url: `/pages/post/post?category=${encodeURIComponent("study")}&prefill_tags=${encodeURIComponent(tags.join(", "))}&draft_hint=${encodeURIComponent("当前页面是跨校小组详情页，发帖时建议写清楚目标、人数、时间安排和联系方式。")}`
    });
  },

  openPost(event) {
    const id = normalizePostId(event.currentTarget.dataset.id || "");
    const title = event.currentTarget.dataset.title || "帖子详情";
    if (!id) {
      return;
    }
    wx.navigateTo({
      url: `/pages/post/post?id=${encodeURIComponent(id)}&title=${encodeURIComponent(title)}`
    });
  }
});
