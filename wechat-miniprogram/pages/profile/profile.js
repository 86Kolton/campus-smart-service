const { apiRequest } = require("../../utils/request");
const { bindWechat, loginWithWechat } = require("../../utils/auth");
const {
  buildGreetingName,
  formatGreetingDate,
  getAvatarText,
  getClientDisplayName,
  syncTabBar
} = require("../../utils/ui");

const EDU_HEADER = { "X-Edu-Session": "mini-program" };
const LIVE_SYNC_MS = 15000;
const DEFAULT_EDU_OVERVIEW = {
  student_name: "赵毅",
  student_id: "20222605045",
  total_score: 167.6,
  gpa: 3.35,
  passed_courses: 46,
  failed_courses: 0,
  retake_courses: 0,
  term: "2025-2026秋学期",
  current_week: 1
};

function formatFixed(value, digits = 1) {
  return Number(value || 0).toFixed(digits);
}

function buildInboxCards(unread = {}) {
  const likesUnread = Number(unread.likes_unread || 0);
  const savedUnread = Number(unread.saved_unread || 0);
  const likesTotal = Number(unread.likes_total || 0);
  const savedTotal = Number(unread.saved_total || 0);
  return [
    {
      id: "likes",
      title: "收到的赞",
      subtitle: likesUnread > 0 ? `${likesUnread} 条未读，累计 ${likesTotal} 条互动` : (likesTotal > 0 ? `累计 ${likesTotal} 条互动` : "暂无点赞记录"),
      count: likesTotal,
      unread: likesUnread
    },
    {
      id: "saved",
      title: "收藏列表",
      subtitle: savedTotal > 0 ? `累计 ${savedTotal} 条收藏内容` : "暂无收藏记录",
      count: savedTotal,
      unread: savedUnread
    }
  ];
}

function isPlaceholderName(value = "") {
  const text = String(value || "").trim();
  if (!text) return true;
  return ["校园访客", "微信用户", "微信访客", "访客", "游客"].includes(text);
}

function resolveVisibleName(summary = null, fallback = "赵毅") {
  const primary = String((summary && summary.name) || fallback || "").trim();
  const publicName = String((summary && summary.public_name) || "").trim();
  if (isPlaceholderName(primary) && publicName) return publicName;
  return primary || publicName || fallback;
}

function buildEduStats(overview = DEFAULT_EDU_OVERVIEW, exams = [], classrooms = []) {
  const upcomingExams = (Array.isArray(exams) ? exams : []).filter((item) => String(item.exam_status || "").toLowerCase() !== "finished").length;
  const recommendedRooms = (Array.isArray(classrooms) ? classrooms : []).filter((item) => Boolean(item.recommended)).length;
  return [
    { label: "累计学分", value: formatFixed(overview.total_score, 1), action: "grades" },
    { label: "平均绩点", value: formatFixed(overview.gpa, 2), action: "grades" },
    { label: "待考安排", value: String(upcomingExams), action: "exams" },
    { label: "推荐空教室", value: String(recommendedRooms), action: "free" }
  ];
}

function buildEduQuickItems(overview = DEFAULT_EDU_OVERVIEW, exams = []) {
  const upcomingExams = (Array.isArray(exams) ? exams : []).filter((item) => String(item.exam_status || "").toLowerCase() !== "finished").length;
  return [
    {
      action: "grades",
      icon: "绩",
      badge: "全学期",
      title: "成绩查询",
      sub: "按学期查看完整成绩"
    },
    {
      action: "schedule",
      icon: "课",
      badge: "1-18周",
      title: "课表查看",
      sub: `当前第 ${Number(overview.current_week || 1)} 周，可切换全部周次`
    },
    {
      action: "free",
      icon: "空",
      badge: "三校区",
      title: "空教室",
      sub: "校区、教学楼、教室三级查看"
    },
    {
      action: "exams",
      icon: "考",
      badge: upcomingExams > 0 ? `${upcomingExams} 条提醒` : "已整理",
      title: "考试安排",
      sub: "统一查看时间、地点和类型"
    }
  ];
}

Page({
  data: {
    greetingName: buildGreetingName("赵毅"),
    greetingDate: formatGreetingDate(),
    loading: false,
    error: "",
    summary: null,
    displayName: "赵毅",
    avatarText: "赵毅",
    unread: { likes_unread: 0, saved_unread: 0, likes_total: 0, saved_total: 0 },
    inboxCards: buildInboxCards({}),
    eduOverview: { ...DEFAULT_EDU_OVERVIEW },
    eduSessionLine: "赵毅 · 学号 20222605045 · 2025-2026秋学期",
    eduStats: buildEduStats(DEFAULT_EDU_OVERVIEW, [], []),
    eduQuickItems: buildEduQuickItems(DEFAULT_EDU_OVERVIEW, [])
  },

  onShow() {
    syncTabBar(this, 3);
    this.setData({
      greetingDate: formatGreetingDate(),
      greetingName: buildGreetingName(getClientDisplayName("赵毅"))
    });
    this.startLiveSync();
    this.refreshAll();
  },

  onHide() {
    this.stopLiveSync();
  },

  onUnload() {
    this.stopLiveSync();
  },

  onPullDownRefresh() {
    this.refreshAll().finally(() => wx.stopPullDownRefresh());
  },

  startLiveSync() {
    this.stopLiveSync();
    this._liveSyncTimer = setInterval(() => {
      if (!this.data.loading) {
        this.refreshAll();
      }
    }, LIVE_SYNC_MS);
  },

  stopLiveSync() {
    if (this._liveSyncTimer) {
      clearInterval(this._liveSyncTimer);
      this._liveSyncTimer = null;
    }
  },

  async refreshAll() {
    const app = getApp();
    this.setData({ loading: true, error: "" });
    try {
      await app.ensureSession();
      await Promise.all([this.loadSummary(), this.loadUnread(), this.loadEduPreview()]);
      this.setData({ loading: false });
    } catch (error) {
      this.setData({
        loading: false,
        error: (error && error.message) || "加载失败"
      });
    }
  },

  async loadSummary() {
    const data = await apiRequest({ url: "/api/client/profile/summary", method: "GET" });
    const fallbackName = getClientDisplayName("赵毅") || "赵毅";
    const summary = data || null;
    const name = resolveVisibleName(summary, fallbackName);
    const publicName = String((summary && summary.public_name) || "赵同学");
    const app = getApp();
    app.globalData.client = {
      ...(app.globalData.client || {}),
      displayName: name,
      publicName,
      wechatBound: Boolean(summary && summary.wechat_bound)
    };
    this.setData({
      summary,
      displayName: name,
      greetingName: buildGreetingName(name),
      avatarText: getAvatarText(name)
    });
  },

  async loadUnread() {
    const data = await apiRequest({ url: "/api/client/messages/unread-count", method: "GET" });
    const unread = {
      likes_unread: Number((data && data.likes_unread) || 0),
      saved_unread: Number((data && data.saved_unread) || 0),
      likes_total: Number((data && data.likes_total) || 0),
      saved_total: Number((data && data.saved_total) || 0)
    };
    const hasUnread = unread.likes_unread + unread.saved_unread > 0;
    const app = getApp();
    app.globalData.profileDot = hasUnread;
    this.setData({ unread, inboxCards: buildInboxCards(unread) });
    const tabBar = this.getTabBar && this.getTabBar();
    if (tabBar && typeof tabBar.setData === "function") {
      tabBar.setData({ profileDot: hasUnread });
    }
  },

  async loadEduPreview() {
    try {
      const [overview, examsResp, classroomsResp] = await Promise.all([
        apiRequest({ url: "/api/client/edu/overview", method: "GET", header: EDU_HEADER }),
        apiRequest({ url: "/api/client/edu/exams", method: "GET", header: EDU_HEADER }),
        apiRequest({
          url: `/api/client/edu/free-classrooms?campus=${encodeURIComponent("七一路校区")}`,
          method: "GET",
          header: EDU_HEADER
        })
      ]);

      const safeOverview = overview || { ...DEFAULT_EDU_OVERVIEW };
      const exams = (examsResp && examsResp.items) || [];
      const classrooms = (classroomsResp && classroomsResp.items) || [];

      this.setData({
        eduOverview: safeOverview,
        eduSessionLine: `${safeOverview.student_name} · 学号 ${safeOverview.student_id} · ${safeOverview.term}`,
        eduStats: buildEduStats(safeOverview, exams, classrooms),
        eduQuickItems: buildEduQuickItems(safeOverview, exams)
      });
    } catch (error) {
      this.setData({
        eduOverview: { ...DEFAULT_EDU_OVERVIEW },
        eduSessionLine: "赵毅 · 学号 20222605045 · 2025-2026秋学期",
        eduStats: buildEduStats(DEFAULT_EDU_OVERVIEW, [], []),
        eduQuickItems: buildEduQuickItems(DEFAULT_EDU_OVERVIEW, [])
      });
    }
  },

  onTapStat(event) {
    const mode = event.currentTarget.dataset.mode || "my";
    if (mode === "likes") {
      return this.openInboxByType("likes");
    }
    this.openProfileList(mode);
  },

  openProfileList(mode = "my") {
    const safeMode = mode === "liked" ? "liked" : "my";
    wx.navigateTo({ url: `/pages/profile-list/profile-list?mode=${encodeURIComponent(safeMode)}` });
  },

  openInbox(event) {
    const type = event.currentTarget.dataset.type || "likes";
    this.openInboxByType(type);
  },

  openInboxByType(type = "likes") {
    const safeType = type === "saved" ? "saved" : "likes";
    wx.navigateTo({ url: `/pages/message-list/message-list?type=${encodeURIComponent(safeType)}` });
  },

  openAccount() {
    wx.navigateTo({ url: "/pages/account/account" });
  },

  openEduHall() {
    wx.navigateTo({ url: "/pages/edu/edu" });
  },

  onTapEdu(event) {
    const action = event.currentTarget.dataset.action || "";
    if (!action) return;
    wx.navigateTo({ url: `/pages/edu/edu?action=${encodeURIComponent(action)}` });
  },

  onTapMenu(event) {
    const action = event.currentTarget.dataset.action || "";
    if (action === "myPosts") return this.openProfileList("my");
    if (action === "likedPosts") return this.openProfileList("liked");
    if (action === "publicName") return this.openAccount();
    if (action === "webLogin") return wx.navigateTo({ url: "/pages/web-login/web-login" });
    if (action === "wechatBind") return this.handleWechatLogin();
    if (action === "privacy") {
      wx.showModal({
        title: "公开展示说明",
        content: "个人资料、登录状态和教务数据统一由服务端维护。真实姓名只在“我的”页保留，帖子、评论和消息提醒对外仅展示公开昵称。",
        showCancel: false
      });
    }
  },

  async handleWechatLogin() {
    try {
      const app = getApp();
      await app.ensureSession();
      const res = await wx.login();
      if (!res.code) {
        wx.showToast({ title: "未获取到微信 code", icon: "none" });
        return;
      }
      const isBound = Boolean(this.data.summary && this.data.summary.wechat_bound);

      if (!isBound) {
        try {
          await bindWechat(res.code);
          await this.refreshAll();
          wx.showToast({ title: "绑定成功", icon: "success" });
          return;
        } catch (bindError) {
          const detail = String((bindError && bindError.data && bindError.data.detail) || (bindError && bindError.message) || "");
          if (!detail.includes("wechat_openid_in_use")) {
            throw bindError;
          }
        }
      }

      const client = await loginWithWechat(res.code, this.data.displayName || "");
      app.globalData.client = client;
      app.globalData.clientReady = true;
      await this.refreshAll();
      wx.showToast({ title: "登录成功", icon: "success" });
    } catch (error) {
      const raw = String((error && error.data && error.data.detail) || (error && error.message) || "");
      const message = raw.includes("wechat_not_configured")
        ? "当前暂未开启正式微信登录"
        : raw.includes("wechat_code2session")
          ? "微信登录校验失败，请稍后再试"
          : raw.includes("wechat_openid_in_use")
            ? "该微信已绑定其他账号"
            : (raw || "微信登录失败");
      wx.showToast({ title: message, icon: "none" });
    }
  },

  async markAllRead() {
    try {
      await apiRequest({ url: "/api/client/messages/mark-read", method: "POST", data: { type: "all" } });
      await this.loadUnread();
      wx.showToast({ title: "已全部标记为已读", icon: "none" });
    } catch (error) {
      wx.showToast({ title: (error && error.message) || "操作失败", icon: "none" });
    }
  }
});
