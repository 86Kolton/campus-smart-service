const { apiRequest, uploadFile } = require("../../utils/request");
const { buildApiUrl } = require("../../config/env");
const { decodeRouteText, normalizePostId } = require("../../utils/ui");

const CATEGORY_OPTIONS = [
  { id: "study", label: "学习空间" },
  { id: "academic", label: "教务课程" },
  { id: "canteen", label: "食堂生活" },
  { id: "market", label: "校园集市" }
];

function getCategoryLabel(category) {
  const hit = CATEGORY_OPTIONS.find((item) => item.id === category);
  return hit ? hit.label : "校园帖子";
}

function normalizeImageUrl(path) {
  const text = String(path || "").trim();
  if (!text) return "";
  return /^https?:\/\//i.test(text) ? text : buildApiUrl(text);
}

function buildTagArray(raw = "") {
  return String(raw || "")
    .split(/[\s,，]+/)
    .map((item) => item.replace(/^#/, "").trim())
    .filter(Boolean)
    .slice(0, 8)
    .map((item) => `#${item}`);
}

function normalizeCommentItem(item = {}) {
  return {
    ...item,
    image_url_full: normalizeImageUrl(item.image_url),
    likes: Number(item.likes || 0),
    liked: Boolean(item.liked)
  };
}

function normalizePostItem(item = {}) {
  return {
    ...item,
    image_url_full: normalizeImageUrl(item.image_url),
    categoryLabel: getCategoryLabel(item.category),
    tags: Array.isArray(item.tags) ? item.tags : [],
    can_delete: Boolean(item.can_delete)
  };
}

function chooseSingleImage() {
  return new Promise((resolve, reject) => {
    wx.chooseImage({
      count: 1,
      sizeType: ["compressed"],
      sourceType: ["album", "camera"],
      success(res) {
        const filePath = res && res.tempFilePaths && res.tempFilePaths[0];
        if (!filePath) return reject(new Error("未选择图片"));
        resolve(filePath);
      },
      fail(err) {
        reject(err || new Error("choose_image_failed"));
      }
    });
  });
}

Page({
  data: {
    mode: "detail",
    id: "",
    title: "帖子详情",
    post: null,
    comments: [],
    commentBusyId: "",
    commentInput: "",
    commentImagePath: "",
    commentSubmitting: false,
    loading: false,
    error: "",
    categoryOptions: CATEGORY_OPTIONS,
    draftCategory: "study",
    draftTitle: "",
    draftContent: "",
    draftTags: "",
    draftHint: "",
    draftImagePath: "",
    postSubmitting: false,
    postDeleting: false,
    postLiking: false,
    postSaving: false
  },

  onLoad(query) {
    const id = normalizePostId(query.id || "");
    const title = decodeRouteText(query.title || "", id ? "帖子详情" : "发布帖子");
    this.setData({
      mode: id ? "detail" : "compose",
      id,
      title,
      draftCategory: String(query.category || "study"),
      draftTitle: decodeRouteText(query.prefill_title || "", ""),
      draftContent: decodeRouteText(query.prefill_content || "", ""),
      draftTags: decodeRouteText(query.prefill_tags || "", ""),
      draftHint: decodeRouteText(query.draft_hint || "", "")
    });
    wx.setNavigationBarTitle({ title: id ? title : "发布帖子" });
    if (id) this.loadAll();
  },

  onPullDownRefresh() {
    if (this.data.mode === "detail") {
      return this.loadAll().finally(() => wx.stopPullDownRefresh());
    }
    wx.stopPullDownRefresh();
  },

  async loadAll() {
    if (!this.data.id) return this.setData({ error: "缺少帖子 ID" });
    const app = getApp();
    this.setData({ loading: true, error: "" });
    try {
      await app.ensureSession();
      await this.loadPost();
      await this.loadComments();
      this.setData({ loading: false });
    } catch (error) {
      this.setData({ loading: false, error: error && error.message || "加载失败" });
    }
  },

  async loadPost() {
    const data = await apiRequest({ url: "/api/client/feed/list?filter=all", method: "GET" });
    const items = Array.isArray(data && data.items) ? data.items : [];
    const match = items.find((item) => normalizePostId(item.id) === this.data.id);
    if (!match) {
      this.setData({ post: null, error: "帖子不存在或已被删除" });
      return;
    }
    const post = normalizePostItem(match);
    this.setData({ post });
    wx.setNavigationBarTitle({ title: post.title || "帖子详情" });
  },

  async loadComments() {
    const data = await apiRequest({
      url: `/api/client/feed/comments?post_id=${encodeURIComponent(this.data.id)}&page=1&page_size=30`,
      method: "GET"
    });
    this.setData({ comments: Array.isArray(data && data.items) ? data.items.map(normalizeCommentItem) : [] });
  },

  async togglePostLike() {
    const post = this.data.post;
    if (!post || this.data.postLiking) return;
    const nextLiked = !post.liked;
    const optimisticPost = {
      ...post,
      liked: nextLiked,
      likes: Math.max(0, Number(post.likes || 0) + (nextLiked ? 1 : -1))
    };
    this.setData({ post: optimisticPost, postLiking: true });
    try {
      const result = await apiRequest({
        url: "/api/client/feed/like",
        method: "POST",
        data: { post_id: this.data.id, liked: nextLiked }
      });
      this.setData({
        post: {
          ...optimisticPost,
          liked: Boolean(result && result.liked),
          likes: Number(result && result.likes || 0)
        },
        postLiking: false
      });
    } catch (error) {
      this.setData({ post, postLiking: false });
      wx.showToast({ title: error && error.message || "点赞失败", icon: "none" });
    }
  },

  async toggleSave() {
    const post = this.data.post;
    if (!post || this.data.postSaving) return;
    const nextSaved = !post.saved;
    const optimisticPost = { ...post, saved: nextSaved };
    this.setData({ post: optimisticPost, postSaving: true });
    try {
      const result = await apiRequest({
        url: "/api/client/feed/save",
        method: "POST",
        data: { post_id: this.data.id, saved: nextSaved }
      });
      this.setData({
        post: { ...optimisticPost, saved: Boolean(result && result.saved) },
        postSaving: false
      });
    } catch (error) {
      this.setData({ post, postSaving: false });
      wx.showToast({ title: error && error.message || "收藏失败", icon: "none" });
    }
  },

  onInputComment(event) { this.setData({ commentInput: event.detail.value || "" }); },
  onInputDraftTitle(event) { this.setData({ draftTitle: event.detail.value || "" }); },
  onInputDraftContent(event) { this.setData({ draftContent: event.detail.value || "" }); },
  onInputDraftTags(event) { this.setData({ draftTags: event.detail.value || "" }); },
  onSelectCategory(event) { this.setData({ draftCategory: event.currentTarget.dataset.category || "study" }); },

  async chooseCommentImage() { try { this.setData({ commentImagePath: await chooseSingleImage() }); } catch (error) {} },
  async chooseDraftImage() { try { this.setData({ draftImagePath: await chooseSingleImage() }); } catch (error) {} },
  removeCommentImage() { this.setData({ commentImagePath: "" }); },
  removeDraftImage() { this.setData({ draftImagePath: "" }); },

  async toggleCommentLike(event) {
    const commentId = String(event.currentTarget.dataset.commentId || "");
    if (!commentId || this.data.commentBusyId === commentId) return;
    const current = this.data.comments.find((item) => item.id === commentId);
    if (!current) return;
    const nextLiked = !current.liked;

    this.setData({
      commentBusyId: commentId,
      comments: this.data.comments.map((item) => {
        if (item.id !== commentId) return item;
        return {
          ...item,
          liked: nextLiked,
          likes: Math.max(0, Number(item.likes || 0) + (nextLiked ? 1 : -1))
        };
      })
    });

    try {
      const result = await apiRequest({
        url: "/api/client/feed/comment/like",
        method: "POST",
        data: { comment_id: commentId, liked: nextLiked }
      });
      this.setData({
        commentBusyId: "",
        comments: this.data.comments.map((item) => {
          if (item.id !== commentId) return item;
          return {
            ...item,
            liked: Boolean(result && result.liked),
            likes: Number(result && result.likes || 0)
          };
        })
      });
      await this.loadPost();
    } catch (error) {
      this.setData({
        commentBusyId: "",
        comments: this.data.comments.map((item) => {
          if (item.id !== commentId) return item;
          return current;
        })
      });
      wx.showToast({ title: error && error.message || "点赞失败", icon: "none" });
    }
  },

  async sendComment() {
    const content = String(this.data.commentInput || "").trim();
    const imagePath = String(this.data.commentImagePath || "").trim();
    if (!content && !imagePath) return wx.showToast({ title: "请输入评论或上传图片", icon: "none" });
    if (this.data.commentSubmitting) return;
    this.setData({ commentSubmitting: true });
    try {
      if (imagePath) {
        await uploadFile({
          url: "/api/client/feed/comment/create-with-image",
          filePath: imagePath,
          name: "image",
          formData: { post_id: this.data.id, content, client_id: `wx-${Date.now()}` }
        });
      } else {
        await apiRequest({ url: "/api/client/feed/comment/create", method: "POST", data: { post_id: this.data.id, content, client_id: `wx-${Date.now()}` } });
      }
      this.setData({ commentInput: "", commentImagePath: "", commentSubmitting: false });
      await this.loadComments();
      await this.loadPost();
      wx.showToast({ title: "评论已发送", icon: "success" });
    } catch (error) {
      this.setData({ commentSubmitting: false });
      wx.showToast({ title: error && error.message || "评论失败", icon: "none" });
    }
  },

  async submitPost() {
    const title = String(this.data.draftTitle || "").trim();
    const content = String(this.data.draftContent || "").trim();
    const tags = buildTagArray(this.data.draftTags);
    const imagePath = String(this.data.draftImagePath || "").trim();
    if (!title) return wx.showToast({ title: "请输入帖子标题", icon: "none" });
    if (!content) return wx.showToast({ title: "请输入帖子内容", icon: "none" });
    if (this.data.postSubmitting) return;
    this.setData({ postSubmitting: true });
    try {
      let result = null;
      if (imagePath) {
        result = await uploadFile({
          url: "/api/client/feed/post/create-with-image",
          filePath: imagePath,
          name: "image",
          formData: { category: this.data.draftCategory, title, content, tags: JSON.stringify(tags) }
        });
      } else {
        result = await apiRequest({ url: "/api/client/feed/post/create", method: "POST", data: { category: this.data.draftCategory, title, content, tags } });
      }
      const nextId = normalizePostId(result && result.id);
      this.setData({ postSubmitting: false });
      wx.showToast({ title: "发帖成功", icon: "success" });
      if (nextId) {
        setTimeout(() => {
          wx.redirectTo({ url: `/pages/post/post?id=${encodeURIComponent(nextId)}&title=${encodeURIComponent(title)}` });
        }, 250);
      }
    } catch (error) {
      this.setData({ postSubmitting: false });
      wx.showToast({ title: error && error.message || "发帖失败", icon: "none" });
    }
  },

  async deletePost() {
    if (!this.data.post || !this.data.post.can_delete || this.data.postDeleting) {
      return;
    }
    const confirmed = await new Promise((resolve) => {
      wx.showModal({
        title: "删除原帖",
        content: "删除后帖子和关联评论会一起移除，是否继续？",
        confirmText: "删除",
        confirmColor: "#c9413a",
        success: (res) => resolve(Boolean(res && res.confirm))
      });
    });
    if (!confirmed) {
      return;
    }
    this.setData({ postDeleting: true });
    try {
      await apiRequest({ url: "/api/client/feed/post/delete", method: "POST", data: { post_id: this.data.id } });
      this.setData({ postDeleting: false });
      wx.showToast({ title: "原帖已删除", icon: "success" });
      setTimeout(() => {
        const pages = getCurrentPages();
        if (pages.length > 1) {
          wx.navigateBack();
        } else {
          wx.switchTab({ url: "/pages/home/home" });
        }
      }, 260);
    } catch (error) {
      this.setData({ postDeleting: false });
      wx.showToast({ title: error && error.message || "删除失败", icon: "none" });
    }
  },

  async deleteComment(event) {
    const commentId = event.currentTarget.dataset.commentId;
    if (!commentId) return;
    try {
      await apiRequest({ url: "/api/client/feed/comment/delete", method: "POST", data: { post_id: this.data.id, comment_id: commentId } });
      await this.loadComments();
      await this.loadPost();
    } catch (error) {
      wx.showToast({ title: error && error.message || "删除失败", icon: "none" });
    }
  },

  previewImage(event) {
    const url = event.currentTarget.dataset.url || "";
    if (!url) return;
    wx.previewImage({ current: url, urls: [url] });
  }
});
