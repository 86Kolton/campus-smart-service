const { ensureClientSession } = require("./utils/auth");
const { getApiBaseUrl } = require("./config/env");

App({
  globalData: {
    apiBaseUrl: getApiBaseUrl(),
    client: null,
    clientReady: false,
    clientError: "",
    profileDot: false
  },

  onLaunch() {
    // Do not block initial routing on network login.
    this.warmupSession();
  },

  warmupSession() {
    if (this._warmupPromise) {
      return this._warmupPromise;
    }

    this._warmupPromise = ensureClientSession()
      .then((client) => {
        this.globalData.client = client;
        this.globalData.clientReady = true;
        this.globalData.clientError = "";
        return client;
      })
      .catch((error) => {
        this.globalData.clientReady = false;
        this.globalData.clientError = error?.message || "login_failed";
        throw error;
      })
      .finally(() => {
        this._warmupPromise = null;
      });

    return this._warmupPromise;
  },

  async ensureSession(force = false) {
    if (force) {
      wx.removeStorageSync("client_access_token");
      wx.removeStorageSync("client_refresh_token");
      this.globalData.client = null;
      this.globalData.clientReady = false;
    }

    if (this.globalData.clientReady && this.globalData.client) {
      return this.globalData.client;
    }

    if (!force && this._warmupPromise) {
      try {
        await this._warmupPromise;
      } catch (error) {
        // Keep going and retry once below.
      }
      if (this.globalData.clientReady && this.globalData.client) {
        return this.globalData.client;
      }
    }

    const client = await ensureClientSession();
    this.globalData.client = client;
    this.globalData.clientReady = true;
    this.globalData.clientError = "";
    return client;
  }
});
