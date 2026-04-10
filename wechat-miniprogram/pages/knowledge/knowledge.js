const { buildApiUrl } = require("../../config/env");
const { apiRequest } = require("../../utils/request");
const { buildGreetingName, formatGreetingDate, getClientDisplayName, syncTabBar } = require("../../utils/ui");

function buildHistory(messages) {
  return messages
    .filter((item) => item.role === "user" || item.role === "assistant")
    .slice(-8)
    .map((item) => ({ role: item.role, text: item.text }));
}

function buildMessage(role, text, extra = {}) {
  return {
    id: `m-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    role,
    text,
    citations: [],
    detailItems: [],
    detailCount: 0,
    collapsedDetailLabel: "查看详情",
    expandedDetailLabel: "收起详情",
    expanded: false,
    ...extra,
  };
}

function getSourceActionLabel(sourceType) {
  return sourceType === "feed" ? "查看原帖" : "复制来源";
}

function normalizeDetailItems(items = []) {
  if (!Array.isArray(items)) return [];
  return items.map((item, index) => {
    const sourceType = String(item.source_type || item.sourceType || "kb");
    const scoreValue = Number(item.score || 0);
    const sourceLabel = sourceType === "feed" ? "论坛来源" : "知识库来源";
    return {
      id: item.id || `c-${index + 1}`,
      order: index + 1,
      title: item.title || item.source || `相关内容 ${index + 1}`,
      snippet: item.snippet || item.quote || item.source || "",
      jump_url: item.jump_url || item.jumpUrl || "",
      source_type: sourceType,
      linkLabel: getSourceActionLabel(sourceType),
      metaText: scoreValue > 0 ? `${sourceLabel} · 匹配分 ${scoreValue.toFixed(3)}` : sourceLabel,
    };
  });
}

function buildDetailState(response = {}) {
  const relatedAnswers = Array.isArray(response.related_answers)
    ? response.related_answers
    : (Array.isArray(response.relatedAnswers) ? response.relatedAnswers : []);
  const citations = Array.isArray(response.citations) ? response.citations : [];
  const detailItems = normalizeDetailItems(relatedAnswers.length ? relatedAnswers : citations);
  return {
    citations: detailItems,
    detailItems,
    detailCount: detailItems.length,
    collapsedDetailLabel: detailItems.length ? `查看详情（相关内容 ${detailItems.length}）` : "查看详情",
    expandedDetailLabel: "收起详情",
  };
}

function extractPostId(id, jumpUrl) {
  const directId = String(id || "").trim();
  if (/^p-\d+$/i.test(directId)) return directId;
  const link = String(jumpUrl || "").trim();
  if (!link) return "";
  const match = link.match(/(?:#post=|[?&]id=)(p-\d+)/i);
  return match ? match[1] : "";
}

function formatAskError(error) {
  const message = String((error && error.message) || "network_error");
  if (message.includes("qa_timeout")) return "知识库响应超时，请稍后再试。";
  if (message.includes("qa_pipeline_failed")) return "问答链路暂时不可用，请稍后再试。";
  if (message.includes("network")) return "网络连接异常，请检查后重试。";
  return `请求失败：${message}`;
}

Page({
  data: {
    greetingName: buildGreetingName("同学"),
    greetingDate: formatGreetingDate(),
    input: "",
    sending: false,
    deepThinking: false,
    scrollTarget: "",
    messages: [],
    hasConversation: false,
    activeDetail: {
      visible: false,
      title: "",
      items: [],
      sourceMessageId: "",
    },
  },

  onShow() {
    const app = getApp();
    syncTabBar(this, 2);
    this.setData({
      greetingDate: formatGreetingDate(),
      greetingName: buildGreetingName(getClientDisplayName("同学")),
    });

    app.ensureSession().finally(() => {
      this.setData({
        greetingName: buildGreetingName(getClientDisplayName("同学")),
        hasConversation: Array.isArray(this.data.messages) && this.data.messages.length > 0,
      });
    });
  },

  onInputChange(event) {
    this.setData({ input: event.detail.value || "" });
  },

  onSwitchDeep(event) {
    this.setData({ deepThinking: Boolean(event.detail.value) });
  },

  async sendQuery(query) {
    const text = String(query || "").trim();
    if (!text || this.data.sending) return;

    const history = buildHistory(this.data.messages);
    const userMessage = buildMessage("user", text);
    const historyBase = [...this.data.messages, userMessage];
    this.setData({
      messages: historyBase,
      input: "",
      sending: true,
      scrollTarget: userMessage.id,
      hasConversation: true,
      activeDetail: {
        visible: false,
        title: "",
        items: [],
        sourceMessageId: "",
      },
    });

    try {
      const res = await apiRequest({
        url: "/api/client/knowledge/ask",
        method: "POST",
        data: {
          query: text,
          history,
          deep_thinking: Boolean(this.data.deepThinking),
        },
      });

      const assistantMessage = buildMessage(
        "assistant",
        (res && res.answer) || "当前未返回有效内容，请稍后再试。",
        {
          ...buildDetailState(res || {}),
          expanded: false,
        }
      );

      this.setData({
        messages: [...historyBase, assistantMessage],
        sending: false,
        scrollTarget: assistantMessage.id,
        hasConversation: true,
      });
    } catch (error) {
      const assistantMessage = buildMessage("assistant", formatAskError(error));
      this.setData({
        messages: [...historyBase, assistantMessage],
        sending: false,
        scrollTarget: assistantMessage.id,
        hasConversation: true,
      });
    }
  },

  async onSend() {
    await this.sendQuery(this.data.input);
  },

  onToggleDetail(event) {
    const index = Number(event.currentTarget.dataset.index);
    if (!Number.isInteger(index) || index < 0) return;
    const target = (this.data.messages || [])[index];
    if (!target || target.role !== "assistant" || !target.detailCount) return;
    const currentId = String(this.data.activeDetail?.sourceMessageId || "");
    const nextId = String(target.id || "");
    if (this.data.activeDetail?.visible && currentId && currentId === nextId) {
      this.onCloseDetail();
      return;
    }
    this.setData({
      activeDetail: {
        visible: true,
        title: target.detailCount > 1 ? `共 ${target.detailCount} 条相关内容` : "1 条相关内容",
        items: Array.isArray(target.detailItems) ? target.detailItems : [],
        sourceMessageId: nextId,
      },
    });
  },

  onCloseDetail() {
    this.setData({
      activeDetail: {
        visible: false,
        title: "",
        items: [],
        sourceMessageId: "",
      },
    });
  },

  noop() {},

  closeDetailIfOpen() {
    if (this.data.activeDetail?.visible) this.onCloseDetail();
  },

  onTapSource(event) {
    const { id, jump, sourceType } = event.currentTarget.dataset || {};
    const postId = extractPostId(id, jump);
    if (postId) {
      this.closeDetailIfOpen();
      wx.navigateTo({
        url: `/pages/post/post?id=${encodeURIComponent(postId)}&title=${encodeURIComponent("知识来源")}`,
      });
      return;
    }

    const link = String(jump || "").trim();
    if (!link) {
      wx.showToast({ title: "当前来源暂无可跳转入口", icon: "none" });
      return;
    }

    const finalLink = /^https?:\/\//i.test(link) ? link : buildApiUrl(link);
    wx.setClipboardData({
      data: finalLink,
      success: () => {
        wx.showToast({
          title: sourceType === "feed" ? "原帖链接已复制" : "来源链接已复制",
          icon: "none",
        });
      },
    });
  },
});
