(() => {
  const API_BASE = window.location.origin;
  const TOKEN_KEY = "campus_admin_token";
  const CLIENT_TOKEN_KEY = "campus_client_token";
  const DEFAULT_SCREEN = "overview";
  const PAGE_SIZES = { kb: 6, docs: 8, tasks: 8, logs: 6, reviews: 6, adoptions: 6 };
  const SECRET_KEYS = new Set(["WECHAT_APP_SECRET", "QA_API_KEY", "DOCUMENT_OCR_API_KEY", "EVOLUTION_AI_REVIEW_API_KEY", "RERANK_API_KEY", "EMBEDDING_API_KEY"]);
  const NUMBER_KEYS = new Set(["QA_TIMEOUT_SECONDS", "DOCUMENT_OCR_TIMEOUT_SECONDS", "DOCUMENT_OCR_MAX_PAGES", "EVOLUTION_AI_REVIEW_TIMEOUT_SECONDS", "EVOLUTION_AI_REVIEW_MIN_SCORE", "EMBEDDING_DIM", "EMBEDDING_TIMEOUT_SECONDS", "RERANK_TIMEOUT_SECONDS", "WECHAT_TIMEOUT_SECONDS"]);
  const DEFAULT_CONFIG_KEYS = [
    "QA_PROVIDER",
    "QA_BASE_URL",
    "QA_API_KEY",
    "QA_MODEL",
    "QA_TIMEOUT_SECONDS",
    "DOCUMENT_OCR_ENABLED",
    "DOCUMENT_OCR_BASE_URL",
    "DOCUMENT_OCR_API_KEY",
    "DOCUMENT_OCR_MODEL",
    "DOCUMENT_OCR_TIMEOUT_SECONDS",
    "DOCUMENT_OCR_MAX_PAGES",
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
      key: "ocr",
      title: "文档 OCR 模型",
      desc: "扫描 PDF、截图和图片资料抽不到文字时自动调用视觉模型入库。",
      keys: ["DOCUMENT_OCR_ENABLED", "DOCUMENT_OCR_BASE_URL", "DOCUMENT_OCR_API_KEY", "DOCUMENT_OCR_MODEL", "DOCUMENT_OCR_TIMEOUT_SECONDS", "DOCUMENT_OCR_MAX_PAGES"],
      cols: 3,
    },
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
    DOCUMENT_OCR_ENABLED: ["true", "false"],
    EVOLUTION_AI_REVIEW_ENABLED: ["true", "false"],
    EVOLUTION_AI_REVIEW_PROVIDER: ["qa_reuse", "openai_compatible", "siliconflow", "none"],
    EMBEDDING_PROVIDER: ["openai_compatible", "local_stub", "siliconflow", "none"],
    RERANK_PROVIDER: ["none", "openai_compatible", "siliconflow"],
    WECHAT_MOCK_ENABLED: ["true", "false"],
    BOOTSTRAP_DEMO_DATA: ["true", "false"],
  };
  const MODEL_HINTS = {
    QA_MODEL: ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen3.5-9B", "deepseek-ai/DeepSeek-V3", "THUDM/GLM-4-9B-Chat"],
    DOCUMENT_OCR_MODEL: ["Qwen/Qwen3-VL-32B-Instruct", "Qwen/Qwen3-VL-8B-Instruct", "PaddlePaddle/PaddleOCR-VL-1.5", "THUDM/GLM-4.1V-9B-Thinking"],
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
    evolutionOverview: null,
    selectedDocument: null,
    lastEvolution: null,
    lastCleanup: null,
  };

  const byId = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  const now = () => new Date().toLocaleString("zh-CN", { hour12: false });
  const compactDate = (value) => {
    if (!value) return "-";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value).slice(0, 16);
    return parsed.toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false });
  };
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
    const friendlyMap = {
      document_format_not_supported: "当前支持 txt、md、csv、tsv、json、yaml、xml、log、rtf、doc/docx、pdf、html、xls/xlsx、ppt/pptx、odt/ods/odp，以及 png/jpg/webp/bmp/tiff 图片 OCR；请确认文件后缀正确。",
      document_mime_not_supported: "文件类型和后缀不一致，请确认上传的是常见文本、网页、PDF、Word、Excel、PPT 或 OpenDocument 文档。",
      document_encoding_not_supported: "文本编码暂时无法识别，请另存为 UTF-8 编码后再上传。",
      document_docx_invalid: "这个 docx 文件结构不完整或已损坏，请重新另存一份 docx 后再上传。",
      document_legacy_doc_not_supported: "旧版 doc 是二进制 Word 格式，当前服务器无法可靠抽取正文；请用 Word/WPS 另存为 docx 后再上传。",
      document_legacy_ppt_not_supported: "旧版 ppt 是二进制演示文稿格式，当前服务器无法可靠抽取正文；请另存为 pptx 后上传。",
      document_pdf_invalid: "这个 PDF 文件结构不完整或已损坏，请重新导出 PDF 后再上传。",
      document_pdf_text_empty: "这个 PDF 没有可抽取文字，且当前 OCR 模型未配置或未能识别；请在配置中心启用文档 OCR 模型后重试。",
      document_ocr_not_configured: "文档 OCR 模型尚未配置。可在配置中心填写 DOCUMENT_OCR_BASE_URL / API_KEY / MODEL，或复用 QA 的接口地址和 Key。",
      document_ocr_failed: "文档 OCR 模型调用失败，请检查接口地址、Key、模型名和网络后重试。",
      document_ocr_empty: "OCR 没有识别到可入库文字，请确认图片清晰、方向正确。",
      document_pdf_ocr_empty: "OCR 没有从 PDF 页面识别到可入库文字，请确认扫描页清晰、方向正确。",
      document_image_ocr_empty: "OCR 没有从图片识别到可入库文字，请确认图片清晰、方向正确。",
      document_image_invalid: "这个图片文件结构异常或后缀不匹配，请重新导出为 png、jpg、webp、bmp 或 tiff 后再上传。",
      document_html_invalid: "这个 HTML 文件结构异常，请重新保存网页或转成 Markdown/文本后上传。",
      document_xml_invalid: "这个 XML 文件结构异常，请检查文件是否完整后再上传。",
      document_xlsx_invalid: "这个 xlsx 文件结构不完整或已损坏，请重新另存一份 xlsx 后再上传。",
      document_xls_invalid: "这个 xls 文件无法解析，请重新另存为 xlsx 后再上传。",
      document_xls_dependency_missing: "服务器缺少 xls 解析依赖，请先改传 xlsx；我已在项目依赖中补上 xlrd，重新部署后即可解析。",
      document_pptx_invalid: "这个 pptx 文件结构不完整或已损坏，请重新另存一份 pptx 后再上传。",
      document_odf_invalid: "这个 OpenDocument 文件结构异常，请重新另存后再上传。",
      document_too_large: "文件超过大小限制，请压缩内容或拆分成多个文档后上传。",
      document_empty: "文件内容为空，请选择有正文内容的文档。",
    };
    const code = text.replace(/^\d+:\s*/, "").trim();
    if (friendlyMap[code]) return friendlyMap[code];
    if (code.startsWith("document_format_not_supported:")) return friendlyMap.document_format_not_supported;
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

  const createApiError = (response, detail, authScope = "none") => {
    const error = new Error(`${response.status}: ${detail}`);
    error.status = response.status;
    error.detail = detail;
    error.authScope = authScope;
    return error;
  };

  const isTokenInvalidError = (error) => {
    const scope = String(error?.authScope || "");
    if (scope === "admin") return false;
    const text = String(error?.detail || error?.message || error || "");
    return /(^|\s)(401:\s*)?(token_invalid|token_expired|client_token_invalid|client_token_required|client_token_revoked)\b/.test(text);
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
      const detail = await parseError(response);
      const authScope = auth ? "admin" : (finalHeaders.Authorization ? "client" : "none");
      if (response.status === 401 && auth) {
        logout(false);
        throw createApiError(response, detail, authScope);
      }
      throw createApiError(response, detail, authScope);
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

  const resetClientDebugToken = () => {
    state.clientToken = "";
    localStorage.removeItem(CLIENT_TOKEN_KEY);
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
    DOCUMENT_OCR_ENABLED: "文档 OCR 开关",
    DOCUMENT_OCR_BASE_URL: "OCR 接口地址",
    DOCUMENT_OCR_API_KEY: "OCR API Key",
    DOCUMENT_OCR_MODEL: "OCR 视觉模型名",
    DOCUMENT_OCR_TIMEOUT_SECONDS: "OCR 超时（秒）",
    DOCUMENT_OCR_MAX_PAGES: "PDF OCR 页数上限",
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

  const isQaReuseReview = (masked = {}) => String(masked.EVOLUTION_AI_REVIEW_PROVIDER || "qa_reuse").trim().toLowerCase() !== "none"
    && String(masked.EVOLUTION_AI_REVIEW_PROVIDER || "qa_reuse").trim().toLowerCase() !== "openai_compatible"
    && String(masked.EVOLUTION_AI_REVIEW_PROVIDER || "qa_reuse").trim().toLowerCase() !== "siliconflow";

  const getConfigFieldPlaceholder = (key, current = "", masked = {}) => {
    if (String(current || "").trim()) return "";
    if (!isQaReuseReview(masked)) return "";
    const placeholders = {
      EVOLUTION_AI_REVIEW_BASE_URL: "复用 QA_BASE_URL，无需单独填写",
      EVOLUTION_AI_REVIEW_API_KEY: "复用 QA_API_KEY，无需单独填写",
      EVOLUTION_AI_REVIEW_MODEL: "复用 QA_MODEL，无需单独填写",
    };
    return placeholders[key] || "";
  };

  const renderConfigField = (key, value = "", masked = {}) => {
    const current = String(value ?? "");
    if (MODEL_KEYS.has(key)) {
      const preset = (MODEL_HINTS[key] || []).includes(current) ? current : CUSTOM_MODEL_VALUE;
      const placeholder = getConfigFieldPlaceholder(key, current, masked) || "可手动输入任意模型名";
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
          <input data-config-key="${esc(key)}" data-secret="false" type="text" value="${esc(current)}" placeholder="${esc(placeholder)}" autocomplete="off" />
        </label>
      `;
    }
    if (SELECT_OPTIONS[key]) {
      return `<label>${esc(getConfigFieldLabel(key))}<select data-config-key="${esc(key)}" data-secret="false">${renderSelectOptions(key, current)}</select></label>`;
    }
    if (SECRET_KEYS.has(key)) {
      const placeholder = current ? `已保存：${current}` : getConfigFieldPlaceholder(key, current, masked) || "未设置（输入后保存）";
      return `<label>${esc(getConfigFieldLabel(key))}<input data-config-key="${esc(key)}" data-secret="true" type="password" value="" placeholder="${esc(placeholder)}" autocomplete="off" /></label>`;
    }
    const placeholder = getConfigFieldPlaceholder(key, current, masked);
    return `<label>${esc(getConfigFieldLabel(key))}<input data-config-key="${esc(key)}" data-secret="false" type="${NUMBER_KEYS.has(key) ? "number" : "text"}" value="${esc(current)}" placeholder="${esc(placeholder)}" autocomplete="off" /></label>`;
  };

  const hasConfigValue = (masked, key) => Boolean(String(masked?.[key] || "").trim());

  const renderConfigGroupNotice = (groupKey, masked) => {
    if (groupKey !== "evolution") return "";
    const enabled = String(masked.EVOLUTION_AI_REVIEW_ENABLED || "true").trim().toLowerCase() !== "false";
    const provider = String(masked.EVOLUTION_AI_REVIEW_PROVIDER || "qa_reuse").trim().toLowerCase() || "qa_reuse";
    const qaReady = hasConfigValue(masked, "QA_BASE_URL") && hasConfigValue(masked, "QA_API_KEY") && hasConfigValue(masked, "QA_MODEL");
    const dedicatedReady = hasConfigValue(masked, "EVOLUTION_AI_REVIEW_BASE_URL") && hasConfigValue(masked, "EVOLUTION_AI_REVIEW_API_KEY") && hasConfigValue(masked, "EVOLUTION_AI_REVIEW_MODEL");

    if (!enabled || provider === "none") {
      return '<div class="config-group-notice is-muted">AI 审核当前关闭：帖子入库会退回规则评分。答辩演示建议保持开启。</div>';
    }
    if (provider === "qa_reuse") {
      return qaReady
        ? '<div class="config-group-notice is-ok">当前 AI 审核已配置为复用 QA：接口地址、API Key、模型名会自动读取 QA_*，所以下方 AI 审核专属地址 / Key / 模型可以留空。</div>'
        : '<div class="config-group-notice is-warn">当前选择复用 QA，但 QA 接口地址、API Key 或模型名还不完整；请先补齐 QA 配置，或把 Provider 改为 openai_compatible 后单独填写 AI 审核配置。</div>';
    }
    return dedicatedReady
      ? '<div class="config-group-notice is-ok">AI 审核已使用独立模型配置，帖子进入知识库前会先调用该模型审核。</div>'
      : '<div class="config-group-notice is-warn">当前选择独立 AI 审核 Provider，需要填写 AI 审核接口地址、API Key 和模型名。</div>';
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
        ${renderConfigGroupNotice(group.key, masked)}
        <div class="config-fields cols-${Number(group.cols || 2)}">${group.keys.map((key) => renderConfigField(key, masked[key] || "", masked)).join("")}</div>
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
          { label: "OCR", ok: Boolean(status.document_ocr_configured) },
          { label: `AI审核 ${status.evolution_ai_review_provider || "-"}`, ok: Boolean(status.evolution_ai_review_configured) },
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
    const detailText = (item) => {
      const detail = String(item.detail || "");
      if (item.name === "qdrant_config" && detail === "qdrant_optional_local_fallback") {
        return "未配置 Qdrant，当前使用本地缓存/词法检索兜底，可正常完成知识库演示；生产环境再补向量库即可。";
      }
      if (item.name === "qdrant_config" && detail === "qdrant_url_configured") {
        return "Qdrant 向量库地址已配置。";
      }
      if (item.name === "document_ocr_config" && detail === "ocr_model_ready") {
        return "文档 OCR 模型已配置，扫描 PDF 和图片可自动识别入库。";
      }
      if (item.name === "document_ocr_config" && detail === "ocr_optional_but_not_configured") {
        return "文档 OCR 未配置；普通可复制文档不受影响，扫描件和图片需要配置视觉模型。";
      }
      if (item.name === "evolution_ai_review_config" && detail === "ai_review_reuse_qa_ready") {
        return "自进化 AI 审核已就绪：当前复用 QA 接口、Key 和模型，AI 审核专属配置留空是正常的。";
      }
      if (item.name === "evolution_ai_review_config" && detail === "ai_review_dedicated_ready") {
        return "自进化 AI 审核已就绪：当前使用独立 AI 审核模型配置。";
      }
      if (item.name === "evolution_ai_review_config" && detail === "ai_review_disabled") {
        return "自进化 AI 审核已关闭；系统会退回规则评分。";
      }
      if (item.name === "evolution_ai_review_config" && detail === "ai_review_missing_base_url_or_key_or_model") {
        return "自进化 AI 审核未完整配置：使用 qa_reuse 时请补齐 QA 接口地址、API Key 和模型；使用独立 Provider 时请补齐 AI 审核专属配置。";
      }
      return detail;
    };
    node.innerHTML = items.map((item) => {
      const optional = item.name === "qdrant_config" && String(item.detail || "").includes("optional");
      const pillClass = optional ? "warn" : item.passed ? "ok" : "bad";
      const pillText = optional ? "可选兜底" : item.passed ? "通过" : "失败";
      return `
      <div class="table-meta">
        <div><strong>${esc(item.name)}</strong><div class="hint">${esc(detailText(item))}</div></div>
        <span class="status-pill ${pillClass}">${pillText}</span>
      </div>
    `;
    }).join("");
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
        <td class="table-actions">
          <button class="btn ghost" type="button" data-action="open-kb-docs" data-id="${item.id}">查看/修改内容</button>
          <button class="btn ghost danger" type="button" data-action="delete-kb" data-id="${item.id}">删除</button>
        </td>
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
      columns: ["ID", "KB", "文件", "状态", "Chunk", "错误", "时间", "操作"],
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
        <td class="table-actions">
          <button class="btn ghost" type="button" data-action="open-document" data-id="${row.id}">查看/编辑</button>
          <button class="btn ghost danger" type="button" data-action="delete-document" data-id="${row.id}">移除</button>
        </td>
      `,
    });
  };

  const renderDocumentEditor = () => {
    const box = byId("docEditor");
    if (!box) return;
    const selected = state.selectedDocument;
    if (!selected) {
      box.innerHTML = '<div class="empty-state">从知识库列表点击“查看/修改内容”，或在文档列表里打开具体文档；保存并重新入库后，编辑窗口会自动关闭，避免误以为没有保存。</div>';
      return;
    }
    const doc = selected.document || {};
    box.innerHTML = `
      <div class="doc-editor-head">
        <div>
          <p class="module-kicker">Review Editor</p>
          <h4>${esc(doc.file_name || `Document #${doc.id}`)}</h4>
          <p class="hint">文档 #${esc(doc.id)} · KB #${esc(doc.kb_id)} · ${esc(doc.status || "")} · ${esc(doc.chunk_count || 0)} chunks</p>
        </div>
        <div class="module-actions">
          <button id="btnSaveDocContent" class="btn" type="button" ${selected.editable ? "" : "disabled"}>保存并重新入库</button>
          <button id="btnDeleteDocContent" class="btn ghost danger" type="button">不保留此条</button>
        </div>
      </div>
      <textarea id="docContentEditor" class="doc-content-editor" ${selected.editable ? "" : "disabled"}>${esc(selected.content || "")}</textarea>
      <p class="hint">建议只保留答辩演示和真实问答会用到的信息；点击保存后会自动重新入库并关闭本窗口，删除会同步移除知识库和回灌记录关联。</p>
    `;
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
    const overview = state.evolutionOverview || {};
    const latestReview = overview.latest_review || {};
    renderPills("reviewSummary", [
      { label: "记录数", value: items.length },
      { label: "通过", value: items.filter((item) => String(item.decision) === "pass").length },
      { label: "拒绝", value: items.filter((item) => String(item.decision) === "reject").length },
      { label: "最新审核", value: latestReview.created_at ? `${compactDate(latestReview.created_at)} ${latestReview.post_id || ""}` : "未加载" },
    ]);
    renderPagedTable({
      key: "reviews",
      containerId: "evolutionReviewTable",
      columns: ["ID", "帖子", "结论", "分数", "模型", "文档", "理由", "时间", "复核"],
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
        <td class="table-actions">
          ${row.document_id ? `<button class="btn ghost" type="button" data-action="open-document" data-id="${row.document_id}">查看/修改</button>` : "-"}
          ${row.document_id ? `<button class="btn ghost danger" type="button" data-action="delete-document" data-id="${row.document_id}">不保留</button>` : ""}
        </td>
      `,
    });
  };

  const renderAdoptionTable = () => {
    const items = state.collections.adoptions;
    const overview = state.evolutionOverview || {};
    const latestAdoption = overview.latest_adoption || {};
    renderPills("adoptionSummary", [
      { label: "录用数", value: items.length },
      { label: "最近录用", value: items[0] ? items[0].post_id : "-" },
      { label: "缺失待修复", value: Number(overview.missing_adoption_records || 0) },
      { label: "最新流水", value: latestAdoption.adopted_at ? `${compactDate(latestAdoption.adopted_at)} ${latestAdoption.post_id || ""}` : "未加载" },
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
    const overview = state.evolutionOverview || {};
    const latestReview = overview.latest_review || {};
    const latestAdoption = overview.latest_adoption || {};
    const fallback = [
      { title: "AI 审核总数", value: overview.total_reviews ?? state.collections.reviews.length, meta: latestReview.created_at ? `最新 ${compactDate(latestReview.created_at)}` : "等待加载健康概览" },
      { title: "通过 / 拒绝", value: `${overview.passed_reviews ?? "-"} / ${overview.rejected_reviews ?? "-"}`, meta: "AI 自动筛选结果" },
      { title: "待处理候选", value: overview.pending_posts ?? "-", meta: `已跳过 ${overview.reviewed_posts_skipped ?? "-"} 条` },
      { title: "论坛采纳缺口", value: overview.missing_adoption_records ?? 0, meta: latestAdoption.adopted_at ? `最新流水 ${compactDate(latestAdoption.adopted_at)}` : "可一键修复迁移缺口" },
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
      DOCUMENT_OCR_ENABLED: "true",
      DOCUMENT_OCR_BASE_URL: "https://api.siliconflow.cn/v1",
      DOCUMENT_OCR_MODEL: "Qwen/Qwen3-VL-32B-Instruct",
      DOCUMENT_OCR_TIMEOUT_SECONDS: "45",
      DOCUMENT_OCR_MAX_PAGES: "3",
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
    renderDocumentEditor();
  };

  const openKbDocuments = async (kbId) => {
    setActiveScreen("ingest");
    const docSelect = byId("docKbSelect");
    if (docSelect) docSelect.value = String(kbId || "");
    state.selectedDocument = null;
    await loadDocs();
    log(`已打开知识库 #${kbId} 的文档列表，可逐条查看、修改或移除`, "ok");
  };

  const openDocument = async (id) => {
    state.selectedDocument = await api(`/api/admin/documents/${encodeURIComponent(id)}/content`);
    renderDocumentEditor();
    setActiveScreen("ingest");
    log(`已打开文档 #${id}，可以查看、编辑或移除`, "ok");
  };

  const saveSelectedDocument = async () => {
    const selected = state.selectedDocument;
    if (!selected?.document?.id) throw new Error("请先选择文档");
    const content = String(byId("docContentEditor")?.value || "").trim();
    if (!content) throw new Error("文档内容不能为空");
    const payload = await api(`/api/admin/documents/${selected.document.id}/content`, {
      method: "PUT",
      body: { content, reindex: true },
    });
    const documentId = selected.document.id;
    state.selectedDocument = null;
    renderDocumentEditor();
    log(payload.message || `文档 #${documentId} 已保存并重新入库，编辑窗口已关闭`, "ok");
    await Promise.all([loadDocs(), loadTasks(), loadKb(), loadStatus()]);
  };

  const deleteDocument = async (id) => {
    if (!window.confirm(`确定不保留文档 #${id} 吗？删除后会从知识库与向量索引中移除。`)) return;
    const payload = await api(`/api/admin/documents/${encodeURIComponent(id)}`, { method: "DELETE" });
    log(payload.message || `文档 #${id} 已移除`, "ok");
    if (state.selectedDocument?.document && String(state.selectedDocument.document.id) === String(id)) {
      state.selectedDocument = null;
      renderDocumentEditor();
    }
    await Promise.all([loadDocs(), loadKb(), loadStatus(), loadEvolutionReviews()]);
  };

  const uploadDoc = async () => {
    const kbId = String(byId("docKbSelect")?.value || "").trim();
    const file = byId("docFile")?.files?.[0];
    if (!kbId) throw new Error("请先选择知识库");
    if (!file) throw new Error("请选择文件");
    const form = new FormData();
    form.append("kb_id", kbId);
    form.append("file", file);
    await api("/api/admin/documents/upload", { method: "POST", body: form });
    log(`文档「${file.name}」上传成功，已自动抽取正文并创建入库任务`, "ok");
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

  const loadEvolutionOverview = async () => {
    const kbId = Number(byId("evoKbId")?.value || 1);
    const minLikes = Number(byId("evoMinLikes")?.value || 30);
    const minComments = Number(byId("evoMinComments")?.value || 5);
    state.evolutionOverview = await api(`/api/admin/rag/evolution/overview?kb_id=${kbId}&min_likes=${minLikes}&min_comments=${minComments}`);
    renderOpsSummary();
    renderEvolutionReviewTable();
    renderAdoptionTable();
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
    await Promise.all([loadStatus(), loadKb(), loadEvolutionReviews(), loadAdoptions(), loadEvolutionOverview()]);
  };

  const repairAdoptions = async () => {
    const payload = await api("/api/admin/feed/adoptions/repair?limit=1000", { method: "POST" });
    state.lastEvolution = null;
    log(`采纳流水修复完成：补齐=${payload.created_adoptions}，清理孤儿采纳=${payload.cleared_orphan_adopted_flags || 0}，跳过无评论=${payload.skipped_without_comment}，剩余缺口=${payload.remaining_missing}`, "ok");
    await Promise.all([loadAdoptions(), loadEvolutionOverview()]);
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

  const reconcileCounts = async () => {
    const payload = await api("/api/admin/maintenance/reconcile-interaction-counts", { method: "POST" });
    log(`互动计数修复完成：帖子点赞=${payload.fixed_post_likes}, 帖子评论=${payload.fixed_post_comments}, 评论点赞=${payload.fixed_comment_likes}`, "ok");
    setWorkspaceStatus("帖子与评论互动计数已按真实明细重新校准。");
    await Promise.all([loadStatus(), loadEvolutionOverview()]);
  };

  const askDebug = async () => {
    const query = String(byId("qaQuestion")?.value || "").trim();
    if (!query) throw new Error("请输入测试问题");
    const request = async () => {
      const token = await clientLogin();
      return api("/api/client/knowledge/ask", {
        method: "POST",
        auth: false,
        headers: { Authorization: `Bearer ${token}` },
        body: { query, history: [], deep_thinking: false },
      });
    };
    let payload;
    try {
      payload = await request();
    } catch (error) {
      if (!isTokenInvalidError(error)) throw error;
      resetClientDebugToken();
      log("客户端调试 token 已失效，已自动刷新后重试。");
      payload = await request();
    }
    if (byId("qaResult")) byId("qaResult").textContent = JSON.stringify(payload, null, 2);
    log("问答调试请求成功", "ok");
    await loadLogs();
  };

  const refreshAll = async () => {
    setWorkspaceStatus("正在同步后台数据...");
    await Promise.all([loadStatus(), loadConfig(), loadKb(), loadTasks(), loadLogs(), loadAdoptions(), loadEvolutionReviews(), loadEvolutionOverview()]);
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
    byId("btnReconcileCounts")?.addEventListener("click", () => withAction("修复互动计数", reconcileCounts));
    byId("btnLoadEvolutionReviews")?.addEventListener("click", () => withAction("刷新 AI 审核记录", loadEvolutionReviews));
    byId("btnLoadAdoptions")?.addEventListener("click", () => withAction("刷新论坛采纳记录", loadAdoptions));
    byId("btnRepairAdoptions")?.addEventListener("click", () => withAction("修复采纳流水", repairAdoptions));
    byId("docKbSelect")?.addEventListener("change", () => withAction("刷新文档", loadDocs));
    document.querySelectorAll(".workspace-nav-btn").forEach((node) => node.addEventListener("click", () => setActiveScreen(node.dataset.screen)));

    document.body.addEventListener("click", (event) => {
      const openButton = event.target.closest("[data-open-screen]");
      if (openButton) {
        setActiveScreen(openButton.dataset.openScreen);
        return;
      }
      const openKbDocsButton = event.target.closest("[data-action='open-kb-docs']");
      if (openKbDocsButton) {
        withAction("打开知识库内容", () => openKbDocuments(openKbDocsButton.dataset.id));
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
      const openDocButton = event.target.closest("[data-action='open-document']");
      if (openDocButton) {
        withAction("打开文档", () => openDocument(openDocButton.dataset.id));
        return;
      }
      const deleteDocButton = event.target.closest("[data-action='delete-document']");
      if (deleteDocButton) {
        withAction("移除文档", () => deleteDocument(deleteDocButton.dataset.id));
        return;
      }
      if (event.target.closest("#btnSaveDocContent")) {
        withAction("保存文档", saveSelectedDocument);
        return;
      }
      if (event.target.closest("#btnDeleteDocContent")) {
        const id = state.selectedDocument?.document?.id;
        if (id) withAction("移除文档", () => deleteDocument(id));
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
    renderDocumentEditor();
    renderOpsSummary();
    log("已进入新的管理工作台，开始同步后台数据。", "ok");
    await withAction("初始化加载", refreshAll);
  };

  boot();
})();
