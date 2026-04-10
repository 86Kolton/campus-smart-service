const { apiRequest } = require("../../utils/request");
const { normalizePostId } = require("../../utils/ui");

const TOPIC_CONFIG_MAP = {
  market: {
    key: "market",
    brow: "校园集市 · 二手频道",
    title: "二手交易",
    subtitle: "同校转让、验机避坑与低价捡漏，优先看成交经验帖。",
    description: "按热度聚合验机建议、交易提醒和可信卖家反馈。",
    keyword: "二手",
    chips: ["显示器", "台灯", "书籍", "耳机"]
  },
  course: {
    key: "course",
    brow: "选课参考 · 口碑频道",
    title: "课程评价",
    subtitle: "聚合平时分、作业量、点名频率和考试体验。",
    description: "优先展示带有真实课程名、老师名和打分维度的帖子。",
    keyword: "课程评价",
    chips: ["平时分", "作业量", "点名", "考试"]
  },
  canteen: {
    key: "canteen",
    brow: "就餐导航 · 食堂频道",
    title: "食堂避雷",
    subtitle: "看窗口高峰、口味反馈和错峰建议，少走弯路。",
    description: "按时间和窗口类型整理高赞食堂经验贴。",
    keyword: "食堂",
    chips: ["排队", "窗口", "麻辣烫", "清汤"]
  },
  study: {
    key: "study",
    brow: "学习空间 · 自习频道",
    title: "自习教室",
    subtitle: "按安静度、插座、灯光和距离筛选可用学习空间。",
    description: "优先展示晚间自习、空教室和图书馆反馈。",
    keyword: "自习",
    chips: ["空教室", "插座", "图书馆", "晚间"]
  }
};

function normalizeSearchItem(item = {}, index = 0) {
  return {
    id: normalizePostId(item.id || `topic-${index + 1}`),
    title: String(item.title || "专题帖子"),
    snippet: String(item.snippet || item.content || ""),
    meta: String(item.meta || "论坛帖子"),
    likes: Number(item.likes || 0),
    comments: Number(item.comments || 0)
  };
}

function resolveConfig(query = {}) {
  const key = String(query.key || "course").trim();
  const base = TOPIC_CONFIG_MAP[key] || TOPIC_CONFIG_MAP.course;
  return {
    ...base,
    title: String(query.title || base.title),
    subtitle: String(query.subtitle || base.subtitle),
    description: String(query.description || base.description),
    keyword: String(query.keyword || base.keyword),
    chips: base.chips
  };
}

function resolveCategory(configKey = "") {
  if (configKey === "market") return "market";
  if (configKey === "canteen") return "canteen";
  if (configKey === "study") return "study";
  return "academic";
}

Page({
  data: {
    config: resolveConfig({}),
    posts: [],
    loading: false,
    error: "",
    sort: "hot",
    activeKeyword: "",
    page: 1,
    pageSize: 10,
    total: 0,
    hasMore: false,
    pageCount: 1
  },

  onLoad(query) {
    const config = resolveConfig(query || {});
    wx.setNavigationBarTitle({ title: config.title });
    this.setData({
      config,
      activeKeyword: config.keyword,
      page: 1
    });
  },

  onShow() {
    const app = getApp();
    app.ensureSession().finally(() => {
      this.loadPosts(this.data.activeKeyword, 1);
    });
  },

  onPullDownRefresh() {
    this.loadPosts(this.data.activeKeyword, this.data.page).finally(() => wx.stopPullDownRefresh());
  },

  async loadPosts(keyword = this.data.activeKeyword, page = this.data.page) {
    const safeKeyword = String(keyword || this.data.config.keyword || "").trim();
    const safePage = Math.max(1, Number(page) || 1);
    this.setData({
      loading: true,
      error: "",
      activeKeyword: safeKeyword,
      page: safePage
    });

    try {
      const data = await apiRequest({
        url: `/api/client/search/posts?q=${encodeURIComponent(safeKeyword)}&sort=${encodeURIComponent(this.data.sort)}&page=${safePage}&page_size=${this.data.pageSize}`,
        method: "GET"
      });
      const posts = Array.isArray(data && data.items)
        ? data.items.map((item, index) => normalizeSearchItem(item, index))
        : [];
      const total = Math.max(0, Number(data && data.total || 0));
      const pageCount = Math.max(1, Math.ceil(total / this.data.pageSize));
      this.setData({
        posts,
        total,
        hasMore: Boolean(data && data.has_more),
        pageCount,
        loading: false
      });
    } catch (error) {
      this.setData({
        posts: [],
        total: 0,
        hasMore: false,
        pageCount: 1,
        loading: false,
        error: error && error.message || "加载专题失败"
      });
    }
  },

  onTapChip(event) {
    const keyword = event.currentTarget.dataset.keyword || "";
    if (!keyword) {
      return;
    }
    this.loadPosts(keyword, 1);
  },

  onChangeSort(event) {
    const sort = event.currentTarget.dataset.sort === "latest" ? "latest" : "hot";
    this.setData({ sort, page: 1 }, () => this.loadPosts(this.data.activeKeyword, 1));
  },

  prevPage() {
    if (this.data.page <= 1 || this.data.loading) {
      return;
    }
    this.loadPosts(this.data.activeKeyword, this.data.page - 1);
  },

  nextPage() {
    if (!this.data.hasMore || this.data.loading) {
      return;
    }
    this.loadPosts(this.data.activeKeyword, this.data.page + 1);
  },

  openComposer() {
    const config = this.data.config || TOPIC_CONFIG_MAP.course;
    const prefillTags = [config.keyword].concat(config.chips || []).join(", ");
    const draftHint = `当前页面是“${config.title}”，发帖时建议把课程名、地点、时间和真实体验写清楚。`;
    wx.navigateTo({
      url: `/pages/post/post?category=${encodeURIComponent(resolveCategory(config.key))}&prefill_tags=${encodeURIComponent(prefillTags)}&draft_hint=${encodeURIComponent(draftHint)}`
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
