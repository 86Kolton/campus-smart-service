(() => {
  const API_BASE = window.location.origin;
  const TOKEN_KEY = "campus_admin_token";
  const policyState = {
    max_attempts: 5,
    lock_minutes: 20,
    window_minutes: 10,
  };

  const byId = (id) => document.getElementById(id);

  const parseError = async (response) => {
    try {
      const payload = await response.json();
      if (payload && Object.prototype.hasOwnProperty.call(payload, "detail")) {
        return payload.detail;
      }
      return payload;
    } catch {
      return response.statusText || `http_${response.status}`;
    }
  };

  const getErrorPayload = (value) => {
    if (value instanceof Error) return value.message;
    return value;
  };

  const formatDuration = (seconds) => {
    const total = Math.max(0, Number(seconds || 0));
    const mins = Math.floor(total / 60);
    const secs = total % 60;
    if (mins && secs) return `${mins} 分 ${secs} 秒`;
    if (mins) return `${mins} 分钟`;
    return `${Math.max(1, secs)} 秒`;
  };

  const applyPolicy = (payload = {}) => {
    const nextMaxAttempts = Number(payload.max_attempts || 0);
    const nextLockMinutes = Number(payload.lock_minutes || 0);
    const nextWindowMinutes = Number(payload.window_minutes || 0);
    if (nextMaxAttempts > 0) policyState.max_attempts = nextMaxAttempts;
    if (nextLockMinutes > 0) policyState.lock_minutes = nextLockMinutes;
    if (nextWindowMinutes > 0) policyState.window_minutes = nextWindowMinutes;

    const summary = byId("guardSummary");
    const detail = byId("guardDetail");
    const hint = byId("guardHint");
    if (summary) {
      summary.textContent = `同设备连续失败 ${policyState.max_attempts} 次后，会锁定 ${policyState.lock_minutes} 分钟。`;
    }
    if (detail) {
      detail.textContent = `统计窗口 ${policyState.window_minutes} 分钟。成功登录后会清零失败计数。`;
    }
    if (hint) {
      hint.textContent = `当前策略：最多 ${policyState.max_attempts} 次尝试，锁定 ${policyState.lock_minutes} 分钟。`;
    }
  };

  const applyGuardFeedback = (raw) => {
    const detail = getErrorPayload(raw);
    if (!detail || typeof detail !== "object") return;
    applyPolicy(detail);
    const guardDetail = byId("guardDetail");
    const guardHint = byId("guardHint");
    if (detail.code === "invalid_admin_credentials") {
      const remaining = Math.max(0, Number(detail.remaining_attempts || 0));
      if (guardDetail) {
        guardDetail.textContent = `本轮还可再试 ${remaining} 次；达到 ${policyState.max_attempts} 次失败后会锁定 ${policyState.lock_minutes} 分钟。`;
      }
      if (guardHint) {
        guardHint.textContent = `剩余尝试次数：${remaining} / ${policyState.max_attempts}。`;
      }
      return;
    }
    if (detail.code === "admin_login_temporarily_blocked") {
      const wait = formatDuration(detail.retry_after_seconds);
      if (guardDetail) {
        guardDetail.textContent = `当前设备已被锁定，还需等待 ${wait} 后才能继续尝试。`;
      }
      if (guardHint) {
        guardHint.textContent = `锁定中：剩余 ${wait}。锁定时长 ${policyState.lock_minutes} 分钟。`;
      }
    }
  };

  const formatUiError = (raw) => {
    const detail = getErrorPayload(raw);
    if (detail && typeof detail === "object") {
      if (detail.code === "admin_login_temporarily_blocked") {
        return `当前设备已被临时锁定，还需等待 ${formatDuration(detail.retry_after_seconds)} 后再试。`;
      }
      if (detail.code === "invalid_admin_credentials") {
        return `账号或密码错误。还可再试 ${Math.max(0, Number(detail.remaining_attempts || 0))} 次。`;
      }
    }
    const text = String(detail || "");
    const blocked = text.match(/admin_login_temporarily_blocked:(\d+)/);
    if (blocked) {
      return `当前设备已被临时锁定，还需等待 ${formatDuration(Number(blocked[1] || 0))} 后再试。`;
    }
    if (text.includes("invalid admin credentials")) {
      return "账号或密码错误。";
    }
    return text || "登录失败，请稍后再试。";
  };

  const setStateText = (text) => {
    const node = byId("authState");
    if (node) {
      node.textContent = text;
    }
  };

  const setPasswordVisible = (visible) => {
    const input = byId("adminPassword");
    const toggle = byId("togglePassword");
    if (!input || !toggle) return;
    input.type = visible ? "text" : "password";
    toggle.textContent = visible ? "隐藏" : "显示";
    toggle.setAttribute("aria-label", visible ? "隐藏密码" : "显示密码");
  };

  const redirectToWorkspace = () => {
    window.location.replace("./");
  };

  const verifyExistingToken = async () => {
    const token = localStorage.getItem(TOKEN_KEY) || "";
    if (!token) {
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/api/admin/devtools/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        redirectToWorkspace();
        return;
      }
      localStorage.removeItem(TOKEN_KEY);
    } catch {
      localStorage.removeItem(TOKEN_KEY);
    }
  };

  const loadPolicy = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/admin/auth/policy`);
      if (!response.ok) return;
      applyPolicy(await response.json());
    } catch {
      applyPolicy();
    }
  };

  const login = async () => {
    const username = String(byId("adminUsername")?.value || "").trim();
    const password = String(byId("adminPassword")?.value || "");
    if (!username || !password) {
      setStateText("请输入账号和密码。");
      return;
    }

    setStateText("正在验证登录信息...");
    const response = await fetch(`${API_BASE}/api/admin/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw await parseError(response);
    }

    const payload = await response.json();
    localStorage.setItem(TOKEN_KEY, payload.access_token || "");
    setStateText("登录成功，正在进入工作台...");
    redirectToWorkspace();
  };

  const bindEvents = () => {
    byId("btnLogin")?.addEventListener("click", async () => {
      try {
        await login();
      } catch (error) {
        applyGuardFeedback(error);
        setStateText(formatUiError(error));
      }
    });

    ["adminUsername", "adminPassword"].forEach((id) => byId(id)?.addEventListener("keydown", async (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      try {
        await login();
      } catch (error) {
        applyGuardFeedback(error);
        setStateText(formatUiError(error));
      }
    }));

    byId("togglePassword")?.addEventListener("click", () => {
      const input = byId("adminPassword");
      setPasswordVisible(String(input?.type || "password") === "password");
    });
  };

  const boot = async () => {
    bindEvents();
    applyPolicy();
    setPasswordVisible(false);
    await loadPolicy();
    await verifyExistingToken();
  };

  boot();
})();
