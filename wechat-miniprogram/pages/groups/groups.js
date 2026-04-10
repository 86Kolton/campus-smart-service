const { apiRequest } = require("../../utils/request");
const { normalizePostId } = require("../../utils/ui");

const GROUPS = [
  {
    id: "g-1",
    title: "期末自习互助群",
    members: 136,
    online: 42,
    tags: ["自习", "考试", "资料"],
    query: "自习 资料"
  },
  {
    id: "g-2",
    title: "空教室情报站",
    members: 98,
    online: 27,
    tags: ["空教室", "自习", "安静"],
    query: "空教室"
  },
  {
    id: "g-3",
    title: "跨校竞赛组队",
    members: 73,
    online: 15,
    tags: ["竞赛", "组队", "项目"],
    query: "跨校 组队"
  }
];

const TOPICS = [
  { id: "t-1", title: "A 区今晚 9 点后还有空教室吗？", meta: "来自 空教室情报站 · 2 分钟前", heat: "2.1k", query: "今晚 9 点 空教室" },
  { id: "t-2", title: "软件测试复习资料互换", meta: "来自 期末自习互助群 · 8 分钟前", heat: "1.3k", query: "软件测试 复习资料" },
  { id: "t-3", title: "计设竞赛有没有跨校队友？", meta: "来自 跨校竞赛组队 · 25 分钟前", heat: "980", query: "跨校 竞赛 组队" }
];

function normalizeSearchItem(item = {}, index = 0) {
  return {
    id: normalizePostId(item.id || `group-${index + 1}`),
    title: String(item.title || "相关帖子"),
    snippet: String(item.snippet || item.content || ""),
    meta: String(item.meta || "论坛帖子"),
    likes: Number(item.likes || 0),
    comments: Number(item.comments || 0)
  };
}

Page({
  data: {
    groups: GROUPS,
    topics: TOPICS,
    activeQuery: "校园趣事",
    activeLabel: "热点话题",
    posts: [],
    loading: false,
    error: ""
  },

  onShow() {
    const app = getApp();
    app.ensureSession().finally(() => {
      this.loadMatches(this.data.activeQuery, this.data.activeLabel);
    });
  },

  onPullDownRefresh() {
    this.loadMatches(this.data.activeQuery, this.data.activeLabel).finally(() => wx.stopPullDownRefresh());
  },

  async loadMatches(query, label) {
    const safeQuery = String(query || "").trim() || "校园趣事";
    this.setData({
      loading: true,
      error: "",
      activeQuery: safeQuery,
      activeLabel: String(label || "热点话题")
    });
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
        error: error && error.message || "加载跨校话题失败"
      });
    }
  },

  onTapGroup(event) {
    const query = event.currentTarget.dataset.query || "";
    const label = event.currentTarget.dataset.title || "讨论组";
    this.loadMatches(query, label);
  },

  onTapTopic(event) {
    const query = event.currentTarget.dataset.query || "";
    const label = event.currentTarget.dataset.title || "热点话题";
    this.loadMatches(query, label);
  },

  openComposer() {
    wx.navigateTo({
      url: `/pages/post/post?category=${encodeURIComponent("study")}&prefill_tags=${encodeURIComponent("跨校, 互助, 组队")}&draft_hint=${encodeURIComponent("当前页面是跨校小组，发帖时建议写清楚目标、人数、时间和联系方式。")}`
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
