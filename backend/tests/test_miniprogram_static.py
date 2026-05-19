from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_home_hot_window_label_uses_24_hour_state() -> None:
    home_wxml = read_text("wechat-miniprogram/pages/home/home.wxml")
    home_js = read_text("wechat-miniprogram/pages/home/home.js")

    stale_label = "首页 2 " + "小时热帖"

    assert stale_label not in home_wxml
    assert "{{hotWindowTitle}}" in home_wxml
    assert 'const HOME_HOT_TITLE = "首页 24 小时热帖";' in home_js
    assert "/api/client/home/hot-topics" in home_js


def test_public_feed_filters_placeholder_artifacts_on_clients() -> None:
    web_js = read_text("app.js")
    home_js = read_text("wechat-miniprogram/pages/home/home.js")

    assert "isPublicFeedArtifact(item = {})" in web_js
    assert "!apiAdapter.isPublicFeedArtifact(item)" in web_js
    assert "smoke post)" in web_js
    assert "placeholders.has(title)" in web_js

    assert "function isValidationArtifact" in home_js
    assert "smoke post)" in home_js
    assert "placeholders.has(title)" in home_js


def test_user_feed_does_not_render_owner_adoption_badge() -> None:
    web_js = read_text("app.js")
    web_css = read_text("styles.css")
    miniprogram_home_js = read_text("wechat-miniprogram/pages/home/home.js")
    miniprogram_home_wxss = read_text("wechat-miniprogram/pages/home/home.wxss")

    forbidden_labels = [
        "楼主" + "采纳评论",
        "楼主" + "已采纳",
        "博主" + "已采纳",
    ]
    for label in forbidden_labels:
        assert label not in web_js
        assert label not in miniprogram_home_js

    assert "post-badge " + "adopted" not in web_js
    assert ".post-badge." + "adopted" not in web_css
    assert ".post-badge." + "adopted" not in miniprogram_home_wxss


def test_web_interactions_require_wechat_binding_hint() -> None:
    web_js = read_text("app.js")
    miniprogram_auth_js = read_text("wechat-miniprogram/utils/auth.js")
    miniprogram_request_js = read_text("wechat-miniprogram/utils/request.js")

    assert "wechat_bind_required" in web_js
    assert "function requireWechatBoundAction" in web_js
    assert "async function ensureWechatBoundAction" in web_js
    assert "refreshWechatBoundForProtectedAction" in web_js
    assert "apiRequest(API_CONFIG.endpoints.clientMe" in web_js
    assert "await ensureWechatBoundAction('发布帖子')" in web_js
    assert "replyTarget ? '回复评论' : '发表评论'" in web_js
    assert "await ensureWechatBoundAction('点赞帖子')" in web_js
    assert "await ensureWechatBoundAction('发布跑腿任务')" in web_js
    assert "await ensureWechatBoundAction('点赞评论')" in web_js
    assert "await ensureWechatBoundAction('查询教务数据')" in web_js
    assert "await ensureWechatBoundAction('查看我的帖子')" in web_js
    assert "await ensureWechatBoundAction('查看我的点赞')" in web_js
    assert "await ensureWechatBoundAction(type === 'saved' ? '查看收藏列表' : '查看收到的赞')" in web_js
    assert "await ensureWechatBoundAction('修改发言昵称')" in web_js
    assert "wechatContext: '查询教务数据'" in web_js
    assert "wechatContext: '查看消息中心'" in web_js
    assert "发帖、评论、点赞、收藏、跑腿和教务查询" in web_js
    assert "绑定后才能在网页端互动" in web_js
    assert "loginWithWechatRuntime" in miniprogram_auth_js
    assert "WECHAT_BOUND_KEY" in miniprogram_request_js


def test_miniprogram_images_are_compressed_and_visible_in_lists() -> None:
    image_util_js = read_text("wechat-miniprogram/utils/image.js")
    request_js = read_text("wechat-miniprogram/utils/request.js")
    post_js = read_text("wechat-miniprogram/pages/post/post.js")
    post_wxml = read_text("wechat-miniprogram/pages/post/post.wxml")
    home_js = read_text("wechat-miniprogram/pages/home/home.js")
    home_wxml = read_text("wechat-miniprogram/pages/home/home.wxml")
    home_wxss = read_text("wechat-miniprogram/pages/home/home.wxss")
    profile_list_js = read_text("wechat-miniprogram/pages/profile-list/profile-list.js")
    profile_list_wxml = read_text("wechat-miniprogram/pages/profile-list/profile-list.wxml")
    profile_list_wxss = read_text("wechat-miniprogram/pages/profile-list/profile-list.wxss")

    assert "MAX_UPLOAD_IMAGE_BYTES = 850 * 1024" in image_util_js
    assert "wx.compressImage" in image_util_js
    assert "compressImageForUpload" in post_js
    assert "commentImageMeta" in post_js
    assert "draftImageMeta" in post_js
    assert "上传图片（自动压缩）" not in post_wxml
    assert "上传图片" in post_wxml
    assert "statusCode === 413" in request_js
    assert "图片过大" in request_js
    assert "imageUrl: normalizeImageUrl" in home_js
    assert 'class="post-image"' in home_wxml
    assert 'mode="widthFix"' in home_wxml
    assert "catchtap=\"previewFeedImage\"" in home_wxml
    assert ".post-image" in home_wxss
    assert "imageUrl: normalizeImageUrl" in profile_list_js
    assert 'class="profile-post-image"' in profile_list_wxml
    assert 'mode="widthFix"' in profile_list_wxml
    assert "height: 300rpx" not in profile_list_wxss


def test_own_posts_can_be_deleted_from_web_and_miniprogram() -> None:
    web_js = read_text("app.js")
    web_html = read_text("index.html")
    web_css = read_text("styles.css")
    profile_list_js = read_text("wechat-miniprogram/pages/profile-list/profile-list.js")
    profile_list_wxml = read_text("wechat-miniprogram/pages/profile-list/profile-list.wxml")
    post_wxml = read_text("wechat-miniprogram/pages/post/post.wxml")

    assert "feedPostDelete: '/api/client/feed/post/delete'" in web_js
    assert "async deletePost(postId)" in web_js
    assert "function requestDeletePost" in web_js
    assert "canDelete: Boolean(item.can_delete || item.canDelete)" in web_js
    assert "data-action=\"delete\"" in web_js
    assert "postDetailDeleteBtn" in web_js
    assert 'id="postDetailDeleteBtn"' in web_html
    assert ".subpage-delete-btn" in web_css
    assert "删除后评论、点赞、收藏和消息提醒会同步清理" in web_js

    assert "can_delete: Boolean(item.can_delete || item.canDelete)" in profile_list_js
    assert "async deletePost(event)" in profile_list_js
    assert 'url: "/api/client/feed/post/delete"' in profile_list_js
    assert 'catchtap="deletePost"' in profile_list_wxml
    assert "profile-post-delete" in profile_list_wxml
    assert 'bindtap="deletePost"' in post_wxml


def test_errand_claimed_tasks_stay_visible_with_contact_on_web_and_miniprogram() -> None:
    web_js = read_text("app.js")
    errand_js = read_text("wechat-miniprogram/pages/errand/errand.js")
    errand_wxml = read_text("wechat-miniprogram/pages/errand/errand.wxml")
    errand_wxss = read_text("wechat-miniprogram/pages/errand/errand.wxss")

    assert "mergeErrandTaskLists" in web_js
    assert "apiAdapter.fetchErrands('my')" in web_js
    assert "activeErrandStatusFilter = 'inprogress'" in web_js
    assert "activeErrandStatusFilter = 'done'" in web_js
    assert "我的接单" in web_js

    assert "function mergeTaskLists" in errand_js
    assert "function normalizeTaskFlags" in errand_js
    assert "function normalizeActionTask" in errand_js
    assert 'url: "/api/client/errands/my"' in errand_js
    assert "Promise.allSettled" in errand_js
    assert "isWechatBindRequiredError" in errand_js
    assert "optimisticTasks" in errand_js
    assert "markPendingRunnerTask" in errand_js
    assert "preserveMyTasks" in errand_js
    assert "clearConfirmedPendingTasks" in errand_js
    assert "getTokenInfo().userId" in errand_js
    assert 'normalizeTaskFlags({ id: taskId, ...item }, userId, ["claim", "delivered", "confirm"].includes(action))' in errand_js
    assert "activeStatus: nextStatus" in errand_js
    assert 'action === "claim" || action === "delivered" ? "inprogress"' in errand_js
    assert 'action === "confirm"' in errand_js
    assert "await this.loadTasks(taskId, { preserveMyTasks: true })" in errand_js
    assert "我的接单" in errand_wxml
    assert "item.can_view_contact ? item.publisher_contact : '接单后可见'" in errand_wxml
    assert "item.primary_action.key !== 'detail'" in errand_wxml
    assert ".tag-chip-role" in errand_wxss


def test_session_logout_controls_exist_for_web_and_miniprogram() -> None:
    web_js = read_text("app.js")
    web_html = read_text("index.html")
    profile_js = read_text("wechat-miniprogram/pages/profile/profile.js")
    profile_wxml = read_text("wechat-miniprogram/pages/profile/profile.wxml")

    assert "CLIENT_WEB_SESSION_EXPIRY_KEY" in web_js
    assert "isWebSessionExpired" in web_js
    assert "handleWebSessionExpired" in web_js
    assert "sessionType === 'web'" in web_js
    assert "data-menu-action=\"webLogout\"" in web_html
    assert "await logoutClient({ remote: true })" in web_js
    assert 'data-action="logoutWebSessions"' in profile_wxml
    assert "logoutWebSessions" in profile_js
    assert 'url: "/api/client/auth/logout-web-sessions"' in profile_js


def test_topic_and_cross_group_pages_match_web_and_miniprogram() -> None:
    web_js = read_text("app.js")
    web_html = read_text("index.html")
    web_css = read_text("styles.css")
    app_json = read_text("wechat-miniprogram/app.json")
    groups_js = read_text("wechat-miniprogram/pages/groups/groups.js")
    groups_wxml = read_text("wechat-miniprogram/pages/groups/groups.wxml")
    groups_wxss = read_text("wechat-miniprogram/pages/groups/groups.wxss")
    group_detail_js = read_text("wechat-miniprogram/pages/group-detail/group-detail.js")
    group_detail_wxml = read_text("wechat-miniprogram/pages/group-detail/group-detail.wxml")
    group_detail_wxss = read_text("wechat-miniprogram/pages/group-detail/group-detail.wxss")

    assert "const topicChannelConfigs" in web_js
    assert "async function openTopicChannelPage" in web_js
    assert "apiAdapter.searchPosts(config.keyword" in web_js
    assert "发布相关帖子" in web_js
    assert "titlePlaceholder: config.titlePlaceholder" in web_js
    assert "contentPlaceholder: config.contentPlaceholder" in web_js
    assert "void openTopicChannelPage('course')" in web_js
    assert "课程评价共建帖" in web_js
    assert "课程评价：数据库系统 补充" in web_js

    assert 'id="crossPostCreateBtn"' in web_html
    assert 'id="crossGroupScroll"' in web_html
    assert 'id="crossGroupDetail"' in web_html
    assert 'id="crossPostList"' in web_html
    assert "function renderCrossPostList" in web_js
    assert "async function loadCrossMatches" in web_js
    assert "function openCrossGroupDetail" in web_js
    assert "function returnCrossGroupList" in web_js
    assert "currentCrossPostItems" in web_js
    assert "加入小组" in web_js
    assert "cross-create-btn" in web_css
    assert ".cross-scroll" in web_css
    assert ".cross-fab" in web_css
    assert ".cross-sheet.is-detail" in web_css
    assert ".cross-post-panel" in web_css
    assert ".cross-post" in web_css

    assert '"pages/group-detail/group-detail"' in app_json
    assert 'class="group-join-btn"' in groups_wxml
    assert 'catchtap="joinGroup"' in groups_wxml
    assert "joinGroup(event)" in groups_js
    assert "buildGroupDetailUrl" in groups_js
    assert "/pages/group-detail/group-detail" in groups_js
    assert ".group-join-btn" in groups_wxss
    assert "单独小组页" in group_detail_wxml
    assert "openComposer" in group_detail_js
    assert "api/client/search/posts" in group_detail_js
    assert "@import \"../groups/groups.wxss\"" in group_detail_wxss


def test_web_unbound_profile_uses_privacy_gate_defaults() -> None:
    web_js = read_text("app.js")
    web_html = read_text("index.html")
    web_css = read_text("styles.css")

    assert "APP_BUILD_VERSION = '20260519-08'" in web_js
    assert "app.js?v=20260519-08" in web_html
    assert "styles.css?v=20260519-08" in web_html
    assert 'class="card profile-hero is-locked"' in web_html
    assert '<h3 id="profileName">请先完成微信互通</h3>' in web_html
    assert '<strong id="profilePostCount">--</strong>' in web_html
    assert '<strong id="profileLikeCount">--</strong>' in web_html
    assert '<strong id="profilePublicName">互通后显示</strong>' in web_html
    assert "function hasProtectedProfileAccess" in web_js
    assert "function renderProtectedProfileGate" in web_js
    assert "未互通前，网页端不会展示个人资料、消息和教务信息" in web_js
    assert "完成微信互通后查看消息" in web_js
    assert "renderProtectedProfileGate();" in web_js
    assert ".profile-hero.is-locked" in web_css
    assert ".inbox-row-locked" in web_css
