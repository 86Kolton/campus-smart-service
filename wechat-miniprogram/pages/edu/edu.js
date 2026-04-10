const { apiRequest } = require("../../utils/request");

const EDU_HEADER = { "X-Edu-Session": "mini-program" };
const DEFAULT_CAMPUS = "七一路校区";
const ALL_BUILDINGS_VALUE = "__all__";

const ACTION_CONFIG = {
  hall: {
    title: "教务大厅",
    brow: "受控教务会话",
    subtitle: "成绩、课表、考试和空教室统一放在一个受控入口里查看，不参与公开知识库检索和推荐。",
    footerNote: "成绩当前使用模拟数据，后续正式教务接口接入后可平滑替换。"
  },
  grades: {
    title: "成绩查询",
    brow: "模拟成绩数据",
    subtitle: "支持按学期切换查看同一位同学的完整成绩记录，只在当前会话内展示。",
    footerNote: "成绩数据不进入公开知识库，也不参与论坛推荐和自进化。"
  },
  schedule: {
    title: "课表查看",
    brow: "周次可切换",
    subtitle: "按周查看本学期 1 到 18 周课表，可自由切换任意周次。",
    footerNote: "课表只在当前登录会话里展示，不会被公开检索。"
  },
  free: {
    title: "空教室",
    brow: "校区与教学楼查看",
    subtitle: "支持按校区切换公共教学楼，再查看该教学楼全部教室的空闲情况。",
    footerNote: "空教室数据仅作为当前会话参考，不写入公开知识库。"
  },
  exams: {
    title: "考试安排",
    brow: "考试提醒",
    subtitle: "统一查看考试时间、地点和考试类型，减少临近考试时翻通知的成本。",
    footerNote: "考试提醒只服务当前登录用户，不对外公开。"
  }
};

function formatFixed(value, digits = 1) {
  return Number(value || 0).toFixed(digits);
}

function getWeekdayLabel(weekday = 1) {
  return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][Math.max(0, Number(weekday || 1) - 1)] || "待定";
}

function getCurrentWeekday() {
  const day = new Date().getDay();
  return day === 0 ? 7 : day;
}

function clampPercent(value) {
  const number = Number(value || 0);
  if (!Number.isFinite(number)) return 0;
  if (number < 0) return 0;
  if (number > 100) return 100;
  return Math.round(number);
}

function buildOverviewFallback() {
  return {
    student_name: "赵毅",
    student_id: "20222605045",
    total_score: 167.6,
    gpa: 3.35,
    passed_courses: 46,
    failed_courses: 0,
    retake_courses: 0,
    term: "2025-2026秋学期",
    available_terms: [
      "2025-2026秋学期",
      "2024-2025春学期",
      "2024-2025秋学期",
      "2023-2024春学期",
      "2023-2024秋学期",
      "2022-2023春学期",
      "2022-2023秋学期"
    ],
    current_week: 1,
    total_weeks: 18,
    campuses: ["七一路校区", "五四路校区", "裕华路校区"]
  };
}

function buildHallStats(overview = buildOverviewFallback(), exams = [], rooms = []) {
  const upcomingExamCount = (exams || []).filter((item) => String(item.exam_status || "").toLowerCase() !== "finished").length;
  const recommendedCount = (rooms || []).filter((item) => Boolean(item.recommended)).length;
  return [
    { label: "累计学分", value: formatFixed(overview.total_score, 1), action: "grades" },
    { label: "平均绩点", value: formatFixed(overview.gpa, 2), action: "grades" },
    { label: "待考安排", value: String(upcomingExamCount), action: "exams" },
    { label: "推荐空教室", value: String(recommendedCount), action: "free" }
  ];
}

function buildHallModules() {
  return [
    { action: "grades", icon: "绩", badge: "全学期", title: "成绩查询", copy: "查看所有学期成绩与绩点变化" },
    { action: "schedule", icon: "课", badge: "1-18 周", title: "课表查看", copy: "切换本学期任意周次课表" },
    { action: "free", icon: "空", badge: "三校区", title: "空教室", copy: "按校区和教学楼查看全部教室" },
    { action: "exams", icon: "考", badge: "提醒", title: "考试安排", copy: "统一查看考试时间和地点" }
  ];
}

function buildTermOptions(terms = []) {
  return (Array.isArray(terms) ? terms : []).map((term) => ({
    label: String(term),
    value: String(term)
  }));
}

function buildWeekOptions(weeks = []) {
  return (Array.isArray(weeks) ? weeks : []).map((week) => ({
    label: `第 ${Number(week)} 周`,
    value: Number(week)
  }));
}

function buildCampusOptions(campuses = []) {
  return (Array.isArray(campuses) ? campuses : []).map((campus) => ({
    label: String(campus),
    value: String(campus)
  }));
}

function buildBuildingOptions(buildings = []) {
  const options = [{ label: "全部教学楼", value: ALL_BUILDINGS_VALUE }];
  (Array.isArray(buildings) ? buildings : []).forEach((building) => {
    options.push({
      label: String(building),
      value: String(building)
    });
  });
  return options;
}

function findOptionIndex(options = [], value = "", fallback = 0) {
  const index = (Array.isArray(options) ? options : []).findIndex((item) => String(item.value) === String(value));
  return index >= 0 ? index : fallback;
}

function getOptionLabel(options = [], index = 0, fallback = "") {
  const safe = (Array.isArray(options) ? options : [])[Number(index) || 0];
  return safe ? String(safe.label || fallback) : String(fallback || "");
}

function getOptionValue(options = [], index = 0, fallback = "") {
  const safe = (Array.isArray(options) ? options : [])[Number(index) || 0];
  return safe ? safe.value : fallback;
}

function normalizeGradeCards(items = []) {
  return (Array.isArray(items) ? items : []).map((item, index) => {
    const score = Number(item.score || 0);
    const tone = score >= 90 ? "emerald" : score >= 80 ? "blue" : score >= 60 ? "sand" : "rose";
    return {
      id: `grade-${index + 1}`,
      eyebrow: "课程成绩",
      title: String(item.course_name || "课程"),
      meta: `${Number(item.credit || 0)} 学分 · 绩点 ${formatFixed(item.grade_point, 1)}`,
      extra: score >= 60 ? "当前课程成绩已归档，可继续关注学分与绩点变化。" : "建议后续重点关注补考或重修安排。",
      value: String(score),
      tone,
      tags: [
        `${Number(item.credit || 0)} 学分`,
        `绩点 ${formatFixed(item.grade_point, 1)}`,
        String(item.status || "").toLowerCase() === "passed" ? "已通过" : "待关注"
      ],
      hasProgress: false,
      progress: 0
    };
  });
}

function normalizeScheduleCards(items = [], focusToday = false) {
  const today = getCurrentWeekday();
  const ordered = (Array.isArray(items) ? items : []).slice().sort((left, right) => {
    const leftToday = Number(left.weekday || 0) === today ? 0 : 1;
    const rightToday = Number(right.weekday || 0) === today ? 0 : 1;
    if (focusToday && leftToday !== rightToday) return leftToday - rightToday;
    if (Number(left.weekday || 0) !== Number(right.weekday || 0)) {
      return Number(left.weekday || 0) - Number(right.weekday || 0);
    }
    return Number(left.section || 0) - Number(right.section || 0);
  });

  return ordered.map((item, index) => {
    const section = Number(item.section || 1);
    const span = Math.max(1, Number(item.section_span || 1));
    const end = section + span - 1;
    const isToday = Number(item.weekday || 0) === today;
    return {
      id: `schedule-${index + 1}`,
      eyebrow: `${isToday ? "今日" : "本周"} · ${getWeekdayLabel(item.weekday)}`,
      title: String(item.course_name || "课程"),
      meta: `第 ${section}${span > 1 ? `-${end}` : ""} 节 · ${String(item.location || "地点待定")}`,
      extra: `${String(item.teacher || "教师待定")} · ${String(item.weeks || "本周")}`,
      value: getWeekdayLabel(item.weekday),
      tone: isToday ? "emerald" : "blue",
      tags: [String(item.location || "地点待定"), String(item.teacher || "教师待定")],
      hasProgress: false,
      progress: 0
    };
  });
}

function normalizeExamCards(items = []) {
  return (Array.isArray(items) ? items : []).map((item, index) => {
    const upcoming = String(item.exam_status || "").toLowerCase() !== "finished";
    return {
      id: `exam-${index + 1}`,
      eyebrow: upcoming ? "待考试" : "已结束",
      title: String(item.course_name || "考试安排"),
      meta: `${String(item.exam_date || "日期待定")} ${String(item.exam_time || "")}`.trim(),
      extra: `${String(item.exam_location || "地点待定")} · ${String(item.exam_type || "考试安排")}`,
      value: upcoming ? "待考" : "已考",
      tone: upcoming ? "sand" : "blue",
      tags: [String(item.term || ""), upcoming ? "提醒" : "归档"],
      hasProgress: false,
      progress: 0
    };
  });
}

function normalizeRoomCards(items = [], activeBuilding = "") {
  return (Array.isArray(items) ? items : [])
    .filter((item) => !activeBuilding || String(item.building || "") === String(activeBuilding))
    .slice()
    .sort((left, right) => {
      if (Boolean(left.recommended) !== Boolean(right.recommended)) {
        return Number(Boolean(right.recommended)) - Number(Boolean(left.recommended));
      }
      return Number(left.idle_percent || 0) - Number(right.idle_percent || 0);
    })
    .map((item, index) => {
      const idle = clampPercent(item.idle_percent);
      return {
        id: `room-${index + 1}`,
        eyebrow: Boolean(item.recommended) ? "优先推荐" : "教室状态",
        title: `${String(item.building || "")} ${String(item.room || "")}`.trim(),
        meta: `${String(item.campus || DEFAULT_CAMPUS)} · 空闲度 ${idle}%`,
        extra: idle <= 20 ? "更适合临时自习、查资料和短时复盘。" : "到达后再确认是否有临时占用变化。",
        value: `${idle}%`,
        tone: Boolean(item.recommended) ? "emerald" : idle <= 20 ? "blue" : "sand",
        tags: [Boolean(item.recommended) ? "优先推荐" : "可选教室"],
        hasProgress: true,
        progress: idle
      };
    });
}

function buildBuildingPreviewCards(items = [], buildings = [], activeBuilding = ALL_BUILDINGS_VALUE) {
  const allItems = Array.isArray(items) ? items : [];
  const cards = [
    {
      id: "all-buildings",
      value: ALL_BUILDINGS_VALUE,
      title: "全部教学楼",
      badge: `${(Array.isArray(buildings) ? buildings : []).length} 栋`,
      copy: `查看本校区全部 ${allItems.length} 间公共教室`,
      active: String(activeBuilding || ALL_BUILDINGS_VALUE) === ALL_BUILDINGS_VALUE
    }
  ];

  (Array.isArray(buildings) ? buildings : []).forEach((building) => {
    const scopedItems = allItems.filter((item) => String(item.building || "") === String(building));
    const recommendedCount = scopedItems.filter((item) => Boolean(item.recommended)).length;
    cards.push({
      id: String(building),
      value: String(building),
      title: String(building),
      badge: `${scopedItems.length} 间`,
      copy: recommendedCount > 0 ? `低占用推荐 ${recommendedCount} 间` : "查看该楼全部教室",
      active: String(activeBuilding || "") === String(building)
    });
  });

  return cards;
}

function buildGradeStats(overview = buildOverviewFallback(), payload = {}) {
  return [
    { label: "累计学分", value: formatFixed(overview.total_score, 1), action: "grades" },
    { label: "学期学分", value: formatFixed(payload.term_credit, 1), action: "grades" },
    { label: "学期绩点", value: formatFixed(payload.term_gpa, 2), action: "grades" },
    { label: "已通过", value: String(payload.passed_count || 0), action: "grades" }
  ];
}

function buildScheduleStats(items = [], weekNo = 1) {
  const weekdays = new Set((Array.isArray(items) ? items : []).map((item) => Number(item.weekday || 0)).filter(Boolean));
  const todayCount = (Array.isArray(items) ? items : []).filter((item) => Number(item.weekday || 0) === getCurrentWeekday()).length;
  return [
    { label: "当前周次", value: `第 ${Number(weekNo || 1)} 周`, action: "schedule" },
    { label: "本周课程", value: String((items || []).length), action: "schedule" },
    { label: "上课天数", value: String(weekdays.size), action: "schedule" },
    { label: "今日课程", value: String(todayCount), action: "schedule" }
  ];
}

function buildExamStats(items = []) {
  const upcoming = (items || []).filter((item) => String(item.exam_status || "").toLowerCase() !== "finished").length;
  const finished = Math.max(0, (items || []).length - upcoming);
  return [
    { label: "全部安排", value: String((items || []).length), action: "exams" },
    { label: "待考试", value: String(upcoming), action: "exams" },
    { label: "已结束", value: String(finished), action: "exams" },
    { label: "当前学期", value: "已同步", action: "exams" }
  ];
}

function buildFreeStats(activeCampus = DEFAULT_CAMPUS, buildings = [], activeBuildingLabel = "全部教学楼", rooms = []) {
  return [
    { label: "当前校区", value: String(activeCampus).replace("校区", ""), action: "free" },
    { label: "公共教学楼", value: String((buildings || []).length), action: "free" },
    { label: "当前查看", value: String(activeBuildingLabel || "全部教学楼"), action: "free" },
    { label: "教室数量", value: String((rooms || []).length), action: "free" }
  ];
}

Page({
  data: {
    action: "hall",
    config: ACTION_CONFIG.hall,
    loading: false,
    error: "",
    overview: buildOverviewFallback(),
    summaryCards: [],
    hallModules: buildHallModules(),
    items: [],
    listTitle: "",
    emptyText: "暂无可展示内容",
    footerNote: ACTION_CONFIG.hall.footerNote,
    termOptions: buildTermOptions(buildOverviewFallback().available_terms),
    termIndex: 0,
    termDisplay: "2025-2026秋学期",
    weekOptions: buildWeekOptions(Array.from({ length: 18 }, (_, index) => index + 1)),
    weekIndex: 0,
    weekDisplay: "第 1 周",
    campusOptions: buildCampusOptions(buildOverviewFallback().campuses),
    campusIndex: 0,
    campusDisplay: DEFAULT_CAMPUS,
    buildingOptions: buildBuildingOptions([]),
    buildingIndex: 0,
    buildingDisplay: "全部教学楼",
    buildingPreviewCards: []
  },

  onLoad(query) {
    const requestedAction = String((query && query.action) || "").trim();
    const action = ACTION_CONFIG[requestedAction] ? requestedAction : "hall";
    this._focusToday = String((query && query.today) || "") === "1";
    this._freeItems = [];
    this._currentBuildings = [];
    this.setAction(action);
  },

  onShow() {
    const app = getApp();
    app.ensureSession().finally(() => {
      this.loadContent();
    });
  },

  onPullDownRefresh() {
    this.loadContent().finally(() => wx.stopPullDownRefresh());
  },

  setAction(action = "hall") {
    const safeAction = ACTION_CONFIG[action] ? action : "hall";
    const config = { ...ACTION_CONFIG[safeAction] };
    wx.setNavigationBarTitle({ title: config.title });
    this.setData({
      action: safeAction,
      config,
      footerNote: config.footerNote
    });
  },

  switchAction(action = "hall") {
    this.setAction(action);
    this.loadContent();
  },

  onTapModule(event) {
    const action = String(event.currentTarget.dataset.action || "").trim();
    if (!action) return;
    this.switchAction(action);
  },

  onTapStatCard(event) {
    const action = String(event.currentTarget.dataset.action || "").trim();
    if (!action || action === this.data.action) return;
    this.switchAction(action);
  },

  goHall() {
    this.switchAction("hall");
  },

  onTermPickerChange(event) {
    const index = Number(event.detail.value || 0);
    if (index === this.data.termIndex) return;
    this.setData({
      termIndex: index,
      termDisplay: getOptionLabel(this.data.termOptions, index, this.data.termDisplay)
    }, () => this.loadContent());
  },

  onWeekPickerChange(event) {
    const index = Number(event.detail.value || 0);
    if (index === this.data.weekIndex) return;
    this.setData({
      weekIndex: index,
      weekDisplay: getOptionLabel(this.data.weekOptions, index, this.data.weekDisplay)
    }, () => this.loadContent());
  },

  onCampusPickerChange(event) {
    const index = Number(event.detail.value || 0);
    if (index === this.data.campusIndex) return;
    this.setData({
      campusIndex: index,
      campusDisplay: getOptionLabel(this.data.campusOptions, index, this.data.campusDisplay),
      buildingIndex: 0,
      buildingDisplay: "全部教学楼"
    }, () => this.loadContent());
  },

  onBuildingPickerChange(event) {
    const index = Number(event.detail.value || 0);
    if (index === this.data.buildingIndex) return;
    this.setData({
      buildingIndex: index,
      buildingDisplay: getOptionLabel(this.data.buildingOptions, index, this.data.buildingDisplay)
    }, () => this.applyFreeSelection());
  },

  onTapBuildingCard(event) {
    const building = String(event.currentTarget.dataset.building || "").trim();
    if (!building) return;
    const nextIndex = findOptionIndex(this.data.buildingOptions, building, 0);
    this.setData({
      buildingIndex: nextIndex,
      buildingDisplay: getOptionLabel(this.data.buildingOptions, nextIndex, this.data.buildingDisplay)
    }, () => this.applyFreeSelection());
  },

  applyFreeSelection() {
    const selectedValue = String(getOptionValue(this.data.buildingOptions, this.data.buildingIndex, ALL_BUILDINGS_VALUE));
    const scopedBuilding = selectedValue === ALL_BUILDINGS_VALUE ? "" : selectedValue;
    const buildingLabel = getOptionLabel(this.data.buildingOptions, this.data.buildingIndex, "全部教学楼");
    const roomCards = normalizeRoomCards(this._freeItems || [], scopedBuilding);
    this.setData({
      buildingDisplay: buildingLabel,
      buildingPreviewCards: buildBuildingPreviewCards(this._freeItems || [], this._currentBuildings || [], selectedValue),
      summaryCards: buildFreeStats(this.data.campusDisplay, this._currentBuildings || [], buildingLabel, roomCards),
      items: roomCards,
      listTitle: `${this.data.campusDisplay} · ${buildingLabel} 教室信息`,
      emptyText: scopedBuilding ? "当前教学楼暂无可展示教室" : "当前校区暂无可展示教室"
    });
  },

  async loadContent() {
    const action = this.data.action;
    this.setData({
      loading: true,
      error: "",
      summaryCards: [],
      items: [],
      listTitle: "",
      buildingPreviewCards: []
    });

    try {
      const overviewResp = await apiRequest({
        url: "/api/client/edu/overview",
        method: "GET",
        header: EDU_HEADER
      });
      const overview = overviewResp || buildOverviewFallback();

      const termOptions = buildTermOptions(overview.available_terms || []);
      const activeTerm = String(getOptionValue(termOptions, this.data.termIndex, overview.term || buildOverviewFallback().term) || overview.term);
      const termIndex = findOptionIndex(termOptions, activeTerm, 0);

      const weekOptions = buildWeekOptions(Array.from({ length: Number(overview.total_weeks || 18) }, (_, index) => index + 1));
      const overviewWeek = Number(overview.current_week || 1);
      const activeWeek = Number(getOptionValue(weekOptions, this.data.weekIndex, overviewWeek) || overviewWeek);
      const weekIndex = findOptionIndex(weekOptions, activeWeek, 0);

      const campusOptions = buildCampusOptions(overview.campuses || []);
      const activeCampus = String(getOptionValue(campusOptions, this.data.campusIndex, this.data.campusDisplay || DEFAULT_CAMPUS) || DEFAULT_CAMPUS);
      const campusIndex = findOptionIndex(campusOptions, activeCampus, 0);

      this.setData({
        overview,
        termOptions,
        termIndex,
        termDisplay: getOptionLabel(termOptions, termIndex, overview.term || ""),
        weekOptions,
        weekIndex,
        weekDisplay: getOptionLabel(weekOptions, weekIndex, `第 ${overviewWeek} 周`),
        campusOptions,
        campusIndex,
        campusDisplay: getOptionLabel(campusOptions, campusIndex, activeCampus)
      });

      if (action === "hall") {
        const [examsResp, freeResp] = await Promise.all([
          apiRequest({ url: "/api/client/edu/exams", method: "GET", header: EDU_HEADER }),
          apiRequest({
            url: `/api/client/edu/free-classrooms?campus=${encodeURIComponent(getOptionValue(campusOptions, campusIndex, DEFAULT_CAMPUS))}`,
            method: "GET",
            header: EDU_HEADER
          })
        ]);
        const rooms = (freeResp && freeResp.items) || [];
        this.setData({
          hallModules: buildHallModules(),
          summaryCards: buildHallStats(overview, (examsResp && examsResp.items) || [], rooms),
          footerNote: ACTION_CONFIG.hall.footerNote,
          loading: false
        });
        return;
      }

      if (action === "grades") {
        const gradesResp = await apiRequest({
          url: `/api/client/edu/grades?term=${encodeURIComponent(activeTerm)}`,
          method: "GET",
          header: EDU_HEADER
        });
        const safeTermOptions = buildTermOptions((gradesResp && gradesResp.terms) || overview.available_terms || []);
        const selectedTerm = String((gradesResp && gradesResp.term) || activeTerm || overview.term || "");
        const selectedTermIndex = findOptionIndex(safeTermOptions, selectedTerm, 0);
        this.setData({
          termOptions: safeTermOptions,
          termIndex: selectedTermIndex,
          termDisplay: getOptionLabel(safeTermOptions, selectedTermIndex, selectedTerm),
          summaryCards: buildGradeStats(overview, gradesResp || {}),
          items: normalizeGradeCards((gradesResp && gradesResp.items) || []),
          listTitle: `课程成绩 · ${selectedTerm}`,
          emptyText: "当前学期暂无成绩数据",
          footerNote: ACTION_CONFIG.grades.footerNote,
          loading: false
        });
        return;
      }

      if (action === "schedule") {
        const scheduleResp = await apiRequest({
          url: `/api/client/edu/schedule?week_no=${encodeURIComponent(String(activeWeek))}`,
          method: "GET",
          header: EDU_HEADER
        });
        const safeWeekOptions = buildWeekOptions((scheduleResp && scheduleResp.weeks) || Array.from({ length: Number(overview.total_weeks || 18) }, (_, index) => index + 1));
        const selectedWeek = Number((scheduleResp && scheduleResp.week_no) || activeWeek || overviewWeek);
        const selectedWeekIndex = findOptionIndex(safeWeekOptions, selectedWeek, 0);
        const scheduleItems = (scheduleResp && scheduleResp.items) || [];
        this.setData({
          weekOptions: safeWeekOptions,
          weekIndex: selectedWeekIndex,
          weekDisplay: getOptionLabel(safeWeekOptions, selectedWeekIndex, `第 ${selectedWeek} 周`),
          summaryCards: buildScheduleStats(scheduleItems, selectedWeek),
          items: normalizeScheduleCards(scheduleItems, this._focusToday),
          listTitle: `${String((scheduleResp && scheduleResp.term) || overview.term || "")} · 第 ${selectedWeek} 周课表`,
          emptyText: "当前周次暂无课程安排",
          footerNote: ACTION_CONFIG.schedule.footerNote,
          loading: false
        });
        return;
      }

      if (action === "free") {
        const freeResp = await apiRequest({
          url: `/api/client/edu/free-classrooms?campus=${encodeURIComponent(activeCampus)}`,
          method: "GET",
          header: EDU_HEADER
        });
        const safeCampusOptions = buildCampusOptions((freeResp && freeResp.campuses) || overview.campuses || []);
        const selectedCampus = String((freeResp && freeResp.campus) || activeCampus);
        const selectedCampusIndex = findOptionIndex(safeCampusOptions, selectedCampus, 0);

        this._freeItems = (freeResp && freeResp.items) || [];
        this._currentBuildings = (freeResp && freeResp.buildings) || [];

        const buildingOptions = buildBuildingOptions(this._currentBuildings);
        const currentBuildingValue = String(getOptionValue(this.data.buildingOptions, this.data.buildingIndex, ALL_BUILDINGS_VALUE));
        const buildingIndex = findOptionIndex(buildingOptions, currentBuildingValue, 0);

        this.setData({
          campusOptions: safeCampusOptions,
          campusIndex: selectedCampusIndex,
          campusDisplay: getOptionLabel(safeCampusOptions, selectedCampusIndex, selectedCampus),
          buildingOptions,
          buildingIndex,
          buildingDisplay: getOptionLabel(buildingOptions, buildingIndex, "全部教学楼"),
          footerNote: ACTION_CONFIG.free.footerNote,
          loading: false
        }, () => this.applyFreeSelection());
        return;
      }

      const examsResp = await apiRequest({
        url: "/api/client/edu/exams",
        method: "GET",
        header: EDU_HEADER
      });
      const examItems = (examsResp && examsResp.items) || [];
      this.setData({
        summaryCards: buildExamStats(examItems),
        items: normalizeExamCards(examItems),
        listTitle: "考试清单",
        emptyText: "当前暂无考试安排",
        footerNote: ACTION_CONFIG.exams.footerNote,
        loading: false
      });
    } catch (error) {
      this.setData({
        loading: false,
        error: (error && error.message) || "加载教务数据失败"
      });
    }
  }
});
