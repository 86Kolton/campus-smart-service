const { apiRequest, getTokenInfo, isWechatBindRequiredError } = require("../../utils/request");

const FILTER_OPTIONS = [
  { id: "all", label: "全部" },
  { id: "quick", label: "快速代取" },
  { id: "delivery", label: "外卖代拿" },
  { id: "print", label: "打印跑腿" }
];

const STATUS_ORDER = {
  open: 0,
  inprogress: 1,
  waiting_confirm: 2,
  done: 3,
  canceled: 4
};

function sortTasks(tasks = []) {
  return tasks.slice().sort((left, right) => {
    const leftOrder = STATUS_ORDER[String(left.status || "open")] ?? 99;
    const rightOrder = STATUS_ORDER[String(right.status || "open")] ?? 99;
    if (leftOrder !== rightOrder) {
      return leftOrder - rightOrder;
    }
    return new Date(String(right.created_at || "")).getTime() - new Date(String(left.created_at || "")).getTime();
  });
}

function mergeTaskLists(poolTasks = [], myTasks = []) {
  const merged = new Map();
  [...poolTasks, ...myTasks].forEach((item) => {
    if (!item || !item.id) {
      return;
    }
    const id = String(item.id);
    const previous = merged.get(id);
    merged.set(id, previous ? { ...previous, ...item } : item);
  });
  return sortTasks(Array.from(merged.values()));
}

function normalizeTaskFlags(item = {}, userId = 0, forceRunner = false) {
  const runnerId = Number(item.runner_id || item.runnerId || 0);
  const publisherId = Number(item.publisher_id || item.publisherId || 0);
  const isRunner = Boolean(forceRunner || item.is_runner || item.isRunner || (userId > 0 && runnerId === userId));
  const isPublisher = Boolean(item.is_publisher || item.isPublisher || (userId > 0 && publisherId === userId));
  return {
    ...item,
    is_runner: isRunner,
    isRunner,
    is_publisher: isPublisher,
    isPublisher
  };
}

function normalizeTaskList(items = [], userId = 0) {
  return (Array.isArray(items) ? items : []).map((item) => normalizeTaskFlags(item, userId));
}

function normalizeActionTask(item = {}, action = "", taskId = "", userId = 0) {
  if (!item || typeof item !== "object") {
    return null;
  }
  const next = normalizeTaskFlags({ id: taskId, ...item }, userId, ["claim", "delivered", "confirm"].includes(action));
  if (action === "claim" && !["inprogress", "waiting_confirm"].includes(String(next.status || ""))) {
    next.status = "inprogress";
  }
  return next;
}

function filterTasks(tasks = [], filter = "all", status = "all") {
  const filtered = filter === "all" ? tasks : tasks.filter((item) => item.task_type === filter);
  if (status === "open") return filtered.filter((item) => String(item.status) === "open");
  if (status === "inprogress") {
    return filtered.filter((item) => isRunnerTask(item) && ["inprogress", "waiting_confirm"].includes(String(item.status)));
  }
  if (status === "done") return filtered.filter((item) => isRunnerTask(item) && String(item.status) === "done");
  return filtered.filter((item) => shouldShowInDefaultPool(item));
}

function getStats(tasks = []) {
  return {
    open: tasks.filter((item) => String(item.status) === "open").length,
    inprogress: tasks.filter((item) => isRunnerTask(item) && ["inprogress", "waiting_confirm"].includes(String(item.status))).length,
    done: tasks.filter((item) => isRunnerTask(item) && String(item.status) === "done").length
  };
}

function isRunnerTask(item = {}) {
  return Boolean(item.is_runner || item.isRunner);
}

function isPublisherTask(item = {}) {
  return Boolean(item.is_publisher || item.isPublisher);
}

function shouldShowInDefaultPool(item = {}) {
  const status = String(item.status || "open");
  return status === "open" || isRunnerTask(item) || isPublisherTask(item);
}

function getEmptyText(status = "all") {
  if (status === "inprogress") return "你暂无进行中的接单任务";
  if (status === "done") return "你暂无已完成的接单任务";
  if (status === "open") return "暂无待接单跑腿需求";
  return "当前筛选下暂无跑腿需求";
}

Page({
  pendingRunnerTaskIds: null,

  data: {
    activeFilter: "all",
    activeStatus: "all",
    filters: FILTER_OPTIONS,
    tasks: [],
    rawTasks: [],
    selectedTask: null,
    stats: {
      open: 0,
      inprogress: 0,
      done: 0
    },
    loading: false,
    error: "",
    emptyText: getEmptyText(),
    focusId: ""
  },

  onLoad(query) {
    this.pendingRunnerTaskIds = new Set();
    this.setData({ focusId: String(query.focus || "") });
  },

  onShow() {
    const app = getApp();
    this.setData({ loading: true, error: "" });
    app.ensureSession().finally(() => this.loadTasks(this.data.focusId));
  },

  onPullDownRefresh() {
    this.loadTasks(this.data.focusId).finally(() => wx.stopPullDownRefresh());
  },

  getPendingRunnerTasks() {
    const pendingIds = this.pendingRunnerTaskIds || new Set();
    return (this.data.rawTasks || []).filter((item) => {
      const status = String(item.status || "");
      return pendingIds.has(String(item.id || "")) && isRunnerTask(item) && ["inprogress", "waiting_confirm", "done"].includes(status);
    });
  },

  markPendingRunnerTask(taskId = "") {
    const id = String(taskId || "").trim();
    if (!id) return;
    if (!this.pendingRunnerTaskIds) {
      this.pendingRunnerTaskIds = new Set();
    }
    this.pendingRunnerTaskIds.add(id);
  },

  clearConfirmedPendingTasks(items = []) {
    if (!this.pendingRunnerTaskIds || !this.pendingRunnerTaskIds.size) {
      return;
    }
    (items || []).forEach((item) => {
      if (isRunnerTask(item)) {
        this.pendingRunnerTaskIds.delete(String(item.id || ""));
      }
    });
  },

  async loadTasks(focusId = "", options = {}) {
    this.setData({ loading: true, error: "" });
    try {
      const [poolResult, myResult] = await Promise.allSettled([
        apiRequest({ url: "/api/client/errands", method: "GET" }),
        apiRequest({ url: "/api/client/errands/my", method: "GET" })
      ]);
      if (poolResult.status === "rejected" && myResult.status === "rejected") {
        throw poolResult.reason || myResult.reason;
      }
      const poolData = poolResult.status === "fulfilled" ? poolResult.value : null;
      const myData = myResult.status === "fulfilled" ? myResult.value : null;
      const userId = Number(getTokenInfo().userId || 0);
      const poolItems = normalizeTaskList(poolData && poolData.items, userId);
      const myItems = normalizeTaskList(myData && myData.items, userId);
      if (myResult.status === "fulfilled") {
        this.clearConfirmedPendingTasks(myItems);
      }
      const rawTasks = mergeTaskLists(
        poolItems,
        options.preserveMyTasks ? mergeTaskLists(this.getPendingRunnerTasks(), myItems) : myItems
      );
      const fallbackTasks = rawTasks.length ? rawTasks : this.data.rawTasks;
      const error = myResult.status === "rejected"
        ? (isWechatBindRequiredError(myResult.reason) ? "请先完成微信登录/绑定后查看我的接单" : ((myResult.reason && myResult.reason.message) || "我的接单暂时加载失败"))
        : "";
      this.setData({ rawTasks: fallbackTasks, loading: false, error }, () => this.refreshView(focusId));
    } catch (error) {
      const keepExisting = Array.isArray(this.data.rawTasks) && this.data.rawTasks.length > 0;
      this.setData({
        rawTasks: keepExisting ? this.data.rawTasks : [],
        tasks: keepExisting ? this.data.tasks : [],
        selectedTask: keepExisting ? this.data.selectedTask : null,
        loading: false,
        error: isWechatBindRequiredError(error) ? "请先完成微信登录/绑定后查看我的接单" : (error && error.message || "加载跑腿任务失败")
      });
    }
  },

  refreshView(focusId = "") {
    const tasks = filterTasks(this.data.rawTasks, this.data.activeFilter, this.data.activeStatus);
    const selectedId = String(focusId || (this.data.selectedTask && this.data.selectedTask.id) || "");
    const selectedTask = tasks.find((item) => item.id === selectedId) || null;
    this.setData({
      tasks,
      selectedTask,
      stats: getStats(this.data.rawTasks),
      emptyText: getEmptyText(this.data.activeStatus),
      focusId: ""
    });
  },

  onChangeFilter(event) {
    const activeFilter = event.currentTarget.dataset.filter || "all";
    this.setData({ activeFilter }, () => this.refreshView());
  },

  onTapHeroStat(event) {
    const nextStatus = String(event.currentTarget.dataset.status || "all");
    const activeStatus = this.data.activeStatus === nextStatus ? "all" : nextStatus;
    this.setData({ activeStatus }, () => this.refreshView());
  },

  openComposer() {
    wx.navigateTo({ url: "/pages/errand-compose/errand-compose" });
  },

  openTask(event) {
    const taskId = String(event.currentTarget.dataset.id || "");
    const selectedTask = this.data.tasks.find((item) => item.id === taskId) || null;
    if (!selectedTask) {
      return;
    }
    this.setData({ selectedTask });
  },

  clearSelection() {
    this.setData({ selectedTask: null });
  },

  async runAction(event) {
    const taskId = String(event.currentTarget.dataset.id || "");
    const action = String(event.currentTarget.dataset.action || "detail");
    if (!taskId) {
      return;
    }
    if (action === "detail") {
      const selectedTask = this.data.tasks.find((item) => item.id === taskId) || null;
      this.setData({ selectedTask });
      return;
    }
    try {
      const result = await apiRequest({
        url: "/api/client/errands/action",
        method: "POST",
        data: { task_id: taskId, action }
      });
      const nextStatus = action === "confirm"
        ? "done"
        : (action === "claim" || action === "delivered" ? "inprogress" : (action === "cancel" ? "open" : this.data.activeStatus));
      const userId = Number(getTokenInfo().userId || 0);
      const actionItem = normalizeActionTask(result && result.item, action, taskId, userId);
      if (["claim", "delivered", "confirm"].includes(action) && actionItem) {
        this.markPendingRunnerTask(actionItem.id || taskId);
      }
      const optimisticTasks = actionItem
        ? mergeTaskLists(this.data.rawTasks, [actionItem])
        : this.data.rawTasks;
      this.setData({ rawTasks: optimisticTasks, activeStatus: nextStatus }, () => this.refreshView(taskId));
      await this.loadTasks(taskId, { preserveMyTasks: true });
      wx.showToast({ title: result && result.message || "任务状态已更新", icon: "none" });
    } catch (error) {
      wx.showToast({ title: isWechatBindRequiredError(error) ? "请先完成微信登录/绑定后再接单" : (error && error.message || "操作失败"), icon: "none" });
    }
  }
});
