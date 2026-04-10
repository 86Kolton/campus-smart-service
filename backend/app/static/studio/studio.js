(() => {
  const API_BASE = window.location.origin;
  const TOKEN_KEY = "campus_admin_token";
  const CLIENT_TOKEN_KEY = "campus_client_token";
  const DEFAULT_SCREEN = "overview";
  const PAGE_SIZES = { kb: 6, docs: 8, tasks: 8, logs: 6, reviews: 6, adoptions: 6 };
  const SECRET_KEYS = new Set(["WECHAT_APP_SECRET", "QA_API_KEY", "EVOLUTION_AI_REVIEW_API_KEY", "RERANK_API_KEY", "EMBEDDING_API_KEY"]);
  const NUMBER_KEYS = new Set(["QA_TIMEOUT_SECONDS", "EMBEDDING_DIM", "EMBEDDING_TIMEOUT_SECONDS", "RERANK_TIMEOUT_SECONDS", "WECHAT_TIMEOUT_SECONDS"]);
  const DEFAULT_CONFIG_KEYS = [
    "QA_PROVIDER",
    "QA_BASE_URL",
    "QA_API_KEY",
    "QA_MODEL",
    "QA_TIMEOUT_SECONDS",
    "EVOLUTION_AI_REVIEW_ENABLED",
    "EVOLUTION_AI_REVIEW_PROVIDER",
    "EVOLUTION_AI_REVIEW_BASE_URL",
    "EVOLUTION_AI_REVIEW_API_KEY",
    "EVOLUTION_AI_REVIEW_MODEL",
    "EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS",
    "EVOLUTION_AI_REVIEW_MIN_SCORE",
    "EMBEDDING_PROVIDER",
    "EMBEDDING_BASE_URL",
    "EMBEDDING_API_KEY",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIM",
    "EMBEDDING_TIMEOUT_SECONDS",
    "RERANK_PROVIDER",
    "RERANK_BASE_URL",
    "RERANK_API_KEY",
    "RERANK_MODEL",
    "QDRANT_URL",
    "QDRANT_COLLECTION",
    "WECHAT_APP_ID",
    "WECHAT_APP_SECRET",
    "WECHAT_CODE2SESSION_URL",
    "WECHAT_TIMEOUT_SECONDS",
    "WECHAT_MOCK_ENABLED",
    "BOOTSTRAP_DEMO_DATA",
  ];
  const CONFIG_GROUPS = [
    { key: "qa", title: "QA 问答模型", desc: "主问答模型与接口地址。", keys: ["QA_PROVIDER", "QA_BASE_URL", "QA_API_KEY", "QA_MODEL", "QA_TIMEOUT_SECONDS"], cols: 2 },
    {
      key: "evolution",
      title: "自进化 AI 审核",
      desc: "高质量帖子进入知识库前的审核模型与阈值。",
      keys: ["EVOLUTION_AI_REVIEW_ENABLED", "EVOLUTION_AI_REVIEW_PROVIDER", "EVOLUTION_AI_REVIEW_BASE_URL", "EVOLUTION_AI_REVIEW_API_KEY", "EVOLUTION_AI_REVIEW_MODEL", "EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS", "EVOLUTION_AI_REVIEW_MIN_SCORE"],
      cols: 3,
    },
    {
      key: "embedding",
      title: "Embedding 向量模型",
      desc: "用于入库向量化与检索。",
      keys: ["EMBEDDING_PROVIDER", "EMBEDDING_BASE_URL", "EMBEDDING_API_KEY", "EMBEDDING_MODEL", "EMBEDDING_DIM", "EMBEDDING_TIMEOUT_SECONDS"],
      cols: 3,
    },
    { key: "rerank", title: "Rerank 重排模型", desc: "深度检索时启用。", keys: ["RERANK_PROVIDER", "RERANK_BASE_URL", "RERANK_API_KEY", "RERANK_MODEL"], cols: 2 },
    { key: "vector", title: "向量库", desc: "Qdrant 存储配置。", keys: ["QDRANT_URL", "QDRANT_COLLECTION"], cols: 2 },
    { key: "wechat", title: "微信登录", desc: "小程序登录与绑定相关配置。", keys: ["WECHAT_APP_ID", "WECHAT_APP_SECRET", "WECHAT_CODE2SESSION_URL", "WECHAT_TIMEOUT_SECONDS", "WECHAT_MOCK_ENABLED"], cols: 2 },
    { key: "runtime", title: "Runtime Guards", desc: "Deployment-safe startup switches.", keys: ["BOOTSTRAP_DEMO_DATA"], cols: 1 },
  ];
  const SELECT_OPTIONS = {
    QA_PROVIDER: ["openai_compatible", "openai", "siliconflow", "none"],
    EVOLUTION_AI_REVIEW_ENABLED: ["true", "false"],
    EVOLUTION_AI_REVIEW_PROVIDER: ["qa_reuse", "openai_compatible", "siliconflow", "none"],
    EMBEDDING_PROVIDER: ["openai_compatible", "local_stub", "siliconflow", "none"],
    RERANK_PROVIDER: ["none", "openai_compatible", "siliconflow"],
    WECHAT_MOCK_ENABLED: ["true", "false"],
    BOOTSTRAP_DEMO_DATA: ["true", "false"],
  };
  const MODEL_HINTS = {
    QA_MODEL: ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen3.5-9B", "deepseek-ai/DeepSeek-V3", "THUDM/GLM-4-9B-Chat"],
    EVOLUTION_AI_REVIEW_MODEL: ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen3.5-9B", "deepseek-ai/DeepSeek-V3"],
    EMBEDDING_MODEL: ["BAAI/bge-m3", "Qwen/Qwen3-Embedding-4B", "BAAI/bge-large-zh-v1.5"],
    RERANK_MODEL: ["Qwen/Qwen3-Reranker-0.6B", "BAAI/bge-reranker-v2-m3", "Qwen/Qwen3-Reranker-4B"],
  };
  const MODEL_KEYS = new Set(Object.keys(MODEL_HINTS));
  const CUSTOM_MODEL_VALUE = "__custom__";
  const SCREENS = new Set(["overview", "config", "kb", "ingest", "qa", "ops"]);
  const state = {
    token: localStorage.getItem(TOKEN_KEY) || "",
    clientToken: localStorage.getItem(CLIENT_TOKEN_KEY) || "",
    kbItems: [],
    collections: { kb: [], docs: [], tasks: [], logs: [], reviews: [], adoptions: [] },
    pagers: {},
    status: null,
    lastEvolution: null,
    lastCleanup: null,
  };

  const byId = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  const now = () => new Date().toLocaleString("zh-CN", { hour12: false });
  const setWorkspaceStatus = (text) => { const node = byId("workspaceStatusText"); if (node) node.textContent = text; };
  const redirectToLogin = () => window.location.replace("./login.html");
  const normalizeScreen = (value) => { const next = String(value || "").replace(/^#/, "").trim(); return SCREENS.has(next) ? next : DEFAULT_SCREEN; };

  const log = (text, level = "info") => {
    const box = byId("console");
    if (!box) return;
    const prefix = level === "error" ? "[ERR]" : level === "ok" ? "[OK]" : "[INFO]";
    box.textContent = `${now()} ${prefix} ${text}\n${box.textContent}`.slice(0, 10000);
  };

  const formatUiError = (message) => {
    const text = String(message || "");
    const blocked = text.match(/admin_login_temporarily_blocked:(\d+)/);
    if (blocked) {
      return `当前设备登录失败次数过多，已被临时限制 ${Math.max(1, Math.ceil(Number(blocked[1] || 0) / 60))} 分钟`;
    }
    return text;
  };

  const parseError = async (response) => {
    try {
      const payload = await response.json();
      return payload && typeof payload.detail === "string" ? payload.detail : JSON.stringify(payload);
    } catch {
      return response.statusText || `http_${response.status}`;
    }
  };

  const logout = (notify = true) => {
    state.token = "";
    localStorage.removeItem(TOKEN_KEY);
    if (notify) log("已退出登录", "ok");
    redirectToLogin();
  };

  const api = async (path, options = {}) => {
    const { method = "GET", auth = true, headers = {}, body, noJson = false } = options;
    const finalHeaders = { ...headers };
    if (auth) {
      if (!state.token) {
        redirectToLogin();
        throw new Error("请先登录后台");
      }
      finalHeaders.Authorization = `Bearer ${state.token}`;
    }
    const isFormData = body instanceof FormData;
    if (body && !isFormData && !finalHeaders["Content-Type"]) finalHeaders["Content-Type"] = "application/json";
    const response = await fetch(`${API_BASE}${path}`, {
      method,
      headers: finalHeaders,
      body: isFormData ? body : body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
      if (response.status === 401 && auth) logout(false);
      throw new Error(`${response.status}: ${await parseError(response)}`);
    }
    if (noJson || response.status === 204) return {};
    return response.json();
  };

  const clientLogin = async () => {
    if (state.clientToken) return state.clientToken;
    const payload = await api("/api/admin/devtools/client-debug-token", { method: "POST" });
    state.clientToken = payload.access_token || "";
    if (!state.clientToken) {
      throw new Error("client_debug_token_missing");
    }
    localStorage.setItem(CLIENT_TOKEN_KEY, state.clientToken);
    return state.clientToken;
  };

  const setActiveScreen = (screen, { updateHash = true } = {}) => {
    const next = normalizeScreen(screen);
    document.querySelectorAll(".screen").forEach((node) => node.classList.toggle("is-active", node.dataset.screen === next));
    document.querySelectorAll(".workspace-nav-btn").forEach((node) => node.classList.toggle("is-active", node.dataset.screen === next));
    if (updateHash) window.history.replaceState(null, "", `#${next}`);
  };

  const renderPills = (containerId, items) => {
    const node = byId(containerId);
    if (!node) return;
    node.innerHTML = (items || [])
      .filter((item) => item && item.label)
      .map((item) => `<span class="stat-pill">${esc(item.label)}：${esc(item.value)}</span>`)
      .join("");
  };

  const getPagerState = (key, total) => {
    const pageSize = PAGE_SIZES[key] || 6;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const page = Math.min(Math.max(1, Number(state.pagers[key] || 1)), totalPages);
    state.pagers[key] = page;
    return { page, pageSize, totalPages };
  };

  const buildPager = (key, total, page, totalPages) => `
    <div class="pager">
      <button class="pager-btn ghost" type="button" data-pager-key="${esc(key)}" data-pager-dir="-1" ${page <= 1 ? "disabled" : ""}>上一页</button>
      <span class="pager-text">${page} / ${totalPages} · 共 ${total} 条</span>
      <button class="pager-btn ghost" type="button" data-pager-key="${esc(key)}" data-pager-dir="1" ${page >= totalPages ? "disabled" : ""}>下一页</button>
    </div>
  `;

  const renderPagedTable = ({ key, containerId, columns, items, emptyText, rowRenderer }) => {
    const container = byId(containerId);
    if (!container) return;
    if (!Array.isArray(items) || !items.length) {
      container.innerHTML = `<div class="empty-state">${esc(emptyText)}</div>`;
      return;
    }
    const { page, pageSize, totalPages } = getPagerState(key, items.length);
    const rows = items.slice((page - 1) * pageSize, (page - 1) * pageSize + pageSize);
    container.innerHTML = `
      <div class="table-meta"><span>当前展示第 ${page} 页</span></div>
      <div class="table-shell">
        <table class="data-table">
          <thead><tr>${columns.map((label) => `<th>${esc(label)}</th>`).join("")}</tr></thead>
          <tbody>${rows.map((item) => `<tr>${rowRenderer(item)}</tr>`).join("")}</tbody>
        </table>
      </div>
      ${buildPager(key, items.length, page, totalPages)}
    `;
  };

  const getConfigFieldLabel = (key) => ({
    WECHAT_APP_ID: "微信小程序 AppID",
    WECHAT_APP_SECRET: "微信小程序 AppSecret",
    WECHAT_CODE2SESSION_URL: "微信 code2session 地址",
    WECHAT_TIMEOUT_SECONDS: "微信请求超时（秒）",
    WECHAT_MOCK_ENABLED: "微信开发兜底模式",
    BOOTSTRAP_DEMO_DATA: "Demo 数据启动注入",
    QA_PROVIDER: "QA Provider",
    QA_BASE_URL: "QA 接口地址",
    QA_API_KEY: "QA API Key",
    QA_MODEL: "QA 模型名",
    QA_TIMEOUT_SECONDS: "QA 超时（秒）",
    EVOLUTION_AI_REVIEW_ENABLED: "AI 审核开关",
    EVOLUTION_AI_REVIEW_PROVIDER: "AI 审核 Provider",
    EVOLUTION_AI_REVIEW_BASE_URL: "AI 审核接口地址",
    EVOLUTION_AI_REVIEW_API_KEY: "AI 审核 API Key",
    EVOLUTION_AI_REVIEW_MODEL: "AI 审核模型名",
    EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS: "AI 审核超时（秒）",
    EVOLUTION_AI_REVIEW_MIN_SCORE: "最低通过分",
    EMBEDDING_PROVIDER: "Embedding Provider",
    EMBEDDING_BASE_URL: "Embedding 接口地址",
    EMBEDDING_API_KEY: "Embedding API Key",
    EMBEDDING_MODEL: "Embedding 模型名",
    EMBEDDING_DIM: "Embedding 向量维度",
    EMBEDDING_TIMEOUT_SECONDS: "Embedding 超时（秒）",
    RERANK_PROVIDER: "Rerank Provider",
    RERANK_BASE_URL: "Rerank 接口地址",
    RERANK_API_KEY: "Rerank API Key",
    RERANK_MODEL: "Rerank 模型名",
    QDRANT_URL: "Qdrant 地址",
    QDRANT_COLLECTION: "Qdrant Collection",
  }[key] || key);

  const renderSelectOptions = (key, value) => {
    const options = Array.isArray(SELECT_OPTIONS[key]) ? SELECT_OPTIONS[key] : [];
    if (!options.length) return "";
    const current = String(value ?? "");
    const rows = options.includes(current) || !current ? [...options] : [current, ...options];
    return rows.map((item) => `<option value="${esc(item)}"${String(item) === current ? " selected" : ""}>${esc(item)}</option>`).join("");
  };

  const renderConfigField = (key, value = "") => {
    const current = String(value ?? "");
    if (MODEL_KEYS.has(key)) {
      const preset = (MODEL_HINTS[key] || []).includes(current) ? current : CUSTOM_MODEL_VALUE;
      const options = [
        { value: "", label: "选择预设模型" },
        ...(MODEL_HINTS[key] || []).map((item) => ({ value: item, label: item })),
        { value: CUSTOM_MODEL_VALUE, label: "自定义输入" },
      ];
      return `
        <label class="config-model-field">
          ${esc(getConfigFieldLabel(key))}
          <select data-model-preset-key="${esc(key)}" data-model-custom="${esc(CUSTOM_MODEL_VALUE)}">
            ${options.map((item) => `<option value="${esc(item.value)}"${item.value === preset ? " selected" : ""}>${esc(item.label)}</option>`).join("")}
          </select>
          <input data-config-key="${esc(key)}" data-secret="false" type="text" value="${esc(current)}" placeholder="可手动输入任意模型名" autocomplete="off" />
        </label>
      `;
    }
    if (SELECT_OPTIONS[key]) {
      return `<label>${esc(getConfigFieldLabel(key))}<select data-config-key="${esc(key)}" data-secret="false">${renderSelectOptions(key, current)}</select></label>`;
    }
    if (SECRET_KEYS.has(key)) {
      const placeholder = current ? `已保存：${current}` : "未设置（输入后保存）";
      return `<label>${esc(getConfigFieldLabel(key))}<input data-config-key="${esc(key)}" data-secret="true" type="password" value="" placeholder="${esc(placeholder)}" autocomplete="off" /></label>`;
    }
    return `<label>${esc(getConfigFieldLabel(key))}<input data-config-key="${esc(key)}" data-secret="false" type="${NUMBER_KEYS.has(key) ? "number" : "text"}" value="${esc(current)}" autocomplete="off" /></label>`;
  };

  const findConfigInputByKey = (key) => Array.from(document.querySelectorAll("#configForm input[data-config-key]")).find((node) => String(node.dataset.configKey || "") === key) || null;

  const syncModelPresetControls = () => {
    document.querySelectorAll("#configForm select[data-model-preset-key]").forEach((select) => {
      const key = String(select.dataset.modelPresetKey || "");
      const input = findConfigInputByKey(key);
      if (!input) return;
      select.value = (MODEL_HINTS[key] || []).includes(String(input.value || "").trim()) ? String(input.value || "").trim() : CUSTOM_MODEL_VALUE;
    });
  };

  const renderConfig = (payload) => {
    const container = byId("configForm");
    if (!container) return;
    const masked = payload?.masked || {};
    const keys = Array.isArray(payload?.editable_keys) && payload.editable_keys.length ? payload.editable_keys : DEFAULT_CONFIG_KEYS;
    const used = new Set();
    const groups = CONFIG_GROUPS.map((group) => {
      const groupKeys = group.keys.filter((key) => keys.includes(key));
      groupKeys.forEach((key) => used.add(key));
      return { ...group, keys: groupKeys };
    }).filter((group) => group.keys.length);
    const extraKeys = keys.filter((key) => !used.has(key));
    if (extraKeys.length) groups.push({ key: "extra", title: "其他配置", desc: "保留项，按原始键名展示。", keys: extraKeys, cols: 2 });
    container.innerHTML = groups.map((group) => `
      <section class="config-group">
        <div class="config-group-head"><h4>${esc(group.title)}</h4><p>${esc(group.desc || "")}</p></div>
        <div class="config-fields cols-${Number(group.cols || 2)}">${group.keys.map((key) => renderConfigField(key, masked[key] || "")).join("")}</div>
      </section>
    `).join("");
  };

  const renderStatus = (status) => {
    state.status = status;
    const cards = [
      { title: "运行环境", value: status.app_env, meta: `时间 ${status.now_iso}` },
      { title: "知识库 / 文档", value: `${status.knowledge_base_count} / ${status.document_count}`, meta: "总知识库 / 总文档" },
      { title: "失败任务 / QA 日志", value: `${status.failed_task_count} / ${status.qa_log_count}`, meta: "待关注 / 已记录" },
      {
        title: "关键配置",
        badges: [
          { label: "QA", ok: Boolean(status.qa_configured) },
          { label: `Embedding ${status.embedding_provider || "-"}`, ok: Boolean(status.embedding_configured) },
          { label: "Rerank", ok: Boolean(status.rerank_configured) },
          { label: "WeChat", ok: Boolean(status.wechat_configured) },
        ],
        meta: "当前生效配置",
      },
    ];
    const node = byId("statusCards");
    if (!node) return;
    node.innerHTML = cards.map((item) => `
      <article class="metric-card ${item.badges ? "metric-card-badges" : ""}">
        <span>${esc(item.title)}</span>
        ${item.badges
          ? `<div class="metric-badges">${item.badges.map((badge) => `<span class="metric-badge ${badge.ok ? "is-ok" : "is-off"}">${esc(badge.label)}${badge.ok ? "" : " 未配"}</span>`).join("")}</div>`
          : `<strong>${esc(item.value)}</strong>`}
        <small>${esc(item.meta)}</small>
      </article>
    `).join("");
  };

  const renderSelfCheck = (items) => {
    const node = byId("selfCheckResult");
    if (!node) return;
    if (!Array.isArray(items) || !items.length) {
      node.innerHTML = '<div class="empty-state">暂无自检结果</div>';
      return;
    }
    node.innerHTML = items.map((item) => `
      <div class="table-meta">
        <div><strong>${esc(item.name)}</strong><div class="hint">${esc(item.detail || "")}</div></div>
        <span class="status-pill ${item.passed ? "ok" : "bad"}">${item.passed ? "通过" : "失败"}</span>
      </div>
    `).join("");
  };

  const renderKbSelectors = (items) => {
    const docSelect = byId("docKbSelect");
    const evoSelect = byId("evoKbId");
    if (!docSelect || !evoSelect) return;
    if (!Array.isArray(items) || !items.length) {
      docSelect.innerHTML = '<option value="">请先创建知识库</option>';
      evoSelect.innerHTML = '<option value="">请先创建知识库</option>';
      return;
    }
    const docCurrent = String(docSelect.value || "");
    const evoCurrent = String(evoSelect.value || "");
    const options = items.map((item) => `<option value="${item.id}">${esc(item.name)} (#${item.id})</option>`).join("");
    const fallback = String(items[0].id);
    docSelect.innerHTML = options;
    evoSelect.innerHTML = options;
    docSelect.value = items.some((item) => String(item.id) === docCurrent) ? docCurrent : fallback;
    evoSelect.value = items.some((item) => String(item.id) === evoCurrent) ? evoCurrent : fallback;
  };

  const renderKbTable = () => {
    const items = state.collections.kb;
    renderPills("kbSummary", [
      { label: "知识库数", value: items.length },
      { label: "文档数", value: items.reduce((sum, item) => sum + Number(item.doc_count || 0), 0) },
      { label: "Chunk 数", value: items.reduce((sum, item) => sum + Number(item.chunk_count || 0), 0) },
    ]);
    renderPagedTable({
      key: "kb",
      containerId: "kbTable",
      columns: ["ID", "名称", "描述", "文档", "Chunk", "状态", "操作"],
      items,
      emptyText: "暂无知识库，请先创建。",
      rowRenderer: (item) => `
        <td>${item.id}</td>
        <td>${esc(item.name)}</td>
        <td>${esc(item.description)}</td>
        <td>${item.doc_count}</td>
        <td>${item.chunk_count}</td>
        <td>${esc(item.status)}</td>
        <td><button class="btn ghost danger" type="button" data-action="delete-kb" data-id="${item.id}">删除</button></td>
      `,
    });
  };

  const renderDocTable = () => {
    const items = state.collections.docs;
    renderPills("docSummary", [
      { label: "总文档", value: items.length },
      { label: "已入库", value: items.filter((item) => String(item.status) === "indexed").length },
      { label: "失败", value: items.filter((item) => String(item.status) === "failed").length },
    ]);
    renderPagedTable({
      key: "docs",
      containerId: "docTable",
      columns: ["ID", "KB", "文件", "状态", "Chunk", "错误", "时间"],
      items,
      emptyText: "当前知识库下暂无文档。",
      rowRenderer: (row) => `
        <td>${row.id}</td>
        <td>${row.kb_id}</td>
        <td>${esc(row.file_name)}</td>
        <td>${esc(row.status)}</td>
        <td>${row.chunk_count}</td>
        <td>${esc(row.error_message || "")}</td>
        <td>${esc(row.created_at || "")}</td>
      `,
    });
  };

  const renderTaskTable = () => {
    const items = state.collections.tasks;
    const failed = items.filter((item) => String(item.status) === "failed").length;
    const success = items.filter((item) => String(item.status) === "success").length;
    renderPills("taskSummary", [
      { label: "总任务", value: items.length },
      { label: "失败", value: failed },
      { label: "已完成", value: success },
      { label: "可重试", value: failed },
    ]);
    renderPagedTable({
      key: "tasks",
      containerId: "taskTable",
      columns: ["ID", "KB", "文档", "类型", "状态", "重试数", "错误", "操作"],
      items,
      emptyText: "暂无任务记录。",
      rowRenderer: (task) => `
        <td>${task.id}</td>
        <td>${task.kb_id}</td>
        <td>${task.document_id}</td>
        <td>${esc(task.task_type)}</td>
        <td>${esc(task.status)}</td>
        <td>${task.retry_count}</td>
        <td>${esc(task.error_message || "")}</td>
        <td>${task.status === "failed" ? `<button class="btn ghost" type="button" data-action="retry-task" data-id="${task.id}">重试</button>` : "-"}</td>
      `,
    });
  };

  const renderLogTable = () => {
    const items = state.collections.logs;
    const avgLatency = items.length ? Math.round(items.reduce((sum, item) => sum + Number(item.latency_ms || 0), 0) / items.length) : 0;
    renderPills("logSummary", [
      { label: "日志条数", value: items.length },
      { label: "平均耗时", value: `${avgLatency} ms` },
      { label: "最近模型", value: items[0] ? items[0].model_name : "—" },
    ]);
    renderPagedTable({
      key: "logs",
      containerId: "logTable",
      columns: ["ID", "问题", "回答", "模型", "耗时(ms)", "状态", "时间"],
      items,
      emptyText: "暂无 QA 日志。",
      rowRenderer: (row) => `
        <td>${row.id}</td>
        <td>${esc(row.query_text).slice(0, 60)}</td>
        <td>${esc(row.answer_text).slice(0, 90)}</td>
        <td>${esc(row.model_name || "")}</td>
        <td>${row.latency_ms}</td>
        <td>${esc(row.status)}</td>
        <td>${esc(row.created_at || "")}</td>
      `,
    });
  };

  const renderEvolutionReviewTable = () => {
    const items = state.collections.reviews;
    renderPills("reviewSummary", [
      { label: "记录数", value: items.length },
      { label: "通过", value: items.filter((item) => String(item.decision) === "pass").length },
      { label: "拒绝", value: items.filter((item) => String(item.decision) === "reject").length },
    ]);
    renderPagedTable({
      key: "reviews",
      containerId: "evolutionReviewTable",
      columns: ["ID", "帖子", "结论", "分数", "模型", "文档", "理由", "时间"],
      items,
      emptyText: "暂无 AI 审核记录。",
      rowRenderer: (row) => `
        <td>${row.id}</td>
        <td>${esc(row.post_title)} (${esc(row.post_id)})</td>
        <td>${esc(row.decision)}</td>
        <td>${row.overall_score}</td>
        <td>${esc(row.reviewer_model)}</td>
        <td>${row.document_id ?? "-"}</td>
        <td>${esc(row.reason).slice(0, 90)}</td>
        <td>${esc(row.created_at || "")}</td>
      `,
    });
  };

  const renderAdoptionTable = () => {
    const items = state.collections.adoptions;
    renderPills("adoptionSummary", [
      { label: "录用数", value: items.length },
      { label: "最近录用", value: items[0] ? items[0].post_id : "—" },
    ]);
    renderPagedTable({
      key: "adoptions",
      containerId: "adoptionTable",
      columns: ["帖子", "楼主", "录用评论人", "录用内容", "时间"],
      items,
      emptyText: "暂无论坛采纳记录。",
      rowRenderer: (row) => `
        <td>${esc(row.post_title)} (${esc(row.post_id)})</td>
        <td>${esc(row.post_author_name)}</td>
        <td>${esc(row.adopted_user_name)}</td>
        <td>${esc(row.adopted_comment_text).slice(0, 100)}</td>
        <td>${esc(row.adopted_at || "")}</td>
      `,
    });
  };

  const renderOpsSummary = () => {
    const evo = state.lastEvolution;
    const cleanup = state.lastCleanup;
    const fallback = [
      { title: "已加载审核", value: state.collections.reviews.length, meta: "当前审核记录数" },
      { title: "已加载采纳", value: state.collections.adoptions.length, meta: "当前论坛采纳记录数" },
      { title: "默认模式", value: "增量处理", meta: "优先跳过已审核帖子" },
      { title: "本批上限", value: byId("evoLimit")?.value || "12", meta: "控制单次工作量" },
    ];
    const cards = evo
      ? [
          { title: "本批处理", value: evo.synced_posts, meta: `上限 ${evo.limit || "全部"}` },
          { title: "通过 / 拒绝", value: `${evo.accepted_posts} / ${evo.rejected_posts}`, meta: "AI 审核结果" },
          { title: "跳过已审核", value: evo.reviewed_posts_skipped, meta: "避免重复筛选" },
          { title: "剩余待处理", value: evo.remaining_posts, meta: `当前候选 ${evo.pending_posts}` },
        ]
      : cleanup
        ? [
            { title: "最近清理", value: cleanup.deleted_posts, meta: `评论 ${cleanup.deleted_comments}` },
            ...fallback.slice(1),
          ]
        : fallback;
    const node = byId("opsSummary");
    if (!node) return;
    node.innerHTML = cards.map((item) => `
      <article class="metric-card">
        <span>${esc(item.title)}</span>
        <strong>${esc(item.value)}</strong>
        <small>${esc(item.meta)}</small>
      </article>
    `).join("");
  };

  const loadStatus = async () => renderStatus(await api("/api/admin/devtools/status"));
  const runSelfCheck = async () => renderSelfCheck((await api("/api/admin/devtools/self-check", { method: "POST" })).items || []);
  const loadConfig = async () => { renderConfig(await api("/api/admin/devtools/config")); syncModelPresetControls(); };

  const saveConfig = async () => {
    const values = {};
    document.querySelectorAll("#configForm [data-config-key]").forEach((input) => {
      const key = input.dataset.configKey;
      const value = String(input.value || "").trim();
      if (input.dataset.secret === "true") {
        if (value) values[key] = value;
      } else {
        values[key] = value;
      }
    });
    if (!Object.keys(values).length) {
      log("没有可保存的配置修改");
      return;
    }
    await api("/api/admin/devtools/config", { method: "POST", body: { values } });
    log("配置已保存到 backend/.env，建议重启后端", "ok");
    setWorkspaceStatus("配置已更新，建议重启后端让新配置完全生效。");
    await Promise.all([loadConfig(), loadStatus()]);
  };

  const applySiliconPreset = () => {
    const preset = {
      QA_PROVIDER: "openai_compatible",
      QA_BASE_URL: "https://api.siliconflow.cn/v1",
      QA_MODEL: "Qwen/Qwen2.5-7B-Instruct",
      QA_TIMEOUT_SECONDS: "30",
      EVOLUTION_AI_REVIEW_ENABLED: "true",
      EVOLUTION_AI_REVIEW_PROVIDER: "qa_reuse",
      EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS: "20",
      EVOLUTION_AI_REVIEW_MIN_SCORE: "72",
      EMBEDDING_PROVIDER: "openai_compatible",
      EMBEDDING_BASE_URL: "https://api.siliconflow.cn/v1",
      EMBEDDING_MODEL: "BAAI/bge-m3",
      EMBEDDING_DIM: "1024",
      EMBEDDING_TIMEOUT_SECONDS: "25",
      RERANK_PROVIDER: "none",
      RERANK_BASE_URL: "https://api.siliconflow.cn/v1",
      RERANK_MODEL: "Qwen/Qwen3-Reranker-0.6B",
      WECHAT_CODE2SESSION_URL: "https://api.weixin.qq.com/sns/jscode2session",
      WECHAT_TIMEOUT_SECONDS: "10",
      WECHAT_MOCK_ENABLED: "true",
      BOOTSTRAP_DEMO_DATA: "false",
    };
    document.querySelectorAll("#configForm [data-config-key]").forEach((input) => {
      const key = String(input.dataset.configKey || "");
      if (Object.prototype.hasOwnProperty.call(preset, key)) input.value = preset[key];
    });
    syncModelPresetControls();
    log("已填入硅基流动推荐配置，请补充 Key 与微信参数后保存。", "ok");
  };

  const loadKb = async () => {
    const payload = await api("/api/admin/kb");
    state.kbItems = payload.items || [];
    state.collections.kb = state.kbItems;
    renderKbSelectors(state.kbItems);
    renderKbTable();
  };

  const createKb = async () => {
    const name = String(byId("kbName")?.value || "").trim();
    const description = String(byId("kbDesc")?.value || "").trim();
    if (!name) throw new Error("知识库名称不能为空");
    await api("/api/admin/kb", { method: "POST", body: { name, description } });
    if (byId("kbName")) byId("kbName").value = "";
    if (byId("kbDesc")) byId("kbDesc").value = "";
    log(`知识库已创建：${name}`, "ok");
    await Promise.all([loadKb(), loadStatus()]);
  };

  const deleteKb = async (id) => {
    const target = state.kbItems.find((item) => String(item.id) === String(id));
    const label = target ? `${target.name} (#${target.id})` : `#${id}`;
    if (!window.confirm(`确定删除知识库 ${label}？`)) return;
    await api(`/api/admin/kb/${id}`, { method: "DELETE" });
    log(`已删除知识库 ${label}`, "ok");
    await Promise.all([loadKb(), loadStatus()]);
  };

  const loadDocs = async () => {
    const kbId = String(byId("docKbSelect")?.value || "").trim();
    const path = kbId ? `/api/admin/documents?kb_id=${encodeURIComponent(kbId)}` : "/api/admin/documents";
    state.collections.docs = (await api(path)).items || [];
    renderDocTable();
  };

  const uploadDoc = async () => {
    const kbId = String(byId("docKbSelect")?.value || "").trim();
    const file = byId("docFile")?.files?.[0];
    if (!kbId) throw new Error("请先选择知识库");
    if (!file) throw new Error("请选择文件");
    const form = new FormData();
    form.append("kb_id", kbId);
    form.append("file", file);
    const payload = await api("/api/admin/documents/upload", { method: "POST", body: form });
    log(payload.message || "文档上传成功", "ok");
    if (byId("docFile")) byId("docFile").value = "";
    await Promise.all([loadDocs(), loadTasks(), loadStatus()]);
  };

  const loadTasks = async () => {
    state.collections.tasks = (await api("/api/admin/tasks")).items || [];
    renderTaskTable();
  };

  const retryTask = async (id) => {
    const payload = await api(`/api/admin/tasks/${id}/retry`, { method: "POST" });
    log(payload.message || `task ${id} retry`, "ok");
    await loadTasks();
  };

  const loadLogs = async () => {
    state.collections.logs = (await api("/api/admin/logs/qa")).items || [];
    renderLogTable();
  };

  const loadAdoptions = async () => {
    state.collections.adoptions = (await api("/api/admin/feed/adoptions")).items || [];
    renderAdoptionTable();
    renderOpsSummary();
  };

  const loadEvolutionReviews = async () => {
    state.collections.reviews = (await api("/api/admin/rag/evolution/reviews?limit=80")).items || [];
    renderEvolutionReviewTable();
    renderOpsSummary();
  };

  const runEvolution = async () => {
    const kbId = Number(byId("evoKbId")?.value || 1);
    const minLikes = Number(byId("evoMinLikes")?.value || 30);
    const minComments = Number(byId("evoMinComments")?.value || 5);
    const limit = Number(byId("evoLimit")?.value || 12);
    const includeReviewed = Boolean(byId("evoIncludeReviewed")?.checked);
    const path = `/api/admin/rag/evolution/sync-high-quality-posts?kb_id=${kbId}&min_likes=${minLikes}&min_comments=${minComments}&limit=${limit}&include_reviewed=${includeReviewed}`;
    const payload = await api(path, { method: "POST" });
    state.lastEvolution = payload;
    renderOpsSummary();
    log(`回灌完成：本批=${payload.synced_posts}，通过=${payload.accepted_posts}，拒绝=${payload.rejected_posts}，跳过已审核=${payload.reviewed_posts_skipped}，剩余=${payload.remaining_posts}`, "ok");
    setWorkspaceStatus("自进化批次已完成，结果已同步。");
    await Promise.all([loadStatus(), loadKb(), loadEvolutionReviews(), loadAdoptions()]);
  };

  const runCleanup = async () => {
    const days = Number(byId("cleanupDays")?.value || 7);
    const payload = await api(`/api/admin/maintenance/cleanup-stale-posts?days=${days}`, { method: "POST" });
    state.lastCleanup = payload;
    renderOpsSummary();
    log(`清理完成：posts=${payload.deleted_posts}, comments=${payload.deleted_comments}, post_assets=${payload.deleted_post_assets}, comment_assets=${payload.deleted_comment_assets}`, "ok");
    setWorkspaceStatus(`已执行 ${days} 天阈值清理。`);
    await loadStatus();
  };

  const askDebug = async () => {
    const query = String(byId("qaQuestion")?.value || "").trim();
    if (!query) throw new Error("请输入测试问题");
    const token = await clientLogin();
    const payload = await api("/api/client/knowledge/ask", {
      method: "POST",
      auth: false,
      headers: { Authorization: `Bearer ${token}` },
      body: { query, history: [], deep_thinking: false },
    });
    if (byId("qaResult")) byId("qaResult").textContent = JSON.stringify(payload, null, 2);
    log("问答调试请求成功", "ok");
    await loadLogs();
  };

  const refreshAll = async () => {
    setWorkspaceStatus("正在同步后台数据...");
    await Promise.all([loadStatus(), loadConfig(), loadKb(), loadTasks(), loadLogs(), loadAdoptions(), loadEvolutionReviews()]);
    await loadDocs();
    renderOpsSummary();
    setWorkspaceStatus("数据已同步，可继续切换模块工作。");
    log("后台数据已刷新", "ok");
  };

  const withAction = async (name, fn) => {
    try {
      await fn();
    } catch (error) {
      const message = formatUiError(error instanceof Error ? error.message : String(error));
      log(`${name}失败：${message}`, "error");
      window.alert(`${name}失败：${message}`);
    }
  };

  const bindEvents = () => {
    byId("btnLogout")?.addEventListener("click", () => logout(true));
    byId("btnRefreshAll")?.addEventListener("click", () => withAction("刷新全部", refreshAll));
    byId("btnLoadStatus")?.addEventListener("click", () => withAction("刷新状态", loadStatus));
    byId("btnSelfCheck")?.addEventListener("click", () => withAction("运行自检", runSelfCheck));
    byId("btnPresetSilicon")?.addEventListener("click", applySiliconPreset);
    byId("btnSaveConfig")?.addEventListener("click", () => withAction("保存配置", saveConfig));
    byId("btnCreateKb")?.addEventListener("click", () => withAction("创建知识库", createKb));
    byId("btnLoadKb")?.addEventListener("click", () => withAction("刷新知识库", loadKb));
    byId("btnUploadDoc")?.addEventListener("click", () => withAction("上传文档", uploadDoc));
    byId("btnLoadDocs")?.addEventListener("click", () => withAction("刷新文档", loadDocs));
    byId("btnLoadTasks")?.addEventListener("click", () => withAction("刷新任务", loadTasks));
    byId("btnAsk")?.addEventListener("click", () => withAction("问答调试", askDebug));
    byId("btnLoadLogs")?.addEventListener("click", () => withAction("刷新日志", loadLogs));
    byId("btnRunEvolution")?.addEventListener("click", () => withAction("执行高质量回灌", runEvolution));
    byId("btnRunCleanup")?.addEventListener("click", () => withAction("执行过期清理", runCleanup));
    byId("btnLoadEvolutionReviews")?.addEventListener("click", () => withAction("刷新 AI 审核记录", loadEvolutionReviews));
    byId("btnLoadAdoptions")?.addEventListener("click", () => withAction("刷新论坛采纳记录", loadAdoptions));
    byId("docKbSelect")?.addEventListener("change", () => withAction("刷新文档", loadDocs));
    document.querySelectorAll(".workspace-nav-btn").forEach((node) => node.addEventListener("click", () => setActiveScreen(node.dataset.screen)));

    document.body.addEventListener("click", (event) => {
      const openButton = event.target.closest("[data-open-screen]");
      if (openButton) {
        setActiveScreen(openButton.dataset.openScreen);
        return;
      }
      const deleteButton = event.target.closest("[data-action='delete-kb']");
      if (deleteButton) {
        withAction("删除知识库", () => deleteKb(deleteButton.dataset.id));
        return;
      }
      const retryButton = event.target.closest("[data-action='retry-task']");
      if (retryButton) {
        withAction("重试任务", () => retryTask(retryButton.dataset.id));
        return;
      }
      const pagerButton = event.target.closest("[data-pager-key]");
      if (!pagerButton) return;
      const key = String(pagerButton.dataset.pagerKey || "");
      const direction = Number(pagerButton.dataset.pagerDir || 0);
      state.pagers[key] = Math.max(1, Number(state.pagers[key] || 1) + direction);
      ({ kb: renderKbTable, docs: renderDocTable, tasks: renderTaskTable, logs: renderLogTable, reviews: renderEvolutionReviewTable, adoptions: renderAdoptionTable }[key] || (() => {}))();
    });

    byId("configForm")?.addEventListener("change", (event) => {
      const preset = event.target.closest("select[data-model-preset-key]");
      if (!preset) return;
      const key = String(preset.dataset.modelPresetKey || "");
      const input = findConfigInputByKey(key);
      if (!input) return;
      if (preset.value && preset.value !== CUSTOM_MODEL_VALUE) input.value = preset.value;
      if (preset.value === CUSTOM_MODEL_VALUE) input.focus();
    });

    byId("configForm")?.addEventListener("input", (event) => {
      const input = event.target.closest("input[data-config-key]");
      if (input && MODEL_KEYS.has(String(input.dataset.configKey || ""))) syncModelPresetControls();
    });

    window.addEventListener("hashchange", () => setActiveScreen(window.location.hash, { updateHash: false }));
  };

  const boot = async () => {
    if (!state.token) {
      redirectToLogin();
      return;
    }
    bindEvents();
    setActiveScreen(window.location.hash, { updateHash: false });
    renderOpsSummary();
    log("已进入新的管理工作台，开始同步后台数据。", "ok");
    await withAction("初始化加载", refreshAll);
  };

  boot();
})();
