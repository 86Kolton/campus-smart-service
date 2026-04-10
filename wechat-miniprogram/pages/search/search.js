const { apiRequest } = require("../../utils/request");
const {
  buildGreetingName,
  formatCompactCount,
  formatGreetingDate,
  getClientDisplayName,
  normalizePostId,
  syncTabBar
} = require("../../utils/ui");

const PREFILL_SEARCH_KEY = "prefill_search_query";

const SEARCH_CATEGORIES = [
  { id: "market", key: "market", name: "二手交易", glyph: "闲", tone: "blue" },
  { id: "course", key: "course", name: "课程评价", glyph: "课", tone: "mint" },
  { id: "canteen", key: "canteen", name: "食堂避雷", glyph: "餐", tone: "sand" },
  { id: "study", key: "study", name: "自习教室", glyph: "习", tone: "pink" }
];

const RANK_HOT_POSTS = [
  { id: "rank-1", postId: "", title: "二手显示器验机建议", heat: "6.2k", keyword: "二手显示器" },
  { id: "rank-2", postId: "", title: "考研自习室插座分布", heat: "5.5k", keyword: "自习室 插座" },
  { id: "rank-3", postId: "", title: "周末校车末班时间", heat: "4.9k", keyword: "校车" }
];

function normalizeSearchItem(item = {}, index = 0) {
  return {
    id: normalizePostId(item.id || `result-${index + 1}`),
    title: String(item.title || "论坛帖子"),
    snippet: String(item.snippet || item.content || item.meta || ""),
    meta: String(item.meta || item.updated_at || "论坛内容"),
    likes: Number(item.likes || 0),
    comments: Number(item.comments || 0)
  };
}

Page({
  data: {
    greetingName: buildGreetingName("赵毅"),
    greetingDate: formatGreetingDate(),
    query: "",
    sort: "hot",
    page: 1,
    pageSize: 10,
    total: 0,
    hasMore: false,
    pageCount: 1,
    results: [],
    recents: [],
    categories: SEARCH_CATEGORIES,
    rankHotPosts: RANK_HOT_POSTS,
    loading: false,
    error: ""
  },

  onShow() {
    const app = getApp();
    syncTabBar(this, 1);
    this.setData({
      greetingDate: formatGreetingDate(),
      greetingName: buildGreetingName(getClientDisplayName("赵毅"))
    });
    app.ensureSession().finally(() => {
      this.setData({
        greetingName: buildGreetingName(getClientDisplayName("赵毅"))
      });
      this.loadRecents();
      this.loadRankHotPosts();
      this.consumePrefillQuery();
    });
  },

  consumePrefillQuery() {
    const text = String(wx.getStorageSync(PREFILL_SEARCH_KEY) || "").trim();
    if (!text) {
      return;
    }
    wx.removeStorageSync(PREFILL_SEARCH_KEY);
    this.setData({ query: text, page: 1 }, () => this.runSearch());
  },

  onInputQuery(event) {
    this.setData({ query: event.detail.value || "" });
  },

  onChangeSort(event) {
    const sort = event.currentTarget.dataset.sort === "latest" ? "latest" : "hot";
    this.setData({ sort, page: 1 });
    if (this.data.query.trim()) {
      this.runSearch();
    }
  },

  async loadRecents() {
    try {
      const data = await apiRequest({ url: "/api/client/search/recent", method: "GET" });
      this.setData({ recents: Array.isArray(data && data.keywords) ? data.keywords.slice(0, 6) : [] });
    } catch (error) {
      this.setData({ recents: [] });
    }
  },

  async loadRankHotPosts() {
    try {
      const data = await apiRequest({
        url: "/api/client/search/posts?q=&sort=hot&page=1&page_size=3",
        method: "GET"
      });
      const items = Array.isArray(data && data.items) ? data.items : [];
      if (!items.length) {
        return;
      }
      const rankHotPosts = items.map((item, index) => {
        const likes = Number(item.likes || 0);
        const comments = Number(item.comments || 0);
        return {
          id: `rank-${index + 1}`,
          postId: normalizePostId(item.id || ""),
          title: String(item.title || `热帖 ${index + 1}`),
          heat: formatCompactCount(Math.max(1, likes + comments) * 120),
          keyword: String(item.title || "")
        };
      });
      this.setData({ rankHotPosts });
    } catch (error) {}
  },

  async saveRecent(keyword) {
    const text = String(keyword || "").trim();
    if (!text) {
      return;
    }
    try {
      await apiRequest({
        url: "/api/client/search/recent",
        method: "POST",
        data: { keyword: text }
      });
    } catch (error) {}
  },

  async runSearch() {
    const q = this.data.query.trim();
    if (!q) {
      wx.showToast({ title: "请输入关键词", icon: "none" });
      return;
    }

    this.setData({ loading: true, error: "" });
    try {
      await this.saveRecent(q);
      const data = await apiRequest({
        url: `/api/client/search/posts?q=${encodeURIComponent(q)}&sort=${encodeURIComponent(this.data.sort)}&page=${this.data.page}&page_size=${this.data.pageSize}`,
        method: "GET"
      });
      const results = Array.isArray(data && data.items) ? data.items.map((item, index) => normalizeSearchItem(item, index)) : [];
      this.setData({
        results,
        total: Number(data && data.total || 0),
        hasMore: Boolean(data && data.has_more),
        pageCount: Math.max(1, Math.ceil(Number(data && data.total || 0) / this.data.pageSize)),
        loading: false
      });
      this.loadRecents();
    } catch (error) {
      this.setData({ loading: false, error: error && error.message || "搜索失败", pageCount: 1 });
    }
  },

  handleSearchTap() {
    this.setData({ page: 1 }, () => this.runSearch());
  },

  handleRecentTap(event) {
    const keyword = event.currentTarget.dataset.keyword || "";
    this.setData({ query: keyword, page: 1 }, () => this.runSearch());
  },

  async clearRecents() {
    try {
      await apiRequest({ url: "/api/client/search/recent", method: "DELETE" });
      this.setData({ recents: [] });
      wx.showToast({ title: "已清空最近搜索", icon: "none" });
    } catch (error) {
      wx.showToast({ title: error && error.message || "清空失败", icon: "none" });
    }
  },

  onTapCategory(event) {
    const key = event.currentTarget.dataset.key || "";
    if (!key) {
      return;
    }
    wx.navigateTo({ url: `/pages/topic/topic?key=${encodeURIComponent(String(key))}` });
  },

  async onTapRankHot(event) {
    const postId = normalizePostId(event.currentTarget.dataset.postId || "");
    const title = String(event.currentTarget.dataset.title || "帖子详情");
    if (postId) {
      this.openPost({ currentTarget: { dataset: { id: postId, title } } });
      return;
    }
    const keyword = String(event.currentTarget.dataset.keyword || "").trim();
    if (!keyword) {
      return;
    }
    try {
      const data = await apiRequest({
        url: `/api/client/search/posts?q=${encodeURIComponent(keyword)}&sort=hot&page=1&page_size=1`,
        method: "GET"
      });
      const item = Array.isArray(data && data.items) && data.items[0] ? data.items[0] : null;
      const nextId = normalizePostId(item && item.id || "");
      if (!nextId) {
        wx.showToast({ title: "未找到原帖", icon: "none" });
        return;
      }
      this.openPost({ currentTarget: { dataset: { id: nextId, title: item.title || title } } });
    } catch (error) {
      wx.showToast({ title: error && error.message || "打开帖子失败", icon: "none" });
    }
  },

  prevPage() {
    if (this.data.page <= 1) {
      return;
    }
    this.setData({ page: this.data.page - 1 }, () => this.runSearch());
  },

  nextPage() {
    if (!this.data.hasMore) {
      return;
    }
    this.setData({ page: this.data.page + 1 }, () => this.runSearch());
  },

  openPost(event) {
    const id = normalizePostId(event.currentTarget.dataset.id);
    const title = event.currentTarget.dataset.title || "帖子详情";
    if (!id) {
      return;
    }
    wx.navigateTo({
      url: `/pages/post/post?id=${encodeURIComponent(id)}&title=${encodeURIComponent(title)}`
    });
  },

  openComposer() {}
});
