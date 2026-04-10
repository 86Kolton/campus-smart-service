function getWeekdayLabel(day) {
  return ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][day] || "今日";
}

function formatGreetingDate(date = new Date()) {
  const current = date instanceof Date ? date : new Date(date);
  return `${getWeekdayLabel(current.getDay())} · ${current.getMonth() + 1}月${current.getDate()}日，欢迎回来`;
}

function extractDisplayName(rawName = "") {
  return String(rawName || "").replace(/^@/, "").replace(/同学$/u, "").trim();
}

function buildGreetingName(rawName = "") {
  const clean = extractDisplayName(rawName);
  if (!clean) return "同学";
  return `${clean.charAt(0)}同学`;
}

function getAvatarText(rawName = "") {
  const clean = extractDisplayName(rawName);
  if (!clean) return "CA";
  if (clean.length === 1) return `${clean}${clean}`.toUpperCase();
  return clean.slice(0, 2).toUpperCase();
}

function formatCompactCount(value) {
  const num = Number(value || 0);
  if (!Number.isFinite(num) || num <= 0) return "0";
  if (num >= 10000) return `${(num / 10000).toFixed(1)}w`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
  return String(num);
}

function normalizePostId(rawId = "") {
  const text = String(rawId || "").trim();
  if (!text) return "";
  if (text.startsWith("m-")) return `p-${text.slice(2)}`;
  return text;
}

function decodeRouteText(value = "", fallback = "") {
  const raw = String(value || "").trim();
  if (!raw) return fallback;
  try {
    return decodeURIComponent(raw);
  } catch (error) {
    return raw;
  }
}

function getClientDisplayName(fallback = "") {
  const app = typeof getApp === "function" ? getApp() : null;
  const candidate = app && app.globalData && app.globalData.client ? app.globalData.client.displayName : "";
  return extractDisplayName(candidate || fallback);
}

function getClientPublicName(fallback = "") {
  const app = typeof getApp === "function" ? getApp() : null;
  const candidate = app && app.globalData && app.globalData.client ? app.globalData.client.publicName : "";
  return extractDisplayName(candidate || fallback);
}

function syncTabBar(page, selected) {
  if (!page || typeof page.getTabBar !== "function") return;
  const tabBar = page.getTabBar();
  if (!tabBar || typeof tabBar.setData !== "function") return;
  const app = typeof getApp === "function" ? getApp() : null;
  tabBar.setData({ selected: Number(selected) || 0, profileDot: Boolean(app && app.globalData && app.globalData.profileDot) });
}

module.exports = { buildGreetingName, decodeRouteText, extractDisplayName, formatCompactCount, formatGreetingDate, getAvatarText, getClientDisplayName, getClientPublicName, normalizePostId, syncTabBar };