Component({
  data: {
    selected: 0,
    profileDot: false,
    list: [
      { pagePath: "/pages/home/home", text: "首页", key: "home" },
      { pagePath: "/pages/search/search", text: "搜索", key: "search" },
      { pagePath: "/pages/knowledge/knowledge", text: "知识库", key: "knowledge" },
      { pagePath: "/pages/profile/profile", text: "我的", key: "profile" }
    ]
  },

  methods: {
    onSwitch(event) {
      const index = Number(event.currentTarget.dataset.index || 0);
      const path = String(event.currentTarget.dataset.path || "");
      if (!path) {
        return;
      }
      if (index === this.data.selected) {
        return;
      }
      this.setData({ selected: index });
      wx.switchTab({ url: path });
    }
  }
});
