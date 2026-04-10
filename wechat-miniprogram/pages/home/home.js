const { apiRequest } = require("../../utils/request");
const {
  buildGreetingName,
  formatCompactCount,
  formatGreetingDate,
  getAvatarText,
  getClientDisplayName,
  normalizePostId,
  syncTabBar
} = require("../../utils/ui");

const PREFILL_SEARCH_KEY = "prefill_search_query";

const QUICK_ENTRANCES = [
  { id: "edu", title: "今日课表", sub: "空档与调课提醒", tone: "blue", action: "edu", eduAction: "schedule", todayOnly: "1" },
  { id: "task", title: "跑腿任务", sub: "代取代送快捷入口", tone: "sand", action: "errand" },
  { id: "review", title: "课程评价", sub: "选课避坑与口碑", tone: "mint", action: "topic", topicKey: "course" },
  { id: "group", title: "跨校小组", sub: "热点话题汇总", tone: "pink", action: "groups" }
];

const LIVE_SYNC_MS = 15000;

const FEED_FILTERS = [
  { id: "all", label: "最新" },
  { id: "canteen", label: "食堂" },
  { id: "study", label: "自习" },
  { id: "academic", label: "教务" }
];

const FALLBACK_FEED = [
  {
    id: "p-fallback-1",
    category: "academic",
    author: "@课表教授队",
    avatar: "课表",
    time: "1 小时前",
    title: "周三晚自习教室有临时调度",
    content: "今晚 19:00 后 A2-402 改为临时值班教室，原本准备去的同学建议直接转到 A1-307 或图书馆二层。",
    tags: ["#教务", "#调课提醒"],
    likes: 82,
    comments: 6,
    liked: false,
    adopted: true,
    commentsPreview: ["赵毅：刚从教务群确认，19:10 前会同步到系统。"]
  },
  {
    id: "p-fallback-2",
    category: "study",
    author: "@清晨图书馆人",
    avatar: "清晨",
    time: "34 分钟前",
    title: "A1-307 晚上 8 点后插座充足",
    content: "靠窗一排基本都有电，适合做实验报告和复习。二排会稍微吵一点，但网速更稳。",
    tags: ["#自习", "#空教室"],
    likes: 61,
    comments: 5,
    liked: true,
    adopted: true,
    commentsPreview: ["课表教授队：今晚 21:30 后整体会更安静。"]
  },
  {
    id: "p-fallback-3",
    category: "canteen",
    author: "@二食堂探店组",
    avatar: "二食",
    time: "22 分钟前",
    title: "麻辣烫窗口 12:30 以后明显拥挤",
    content: "今天实测北门清汤窗口 12:35 之后更快，麻辣烫和煲仔饭窗口在 12:10 到 12:30 最堵。",
    tags: ["#食堂避雷", "#排队时间"],
    likes: 43,
    comments: 3,
    liked: false,
    adopted: false,
    commentsPreview: ["清晨图书馆人：北门清汤今天确实快，12:40 基本不用排。"]
  }
];

function normalizeFeedItem(item = {}, index = 0) {
  const tags = Array.isArray(item.tags) ? item.tags.filter(Boolean).map((tag) => String(tag)) : [];
  const likes = Number(item.likes || 0);
  const comments = Number(item.comments || 0);
  const canonicalId = normalizePostId(item.id || `p-fallback-${index + 1}`);
  const knowledgeReviewDecision = String(item.knowledge_review_decision || item.knowledgeReviewDecision || "").toLowerCase();
  const knowledgeReviewReason = String(item.knowledge_review_reason || item.knowledgeReviewReason || "");
  const knowledgeReady = Boolean(item.knowledge_ready || item.knowledgeReady);
  const adopted = Boolean(item.adopted);
  const duplicateRejected = /重复|duplicate/i.test(knowledgeReviewReason);
  const statusBadgeText = knowledgeReady
    ? "AI已采纳"
    : duplicateRejected
      ? "同主题已入库"
      : adopted
        ? "楼主采纳评论"
        : "";
  const statusBadgeTone = knowledgeReady ? "knowledge" : duplicateRejected ? "synced" : adopted ? "adopted" : "";
  return {
    id: canonicalId,
    rawId: String(item.id || canonicalId),
    category: String(item.category || "study"),
    author: String(item.author || "@校园助手"),
    avatar: String(item.avatar || "").trim() || getAvatarText(item.author || ""),
    time: String(item.time || "刚刚"),
    title: String(item.title || "校园帖子"),
    content: String(item.content || item.snippet || ""),
    tags,
    tagText: tags.join(" "),
    likes,
    comments,
    liked: Boolean(item.liked),
    saved: Boolean(item.saved),
    adopted,
    knowledgeReady,
    knowledgeReviewDecision,
    knowledgeReviewReason,
    statusBadgeText,
    statusBadgeTone,
    commentsPreview: Array.isArray(item.comments_preview)
      ? item.comments_preview.filter(Boolean).map((line) => String(line))
      : Array.isArray(item.commentsPreview)
        ? item.commentsPreview.filter(Boolean).map((line) => String(line))
        : [],
    hotScore: likes + comments
  };
}

function buildFallbackFeed() {
  return FALLBACK_FEED.map((item, index) => normalizeFeedItem(item, index));
}

function isValidationArtifact(item = {}) {
  const haystack = [item.title, item.content, item.author, item.tagText].join(" ");
  return /(验证贴\s*[ab]?|图文验证贴|验证跑腿|domain-current|local-current|smoke_[ab]_)/i.test(haystack);
}

function sanitizeFeed(items = []) {
  return items.filter((item) => !isValidationArtifact(item));
}

function buildHotPosts(items = []) {
  const source = Array.isArray(items) && items.length ? items : buildFallbackFeed();
  return source
    .slice()
    .sort((left, right) => right.hotScore - left.hotScore)
    .slice(0, 3)
    .map((item, index) => ({
      id: item.id,
      rank: index + 1,
      title: item.title,
      heat: formatCompactCount(Math.max(1, item.hotScore) * 120)
    }));
}

Page({
  data: {
    greetingName: buildGreetingName("赵毅"),
    greetingDate: formatGreetingDate(),
    loading: false,
    feedBusyId: "",
    serviceStatus: "在线",
    serviceDesc: "社区动态、课程提醒与知识库问答已联动，热点变化会实时反映到推荐与检索结果。",
    hotTopic: "今晚哪里自习最安静？",
    hotPosts: buildHotPosts([]),
    quickEntrances: QUICK_ENTRANCES,
    feedFilters: FEED_FILTERS,
    activeFilter: "all",
    feedItems: buildFallbackFeed(),
    displayFeedItems: buildFallbackFeed()
  },

  onShow() {
    syncTabBar(this, 0);
    this.setData({
      greetingDate: formatGreetingDate(),
      greetingName: buildGreetingName(getClientDisplayName("赵毅"))
    });
    this.startLiveSync();
    this.loadHome();
  },

  onHide() {
    this.stopLiveSync();
  },

  onUnload() {
    this.stopLiveSync();
  },

  onPullDownRefresh() {
    this.loadHome().finally(() => wx.stopPullDownRefresh());
  },

  startLiveSync() {
    this.stopLiveSync();
    this._liveSyncTimer = setInterval(() => {
      if (!this.data.feedBusyId && !this.data.loading) {
        this.loadHome();
      }
    }, LIVE_SYNC_MS);
  },

  stopLiveSync() {
    if (this._liveSyncTimer) {
      clearInterval(this._liveSyncTimer);
      this._liveSyncTimer = null;
    }
  },

  applyFilter(filterName, sourceItems = this.data.feedItems) {
    const safeFilter = FEED_FILTERS.some((item) => item.id === filterName) ? filterName : "all";
    const displayFeedItems = safeFilter === "all"
      ? sourceItems
      : sourceItems.filter((item) => item.category === safeFilter);
    this.setData({ activeFilter: safeFilter, displayFeedItems });
  },

  async loadHome() {
    const app = getApp();
    this.setData({
      loading: true,
      serviceStatus: "在线",
      greetingName: buildGreetingName(getClientDisplayName("赵毅"))
    });

    try {
      await app.ensureSession();
    } catch (error) {}

    try {
      const data = await apiRequest({ url: "/api/client/feed/list?filter=all", method: "GET" });
      const rawItems = Array.isArray(data && data.items)
        ? data.items.map((item, index) => normalizeFeedItem(item, index))
        : [];
      const items = sanitizeFeed(rawItems);
      const nextFeed = items.length ? items : buildFallbackFeed();
      const hotPosts = buildHotPosts(nextFeed);
      this.setData({
        greetingName: buildGreetingName(getClientDisplayName("赵毅")),
        hotPosts,
        hotTopic: hotPosts[0] ? hotPosts[0].title : this.data.hotTopic,
        feedItems: nextFeed,
        loading: false
      });
      this.applyFilter(this.data.activeFilter, nextFeed);
    } catch (error) {
      const fallbackFeed = buildFallbackFeed();
      const hotPosts = buildHotPosts(fallbackFeed);
      this.setData({
        serviceStatus: "离线",
        serviceDesc: "当前接口波动，已切换到示例内容预览。",
        hotPosts,
        hotTopic: hotPosts[0] ? hotPosts[0].title : this.data.hotTopic,
        feedItems: fallbackFeed,
        loading: false
      });
      this.applyFilter(this.data.activeFilter, fallbackFeed);
    }
  },

  onChangeFilter(event) {
    const filterName = event.currentTarget.dataset.filter || "all";
    this.applyFilter(filterName);
  },

  onTapEntrance(event) {
    const { action, keyword, topicKey, eduAction, todayOnly } = event.currentTarget.dataset || {};
    if (action === "search") {
      wx.setStorageSync(PREFILL_SEARCH_KEY, String(keyword || ""));
      wx.switchTab({ url: "/pages/search/search" });
      return;
    }
    if (action === "edu") {
      wx.navigateTo({
        url: `/pages/edu/edu?action=${encodeURIComponent(String(eduAction || "schedule"))}&today=${encodeURIComponent(String(todayOnly || ""))}`
      });
      return;
    }
    if (action === "errand") {
      wx.navigateTo({ url: "/pages/errand/errand" });
      return;
    }
    if (action === "topic") {
      wx.navigateTo({ url: `/pages/topic/topic?key=${encodeURIComponent(String(topicKey || "course"))}` });
      return;
    }
    if (action === "groups") {
      wx.navigateTo({ url: "/pages/groups/groups" });
      return;
    }
    if (action === "profile") {
      wx.switchTab({ url: "/pages/profile/profile" });
      return;
    }
    if (action === "knowledge") {
      wx.switchTab({ url: "/pages/knowledge/knowledge" });
    }
  },

  openComposer() {
    wx.navigateTo({ url: "/pages/post/post" });
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

  openComment(event) {
    this.openPost(event);
  },

  onTapHotPost(event) {
    this.openPost(event);
  },

  async toggleLike(event) {
    const id = normalizePostId(event.currentTarget.dataset.id);
    if (!id || this.data.feedBusyId) {
      return;
    }
    const target = this.data.feedItems.find((item) => item.id === id);
    if (!target) {
      return;
    }

    const nextLiked = !target.liked;
    const nextFeedItems = this.data.feedItems.map((item) => {
      if (item.id !== id) {
        return item;
      }
      const likes = nextLiked ? item.likes + 1 : Math.max(0, item.likes - 1);
      return { ...item, liked: nextLiked, likes, hotScore: likes + item.comments };
    });

    this.setData({ feedBusyId: id, feedItems: nextFeedItems });
    this.applyFilter(this.data.activeFilter, nextFeedItems);
    this.setData({ hotPosts: buildHotPosts(nextFeedItems) });

    try {
      const resp = await apiRequest({
        url: "/api/client/feed/like",
        method: "POST",
        data: { post_id: id, liked: nextLiked }
      });

      const confirmedFeedItems = nextFeedItems.map((item) => {
        if (item.id !== id) {
          return item;
        }
        const likes = Number(resp && resp.likes != null ? resp.likes : item.likes);
        const liked = Boolean(resp && resp.liked);
        return { ...item, liked, likes, hotScore: likes + item.comments };
      });

      this.setData({ feedItems: confirmedFeedItems, feedBusyId: "" });
      this.applyFilter(this.data.activeFilter, confirmedFeedItems);
      this.setData({ hotPosts: buildHotPosts(confirmedFeedItems) });
    } catch (error) {
      this.setData({ feedBusyId: "" });
      this.loadHome();
      wx.showToast({ title: error && error.message || "点赞失败", icon: "none" });
    }
  },

  async toggleSave(event) {
    const id = normalizePostId(event.currentTarget.dataset.id);
    if (!id || this.data.feedBusyId) {
      return;
    }
    const target = this.data.feedItems.find((item) => item.id === id);
    if (!target) {
      return;
    }

    const nextSaved = !target.saved;
    const nextFeedItems = this.data.feedItems.map((item) => {
      if (item.id !== id) {
        return item;
      }
      return { ...item, saved: nextSaved };
    });

    this.setData({ feedBusyId: id, feedItems: nextFeedItems });
    this.applyFilter(this.data.activeFilter, nextFeedItems);

    try {
      const resp = await apiRequest({
        url: "/api/client/feed/save",
        method: "POST",
        data: { post_id: id, saved: nextSaved }
      });

      const confirmedFeedItems = nextFeedItems.map((item) => {
        if (item.id !== id) {
          return item;
        }
        return { ...item, saved: Boolean(resp && resp.saved) };
      });

      this.setData({ feedItems: confirmedFeedItems, feedBusyId: "" });
      this.applyFilter(this.data.activeFilter, confirmedFeedItems);
    } catch (error) {
      this.setData({ feedBusyId: "" });
      this.loadHome();
      wx.showToast({ title: error && error.message || "收藏失败", icon: "none" });
    }
  }
});
