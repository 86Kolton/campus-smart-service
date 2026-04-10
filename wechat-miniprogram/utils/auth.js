const { apiRequest, saveTokens, getTokenInfo } = require("./request");
const GUEST_USERNAME_KEY = "client_guest_username";
const GUEST_PASSWORD_KEY = "client_guest_password";
const GUEST_DISPLAY_NAME = "校园访客";

function isPlaceholderDisplayName(value = "") {
  const text = String(value || "").trim();
  if (!text) return true;
  return ["校园访客", "微信访客", "微信用户", "访客", "游客"].includes(text);
}

function isNotFoundError(error) {
  const code = Number(error && error.statusCode || 0);
  const text = String(error && error.message || "").toLowerCase();
  return code === 404 || text.includes("not found");
}

function isCredentialError(error) {
  const code = Number(error && error.statusCode || 0);
  const text = String(error && error.message || "").toLowerCase();
  return code === 401 || text.includes("invalid_client_credentials");
}

function normalizeClientPayload(data = {}, guest = false) {
  const tokens = saveTokens(data || {});
  return { ...tokens, guest };
}

function loadGuestCredentials() {
  return {
    username: String(wx.getStorageSync(GUEST_USERNAME_KEY) || "").trim(),
    password: String(wx.getStorageSync(GUEST_PASSWORD_KEY) || "").trim()
  };
}

function saveGuestCredentials(username, password) {
  wx.setStorageSync(GUEST_USERNAME_KEY, String(username || "").trim());
  wx.setStorageSync(GUEST_PASSWORD_KEY, String(password || "").trim());
}

function clearGuestCredentials() {
  wx.removeStorageSync(GUEST_USERNAME_KEY);
  wx.removeStorageSync(GUEST_PASSWORD_KEY);
}

function buildGuestCredentials() {
  const seed = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return {
    username: `wx_${seed}`,
    password: `demo-${seed}-A1`,
    displayName: GUEST_DISPLAY_NAME
  };
}

async function loginWithGuest(username, password) {
  const data = await apiRequest({ url: "/api/client/auth/login", method: "POST", auth: false, data: { username, password } });
  return normalizeClientPayload(data, true);
}

async function registerGuest(username, password, displayName = GUEST_DISPLAY_NAME) {
  const data = await apiRequest({
    url: "/api/client/auth/register",
    method: "POST",
    auth: false,
    data: { username, password, display_name: String(displayName || "").trim() || GUEST_DISPLAY_NAME }
  });
  return normalizeClientPayload(data, true);
}

async function loginWithWechat(code, displayName = "") {
  const textCode = String(code || "").trim();
  if (!textCode) throw new Error("未获取到微信登录凭证");
  const safeDisplayName = isPlaceholderDisplayName(displayName) ? "" : String(displayName || "").trim();
  const data = await apiRequest({
    url: "/api/client/auth/wechat/login",
    method: "POST",
    auth: false,
    data: { code: textCode, display_name: safeDisplayName || null }
  });
  return normalizeClientPayload(data, false);
}

async function bindWechat(code) {
  const textCode = String(code || "").trim();
  if (!textCode) throw new Error("未获取到微信登录凭证");
  return apiRequest({
    url: "/api/client/auth/wechat/bind",
    method: "POST",
    data: { code: textCode }
  });
}

async function fetchClientMe() {
  const data = await apiRequest({ url: "/api/client/auth/me", method: "GET" });
  return data || {};
}

async function ensureClientSession() {
  const tokenInfo = getTokenInfo();
  if (tokenInfo.accessToken) {
    if (tokenInfo.displayName || tokenInfo.publicName) return { ...tokenInfo, guest: false };
    try {
      const me = await fetchClientMe();
      return normalizeClientPayload({
        access_token: tokenInfo.accessToken,
        refresh_token: tokenInfo.refreshToken,
        user_id: me.user_id,
        username: me.username,
        display_name: me.display_name,
        public_name: me.public_name
      }, false);
    } catch (error) {
      if (!isNotFoundError(error)) throw error;
    }
  }

  for (let attempt = 0; attempt < 2; attempt += 1) {
    let creds = loadGuestCredentials();
    if (!creds.username || !creds.password) {
      const next = buildGuestCredentials();
      saveGuestCredentials(next.username, next.password);
      creds = { username: next.username, password: next.password };
    }

    try {
      return await loginWithGuest(creds.username, creds.password);
    } catch (error) {
      if (!isCredentialError(error) && !isNotFoundError(error)) throw error;
    }

    const fresh = buildGuestCredentials();
    saveGuestCredentials(fresh.username, fresh.password);
    try {
      return await registerGuest(fresh.username, fresh.password, fresh.displayName);
    } catch (error) {
      const text = String(error && error.message || "").toLowerCase();
      if (text.includes("username_already_exists")) {
        clearGuestCredentials();
        continue;
      }
      if (isNotFoundError(error)) {
        return { accessToken: "", refreshToken: "", userId: 0, username: "", displayName: "", publicName: "", guest: true };
      }
      throw error;
    }
  }

  return { accessToken: "", refreshToken: "", userId: 0, username: "", displayName: "", publicName: "", guest: true };
}

module.exports = { bindWechat, ensureClientSession, loginWithGuest, loginWithWechat, registerGuest };
