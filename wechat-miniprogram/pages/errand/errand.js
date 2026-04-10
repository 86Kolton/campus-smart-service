const { apiRequest } = require("../../utils/request");

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

function filterTasks(tasks = [], filter = "all", status = "all") {
  const filtered = filter === "all" ? tasks : tasks.filter((item) => item.task_type === filter);
  if (status === "open") return filtered.filter((item) => String(item.status) === "open");
  if (status === "inprogress") {
    return filtered.filter((item) => ["inprogress", "waiting_confirm"].includes(String(item.status)));
  }
  if (status === "done") return filtered.filter((item) => String(item.status) === "done");
  return filtered;
}

function getStats(tasks = []) {
  return {
    open: tasks.filter((item) => String(item.status) === "open").length,
    inprogress: tasks.filter((item) => ["inprogress", "waiting_confirm"].includes(String(item.status))).length,
    done: tasks.filter((item) => String(item.status) === "done").length
  };
}

Page({
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
    focusId: ""
  },

  onLoad(query) {
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

  async loadTasks(focusId = "") {
    this.setData({ loading: true, error: "" });
    try {
      const data = await apiRequest({ url: "/api/client/errands", method: "GET" });
      const rawTasks = sortTasks(Array.isArray(data && data.items) ? data.items : []);
      this.setData({ rawTasks, loading: false }, () => this.refreshView(focusId));
    } catch (error) {
      this.setData({ rawTasks: [], tasks: [], selectedTask: null, loading: false, error: error && error.message || "加载跑腿任务失败" });
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
      await this.loadTasks(taskId);
      wx.showToast({ title: result && result.message || "任务状态已更新", icon: "none" });
    } catch (error) {
      wx.showToast({ title: error && error.message || "操作失败", icon: "none" });
    }
  }
});
