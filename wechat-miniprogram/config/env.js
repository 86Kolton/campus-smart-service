const API_BASE_KEY = "api_base_url";
const DEFAULT_API_BASE_URL = "https://rag-user.yyaxx.cc";
const LEGACY_API_BASE_URLS = new Set([
  "http://116.204.132.58:8000",
  "https://116.204.132.58:8000",
  "http://rag-user.yyaxx.cc",
  "https://rag-user.yyaxx.cc:8000",
  "http://rag.yyaxx.cc",
  "https://rag.yyaxx.cc:8000",
  "https://rag.yyaxx.cc"
]);

function normalizeApiBaseUrl(value) {
  const text = String(value || "").trim();
  if (!text) {
    return DEFAULT_API_BASE_URL;
  }
  const normalized = text.replace(/\/+$/, "");
  if (LEGACY_API_BASE_URLS.has(normalized)) {
    return DEFAULT_API_BASE_URL;
  }
  return normalized;
}

function getApiBaseUrl() {
  const local = wx.getStorageSync(API_BASE_KEY);
  return normalizeApiBaseUrl(local || DEFAULT_API_BASE_URL);
}

function setApiBaseUrl(value) {
  const next = normalizeApiBaseUrl(value);
  wx.setStorageSync(API_BASE_KEY, next);
  return next;
}

function buildApiUrl(path) {
  if (!path) {
    return getApiBaseUrl();
  }
  const source = String(path);
  if (/^https?:\/\//i.test(source)) {
    return source;
  }
  const base = getApiBaseUrl();
  return `${base}${source.startsWith("/") ? "" : "/"}${source}`;
}

module.exports = {
  API_BASE_KEY,
  DEFAULT_API_BASE_URL,
  normalizeApiBaseUrl,
  getApiBaseUrl,
  setApiBaseUrl,
  buildApiUrl
};


