const { buildApiUrl } = require("../config/env");

const ACCESS_TOKEN_KEY = "client_access_token";
const REFRESH_TOKEN_KEY = "client_refresh_token";
const USER_ID_KEY = "client_user_id";
const USERNAME_KEY = "client_username";
const DISPLAY_NAME_KEY = "client_display_name";
const PUBLIC_NAME_KEY = "client_public_name";

function getTokenInfo() {
  return {
    accessToken: wx.getStorageSync(ACCESS_TOKEN_KEY) || "",
    refreshToken: wx.getStorageSync(REFRESH_TOKEN_KEY) || "",
    userId: Number(wx.getStorageSync(USER_ID_KEY) || 0),
    username: wx.getStorageSync(USERNAME_KEY) || "",
    displayName: wx.getStorageSync(DISPLAY_NAME_KEY) || "",
    publicName: wx.getStorageSync(PUBLIC_NAME_KEY) || ""
  };
}

function saveTokens(payload = {}) {
  const accessToken = String(payload.access_token || payload.accessToken || "").trim();
  const refreshToken = String(payload.refresh_token || payload.refreshToken || "").trim();
  const userId = Number(payload.user_id || payload.userId || 0);
  const username = String(payload.username || "").trim();
  const displayName = String(payload.display_name || payload.displayName || "").trim();
  const publicName = String(payload.public_name || payload.publicName || "").trim();

  if (accessToken) wx.setStorageSync(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) wx.setStorageSync(REFRESH_TOKEN_KEY, refreshToken);
  if (userId > 0) wx.setStorageSync(USER_ID_KEY, userId);
  if (username) wx.setStorageSync(USERNAME_KEY, username);
  if (displayName) wx.setStorageSync(DISPLAY_NAME_KEY, displayName);
  if (publicName) wx.setStorageSync(PUBLIC_NAME_KEY, publicName);

  return { accessToken, refreshToken, userId, username, displayName, publicName };
}

function clearTokens() {
  wx.removeStorageSync(ACCESS_TOKEN_KEY);
  wx.removeStorageSync(REFRESH_TOKEN_KEY);
  wx.removeStorageSync(USER_ID_KEY);
  wx.removeStorageSync(USERNAME_KEY);
  wx.removeStorageSync(DISPLAY_NAME_KEY);
  wx.removeStorageSync(PUBLIC_NAME_KEY);
}

function parseErrorMessage(responseData, statusCode) {
  if (responseData && typeof responseData === "object") {
    if (typeof responseData.detail === "string" && responseData.detail.trim()) return responseData.detail;
    if (typeof responseData.message === "string" && responseData.message.trim()) return responseData.message;
  }
  if (statusCode === 404) return "当前接口或内容不存在";
  if (statusCode === 401) return "登录状态已失效";
  if (statusCode >= 500) return "服务暂时不可用";
  if (!responseData) return statusCode ? `http_${statusCode}` : "network_error";
  if (typeof responseData === "string") {
    const text = responseData.trim();
    if (!text) return statusCode ? `http_${statusCode}` : "request_failed";
    if (/not found/i.test(text)) return "当前接口或内容不存在";
    return text;
  }
  return statusCode ? `http_${statusCode}` : "request_failed";
}

function buildAuthHeader(auth = true, extraHeader = {}) {
  const tokens = getTokenInfo();
  const finalHeader = { ...extraHeader };
  if (auth && tokens.accessToken) finalHeader.Authorization = `Bearer ${tokens.accessToken}`;
  return finalHeader;
}

function rawRequest({ url, method = "GET", data = undefined, auth = true, header = {}, timeout = 20000 }) {
  const finalHeader = { "content-type": "application/json", ...buildAuthHeader(auth, header) };
  return new Promise((resolve, reject) => {
    wx.request({
      url: buildApiUrl(url),
      method,
      data,
      header: finalHeader,
      timeout,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        reject({ statusCode: res.statusCode, data: res.data, message: parseErrorMessage(res.data, res.statusCode) });
      },
      fail(err) {
        reject({ statusCode: 0, data: null, message: err && err.errMsg ? err.errMsg : "network_error" });
      }
    });
  });
}

function rawUploadFile({ url, filePath, name = "image", formData = {}, auth = true, header = {}, timeout = 30000 }) {
  const finalHeader = buildAuthHeader(auth, header);
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: buildApiUrl(url),
      filePath,
      name,
      formData,
      header: finalHeader,
      timeout,
      success(res) {
        let responseData = null;
        try {
          responseData = JSON.parse(res.data || "{}");
        } catch (error) {
          responseData = res.data;
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(responseData);
          return;
        }
        reject({ statusCode: res.statusCode, data: responseData, message: parseErrorMessage(responseData, res.statusCode) });
      },
      fail(err) {
        reject({ statusCode: 0, data: null, message: err && err.errMsg ? err.errMsg : "upload_failed" });
      }
    });
  });
}

async function refreshAccessToken() {
  const { refreshToken } = getTokenInfo();
  if (!refreshToken) return false;
  try {
    const data = await rawRequest({ url: "/api/client/auth/refresh", method: "POST", auth: false, data: { refresh_token: refreshToken } });
    saveTokens(data || {});
    return true;
  } catch (error) {
    clearTokens();
    return false;
  }
}

async function apiRequest(options, retryOn401 = true) {
  try {
    return await rawRequest(options);
  } catch (error) {
    if (retryOn401 && options && options.auth !== false && Number(error && error.statusCode || 0) === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) return apiRequest(options, false);
    }
    throw error;
  }
}

async function uploadFile(options, retryOn401 = true) {
  try {
    return await rawUploadFile(options);
  } catch (error) {
    if (retryOn401 && options && options.auth !== false && Number(error && error.statusCode || 0) === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) return uploadFile(options, false);
    }
    throw error;
  }
}

module.exports = { apiRequest, clearTokens, getTokenInfo, refreshAccessToken, saveTokens, uploadFile };
