const { apiRequest } = require("../../utils/request");
const { getClientPublicName } = require("../../utils/ui");

const TYPE_OPTIONS = [
  { id: "quick", label: "快速代取" },
  { id: "delivery", label: "外卖代拿" },
  { id: "print", label: "打印跑腿" },
  { id: "other", label: "其他跑腿" }
];

function buildForm() {
  const publicName = getClientPublicName("赵同学") || "赵同学";
  return {
    taskType: "quick",
    title: "",
    reward: "5",
    time: "20 分钟内",
    pickupLocation: "",
    destination: "",
    note: "",
    contact: `站内私信 @${publicName}`
  };
}

Page({
  data: {
    typeOptions: TYPE_OPTIONS,
    form: buildForm(),
    submitting: false
  },

  onShow() {
    const app = getApp();
    app.ensureSession().finally(() => {
      if (!this.data.form.contact) {
        this.setData({ form: buildForm() });
      }
    });
  },

  onSelectType(event) {
    const taskType = String(event.currentTarget.dataset.type || "quick");
    this.setData({ "form.taskType": taskType });
  },

  onInputField(event) {
    const field = String(event.currentTarget.dataset.field || "");
    if (!field) {
      return;
    }
    this.setData({ [`form.${field}`]: event.detail.value || "" });
  },

  async submit() {
    const payload = {
      task_type: this.data.form.taskType,
      title: String(this.data.form.title || "").trim(),
      reward: String(this.data.form.reward || "").trim(),
      time: String(this.data.form.time || "").trim(),
      pickup_location: String(this.data.form.pickupLocation || "").trim(),
      destination: String(this.data.form.destination || "").trim(),
      note: String(this.data.form.note || "").trim(),
      contact: String(this.data.form.contact || "").trim()
    };
    if (!payload.title) return wx.showToast({ title: "请填写任务标题", icon: "none" });
    if (!payload.pickup_location) return wx.showToast({ title: "请填写取货点", icon: "none" });
    if (!payload.destination) return wx.showToast({ title: "请填写送达点", icon: "none" });
    if (!payload.contact) return wx.showToast({ title: "请填写联系方式", icon: "none" });
    if (this.data.submitting) return;

    this.setData({ submitting: true });
    try {
      const result = await apiRequest({ url: "/api/client/errands", method: "POST", data: payload });
      const nextId = result && result.id || "";
      this.setData({ submitting: false, form: buildForm() });
      wx.showToast({ title: "需求已发布", icon: "success" });
      setTimeout(() => {
        wx.redirectTo({ url: `/pages/errand/errand?focus=${encodeURIComponent(nextId)}` });
      }, 260);
    } catch (error) {
      this.setData({ submitting: false });
      wx.showToast({ title: error && error.message || "发布失败", icon: "none" });
    }
  }
});