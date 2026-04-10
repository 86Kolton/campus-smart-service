const tabs = Array.from(document.querySelectorAll('.tab'));
const screens = Array.from(document.querySelectorAll('.screen'));

const todaySentence = document.getElementById('todaySentence');
const headerGreeting = document.getElementById('headerGreeting');

const marketQuery = document.getElementById('marketQuery');
const marketSearchBtn = document.getElementById('marketSearchBtn');
const marketResultList = document.getElementById('marketResultList');
const marketCount = document.getElementById('marketCount');
const recentSearchList = document.getElementById('recentSearchList');
const clearRecentBtn = document.getElementById('clearRecentBtn');
const sortButtons = Array.from(document.querySelectorAll('.sort-btn'));
const loadMoreSearchBtn = document.getElementById('loadMoreSearchBtn');

const wikiBoard = document.getElementById('wikiBoard');
const wikiForm = document.getElementById('wikiForm');
const wikiInput = document.getElementById('wikiInput');
const wikiQuickRow = document.getElementById('wikiQuickRow');
const wikiDeepThinkingToggle = document.getElementById('wikiDeepThinkingToggle');
const wikiDetailSheet = document.getElementById('wikiDetailSheet');
const wikiDetailMask = document.getElementById('wikiDetailMask');
const wikiDetailTitle = document.getElementById('wikiDetailTitle');
const wikiDetailList = document.getElementById('wikiDetailList');
const wikiDetailCloseBtn = document.getElementById('wikiDetailCloseBtn');

const copyUsageBtn = document.getElementById('copyUsageBtn');
const feedList = document.getElementById('feedList');
const homeHotList = document.getElementById('homeHotList');
const feedFilterButtons = Array.from(document.querySelectorAll('.feed-filter-btn'));
const fabBtn = document.getElementById('globalFabBtn');
const appShell = document.querySelector('.app-shell');

const profileMessageList = document.getElementById('profileMessageList');
const profileTabDot = document.getElementById('profileTabDot');
const profileName = document.getElementById('profileName');
const profileMeta = document.getElementById('profileMeta');
const profileBindState = document.getElementById('profileBindState');
const profilePublicName = document.getElementById('profilePublicName');
const profilePublicNameMenuHint = document.getElementById('profilePublicNameMenuHint');
const profileInteropHint = document.getElementById('profileInteropHint');
const profilePostCount = document.getElementById('profilePostCount');
const profileLikeCount = document.getElementById('profileLikeCount');
const wechatBindRow = document.querySelector('.menu-row[data-menu-action="wechatBind"]');

const detailSheet = document.getElementById('inboxDetailSheet');
const detailSheetMask = document.getElementById('detailSheetMask');
const closeDetailSheetBtn = document.getElementById('closeDetailSheetBtn');
const detailSheetTitle = document.getElementById('detailSheetTitle');
const detailTabButtons = Array.from(document.querySelectorAll('.detail-tab'));
const inboxDetailList = document.getElementById('inboxDetailList');
const markTypeReadBtn = document.getElementById('markTypeReadBtn');
const markAllReadBtn = document.getElementById('markAllReadBtn');
const inboxNetworkHint = document.getElementById('inboxNetworkHint');
const searchResultSheet = document.getElementById('searchResultSheet');
const searchResultMask = document.getElementById('searchResultMask');
const backSearchResultBtn = document.getElementById('backSearchResultBtn');
const searchResultTitle = document.getElementById('searchResultTitle');
const searchResultSub = document.getElementById('searchResultSub');
const searchResultCount = document.getElementById('searchResultCount');
const searchResultList = document.getElementById('searchResultList');
const searchPagePrevBtn = document.getElementById('searchPagePrevBtn');
const searchPageNextBtn = document.getElementById('searchPageNextBtn');
const searchPageNumbers = document.getElementById('searchPageNumbers');
const searchPageJumpInput = document.getElementById('searchPageJumpInput');
const searchPageJumpBtn = document.getElementById('searchPageJumpBtn');
const searchPageSortButtons = Array.from(document.querySelectorAll('.search-page-sort-btn'));
const imageViewer = document.getElementById('imageViewer');
const imageViewerImg = document.getElementById('imageViewerImg');
const imageViewerClose = document.getElementById('imageViewerClose');
const subpageSheet = document.getElementById('subpageSheet');
const subpageMask = document.getElementById('subpageMask');
const backSubpageBtn = document.getElementById('backSubpageBtn');
const subpageTitle = document.getElementById('subpageTitle');
const subpageSub = document.getElementById('subpageSub');
const subpageBody = document.getElementById('subpageBody');
const subpageList = document.getElementById('subpageList');
const subpageActionBtn = document.getElementById('subpageActionBtn');
const errandSheet = document.getElementById('errandSheet');
const errandMask = document.getElementById('errandMask');
const backErrandBtn = document.getElementById('backErrandBtn');
const errandList = document.getElementById('errandList');
const errandCreateBtn = document.getElementById('errandCreateBtn');
const errandFilterButtons = Array.from(document.querySelectorAll('.errand-filters .chip[data-errand-filter]'));
const errandOpenCount = document.getElementById('errandOpenCount');
const errandInProgressCount = document.getElementById('errandInProgressCount');
const errandDoneCount = document.getElementById('errandDoneCount');
const crossGroupSheet = document.getElementById('crossGroupSheet');
const crossGroupMask = document.getElementById('crossGroupMask');
const backCrossGroupBtn = document.getElementById('backCrossGroupBtn');
const crossGroupList = document.getElementById('crossGroupList');
const crossTopicList = document.getElementById('crossTopicList');
const postDetailSheet = document.getElementById('postDetailSheet');
const postDetailMask = document.getElementById('postDetailMask');
const backPostDetailBtn = document.getElementById('backPostDetailBtn');
const postDetailTitle = document.getElementById('postDetailTitle');
const postDetailMeta = document.getElementById('postDetailMeta');
const postDetailHeading = document.getElementById('postDetailHeading');
const postDetailContent = document.getElementById('postDetailContent');
const postDetailTags = document.getElementById('postDetailTags');
const postFallbackList = document.getElementById('postFallbackList');
const postDetailImage = document.getElementById('postDetailImage');
const postDetailPreview = document.getElementById('postDetailPreview');
const postDetailCommentBtn = document.getElementById('postDetailCommentBtn');
const commentSheet = document.getElementById('commentSheet');
const commentSheetMask = document.getElementById('commentSheetMask');
const backCommentSheetBtn = document.getElementById('backCommentSheetBtn');
const commentSheetTitle = document.getElementById('commentSheetTitle');
const commentSheetSub = document.getElementById('commentSheetSub');
const commentList = document.getElementById('commentList');
const commentForm = document.getElementById('commentForm');
const commentInput = document.getElementById('commentInput');
const commentSendBtn = document.getElementById('commentSendBtn');
const commentImageInput = document.getElementById('commentImageInput');
const commentImageMeta = document.getElementById('commentImageMeta');
const commentReplyMeta = document.getElementById('commentReplyMeta');
const commentReplyText = document.getElementById('commentReplyText');
const commentReplyCancelBtn = document.getElementById('commentReplyCancelBtn');

const postComposerSheet = document.getElementById('postComposerSheet');
const postComposerMask = document.getElementById('postComposerMask');
const closePostComposerBtn = document.getElementById('closePostComposerBtn');
const postComposerForm = document.getElementById('postComposerForm');
const postCategoryInput = document.getElementById('postCategoryInput');
const postTitleInput = document.getElementById('postTitleInput');
const postContentInput = document.getElementById('postContentInput');
const postTagsInput = document.getElementById('postTagsInput');
const postImageInput = document.getElementById('postImageInput');
const postImageMeta = document.getElementById('postImageMeta');
const postSubmitBtn = document.getElementById('postSubmitBtn');
const eduItems = Array.from(document.querySelectorAll('.edu-item[data-edu-action]'));
const eduSheet = document.getElementById('eduSheet');
const eduSheetMask = document.getElementById('eduSheetMask');
const backEduSheetBtn = document.getElementById('backEduSheetBtn');
const eduSheetTitle = document.getElementById('eduSheetTitle');
const eduSheetSub = document.getElementById('eduSheetSub');
const eduSheetBody = document.getElementById('eduSheetBody');
const eduCard = document.querySelector('.edu-card');

const STORAGE_KEY = 'campus_ui_state_v2';
const LIKED_STORAGE_KEY = 'campus_liked_posts_v1';
const COMMENT_LIKED_STORAGE_KEY = 'campus_liked_comments_v1';
const CLIENT_TOKEN_KEY = 'campus_client_token_v1';
const CLIENT_REFRESH_KEY = 'campus_client_refresh_v1';
const CLIENT_BOOTSTRAP_USERNAME_KEY = 'campus_bootstrap_username_v1';
const CLIENT_BOOTSTRAP_PASSWORD_KEY = 'campus_bootstrap_password_v1';
const ERRAND_STORAGE_KEY = 'campus_errand_tasks_v2';
const KNOWLEDGE_UI_CONFIG = Object.freeze({
  showQuickPrompts: false
});

function loadClientToken() {
  try {
    return String(localStorage.getItem(CLIENT_TOKEN_KEY) || '');
  } catch (error) {
    return '';
  }
}

function saveClientToken(token) {
  try {
    if (token) {
      localStorage.setItem(CLIENT_TOKEN_KEY, String(token));
    } else {
      localStorage.removeItem(CLIENT_TOKEN_KEY);
    }
  } catch (error) {
    // ignore
  }
}

function loadClientRefreshToken() {
  try {
    return String(localStorage.getItem(CLIENT_REFRESH_KEY) || '');
  } catch (error) {
    return '';
  }
}

function saveClientRefreshToken(token) {
  try {
    if (token) {
      localStorage.setItem(CLIENT_REFRESH_KEY, String(token));
    } else {
      localStorage.removeItem(CLIENT_REFRESH_KEY);
    }
  } catch (error) {
    // ignore
  }
}

function loadBootstrapCredentials() {
  try {
    return {
      username: String(sessionStorage.getItem(CLIENT_BOOTSTRAP_USERNAME_KEY) || '').trim(),
      password: String(sessionStorage.getItem(CLIENT_BOOTSTRAP_PASSWORD_KEY) || '').trim()
    };
  } catch (error) {
    return { username: '', password: '' };
  }
}

function saveBootstrapCredentials(username, password) {
  try {
    sessionStorage.setItem(CLIENT_BOOTSTRAP_USERNAME_KEY, String(username || '').trim());
    sessionStorage.setItem(CLIENT_BOOTSTRAP_PASSWORD_KEY, String(password || '').trim());
  } catch (error) {
    // ignore
  }
}

function clearBootstrapCredentials() {
  try {
    sessionStorage.removeItem(CLIENT_BOOTSTRAP_USERNAME_KEY);
    sessionStorage.removeItem(CLIENT_BOOTSTRAP_PASSWORD_KEY);
  } catch (error) {
    // ignore
  }
}

function buildBootstrapCredentials() {
  const seed = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
  return {
    username: `web_${seed}`,
    password: `demo-${seed}-A1`,
    displayName: '网页访客'
  };
}

function getUserScopedKey(base, userId) {
  const uid = Number(userId || 0);
  return uid ? `${base}_${uid}` : base;
}

function loadLikedSet(userId = 0) {
  try {
    const raw = localStorage.getItem(getUserScopedKey(LIKED_STORAGE_KEY, userId));
    if (!raw) {
      return new Set();
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return new Set(parsed.map((item) => String(item)));
    }
  } catch (error) {
    // ignore
  }
  return new Set();
}

function saveLikedSet(set, userId = 0) {
  try {
    const arr = Array.from(set);
    localStorage.setItem(getUserScopedKey(LIKED_STORAGE_KEY, userId), JSON.stringify(arr));
  } catch (error) {
    // ignore
  }
}

const likedPostIds = loadLikedSet();

function loadCommentLikedSet(userId = 0) {
  try {
    const raw = localStorage.getItem(getUserScopedKey(COMMENT_LIKED_STORAGE_KEY, userId));
    if (!raw) {
      return new Set();
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return new Set(parsed.map((item) => String(item)));
    }
  } catch (error) {
    // ignore
  }
  return new Set();
}

function saveCommentLikedSet(set, userId = 0) {
  try {
    const arr = Array.from(set);
    localStorage.setItem(getUserScopedKey(COMMENT_LIKED_STORAGE_KEY, userId), JSON.stringify(arr));
  } catch (error) {
    // ignore
  }
}

const likedCommentIds = loadCommentLikedSet();

function normalizeErrandStatus(status) {
  const safe = String(status || '').trim();
  if (['open', 'inprogress', 'waiting_confirm', 'done', 'canceled'].includes(safe)) {
    return safe;
  }
  return 'open';
}

function normalizeErrandTask(raw, index = 0) {
  const safe = raw && typeof raw === 'object' ? raw : {};
  const nowIso = new Date().toISOString();
  const id = String(safe.id || `e-seed-${index + 1}`);
  const status = normalizeErrandStatus(safe.status);
  return {
    id,
    title: String(safe.title || '未命名任务'),
    reward: String(safe.reward || '￥0'),
    time: String(safe.time || '尽快'),
    distance: String(safe.distance || '未知'),
    tag: String(safe.tag || '跑腿任务'),
    note: String(safe.note || ''),
    publisherId: Number(safe.publisherId || safe.publisher_id || 0),
    publisherName: String(safe.publisherName || safe.publisher_name || '匿名同学'),
    publisherContact: String(safe.publisherContact || safe.publisher_contact || ''),
    runnerId: Number(safe.runnerId || safe.runner_id || 0),
    runnerName: String(safe.runnerName || safe.runner_name || ''),
    runnerContact: String(safe.runnerContact || safe.runner_contact || ''),
    status,
    createdAt: String(safe.createdAt || safe.created_at || nowIso),
    acceptedAt: String(safe.acceptedAt || safe.accepted_at || ''),
    deliveredAt: String(safe.deliveredAt || safe.delivered_at || ''),
    confirmedAt: String(safe.confirmedAt || safe.confirmed_at || '')
  };
}

function loadErrandTasks(seed = []) {
  try {
    const raw = localStorage.getItem(ERRAND_STORAGE_KEY);
    if (!raw) {
      return seed.map((item, index) => normalizeErrandTask(item, index));
    }
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return seed.map((item, index) => normalizeErrandTask(item, index));
    }
    return parsed.map((item, index) => normalizeErrandTask(item, index));
  } catch (error) {
    return seed.map((item, index) => normalizeErrandTask(item, index));
  }
}

function saveErrandTasks(tasks) {
  try {
    localStorage.setItem(ERRAND_STORAGE_KEY, JSON.stringify(Array.isArray(tasks) ? tasks : []));
  } catch (error) {
    // ignore
  }
}

function detectApiBaseUrl() {
  try {
    const injected = typeof window !== 'undefined' ? String(window.__API_BASE_URL__ || '').trim() : '';
    if (injected) {
      return injected.replace(/\/$/, '');
    }
  } catch (error) {
    // ignore
  }

  try {
    const saved = typeof localStorage !== 'undefined' ? String(localStorage.getItem('campus_api_base_url') || '').trim() : '';
    if (saved) {
      return saved.replace(/\/$/, '');
    }
  } catch (error) {
    // ignore
  }

  try {
    if (typeof window !== 'undefined' && window.location && window.location.search) {
      const params = new URLSearchParams(window.location.search);
      const fromQuery = String(params.get('apiBase') || '').trim();
      if (fromQuery) {
        return fromQuery.replace(/\/$/, '');
      }
    }
  } catch (error) {
    // ignore
  }

  try {
    if (typeof window !== 'undefined' && window.location) {
      const protocol = String(window.location.protocol || '');
      const hostname = String(window.location.hostname || '');
      const port = String(window.location.port || '');
      const origin = String(window.location.origin || '').trim();
      const isHttp = protocol === 'http:' || protocol === 'https:';
      const isLocalHost = hostname === '127.0.0.1' || hostname === 'localhost';
      const devPorts = new Set(['3000', '5173', '5174', '5500', '8080']);
      if (isHttp && isLocalHost && devPorts.has(port)) {
        return 'http://127.0.0.1:8000';
      }
      if (isHttp && origin) {
        return origin.replace(/\/$/, '');
      }
    }
  } catch (error) {
    // ignore
  }

  return 'http://127.0.0.1:8000';
}

function getApiBaseLabel() {
  const base = String(API_CONFIG && API_CONFIG.baseUrl ? API_CONFIG.baseUrl : '').trim();
  if (!base) {
    return '';
  }
  try {
    return new URL(base).host;
  } catch (error) {
    return base;
  }
}

// Backend interface placeholders (reserved for future integration)
const API_CONFIG = {
  enabled: true,
  baseUrl: detectApiBaseUrl(),
  eduSessionToken: 'demo-edu-session',
  timeoutMs: 3500,
  refreshOnProfileEnter: true,
  pollingEnabled: true,
  pollingIntervalMs: 30000,
  endpoints: {
    // auth
    clientLogin: '/api/client/auth/login',
    clientRegister: '/api/client/auth/register',
    clientMe: '/api/client/auth/me',
    clientRefresh: '/api/client/auth/refresh',
    clientLogout: '/api/client/auth/logout',
    clientWechatLogin: '/api/client/auth/wechat/login',
    clientWechatBind: '/api/client/auth/wechat/bind',
    clientWebLoginCode: '/api/client/auth/web-login-code',
    clientWebLoginExchange: '/api/client/auth/web-login-exchange',
    // home/feed
    feedList: '/api/client/feed/list',
    feedPostDetail: '/api/client/feed/post',
    feedLike: '/api/client/feed/like',
    feedSave: '/api/client/feed/save',
    feedPostCreate: '/api/client/feed/post/create',
    feedPostCreateWithImage: '/api/client/feed/post/create-with-image',
    feedComments: '/api/client/feed/comments',
    feedCommentCreate: '/api/client/feed/comment/create',
    feedCommentCreateWithImage: '/api/client/feed/comment/create-with-image',
    feedCommentLike: '/api/client/feed/comment/like',
    feedCommentDelete: '/api/client/feed/comment/delete',
    homeHotTopics: '/api/client/home/hot-topics',
    // search
    searchPosts: '/api/client/search/posts',
    unreadCount: '/api/client/messages/unread-count',
    inboxLikes: '/api/client/messages/likes',
    inboxSaved: '/api/client/messages/saved',
    markRead: '/api/client/messages/mark-read',
    recentSearches: '/api/client/search/recent',
    // knowledge/profile
    knowledgeAsk: '/api/client/knowledge/ask',
    profileSummary: '/api/client/profile/summary',
    profileSettings: '/api/client/profile/settings',
    profilePublicName: '/api/client/profile/public-name',
    profileMyPosts: '/api/client/profile/my-posts',
    profileLikedPosts: '/api/client/profile/liked-posts',
    errandList: '/api/client/errands',
    errandMyList: '/api/client/errands/my',
    errandAction: '/api/client/errands/action',
    // edu (placeholder secure endpoints)
    eduOverview: '/api/client/edu/overview',
    eduGrades: '/api/client/edu/grades',
    eduExams: '/api/client/edu/exams',
    eduSchedule: '/api/client/edu/schedule',
    eduFreeClassrooms: '/api/client/edu/free-classrooms'
  }
};

const marketPosts = [
  {
    id: 'm-1',
    title: '二食堂错峰窗口实测',
    snippet: '11:50 前北门清汤窗口平均排队 6-8 分钟，12:20 后麻辣烫窗口排队明显增加。',
    likes: 214,
    comments: 52,
    meta: '食堂 · 当日更新',
    updatedAt: '2026-04-06 19:12',
    hotScore: 98,
    keywords: ['食堂', '排队', '窗口', '麻辣烫', '错峰']
  },
  {
    id: 'm-2',
    title: 'A1-307 晚间自习位反馈',
    snippet: '19:00 后插座较充足，噪音中低，适合长时段复习。',
    likes: 189,
    comments: 37,
    meta: '自习教室 · 夜间',
    updatedAt: '2026-04-06 18:36',
    hotScore: 91,
    keywords: ['自习', '教室', '图书馆', '安静', '插座']
  },
  {
    id: 'm-3',
    title: '周三调课通知集中帖',
    snippet: '多门课程调至 B3-201 与 A2-403，17:00 前会同步到课表。',
    likes: 143,
    comments: 28,
    meta: '教务 · 临时通知',
    updatedAt: '2026-04-06 17:54',
    hotScore: 78,
    keywords: ['调课', '通知', '课表', '教务']
  },
  {
    id: 'm-4',
    title: '二手显示器验机建议',
    snippet: '建议现场测坏点和接口，优先看通电时长小于 5000 小时的机型。',
    likes: 121,
    comments: 41,
    meta: '二手交易 · 经验贴',
    updatedAt: '2026-04-05 21:16',
    hotScore: 72,
    keywords: ['二手', '显示器', '验机', '交易']
  },
  {
    id: 'm-5',
    title: '考研自习室插座分布',
    snippet: 'A2 四层东侧插座密度更高，但晚高峰占座速度快。',
    likes: 112,
    comments: 25,
    meta: '自习教室 · 经验贴',
    updatedAt: '2026-04-04 22:08',
    hotScore: 65,
    keywords: ['考研', '自习', '插座', '教室']
  },
  {
    id: 'm-6',
    title: '周末校车末班时间',
    snippet: '东门线末班 22:10，西门线末班 22:25，考试周将临时加班。',
    likes: 96,
    comments: 19,
    meta: '出行 · 校车',
    updatedAt: '2026-04-03 20:35',
    hotScore: 57,
    keywords: ['校车', '班次', '末班', '周末']
  }
];

const DEFAULT_ERRAND_TASKS = [
  {
    id: 'e-1',
    title: '帮我取快递（南门驿站）',
    reward: '￥6',
    time: '15 分钟内',
    distance: '600m',
    tag: '快速代取',
    note: '可顺路带一杯奶茶',
    publisherId: 3,
    publisherName: '小吴',
    publisherContact: 'wx: xiaowu_n',
    runnerId: 0,
    runnerName: '',
    runnerContact: '',
    status: 'open',
    createdAt: '2026-04-07T09:35:00+08:00',
    acceptedAt: '',
    deliveredAt: '',
    confirmedAt: ''
  },
  {
    id: 'e-2',
    title: '外卖代拿（北食堂）',
    reward: '￥4',
    time: '20 分钟内',
    distance: '400m',
    tag: '外卖代拿',
    note: '取到后电话联系',
    publisherId: 2,
    publisherName: '小陈',
    publisherContact: '手机号 139****6612',
    runnerId: 0,
    runnerName: '',
    runnerContact: '',
    status: 'open',
    createdAt: '2026-04-07T09:41:00+08:00',
    acceptedAt: '',
    deliveredAt: '',
    confirmedAt: ''
  },
  {
    id: 'e-3',
    title: '打印资料 30 页',
    reward: '￥8',
    time: '1 小时内',
    distance: '教学楼 A4',
    tag: '打印跑腿',
    note: '需要双面黑白',
    publisherId: 4,
    publisherName: '研一学长',
    publisherContact: 'qq: 2748****',
    runnerId: 1,
    runnerName: '赵毅',
    runnerContact: '站内私信',
    status: 'inprogress',
    createdAt: '2026-04-07T08:20:00+08:00',
    acceptedAt: '2026-04-07T08:28:00+08:00',
    deliveredAt: '',
    confirmedAt: ''
  }
];

let errandTasks = [];

const crossGroups = [
  {
    id: 'g-1',
    title: '期末自习互助群',
    members: 136,
    online: 42,
    tags: ['自习', '考试', '资料']
  },
  {
    id: 'g-2',
    title: '空教室情报站',
    members: 98,
    online: 27,
    tags: ['空教室', '自习', '安静']
  },
  {
    id: 'g-3',
    title: '跨校竞赛组队',
    members: 73,
    online: 15,
    tags: ['竞赛', '组队', '项目']
  }
];

const crossTopics = [
  {
    id: 't-1',
    title: 'A 区今晚 9 点后还有空教室吗？',
    meta: '来自 空教室情报站 · 2 分钟前',
    heat: '2.1k',
    query: '今晚 9 点 空教室'
  },
  {
    id: 't-2',
    title: '软件测试复习资料互换',
    meta: '来自 期末自习互助群 · 8 分钟前',
    heat: '1.3k',
    query: '软件测试 复习资料'
  },
  {
    id: 't-3',
    title: '计设竞赛有没有跨校队友？',
    meta: '来自 跨校竞赛组队 · 25 分钟前',
    heat: '980',
    query: '跨校 竞赛 组队'
  }
];

const hotTopicPostMap = {
  'hot-1': 'm-1',
  'hot-2': 'm-2',
  'hot-3': 'm-3'
};

const rankHotPostMap = {
  '二手显示器验机建议': 'm-4',
  '考研自习室插座分布': 'm-5',
  '周末校车末班时间': 'm-6'
};

let homeHotTopics = [
  { id: 'hot-1', rank: 1, query: '二食堂清汤窗口排队更快吗？', title: '二食堂错峰窗口实测', heat: '9.8k', postRef: 'm-1', sourceType: 'search' },
  { id: 'hot-2', rank: 2, query: 'A1 教学楼晚上自习体验如何？', title: 'A1-307 晚间自习位反馈', heat: '8.6k', postRef: 'm-2', sourceType: 'search' },
  { id: 'hot-3', rank: 3, query: '周三临时调课是否已经同步到课表？', title: '周三调课通知集中帖', heat: '7.9k', postRef: 'm-3', sourceType: 'search' }
];

const feedPosts = [
  {
    id: 'p-1',
    category: 'study',
    authorId: 2,
    author: '@清晨图书馆人',
    avatar: '图书',
    level: 'Lv.4',
    time: '刚刚',
    title: 'A1-307 晚上 8 点后插座充足',
    content: '空调稳定，噪音中低，建议先占靠窗区域，灯光更柔和。',
    tags: ['#自习室', '#图书馆周边', '#夜间学习'],
    likes: 63,
    comments: 18,
    liked: false,
    commented: false,
    adopted: true
  },
  {
    id: 'p-2',
    category: 'canteen',
    authorId: 3,
    author: '@二食堂探店组',
    avatar: '食堂',
    level: 'Lv.3',
    time: '10 分钟前',
    title: '麻辣烫窗口 12:30 以后明显拥挤',
    content: '建议先走北门清汤窗口，平均快 6-8 分钟，口味也更稳定。',
    tags: ['#食堂避雷', '#排队时间', '#午高峰'],
    likes: 41,
    comments: 12,
    liked: false,
    commented: false,
    adopted: false
  },
  {
    id: 'p-3',
    category: 'academic',
    authorId: 4,
    author: '@课表救援队',
    avatar: '教务',
    level: 'Lv.5',
    time: '22 分钟前',
    title: '周三晚自习教室有临时调度',
    content: '系统将在 17:00 前同步并推送提醒，建议提前确认课程地点。',
    tags: ['#教务通知', '#调课提醒', '#课程安排'],
    likes: 82,
    comments: 20,
    liked: false,
    commented: false,
    adopted: true
  },
  {
    id: 'p-4',
    category: 'study',
    authorId: 5,
    author: '@考研作战组',
    avatar: '自习',
    level: 'Lv.2',
    time: '35 分钟前',
    title: 'A2-402 更安静但距离稍远',
    content: '若以长时复习为优先，建议选 A2-402；若重视通勤，优先 A1-307。',
    tags: ['#考研复习', '#教室体验', '#晚间学习'],
    likes: 29,
    comments: 9,
    liked: false,
    commented: false,
    adopted: false
  }
];

function applyLikedStateToLocalFeed() {
  feedPosts.forEach((post) => {
    if (post && post.id && likedPostIds.has(String(post.id))) {
      post.liked = true;
    }
  });
}

const commentMockByPost = {
  'p-1': [
    { id: 'c-1-1', author: '@夜读组', content: 'A1-307 我昨晚 9 点去还有位，体验不错。', time: '3 分钟前', status: 'sent' },
    { id: 'c-1-2', author: '@晚自习观察员', content: '靠窗位置确实更舒服，推荐。', time: '12 分钟前', status: 'sent' }
  ],
  'p-2': [
    { id: 'c-2-1', author: '@食堂地图', content: '补充一下，周五 12:00 以后麻辣烫更慢。', time: '8 分钟前', status: 'sent' },
    {
      id: 'c-2-2',
      author: '@不儿',
      content: '是菜品不太新鲜吗？',
      time: '7 分钟前',
      status: 'sent',
      parentCommentId: 'c-2-1',
      replyToAuthor: '@食堂地图'
    },
    {
      id: 'c-2-3',
      author: '@还是睡吧',
      content: '喜三胖环境还行，口味一般。',
      time: '5 分钟前',
      status: 'sent'
    }
  ],
  'p-3': [
    { id: 'c-3-1', author: '@教务通知员', content: '调课信息已同步到系统，可再次确认。', time: '15 分钟前', status: 'sent' }
  ],
  'p-4': [
    { id: 'c-4-1', author: '@考研互助', content: 'A2-402 晚上 10 点后会更安静。', time: '22 分钟前', status: 'sent' }
  ]
};

const inboxItems = [
  { id: 'likes', title: '收到的赞', subtitle: '有人给你的帖子点赞', defaultCount: 49 },
  { id: 'saved', title: '收藏列表', subtitle: '有人收藏了你的帖子', defaultCount: 12 }
];

const inboxMockDetails = {
  likes: [
    { id: 'l-1', main: '@清晨图书馆人 赞了你：A1-307 晚间自习位反馈', meta: '2 分钟前 · 来自帖子互动', postId: 'p-1', sourceType: 'feed' },
    { id: 'l-2', main: '@二食堂探店组 赞了你：食堂错峰窗口清单', meta: '18 分钟前 · 来自食堂频道', postId: 'p-2', sourceType: 'feed' },
    { id: 'l-3', main: '@课表救援队 赞了你：周三调课提醒合集', meta: '1 小时前 · 来自教务频道', postId: 'p-3', sourceType: 'feed' }
  ],
  saved: [
    { id: 's-1', main: '@考研作战组 收藏了你：A2-402 安静时段建议', meta: '12 分钟前 · 收藏到自习清单', postId: 'p-4', sourceType: 'feed' },
    { id: 's-2', main: '@图书馆夜跑组 收藏了你：图书馆附近插座地图', meta: '43 分钟前 · 收藏到工具箱', postId: 'm-5', sourceType: 'search' }
  ]
};

const eduMockData = {
  overview: {
    studentName: '赵毅',
    studentId: '20222605045',
    totalScore: 167.6,
    gpa: 3.35,
    passedCourses: 46,
    failedCourses: 2,
    retakeCourses: 1,
    term: '2025-2026 秋学期'
  },
  grades: {
    term: '2025-2026秋学期',
    items: [
      { courseName: '中华民族共同体概论', credit: 2, gradePoint: 4.5, score: 90, status: 'passed' },
      { courseName: '形势与政策7', credit: 0.3, gradePoint: 5, score: 97, status: 'passed' },
      { courseName: '实习实训', credit: 4, gradePoint: 3.9, score: 84, status: 'passed' },
      { courseName: '软件测试实验', credit: 1, gradePoint: 3.8, score: 83, status: 'passed' },
      { courseName: '软件测试', credit: 2, gradePoint: 3.5, score: 80, status: 'passed' },
      { courseName: '学科前沿讲座', credit: 2, gradePoint: 3.1, score: 76, status: 'passed' }
    ]
  },
  exams: [
    {
      courseName: '人机交互及可视化技术',
      examType: '第20周周末考试',
      term: '2024-2025学年',
      examDate: '2025-07-09',
      examTime: '10:00-11:30',
      examLocation: '七一路校区A1座407教室',
      examStatus: 'finished'
    },
    {
      courseName: '软件项目管理',
      examType: '第20周周末考试',
      term: '2024-2025学年',
      examDate: '2025-07-08',
      examTime: '10:00-11:30',
      examLocation: '七一路校区A4座606教室',
      examStatus: 'finished'
    }
  ],
  schedule: {
    weekNo: 1,
    items: [
      { weekday: 1, section: 3, sectionSpan: 2, courseName: '软件测试', location: 'A1-307', teacher: '王老师', weeks: '1-16周' },
      { weekday: 3, section: 1, sectionSpan: 2, courseName: '软件项目管理', location: 'A4-606', teacher: '李老师', weeks: '1-16周' }
    ]
  },
  freeClassrooms: {
    campus: '七一路校区',
    items: [
      { building: 'A4', room: '307', idlePercent: 12, campus: '七一路校区', recommended: true },
      { building: 'A4', room: '310', idlePercent: 18, campus: '七一路校区', recommended: true },
      { building: 'A4', room: '410', idlePercent: 32, campus: '七一路校区', recommended: false },
      { building: 'A5', room: '603', idlePercent: 24, campus: '七一路校区', recommended: false }
    ]
  }
};

const defaultState = {
  activeFeedFilter: 'all',
  lastTab: 'home',
  lastSearch: '',
  recentSearches: [],
  searchSort: 'hot',
  inboxRead: {
    likes: false,
    saved: false
  },
  wikiDeepThinking: false,
  wikiHistory: [],
  clientAuth: {
    token: loadClientToken(),
    refreshToken: loadClientRefreshToken(),
    userId: 0,
    username: '',
    displayName: ''
  }
};

const validViews = new Set(['home', 'search', 'messages', 'profile']);
const validSort = new Set(['hot', 'latest']);
const LIVE_STATE_SYNC_MS = 15000;

let inboxCounts = {
  likes: inboxItems.find((item) => item.id === 'likes').defaultCount,
  saved: inboxItems.find((item) => item.id === 'saved').defaultCount
};
let inboxTotals = {
  likes: inboxItems.find((item) => item.id === 'likes').defaultCount,
  saved: inboxItems.find((item) => item.id === 'saved').defaultCount
};
let inboxDetails = {
  likes: [...inboxMockDetails.likes],
  saved: [...inboxMockDetails.saved]
};
let activeDetailTab = 'likes';
let isWikiResponding = false;
let isRefreshingUnread = false;
let unreadPollingTimer = null;
let apiFailureToastAt = 0;
let lastApiIssueMessage = '';
let unreadPollAttempt = 0;
let lastLiveStateSyncAt = 0;
let isRefreshingVisibleState = false;
let isUserIdle = false;
let idleTimer = null;
let activeCommentPostId = '';
let isLoadingComments = false;
let isSendingComment = false;
let activeEduAction = '';
const EDU_ALL_BUILDINGS = '__all__';
const EDU_DEFAULT_CAMPUS = '七一路校区';
const EDU_ACTION_CONFIG = {
  hall: {
    title: '教务大厅',
    brow: '受控教务会话',
    subtitle: '成绩、课表、考试和空教室统一放在一个受控入口里查看，不参与公开知识库检索和推荐。',
    footerNote: '成绩当前使用模拟数据，后续正式教务接口接入后可平滑替换。'
  },
  grades: {
    title: '成绩查询',
    brow: '模拟成绩数据',
    subtitle: '支持按学期切换查看同一位同学的完整成绩记录，只在当前会话内展示。',
    footerNote: '成绩数据不进入公开知识库，也不参与论坛推荐和自进化。'
  },
  schedule: {
    title: '课表查看',
    brow: '周次可切换',
    subtitle: '按周查看本学期 1 到 18 周课表，可自由切换任意周次。',
    footerNote: '课表只在当前登录会话里展示，不会被公开检索。'
  },
  freeClassrooms: {
    title: '空教室',
    brow: '校区与教学楼查看',
    subtitle: '支持按校区切换公共教学楼，再查看该教学楼全部教室的空闲情况。',
    footerNote: '空教室数据仅作为当前会话参考，不写入公开知识库。'
  },
  exams: {
    title: '考试安排',
    brow: '考试提醒',
    subtitle: '统一查看考试时间、地点和考试类型，减少临近考试时翻通知的成本。',
    footerNote: '考试提醒只服务当前登录用户，不对外公开。'
  }
};
let eduSheetState = {
  overview: null,
  activeTerm: '',
  activeWeek: 1,
  activeCampus: EDU_DEFAULT_CAMPUS,
  activeBuilding: EDU_ALL_BUILDINGS,
  freeItems: [],
  buildingOptions: []
};
let selectedCommentImage = null;
let selectedPostImage = null;
let isPublishingPost = false;
let activeReplyTarget = null;
let activeSubpageAction = null;
let currentSubpageListItems = [];
let currentSubpageSourceType = 'feed';
const wikiDetailRegistry = new Map();
let activeWikiDetailId = '';
let activeWikiDetailTrigger = null;

const commentDraftByPost = {};
let commentStore = JSON.parse(JSON.stringify(commentMockByPost));

const USER_IDLE_MS = 60000;
const MAX_IMAGE_BYTES = 1 * 1024 * 1024;

const SEARCH_PAGE_SIZE = 3;
let searchResultState = {
  all: [],
  visibleCount: 0,
  source: 'local',
  page: 1,
  pageSize: 30,
  total: 0,
  hasMore: false,
  loadingMore: false,
  query: '',
  sort: 'hot'
};
const SEARCH_PAGE_VIEW_SIZE = 8;

function normalizeWikiHistory(rawHistory) {
  if (!Array.isArray(rawHistory)) {
    return [];
  }

  return rawHistory
    .map((item) => {
      const role = item && typeof item.role === 'string' ? item.role : '';
      const text = item && typeof item.text === 'string' ? item.text : '';
      const meta = item && item.meta && typeof item.meta === 'object'
        ? {
            route: item.meta.route === 'local' ? 'local' : 'cloud',
            routeLabel: String(item.meta.routeLabel || ''),
            source: String(item.meta.source || ''),
            citations: Array.isArray(item.meta.citations)
              ? item.meta.citations.slice(0, 8).map((citation, index) => ({
                  id: String(citation.id || `src-${index}`),
                  title: String(citation.title || `来源${index + 1}`),
                  jumpUrl: String(citation.jumpUrl || ''),
                  sourceType: String(citation.sourceType || 'kb')
                }))
              : [],
            relatedAnswers: Array.isArray(item.meta.relatedAnswers)
              ? item.meta.relatedAnswers.slice(0, 5).map((answer, index) => ({
                  id: String(answer.id || `rel-${index + 1}`),
                  title: String(answer.title || `相关答案 ${index + 1}`),
                  snippet: String(answer.snippet || ''),
                  sourceType: String(answer.sourceType || 'kb'),
                  jumpUrl: String(answer.jumpUrl || ''),
                  score: Number(answer.score ?? 0)
                }))
              : []
          }
        : null;

      return { role, text, meta };
    })
    .filter((item) => ['user', 'assistant', 'system'].includes(item.role) && item.text.trim())
    .slice(-24);
}

function normalizeRecentSearches(rawSearches) {
  if (!Array.isArray(rawSearches)) {
    return [];
  }

  return rawSearches
    .map((item) => String(item || '').trim())
    .filter((item) => item)
    .slice(0, 6);
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return {
        ...defaultState,
        inboxRead: { ...defaultState.inboxRead },
        recentSearches: [],
        clientAuth: { ...defaultState.clientAuth }
      };
    }

    const parsed = JSON.parse(raw);
    const clientAuth = parsed.clientAuth && typeof parsed.clientAuth === 'object'
      ? {
          token: String(parsed.clientAuth.token || loadClientToken() || ''),
          refreshToken: String(parsed.clientAuth.refreshToken || loadClientRefreshToken() || ''),
          userId: Number(parsed.clientAuth.userId || 0),
          username: String(parsed.clientAuth.username || ''),
          displayName: String(parsed.clientAuth.displayName || '')
        }
      : { ...defaultState.clientAuth };
    return {
      ...defaultState,
      ...parsed,
      recentSearches: normalizeRecentSearches(parsed.recentSearches),
      searchSort: validSort.has(parsed.searchSort) ? parsed.searchSort : 'hot',
      wikiDeepThinking: Boolean(parsed.wikiDeepThinking),
      inboxRead: {
        ...defaultState.inboxRead,
        ...(parsed.inboxRead || {})
      },
      wikiHistory: normalizeWikiHistory(parsed.wikiHistory),
      clientAuth
    };
  } catch (error) {
    return {
      ...defaultState,
      inboxRead: { ...defaultState.inboxRead },
      recentSearches: [],
      wikiHistory: [],
      clientAuth: { ...defaultState.clientAuth }
    };
  }
}

let appState = loadState();
const PREVIEW_NOISE_PATTERN = /^ui-refresh-del-\d+$/i;

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(appState));
  } catch (error) {
    // ignore persistence failure in demo mode
  }
}


function toLowerSafe(text) {
  return (text || '').toLowerCase();
}

function validateImageFile(file) {
  if (!file) {
    return { ok: true, message: '' };
  }
  const mime = String(file.type || '');
  if (!/^image\/(png|jpeg|webp|gif)$/i.test(mime)) {
    return { ok: false, message: '仅支持 png/jpeg/webp/gif 图片' };
  }
  return { ok: true, message: '' };
}

function loadImageElement(file) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('image_load_failed'));
    };
    img.src = url;
  });
}

async function compressImageFile(file, options = {}) {
  const maxBytes = Number(options.maxBytes || MAX_IMAGE_BYTES);
  const maxWidth = Number(options.maxWidth || 1280);
  const maxHeight = Number(options.maxHeight || 1280);
  const originalType = String(file.type || '');
  if (/image\/gif/i.test(originalType)) {
    if (file.size > maxBytes) {
      return { file: null, message: 'GIF 超过 1MB，请换一张图片', wasCompressed: false };
    }
    return { file, message: '', wasCompressed: false };
  }

  let quality = Number(options.quality || 0.82);
  let scale = 1;
  const img = await loadImageElement(file);
  const ratio = Math.min(1, maxWidth / img.width, maxHeight / img.height);
  let targetWidth = Math.max(1, Math.floor(img.width * ratio));
  let targetHeight = Math.max(1, Math.floor(img.height * ratio));

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return { file: null, message: '图片压缩失败，请重试', wasCompressed: false };
  }

  let blob = null;
  while (scale > 0.5) {
    canvas.width = Math.max(1, Math.floor(targetWidth * scale));
    canvas.height = Math.max(1, Math.floor(targetHeight * scale));
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', quality));
    if (!blob) {
      break;
    }
    if (blob.size <= maxBytes) {
      break;
    }
    if (quality > 0.68) {
      quality = Math.max(0.62, quality - 0.08);
    } else {
      scale = scale - 0.12;
    }
  }

  if (!blob) {
    return { file: null, message: '图片压缩失败，请重试', wasCompressed: false };
  }
  if (blob.size > maxBytes) {
    return { file: null, message: '图片压缩后仍超过 1MB，请换一张', wasCompressed: true };
  }
  const baseName = file.name.replace(/\.[^/.]+$/, '') || 'upload';
  const compressedFile = new File([blob], `${baseName}.jpg`, { type: 'image/jpeg' });
  return { file: compressedFile, message: '', wasCompressed: true };
}

function showToast(text) {
  if (!appShell) {
    return;
  }

  const oldToast = appShell.querySelector('.floating-toast');
  if (oldToast) {
    oldToast.remove();
  }

  const toast = document.createElement('div');
  toast.className = 'floating-toast';
  toast.textContent = text;
  appShell.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 1900);
}

function openImageViewer(url, alt = '图片预览') {
  if (!imageViewer || !imageViewerImg) {
    return;
  }
  const safe = String(url || '').trim();
  if (!safe) {
    return;
  }
  imageViewerImg.src = safe;
  imageViewerImg.alt = alt;
  imageViewer.hidden = false;
}

function closeImageViewer() {
  if (!imageViewer || !imageViewerImg) {
    return;
  }
  imageViewer.hidden = true;
  imageViewerImg.src = '';
}

function notifyApiIssue(message) {
  lastApiIssueMessage = String(message || '').trim();
  const now = Date.now();
  if (now - apiFailureToastAt > 8000) {
    showToast(lastApiIssueMessage || message);
    apiFailureToastAt = now;
  }
}

function getClientAuthHeader() {
  const token = appState.clientAuth && appState.clientAuth.token ? String(appState.clientAuth.token) : '';
  if (!token) {
    return {};
  }
  return { Authorization: `Bearer ${token}` };
}

async function loginClient(username, password) {
  const data = await apiRequest(API_CONFIG.endpoints.clientLogin, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    auth: false,
    allowRefresh: false
  });
  if (!data || !data.access_token) {
    return null;
  }
  appState.clientAuth = {
    token: String(data.access_token),
    refreshToken: String(data.refresh_token || ''),
    userId: Number(data.user_id || 0),
    username: String(data.username || ''),
    displayName: String(data.display_name || '')
  };
  saveClientToken(appState.clientAuth.token);
  saveClientRefreshToken(appState.clientAuth.refreshToken);
  saveState();
  syncUserScopedLikes();
  syncHeaderGreeting();
  return appState.clientAuth;
}

async function registerClient(username, password, displayName) {
  const data = await apiRequest(API_CONFIG.endpoints.clientRegister, {
    method: 'POST',
    body: JSON.stringify({
      username,
      password,
      display_name: String(displayName || '').trim() || '网页访客'
    }),
    auth: false,
    allowRefresh: false
  });
  if (!data || !data.access_token) {
    return null;
  }
  appState.clientAuth = {
    token: String(data.access_token),
    refreshToken: String(data.refresh_token || ''),
    userId: Number(data.user_id || 0),
    username: String(data.username || ''),
    displayName: String(data.display_name || '')
  };
  saveClientToken(appState.clientAuth.token);
  saveClientRefreshToken(appState.clientAuth.refreshToken);
  saveState();
  syncUserScopedLikes();
  syncHeaderGreeting();
  return appState.clientAuth;
}

async function refreshClientSession() {
  if (!API_CONFIG.enabled) {
    return null;
  }
  const refreshToken = appState.clientAuth ? String(appState.clientAuth.refreshToken || '') : '';
  if (!refreshToken) {
    return null;
  }
  const data = await apiRequest(API_CONFIG.endpoints.clientRefresh, {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
    auth: false,
    allowRefresh: false,
    silent: true
  });
  if (!data || !data.access_token) {
    return null;
  }
  appState.clientAuth = {
    token: String(data.access_token),
    refreshToken: String(data.refresh_token || refreshToken),
    userId: Number(data.user_id || appState.clientAuth.userId || 0),
    username: String(data.username || appState.clientAuth.username || ''),
    displayName: String(data.display_name || appState.clientAuth.displayName || '')
  };
  saveClientToken(appState.clientAuth.token);
  saveClientRefreshToken(appState.clientAuth.refreshToken);
  saveState();
  syncUserScopedLikes();
  syncHeaderGreeting();
  return appState.clientAuth;
}

function syncUserScopedLikes() {
  const userId = Number(appState.clientAuth && appState.clientAuth.userId ? appState.clientAuth.userId : 0);
  if (!userId) {
    return;
  }
  const postSet = loadLikedSet(userId);
  likedPostIds.clear();
  postSet.forEach((id) => likedPostIds.add(String(id)));
  const commentSet = loadCommentLikedSet(userId);
  likedCommentIds.clear();
  commentSet.forEach((id) => likedCommentIds.add(String(id)));
}

async function logoutClient(options = {}) {
  const remote = options.remote !== false;
  if (!API_CONFIG.enabled) {
    appState.clientAuth = { ...defaultState.clientAuth };
    saveClientToken('');
    saveClientRefreshToken('');
    saveState();
    return;
  }
  try {
    if (remote) {
      await apiRequest(API_CONFIG.endpoints.clientLogout, {
        method: 'POST',
        body: JSON.stringify({ refresh_token: String(appState.clientAuth.refreshToken || '') }),
        allowRefresh: false,
        retries: 0,
        silent: true
      });
    }
  } catch (error) {
    // ignore
  }
  appState.clientAuth = { ...defaultState.clientAuth };
  saveClientToken('');
  saveClientRefreshToken('');
  likedPostIds.clear();
  likedCommentIds.clear();
  saveState();
  syncHeaderGreeting('');
}

async function ensureClientSession() {
  if (!API_CONFIG.enabled) {
    return null;
  }

  if (appState.clientAuth && appState.clientAuth.token) {
    const me = await apiRequest(API_CONFIG.endpoints.clientMe, { method: 'GET' });
    if (me && typeof me === 'object') {
      appState.clientAuth = {
        token: appState.clientAuth.token,
        refreshToken: appState.clientAuth.refreshToken,
        userId: Number(me.user_id || appState.clientAuth.userId || 0),
        username: String(me.username || appState.clientAuth.username || ''),
        displayName: String(me.display_name || appState.clientAuth.displayName || '')
      };
      saveState();
      syncUserScopedLikes();
      syncHeaderGreeting();
      return appState.clientAuth;
    }
    const refreshed = await refreshClientSession();
    if (refreshed) {
      return refreshed;
    }
  }

  for (let attempt = 0; attempt < 2; attempt += 1) {
    let creds = loadBootstrapCredentials();
    const hasStoredCreds = Boolean(creds.username && creds.password);
    if (!hasStoredCreds) {
      const fresh = buildBootstrapCredentials();
      saveBootstrapCredentials(fresh.username, fresh.password);
      try {
        const registered = await registerClient(fresh.username, fresh.password, fresh.displayName);
        if (registered) {
          return registered;
        }
      } catch (error) {
        const detail = String(error && error.message || '').trim();
        if (!detail.includes('username_already_exists')) {
          throw error;
        }
        clearBootstrapCredentials();
        continue;
      }
      continue;
    }

    try {
      const loggedIn = await loginClient(creds.username, creds.password);
      if (loggedIn) {
        return loggedIn;
      }
    } catch (error) {
      const detail = String(error && error.message || '').trim();
      const knownCredentialIssue = detail.includes('invalid_client_credentials') || detail.includes('client_not_found');
      if (!knownCredentialIssue) {
        throw error;
      }
      clearBootstrapCredentials();
    }
  }

  return null;
}

async function bindWechat() {
  const code = `demo-${Date.now()}`;
  if (!appState.clientAuth || !appState.clientAuth.token) {
    await ensureClientSession();
  }
  const resp = await apiRequest(API_CONFIG.endpoints.clientWechatBind, {
    method: 'POST',
    body: JSON.stringify({ code })
  });
  if (resp && resp.ok) {
    showToast('微信绑定成功');
    const remoteProfile = await apiAdapter.fetchProfileSummary();
    if (remoteProfile) {
      applyProfileSummary(remoteProfile);
    }
    return true;
  }
  showToast('微信绑定失败，请稍后重试');
  return false;
}

async function bindWechatByCode(code) {
  const safeCode = String(code || '').trim();
  if (!safeCode) {
    showToast('请输入微信登录 code');
    return false;
  }
  if (!appState.clientAuth || !appState.clientAuth.token) {
    await ensureClientSession();
  }
  const resp = await apiRequest(API_CONFIG.endpoints.clientWechatBind, {
    method: 'POST',
    body: JSON.stringify({ code: safeCode })
  });
  if (resp && resp.ok) {
    showToast('微信绑定成功');
    const remoteProfile = await apiAdapter.fetchProfileSummary();
    if (remoteProfile) {
      applyProfileSummary(remoteProfile);
    }
    return true;
  }
  showToast('微信绑定失败，请检查 AppID/Secret 与 code');
  return false;
}

async function loginWithWechatCode(code, displayName = '') {
  const safeCode = String(code || '').trim();
  if (!safeCode) {
    showToast('请输入微信登录 code');
    return false;
  }

  const data = await apiRequest(API_CONFIG.endpoints.clientWechatLogin, {
    method: 'POST',
    auth: false,
    allowRefresh: false,
    retries: 0,
    body: JSON.stringify({
      code: safeCode,
      display_name: String(displayName || '').trim() || null
    })
  });
  if (!data || !data.access_token) {
    showToast('微信登录失败，请检查 code 是否有效');
    return false;
  }

  appState.clientAuth = {
    token: String(data.access_token),
    refreshToken: String(data.refresh_token || ''),
    userId: Number(data.user_id || 0),
    username: String(data.username || ''),
    displayName: String(data.display_name || '')
  };
  saveClientToken(appState.clientAuth.token);
  saveClientRefreshToken(appState.clientAuth.refreshToken);
  saveState();
  syncUserScopedLikes();
  syncHeaderGreeting();
  showToast('微信登录成功');
  const remoteProfile = await apiAdapter.fetchProfileSummary();
  if (remoteProfile) {
    applyProfileSummary(remoteProfile);
  }
  return true;
}

function openWechatAuthPage() {
  openSubpageSheet({
    title: '账号互通',
    subtitle: '小程序与网页端共用同一账号',
    body: `
      <div class="wechat-auth-panel">
        <div class="wechat-auth-hero">
          <strong>微信互通登录</strong>
          <p>网页端会接入你在小程序里的同一个账号，帖子、收藏、消息和知识对话记录都会保持联通。</p>
        </div>
        <div class="wechat-auth-steps">
          <div class="wechat-auth-step"><span>1</span><p>打开小程序“我的”页，进入“网页互通登录”。</p></div>
          <div class="wechat-auth-step"><span>2</span><p>复制小程序生成的一次性登录码。</p></div>
          <div class="wechat-auth-step"><span>3</span><p>把登录码粘贴到这里，完成网页端登录。</p></div>
        </div>
        <input id="webLoginCodeInput" type="text" maxlength="12" placeholder="请输入小程序生成的登录码" />
        <div class="wechat-auth-benefits">
          <span class="wechat-auth-benefit">同账号</span>
          <span class="wechat-auth-benefit">同收藏</span>
          <span class="wechat-auth-benefit">同消息</span>
          <span class="wechat-auth-benefit">同知识记录</span>
        </div>
      </div>
    `,
    actionLabel: '登录网页',
    action: () => {
      const input = subpageBody ? subpageBody.querySelector('#webLoginCodeInput') : null;
      const code = String(input ? input.value : '').trim();
      if (!code) {
        showToast('请先输入登录码');
        return false;
      }
      void (async () => {
        const data = await apiAdapter.exchangeWebLoginCode(code);
        if (!data || !appState.clientAuth || !appState.clientAuth.token) {
          showToast('登录码无效或已过期');
          return;
        }
        closeSubpageSheet();
        await hydrateRemoteState();
        showToast('网页账号已与小程序互通');
      })();
      return false;
    }
  });
  return;

  openSubpageSheet({
    title: '微信登录与绑定',
    subtitle: '小程序可直接接入',
    body: `
      <div class="wechat-auth-panel">
        <p>小程序端：先调用 <code>wx.login</code> 拿到 code，再调用后端微信登录接口。</p>
        <input id="wechatCodeInput" type="text" placeholder="粘贴 wx.login 返回的 code" />
        <input id="wechatDisplayNameInput" type="text" placeholder="可选：首次登录昵称" />
        <div class="wechat-auth-actions">
          <button id="wechatLoginBtn" class="btn-dark" type="button">微信登录</button>
          <button id="wechatBindBtn" class="btn-light" type="button">绑定当前账号</button>
        </div>
        <p class="scope-tip">本地网页调试可用临时 code（如 demo-时间戳）；正式上线请在后台配置微信 AppID/AppSecret。</p>
      </div>
    `,
    actionLabel: '',
    action: null
  });

  const codeInput = subpageBody ? subpageBody.querySelector('#wechatCodeInput') : null;
  const nameInput = subpageBody ? subpageBody.querySelector('#wechatDisplayNameInput') : null;
  const loginBtn = subpageBody ? subpageBody.querySelector('#wechatLoginBtn') : null;
  const bindBtn = subpageBody ? subpageBody.querySelector('#wechatBindBtn') : null;

  if (loginBtn && codeInput) {
    loginBtn.addEventListener('click', () => {
      void (async () => {
        const ok = await loginWithWechatCode(codeInput.value, nameInput ? nameInput.value : '');
        if (ok) {
          closeSubpageSheet();
          await hydrateRemoteState();
        }
      })();
    });
  }
  if (bindBtn && codeInput) {
    bindBtn.addEventListener('click', () => {
      void bindWechatByCode(codeInput.value);
    });
  }
}

function setNetworkHint(mode = 'local') {
  if (!inboxNetworkHint) {
    return;
  }

  inboxNetworkHint.classList.remove('is-online', 'is-offline', 'is-local');

  if (mode === 'online') {
    inboxNetworkHint.classList.add('is-online');
    inboxNetworkHint.textContent = '在线';
    return;
  }

  if (mode === 'offline') {
    inboxNetworkHint.classList.add('is-offline');
    inboxNetworkHint.textContent = '离线模式';
    return;
  }

  inboxNetworkHint.classList.add('is-local');
  inboxNetworkHint.textContent = API_CONFIG.enabled ? '服务异常，请稍后重试' : '离线模式';
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildApiUrl(path) {
  const base = String(API_CONFIG.baseUrl || '').trim();
  if (!base) {
    return path;
  }
  return `${base.replace(/\/$/, '')}${path}`;
}

function normalizeMediaUrl(url) {
  const safe = String(url || '').trim();
  if (!safe) {
    return '';
  }
  if (safe.startsWith('/')) {
    return buildApiUrl(safe);
  }
  return safe;
}

async function apiRequest(path, options = {}) {
  if (!API_CONFIG.enabled) {
    return null;
  }
  const silent = Boolean(options.silent);
  const useAuth = options.auth !== false;
  const allowRefresh = options.allowRefresh !== false;

  if (useAuth && (!appState.clientAuth || !appState.clientAuth.token)) {
    await ensureClientSession();
  }

  if (!navigator.onLine) {
    if (!silent) {
      setNetworkHint('offline');
      notifyApiIssue('当前离线，已切换为缓存内容');
    }
    return null;
  }

  const retries = Number(options.retries ?? 2);
  const retryDelayMs = Number(options.retryDelayMs ?? 450);
  let attempt = 0;

  while (attempt <= retries) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), API_CONFIG.timeoutMs);

    try {
      const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
      const authHeader = useAuth ? getClientAuthHeader() : {};
      const response = await fetch(buildApiUrl(path), {
        ...options,
        signal: controller.signal,
        headers: isFormData
          ? { ...authHeader, ...(options.headers || {}) }
          : {
              'Content-Type': 'application/json',
              ...authHeader,
              ...(options.headers || {})
            }
      });

      if (!response.ok) {
        if (response.status === 401 && useAuth && allowRefresh) {
          const refreshed = await refreshClientSession();
          if (refreshed) {
            attempt += 1;
            continue;
          }
        }
        if (silent) {
          return null;
        }
        if (response.status === 429) {
          let detail = '';
          try {
            const payload = await response.json();
            detail = String(payload && payload.detail ? payload.detail : '');
          } catch (error) {
            detail = '';
          }
          if (detail.includes('post_rate_limit_30m_3')) {
            notifyApiIssue('操作过于频繁：30分钟最多发布3条帖子');
          } else {
            notifyApiIssue('操作过于频繁，请稍后再试');
          }
          return null;
        }

        if (response.status === 422) {
          let detail = '';
          try {
            const payload = await response.json();
            detail = String(payload && payload.detail ? payload.detail : '');
          } catch (error) {
            detail = '';
          }
          if (detail.includes('image_too_large')) {
            notifyApiIssue('图片超过 1MB，请压缩后再上传');
          } else if (detail.includes('image_format_not_supported') || detail.includes('image_mime_not_supported')) {
            notifyApiIssue('图片格式不支持，仅允许 png/jpeg/webp/gif');
          } else {
            notifyApiIssue('提交参数不合法，请检查输入');
          }
          return null;
        }

        if (response.status === 404) {
          let detail = '';
          try {
            const payload = await response.json();
            detail = String(payload && payload.detail ? payload.detail : '');
          } catch (error) {
            detail = '';
          }
          if (detail.includes('post_not_found')) {
            notifyApiIssue('原帖不存在或已被清理，无法评论');
          } else if (detail.includes('comment_not_found')) {
            notifyApiIssue('评论不存在或已被删除');
          } else {
            notifyApiIssue('接口不存在（404），请重启后端并确认版本已更新');
          }
          return null;
        }

        if (response.status === 401) {
          notifyApiIssue('登录已失效，请重新登录');
          await logoutClient({ remote: false });
          setNetworkHint('local');
          return null;
        }

        if (response.status === 400) {
          let detail = '';
          try {
            const payload = await response.json();
            detail = String(payload && payload.detail ? payload.detail : '');
          } catch (error) {
            detail = '';
          }
          if (detail.includes('invalid_reply_target')) {
            notifyApiIssue('回复目标无效，请刷新评论后重试');
          } else {
            notifyApiIssue(detail ? `请求失败：${detail}` : '请求失败（400）');
          }
          return null;
        }

        if (response.status === 403) {
          setNetworkHint('local');
          notifyApiIssue('操作无权限或鉴权失败');
          return null;
        }

        if (attempt < retries && response.status >= 500) {
          await new Promise((resolve) => setTimeout(resolve, retryDelayMs * (attempt + 1)));
          attempt += 1;
          continue;
        }

        if (response.status >= 500) {
          notifyApiIssue('服务端异常（5xx），已切换为缓存内容');
        } else {
          notifyApiIssue(`接口异常（${response.status}），已切换为缓存内容`);
        }
        setNetworkHint('local');
        return null;
      }

      if (!silent) {
        setNetworkHint('online');
      }
      lastApiIssueMessage = '';
      return await response.json();
    } catch (error) {
      const isTimeout = error && error.name === 'AbortError';
      if (silent) {
        return null;
      }
      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, retryDelayMs * (attempt + 1)));
        attempt += 1;
        continue;
      }

      setNetworkHint(navigator.onLine ? 'local' : 'offline');
      notifyApiIssue(isTimeout ? '接口请求超时，已切换为缓存内容' : '后端连接失败，已切换为缓存内容');
      return null;
    } finally {
      clearTimeout(timer);
    }
  }

  return null;
}

const apiAdapter = {
  mapFeedItem(item, index = 0) {
    const id = String(item.id || `feed-${index}`);
    const liked = API_CONFIG.enabled
      ? Boolean(item.liked)
      : (Boolean(item.liked) || likedPostIds.has(id));
    const commentsPreview = Array.isArray(item.comments_preview)
      ? item.comments_preview.map((line) => sanitizePreviewLine(line)).filter((line) => line)
      : [];
    return {
      id,
      category: String(item.category || 'all'),
      authorId: Number(item.author_id || item.authorId || 0),
      author: String(item.author || '@匿名用户'),
      avatar: String(item.avatar || '社区'),
      level: String(item.level || 'Lv.1'),
      time: String(item.time || '刚刚'),
      title: String(item.title || ''),
      content: String(item.content || ''),
      tags: Array.isArray(item.tags) ? item.tags.map((tag) => String(tag)) : [],
      likes: Number(item.likes || 0),
      comments: Number(item.comments || 0),
      liked,
      commented: Boolean(item.commented),
      adopted: Boolean(item.adopted),
      knowledgeReady: Boolean(item.knowledge_ready || item.knowledgeReady),
      knowledgeReviewDecision: String(item.knowledge_review_decision || item.knowledgeReviewDecision || '').toLowerCase(),
      knowledgeReviewReason: String(item.knowledge_review_reason || item.knowledgeReviewReason || ''),
      imageUrl: normalizeMediaUrl(item.image_url || item.imageUrl || ''),
      commentsPreview
    };
  },
  mapErrandItem(item, index = 0) {
    return {
      id: String(item.id || `e-${index}`),
      title: String(item.title || '跑腿任务'),
      reward: String(item.reward || '￥0'),
      time: String(item.time || '尽快'),
      pickupLocation: String(item.pickup_location || item.pickupLocation || ''),
      destination: String(item.destination || ''),
      locationSummary: String(item.location_summary || item.locationSummary || '').trim(),
      note: String(item.note || ''),
      tag: String(item.tag || '跑腿任务'),
      taskType: String(item.task_type || item.taskType || 'quick'),
      publisherId: Number(item.publisher_id || item.publisherId || 0),
      publisherName: String(item.publisher_name || item.publisherName || '匿名同学'),
      publisherContact: String(item.publisher_contact || item.publisherContact || '接单后可见'),
      runnerId: Number(item.runner_id || item.runnerId || 0),
      runnerName: String(item.runner_name || item.runnerName || ''),
      runnerContact: String(item.runner_contact || item.runnerContact || ''),
      status: String(item.status || 'open'),
      statusLabel: String(item.status_label || item.statusLabel || '待接单'),
      statusTone: String(item.status_tone || item.statusTone || 'blue'),
      relativeText: String(item.relative_text || item.relativeText || '刚刚'),
      createdAt: String(item.created_at || item.createdAt || ''),
      acceptedAt: String(item.accepted_at || item.acceptedAt || ''),
      deliveredAt: String(item.delivered_at || item.deliveredAt || ''),
      confirmedAt: String(item.confirmed_at || item.confirmedAt || ''),
      canDelete: Boolean(item.can_delete || item.canDelete),
      primaryAction: item && item.primary_action ? {
        key: String(item.primary_action.key || 'detail'),
        label: String(item.primary_action.label || '查看详情'),
        tone: String(item.primary_action.tone || 'ghost')
      } : {
        key: 'detail',
        label: '查看详情',
        tone: 'ghost'
      },
      timeline: Array.isArray(item.timeline)
        ? item.timeline.map((row) => ({
            key: String(row.key || ''),
            label: String(row.label || ''),
            value: String(row.value || '')
          }))
        : [],
      source_type: 'errand'
    };
  },
  async fetchFeedList(filter = 'all') {
    const query = new URLSearchParams({ filter: String(filter || 'all') }).toString();
    const data = await apiRequest(`${API_CONFIG.endpoints.feedList}?${query}`, { method: 'GET' });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }

    return data.items.map((item, index) => apiAdapter.mapFeedItem(item, index))
      .filter((item) => item.id && item.title);
  },

  async fetchFeedPost(postId) {
    const params = new URLSearchParams({ post_id: String(postId || '') });
    const data = await apiRequest(`${API_CONFIG.endpoints.feedPostDetail}?${params.toString()}`, { method: 'GET' });
    if (!data || typeof data !== 'object' || !data.id) {
      return null;
    }
    return apiAdapter.mapFeedItem(data, 0);
  },

  async fetchHomeHotTopics() {
    const data = await apiRequest(API_CONFIG.endpoints.homeHotTopics, { method: 'GET' });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }

    return data.items.map((item, index) => ({
      id: String(item.id || `hot-${index}`),
      title: String(item.title || ''),
      heat: String(item.heat || '')
    })).filter((item) => item.title);
  },

  async toggleFeedLike(postId, liked) {
    const data = await apiRequest(API_CONFIG.endpoints.feedLike, {
      method: 'POST',
      body: JSON.stringify({ post_id: postId, liked: Boolean(liked) })
    });
    if (!data || typeof data !== 'object') {
      return null;
    }

    return {
      liked: Boolean(data.liked),
      likes: Number(data.likes || 0)
    };
  },

  async fetchPostComments(postId, options = {}) {
    const params = new URLSearchParams({
      post_id: String(postId || ''),
      page: String(Number(options.page || 1)),
      page_size: String(Number(options.pageSize || 20))
    });

    const data = await apiRequest(`${API_CONFIG.endpoints.feedComments}?${params.toString()}`, { method: 'GET' });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }

    const items = data.items.map((item, index) => ({
      id: String(item.id || `cm-${index}`),
      authorId: Number(item.author_id || item.authorId || 0),
      author: String(item.author || item.nickname || '@匿名用户'),
      content: String(item.content || ''),
      time: String(item.time || item.created_at || '刚刚'),
      imageUrl: normalizeMediaUrl(item.image_url || item.imageUrl || ''),
      likes: Number(item.likes || 0),
      parentCommentId: String(item.parent_comment_id || item.parentCommentId || ''),
      replyToAuthor: String(item.reply_to_author || item.replyToAuthor || ''),
      canDelete: Boolean(item.can_delete || item.canDelete),
      status: 'sent'
    })).filter((item) => item.content || item.imageUrl);

    return {
      page: Number(data.page || options.page || 1),
      pageSize: Number(data.page_size || options.pageSize || 20),
      total: Number(data.total || items.length),
      hasMore: Boolean(data.has_more),
      items
    };
  },

  async createPostComment(postId, content, clientId = '', imageFile = null, replyTarget = null) {
    if (!API_CONFIG.enabled) {
    return {
      id: String(clientId || `cm-${Date.now()}`),
      authorId: Number(appState.clientAuth.userId || 0),
      author: '@我',
      content: String(content || ''),
      time: '刚刚',
      imageUrl: imageFile ? URL.createObjectURL(imageFile) : '',
      likes: 0,
      parentCommentId: replyTarget && replyTarget.id ? String(replyTarget.id) : '',
      replyToAuthor: replyTarget && replyTarget.author ? String(replyTarget.author) : '',
      canDelete: true,
      localImageFile: null,
      errorMsg: '',
      status: 'sent'
    };
    }

    let data = null;
    if (imageFile) {
      const form = new FormData();
      form.append('post_id', String(postId || ''));
      form.append('content', String(content || ''));
      form.append('client_id', String(clientId || ''));
      if (replyTarget && replyTarget.id) {
        form.append('reply_to_comment_id', String(replyTarget.id));
      }
      if (replyTarget && replyTarget.author) {
        form.append('reply_to_author', String(replyTarget.author));
      }
      form.append('image', imageFile);
      data = await apiRequest(API_CONFIG.endpoints.feedCommentCreateWithImage, {
        method: 'POST',
        body: form,
        retries: 0
      });
    } else {
      data = await apiRequest(API_CONFIG.endpoints.feedCommentCreate, {
        method: 'POST',
        body: JSON.stringify({
          post_id: postId,
          content,
          client_id: String(clientId || ''),
          reply_to_comment_id: replyTarget && replyTarget.id ? String(replyTarget.id) : null,
          reply_to_author: replyTarget && replyTarget.author ? String(replyTarget.author) : null
        }),
        retries: 0
      });
    }

    if (!data || typeof data !== 'object') {
      return null;
    }

    return {
      id: String(data.id || clientId || `cm-${Date.now()}`),
      authorId: Number(data.author_id || data.authorId || appState.clientAuth.userId || 0),
      author: String(data.author || '@我'),
      content: String(data.content || content),
      time: String(data.time || data.created_at || '刚刚'),
      imageUrl: normalizeMediaUrl(data.image_url || data.imageUrl || ''),
      likes: Number(data.likes || 0),
      parentCommentId: String(data.parent_comment_id || data.parentCommentId || ''),
      replyToAuthor: String(data.reply_to_author || data.replyToAuthor || ''),
      canDelete: Boolean(data.can_delete || data.canDelete || true),
      localImageFile: null,
      errorMsg: '',
      status: 'sent'
    };
  },

  async toggleCommentLike(commentId, liked) {
    const data = await apiRequest(API_CONFIG.endpoints.feedCommentLike, {
      method: 'POST',
      body: JSON.stringify({ comment_id: String(commentId || ''), liked: Boolean(liked) })
    });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return {
      commentId: String(data.comment_id || commentId || ''),
      liked: Boolean(data.liked),
      likes: Number(data.likes || 0)
    };
  },

  async deleteComment(postId, commentId) {
    const data = await apiRequest(API_CONFIG.endpoints.feedCommentDelete, {
      method: 'POST',
      body: JSON.stringify({ post_id: String(postId || ''), comment_id: String(commentId || '') })
    });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return {
      postId: String(data.post_id || postId || ''),
      commentId: String(data.comment_id || commentId || ''),
      deleted: Boolean(data.deleted),
      deletedCount: Number(data.deleted_count || data.deletedCount || 1),
      deletedIds: Array.isArray(data.deleted_ids)
        ? data.deleted_ids.map((id) => String(id))
        : (Array.isArray(data.deletedIds) ? data.deletedIds.map((id) => String(id)) : [])
    };
  },

  async createPost(category, title, content, tags = [], imageFile = null) {
    if (!API_CONFIG.enabled) {
      return null;
    }

    let data = null;
    if (imageFile) {
      const form = new FormData();
      form.append('category', String(category || 'study'));
      form.append('title', String(title || ''));
      form.append('content', String(content || ''));
      form.append('tags', JSON.stringify(Array.isArray(tags) ? tags : []));
      form.append('image', imageFile);
      data = await apiRequest(API_CONFIG.endpoints.feedPostCreateWithImage, {
        method: 'POST',
        body: form,
        retries: 0
      });
    } else {
      data = await apiRequest(API_CONFIG.endpoints.feedPostCreate, {
        method: 'POST',
        body: JSON.stringify({
          category: String(category || 'study'),
          title: String(title || ''),
          content: String(content || ''),
          tags: Array.isArray(tags) ? tags : []
        }),
        retries: 0
      });
    }

    if (!data || typeof data !== 'object' || !data.id) {
      return null;
    }

    return {
      id: String(data.id),
      category: String(data.category || 'all'),
      authorId: Number(data.author_id || data.authorId || appState.clientAuth.userId || 0),
      author: String(data.author || '@我'),
      avatar: String(data.avatar || '我'),
      level: String(data.level || 'Lv.1'),
      time: String(data.time || '刚刚'),
      title: String(data.title || ''),
      content: String(data.content || ''),
      tags: Array.isArray(data.tags) ? data.tags.map((tag) => String(tag)) : [],
      likes: Number(data.likes || 0),
      comments: Number(data.comments || 0),
      liked: Boolean(data.liked),
      commented: Boolean(data.commented),
      adopted: Boolean(data.adopted),
      imageUrl: normalizeMediaUrl(data.image_url || data.imageUrl || ''),
      commentsPreview: Array.isArray(data.comments_preview)
        ? data.comments_preview.map((line) => String(line || '')).filter((line) => line)
        : []
    };
  },

  async searchPosts(keyword, sortBy, options = {}) {
    const params = new URLSearchParams({
      q: String(keyword || ''),
      sort: String(sortBy || 'hot'),
      page: String(Number(options.page || 1)),
      page_size: String(Number(options.pageSize || 30))
    });

    const data = await apiRequest(`${API_CONFIG.endpoints.searchPosts}?${params.toString()}`, { method: 'GET' });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }

    const items = data.items.map((item, index) => {
      const id = String(item.id || `m-${index}`);
      const match = id.match(/^m-(\d+)$/i);
      return {
      id,
      postId: String(item.post_id || item.postId || (match ? `p-${match[1]}` : '')),
      title: String(item.title || ''),
      snippet: String(item.snippet || item.content || ''),
      likes: Number(item.likes || 0),
      comments: Number(item.comments || 0),
      meta: String(item.meta || item.category || '论坛帖子'),
      updatedAt: String(item.updated_at || item.updatedAt || ''),
      hotScore: Number(item.hot_score ?? item.hotScore ?? 0),
      keywords: Array.isArray(item.keywords) ? item.keywords.map((tag) => String(tag)) : []
    };
    }).filter((item) => item.id && item.title);

    return {
      page: Number(data.page || options.page || 1),
      pageSize: Number(data.page_size || options.pageSize || 30),
      total: Number(data.total || items.length),
      hasMore: Boolean(data.has_more),
      items
    };
  },

  async askKnowledge(query, history = [], options = {}) {
    const data = await apiRequest(API_CONFIG.endpoints.knowledgeAsk, {
      method: 'POST',
      body: JSON.stringify({
        query: String(query || ''),
        history: Array.isArray(history) ? history : [],
        deep_thinking: Boolean(options.deepThinking)
      })
    });

    if (!data || typeof data !== 'object' || !data.answer) {
      return null;
    }

    return {
      route: data.route === 'local' ? 'local' : 'cloud',
      routeLabel: String(data.route_label || data.routeLabel || '校园知识库'),
      source: String(data.source || '来源：校园知识库'),
      text: String(data.answer),
      rerankUsed: Boolean(data.rerank_used),
      citations: Array.isArray(data.citations)
        ? data.citations.map((item, index) => ({
            id: String(item.id || `src-${index}`),
            title: String(item.title || item.id || `来源${index + 1}`),
            jumpUrl: String(item.jump_url || item.jumpUrl || ''),
            sourceType: String(item.source_type || item.sourceType || 'kb')
          }))
        : [],
      relatedAnswers: Array.isArray(data.related_answers)
        ? data.related_answers.map((item, index) => ({
            id: String(item.id || `rel-${index + 1}`),
            title: String(item.title || `相关答案 ${index + 1}`),
            snippet: String(item.snippet || ''),
            sourceType: String(item.source_type || item.sourceType || 'kb'),
            jumpUrl: String(item.jump_url || item.jumpUrl || ''),
            score: Number(item.score ?? 0)
          }))
        : []
    };
  },

  async fetchEduOverview() {
    const data = await apiRequest(API_CONFIG.endpoints.eduOverview, {
      method: 'GET',
      headers: {
        'X-Edu-Session': API_CONFIG.eduSessionToken
      }
    });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return {
      studentName: String(data.student_name || ''),
      studentId: String(data.student_id || ''),
      totalScore: Number(data.total_score || 0),
      gpa: Number(data.gpa || 0),
      passedCourses: Number(data.passed_courses || 0),
      failedCourses: Number(data.failed_courses || 0),
      retakeCourses: Number(data.retake_courses || 0),
      term: String(data.term || ''),
      availableTerms: Array.isArray(data.available_terms) ? data.available_terms.map((item) => String(item || '')) : [],
      currentWeek: Number(data.current_week || 1),
      totalWeeks: Number(data.total_weeks || 18),
      campuses: Array.isArray(data.campuses) ? data.campuses.map((item) => String(item || '')) : []
    };
  },

  async fetchEduGrades(term = '') {
    const params = new URLSearchParams();
    if (term) {
      params.set('term', String(term));
    }
    const data = await apiRequest(`${API_CONFIG.endpoints.eduGrades}?${params.toString()}`, {
      method: 'GET',
      headers: {
        'X-Edu-Session': API_CONFIG.eduSessionToken
      }
    });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return {
      term: String(data.term || ''),
      terms: Array.isArray(data.terms) ? data.terms.map((item) => String(item || '')) : [],
      termCredit: Number(data.term_credit || 0),
      termGpa: Number(data.term_gpa || 0),
      passedCount: Number(data.passed_count || 0),
      pendingCount: Number(data.pending_count || 0),
      items: data.items.map((item) => ({
        courseName: String(item.course_name || ''),
        credit: Number(item.credit || 0),
        gradePoint: Number(item.grade_point || 0),
        score: Number(item.score || 0),
        status: String(item.status || 'unknown')
      }))
    };
  },

  async fetchEduExams() {
    const data = await apiRequest(API_CONFIG.endpoints.eduExams, {
      method: 'GET',
      headers: {
        'X-Edu-Session': API_CONFIG.eduSessionToken
      }
    });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return data.items.map((item) => ({
      courseName: String(item.course_name || ''),
      examType: String(item.exam_type || ''),
      term: String(item.term || ''),
      examDate: String(item.exam_date || ''),
      examTime: String(item.exam_time || ''),
      examLocation: String(item.exam_location || ''),
      examStatus: String(item.exam_status || '')
    }));
  },

  async fetchEduSchedule(weekNo = 1) {
    const data = await apiRequest(`${API_CONFIG.endpoints.eduSchedule}?week_no=${Number(weekNo || 1)}`, {
      method: 'GET',
      headers: {
        'X-Edu-Session': API_CONFIG.eduSessionToken
      }
    });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return {
      term: String(data.term || ''),
      weekNo: Number(data.week_no || weekNo || 1),
      weeks: Array.isArray(data.weeks) ? data.weeks.map((item) => Number(item || 0)).filter(Boolean) : [],
      items: data.items.map((item) => ({
        weekday: Number(item.weekday || 1),
        section: Number(item.section || 1),
        sectionSpan: Number(item.section_span || 1),
        courseName: String(item.course_name || ''),
        location: String(item.location || ''),
        teacher: String(item.teacher || ''),
        weeks: String(item.weeks || '')
      }))
    };
  },

  async fetchEduFreeClassrooms(campus = EDU_DEFAULT_CAMPUS, building = '') {
    const params = new URLSearchParams({ campus: String(campus || EDU_DEFAULT_CAMPUS) });
    if (building) {
      params.set('building', String(building));
    }
    const data = await apiRequest(`${API_CONFIG.endpoints.eduFreeClassrooms}?${params.toString()}`, {
      method: 'GET',
      headers: {
        'X-Edu-Session': API_CONFIG.eduSessionToken
      }
    });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return {
      campus: String(data.campus || campus),
      campuses: Array.isArray(data.campuses) ? data.campuses.map((item) => String(item || '')) : [],
      building: String(data.building || ''),
      buildings: Array.isArray(data.buildings) ? data.buildings.map((item) => String(item || '')) : [],
      items: data.items.map((item) => ({
        building: String(item.building || ''),
        room: String(item.room || ''),
        idlePercent: Number(item.idle_percent || 0),
        campus: String(item.campus || campus),
        recommended: Boolean(item.recommended)
      }))
    };
  },

  async fetchProfileSummary() {
    const data = await apiRequest(API_CONFIG.endpoints.profileSummary, { method: 'GET' });
    if (!data || typeof data !== 'object') {
      return null;
    }

    return {
      name: String(data.name || ''),
      meta: String(data.meta || ''),
      bindState: String(data.bind_state || data.bindState || ''),
      wechatBound: Boolean(data.wechat_bound ?? data.wechatBound ?? false),
      posts: Number(data.posts || 0),
      likes: Number(data.likes || 0)
    };
  },

  async fetchProfileSettings() {
    const data = await apiRequest(API_CONFIG.endpoints.profileSettings, { method: 'GET', silent: true });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return {
      displayName: String(data.display_name || data.displayName || ''),
      publicName: String(data.public_name || data.publicName || ''),
      bindState: String(data.bind_state || data.bindState || ''),
      wechatBound: Boolean(data.wechat_bound ?? data.wechatBound ?? false)
    };
  },

  async updatePublicName(publicName) {
    const data = await apiRequest(API_CONFIG.endpoints.profilePublicName, {
      method: 'POST',
      body: JSON.stringify({ public_name: String(publicName || '').trim() }),
      retries: 0
    });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return {
      publicName: String(data.public_name || data.publicName || '')
    };
  },

  async fetchMyPosts() {
    const data = await apiRequest(API_CONFIG.endpoints.profileMyPosts, { method: 'GET', silent: true });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return data.items.map((item, index) => apiAdapter.mapFeedItem(item, index))
      .filter((item) => item.id && item.title);
  },

  async fetchLikedPosts() {
    const data = await apiRequest(API_CONFIG.endpoints.profileLikedPosts, { method: 'GET', silent: true });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return data.items.map((item, index) => apiAdapter.mapFeedItem(item, index))
      .filter((item) => item.id && item.title);
  },

  async fetchErrands(scope = 'all') {
    const endpoint = scope === 'my'
      ? API_CONFIG.endpoints.errandMyList
      : API_CONFIG.endpoints.errandList;
    const data = await apiRequest(endpoint, { method: 'GET', silent: true });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }
    return data.items.map((item, index) => apiAdapter.mapErrandItem(item, index))
      .filter((item) => item.id && item.title);
  },

  async createErrand(payload = {}) {
    const data = await apiRequest(API_CONFIG.endpoints.errandList, {
      method: 'POST',
      body: JSON.stringify({
        task_type: String(payload.task_type || 'quick'),
        title: String(payload.title || ''),
        reward: String(payload.reward || '￥5'),
        time: String(payload.time || '尽快'),
        pickup_location: String(payload.pickup_location || ''),
        destination: String(payload.destination || ''),
        note: String(payload.note || ''),
        contact: String(payload.contact || '')
      }),
      retries: 0
    });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return apiAdapter.mapErrandItem(data, 0);
  },

  async runErrandAction(taskId, action) {
    const data = await apiRequest(API_CONFIG.endpoints.errandAction, {
      method: 'POST',
      body: JSON.stringify({ task_id: String(taskId || ''), action: String(action || 'detail') }),
      retries: 0
    });
    if (!data || typeof data !== 'object' || !data.item) {
      return null;
    }
    return {
      message: String(data.message || '状态已更新'),
      item: apiAdapter.mapErrandItem(data.item, 0)
    };
  },

  async createWebLoginCode() {
    const data = await apiRequest(API_CONFIG.endpoints.clientWebLoginCode, {
      method: 'POST',
      retries: 0
    });
    if (!data || typeof data !== 'object') {
      return null;
    }
    return {
      code: String(data.code || ''),
      expiresIn: Number(data.expires_in || data.expiresIn || 0),
      expiresAt: String(data.expires_at || data.expiresAt || '')
    };
  },

  async exchangeWebLoginCode(code) {
    const data = await apiRequest(API_CONFIG.endpoints.clientWebLoginExchange, {
      method: 'POST',
      auth: false,
      allowRefresh: false,
      retries: 0,
      body: JSON.stringify({ code: String(code || '').trim() })
    });
    if (!data || !data.access_token) {
      return null;
    }
    appState.clientAuth = {
      token: String(data.access_token),
      refreshToken: String(data.refresh_token || ''),
      userId: Number(data.user_id || 0),
      username: String(data.username || ''),
      displayName: String(data.display_name || ''),
      publicName: String(data.public_name || '')
    };
    saveClientToken(appState.clientAuth.token);
    saveClientRefreshToken(appState.clientAuth.refreshToken);
    saveState();
    syncUserScopedLikes();
    syncHeaderGreeting();
    return appState.clientAuth;
  },

  async fetchUnreadCounts() {
    const data = await apiRequest(API_CONFIG.endpoints.unreadCount, { method: 'GET' });
    if (!data || typeof data !== 'object') {
      return null;
    }

    return {
      likesUnread: Number(data.likes_unread ?? data.likes ?? 0),
      savedUnread: Number(data.saved_unread ?? data.saved ?? 0),
      likesTotal: Number(data.likes_total ?? data.likesTotal ?? data.likes_unread ?? data.likes ?? 0),
      savedTotal: Number(data.saved_total ?? data.savedTotal ?? data.saved_unread ?? data.saved ?? 0)
    };
  },

  async fetchInboxDetail(type) {
    const endpoint = type === 'saved'
      ? API_CONFIG.endpoints.inboxSaved
      : API_CONFIG.endpoints.inboxLikes;

    const data = await apiRequest(endpoint, { method: 'GET' });
    if (!data || !Array.isArray(data.items)) {
      return null;
    }

    return data.items.map((item, index) => ({
      id: String(item.id || `${type}-${index}`),
      main: String(item.main || item.title || item.content || ''),
      meta: String(item.meta || item.time || ''),
      postId: String(item.post_id || item.postId || ''),
      sourceType: item.source_type === 'search' ? 'search' : 'feed'
    })).filter((item) => item.main);
  },

  async markInboxRead(type) {
    await apiRequest(API_CONFIG.endpoints.markRead, {
      method: 'POST',
      body: JSON.stringify({ type })
    });
  },

  async fetchRecentSearches() {
    const data = await apiRequest(API_CONFIG.endpoints.recentSearches, { method: 'GET' });
    if (!data || !Array.isArray(data.keywords)) {
      return null;
    }
    return normalizeRecentSearches(data.keywords);
  },

  async saveRecentSearch(keyword) {
    await apiRequest(API_CONFIG.endpoints.recentSearches, {
      method: 'POST',
      body: JSON.stringify({ keyword })
    });
  }
};

function setActiveView(view) {
  const safeView = validViews.has(view) ? view : 'home';

  tabs.forEach((tab) => {
    tab.classList.toggle('is-active', tab.dataset.target === safeView);
  });

  screens.forEach((screen) => {
    screen.classList.toggle('is-active', screen.dataset.view === safeView);
  });

  if (fabBtn) {
    fabBtn.classList.toggle('is-hidden', safeView !== 'home');
  }

  if (safeView !== 'profile' && !detailSheet.hidden) {
    closeInboxDetailSheet();
  }

  if (safeView !== 'profile' && postDetailSheet && !postDetailSheet.hidden) {
    closePostDetailSheet();
  }

  if (safeView !== 'home' && commentSheet && !commentSheet.hidden) {
    closeCommentSheet();
  }

  if (safeView !== 'home' && postComposerSheet && !postComposerSheet.hidden) {
    closePostComposer();
  }

  if (safeView !== 'messages' && wikiDetailSheet && !wikiDetailSheet.hidden) {
    closeWikiDetailSheet();
  }

  if (safeView !== 'profile' && eduSheet && !eduSheet.hidden) {
    closeEduSheet();
  }

  if (searchResultSheet && !searchResultSheet.hidden) {
    closeSearchResultSheet();
  }

  if (subpageSheet && !subpageSheet.hidden) {
    closeSubpageSheet();
  }

  if (errandSheet && !errandSheet.hidden) {
    closeErrandPage();
  }

  if (crossGroupSheet && !crossGroupSheet.hidden) {
    closeCrossGroupPage();
  }

  if (imageViewer && !imageViewer.hidden) {
    closeImageViewer();
  }

  if ((safeView === 'profile' || safeView === 'home') && API_CONFIG.refreshOnProfileEnter) {
    void refreshVisibleClientState({ force: true });
  }

  appState.lastTab = safeView;
  saveState();
}

function getFeedByFilter(filter) {
  if (filter === 'all') {
    return feedPosts;
  }
  return feedPosts.filter((item) => item.category === filter);
}

function isDuplicateReviewReason(reason) {
  const text = String(reason || '').trim();
  return text.includes('重复') || /duplicate/i.test(text);
}

function getPostStatusBadge(post) {
  if (post.knowledgeReady) {
    return { tone: 'knowledge', text: 'AI已采纳' };
  }
  if (isDuplicateReviewReason(post.knowledgeReviewReason)) {
    return { tone: 'synced', text: '同主题已入库' };
  }
  if (post.adopted) {
    return { tone: 'adopted', text: '楼主采纳评论' };
  }
  return null;
}

function renderFeed() {
  if (!feedList) {
    return;
  }

  const posts = getFeedByFilter(appState.activeFeedFilter);
  feedList.innerHTML = '';

  if (!posts.length) {
    const empty = document.createElement('article');
    empty.className = 'card post-card';
    empty.innerHTML = '<p>当前分类暂无帖子，试试切换到“最新”。</p>';
    feedList.appendChild(empty);
    return;
  }

  posts.forEach((post) => {
    const badgeItems = [];
    if (post.knowledgeReady) {
      badgeItems.push('<span class="post-badge knowledge">AI已采纳</span>');
    } else if (post.adopted) {
      badgeItems.push('<span class="post-badge adopted">楼主已采纳</span>');
    }
    const legacyBadges = badgeItems.join('');
    const badge = getPostStatusBadge(post);
    const badges = badge ? `<span class="post-badge ${badge.tone}">${escapeHtml(badge.text)}</span>` : legacyBadges;

    const postNode = document.createElement('article');
    postNode.className = 'card post-card is-clickable';
    postNode.dataset.feedPostId = post.id;
    postNode.dataset.postImageUrl = post.imageUrl ? String(post.imageUrl) : '';
    const safePostId = escapeHtml(post.id);
    const safeAvatar = escapeHtml(post.avatar);
    const safeAuthor = escapeHtml(post.author);
    const safeTime = escapeHtml(post.time);
    const safeTitle = escapeHtml(post.title);
    const safeContent = escapeHtml(post.content);
    const safeTags = Array.isArray(post.tags) ? post.tags.map((tag) => escapeHtml(tag)).join(' ') : '';
    const localPreview = getCommentPreviewForPost(post.id, 3);
    const remotePreview = Array.isArray(post.commentsPreview)
      ? post.commentsPreview.map((line) => sanitizePreviewLine(line)).filter((line) => line)
      : [];
    const previewLines = remotePreview.length
      ? remotePreview
      : localPreview;
    const previewBlock = previewLines.length
      ? `<div class="post-thread-preview">${previewLines.map((line) => `<p>${escapeHtml(line)}</p>`).join('')}</div>`
      : '';
    const imageBlock = post.imageUrl
      ? `<img class="comment-image" src="${escapeHtml(post.imageUrl)}" alt="帖子图片" data-image-kind="post" data-image-viewer="true">`
      : '';
    postNode.innerHTML = `
      <div class="author-row">
        <div class="avatar">${safeAvatar}</div>
        <div class="author-meta">
          <p class="author-line"><strong>${safeAuthor}</strong></p>
          <p class="time">${safeTime}</p>
        </div>
        <span class="more">···</span>
      </div>
      <h4>${safeTitle}</h4>
      <p>${safeContent}</p>
      ${imageBlock}
      ${previewBlock}
      ${badges ? `<div class="post-badges">${badges}</div>` : ''}
      <p class="tags">${safeTags}</p>
      <div class="post-actions">
        <button class="${post.liked ? 'is-on' : ''}" data-action="like" data-post-id="${safePostId}">
          ${post.liked ? `已点赞 ${post.likes}` : `点赞 ${post.likes}`}
        </button>
        <button class="${post.commented ? 'is-on' : ''}" data-action="comment" data-post-id="${safePostId}">
          评论 ${post.comments}
        </button>
      </div>
    `;

    feedList.appendChild(postNode);
  });
}

function normalizeMatchText(value) {
  return String(value || '').replace(/\s+/g, '').toLowerCase();
}

function findMarketPostByKeyword(keyword) {
  const key = normalizeMatchText(keyword);
  if (!key) {
    return null;
  }

  return marketPosts.find((item) => normalizeMatchText(item.title) === key)
    || marketPosts.find((item) => normalizeMatchText(item.title).includes(key))
    || marketPosts.find((item) => normalizeMatchText((item.keywords || []).join(' ')).includes(key))
    || null;
}

function findFeedPostByKeyword(keyword) {
  const key = normalizeMatchText(keyword);
  if (!key) {
    return null;
  }

  return feedPosts.find((item) => normalizeMatchText(item.title) === key)
    || feedPosts.find((item) => normalizeMatchText(item.title).includes(key))
    || feedPosts.find((item) => {
      const source = `${item.content || ''} ${(item.tags || []).join(' ')}`;
      return normalizeMatchText(source).includes(key);
    })
    || null;
}

function resolvePostTargetByKeyword(keyword, preferred = 'search') {
  const key = String(keyword || '').trim();
  if (!key) {
    return null;
  }

  const preferredSearch = preferred === 'search';
  if (preferredSearch) {
    const market = findMarketPostByKeyword(key);
    if (market) {
      return { postId: market.id, sourceType: 'search' };
    }
    const feed = findFeedPostByKeyword(key);
    if (feed) {
      return { postId: feed.id, sourceType: 'feed' };
    }
    return null;
  }

  const feed = findFeedPostByKeyword(key);
  if (feed) {
    return { postId: feed.id, sourceType: 'feed' };
  }
  const market = findMarketPostByKeyword(key);
  if (market) {
    return { postId: market.id, sourceType: 'search' };
  }
  return null;
}

function openPostByKeyword(keyword, options = {}) {
  const {
    preferred = 'search',
    fallbackSearch = true
  } = options;
  const key = String(keyword || '').trim();
  if (!key) {
    return false;
  }

  const target = resolvePostTargetByKeyword(key, preferred);
  if (target && target.postId) {
    openPostDetailSheet(target.postId, target.sourceType || 'search');
    return true;
  }

  if (fallbackSearch) {
    if (marketQuery) {
      marketQuery.value = key;
    }
    void runMarketSearch({ openResultPage: true });
  }
  return false;
}

function renderHomeHotTopics() {
  if (!homeHotList) {
    return;
  }

  homeHotList.innerHTML = '';
  const list = Array.isArray(homeHotTopics) ? homeHotTopics.slice(0, 3) : [];
  if (!list.length) {
    return;
  }

  list.forEach((item, idx) => {
    const row = document.createElement('button');
    row.className = 'hot-row';
    row.type = 'button';
    row.dataset.hot = item.query || item.title || '';
    const mappedPostId = item.postRef || hotTopicPostMap[String(item.id || '')] || '';
    if (mappedPostId) {
      row.dataset.marketPostId = mappedPostId;
      row.dataset.source = item.sourceType || 'search';
    }
    row.dataset.hotId = item.id || `hot-${idx + 1}`;
    row.innerHTML = `
      <span class="hot-rank top">${item.rank || idx + 1}</span>
      <span class="hot-title">${item.title || ''}</span>
      <span class="hot-heat">${item.heat || ''}</span>
    `;
    homeHotList.appendChild(row);
  });
}

function setActiveFeedFilter(filter) {
  appState.activeFeedFilter = filter;
  saveState();

  feedFilterButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.filter === filter);
  });

  renderFeed();
  void hydrateFeedByFilter(filter);
}

async function hydrateFeedByFilter(filter) {
  const remotePosts = await apiAdapter.fetchFeedList(filter);
  if (!Array.isArray(remotePosts) || !remotePosts.length) {
    return;
  }

  feedPosts.splice(0, feedPosts.length, ...remotePosts);
  renderFeed();
}

function findFeedPost(postId) {
  return feedPosts.find((item) => item.id === postId) || null;
}

function ensureCommentStore(postId) {
  if (!Array.isArray(commentStore[postId])) {
    commentStore[postId] = [];
  }
  return commentStore[postId];
}

function sanitizePreviewLine(line) {
  const text = String(line || '').replace(/\s+/g, ' ').trim();
  if (!text) {
    return '';
  }
  if (PREVIEW_NOISE_PATTERN.test(text)) {
    return '';
  }
  const colonPos = Math.max(text.lastIndexOf('：'), text.lastIndexOf(':'));
  if (colonPos >= 0) {
    const tail = text.slice(colonPos + 1).trim();
    if (!tail || PREVIEW_NOISE_PATTERN.test(tail)) {
      return '';
    }
  } else if (PREVIEW_NOISE_PATTERN.test(text)) {
    return '';
  }
  return text.slice(0, 96);
}

function formatCommentPreviewLine(item) {
  const author = String(item.author || '@匿名用户');
  const cleanAuthor = author.startsWith('@') ? author.slice(1) : author;
  const rawContent = String(item.content || '').replace(/\s+/g, ' ').trim();
  if (PREVIEW_NOISE_PATTERN.test(rawContent)) {
    return '';
  }
  const content = rawContent || (item.imageUrl ? '[图片]' : '');
  if (!content) {
    return '';
  }
  const replyTo = String(item.replyToAuthor || '').trim();
  const cleanReplyTo = replyTo.startsWith('@') ? replyTo.slice(1) : replyTo;
  const prefix = cleanReplyTo ? `${cleanAuthor} 回复 ${cleanReplyTo}：` : `${cleanAuthor}：`;
  return sanitizePreviewLine(`${prefix}${content}`);
}

function getCommentPreviewForPost(postId, limit = 3) {
  const rows = ensureCommentStore(postId)
    .filter((item) => item && item.status === 'sent' && (item.content || item.imageUrl))
    .slice(-Math.max(1, Number(limit || 3)));
  return rows
    .map((item) => formatCommentPreviewLine(item))
    .filter((line) => line);
}

function collectCommentThreadIds(items, rootCommentId) {
  const rootId = String(rootCommentId || '');
  if (!rootId) {
    return new Set();
  }

  const childrenByParent = new Map();
  (Array.isArray(items) ? items : []).forEach((item) => {
    const childId = String(item && item.id ? item.id : '');
    const parentId = String(item && item.parentCommentId ? item.parentCommentId : '');
    if (!childId || !parentId) {
      return;
    }
    if (!childrenByParent.has(parentId)) {
      childrenByParent.set(parentId, []);
    }
    childrenByParent.get(parentId).push(childId);
  });

  const visited = new Set();
  const stack = [rootId];
  while (stack.length) {
    const current = stack.pop();
    if (!current || visited.has(current)) {
      continue;
    }
    visited.add(current);
    const children = childrenByParent.get(current) || [];
    children.forEach((child) => {
      if (!visited.has(child)) {
        stack.push(child);
      }
    });
  }
  return visited;
}

function updateCommentReplyMeta() {
  if (!commentReplyMeta || !commentReplyText || !commentInput) {
    return;
  }

  if (!activeReplyTarget) {
    commentReplyMeta.hidden = true;
    commentReplyText.textContent = '';
    commentInput.placeholder = '说点什么...';
    return;
  }

  commentReplyMeta.hidden = false;
  commentReplyText.textContent = `正在回复 ${activeReplyTarget.author || '@某同学'}`;
  commentInput.placeholder = `回复 ${activeReplyTarget.author || '@某同学'}...`;
}

function clearReplyTarget() {
  activeReplyTarget = null;
  updateCommentReplyMeta();
}

function setReplyTarget(commentId) {
  if (!activeCommentPostId) {
    return;
  }
  const rows = ensureCommentStore(activeCommentPostId);
  const target = rows.find((item) => item.id === commentId);
  if (!target) {
    return;
  }
  activeReplyTarget = {
    id: String(target.id || ''),
    author: String(target.author || '@匿名用户')
  };
  updateCommentReplyMeta();
  if (commentInput) {
    commentInput.focus();
  }
}

function setCommentComposerState() {
  if (!commentSendBtn || !commentInput) {
    return;
  }

  const hasValue = Boolean(String(commentInput.value || '').trim());
  commentSendBtn.disabled = isSendingComment || (!hasValue && !selectedCommentImage);
  commentSendBtn.textContent = isSendingComment ? '发送中...' : '发送';
}

function renderCommentList() {
  if (!commentList) {
    return;
  }

  commentList.innerHTML = '';
  const items = activeCommentPostId ? ensureCommentStore(activeCommentPostId) : [];

  if (isLoadingComments && !items.length) {
    const loading = document.createElement('div');
    loading.className = 'detail-empty';
    loading.textContent = '评论加载中...';
    commentList.appendChild(loading);
    return;
  }

  if (!items.length) {
    const empty = document.createElement('div');
    empty.className = 'detail-empty';
    empty.textContent = '还没有评论，来发第一条吧';
    commentList.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const commentId = String(item.id || '');
    const likedOnce = commentId && likedCommentIds.has(commentId);
    const card = document.createElement('article');
    card.className = 'comment-item';
    card.dataset.commentId = commentId;
    if (item.parentCommentId) {
      card.classList.add('is-reply');
    }

    const head = document.createElement('div');
    head.className = 'comment-item-head';

    const author = document.createElement('span');
    author.className = 'comment-author';
    author.textContent = item.author || '@匿名用户';

    const meta = document.createElement('span');
    meta.className = 'comment-meta';

    const time = document.createElement('span');
    time.textContent = item.time || '刚刚';
    meta.appendChild(time);

    if (item.status === 'sending' || item.status === 'failed') {
      const status = document.createElement('span');
      status.className = `comment-status ${item.status}`;
      status.textContent = item.status === 'sending' ? '发送中' : '发送失败';
      meta.appendChild(status);

      if (item.status === 'failed' && item.errorMsg) {
        const err = document.createElement('span');
        err.className = 'comment-error-tip';
        err.textContent = String(item.errorMsg);
        meta.appendChild(err);
      }
    }

    head.append(author, meta);

    const content = document.createElement('p');
    content.className = 'comment-content';
    content.textContent = item.content || '';

    card.append(head);

    if (item.replyToAuthor) {
      const replyContext = document.createElement('p');
      replyContext.className = 'comment-reply-context';
      replyContext.textContent = `回复 ${item.replyToAuthor}`;
      card.appendChild(replyContext);
    }

    card.appendChild(content);

    if (item.imageUrl) {
      const image = document.createElement('img');
      image.className = 'comment-image';
      image.src = item.imageUrl;
      image.alt = '评论图片';
      image.dataset.imageViewer = 'true';
      image.addEventListener('error', () => {
        const fallback = document.createElement('div');
        fallback.className = 'comment-image-fallback';
        fallback.textContent = '图片不可用';
        image.replaceWith(fallback);
      });
      card.appendChild(image);
    }

    {
      const actions = document.createElement('div');
      actions.className = 'comment-actions';
      const actionLeft = document.createElement('div');
      actionLeft.className = 'comment-action-left';
      const reply = document.createElement('button');
      reply.type = 'button';
      reply.className = 'comment-reply-btn';
      reply.dataset.replyCommentId = item.id;
      reply.textContent = '回复';
      actionLeft.appendChild(reply);
      const like = document.createElement('button');
      like.type = 'button';
      like.className = `comment-like-btn${likedOnce ? ' is-on' : ''}`;
      like.dataset.likeCommentId = item.id;
      like.textContent = likedOnce ? `已赞 ${item.likes || 0}` : `点赞 ${item.likes || 0}`;
      actionLeft.appendChild(like);
      actions.appendChild(actionLeft);

      const post = activeCommentPostId ? findFeedPost(activeCommentPostId) : null;
      const currentUserId = Number(appState.clientAuth && appState.clientAuth.userId ? appState.clientAuth.userId : 0);
      const isOwner = post && Number(post.authorId || 0) === currentUserId;
      const isAuthor = Number(item.authorId || 0) === currentUserId;
      const canDelete = Boolean(item.canDelete) || isOwner || isAuthor;
      if (canDelete) {
        const del = document.createElement('button');
        del.type = 'button';
        del.className = 'comment-delete-btn';
        del.dataset.deleteCommentId = item.id;
        del.textContent = '删除';
        del.addEventListener('click', () => {
          requestDeleteComment(String(item.id || ''));
        });
        actions.appendChild(del);
      }

      if (item.status === 'failed') {
        const retry = document.createElement('button');
        retry.type = 'button';
        retry.className = 'comment-retry-btn';
        retry.dataset.retryCommentId = item.id;
        retry.textContent = '重试发送';
        actions.appendChild(retry);
      }

      card.appendChild(actions);
    }

    commentList.appendChild(card);
  });
}

function updateCommentSheetHeader(postId) {
  const post = findFeedPost(postId);
  if (!post || !commentSheetTitle || !commentSheetSub) {
    return;
  }

  commentSheetTitle.textContent = post.title;
  commentSheetSub.textContent = `${post.comments} 条评论`;
}

function closeCommentSheet() {
  if (!commentSheet || !commentSheetMask) {
    return;
  }
  commentSheet.hidden = true;
  commentSheetMask.hidden = true;
  activeCommentPostId = '';
  isSendingComment = false;
  selectedCommentImage = null;
  activeReplyTarget = null;
  if (commentImageInput) {
    commentImageInput.value = '';
  }
  if (commentImageMeta) {
    commentImageMeta.textContent = '未选择图片';
  }
  updateCommentReplyMeta();
  setCommentComposerState();
}

function mergeRemoteComments(postId, remoteItems) {
  const current = ensureCommentStore(postId);
  const pendingItems = current.filter((item) => item.status !== 'sent');
  const map = new Map();
  [...pendingItems, ...remoteItems].forEach((item) => {
    map.set(item.id, item);
  });
  commentStore[postId] = Array.from(map.values());
}

function requestDeleteComment(commentId) {
  if (!commentId || !activeCommentPostId) {
    return;
  }
  if (!confirm('确认删除这条评论？')) {
    return;
  }
  const postId = activeCommentPostId;
  const list = ensureCommentStore(postId);
  if (!list.some((item) => String(item.id) === String(commentId))) {
    return;
  }

  const snapshot = list.slice();
  const removeIds = collectCommentThreadIds(snapshot, commentId);
  const removedCount = snapshot.filter((item) => {
    const id = String(item && item.id ? item.id : '');
    const status = String(item && item.status ? item.status : 'sent');
    return removeIds.has(id) && status === 'sent';
  }).length;

  commentStore[postId] = snapshot.filter((item) => !removeIds.has(String(item.id || '')));

  const post = findFeedPost(postId);
  const previousPostComments = post ? Number(post.comments || 0) : 0;
  const previousPreview = post && Array.isArray(post.commentsPreview) ? [...post.commentsPreview] : [];
  if (post) {
    post.comments = Math.max(0, previousPostComments - removedCount);
    post.commentsPreview = getCommentPreviewForPost(postId, 3);
  }
  renderFeed();
  renderCommentList();
  void apiAdapter.deleteComment(postId, commentId).then((resp) => {
    if (!resp || !resp.deleted) {
      showToast('删除失败，请稍后再试');
      commentStore[postId] = snapshot;
      if (post) {
        post.comments = previousPostComments;
        post.commentsPreview = previousPreview;
      }
      renderFeed();
      renderCommentList();
      return;
    }

    if (Array.isArray(resp.deletedIds) && resp.deletedIds.length) {
      const remoteRemoved = new Set(resp.deletedIds.map((id) => String(id)));
      commentStore[postId] = ensureCommentStore(postId).filter((item) => !remoteRemoved.has(String(item.id || '')));
    }

    if (post && Number.isFinite(resp.deletedCount)) {
      post.comments = Math.max(0, previousPostComments - Number(resp.deletedCount || 0));
      post.commentsPreview = getCommentPreviewForPost(postId, 3);
    }
    renderFeed();
    renderCommentList();
  });
}

async function loadCommentsForPost(postId) {
  isLoadingComments = true;
  renderCommentList();

  try {
    const remote = await apiAdapter.fetchPostComments(postId, { page: 1, pageSize: 20 });
    if (remote && Array.isArray(remote.items)) {
      mergeRemoteComments(postId, remote.items);
      const post = findFeedPost(postId);
      if (post) {
        post.commentsPreview = getCommentPreviewForPost(postId, 3);
      }
      if (Number.isFinite(remote.total)) {
        if (post) {
          post.comments = Math.max(Number(post.comments || 0), Number(remote.total || 0));
          renderFeed();
        }
      }
    }
  } finally {
    isLoadingComments = false;
    if (activeCommentPostId === postId) {
      renderCommentList();
      updateCommentSheetHeader(postId);
    }
  }
}

function openCommentSheet(postId) {
  if (!commentSheet || !commentSheetMask || !commentInput) {
    return;
  }

  const post = findFeedPost(postId);
  if (!post) {
    showToast('原帖不存在');
    return;
  }

  activeCommentPostId = postId;
  closeInboxDetailSheet();
  closePostDetailSheet();
  updateCommentSheetHeader(postId);
  commentInput.value = commentDraftByPost[postId] || '';
  activeReplyTarget = null;
  selectedCommentImage = null;
  if (commentImageInput) {
    commentImageInput.value = '';
  }
  if (commentImageMeta) {
    commentImageMeta.textContent = '未选择图片';
  }
  updateCommentReplyMeta();
  setCommentComposerState();
  renderCommentList();

  commentSheet.hidden = false;
  commentSheetMask.hidden = true;
  void loadCommentsForPost(postId);
}

function upsertComment(postId, targetId, nextComment) {
  const list = ensureCommentStore(postId);
  const idx = list.findIndex((item) => item.id === targetId);
  if (idx < 0) {
    list.push(nextComment);
    return;
  }
  list[idx] = {
    ...list[idx],
    ...nextComment
  };
}

function bumpPostCommentCount(postId) {
  const post = findFeedPost(postId);
  if (!post) {
    return;
  }
  post.commented = true;
  post.comments = Number(post.comments || 0) + 1;
  post.commentsPreview = getCommentPreviewForPost(postId, 3);
  renderFeed();
  updateCommentSheetHeader(postId);
}

async function submitComment() {
  if (!activeCommentPostId || !commentInput || isSendingComment) {
    return;
  }

  const postId = activeCommentPostId;
  const content = String(commentInput.value || '').trim();
  const imageFile = selectedCommentImage;
  const replyTarget = activeReplyTarget
    ? { id: String(activeReplyTarget.id || ''), author: String(activeReplyTarget.author || '') }
    : null;
  if (!content && !imageFile) {
    setCommentComposerState();
    return;
  }

  const clientId = `local-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
  const localComment = {
    id: clientId,
    author: '@我',
    content,
    time: '刚刚',
    imageUrl: imageFile ? URL.createObjectURL(imageFile) : '',
    likes: 0,
    parentCommentId: replyTarget && replyTarget.id ? replyTarget.id : '',
    replyToAuthor: replyTarget && replyTarget.author ? replyTarget.author : '',
    localImageFile: imageFile,
    errorMsg: '',
    status: 'sending'
  };

  ensureCommentStore(postId).push(localComment);
  commentInput.value = '';
  commentDraftByPost[postId] = '';
  selectedCommentImage = null;
  clearReplyTarget();
  if (commentImageInput) {
    commentImageInput.value = '';
  }
  if (commentImageMeta) {
    commentImageMeta.textContent = '未选择图片';
  }
  isSendingComment = true;
  setCommentComposerState();
  renderCommentList();

  try {
    const remoteComment = await apiAdapter.createPostComment(postId, content, clientId, imageFile, replyTarget);
    if (!remoteComment) {
      upsertComment(postId, clientId, {
        status: 'failed',
        time: '发送失败',
        errorMsg: lastApiIssueMessage || '后端未连接'
      });
      notifyApiIssue(lastApiIssueMessage || '评论发送失败，可点击重试');
      return;
    }

    upsertComment(postId, clientId, remoteComment);
    bumpPostCommentCount(postId);
  } finally {
    isSendingComment = false;
    if (activeCommentPostId === postId) {
      renderCommentList();
      setCommentComposerState();
    }
  }
}

async function retryComment(commentId) {
  if (!activeCommentPostId || !commentId || isSendingComment) {
    return;
  }

  const postId = activeCommentPostId;
  const list = ensureCommentStore(postId);
  const target = list.find((item) => item.id === commentId);
  if (!target || target.status !== 'failed') {
    return;
  }

  isSendingComment = true;
  upsertComment(postId, commentId, { status: 'sending', time: '重试中' });
  renderCommentList();
  setCommentComposerState();

  try {
    const retryReplyTarget = target.parentCommentId
      ? {
          id: String(target.parentCommentId || ''),
          author: String(target.replyToAuthor || '')
        }
      : null;
    const remoteComment = await apiAdapter.createPostComment(
      postId,
      target.content,
      commentId,
      target.localImageFile || null,
      retryReplyTarget
    );
    if (!remoteComment) {
      upsertComment(postId, commentId, {
        status: 'failed',
        time: '重试失败',
        errorMsg: lastApiIssueMessage || '后端未连接'
      });
      notifyApiIssue(lastApiIssueMessage || '评论重试失败，请稍后再试');
      return;
    }

    upsertComment(postId, commentId, remoteComment);
    bumpPostCommentCount(postId);
  } finally {
    isSendingComment = false;
    if (activeCommentPostId === postId) {
      renderCommentList();
      setCommentComposerState();
    }
  }
}

function closePostComposer() {
  if (!postComposerSheet || !postComposerMask) {
    return;
  }
  postComposerSheet.hidden = true;
  postComposerMask.hidden = true;
  selectedPostImage = null;
  if (postImageInput) {
    postImageInput.value = '';
  }
  if (postImageMeta) {
    postImageMeta.textContent = '未选择图片';
  }
  if (postSubmitBtn) {
    postSubmitBtn.textContent = '发布';
    postSubmitBtn.disabled = false;
  }
}

function openPostComposer() {
  if (!postComposerSheet || !postComposerMask) {
    return;
  }
  closeCommentSheet();
  closeInboxDetailSheet();
  closePostDetailSheet();
  postComposerSheet.hidden = false;
  postComposerMask.hidden = false;
}

async function submitPostComposer() {
  if (!postCategoryInput || !postTitleInput || !postContentInput || isPublishingPost) {
    return;
  }

  const category = String(postCategoryInput.value || 'study');
  const title = String(postTitleInput.value || '').trim();
  const content = String(postContentInput.value || '').trim();
  const tags = String(postTagsInput ? postTagsInput.value : '')
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item)
    .slice(0, 8);

  if (!title || !content) {
    showToast('请填写标题和内容');
    return;
  }

  isPublishingPost = true;
  if (postSubmitBtn) {
    postSubmitBtn.disabled = true;
    postSubmitBtn.textContent = '发布中...';
  }

  try {
    const created = await apiAdapter.createPost(category, title, content, tags, selectedPostImage);
    if (!created) {
      const reason = lastApiIssueMessage || '请检查后端是否启动';
      showToast(`发布失败：${reason}`);
      return;
    }

    feedPosts.unshift(created);
    renderFeed();
    closePostComposer();
    showToast('发布成功');

    postTitleInput.value = '';
    postContentInput.value = '';
    if (postTagsInput) {
      postTagsInput.value = '';
    }
  } finally {
    isPublishingPost = false;
    if (postSubmitBtn) {
      postSubmitBtn.disabled = false;
      postSubmitBtn.textContent = '发布';
    }
  }
}

async function handleFeedAction(action, id) {
  const post = findFeedPost(id);
  if (!post) {
    return;
  }

  if (action === 'like') {
    const wasLiked = post.liked || likedPostIds.has(String(id));
    const nextLiked = !wasLiked;
    const previousLiked = Boolean(wasLiked);
    const previousLikes = Number(post.likes || 0);

    post.liked = nextLiked;
    post.likes = nextLiked ? previousLikes + 1 : Math.max(0, previousLikes - 1);
    if (nextLiked) {
      likedPostIds.add(String(id));
    } else {
      likedPostIds.delete(String(id));
    }
    saveLikedSet(likedPostIds, appState.clientAuth.userId);
    renderFeed();

    const remote = await apiAdapter.toggleFeedLike(id, nextLiked);
    if (remote) {
      post.liked = Boolean(remote.liked);
      post.likes = Math.max(0, Number(remote.likes || post.likes));
      if (post.liked) {
        likedPostIds.add(String(id));
      } else {
        likedPostIds.delete(String(id));
      }
      saveLikedSet(likedPostIds, appState.clientAuth.userId);
      renderFeed();
    } else {
      post.liked = previousLiked;
      post.likes = previousLikes;
      if (previousLiked) {
        likedPostIds.add(String(id));
      } else {
        likedPostIds.delete(String(id));
      }
      saveLikedSet(likedPostIds, appState.clientAuth.userId);
      renderFeed();
      showToast('点赞失败，请重试');
    }
    return;
  }

  if (action === 'comment') {
    openCommentSheet(id);
  }
}

function searchMarketPosts(keyword) {
  const key = toLowerSafe(keyword).trim();
  if (!key) {
    return [...marketPosts];
  }

  return marketPosts.filter((post) => {
    const source = [post.title, post.snippet, post.meta, post.keywords.join(' ')].join(' ');
    return toLowerSafe(source).includes(key);
  });
}

function sortMarketResults(list, sortBy) {
  if (sortBy === 'latest') {
    return [...list].sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt)));
  }

  return [...list].sort((a, b) => (b.hotScore || 0) - (a.hotScore || 0));
}

function renderMarketResults(list, options = {}) {
  if (!marketResultList || !marketCount) {
    return;
  }

  const safeList = Array.isArray(list) ? list : [];
  const {
    append = false,
    mode = 'local',
    page = 1,
    pageSize = 30,
    total = safeList.length,
    hasMore = false,
    query = '',
    sort = appState.searchSort || 'hot'
  } = options;

  if (!append) {
    searchResultState = {
      ...searchResultState,
      all: safeList,
      source: mode === 'remote' ? 'remote' : 'local',
      page: Math.max(1, Number(page) || 1),
      pageSize: Math.max(1, Number(pageSize) || 30),
      total: Math.max(0, Number(total) || safeList.length),
      hasMore: Boolean(hasMore),
      loadingMore: false,
      query: String(query || ''),
      sort: validSort.has(sort) ? sort : 'hot'
    };
    searchResultState.visibleCount = searchResultState.source === 'remote'
      ? searchResultState.all.length
      : Math.min(SEARCH_PAGE_VIEW_SIZE, searchResultState.all.length);
  } else if (searchResultState.source === 'remote') {
    const merged = new Map();
    searchResultState.all.forEach((item) => merged.set(item.id, item));
    safeList.forEach((item) => merged.set(item.id, item));
    searchResultState.all = Array.from(merged.values());
    searchResultState.page = Math.max(Number(page) || 1, searchResultState.page);
    searchResultState.pageSize = Math.max(1, Number(pageSize) || searchResultState.pageSize || 30);
    searchResultState.total = Math.max(Number(total) || searchResultState.total || 0, searchResultState.all.length);
    searchResultState.hasMore = Boolean(hasMore);
    searchResultState.visibleCount = searchResultState.all.length;
    if (query) {
      searchResultState.query = String(query);
    }
  } else {
    searchResultState.visibleCount = Math.min(
      searchResultState.visibleCount + SEARCH_PAGE_VIEW_SIZE,
      searchResultState.all.length
    );
  }

  renderVisibleSearchResults();
}

function renderSearchResultsInto(listEl, countEl) {
  if (!listEl || !countEl) {
    return;
  }
  const isRemoteSource = searchResultState.source === 'remote';
  const all = searchResultState.all || [];
  const pageSize = isRemoteSource ? Number(searchResultState.pageSize || 10) : SEARCH_PAGE_VIEW_SIZE;
  const page = Math.max(1, Number(searchResultState.page || 1));
  const sliceStart = isRemoteSource ? 0 : (page - 1) * pageSize;
  const sliceEnd = isRemoteSource ? all.length : sliceStart + pageSize;
  const visibleList = isRemoteSource ? all : all.slice(sliceStart, sliceEnd);

  listEl.innerHTML = '';
  if (!all.length) {
    countEl.textContent = '0 条';
  } else if (isRemoteSource) {
    const total = Math.max(Number(searchResultState.total || 0), all.length);
    countEl.textContent = `${all.length}/${total} 条`;
  } else {
    const totalPages = Math.max(1, Math.ceil(all.length / pageSize));
    countEl.textContent = `第 ${page}/${totalPages} 页 · 共 ${all.length} 条`;
  }

  if (!all.length) {
    const empty = document.createElement('div');
    empty.className = 'result-item';
    empty.innerHTML = '<h5>暂无匹配结果</h5><p>可尝试关键词：食堂、空教室、调课、校车。</p>';
    listEl.appendChild(empty);
    if (loadMoreSearchBtn) {
      loadMoreSearchBtn.hidden = true;
    }
    return;
  }

  visibleList.forEach((item) => {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'result-item is-clickable';
    card.dataset.marketPostId = item.postId || item.id;
    card.dataset.searchPostRef = item.id;
    card.dataset.source = item.postId ? 'feed' : 'search';
    card.innerHTML = `
      <h5>${item.title}</h5>
      <p>${item.snippet}</p>
      <small>${item.meta} · 更新时间 ${item.updatedAt} · 热度 ${item.hotScore}</small>
    `;
    card.addEventListener('click', () => {
      const searchRef = String(card.dataset.searchPostRef || card.dataset.marketPostId || '').trim();
      const fallback = findSearchResultItem(searchRef) || null;
      void openPostDetailSheet(card.dataset.marketPostId || searchRef, card.dataset.source || 'search', fallback);
    });
    listEl.appendChild(card);
  });

}

function renderVisibleSearchResults() {
  renderSearchResultsInto(marketResultList, marketCount);
  renderSearchResultsInto(searchResultList, searchResultCount);
  updateSearchPager();
}

async function loadMoreSearchResults() {
  if (!searchResultState.all.length) {
    return;
  }

  if (searchResultState.source !== 'remote') {
    renderMarketResults(searchResultState.all, { append: true });
    return;
  }

  if (searchResultState.loadingMore || !searchResultState.hasMore) {
    return;
  }

  searchResultState.loadingMore = true;
  renderVisibleSearchResults();

  try {
    const nextPage = Number(searchResultState.page || 1) + 1;
    const remoteResult = await apiAdapter.searchPosts(searchResultState.query, searchResultState.sort, {
      page: nextPage,
      pageSize: searchResultState.pageSize || 30
    });

    if (!remoteResult || !Array.isArray(remoteResult.items)) {
      notifyApiIssue('加载更多失败，保持当前结果');
      return;
    }

    renderMarketResults(remoteResult.items, {
      append: true,
      mode: 'remote',
      page: remoteResult.page,
      pageSize: remoteResult.pageSize,
      total: remoteResult.total,
      hasMore: remoteResult.hasMore,
      query: searchResultState.query,
      sort: searchResultState.sort
    });
  } finally {
    searchResultState.loadingMore = false;
    renderVisibleSearchResults();
  }
}

function renderRecentSearches() {
  if (!recentSearchList) {
    return;
  }

  recentSearchList.innerHTML = '';
  const list = appState.recentSearches || [];

  if (!list.length) {
    const empty = document.createElement('span');
    empty.className = 'recent-empty';
    empty.textContent = '暂无历史搜索';
    recentSearchList.appendChild(empty);
    return;
  }

  list.forEach((keyword) => {
    const chip = document.createElement('button');
    chip.className = 'recent-chip';
    chip.type = 'button';
    chip.textContent = keyword;
    chip.dataset.keyword = keyword;
    recentSearchList.appendChild(chip);
  });
}

function setSearchSort(sortBy, triggerSearch = true) {
  const safeSort = validSort.has(sortBy) ? sortBy : 'hot';
  appState.searchSort = safeSort;
  saveState();

  sortButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.sort === safeSort);
  });

  searchPageSortButtons.forEach((button) => {
    button.classList.toggle('is-active', button.dataset.searchPageSort === safeSort);
  });

  if (triggerSearch) {
    void runMarketSearch({ persistRecent: false });
  }
}

function addRecentSearch(keyword) {
  const clean = String(keyword || '').trim();
  if (!clean) {
    return;
  }

  const prev = Array.isArray(appState.recentSearches) ? appState.recentSearches : [];
  const next = [clean, ...prev.filter((item) => item !== clean)].slice(0, 6);
  appState.recentSearches = next;
  saveState();
  renderRecentSearches();

  void apiAdapter.saveRecentSearch(clean);
}

async function runMarketSearch(options = {}) {
  if (!marketQuery) {
    return;
  }

  const { persistRecent = true, openResultPage = true } = options;
  if (API_CONFIG.enabled && (!appState.clientAuth || !appState.clientAuth.token)) {
    await ensureClientSession();
  }
  const query = marketQuery.value.trim();
  appState.lastSearch = query;
  saveState();

  if (persistRecent && query) {
    addRecentSearch(query);
  }

  const remoteResult = await apiAdapter.searchPosts(query, appState.searchSort, {
    page: 1,
    pageSize: 30
  });

  if (remoteResult && Array.isArray(remoteResult.items)) {
    renderMarketResults(remoteResult.items, {
      append: false,
      mode: 'remote',
      page: remoteResult.page,
      pageSize: remoteResult.pageSize,
      total: remoteResult.total,
      hasMore: remoteResult.hasMore,
      query,
      sort: appState.searchSort
    });
    if (openResultPage) {
      openSearchResultSheet(query);
    }
    return;
  }

  const result = sortMarketResults(searchMarketPosts(query), appState.searchSort);
  renderMarketResults(result, {
    append: false,
    mode: 'local',
    page: 1,
    pageSize: SEARCH_PAGE_SIZE,
    total: result.length,
    hasMore: false,
    query,
    sort: appState.searchSort
  });
  if (openResultPage) {
    openSearchResultSheet(query);
  }
}

function scrollBottom(node) {
  if (!node) {
    return;
  }
  node.scrollTop = node.scrollHeight;
}

function openSearchResultSheet(query = '') {
  if (!searchResultSheet || !searchResultMask) {
    return;
  }
  if (searchResultTitle) {
    searchResultTitle.textContent = '搜索结果';
  }
  if (searchResultSub) {
    searchResultSub.textContent = query ? `关键词：${query}` : '关键词';
  }
  renderVisibleSearchResults();
  searchResultSheet.hidden = false;
  searchResultMask.hidden = true;
}

function buildPagerItems(page, totalPages) {
  const items = [];
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i += 1) {
      items.push(i);
    }
    return items;
  }

  items.push(1);
  if (page > 4) {
    items.push('...');
  }
  const start = Math.max(2, page - 1);
  const end = Math.min(totalPages - 1, page + 1);
  for (let i = start; i <= end; i += 1) {
    items.push(i);
  }
  if (page < totalPages - 3) {
    items.push('...');
  }
  items.push(totalPages);
  return items;
}

function updateSearchPager() {
  if (!searchPageNumbers || !searchPagePrevBtn || !searchPageNextBtn) {
    return;
  }
  const isRemoteSource = searchResultState.source === 'remote';
  const page = Math.max(1, Number(searchResultState.page || 1));
  const pageSize = isRemoteSource ? Number(searchResultState.pageSize || 10) : SEARCH_PAGE_VIEW_SIZE;
  const total = isRemoteSource
    ? Math.max(Number(searchResultState.total || 0), (searchResultState.all || []).length)
    : (searchResultState.all || []).length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  searchPagePrevBtn.disabled = page <= 1;
  if (isRemoteSource) {
    searchPageNextBtn.disabled = !Boolean(searchResultState.hasMore);
  } else {
    searchPageNextBtn.disabled = page >= totalPages;
  }

  searchPageNumbers.innerHTML = '';
  const items = buildPagerItems(page, totalPages);
  items.forEach((item) => {
    if (item === '...') {
      const span = document.createElement('span');
      span.className = 'pager-ellipsis';
      span.textContent = '...';
      searchPageNumbers.appendChild(span);
      return;
    }
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `pager-number${item === page ? ' is-active' : ''}`;
    btn.textContent = String(item);
    btn.dataset.page = String(item);
    searchPageNumbers.appendChild(btn);
  });
}

async function goSearchPage(nextPage) {
  const page = Math.max(1, Number(nextPage || 1));
  const isRemoteSource = searchResultState.source === 'remote';
  if (isRemoteSource) {
    searchResultState.loadingMore = true;
    renderVisibleSearchResults();
    try {
      const remoteResult = await apiAdapter.searchPosts(searchResultState.query, searchResultState.sort, {
        page,
        pageSize: searchResultState.pageSize || 30
      });
      if (!remoteResult || !Array.isArray(remoteResult.items)) {
        notifyApiIssue('翻页失败，请稍后再试');
        return;
      }
      renderMarketResults(remoteResult.items, {
        append: false,
        mode: 'remote',
        page: remoteResult.page,
        pageSize: remoteResult.pageSize,
        total: remoteResult.total,
        hasMore: remoteResult.hasMore,
        query: searchResultState.query,
        sort: searchResultState.sort
      });
    } finally {
      searchResultState.loadingMore = false;
      renderVisibleSearchResults();
    }
  } else {
    searchResultState.page = page;
    renderVisibleSearchResults();
  }
}

function openWechatAuthPage() {
  openSubpageSheet({
    title: '账号互通',
    subtitle: '小程序与网页端共用同一账号',
    body: `
      <div class="wechat-auth-panel">
        <div class="wechat-auth-hero">
          <strong>微信互通登录</strong>
          <p>网页端会接入你在小程序里的同一个账号，帖子、收藏、消息和知识对话记录都会保持联通。</p>
        </div>
        <div class="wechat-auth-steps">
          <div class="wechat-auth-step"><span>1</span><p>打开小程序“我的”页，进入“网页互通登录”。</p></div>
          <div class="wechat-auth-step"><span>2</span><p>复制小程序生成的一次性登录码。</p></div>
          <div class="wechat-auth-step"><span>3</span><p>把登录码粘贴到这里，完成网页端登录。</p></div>
        </div>
        <input id="webLoginCodeInput" type="text" maxlength="12" placeholder="请输入小程序生成的登录码" />
        <div class="wechat-auth-benefits">
          <span class="wechat-auth-benefit">同账号</span>
          <span class="wechat-auth-benefit">同收藏</span>
          <span class="wechat-auth-benefit">同消息</span>
          <span class="wechat-auth-benefit">同知识记录</span>
        </div>
      </div>
    `,
    actionLabel: '登录网页',
    action: () => {
      const input = subpageBody ? subpageBody.querySelector('#webLoginCodeInput') : null;
      const code = String(input ? input.value : '').trim();
      if (!code) {
        showToast('请先输入登录码');
        return false;
      }
      void (async () => {
        const data = await apiAdapter.exchangeWebLoginCode(code);
        if (!data || !appState.clientAuth || !appState.clientAuth.token) {
          showToast('登录码无效或已过期');
          return;
        }
        closeSubpageSheet();
        await hydrateRemoteState();
        showToast('网页账号已与小程序互通');
      })();
      return false;
    }
  });
}

async function openMyPostsPage() {
  const remote = await apiAdapter.fetchMyPosts();
  const local = feedPosts.filter((post) => String(post.author || '').includes('@我'));
  const items = Array.isArray(remote) && remote.length ? remote : local;
  openSubpageListPage({
    title: '我的帖子',
    subtitle: '个人中心',
    description: '展示你发布过的帖子，支持进入详情查看评论。',
    items,
    sourceType: 'feed',
    emptyText: '你还没有发布过帖子'
  });
}

async function openLikedPostsPage() {
  const remote = await apiAdapter.fetchLikedPosts();
  const local = feedPosts.filter((post) => Boolean(post.liked) || likedPostIds.has(String(post.id)));
  const items = Array.isArray(remote) && remote.length ? remote : local;
  openSubpageListPage({
    title: '我的点赞',
    subtitle: '个人中心',
    description: '展示你点赞过的帖子，支持进入详情查看评论。',
    items,
    sourceType: 'feed',
    emptyText: '暂无点赞记录'
  });
}

function appendBubble(container, role, text, meta = null) {
  if (!container) {
    return null;
  }

  const bubble = document.createElement('article');
  bubble.className = `bubble ${role}`;

  const roleLine = document.createElement('p');
  roleLine.className = 'bubble-role';
  roleLine.textContent = role === 'user' ? '我' : role === 'assistant' ? '校园助手' : '系统';

  const textLine = document.createElement('p');
  textLine.className = 'bubble-text';
  textLine.textContent = text || '';

  bubble.append(roleLine, textLine);

  if (meta) {
    const related = Array.isArray(meta.relatedAnswers) && meta.relatedAnswers.length
      ? meta.relatedAnswers.slice(0, 5)
      : (Array.isArray(meta.citations)
        ? meta.citations.slice(0, 5).map((item, index) => ({
            id: String(item.id || `src-${index}`),
            title: String(item.title || `相关来源 ${index + 1}`),
            snippet: '',
            sourceType: String(item.sourceType || 'kb'),
            jumpUrl: String(item.jumpUrl || ''),
            score: 0
          }))
        : []);

    const detailWrap = document.createElement('div');
    detailWrap.className = 'qa-detail-wrap';
    const detailId = `qa-detail-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

    const detailToggle = document.createElement('button');
    detailToggle.type = 'button';
    detailToggle.className = 'qa-detail-toggle';
    detailToggle.dataset.qaToggleId = detailId;
    const collapsedText = related.length ? `查看详情（相关内容 ${related.length}）` : '查看详情';
    detailToggle.dataset.collapsedText = collapsedText;
    detailToggle.dataset.expandedText = '收起详情';
    detailToggle.textContent = collapsedText;

    const detailPanel = document.createElement('div');
    detailPanel.className = 'qa-detail-panel';
    detailPanel.dataset.qaDetailId = detailId;
    detailPanel.hidden = true;

    if (related.length) {
      const list = document.createElement('div');
      list.className = 'qa-related-list';
      related.forEach((item, index) => {
        const row = document.createElement('article');
        row.className = 'qa-related-item';

        const title = document.createElement('h6');
        title.textContent = `${index + 1}. ${String(item.title || `相关内容 ${index + 1}`)}`;

        const snippet = document.createElement('p');
        snippet.textContent = String(item.snippet || '').trim() || '点击下方按钮可跳转到源内容。';

        const footer = document.createElement('div');
        footer.className = 'qa-related-footer';
        const sourceMeta = document.createElement('small');
        sourceMeta.textContent = item.score > 0
          ? `${String(item.sourceType || 'kb')} · 匹配分 ${Number(item.score).toFixed(3)}`
          : String(item.sourceType || 'kb');

        const jump = document.createElement('button');
        jump.type = 'button';
        jump.className = 'source-link-btn';
        jump.dataset.sourceOpen = '1';
        jump.dataset.sourceType = String(item.sourceType || 'kb');
        jump.dataset.jumpUrl = String(item.jumpUrl || '');
        jump.dataset.sourceId = String(item.id || `src-${index}`);
        jump.textContent = '打开源内容';

        footer.append(sourceMeta, jump);
        row.append(title, snippet, footer);
        list.appendChild(row);
      });
      detailPanel.appendChild(list);
    } else {
      const empty = document.createElement('p');
      empty.className = 'qa-detail-empty';
      empty.textContent = '当前回答未返回可跳转的相关来源。';
      detailPanel.appendChild(empty);
    }

    detailWrap.append(detailToggle, detailPanel);
    bubble.appendChild(detailWrap);
  }

  container.appendChild(bubble);
  scrollBottom(container);

  return textLine;
}

function appendWikiBubble(container, role, text, meta = null) {
  if (!container) {
    return null;
  }

  const bubble = document.createElement('article');
  bubble.className = `bubble ${role}`;

  const roleLine = document.createElement('p');
  roleLine.className = 'bubble-role';
  roleLine.textContent = role === 'user' ? '我' : role === 'assistant' ? '校园助手' : '系统';

  const textLine = document.createElement('p');
  textLine.className = 'bubble-text';
  textLine.textContent = text || '';

  bubble.append(roleLine, textLine);

  if (meta) {
    const related = Array.isArray(meta.relatedAnswers) && meta.relatedAnswers.length
      ? meta.relatedAnswers.slice(0, 5)
      : (Array.isArray(meta.citations)
        ? meta.citations.slice(0, 5).map((item, index) => ({
            id: String(item.id || `src-${index}`),
            title: String(item.title || `相关来源 ${index + 1}`),
            snippet: '',
            sourceType: String(item.sourceType || 'kb'),
            jumpUrl: String(item.jumpUrl || ''),
            score: 0
          }))
        : []);

    const detailWrap = document.createElement('div');
    detailWrap.className = 'qa-detail-wrap';
    const detailId = `qa-detail-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

    const detailToggle = document.createElement('button');
    detailToggle.type = 'button';
    detailToggle.className = 'qa-detail-toggle';
    detailToggle.dataset.qaToggleId = detailId;
    detailToggle.dataset.collapsedText = related.length ? `查看详情（相关内容 ${related.length}）` : '查看详情';
    detailToggle.dataset.expandedText = '收起详情';
    detailToggle.setAttribute('aria-expanded', 'false');
    detailToggle.textContent = detailToggle.dataset.collapsedText;

    wikiDetailRegistry.set(detailId, {
      title: related.length > 1 ? `相关内容 ${related.length} 条` : '相关内容',
      items: related.map((item, index) => ({
        id: String(item.id || `src-${index}`),
        title: String(item.title || `相关内容 ${index + 1}`),
        snippet: String(item.snippet || '').trim(),
        sourceType: String(item.sourceType || 'kb'),
        jumpUrl: String(item.jumpUrl || ''),
        score: Number(item.score ?? 0)
      }))
    });

    detailWrap.appendChild(detailToggle);
    bubble.appendChild(detailWrap);
  }

  container.appendChild(bubble);
  scrollBottom(container);

  return textLine;
}

function persistWikiMessage(role, text, meta = null) {
  const cleanRole = ['user', 'assistant', 'system'].includes(role) ? role : '';
  const cleanText = String(text || '').trim();
  if (!cleanRole || !cleanText) {
    return;
  }

  const cleanMeta = meta
    ? {
        route: meta.route === 'local' ? 'local' : 'cloud',
        routeLabel: String(meta.routeLabel || ''),
        source: String(meta.source || ''),
        citations: Array.isArray(meta.citations)
          ? meta.citations.slice(0, 8).map((item, index) => ({
              id: String(item.id || `src-${index}`),
              title: String(item.title || item.id || `来源${index + 1}`),
              jumpUrl: String(item.jumpUrl || ''),
              sourceType: String(item.sourceType || 'kb')
            }))
          : [],
        relatedAnswers: Array.isArray(meta.relatedAnswers)
          ? meta.relatedAnswers.slice(0, 5).map((item, index) => ({
              id: String(item.id || `rel-${index + 1}`),
              title: String(item.title || `相关答案 ${index + 1}`),
              snippet: String(item.snippet || ''),
              sourceType: String(item.sourceType || 'kb'),
              jumpUrl: String(item.jumpUrl || ''),
              score: Number(item.score ?? 0)
            }))
          : []
      }
    : null;

  const currentHistory = Array.isArray(appState.wikiHistory) ? appState.wikiHistory : [];
  appState.wikiHistory = [...currentHistory, { role: cleanRole, text: cleanText, meta: cleanMeta }].slice(-24);
  saveState();
}

function renderWikiHistory() {
  if (!wikiBoard) {
    return;
  }

  closeWikiDetailSheet();
  wikiDetailRegistry.clear();

  const history = Array.isArray(appState.wikiHistory) ? appState.wikiHistory : [];
  if (!history.length) {
    scrollBottom(wikiBoard);
    return;
  }

  wikiBoard.innerHTML = '';
  history.forEach((item) => {
    appendWikiBubble(wikiBoard, item.role, item.text, item.meta);
  });
}

function streamText(target, content, onDone) {
  if (!target) {
    return;
  }

  let index = 0;
  const timer = setInterval(() => {
    target.textContent += content[index] || '';
    index += 1;

    if (index >= content.length) {
      clearInterval(timer);
      if (onDone) {
        onDone();
      }
    }
  }, 18);
}

function decideKnowledgeAnswer(query) {
  if (/成绩|绩点|学分|课表|考试/.test(query)) {
    return {
      route: 'local',
      routeLabel: '教务答复',
      source: '来源：课程与教务信息',
      text: '已通过本地隐私通道查询。你本学期当前绩点为 3.57，建议优先提升高学分课程成绩，以更快拉升总绩点。'
    };
  }

  if (/教务处|下班|办公/.test(query)) {
    return {
      route: 'cloud',
      routeLabel: '校园问答',
      source: '来源：办事指引与社区经验',
      text: '教务大厅常规工作时间为工作日 8:30-17:30。遇到调课周或考试周，窗口值班可能延长，建议出发前再确认通知。'
    };
  }

  if (/食堂|排队|窗口/.test(query)) {
    return {
      route: 'cloud',
      routeLabel: '经验汇总',
      source: '来源：校园帖子与互动内容',
      text: '午高峰建议优先北门清汤窗口，体感排队更短；若想吃麻辣烫，11:50 前到达体验更稳定。'
    };
  }

  if (/自习|教室|安静|图书馆/.test(query)) {
    return {
      route: 'cloud',
      routeLabel: '校园问答',
      source: '来源：办事指引与社区经验',
      text: '今晚推荐 A1-307（近图书馆，插座多）和 A2-402（更安静）。如果你需要长时段复习，优先 A2-402。'
    };
  }

  return {
    route: 'cloud',
    routeLabel: '综合建议',
    source: '来源：校园公开信息与经验内容',
    text: '已检索校园知识库。你可以补充“时间段 + 地点 + 目标”，例如“今晚 19 点后 + 图书馆附近 + 安静有插座”，我会给出更精确建议。'
  };
}

function syncKnowledgeComposerUi() {
  if (wikiQuickRow) {
    wikiQuickRow.hidden = !KNOWLEDGE_UI_CONFIG.showQuickPrompts;
  }
  if (wikiDeepThinkingToggle) {
    wikiDeepThinkingToggle.checked = Boolean(appState.wikiDeepThinking);
  }
}

async function resolveKnowledgeAnswer(query, options = {}) {
  const deepThinkingEnabled = Boolean(options.deepThinking);
  const remoteAnswer = await apiAdapter.askKnowledge(query, appState.wikiHistory.slice(-8), {
    deepThinking: deepThinkingEnabled
  });
  if (remoteAnswer && remoteAnswer.text) {
    return remoteAnswer;
  }
  return {
    route: 'cloud',
    routeLabel: '未找到充分依据',
    source: '来源：当前知识库',
    text: '当前知识库未检索到足够依据，已拒绝生成臆测答案。请补充知识库文档或更换问题。',
    citations: [],
    relatedAnswers: []
  };
}

async function sendKnowledgeMessage(text) {
  if (!wikiBoard) {
    return;
  }

  closeWikiDetailSheet();

  if (isWikiResponding) {
    showToast('请等待上一条回答完成');
    return;
  }

  const query = String(text || '').trim();
  if (!query) {
    return;
  }

  appendWikiBubble(wikiBoard, 'user', query);
  persistWikiMessage('user', query);

  isWikiResponding = true;
  try {
    const answer = await resolveKnowledgeAnswer(query, {
      deepThinking: Boolean(appState.wikiDeepThinking)
    });
    const answerMeta = {
      route: answer.route,
      routeLabel: answer.routeLabel,
      source: answer.source,
      citations: Array.isArray(answer.citations) ? answer.citations : [],
      relatedAnswers: Array.isArray(answer.relatedAnswers) ? answer.relatedAnswers.slice(0, 5) : []
    };

    const target = appendWikiBubble(wikiBoard, 'assistant', '', answerMeta);
    persistWikiMessage('assistant', answer.text, answerMeta);

    streamText(target, answer.text, () => {
      isWikiResponding = false;
      scrollBottom(wikiBoard);
    });
  } catch (error) {
    isWikiResponding = false;
    showToast('知识库回答失败，请稍后再试');
  }
}

function openKnowledgeSource(sourceType, jumpUrl, sourceId) {
  const safeType = String(sourceType || 'kb');
  const safeJump = String(jumpUrl || '').trim();
  const safeId = String(sourceId || '');

  if (safeJump.includes('#post=')) {
    const postId = safeJump.split('#post=')[1] || '';
    if (postId) {
      locateOriginalPost(postId, 'feed', safeId || postId);
      return;
    }
  }

  if ((safeType === 'feed' || safeType === 'search') && safeId) {
    locateOriginalPost(safeId, safeType, safeId || '来源内容');
    return;
  }

  if (safeType === 'post' && /^p-\d+$/i.test(safeId)) {
    locateOriginalPost(safeId, 'feed', safeId);
    return;
  }

  if (/^post:\/\/p-\d+$/i.test(safeJump)) {
    const postId = safeJump.replace(/^post:\/\//i, '');
    locateOriginalPost(postId, 'feed', safeId || postId);
    return;
  }

  if (safeJump.startsWith('/')) {
    window.open(buildApiUrl(safeJump), '_blank', 'noopener');
    return;
  }

  if (safeJump.startsWith('http://') || safeJump.startsWith('https://')) {
    window.open(safeJump, '_blank', 'noopener');
    return;
  }

  showToast(`来源片段：${safeId || '未命名来源'}`);
}

function setWikiDetailTriggerState(trigger, expanded) {
  if (!trigger) {
    return;
  }
  const expandedText = String(trigger.dataset.expandedText || '收起详情');
  const collapsedText = String(trigger.dataset.collapsedText || '查看详情');
  trigger.textContent = expanded ? expandedText : collapsedText;
  trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
}

function closeWikiDetailSheet() {
  if (!wikiDetailSheet || !wikiDetailMask) {
    return;
  }
  wikiDetailSheet.hidden = true;
  wikiDetailMask.hidden = true;
  if (activeWikiDetailTrigger) {
    setWikiDetailTriggerState(activeWikiDetailTrigger, false);
  }
  activeWikiDetailId = '';
  activeWikiDetailTrigger = null;
}

function openWikiDetailSheet(detailId, triggerBtn) {
  if (!wikiDetailSheet || !wikiDetailMask || !wikiDetailList || !wikiDetailTitle) {
    return;
  }

  const record = wikiDetailRegistry.get(String(detailId || ''));
  if (!record) {
    return;
  }

  if (activeWikiDetailId === detailId && !wikiDetailSheet.hidden) {
    closeWikiDetailSheet();
    return;
  }

  if (activeWikiDetailTrigger && activeWikiDetailTrigger !== triggerBtn) {
    setWikiDetailTriggerState(activeWikiDetailTrigger, false);
  }

  wikiDetailTitle.textContent = String(record.title || '相关内容');
  wikiDetailList.innerHTML = '';

  const items = Array.isArray(record.items) ? record.items : [];
  if (!items.length) {
    const empty = document.createElement('p');
    empty.className = 'qa-detail-empty';
    empty.textContent = '当前回答暂未返回可跳转的来源。';
    wikiDetailList.appendChild(empty);
  } else {
    items.forEach((item, index) => {
      const article = document.createElement('article');
      article.className = 'wiki-detail-item';

      const title = document.createElement('h5');
      title.textContent = `${index + 1}. ${String(item.title || `相关内容 ${index + 1}`)}`;

      const snippet = document.createElement('p');
      snippet.textContent = String(item.snippet || '').trim() || '点击下方按钮可打开来源内容。';

      const meta = document.createElement('div');
      meta.className = 'wiki-detail-meta';
      meta.textContent = Number(item.score) > 0
        ? `${String(item.sourceType || 'kb')} · 匹配分 ${Number(item.score).toFixed(3)}`
        : String(item.sourceType || 'kb');

      const actions = document.createElement('div');
      actions.className = 'wiki-detail-actions';

      const jump = document.createElement('button');
      jump.type = 'button';
      jump.className = 'source-link-btn';
      jump.dataset.sourceOpen = '1';
      jump.dataset.sourceType = String(item.sourceType || 'kb');
      jump.dataset.jumpUrl = String(item.jumpUrl || '');
      jump.dataset.sourceId = String(item.id || `src-${index}`);
      jump.textContent = '打开来源内容';

      actions.appendChild(jump);
      article.append(title, snippet, meta, actions);
      wikiDetailList.appendChild(article);
    });
  }

  wikiDetailSheet.hidden = false;
  wikiDetailMask.hidden = false;
  activeWikiDetailId = String(detailId || '');
  activeWikiDetailTrigger = triggerBtn || null;
  setWikiDetailTriggerState(activeWikiDetailTrigger, true);
}

function closeEduSheet() {
  if (!eduSheet || !eduSheetMask) {
    return;
  }
  eduSheet.hidden = true;
  eduSheetMask.hidden = true;
  activeEduAction = '';
}

function getEduConfig(action = 'hall') {
  return EDU_ACTION_CONFIG[action] || EDU_ACTION_CONFIG.hall;
}

function getEduWeekdayLabel(weekday = 1) {
  return ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][Math.max(0, Math.min(6, Number(weekday || 1) - 1))] || '待定';
}

function buildEduWeeks(totalWeeks = 18) {
  const safeTotal = Math.max(1, Number(totalWeeks || 18));
  return Array.from({ length: safeTotal }, (_, index) => index + 1);
}

function normalizeEduState(overview) {
  const safeOverview = overview || {};
  const terms = Array.isArray(safeOverview.availableTerms) ? safeOverview.availableTerms : [];
  const campuses = Array.isArray(safeOverview.campuses) ? safeOverview.campuses : [];
  const currentWeek = Math.max(1, Number(safeOverview.currentWeek || 1));
  const totalWeeks = Math.max(currentWeek, Number(safeOverview.totalWeeks || 18));

  if (!terms.includes(eduSheetState.activeTerm)) {
    eduSheetState.activeTerm = String(safeOverview.term || terms[0] || '');
  }
  if (!Number.isFinite(Number(eduSheetState.activeWeek)) || Number(eduSheetState.activeWeek) < 1 || Number(eduSheetState.activeWeek) > totalWeeks) {
    eduSheetState.activeWeek = currentWeek;
  }
  if (!campuses.includes(eduSheetState.activeCampus)) {
    eduSheetState.activeCampus = String(campuses[0] || EDU_DEFAULT_CAMPUS);
  }
  if (!eduSheetState.activeBuilding) {
    eduSheetState.activeBuilding = EDU_ALL_BUILDINGS;
  }
}

function buildEduHallStats(overview, exams = [], freePayload = { items: [] }) {
  const upcoming = Array.isArray(exams)
    ? exams.filter((item) => String(item.examStatus || '').toLowerCase() !== 'finished').length
    : 0;
  const recommended = Array.isArray(freePayload.items)
    ? freePayload.items.filter((item) => Boolean(item.recommended)).length
    : 0;
  return [
    { label: '累计学分', value: Number(overview.totalScore || 0).toFixed(1), action: 'grades' },
    { label: '平均绩点', value: Number(overview.gpa || 0).toFixed(2), action: 'grades' },
    { label: '待考安排', value: String(upcoming), action: 'exams' },
    { label: '推荐空教室', value: String(recommended), action: 'freeClassrooms' }
  ];
}

function buildEduGradeStats(overview, grades) {
  return [
    { label: '累计学分', value: Number(overview.totalScore || 0).toFixed(1), action: 'grades' },
    { label: '学期学分', value: Number(grades.termCredit || 0).toFixed(1), action: 'grades' },
    { label: '学期绩点', value: Number(grades.termGpa || 0).toFixed(2), action: 'grades' },
    { label: '已通过', value: String(grades.passedCount || 0), action: 'grades' }
  ];
}

function buildEduScheduleStats(schedule) {
  const items = Array.isArray(schedule.items) ? schedule.items : [];
  const weekdays = new Set(items.map((item) => Number(item.weekday || 0)).filter(Boolean));
  const currentDay = new Date().getDay() || 7;
  const todayCount = items.filter((item) => Number(item.weekday || 0) === currentDay).length;
  return [
    { label: '当前周次', value: `第 ${Number(schedule.weekNo || 1)} 周`, action: 'schedule' },
    { label: '本周课程', value: String(items.length), action: 'schedule' },
    { label: '上课天数', value: String(weekdays.size), action: 'schedule' },
    { label: '今日课程', value: String(todayCount), action: 'schedule' }
  ];
}

function buildEduExamStats(exams = []) {
  const upcoming = Array.isArray(exams)
    ? exams.filter((item) => String(item.examStatus || '').toLowerCase() !== 'finished').length
    : 0;
  const finished = Math.max(0, (Array.isArray(exams) ? exams.length : 0) - upcoming);
  return [
    { label: '全部安排', value: String(Array.isArray(exams) ? exams.length : 0), action: 'exams' },
    { label: '待考试', value: String(upcoming), action: 'exams' },
    { label: '已结束', value: String(finished), action: 'exams' },
    { label: '当前学期', value: '已同步', action: 'exams' }
  ];
}

function buildEduFreeStats(payload, activeBuildingLabel = '全部教学楼', visibleItems = []) {
  return [
    { label: '当前校区', value: String(payload.campus || EDU_DEFAULT_CAMPUS).replace('校区', ''), action: 'freeClassrooms' },
    { label: '公共教学楼', value: String(Array.isArray(payload.buildings) ? payload.buildings.length : 0), action: 'freeClassrooms' },
    { label: '当前查看', value: String(activeBuildingLabel || '全部教学楼'), action: 'freeClassrooms' },
    { label: '教室数量', value: String(Array.isArray(visibleItems) ? visibleItems.length : 0), action: 'freeClassrooms' }
  ];
}

function renderEduSummaryGrid(cards = []) {
  return `
    <section class="edu-overview-grid">
      ${(Array.isArray(cards) ? cards : []).map((item) => `
        <button class="edu-kpi edu-kpi-btn" type="button" data-edu-nav="${escapeHtml(item.action || activeEduAction || 'hall')}">
          <strong>${escapeHtml(item.value || '')}</strong>
          <span>${escapeHtml(item.label || '')}</span>
        </button>
      `).join('')}
    </section>
  `;
}

function renderEduHero(overview, action) {
  const config = getEduConfig(action);
  return `
    <article class="edu-hero-panel">
      <div class="edu-hero-head">
        <div>
          <span class="edu-hero-brow">${escapeHtml(config.brow)}</span>
          <h5>${escapeHtml(config.title)}</h5>
          <p>${escapeHtml(config.subtitle)}</p>
        </div>
        ${action !== 'hall' ? '<button class="btn-light edu-hall-btn" type="button" data-edu-nav="hall">大厅总览</button>' : ''}
      </div>
      <div class="edu-identity-card">
        <div class="edu-identity-main">
          <strong>${escapeHtml(overview.studentName || '赵毅')}</strong>
          <span>学号 ${escapeHtml(overview.studentId || '-')} · ${escapeHtml(overview.term || '')}</span>
        </div>
        <div class="edu-chip-row">
          <span class="edu-chip">受控会话</span>
          <span class="edu-chip">仅本人可见</span>
          <span class="edu-chip">不公开检索</span>
        </div>
      </div>
    </article>
  `;
}

function renderEduState(type, message) {
  const safeMsg = escapeHtml(message || '');
  return `
    <article class="edu-list-card">
      <div class="edu-list-head">
        <div>
          <h5>${escapeHtml(type)}</h5>
          <p>${safeMsg}</p>
        </div>
      </div>
      <button class="btn-light edu-retry-btn" data-edu-retry="1">重新加载</button>
    </article>
  `;
}

function renderEduSelectorRow(label, currentLabel, name, options = [], selectedValue = '') {
  return `
    <article class="edu-filter-row">
      <div class="edu-filter-copy">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(currentLabel)}</strong>
      </div>
      <label class="edu-select-wrap">
        <select class="edu-select" data-edu-select="${escapeHtml(name)}">
          ${(Array.isArray(options) ? options : []).map((item) => `
            <option value="${escapeHtml(item.value)}"${String(item.value) === String(selectedValue) ? ' selected' : ''}>${escapeHtml(item.label)}</option>
          `).join('')}
        </select>
        <span class="edu-select-arrow" aria-hidden="true">⌄</span>
      </label>
    </article>
  `;
}

function renderEduModuleGrid() {
  const modules = [
    { action: 'grades', icon: '绩', badge: '全学期', title: '成绩查询', copy: '查看所有学期成绩与绩点变化' },
    { action: 'schedule', icon: '课', badge: '1-18 周', title: '课表查看', copy: '切换本学期任意周次课表' },
    { action: 'freeClassrooms', icon: '空', badge: '三校区', title: '空教室', copy: '按校区和教学楼查看全部教室' },
    { action: 'exams', icon: '考', badge: '提醒', title: '考试安排', copy: '统一查看考试时间和地点' }
  ];
  return `
    <article class="edu-panel">
      <div class="edu-panel-head">
        <h5>快捷入口</h5>
        <p>每个模块都可以直接点进去，先看状态，再进入对应详情。</p>
      </div>
      <div class="edu-module-grid">
        ${modules.map((item) => `
          <button class="edu-module-btn" type="button" data-edu-nav="${item.action}">
            <span class="edu-module-icon-box">${item.icon}</span>
            <div class="edu-module-copy-block">
              <strong>${item.title}</strong>
              <small>${item.copy}</small>
            </div>
            <em>${item.badge}</em>
          </button>
        `).join('')}
      </div>
    </article>
  `;
}

function renderEduListCard({ eyebrow = '', title = '', meta = '', extra = '', value = '', tags = [], progress = null }) {
  return `
    <article class="edu-list-card">
      <div class="edu-list-head">
        <div>
          ${eyebrow ? `<span class="edu-list-brow">${escapeHtml(eyebrow)}</span>` : ''}
          <h5>${escapeHtml(title)}</h5>
          ${meta ? `<p>${escapeHtml(meta)}</p>` : ''}
        </div>
        ${value ? `<strong class="edu-list-score">${escapeHtml(value)}</strong>` : ''}
      </div>
      ${extra ? `<p class="edu-list-copy">${escapeHtml(extra)}</p>` : ''}
      ${progress !== null ? `
        <div class="edu-progress-block">
          <div class="edu-progress-track"><span style="width:${Math.max(0, Math.min(100, Number(progress || 0)))}%"></span></div>
          <p class="edu-progress-text">空闲度 ${Math.max(0, Math.min(100, Number(progress || 0)))}%</p>
        </div>
      ` : ''}
      ${Array.isArray(tags) && tags.length ? `<div class="edu-chip-row">${tags.map((tag) => `<span class="edu-badge">${escapeHtml(tag)}</span>`).join('')}</div>` : ''}
    </article>
  `;
}

function renderEduFilterPanel(action, data) {
  if (action === 'hall' || action === 'exams') {
    return '';
  }

  if (action === 'grades') {
    return `
      <article class="edu-panel">
        <div class="edu-panel-head">
          <h5>查看筛选</h5>
          <p>支持自由切换所有学期。</p>
        </div>
        ${renderEduSelectorRow('当前学期', data.activeTermLabel, 'term', data.termOptions, data.activeTermValue)}
      </article>
    `;
  }

  if (action === 'schedule') {
    return `
      <article class="edu-panel">
        <div class="edu-panel-head">
          <h5>查看筛选</h5>
          <p>支持自由切换第 1 到 18 周。</p>
        </div>
        ${renderEduSelectorRow('当前周次', data.activeWeekLabel, 'week', data.weekOptions, data.activeWeekValue)}
      </article>
    `;
  }

  return `
    <article class="edu-panel">
      <div class="edu-panel-head">
        <h5>查看筛选</h5>
        <p>按校区和教学楼自由切换，再查看该楼全部教室。</p>
      </div>
      ${renderEduSelectorRow('当前校区', data.activeCampusLabel, 'campus', data.campusOptions, data.activeCampusValue)}
      ${renderEduSelectorRow('当前教学楼', data.activeBuildingLabel, 'building', data.buildingOptions, data.activeBuildingValue)}
      <div class="edu-building-grid"${data.buildingCards.length ? '' : ' hidden'}>
        ${data.buildingCards.map((item) => `
          <button class="edu-building-btn${item.active ? ' is-active' : ''}" type="button" data-edu-building="${escapeHtml(item.value)}">
            <strong>${escapeHtml(item.title)}</strong>
            <span>${escapeHtml(item.copy)}</span>
            <em>${escapeHtml(item.badge)}</em>
          </button>
        `).join('')}
      </div>
    </article>
  `;
}

function renderEduShell(action, overview, summaryCards, filterMarkup, listTitle, listCards, footerNote) {
  return `
    <div class="edu-shell">
      ${renderEduHero(overview, action)}
      ${renderEduSummaryGrid(summaryCards)}
      ${filterMarkup}
      <article class="edu-panel">
        <div class="edu-panel-head">
          <h5>${escapeHtml(listTitle)}</h5>
        </div>
        ${listCards}
      </article>
      <article class="edu-panel edu-note-panel">
        <p>${escapeHtml(footerNote)}</p>
      </article>
    </div>
  `;
}

function renderEduHallView(overview, exams, freePayload) {
  const listCards = [
    renderEduListCard({
      eyebrow: '受控教务会话',
      title: overview.studentName || '赵毅',
      meta: `学号 ${overview.studentId || '-'} · ${overview.term || ''}`,
      extra: '网页端与小程序端使用同一套教务受控接口，数据只在本人会话内展示。',
      tags: ['受控会话', '模拟成绩', '不公开检索']
    })
  ].join('');
  return renderEduShell(
    'hall',
    overview,
    buildEduHallStats(overview, exams, freePayload),
    renderEduModuleGrid(),
    '本次会话概览',
    listCards,
    getEduConfig('hall').footerNote
  );
}

function renderEduGradesView(overview, grades) {
  const termOptions = (Array.isArray(grades.terms) ? grades.terms : []).map((item) => ({ label: item, value: item }));
  const cards = (Array.isArray(grades.items) ? grades.items : []).map((item) => renderEduListCard({
    eyebrow: '课程成绩',
    title: item.courseName,
    meta: `${item.credit} 学分 · 绩点 ${Number(item.gradePoint || 0).toFixed(1)}`,
    extra: item.score >= 60 ? '当前课程成绩已归档，可继续关注学分与绩点变化。' : '建议后续重点关注补考或重修安排。',
    value: String(item.score),
    tags: [item.status === 'passed' ? '已通过' : '待关注']
  })).join('') || renderEduState('暂无成绩', '当前学期暂无成绩数据。');

  return renderEduShell(
    'grades',
    overview,
    buildEduGradeStats(overview, grades),
    renderEduFilterPanel('grades', {
      activeTermLabel: grades.term || overview.term || '',
      activeTermValue: grades.term || overview.term || '',
      termOptions
    }),
    `课程成绩 · ${grades.term || overview.term || '当前学期'}`,
    cards,
    getEduConfig('grades').footerNote
  );
}

function renderEduScheduleView(overview, schedule) {
  const weekOptions = (Array.isArray(schedule.weeks) ? schedule.weeks : []).map((item) => ({
    label: `第 ${Number(item)} 周`,
    value: String(item)
  }));
  const cards = (Array.isArray(schedule.items) ? schedule.items : []).map((item) => renderEduListCard({
    eyebrow: `${getEduWeekdayLabel(item.weekday)} · 第 ${item.section}${Number(item.sectionSpan || 1) > 1 ? `-${Number(item.section || 1) + Number(item.sectionSpan || 1) - 1}` : ''} 节`,
    title: item.courseName,
    meta: `${item.location} · ${item.teacher}`,
    extra: item.weeks,
    value: getEduWeekdayLabel(item.weekday),
    tags: [item.location, item.teacher]
  })).join('') || renderEduState('暂无课表', '当前周次暂无课程安排。');

  return renderEduShell(
    'schedule',
    overview,
    buildEduScheduleStats(schedule),
    renderEduFilterPanel('schedule', {
      activeWeekLabel: `第 ${Number(schedule.weekNo || 1)} 周`,
      activeWeekValue: String(schedule.weekNo || 1),
      weekOptions
    }),
    `${schedule.term || overview.term || ''} · 第 ${Number(schedule.weekNo || 1)} 周课表`,
    cards,
    getEduConfig('schedule').footerNote
  );
}

function renderEduFreeClassroomsView(overview, payload) {
  const buildingCards = [
    {
      value: EDU_ALL_BUILDINGS,
      title: '全部教学楼',
      copy: `查看本校区全部 ${(Array.isArray(payload.items) ? payload.items.length : 0)} 间公共教室`,
      badge: `${Array.isArray(payload.buildings) ? payload.buildings.length : 0} 栋`,
      active: eduSheetState.activeBuilding === EDU_ALL_BUILDINGS
    }
  ];
  (Array.isArray(payload.buildings) ? payload.buildings : []).forEach((building) => {
    const scoped = (payload.items || []).filter((item) => String(item.building || '') === String(building));
    const recommendedCount = scoped.filter((item) => Boolean(item.recommended)).length;
    buildingCards.push({
      value: String(building),
      title: String(building),
      copy: recommendedCount > 0 ? `低占用推荐 ${recommendedCount} 间` : '查看该楼全部教室',
      badge: `${scoped.length} 间`,
      active: String(eduSheetState.activeBuilding || '') === String(building)
    });
  });

  const activeBuildingLabel = eduSheetState.activeBuilding === EDU_ALL_BUILDINGS ? '全部教学楼' : eduSheetState.activeBuilding;
  const visibleItems = (Array.isArray(payload.items) ? payload.items : [])
    .filter((item) => eduSheetState.activeBuilding === EDU_ALL_BUILDINGS || String(item.building || '') === String(eduSheetState.activeBuilding || ''))
    .slice()
    .sort((left, right) => {
      if (Boolean(left.recommended) !== Boolean(right.recommended)) {
        return Number(Boolean(right.recommended)) - Number(Boolean(left.recommended));
      }
      return Number(left.idlePercent || 0) - Number(right.idlePercent || 0);
    });

  const cards = visibleItems.map((item) => renderEduListCard({
    eyebrow: item.recommended ? '优先推荐' : '教室状态',
    title: `${item.building} ${item.room}`,
    meta: `${item.campus} · 空闲度 ${item.idlePercent}%`,
    extra: Number(item.idlePercent || 0) <= 20 ? '更适合临时自习、查资料和短时复盘。' : '到达后再确认是否有临时占用变化。',
    value: `${item.idlePercent}%`,
    tags: [item.recommended ? '优先推荐' : '可选教室'],
    progress: Number(item.idlePercent || 0)
  })).join('') || renderEduState('暂无教室', '当前条件下暂无可展示教室。');

  return renderEduShell(
    'freeClassrooms',
    overview,
    buildEduFreeStats(payload, activeBuildingLabel, visibleItems),
    renderEduFilterPanel('freeClassrooms', {
      activeCampusLabel: payload.campus || EDU_DEFAULT_CAMPUS,
      activeCampusValue: payload.campus || EDU_DEFAULT_CAMPUS,
      campusOptions: (Array.isArray(payload.campuses) ? payload.campuses : []).map((item) => ({ label: item, value: item })),
      activeBuildingLabel,
      activeBuildingValue: eduSheetState.activeBuilding || EDU_ALL_BUILDINGS,
      buildingOptions: [
        { label: '全部教学楼', value: EDU_ALL_BUILDINGS },
        ...(Array.isArray(payload.buildings) ? payload.buildings : []).map((item) => ({ label: item, value: item }))
      ],
      buildingCards
    }),
    `${payload.campus || EDU_DEFAULT_CAMPUS} · ${activeBuildingLabel} 教室信息`,
    cards,
    getEduConfig('freeClassrooms').footerNote
  );
}

function renderEduExamsView(overview, exams) {
  const cards = (Array.isArray(exams) ? exams : []).map((item) => renderEduListCard({
    eyebrow: String(item.examStatus || '').toLowerCase() === 'finished' ? '已结束' : '待考试',
    title: item.courseName,
    meta: `${item.examDate} ${item.examTime}`,
    extra: `${item.examLocation} · ${item.examType}`,
    value: String(item.examStatus || '').toLowerCase() === 'finished' ? '已考' : '待考',
    tags: [item.term]
  })).join('') || renderEduState('暂无考试', '当前暂无考试安排。');

  return renderEduShell(
    'exams',
    overview,
    buildEduExamStats(exams),
    '',
    '考试清单',
    cards,
    getEduConfig('exams').footerNote
  );
}

async function renderEduAction(action) {
  const safeAction = getEduConfig(action) === EDU_ACTION_CONFIG.hall && action !== 'hall' ? 'hall' : action;
  const overview = await apiAdapter.fetchEduOverview();
  if (!overview) {
    eduSheetTitle.textContent = '教务大厅';
    eduSheetBody.innerHTML = renderEduState('加载失败', '教务接口不可用或权限失效。');
    return;
  }

  normalizeEduState(overview);
  eduSheetState.overview = overview;
  eduSheetTitle.textContent = getEduConfig(safeAction).title;
  eduSheetSub.textContent = '教务会话已连接';

  if (safeAction === 'hall') {
    const [exams, freePayload] = await Promise.all([
      apiAdapter.fetchEduExams(),
      apiAdapter.fetchEduFreeClassrooms(eduSheetState.activeCampus)
    ]);
    eduSheetBody.innerHTML = renderEduHallView(overview, Array.isArray(exams) ? exams : [], freePayload || { items: [], buildings: [] });
    return;
  }

  if (safeAction === 'grades') {
    const grades = await apiAdapter.fetchEduGrades(eduSheetState.activeTerm || overview.term);
    if (!grades) {
      eduSheetBody.innerHTML = renderEduState('暂无成绩', '当前学期未返回成绩数据。');
      return;
    }
    eduSheetState.activeTerm = String(grades.term || overview.term || '');
    eduSheetBody.innerHTML = renderEduGradesView(overview, grades);
    return;
  }

  if (safeAction === 'schedule') {
    const schedule = await apiAdapter.fetchEduSchedule(eduSheetState.activeWeek || overview.currentWeek || 1);
    if (!schedule) {
      eduSheetBody.innerHTML = renderEduState('暂无课表', '当前周次未返回课表数据。');
      return;
    }
    eduSheetState.activeWeek = Number(schedule.weekNo || overview.currentWeek || 1);
    eduSheetBody.innerHTML = renderEduScheduleView(overview, schedule);
    return;
  }

  if (safeAction === 'freeClassrooms') {
    const freePayload = await apiAdapter.fetchEduFreeClassrooms(eduSheetState.activeCampus);
    if (!freePayload) {
      eduSheetBody.innerHTML = renderEduState('暂无空教室', '暂未返回空教室数据。');
      return;
    }
    eduSheetState.activeCampus = String(freePayload.campus || eduSheetState.activeCampus || EDU_DEFAULT_CAMPUS);
    eduSheetState.buildingOptions = Array.isArray(freePayload.buildings) ? freePayload.buildings : [];
    if (!eduSheetState.buildingOptions.includes(eduSheetState.activeBuilding)) {
      eduSheetState.activeBuilding = EDU_ALL_BUILDINGS;
    }
    eduSheetBody.innerHTML = renderEduFreeClassroomsView(overview, freePayload);
    return;
  }

  const exams = await apiAdapter.fetchEduExams();
  if (!Array.isArray(exams)) {
    eduSheetBody.innerHTML = renderEduState('暂无考试', '暂未返回考试安排。');
    return;
  }
  eduSheetBody.innerHTML = renderEduExamsView(overview, exams);
}

async function openEduSheet(action = 'hall') {
  if (!eduSheet || !eduSheetMask || !eduSheetBody) {
    return;
  }

  activeEduAction = EDU_ACTION_CONFIG[action] ? action : 'hall';
  closeInboxDetailSheet();
  closeCommentSheet();
  closePostDetailSheet();
  closeSearchResultSheet();
  closeSubpageSheet();
  closeErrandPage();
  closeCrossGroupPage();
  eduSheet.hidden = false;
  eduSheetMask.hidden = true;
  eduSheetTitle.textContent = getEduConfig(activeEduAction).title;
  eduSheetSub.textContent = '教务会话已连接';
  eduSheetBody.innerHTML = '<article class="edu-list-card"><p>正在加载...</p></article>';
  await renderEduAction(activeEduAction);
}

function handleEduSheetSelectionChange(name, value) {
  const safeName = String(name || '').trim();
  const safeValue = String(value || '').trim();
  if (!safeName) {
    return;
  }

  if (safeName === 'term') {
    if (safeValue && safeValue !== String(eduSheetState.activeTerm || '')) {
      eduSheetState.activeTerm = safeValue;
      void openEduSheet('grades');
    }
    return;
  }

  if (safeName === 'week') {
    const nextWeek = Math.max(1, Number.parseInt(safeValue, 10) || 1);
    if (nextWeek !== Number(eduSheetState.activeWeek || 1)) {
      eduSheetState.activeWeek = nextWeek;
      void openEduSheet('schedule');
    }
    return;
  }

  if (safeName === 'campus') {
    if (safeValue && safeValue !== String(eduSheetState.activeCampus || EDU_DEFAULT_CAMPUS)) {
      eduSheetState.activeCampus = safeValue;
      eduSheetState.activeBuilding = EDU_ALL_BUILDINGS;
      void openEduSheet('freeClassrooms');
    }
    return;
  }

  if (safeName === 'building') {
    const nextBuilding = safeValue || EDU_ALL_BUILDINGS;
    if (nextBuilding !== String(eduSheetState.activeBuilding || EDU_ALL_BUILDINGS)) {
      eduSheetState.activeBuilding = nextBuilding;
      void openEduSheet('freeClassrooms');
    }
  }
}

function unreadCountByType(type) {
  if (appState.inboxRead[type]) {
    return 0;
  }
  return Number(inboxCounts[type] || 0);
}

function getUnreadCount() {
  return unreadCountByType('likes') + unreadCountByType('saved');
}

function updateProfileDot() {
  if (!profileTabDot) {
    return;
  }

  profileTabDot.hidden = getUnreadCount() <= 0;
}

const COMPOUND_SURNAME_PREFIXES = [
  '欧阳',
  '司马',
  '上官',
  '诸葛',
  '东方',
  '皇甫',
  '尉迟',
  '公孙',
  '慕容',
  '司徒',
  '司空',
  '夏侯',
  '令狐',
  '长孙',
  '宇文',
  '轩辕'
];

function extractSurnameForGreeting(rawName = '') {
  const cleaned = String(rawName || '').trim()
    .replace(/^@+/, '')
    .replace(/\s+/g, ' ');
  if (!cleaned) {
    return '';
  }

  const firstSegment = cleaned.split(/[·\-_()（）【】\[\]]/)[0].trim();
  if (!firstSegment) {
    return '';
  }

  const cjkOnly = firstSegment.replace(/[^\u3400-\u9fff]/g, '');
  if (cjkOnly) {
    const compound = COMPOUND_SURNAME_PREFIXES.find((prefix) => cjkOnly.startsWith(prefix));
    return compound || cjkOnly.charAt(0);
  }

  const parts = firstSegment.split(/\s+/).filter(Boolean);
  if (!parts.length) {
    return '';
  }
  if (parts.length === 1) {
    return parts[0];
  }
  return parts[parts.length - 1];
}

function buildHeaderGreeting(rawName = '') {
  const surname = extractSurnameForGreeting(rawName);
  if (!surname) {
    return '你好，同学';
  }
  return `你好，${surname}同学`;
}

function syncHeaderGreeting(preferredName = '') {
  if (!headerGreeting) {
    return;
  }
  const auth = appState && appState.clientAuth ? appState.clientAuth : {};
  const fallback = String(auth.displayName || auth.username || '').trim();
  headerGreeting.textContent = buildHeaderGreeting(preferredName || fallback);
}

function renderProfileInbox() {
  if (!profileMessageList) {
    return;
  }

  profileMessageList.innerHTML = '';

  inboxItems.forEach((item) => {
    const unread = unreadCountByType(item.id);
    const total = Number(inboxTotals[item.id] || 0);
    const subtitle = unread > 0
      ? `${item.subtitle} · ${unread} 条未读`
      : (total > 0 ? `累计 ${total} 条记录` : '暂无记录');
    const row = document.createElement('button');
    row.className = 'inbox-row';
    row.dataset.inboxId = item.id;
    row.type = 'button';
    row.innerHTML = `
      <div class="inbox-left">
        <span class="inbox-title">${item.title}</span>
        <span class="inbox-sub">${subtitle}</span>
      </div>
      <div class="inbox-right">
        <span class="inbox-count">${total}</span>
        ${unread > 0 ? '<span class="inbox-dot" aria-hidden="true"></span>' : ''}
      </div>
    `;
    profileMessageList.appendChild(row);
  });
}

function applyProfileSummary(summary) {
  if (!summary || typeof summary !== 'object') {
    return;
  }

  if (profileName && summary.name) {
    profileName.textContent = summary.name;
  }
  syncHeaderGreeting(summary.name || '');
  if (profileMeta && summary.meta) {
    profileMeta.textContent = summary.meta;
  }
  if (profileBindState && summary.bindState) {
    profileBindState.textContent = summary.bindState;
  }
  if (wechatBindRow) {
    const hint = wechatBindRow.querySelector('i');
    if (hint) {
      hint.textContent = summary.wechatBound ? '已开启微信互通' : '通过小程序互通登录';
    }
  }
  if (profilePostCount && Number.isFinite(summary.posts)) {
    profilePostCount.textContent = String(summary.posts);
  }
  if (profileLikeCount && Number.isFinite(summary.likes)) {
    profileLikeCount.textContent = String(summary.likes);
  }
}

function renderDetailTabs() {
  detailTabButtons.forEach((tab) => {
    tab.classList.toggle('is-active', tab.dataset.detailTab === activeDetailTab);
  });
}

function renderInboxDetailList() {
  if (!inboxDetailList) {
    return;
  }

  inboxDetailList.innerHTML = '';
  const items = Array.isArray(inboxDetails[activeDetailTab]) ? inboxDetails[activeDetailTab] : [];

  if (!items.length) {
    const empty = document.createElement('div');
    empty.className = 'detail-empty';
    empty.textContent = '暂无记录';
    inboxDetailList.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'detail-item';
    card.innerHTML = `
      <p class="main">${item.main}</p>
      <p class="meta">${item.meta}</p>
      <div class="detail-actions">
        ${item.postId ? `<button class="detail-link-btn" type="button" data-open-post="${item.postId}" data-source="${item.sourceType || 'feed'}" data-hint="${String(item.main).replace(/\"/g, '&quot;')}">定位原帖</button>` : ''}
      </div>
    `;
    inboxDetailList.appendChild(card);
  });
}

async function markInboxRead(type) {
  if (appState.inboxRead[type]) {
    return;
  }

  appState.inboxRead[type] = true;
  saveState();
  renderProfileInbox();
  updateProfileDot();

  await apiAdapter.markInboxRead(type);
}

async function loadInboxDetail(type) {
  const remote = await apiAdapter.fetchInboxDetail(type);
  if (Array.isArray(remote)) {
    inboxDetails[type] = remote;
  }
}

function setSubpageLayoutMode(mode = 'default') {
  if (!subpageSheet) {
    return;
  }
  subpageSheet.classList.toggle('subpage-list-mode', mode === 'list');
}

function normalizeTagText(tags) {
  const list = Array.isArray(tags)
    ? tags.map((tag) => String(tag || '').trim()).filter((tag) => tag)
    : String(tags || '')
      .split(/[,\s]+/)
      .map((tag) => String(tag || '').trim())
      .filter((tag) => tag);
  return list.map((tag) => (tag.startsWith('#') ? tag : `#${tag}`)).join(' ');
}

function findSearchResultItem(postRef, fallbackItem = null) {
  const safeRef = String(postRef || '').trim();
  if (fallbackItem && String(fallbackItem.id || fallbackItem.postId || '').trim()) {
    return fallbackItem;
  }
  const inRemote = Array.isArray(searchResultState.all)
    ? searchResultState.all.find((item) => String(item.id || '') === safeRef || String(item.postId || '') === safeRef)
    : null;
  if (inRemote) {
    return inRemote;
  }
  return marketPosts.find((item) => String(item.id || '') === safeRef) || null;
}

function deriveFeedPostId(postRef, fallbackItem = null) {
  const safeRef = String(postRef || '').trim();
  if (/^p-\d+$/i.test(safeRef)) {
    return safeRef;
  }
  const match = safeRef.match(/^m-(\d+)$/i);
  if (match) {
    return `p-${match[1]}`;
  }
  const source = findSearchResultItem(safeRef, fallbackItem);
  const mapped = source ? String(source.postId || '') : '';
  return /^p-\d+$/i.test(mapped) ? mapped : '';
}

function upsertFeedPost(item) {
  if (!item || !item.id) {
    return;
  }
  const index = feedPosts.findIndex((post) => String(post.id || '') === String(item.id || ''));
  if (index >= 0) {
    feedPosts[index] = { ...feedPosts[index], ...item };
    return;
  }
  feedPosts.unshift(item);
}

function buildSearchFallbackDetail(source, postRef) {
  const safeRef = String(postRef || source.id || '').trim();
  const keywords = Array.isArray(source.keywords)
    ? source.keywords.map((tag) => String(tag || '').trim()).filter((tag) => tag)
    : [];
  const tags = keywords.length
    ? keywords.map((tag) => `#${tag}`).join(' ')
    : normalizeTagText(source.tags) || '#论坛帖子';

  return {
    jumpView: 'search',
    sourceText: `${source.meta || '论坛帖子'} · 更新时间 ${source.updatedAt || source.time || '刚刚'}`,
    title: source.title || '论坛帖子',
    content: source.snippet || source.content || '',
    tags,
    imageUrl: normalizeMediaUrl(source.image_url || source.imageUrl || ''),
    commentsPreview: [],
    postId: deriveFeedPostId(safeRef, source) || String(source.id || safeRef),
    sourceType: 'search'
  };
}

function resolveSubpageFallbackItem(postId, sourceType = 'feed') {
  const safeId = String(postId || '').trim();
  const safeType = sourceType === 'search' ? 'search' : 'feed';
  if (!safeId || safeType !== currentSubpageSourceType || !Array.isArray(currentSubpageListItems)) {
    return null;
  }
  return currentSubpageListItems.find((item) => String(item && item.id ? item.id : '') === safeId) || null;
}

function resolvePostDetailByRef(postId, sourceType = 'feed', fallbackItem = null) {
  if (!postId) {
    return null;
  }

  const safePostId = String(postId || '').trim();
  const feedPostId = deriveFeedPostId(safePostId, fallbackItem);

  if (sourceType === 'search' || safePostId.startsWith('m-')) {
    if (feedPostId) {
      const feed = feedPosts.find((item) => item.id === feedPostId);
      if (feed) {
        return resolvePostDetailByRef(feedPostId, 'feed', feed);
      }
    }
    const source = findSearchResultItem(safePostId, fallbackItem);
    return source ? buildSearchFallbackDetail(source, safePostId) : null;
  }

  const feed = feedPosts.find((item) => item.id === safePostId);
  const source = feed || fallbackItem;
  if (!source) {
    return null;
  }

  return {
    jumpView: 'home',
    sourceText: `${source.author || '@匿名用户'} · ${source.time || source.updatedAt || '刚刚'}`,
    title: source.title || '社区帖子',
    content: source.content || source.snippet || '',
    tags: normalizeTagText(source.tags) || '#校园论坛',
    imageUrl: normalizeMediaUrl(source.image_url || source.imageUrl || ''),
    commentsPreview: Array.isArray(source.commentsPreview)
      ? source.commentsPreview
      : getCommentPreviewForPost(String(source.id || postId), 3),
    postId: feed ? feed.id : String(source.id || postId),
    sourceType: 'feed'
  };
}

async function openPostDetailSheet(postRef, sourceType = 'feed', fallbackItem = null) {
  let safePostRef = String(postRef || '').trim();
  let safeSourceType = sourceType === 'search' ? 'search' : 'feed';
  let detail = resolvePostDetailByRef(safePostRef, safeSourceType, fallbackItem);

  if (!detail && safeSourceType === 'search') {
    const feedPostId = deriveFeedPostId(safePostRef, fallbackItem);
    if (feedPostId) {
      const remotePost = await apiAdapter.fetchFeedPost(feedPostId);
      if (remotePost) {
        upsertFeedPost(remotePost);
        safePostRef = feedPostId;
        safeSourceType = 'feed';
        detail = resolvePostDetailByRef(feedPostId, 'feed', remotePost);
      }
    }

    if (!detail) {
      const searchItem = findSearchResultItem(safePostRef, fallbackItem);
      if (searchItem) {
        detail = buildSearchFallbackDetail(searchItem, safePostRef);
      }
    }
  } else if (!detail && safeSourceType === 'feed') {
    const remotePost = await apiAdapter.fetchFeedPost(safePostRef);
    if (remotePost) {
      upsertFeedPost(remotePost);
      detail = resolvePostDetailByRef(safePostRef, 'feed', remotePost);
    }
  }

  if (!detail) {
    showToast('原帖暂不可用');
    return false;
  }

  closeInboxDetailSheet();
  closeCommentSheet();
  closeSearchResultSheet();
  closeSubpageSheet();
  closeErrandPage();
  closeCrossGroupPage();
  closeEduSheet();

  postDetailTitle.textContent = detail.jumpView === 'search' ? '论坛帖子详情' : '社区原帖详情';
  postDetailMeta.textContent = detail.sourceText;
  postDetailHeading.textContent = detail.title;
  postDetailContent.textContent = detail.content;
  postDetailTags.textContent = detail.tags;
  if (postDetailImage) {
    if (detail.imageUrl) {
      postDetailImage.src = detail.imageUrl;
      postDetailImage.dataset.imageViewer = 'true';
      postDetailImage.hidden = false;
      postDetailImage.onerror = () => {
        postDetailImage.hidden = true;
      };
    } else {
      postDetailImage.src = '';
      postDetailImage.hidden = true;
    }
  }
  if (postDetailPreview) {
    postDetailPreview.innerHTML = '';
    const previewLines = Array.isArray(detail.commentsPreview) ? detail.commentsPreview : [];
    if (previewLines.length) {
      postDetailPreview.innerHTML = previewLines.map((line) => `<p>${escapeHtml(line)}</p>`).join('');
      postDetailPreview.hidden = false;
    } else {
      postDetailPreview.hidden = true;
    }
  }
  if (postDetailCommentBtn) {
    const canOpen = detail.sourceType === 'feed' && detail.postId;
    postDetailCommentBtn.hidden = !canOpen;
    postDetailCommentBtn.dataset.postId = canOpen ? String(detail.postId) : '';
  }
  if (postFallbackList) {
    postFallbackList.innerHTML = '';
  }

  postDetailSheet.hidden = false;
  postDetailMask.hidden = true;
}

function closePostDetailSheet() {
  if (!postDetailSheet || !postDetailMask) {
    return;
  }
  postDetailSheet.hidden = true;
  postDetailMask.hidden = true;
}

function closeSearchResultSheet() {
  if (!searchResultSheet || !searchResultMask) {
    return;
  }
  searchResultSheet.hidden = true;
  searchResultMask.hidden = true;
}

function closeSubpageSheet() {
  if (!subpageSheet || !subpageMask) {
    return;
  }
  subpageSheet.hidden = true;
  subpageMask.hidden = true;
  setSubpageLayoutMode('default');
  currentSubpageListItems = [];
  currentSubpageSourceType = 'feed';
  activeSubpageAction = null;
}

function openSubpageSheet({ title = '', subtitle = '', body = '', actionLabel = '', action = null } = {}) {
  if (!subpageSheet || !subpageMask || !subpageTitle || !subpageSub || !subpageBody || !subpageActionBtn) {
    return;
  }
  setSubpageLayoutMode('default');
  currentSubpageListItems = [];
  currentSubpageSourceType = 'feed';
  subpageTitle.textContent = title || '页面';
  subpageSub.textContent = subtitle || '';
  subpageBody.innerHTML = body || '';
  if (subpageList) {
    subpageList.innerHTML = '';
  }
  activeSubpageAction = typeof action === 'function' ? action : null;
  if (actionLabel && activeSubpageAction) {
    subpageActionBtn.textContent = actionLabel;
    subpageActionBtn.hidden = false;
  } else {
    subpageActionBtn.hidden = true;
  }
  closeInboxDetailSheet();
  closeCommentSheet();
  closePostDetailSheet();
  closeSearchResultSheet();
  closeErrandPage();
  closeCrossGroupPage();
  closeEduSheet();
  subpageSheet.hidden = false;
  subpageMask.hidden = false;
}

function renderSubpageList(items, sourceType = 'feed', emptyText = '暂无记录') {
  if (!subpageList) {
    return;
  }
  subpageList.innerHTML = '';
  const list = Array.isArray(items) ? items : [];
  currentSubpageListItems = [...list];
  currentSubpageSourceType = sourceType === 'search' ? 'search' : 'feed';
  if (!list.length) {
    const empty = document.createElement('div');
    empty.className = 'subpage-empty';
    empty.textContent = emptyText;
    subpageList.appendChild(empty);
    return;
  }

  list.forEach((item, index) => {
    const card = document.createElement('article');
    card.className = 'subpage-card is-clickable';
    card.dataset.subpageIndex = String(index);
    const safeId = String(item && item.id ? item.id : `${sourceType}-${index}`);
    if (sourceType === 'search') {
      card.dataset.marketPostId = safeId;
      card.innerHTML = `
        <h5>${escapeHtml(item.title)}</h5>
        <p>${escapeHtml(item.snippet || item.content || '')}</p>
        <small>${escapeHtml(item.meta || '论坛帖子')} · 更新时间 ${escapeHtml(item.updatedAt || '')} · 热度 ${escapeHtml(item.hotScore || 0)}</small>
      `;
    } else {
      card.dataset.feedPostId = safeId;
      card.innerHTML = `
        <div class="subpage-meta">${escapeHtml(item.author || '@匿名用户')} · ${escapeHtml(item.time || '')}</div>
        <h5>${escapeHtml(item.title)}</h5>
        <p>${escapeHtml(item.content || '')}</p>
        <div class="subpage-stats">点赞 ${escapeHtml(item.likes || 0)} · 评论 ${escapeHtml(item.comments || 0)}</div>
      `;
    }
    subpageList.appendChild(card);
  });
}

function openSubpageListPage({
  title = '',
  subtitle = '',
  description = '',
  items = [],
  sourceType = 'feed',
  emptyText = '暂无记录'
} = {}) {
  if (!subpageSheet || !subpageMask || !subpageTitle || !subpageSub || !subpageBody || !subpageActionBtn) {
    return;
  }
  setSubpageLayoutMode('list');
  subpageTitle.textContent = title || '列表';
  subpageSub.textContent = subtitle || '';
  subpageBody.innerHTML = description ? `<p>${description}</p>` : '';
  renderSubpageList(items, sourceType, emptyText);
  subpageActionBtn.hidden = true;
  activeSubpageAction = null;
  closeInboxDetailSheet();
  closeCommentSheet();
  closePostDetailSheet();
  closeSearchResultSheet();
  closeErrandPage();
  closeCrossGroupPage();
  closeEduSheet();
  subpageSheet.hidden = false;
  subpageMask.hidden = true;
}

let activeErrandFilter = 'all';

function getCurrentClientIdentity() {
  const auth = appState && appState.clientAuth ? appState.clientAuth : {};
  const userId = Number(auth.userId || 0);
  const displayName = String(auth.displayName || auth.username || (userId ? `用户${userId}` : '匿名同学')).trim() || '匿名同学';
  const contact = `站内私信 @${displayName}`;
  return { userId, displayName, contact };
}

function getErrandStatusLabel(status) {
  const map = {
    open: '待接单',
    inprogress: '进行中',
    waiting_confirm: '待发布方确认',
    done: '已完成',
    canceled: '已取消'
  };
  return map[normalizeErrandStatus(status)] || '待接单';
}

function getErrandStatusClass(status) {
  return `errand-status-tag errand-status-${normalizeErrandStatus(status)}`;
}

function renderErrandSummary() {
  const open = errandTasks.filter((task) => task.status === 'open').length;
  const inprogress = errandTasks.filter((task) => task.status === 'inprogress' || task.status === 'waiting_confirm').length;
  const done = errandTasks.filter((task) => task.status === 'done').length;
  if (errandOpenCount) {
    errandOpenCount.textContent = String(open);
  }
  if (errandInProgressCount) {
    errandInProgressCount.textContent = String(inprogress);
  }
  if (errandDoneCount) {
    errandDoneCount.textContent = String(done);
  }
}

function persistErrandState() {
  saveErrandTasks(errandTasks);
  renderErrandSummary();
}

function getErrandPrimaryAction(task) {
  const identity = getCurrentClientIdentity();
  const isPublisher = identity.userId > 0 && Number(task.publisherId || 0) === identity.userId;
  const isRunner = identity.userId > 0 && Number(task.runnerId || 0) === identity.userId;
  const status = normalizeErrandStatus(task.status);

  if (status === 'open') {
    if (isPublisher) {
      return { action: 'detail', label: '查看详情', buttonClass: 'btn-light' };
    }
    return { action: 'claim', label: '我要接单', buttonClass: 'btn-dark' };
  }
  if (status === 'inprogress') {
    if (isRunner) {
      return { action: 'delivered', label: '我已送达', buttonClass: 'btn-dark' };
    }
    return { action: 'detail', label: '查看进度', buttonClass: 'btn-light' };
  }
  if (status === 'waiting_confirm') {
    if (isPublisher) {
      return { action: 'confirm', label: '确认完成', buttonClass: 'btn-dark' };
    }
    return { action: 'detail', label: '等待确认', buttonClass: 'btn-light' };
  }
  return { action: 'detail', label: '查看详情', buttonClass: 'btn-light' };
}

function applyErrandAction(task, action) {
  if (!task) {
    return false;
  }
  const identity = getCurrentClientIdentity();
  const isPublisher = identity.userId > 0 && Number(task.publisherId || 0) === identity.userId;
  const isRunner = identity.userId > 0 && Number(task.runnerId || 0) === identity.userId;
  const nowIso = new Date().toISOString();

  if (action === 'claim') {
    if (task.status !== 'open') {
      showToast('任务状态已变化，请刷新列表');
      return false;
    }
    if (isPublisher) {
      showToast('不能接自己发布的任务');
      return false;
    }
    task.status = 'inprogress';
    task.runnerId = Number(identity.userId || 0);
    task.runnerName = String(identity.displayName || '接单同学');
    task.runnerContact = String(identity.contact || '站内私信');
    task.acceptedAt = nowIso;
    persistErrandState();
    renderErrandList();
    showToast('接单成功，请完成后点击“我已送达”');
    return true;
  }

  if (action === 'delivered') {
    if (task.status !== 'inprogress') {
      showToast('当前任务不在进行中');
      return false;
    }
    if (!isRunner) {
      showToast('仅接单者可标记送达');
      return false;
    }
    task.status = 'waiting_confirm';
    task.deliveredAt = nowIso;
    persistErrandState();
    renderErrandList();
    showToast('已标记送达，等待发布方确认');
    return true;
  }

  if (action === 'confirm') {
    if (task.status !== 'waiting_confirm') {
      showToast('当前任务不在待确认状态');
      return false;
    }
    if (!isPublisher) {
      showToast('仅发布方可确认完成');
      return false;
    }
    task.status = 'done';
    task.confirmedAt = nowIso;
    persistErrandState();
    renderErrandList();
    showToast('任务已确认完成');
    return true;
  }

  if (action === 'cancel') {
    if (task.status !== 'open' || !isPublisher) {
      showToast('仅发布方可撤销待接单任务');
      return false;
    }
    task.status = 'canceled';
    persistErrandState();
    renderErrandList();
    showToast('任务已撤销');
    return true;
  }

  return false;
}

function renderErrandList() {
  if (!errandList) {
    return;
  }
  renderErrandSummary();
  const filtered = errandTasks.filter((task) => {
    if (activeErrandFilter === 'all') {
      return true;
    }
    if (activeErrandFilter === 'quick') {
      return task.tag.includes('快速');
    }
    if (activeErrandFilter === 'delivery') {
      return task.tag.includes('外卖');
    }
    if (activeErrandFilter === 'print') {
      return task.tag.includes('打印');
    }
    return true;
  });

  if (!filtered.length) {
    errandList.innerHTML = '<div class="subpage-empty">暂无跑腿需求</div>';
    return;
  }

  errandList.innerHTML = filtered
    .map(
      (task) => {
        const action = getErrandPrimaryAction(task);
        return `
        <article class="errand-card" data-errand-id="${escapeHtml(task.id)}">
          <div class="errand-head">
            <h5>${escapeHtml(task.title)}</h5>
            <span class="errand-reward">${escapeHtml(task.reward)}</span>
          </div>
          <div class="errand-meta">
            <span>${escapeHtml(task.time)}</span>
            <span>${escapeHtml(task.distance)}</span>
            <span class="errand-tag">${escapeHtml(task.tag)}</span>
          </div>
          <p class="errand-note">${escapeHtml(task.note)}</p>
          <div class="errand-status">
            <span class="${escapeHtml(getErrandStatusClass(task.status))}">${escapeHtml(getErrandStatusLabel(task.status))}</span>
          </div>
          <p class="errand-contact">发布者：${escapeHtml(task.publisherName || '匿名同学')} · 联系：${escapeHtml(task.publisherContact || '站内私信')}</p>
          <div class="errand-actions">
            <button class="btn-light" type="button" data-errand-action="detail" data-errand-id="${escapeHtml(task.id)}">查看详情</button>
            <button class="${escapeHtml(action.buttonClass)}" type="button" data-errand-action="${escapeHtml(action.action)}" data-errand-id="${escapeHtml(task.id)}">${escapeHtml(action.label)}</button>
          </div>
        </article>
      `;
      }
    )
    .join('');
}

function findErrandTask(taskId) {
  const safeId = String(taskId || '');
  return errandTasks.find((item) => String(item.id) === safeId) || null;
}

function openErrandTaskDetail(taskId) {
  const task = findErrandTask(taskId);
  if (!task) {
    showToast('该跑腿需求不存在');
    return;
  }

  const identity = getCurrentClientIdentity();
  const isPublisher = identity.userId > 0 && Number(task.publisherId || 0) === identity.userId;
  const isRunner = identity.userId > 0 && Number(task.runnerId || 0) === identity.userId;
  const status = normalizeErrandStatus(task.status);
  const timeline = [
    `发布：${task.createdAt ? new Date(task.createdAt).toLocaleString('zh-CN', { hour12: false }) : '-'}`,
    task.acceptedAt ? `接单：${new Date(task.acceptedAt).toLocaleString('zh-CN', { hour12: false })}` : '',
    task.deliveredAt ? `送达：${new Date(task.deliveredAt).toLocaleString('zh-CN', { hour12: false })}` : '',
    task.confirmedAt ? `确认：${new Date(task.confirmedAt).toLocaleString('zh-CN', { hour12: false })}` : ''
  ].filter(Boolean);

  let actionLabel = '返回任务池';
  let action = () => {
    openErrandPage();
    return false;
  };

  if (status === 'open' && !isPublisher) {
    actionLabel = '我要接单';
    action = () => {
      const ok = applyErrandAction(task, 'claim');
      if (ok) {
        openErrandPage();
        return false;
      }
      return false;
    };
  } else if (status === 'inprogress' && isRunner) {
    actionLabel = '我已送达';
    action = () => {
      const ok = applyErrandAction(task, 'delivered');
      if (ok) {
        openErrandPage();
        return false;
      }
      return false;
    };
  } else if (status === 'waiting_confirm' && isPublisher) {
    actionLabel = '确认完成';
    action = () => {
      const ok = applyErrandAction(task, 'confirm');
      if (ok) {
        openErrandPage();
        return false;
      }
      return false;
    };
  } else if (status === 'open' && isPublisher) {
    actionLabel = '撤销任务';
    action = () => {
      const ok = applyErrandAction(task, 'cancel');
      if (ok) {
        openErrandPage();
        return false;
      }
      return false;
    };
  }

  const body = `
    <p>任务类型：${escapeHtml(task.tag)} · 奖励 ${escapeHtml(task.reward)}</p>
    <p>预计时效：${escapeHtml(task.time)}，位置：${escapeHtml(task.distance)}。</p>
    <p>需求说明：${escapeHtml(task.note)}</p>
    <p>状态：${escapeHtml(getErrandStatusLabel(task.status))}</p>
    <p>发布者：${escapeHtml(task.publisherName || '匿名同学')} · 联系方式：${escapeHtml(task.publisherContact || '站内私信')}</p>
    ${task.runnerName ? `<p>接单者：${escapeHtml(task.runnerName)} · 联系方式：${escapeHtml(task.runnerContact || '站内私信')}</p>` : '<p>接单者：暂无</p>'}
    <p>流转记录：${escapeHtml(timeline.join(' ｜ '))}</p>
  `;
  openSubpageSheet({
    title: task.title,
    subtitle: '跑腿配送 · 任务详情',
    body,
    actionLabel,
    action
  });
}

function openErrandCreateSheet() {
  const identity = getCurrentClientIdentity();
  const body = `
    <div class="wechat-auth-panel">
      <label>
        任务类型
        <select id="errandCreateType">
          <option value="quick">快速代取</option>
          <option value="delivery">外卖代拿</option>
          <option value="print">打印跑腿</option>
          <option value="other">其他跑腿</option>
        </select>
      </label>
      <label>
        任务标题
        <input id="errandCreateTitle" type="text" maxlength="80" placeholder="例如：帮我取快递（南门驿站）" />
      </label>
      <label>
        奖励金额
        <input id="errandCreateReward" type="text" maxlength="10" value="￥5" placeholder="例如：￥5" />
      </label>
      <label>
        预计时效
        <input id="errandCreateTime" type="text" maxlength="30" placeholder="例如：20 分钟内" />
      </label>
      <label>
        位置/距离
        <input id="errandCreateDistance" type="text" maxlength="30" placeholder="例如：北食堂 300m" />
      </label>
      <label>
        需求说明
        <textarea id="errandCreateNote" rows="3" maxlength="180" placeholder="填写注意事项、取件码等"></textarea>
      </label>
      <label>
        联系方式（必填）
        <input id="errandCreateContact" type="text" maxlength="40" placeholder="例如：微信 zhaoyi_2026 / 手机 13xxxx" value="${escapeHtml(identity.contact)}" />
      </label>
    </div>
  `;

  openSubpageSheet({
    title: '发布跑腿需求',
    subtitle: '校园集市 · 发布',
    body,
    actionLabel: '发布任务',
    action: () => {
      if (!subpageBody) {
        return false;
      }
      const typeInput = subpageBody.querySelector('#errandCreateType');
      const titleInput = subpageBody.querySelector('#errandCreateTitle');
      const rewardInput = subpageBody.querySelector('#errandCreateReward');
      const timeInput = subpageBody.querySelector('#errandCreateTime');
      const distanceInput = subpageBody.querySelector('#errandCreateDistance');
      const noteInput = subpageBody.querySelector('#errandCreateNote');
      const contactInput = subpageBody.querySelector('#errandCreateContact');
      const type = String(typeInput ? typeInput.value : 'quick').trim();
      const title = String(titleInput ? titleInput.value : '').trim();
      const rewardRaw = String(rewardInput ? rewardInput.value : '').trim();
      const reward = rewardRaw.startsWith('￥') ? rewardRaw : `￥${rewardRaw || '0'}`;
      const time = String(timeInput ? timeInput.value : '').trim() || '尽快';
      const distance = String(distanceInput ? distanceInput.value : '').trim() || '待沟通';
      const note = String(noteInput ? noteInput.value : '').trim();
      const contact = String(contactInput ? contactInput.value : '').trim();

      if (!title) {
        showToast('请先填写任务标题');
        return false;
      }
      if (!contact) {
        showToast('请填写联系方式，方便接单同学联系');
        return false;
      }

      const tagMap = {
        quick: '快速代取',
        delivery: '外卖代拿',
        print: '打印跑腿',
        other: '其他跑腿'
      };
      const newTask = normalizeErrandTask({
        id: `e-${Date.now()}`,
        title,
        reward,
        time,
        distance,
        tag: tagMap[type] || tagMap.other,
        note,
        publisherId: Number(identity.userId || 0),
        publisherName: identity.displayName,
        publisherContact: contact,
        runnerId: 0,
        runnerName: '',
        runnerContact: '',
        status: 'open',
        createdAt: new Date().toISOString(),
        acceptedAt: '',
        deliveredAt: '',
        confirmedAt: ''
      });
      errandTasks.unshift(newTask);
      persistErrandState();
      renderErrandList();
      showToast('任务发布成功，已进入任务池');
      openErrandPage();
      return false;
    }
  });
}

function openErrandPage() {
  if (!errandSheet || !errandMask) {
    return;
  }
  setSubpageLayoutMode('default');
  closeInboxDetailSheet();
  closeCommentSheet();
  closePostDetailSheet();
  closeSearchResultSheet();
  closeSubpageSheet();
  closeCrossGroupPage();
  closeEduSheet();
  if (errandFilterButtons.length) {
    errandFilterButtons.forEach((btn) => {
      btn.classList.toggle('is-active', btn.dataset.errandFilter === activeErrandFilter);
    });
  }
  renderErrandList();
  errandSheet.hidden = false;
  errandMask.hidden = true;
}

function closeErrandPage() {
  if (!errandSheet || !errandMask) {
    return;
  }
  errandSheet.hidden = true;
  errandMask.hidden = true;
}

function renderCrossGroupPage() {
  if (crossGroupList) {
    crossGroupList.innerHTML = crossGroups
      .map(
        (group) => `
          <article class="cross-card" data-cross-group-id="${escapeHtml(group.id)}">
            <div>
              <h5>${escapeHtml(group.title)}</h5>
              <p>${escapeHtml(group.tags.join(' · '))}</p>
            </div>
            <div class="cross-meta">
              <span>${escapeHtml(String(group.members))} 人</span>
              <span>在线 ${escapeHtml(String(group.online))}</span>
            </div>
            <button class="btn-light" type="button" data-cross-action="join" data-cross-group-id="${escapeHtml(group.id)}">加入讨论</button>
          </article>
        `
      )
      .join('');
  }

  if (crossTopicList) {
    crossTopicList.innerHTML = crossTopics
      .map(
        (topic) => `
          <article class="cross-topic" data-cross-topic-id="${escapeHtml(topic.id)}" role="button" tabindex="0">
            <div>
              <h6>${escapeHtml(topic.title)}</h6>
              <p>${escapeHtml(topic.meta)}</p>
            </div>
            <span class="cross-heat">${escapeHtml(topic.heat)}</span>
          </article>
        `
      )
      .join('');
  }
}

function openCrossGroupPage() {
  if (!crossGroupSheet || !crossGroupMask) {
    return;
  }
  setSubpageLayoutMode('default');
  closeInboxDetailSheet();
  closeCommentSheet();
  closePostDetailSheet();
  closeSearchResultSheet();
  closeSubpageSheet();
  closeErrandPage();
  closeEduSheet();
  renderCrossGroupPage();
  crossGroupSheet.hidden = false;
  crossGroupMask.hidden = true;
}

function closeCrossGroupPage() {
  if (!crossGroupSheet || !crossGroupMask) {
    return;
  }
  crossGroupSheet.hidden = true;
  crossGroupMask.hidden = true;
}

function findCrossGroup(groupId) {
  const safeId = String(groupId || '');
  return crossGroups.find((item) => String(item.id) === safeId) || null;
}

function findCrossTopic(topicId) {
  const safeId = String(topicId || '');
  return crossTopics.find((item) => String(item.id) === safeId) || null;
}

function openCrossTopicDirect(topicId) {
  const topic = findCrossTopic(topicId);
  if (!topic) {
    showToast('该话题暂不可用');
    return;
  }
  const titleKeyword = String(topic.title || '').trim();
  if (titleKeyword && openPostByKeyword(titleKeyword, { preferred: 'search', fallbackSearch: false })) {
    return;
  }

  const queryKeyword = String(topic.query || '').trim();
  if (queryKeyword) {
    closeCrossGroupPage();
    openPostByKeyword(queryKeyword, { preferred: 'search', fallbackSearch: true });
    return;
  }

  showToast('已为你打开相关帖子检索');
}

function openEduCenterPage() {
  void openEduSheet('hall');
}

function buildFallbackRecommendations(sourceType = 'feed', hintText = '') {
  const hint = toLowerSafe(hintText);
  const fallback = [];

  const addCandidate = (item, type, baseScore) => {
    const sourceText = toLowerSafe(
      `${item.title || ''} ${item.content || item.snippet || ''} ${(item.tags || []).join(' ')} ${(item.keywords || []).join(' ')}`
    );
    let score = baseScore;
    if (hint) {
      if (sourceText.includes(hint)) {
        score += 8;
      } else if (hint.length >= 2 && sourceText.includes(hint.slice(0, 2))) {
        score += 3;
      }
    }

    fallback.push({
      id: item.id,
      sourceType: type,
      title: item.title,
      meta: type === 'search'
        ? `${item.meta || '搜索结果'} · 热度 ${item.hotScore || 0}`
        : `${item.author || '社区帖子'} · ${item.time || ''}`,
      score
    });
  };

  marketPosts.forEach((item) => addCandidate(item, 'search', sourceType === 'search' ? 5 : 2));
  feedPosts.forEach((item) => addCandidate(item, 'feed', sourceType === 'feed' ? 5 : 2));

  return fallback
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
}

function showFallbackRecommendationCard(sourceType = 'feed', hintText = '') {
  const list = buildFallbackRecommendations(sourceType, hintText);

  postDetailTitle.textContent = '未定位到原帖';
  postDetailMeta.textContent = '定位失败兜底';
  postDetailHeading.textContent = '推荐相似内容';
  postDetailContent.textContent = '原帖可能已删除或已下线。你可以先查看下列相似内容。';
  postDetailTags.textContent = hintText ? `原始线索：${hintText}` : '可继续使用关键词搜索。';

  if (postFallbackList) {
    postFallbackList.innerHTML = '';

    if (!list.length) {
      const empty = document.createElement('div');
      empty.className = 'detail-empty';
      empty.textContent = '暂无可推荐内容';
      postFallbackList.appendChild(empty);
    } else {
      list.forEach((item) => {
        const btn = document.createElement('button');
        btn.className = 'fallback-item';
        btn.type = 'button';
        btn.dataset.openPost = item.id;
        btn.dataset.source = item.sourceType;
        btn.innerHTML = `<strong>${item.title}</strong><span>${item.meta}</span>`;
        postFallbackList.appendChild(btn);
      });
    }
  }

  postDetailSheet.hidden = false;
  postDetailMask.hidden = false;
  return true;
}

function highlightElement(target) {
  if (!target) {
    return false;
  }

  target.classList.remove('is-focused');
  // Force reflow to retrigger animation when repeatedly focusing same item.
  void target.offsetWidth;
  target.classList.add('is-focused');
  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  setTimeout(() => {
    target.classList.remove('is-focused');
  }, 2200);
  return true;
}

async function locateSearchPostById(postId, hintText = '') {
  const post = marketPosts.find((item) => item.id === postId);
  if (!post) {
    showFallbackRecommendationCard('search', hintText || String(postId || ''));
    return false;
  }

  if (marketQuery) {
    marketQuery.value = post.title;
  }
  await runMarketSearch({ persistRecent: false });

  const index = searchResultState.all.findIndex((item) => item.id === postId);
  if (index >= 0 && index >= searchResultState.visibleCount) {
    searchResultState.visibleCount = index + 1;
    renderVisibleSearchResults();
  }

  requestAnimationFrame(() => {
    const target = marketResultList ? marketResultList.querySelector(`[data-market-post-id=\"${postId}\"]`) : null;
    if (!highlightElement(target)) {
      showFallbackRecommendationCard('search', post.title);
    }
  });

  return true;
}

function locateFeedPostById(postId, hintText = '') {
  const exists = feedPosts.some((item) => item.id === postId);
  if (!exists) {
    showFallbackRecommendationCard('feed', hintText || String(postId || ''));
    return;
  }

  setActiveFeedFilter('all');
  requestAnimationFrame(() => {
    const target = feedList ? feedList.querySelector(`[data-feed-post-id=\"${postId}\"]`) : null;
    if (!highlightElement(target)) {
      const post = feedPosts.find((item) => item.id === postId);
      showFallbackRecommendationCard('feed', post ? post.title : hintText);
    }
  });
}

function locateOriginalPost(postRef, sourceType = 'feed', hintText = '') {
  if (!postRef) {
    showFallbackRecommendationCard(sourceType, hintText || '原帖缺失');
    return;
  }
  void openPostDetailSheet(postRef, sourceType).then((opened) => {
    if (!opened) {
      showFallbackRecommendationCard(sourceType, hintText || String(postRef || ''));
    }
  });
}

function openInboxDetailSheet(type) {
  activeDetailTab = type === 'saved' ? 'saved' : 'likes';
  renderDetailTabs();

  detailSheetTitle.textContent = activeDetailTab === 'likes' ? '收到的赞' : '收藏列表';
  closeCommentSheet();
  detailSheet.hidden = false;
  detailSheetMask.hidden = false;

  void loadInboxDetail(activeDetailTab).then(() => {
    renderInboxDetailList();
  });
  void markInboxRead(activeDetailTab);
  renderInboxDetailList();
}

function closeInboxDetailSheet() {
  detailSheet.hidden = true;
  detailSheetMask.hidden = true;
}

async function refreshUnreadCounts() {
  if (isRefreshingUnread) {
    return true;
  }

  if (!API_CONFIG.enabled) {
    return false;
  }

  isRefreshingUnread = true;
  try {
    const unread = await apiAdapter.fetchUnreadCounts();
    if (!unread) {
      return false;
    }

    inboxCounts = {
      likes: Number(unread.likesUnread || 0),
      saved: Number(unread.savedUnread || 0)
    };

    inboxTotals = {
      likes: Number(unread.likesTotal ?? inboxCounts.likes),
      saved: Number(unread.savedTotal ?? inboxCounts.saved)
    };

    // Backend unread state wins when available (avoid multi-device inconsistency).
    appState.inboxRead.likes = inboxCounts.likes <= 0;
    appState.inboxRead.saved = inboxCounts.saved <= 0;
    saveState();

    renderProfileInbox();
    updateProfileDot();
    return true;
  } catch (error) {
    return false;
  } finally {
    isRefreshingUnread = false;
  }
}

async function refreshVisibleClientState(options = {}) {
  const { force = false } = options;
  if (!API_CONFIG.enabled) {
    return false;
  }

  const now = Date.now();
  if (!force && isRefreshingVisibleState) {
    return true;
  }
  if (!force && lastLiveStateSyncAt && (now - lastLiveStateSyncAt) < LIVE_STATE_SYNC_MS) {
    return true;
  }

  isRefreshingVisibleState = true;
  try {
    await ensureClientSession();
    const activeView = String(appState.lastTab || 'home').trim() || 'home';
    const tasks = [refreshUnreadCounts()];

    if (activeView === 'home') {
      tasks.push(hydrateFeedByFilter(appState.activeFeedFilter || 'all'));
      tasks.push((async () => {
        const remoteHotTopics = await apiAdapter.fetchHomeHotTopics();
        if (Array.isArray(remoteHotTopics) && remoteHotTopics.length) {
          homeHotTopics = remoteHotTopics.map((item, index) => ({
            id: item.id,
            rank: index + 1,
            query: item.title,
            title: item.title,
            heat: item.heat,
            postRef: hotTopicPostMap[String(item.id || '')] || '',
            sourceType: 'search'
          }));
          renderHomeHotTopics();
        }
      })());
    }

    if (activeView === 'profile') {
      tasks.push((async () => {
        const [remoteProfile, profileSettings] = await Promise.all([
          apiAdapter.fetchProfileSummary(),
          apiAdapter.fetchProfileSettings()
        ]);
        if (remoteProfile) {
          applyProfileSummary(remoteProfile);
        }
        if (profileSettings) {
          applyProfileSettings(profileSettings);
        }
      })());
    }

    await Promise.allSettled(tasks);
    lastLiveStateSyncAt = Date.now();
    return true;
  } catch (error) {
    return false;
  } finally {
    isRefreshingVisibleState = false;
  }
}

async function markActiveTypeRead() {
  await markInboxRead(activeDetailTab);
  renderInboxDetailList();
  showToast('已标记当前分类为已读');
}

async function markAllInboxRead() {
  const hasUnread = getUnreadCount() > 0;
  if (!hasUnread) {
    showToast('已是全部已读');
    return;
  }

  appState.inboxRead.likes = true;
  appState.inboxRead.saved = true;
  saveState();
  renderProfileInbox();
  updateProfileDot();
  renderInboxDetailList();

  await Promise.allSettled([
    apiAdapter.markInboxRead('likes'),
    apiAdapter.markInboxRead('saved')
  ]);

  showToast('已全部标记为已读');
}

function clearUnreadPollingTimer() {
  if (!unreadPollingTimer) {
    return;
  }
  clearTimeout(unreadPollingTimer);
  unreadPollingTimer = null;
}

function clearIdleTimer() {
  if (!idleTimer) {
    return;
  }
  clearTimeout(idleTimer);
  idleTimer = null;
}

function getUnreadPollBaseDelay() {
  return Math.max(10000, Number(API_CONFIG.pollingIntervalMs) || 30000);
}

function getUnreadPollDelay(attempt = 0) {
  const base = getUnreadPollBaseDelay();
  const cappedAttempt = Math.max(0, Math.min(Number(attempt) || 0, 6));
  const maxDelay = Math.max(base * 8, 120000);
  return Math.min(base * (2 ** cappedAttempt), maxDelay);
}

function shouldPauseUnreadPolling() {
  if (!API_CONFIG.enabled || !API_CONFIG.pollingEnabled) {
    return true;
  }
  if (!navigator.onLine) {
    return true;
  }
  if (document.hidden || isUserIdle) {
    return true;
  }
  return false;
}

function setUserIdle(nextIdle) {
  if (isUserIdle === nextIdle) {
    return;
  }
  isUserIdle = nextIdle;
  if (nextIdle) {
    clearUnreadPollingTimer();
  }
}

function resetIdleCountdown() {
  if (!API_CONFIG.enabled || !API_CONFIG.pollingEnabled) {
    clearIdleTimer();
    return;
  }

  clearIdleTimer();
  idleTimer = setTimeout(() => {
    setUserIdle(true);
  }, USER_IDLE_MS);
}

function scheduleUnreadPolling(delayMs = getUnreadPollBaseDelay()) {
  clearUnreadPollingTimer();
  if (shouldPauseUnreadPolling()) {
    return;
  }

  const safeDelay = Math.max(5000, Number(delayMs) || getUnreadPollBaseDelay());
  unreadPollingTimer = setTimeout(() => {
    void runUnreadPollingCycle();
  }, safeDelay);
}

async function runUnreadPollingCycle() {
  if (shouldPauseUnreadPolling()) {
    clearUnreadPollingTimer();
    return;
  }

  const ok = await refreshVisibleClientState();
  unreadPollAttempt = ok ? 0 : Math.min(unreadPollAttempt + 1, 6);
  scheduleUnreadPolling(getUnreadPollDelay(unreadPollAttempt));
}

function resumeUnreadPolling(options = {}) {
  const { immediate = false, resetBackoff = false } = options;
  if (resetBackoff) {
    unreadPollAttempt = 0;
  }
  if (shouldPauseUnreadPolling()) {
    clearUnreadPollingTimer();
    return;
  }

  if (immediate) {
    clearUnreadPollingTimer();
    void runUnreadPollingCycle();
    return;
  }

  scheduleUnreadPolling(getUnreadPollDelay(unreadPollAttempt));
}

function startUnreadPolling() {
  clearUnreadPollingTimer();
  clearIdleTimer();

  if (!API_CONFIG.enabled || !API_CONFIG.pollingEnabled) {
    return;
  }

  setUserIdle(false);
  unreadPollAttempt = 0;
  resetIdleCountdown();
  scheduleUnreadPolling(getUnreadPollBaseDelay());
}

function handleUserActivity() {
  if (!API_CONFIG.enabled || !API_CONFIG.pollingEnabled || document.hidden) {
    return;
  }

  const wasIdle = isUserIdle;
  setUserIdle(false);
  resetIdleCountdown();

  if (wasIdle) {
    resumeUnreadPolling({ immediate: true, resetBackoff: true });
  }
}

function applyProfileSettings(settings) {
  if (!settings || typeof settings !== 'object') {
    return;
  }

  if (settings.displayName) {
    appState.clientAuth.displayName = settings.displayName;
  }
  if (settings.publicName) {
    appState.clientAuth.publicName = settings.publicName;
  }
  saveState();

  if (profilePublicName && settings.publicName) {
    profilePublicName.textContent = settings.publicName;
  }
  if (profilePublicNameMenuHint && settings.publicName) {
    profilePublicNameMenuHint.textContent = settings.publicName;
  }
  if (profileBindState && settings.bindState) {
    profileBindState.textContent = settings.bindState;
  }
  if (profileInteropHint) {
    profileInteropHint.textContent = settings.wechatBound ? '已开启微信互通' : '通过小程序互通登录';
  }
  syncHeaderGreeting(settings.displayName || settings.publicName || '');
}

async function hydrateRemoteState() {
  await ensureClientSession();
  await refreshUnreadCounts();
  void hydrateFeedByFilter(appState.activeFeedFilter || 'all');

  const remoteHotTopics = await apiAdapter.fetchHomeHotTopics();
  if (Array.isArray(remoteHotTopics) && remoteHotTopics.length) {
    homeHotTopics = remoteHotTopics.map((item, index) => ({
      id: item.id,
      rank: index + 1,
      query: item.title,
      title: item.title,
      heat: item.heat,
      postRef: hotTopicPostMap[String(item.id || '')] || '',
      sourceType: 'search'
    }));
    renderHomeHotTopics();
  }

  const remoteRecent = await apiAdapter.fetchRecentSearches();
  if (Array.isArray(remoteRecent)) {
    appState.recentSearches = remoteRecent;
    saveState();
    renderRecentSearches();
  }

  const [remoteProfile, profileSettings] = await Promise.all([
    apiAdapter.fetchProfileSummary(),
    apiAdapter.fetchProfileSettings()
  ]);
  if (remoteProfile) {
    applyProfileSummary(remoteProfile);
  }
  if (profileSettings) {
    applyProfileSettings(profileSettings);
  }
}

function openPublicNameSheet() {
  const current = String(
    (profilePublicName && profilePublicName.textContent)
    || (appState.clientAuth && appState.clientAuth.publicName)
    || ''
  ).trim();

  openSubpageSheet({
    title: '发言昵称',
    subtitle: '账号设置',
    body: `
      <div class="wechat-auth-panel">
        <p>帖子、评论和消息提醒只显示这个昵称，不直接展示真实姓名。</p>
        <input id="publicNameInput" type="text" maxlength="16" placeholder="请输入公开昵称" value="${escapeHtml(current)}" />
      </div>
    `,
    actionLabel: '保存昵称',
    action: () => {
      const input = subpageBody ? subpageBody.querySelector('#publicNameInput') : null;
      const nextName = String(input ? input.value : '').trim();
      if (!nextName) {
        showToast('请先填写公开昵称');
        return false;
      }
      void (async () => {
        const updated = await apiAdapter.updatePublicName(nextName);
        if (!updated || !updated.publicName) {
          showToast('昵称保存失败，请稍后再试');
          return;
        }
        applyProfileSettings({
          displayName: appState.clientAuth.displayName || '',
          publicName: updated.publicName,
          bindState: profileBindState ? profileBindState.textContent : ''
        });
        closeSubpageSheet();
        showToast('发言昵称已更新');
      })();
      return false;
    }
  });
}

function openWechatAuthPage() {
  openSubpageSheet({
    title: '账号互通',
    subtitle: '小程序与网页共用同一账号',
    body: `
      <div class="wechat-auth-panel">
        <p>在小程序“我的”页点击“网页登录”，复制一次性登录码后粘贴到这里。</p>
        <input id="webLoginCodeInput" type="text" maxlength="12" placeholder="请输入小程序生成的登录码" />
        <p class="scope-tip">登录成功后，网页端会直接接入同一账号、帖子、收藏和消息提醒。</p>
      </div>
    `,
    actionLabel: '登录网页',
    action: () => {
      const input = subpageBody ? subpageBody.querySelector('#webLoginCodeInput') : null;
      const code = String(input ? input.value : '').trim();
      if (!code) {
        showToast('请先输入登录码');
        return false;
      }
      void (async () => {
        const data = await apiAdapter.exchangeWebLoginCode(code);
        if (!data || !appState.clientAuth || !appState.clientAuth.token) {
          showToast('登录码无效或已过期');
          return;
        }
        closeSubpageSheet();
        await hydrateRemoteState();
        showToast('网页账号已与小程序互通');
      })();
      return false;
    }
  });
}

async function openMyPostsPage() {
  const [remotePosts, remoteErrands] = await Promise.all([
    apiAdapter.fetchMyPosts(),
    apiAdapter.fetchErrands('my')
  ]);
  const localPosts = feedPosts.filter((post) => String(post.author || '').includes('@我'));
  const feedItems = Array.isArray(remotePosts) && remotePosts.length ? remotePosts : localPosts;
  const errandItems = Array.isArray(remoteErrands) ? remoteErrands : [];
  const items = [...feedItems, ...errandItems].sort((left, right) => {
    const leftTime = new Date(left && left.createdAt ? left.createdAt : left && left.time ? left.time : 0).getTime();
    const rightTime = new Date(right && right.createdAt ? right.createdAt : right && right.time ? right.time : 0).getTime();
    if (Number.isFinite(leftTime) && Number.isFinite(rightTime) && leftTime !== rightTime) {
      return rightTime - leftTime;
    }
    const leftId = Number(String(left && left.id ? left.id : '').replace(/\D+/g, '') || 0);
    const rightId = Number(String(right && right.id ? right.id : '').replace(/\D+/g, '') || 0);
    return rightId - leftId;
  });
  openSubpageListPage({
    title: '我的帖子',
    subtitle: '个人中心',
    description: '展示你发布过的帖子与跑腿需求，支持进入详情继续互动。',
    items,
    sourceType: 'mixed',
    emptyText: '你还没有发布过内容'
  });
}

function renderSubpageList(items, sourceType = 'feed', emptyText = '暂无记录') {
  if (!subpageList) {
    return;
  }
  subpageList.innerHTML = '';
  const list = Array.isArray(items) ? items : [];
  currentSubpageListItems = [...list];
  currentSubpageSourceType = sourceType;
  if (!list.length) {
    const empty = document.createElement('div');
    empty.className = 'subpage-empty';
    empty.textContent = emptyText;
    subpageList.appendChild(empty);
    return;
  }

  list.forEach((item, index) => {
    const safeSourceType = item && item.source_type === 'errand'
      ? 'errand'
      : (sourceType === 'search' ? 'search' : 'feed');
    const card = document.createElement('article');
    card.className = 'subpage-card is-clickable';
    card.dataset.subpageIndex = String(index);
    const safeId = String(item && item.id ? item.id : `${safeSourceType}-${index}`);
    if (safeSourceType === 'search') {
      card.dataset.marketPostId = safeId;
      card.innerHTML = `
        <h5>${escapeHtml(item.title)}</h5>
        <p>${escapeHtml(item.snippet || item.content || '')}</p>
        <small>${escapeHtml(item.meta || '论坛帖子')} · 更新时间 ${escapeHtml(item.updatedAt || '')} · 热度 ${escapeHtml(item.hotScore || 0)}</small>
      `;
    } else if (safeSourceType === 'errand') {
      card.dataset.errandTaskId = safeId;
      const locationText = item.locationSummary || [item.pickupLocation, item.destination].filter(Boolean).join(' → ');
      card.innerHTML = `
        <div class="subpage-meta">${escapeHtml(item.statusLabel || '待接单')} · ${escapeHtml(item.reward || '')} · ${escapeHtml(item.relativeText || item.time || '')}</div>
        <h5>${escapeHtml(item.title)}</h5>
        <p>${escapeHtml(item.note || locationText || '查看任务详情')}</p>
        <div class="subpage-stats">${escapeHtml(locationText || '跑腿任务')} </div>
      `;
    } else {
      card.dataset.feedPostId = safeId;
      card.innerHTML = `
        <div class="subpage-meta">${escapeHtml(item.author || '@匿名用户')} · ${escapeHtml(item.time || '')}</div>
        <h5>${escapeHtml(item.title)}</h5>
        <p>${escapeHtml(item.content || '')}</p>
        <div class="subpage-stats">点赞 ${escapeHtml(item.likes || 0)} · 评论 ${escapeHtml(item.comments || 0)}</div>
      `;
    }
    subpageList.appendChild(card);
  });
}

function getErrandPrimaryAction(task) {
  const primary = task && task.primaryAction ? task.primaryAction : { key: 'detail', label: '查看详情', tone: 'ghost' };
  return {
    action: String(primary.key || 'detail'),
    label: String(primary.label || '查看详情'),
    buttonClass: String(primary.tone || 'ghost') === 'primary' ? 'btn-dark' : 'btn-light'
  };
}

async function refreshErrandTasks({ silent = true } = {}) {
  const remote = await apiAdapter.fetchErrands('all');
  if (Array.isArray(remote)) {
    errandTasks = remote;
    renderErrandSummary();
    renderErrandList();
    return errandTasks;
  }
  if (!silent) {
    showToast('跑腿任务加载失败，请稍后重试');
  }
  return errandTasks;
}

function renderErrandSummary() {
  const open = errandTasks.filter((task) => normalizeErrandStatus(task.status) === 'open').length;
  const inprogress = errandTasks.filter((task) => {
    const status = normalizeErrandStatus(task.status);
    return status === 'inprogress' || status === 'waiting_confirm';
  }).length;
  const done = errandTasks.filter((task) => normalizeErrandStatus(task.status) === 'done').length;
  if (errandOpenCount) {
    errandOpenCount.textContent = String(open);
  }
  if (errandInProgressCount) {
    errandInProgressCount.textContent = String(inprogress);
  }
  if (errandDoneCount) {
    errandDoneCount.textContent = String(done);
  }
}

function renderErrandList() {
  if (!errandList) {
    return;
  }
  renderErrandSummary();
  const filtered = errandTasks.filter((task) => {
    if (activeErrandFilter === 'all') {
      return true;
    }
    return String(task.taskType || 'quick') === String(activeErrandFilter || 'all');
  });

  if (!filtered.length) {
    errandList.innerHTML = '<div class="subpage-empty">暂无跑腿需求</div>';
    return;
  }

  errandList.innerHTML = filtered.map((task) => {
    const action = getErrandPrimaryAction(task);
    const locationText = task.locationSummary || [task.pickupLocation, task.destination].filter(Boolean).join(' → ') || '待沟通';
    return `
      <article class="errand-card" data-errand-id="${escapeHtml(task.id)}">
        <div class="errand-head">
          <h5>${escapeHtml(task.title)}</h5>
          <span class="errand-reward">${escapeHtml(task.reward)}</span>
        </div>
        <div class="errand-meta">
          <span>${escapeHtml(task.time)}</span>
          <span>${escapeHtml(locationText)}</span>
          <span class="errand-tag">${escapeHtml(task.tag)}</span>
        </div>
        <p class="errand-note">${escapeHtml(task.note || locationText)}</p>
        <div class="errand-status">
          <span class="${escapeHtml(getErrandStatusClass(task.status))}">${escapeHtml(task.statusLabel || getErrandStatusLabel(task.status))}</span>
        </div>
        <p class="errand-contact">发布者：${escapeHtml(task.publisherName || '匿名同学')} · 联系方式：${escapeHtml(task.publisherContact || '接单后可见')}</p>
        <div class="errand-actions">
          <button class="btn-light" type="button" data-errand-action="detail" data-errand-id="${escapeHtml(task.id)}">查看详情</button>
          <button class="${escapeHtml(action.buttonClass)}" type="button" data-errand-action="${escapeHtml(action.action)}" data-errand-id="${escapeHtml(task.id)}">${escapeHtml(action.label)}</button>
        </div>
      </article>
    `;
  }).join('');
}

async function applyErrandAction(task, action) {
  if (!task || !action || action === 'detail') {
    return task || null;
  }
  const result = await apiAdapter.runErrandAction(task.id, action);
  if (!result || !result.item) {
    showToast('任务操作失败，请稍后再试');
    return null;
  }

  if (action === 'delete') {
    errandTasks = errandTasks.filter((item) => item.id !== task.id);
  } else {
    let updated = false;
    errandTasks = errandTasks.map((item) => {
      if (item.id !== result.item.id) {
        return item;
      }
      updated = true;
      return result.item;
    });
    if (!updated) {
      errandTasks.unshift(result.item);
    }
  }

  renderErrandSummary();
  renderErrandList();
  showToast(result.message || '任务状态已更新');
  return result.item;
}

function openErrandTaskDetail(taskId) {
  const task = findErrandTask(taskId);
  if (!task) {
    showToast('该跑腿需求不存在');
    return;
  }

  const timeline = Array.isArray(task.timeline) && task.timeline.length
    ? task.timeline.map((item) => `${item.label}：${item.value}`).join(' ｜ ')
    : [
        task.createdAt ? `发布：${new Date(task.createdAt).toLocaleString('zh-CN', { hour12: false })}` : '发布：刚刚',
        task.acceptedAt ? `接单：${new Date(task.acceptedAt).toLocaleString('zh-CN', { hour12: false })}` : '',
        task.deliveredAt ? `送达：${new Date(task.deliveredAt).toLocaleString('zh-CN', { hour12: false })}` : '',
        task.confirmedAt ? `确认：${new Date(task.confirmedAt).toLocaleString('zh-CN', { hour12: false })}` : ''
      ].filter(Boolean).join(' ｜ ');
  const primary = getErrandPrimaryAction(task);
  const actionLabel = primary.label || '返回任务池';
  const body = `
    <p>任务类型：${escapeHtml(task.tag)} · 奖励 ${escapeHtml(task.reward)}</p>
    <p>预计时效：${escapeHtml(task.time)}。</p>
    <p>取货地址：${escapeHtml(task.pickupLocation || '待沟通')}</p>
    <p>送达地址：${escapeHtml(task.destination || '待沟通')}</p>
    <p>需求说明：${escapeHtml(task.note || '暂无补充说明')}</p>
    <p>状态：${escapeHtml(task.statusLabel || getErrandStatusLabel(task.status))}</p>
    <p>发布者：${escapeHtml(task.publisherName || '匿名同学')} · 联系方式：${escapeHtml(task.publisherContact || '接单后可见')}</p>
    ${task.runnerName ? `<p>接单者：${escapeHtml(task.runnerName)} · 联系方式：${escapeHtml(task.runnerContact || '站内已接单')}</p>` : '<p>接单者：暂无</p>'}
    <p>流转记录：${escapeHtml(timeline || '暂无')}</p>
  `;

  openSubpageSheet({
    title: task.title,
    subtitle: '跑腿配送 · 任务详情',
    body,
    actionLabel,
    action: () => {
      if (primary.action === 'detail') {
        openErrandPage();
        return false;
      }
      void (async () => {
        const updated = await applyErrandAction(task, primary.action);
        if (primary.action === 'delete') {
          openErrandPage();
          return;
        }
        if (updated) {
          openErrandTaskDetail(updated.id);
        }
      })();
      return false;
    }
  });
}

function openErrandCreateSheet() {
  const identity = getCurrentClientIdentity();
  openSubpageSheet({
    title: '发布跑腿需求',
    subtitle: '校园集市 · 发布',
    body: `
      <div class="wechat-auth-panel">
        <label>
          任务类型
          <select id="errandCreateType">
            <option value="quick">快速代取</option>
            <option value="delivery">外卖代拿</option>
            <option value="print">打印跑腿</option>
            <option value="other">其他跑腿</option>
          </select>
        </label>
        <label>
          任务标题
          <input id="errandCreateTitle" type="text" maxlength="80" placeholder="例如：帮我取南门驿站快递" />
        </label>
        <div class="dual-field-row">
          <label>
            奖励金额
            <input id="errandCreateReward" type="text" maxlength="10" value="￥5" placeholder="例如：￥5" />
          </label>
          <label>
            预计时效
            <input id="errandCreateTime" type="text" maxlength="30" placeholder="例如：20 分钟内" />
          </label>
        </div>
        <label>
          取货地址
          <input id="errandCreatePickup" type="text" maxlength="60" placeholder="例如：北院驿站 3 号架" />
        </label>
        <label>
          送达地址
          <input id="errandCreateDestination" type="text" maxlength="60" placeholder="例如：A 区教学楼门口" />
        </label>
        <label>
          需求说明
          <textarea id="errandCreateNote" rows="3" maxlength="180" placeholder="填写取件码、口味或注意事项"></textarea>
        </label>
        <label>
          联系方式
          <input id="errandCreateContact" type="text" maxlength="40" placeholder="例如：微信 zhao_2026 / 手机 13xxxx" value="${escapeHtml(identity.contact)}" />
        </label>
      </div>
    `,
    actionLabel: '发布任务',
    action: () => {
      if (!subpageBody) {
        return false;
      }
      const type = String(subpageBody.querySelector('#errandCreateType')?.value || 'quick').trim();
      const title = String(subpageBody.querySelector('#errandCreateTitle')?.value || '').trim();
      const rewardRaw = String(subpageBody.querySelector('#errandCreateReward')?.value || '').trim();
      const reward = rewardRaw.startsWith('￥') ? rewardRaw : `￥${rewardRaw || '0'}`;
      const time = String(subpageBody.querySelector('#errandCreateTime')?.value || '').trim() || '尽快';
      const pickupLocation = String(subpageBody.querySelector('#errandCreatePickup')?.value || '').trim();
      const destination = String(subpageBody.querySelector('#errandCreateDestination')?.value || '').trim();
      const note = String(subpageBody.querySelector('#errandCreateNote')?.value || '').trim();
      const contact = String(subpageBody.querySelector('#errandCreateContact')?.value || '').trim();

      if (!title) {
        showToast('请先填写任务标题');
        return false;
      }
      if (!pickupLocation) {
        showToast('请填写取货地址');
        return false;
      }
      if (!destination) {
        showToast('请填写送达地址');
        return false;
      }
      if (!contact) {
        showToast('请填写联系方式');
        return false;
      }

      void (async () => {
        const created = await apiAdapter.createErrand({
          task_type: type,
          title,
          reward,
          time,
          pickup_location: pickupLocation,
          destination,
          note,
          contact
        });
        if (!created) {
          showToast('任务发布失败，请稍后再试');
          return;
        }
        errandTasks = [created, ...errandTasks.filter((item) => item.id !== created.id)];
        closeSubpageSheet();
        await openErrandPage();
        showToast('任务发布成功');
        openErrandTaskDetail(created.id);
      })();
      return false;
    }
  });
}

async function openErrandPage() {
  if (!errandSheet || !errandMask) {
    return;
  }
  setSubpageLayoutMode('default');
  closeInboxDetailSheet();
  closeCommentSheet();
  closePostDetailSheet();
  closeSearchResultSheet();
  closeSubpageSheet();
  closeCrossGroupPage();
  closeEduSheet();
  errandFilterButtons.forEach((btn) => {
    btn.classList.toggle('is-active', btn.dataset.errandFilter === activeErrandFilter);
  });
  renderErrandList();
  errandSheet.hidden = false;
  errandMask.hidden = true;
  await refreshErrandTasks({ silent: false });
}

// Event bindings

tabs.forEach((tab) => {
  tab.addEventListener('click', () => setActiveView(tab.dataset.target));
});

feedFilterButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setActiveFeedFilter(button.dataset.filter || 'all');
  });
});

if (feedList) {
  feedList.addEventListener('click', (event) => {
    const actionButton = event.target.closest('button[data-action][data-post-id]');
    if (!actionButton) {
      const card = event.target.closest('.post-card[data-feed-post-id]');
      if (card) {
        openPostDetailSheet(card.dataset.feedPostId, 'feed');
      }
      return;
    }

    void handleFeedAction(actionButton.dataset.action, actionButton.dataset.postId);
  });

  feedList.addEventListener(
    'error',
    (event) => {
      const target = event.target;
      if (target && target.tagName === 'IMG' && target.dataset.imageKind === 'post') {
        const fallback = document.createElement('div');
        fallback.className = 'comment-image-fallback';
        fallback.textContent = '图片不可用';
        target.replaceWith(fallback);
      }
    },
    true
  );
}

if (fabBtn) {
  fabBtn.addEventListener('click', () => {
    openPostComposer();
  });
}

if (marketSearchBtn) {
  marketSearchBtn.addEventListener('click', () => {
    void runMarketSearch({ openResultPage: true });
  });
}

if (loadMoreSearchBtn) {
  loadMoreSearchBtn.hidden = true;
}

if (marketQuery) {
  marketQuery.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      void runMarketSearch({ openResultPage: true });
    }
  });
}

if (marketResultList) {
  marketResultList.addEventListener('click', (event) => {
    const row = event.target.closest('[data-market-post-id]');
    if (!row) {
      return;
    }
    const searchRef = String(row.dataset.searchPostRef || row.dataset.marketPostId || '').trim();
    const fallback = findSearchResultItem(searchRef) || null;
    void openPostDetailSheet(row.dataset.marketPostId || searchRef, row.dataset.source || 'search', fallback);
  });
}

if (clearRecentBtn) {
  clearRecentBtn.addEventListener('click', () => {
    appState.recentSearches = [];
    saveState();
    renderRecentSearches();
    showToast('已清空最近搜索');
  });
}

if (recentSearchList) {
  recentSearchList.addEventListener('click', (event) => {
    const chip = event.target.closest('button[data-keyword]');
    if (!chip) {
      return;
    }

    if (marketQuery) {
      marketQuery.value = chip.dataset.keyword || '';
    }
    void runMarketSearch({ persistRecent: false, openResultPage: true });
  });
}

sortButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setSearchSort(button.dataset.sort || 'hot');
  });
});

Array.from(document.querySelectorAll('.rank-row')).forEach((row) => {
  row.addEventListener('click', () => {
    const explicitPostId = String(row.dataset.marketPostId || rankHotPostMap[String(row.dataset.hot || '')] || '').trim();
    if (explicitPostId) {
      openPostDetailSheet(explicitPostId, 'search');
      return;
    }

    const hotKeyword = String(row.dataset.hot || row.textContent || '').trim();
    openPostByKeyword(hotKeyword, { preferred: 'search', fallbackSearch: true });
  });
});

if (homeHotList) {
  homeHotList.addEventListener('click', (event) => {
    const row = event.target.closest('.hot-row');
    if (!row) {
      return;
    }

    const explicitPostId = String(row.dataset.marketPostId || '').trim();
    if (explicitPostId) {
      openPostDetailSheet(explicitPostId, String(row.dataset.source || 'search'));
      return;
    }

    const hotKeyword = String(row.dataset.hot || '').trim();
    openPostByKeyword(hotKeyword, { preferred: 'search', fallbackSearch: true });
  });
}

Array.from(document.querySelectorAll('.panel')).forEach((panel) => {
  panel.addEventListener('click', () => {
    const target = panel.dataset.jump || 'home';
    const prompt = panel.dataset.prompt || '';
    const title = panel.querySelector('strong') ? panel.querySelector('strong').textContent : '功能入口';
    const isEdu = title && title.includes('课表');
    const subtitle = isEdu ? '教务系统' : '功能页面';
    const description = isEdu
      ? '该入口与真实教务系统对接，独立于知识库问答。'
      : '该入口已切到独立页面，支持后续功能接入与权限校验。';
    if (isEdu) {
      void openEduSheet('schedule');
      return;
    }

    if (title && title.includes('跨校小组')) {
      openCrossGroupPage();
      return;
    }

    if (title && title.includes('跑腿任务')) {
      openErrandPage();
      return;
    }

    if (title && title.includes('课程评价')) {
      const localResults = searchMarketPosts(title);
      openSubpageListPage({
        title,
        subtitle: '专题频道',
        description: '该频道展示对应主题的高赞帖子与问答。',
        items: localResults,
        sourceType: 'search',
        emptyText: '暂无相关内容'
      });
      return;
    }

    if (target === 'search' && prompt) {
      if (marketQuery) {
        marketQuery.value = prompt;
      }
      void runMarketSearch({ openResultPage: true });
      return;
    }

    if (target === 'home') {
      openSubpageSheet({
        title: title || '功能入口',
        subtitle,
        body: `<p>${description}</p>`,
        actionLabel: '',
        action: null
      });
      if (prompt) {
        showToast('已生成跑腿任务草稿');
      }
      return;
    }

    openSubpageSheet({
      title: title || '功能入口',
      subtitle,
      body: `<p>${description}</p>`,
      actionLabel: '',
      action: null
    });
  });
});

if (wikiForm) {
  wikiForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const text = wikiInput ? wikiInput.value : '';
    void sendKnowledgeMessage(text);
    if (wikiInput) {
      wikiInput.value = '';
    }
  });
}

if (wikiDeepThinkingToggle) {
  wikiDeepThinkingToggle.addEventListener('change', () => {
    appState.wikiDeepThinking = Boolean(wikiDeepThinkingToggle.checked);
    saveState();
    showToast(appState.wikiDeepThinking ? '已开启深度思考' : '已关闭深度思考');
  });
}

Array.from(document.querySelectorAll('.wiki-chip')).forEach((chip) => {
  chip.addEventListener('click', () => {
    const text = chip.dataset.text || '';
    if (wikiInput) {
      wikiInput.value = text;
    }
    void sendKnowledgeMessage(text);
    if (wikiInput) {
      wikiInput.value = '';
    }
  });
});

if (wikiBoard) {
  wikiBoard.addEventListener('click', (event) => {
    const toggleBtn = event.target.closest('button[data-qa-toggle-id]');
    if (toggleBtn) {
      event.preventDefault();
      event.stopPropagation();
      openWikiDetailSheet(toggleBtn.dataset.qaToggleId || '', toggleBtn);
      return;
    }
  }, true);
}

if (wikiBoard) {
  wikiBoard.addEventListener('click', (event) => {
    const toggleBtn = event.target.closest('button[data-qa-toggle-id]');
    if (toggleBtn) {
      const panel = wikiBoard.querySelector(`[data-qa-detail-id="${toggleBtn.dataset.qaToggleId}"]`);
      if (!panel) {
        return;
      }
      const willOpen = Boolean(panel.hidden);
      panel.hidden = !willOpen;
      const expandedText = String(toggleBtn.dataset.expandedText || '收起详情');
      const collapsedText = String(toggleBtn.dataset.collapsedText || '查看详情');
      toggleBtn.textContent = willOpen ? expandedText : collapsedText;
      return;
    }

    const sourceBtn = event.target.closest('button[data-source-open],button[data-source-id]');
    if (!sourceBtn) {
      return;
    }

    openKnowledgeSource(
      sourceBtn.dataset.sourceType || 'kb',
      sourceBtn.dataset.jumpUrl || '',
      sourceBtn.dataset.sourceId || ''
    );
  });
}

eduItems.forEach((item) => {
  item.addEventListener('click', () => {
    const action = item.dataset.eduAction || '';
    void openEduSheet(action);
  });
});

if (eduCard) {
  eduCard.addEventListener('click', (event) => {
    const isBtn = event.target.closest('.edu-item');
    if (isBtn) {
      return;
    }
    openEduCenterPage();
  });
}

if (profileMessageList) {
  profileMessageList.addEventListener('click', (event) => {
    const row = event.target.closest('button[data-inbox-id]');
    if (!row) {
      return;
    }

    openInboxDetailSheet(row.dataset.inboxId);
  });
}

if (inboxDetailList) {
  inboxDetailList.addEventListener('click', (event) => {
    const jumpBtn = event.target.closest('button[data-open-post]');
    if (!jumpBtn) {
      return;
    }

    locateOriginalPost(
      jumpBtn.dataset.openPost,
      jumpBtn.dataset.source || 'feed',
      jumpBtn.dataset.hint || ''
    );
  });
}

if (postFallbackList) {
  postFallbackList.addEventListener('click', (event) => {
    const btn = event.target.closest('button[data-open-post]');
    if (!btn) {
      return;
    }

    locateOriginalPost(btn.dataset.openPost, btn.dataset.source || 'feed', btn.textContent || '');
  });
}

if (postDetailCommentBtn) {
  postDetailCommentBtn.addEventListener('click', () => {
    const postId = postDetailCommentBtn.dataset.postId || '';
    if (!postId) {
      return;
    }
    closePostDetailSheet();
    openCommentSheet(postId);
  });
}

if (postDetailImage) {
  postDetailImage.addEventListener('click', () => {
    if (!postDetailImage.src) {
      return;
    }
    openImageViewer(postDetailImage.src, '帖子图片');
  });
}

if (closeDetailSheetBtn) {
  closeDetailSheetBtn.addEventListener('click', closeInboxDetailSheet);
}

if (markTypeReadBtn) {
  markTypeReadBtn.addEventListener('click', () => {
    void markActiveTypeRead();
  });
}

if (markAllReadBtn) {
  markAllReadBtn.addEventListener('click', () => {
    void markAllInboxRead();
  });
}

if (detailSheetMask) {
  detailSheetMask.addEventListener('click', closeInboxDetailSheet);
}

if (backPostDetailBtn) {
  backPostDetailBtn.addEventListener('click', closePostDetailSheet);
}

if (postDetailMask) {
  postDetailMask.addEventListener('click', closePostDetailSheet);
}

if (backSearchResultBtn) {
  backSearchResultBtn.addEventListener('click', closeSearchResultSheet);
}

if (searchResultMask) {
  searchResultMask.addEventListener('click', closeSearchResultSheet);
}

if (searchResultList) {
  searchResultList.addEventListener('click', (event) => {
    const row = event.target.closest('[data-market-post-id]');
    if (!row) {
      return;
    }
    const searchRef = String(row.dataset.searchPostRef || row.dataset.marketPostId || '').trim();
    const fallback = findSearchResultItem(searchRef) || null;
    void openPostDetailSheet(row.dataset.marketPostId || searchRef, row.dataset.source || 'search', fallback);
  });
}

if (searchPagePrevBtn) {
  searchPagePrevBtn.addEventListener('click', () => {
    void goSearchPage(Math.max(1, Number(searchResultState.page || 1) - 1));
  });
}

if (searchPageNextBtn) {
  searchPageNextBtn.addEventListener('click', () => {
    void goSearchPage(Number(searchResultState.page || 1) + 1);
  });
}

if (searchPageNumbers) {
  searchPageNumbers.addEventListener('click', (event) => {
    const btn = event.target.closest('button[data-page]');
    if (!btn) {
      return;
    }
    const next = Number(btn.dataset.page || 1);
    if (!Number.isNaN(next)) {
      void goSearchPage(next);
    }
  });
}

if (searchPageJumpBtn) {
  searchPageJumpBtn.addEventListener('click', () => {
    if (!searchPageJumpInput) {
      return;
    }
    const next = Number(searchPageJumpInput.value || 1);
    if (!Number.isNaN(next) && next > 0) {
      void goSearchPage(next);
    }
  });
}

if (searchPageJumpInput) {
  searchPageJumpInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      const next = Number(searchPageJumpInput.value || 1);
      if (!Number.isNaN(next) && next > 0) {
        void goSearchPage(next);
      }
    }
  });
}

searchPageSortButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const nextSort = button.dataset.searchPageSort || 'hot';
    setSearchSort(nextSort);
  });
});

if (backSubpageBtn) {
  backSubpageBtn.addEventListener('click', closeSubpageSheet);
}

if (subpageMask) {
  subpageMask.addEventListener('click', closeSubpageSheet);
}

if (wikiDetailCloseBtn) {
  wikiDetailCloseBtn.addEventListener('click', closeWikiDetailSheet);
}

if (wikiDetailMask) {
  wikiDetailMask.addEventListener('click', closeWikiDetailSheet);
}

if (wikiDetailList) {
  wikiDetailList.addEventListener('click', (event) => {
    const sourceBtn = event.target.closest('button[data-source-open],button[data-source-id]');
    if (!sourceBtn) {
      return;
    }
    openKnowledgeSource(
      sourceBtn.dataset.sourceType || 'kb',
      sourceBtn.dataset.jumpUrl || '',
      sourceBtn.dataset.sourceId || ''
    );
  });
}

if (backErrandBtn) {
  backErrandBtn.addEventListener('click', closeErrandPage);
}

if (errandMask) {
  errandMask.addEventListener('click', closeErrandPage);
}

if (errandFilterButtons.length) {
  errandFilterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      activeErrandFilter = button.dataset.errandFilter || 'all';
      errandFilterButtons.forEach((btn) => btn.classList.toggle('is-active', btn === button));
      renderErrandList();
    });
  });
}

if (errandCreateBtn) {
  errandCreateBtn.addEventListener('click', () => {
    openErrandCreateSheet();
  });
}

if (errandList) {
  errandList.addEventListener('click', (event) => {
    const actionBtn = event.target.closest('button[data-errand-action][data-errand-id]');
    if (!actionBtn) {
      const card = event.target.closest('.errand-card[data-errand-id]');
      if (card) {
        openErrandTaskDetail(card.dataset.errandId);
      }
      return;
    }

    const taskId = String(actionBtn.dataset.errandId || '');
    const action = String(actionBtn.dataset.errandAction || '');
    if (action === 'detail') {
      openErrandTaskDetail(taskId);
      return;
    }
    if (['claim', 'delivered', 'confirm', 'cancel', 'delete'].includes(action)) {
      const task = findErrandTask(taskId);
      if (!task) {
        showToast('任务不存在');
        return;
      }
      void (async () => {
        const updated = await applyErrandAction(task, action);
        if (action === 'delete') {
          await openErrandPage();
          return;
        }
        if (updated) {
          openErrandTaskDetail(updated.id);
          return;
        }
        openErrandTaskDetail(taskId);
      })();
      return;
    }
    openErrandTaskDetail(taskId);
  });
}

if (backCrossGroupBtn) {
  backCrossGroupBtn.addEventListener('click', closeCrossGroupPage);
}

if (crossGroupMask) {
  crossGroupMask.addEventListener('click', closeCrossGroupPage);
}

if (crossGroupList) {
  crossGroupList.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-cross-group-id]');
    if (!trigger) {
      return;
    }
    const group = findCrossGroup(trigger.dataset.crossGroupId);
    if (!group) {
      showToast('讨论组不存在');
      return;
    }
    const keyword = `${group.title} ${group.tags.join(' ')}`.trim();
    if (marketQuery) {
      marketQuery.value = keyword;
    }
    closeCrossGroupPage();
    void runMarketSearch({ openResultPage: true });
  });
}

if (crossTopicList) {
  crossTopicList.addEventListener('click', (event) => {
    const topicCard = event.target.closest('.cross-topic[data-cross-topic-id]');
    if (!topicCard) {
      return;
    }
    openCrossTopicDirect(topicCard.dataset.crossTopicId);
  });

  crossTopicList.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') {
      return;
    }
    const topicCard = event.target.closest('.cross-topic[data-cross-topic-id]');
    if (!topicCard) {
      return;
    }
    event.preventDefault();
    openCrossTopicDirect(topicCard.dataset.crossTopicId);
  });
}

if (subpageActionBtn) {
  subpageActionBtn.addEventListener('click', () => {
    if (activeSubpageAction) {
      const result = activeSubpageAction();
      if (result === false) {
        return;
      }
      closeSubpageSheet();
    }
  });
}

if (subpageList) {
  subpageList.addEventListener('click', (event) => {
    const getFallbackByCard = (card) => {
      if (!card) {
        return null;
      }
      const index = Number(card.dataset.subpageIndex || -1);
      if (!Number.isNaN(index) && index >= 0 && index < currentSubpageListItems.length) {
        return currentSubpageListItems[index] || null;
      }
      return null;
    };
    const eduBtn = event.target.closest('button[data-edu-action]');
    if (eduBtn) {
      closeSubpageSheet();
      void openEduSheet(eduBtn.dataset.eduAction || '');
      return;
    }
    const feedCard = event.target.closest('[data-feed-post-id]');
    if (feedCard) {
      const fallback = getFallbackByCard(feedCard) || resolveSubpageFallbackItem(feedCard.dataset.feedPostId, 'feed');
      openPostDetailSheet(feedCard.dataset.feedPostId, 'feed', fallback);
      return;
    }
    const errandCard = event.target.closest('[data-errand-task-id]');
    if (errandCard) {
      openErrandTaskDetail(errandCard.dataset.errandTaskId);
      return;
    }
    const marketCard = event.target.closest('[data-market-post-id]');
    if (marketCard) {
      const fallback = getFallbackByCard(marketCard)
        || resolveSubpageFallbackItem(marketCard.dataset.marketPostId, 'search');
      openPostDetailSheet(marketCard.dataset.marketPostId, 'search', fallback);
    }
  });
}

if (backCommentSheetBtn) {
  backCommentSheetBtn.addEventListener('click', closeCommentSheet);
}

if (commentSheetMask) {
  commentSheetMask.addEventListener('click', closeCommentSheet);
}

if (backEduSheetBtn) {
  backEduSheetBtn.addEventListener('click', closeEduSheet);
}

if (eduSheetMask) {
  eduSheetMask.addEventListener('click', closeEduSheet);
}

if (eduSheetBody) {
  eduSheetBody.addEventListener('click', (event) => {
    const navBtn = event.target.closest('[data-edu-nav]');
    if (navBtn) {
      void openEduSheet(navBtn.dataset.eduNav || 'hall');
      return;
    }

    const buildingBtn = event.target.closest('[data-edu-building]');
    if (buildingBtn) {
      eduSheetState.activeBuilding = String(buildingBtn.dataset.eduBuilding || EDU_ALL_BUILDINGS) || EDU_ALL_BUILDINGS;
      void openEduSheet('freeClassrooms');
      return;
    }

    const retry = event.target.closest('button[data-edu-retry]');
    if (retry && activeEduAction) {
      void openEduSheet(activeEduAction);
    }
  });

  eduSheetBody.addEventListener('change', (event) => {
    const select = event.target.closest('select[data-edu-select]');
    if (!select) {
      return;
    }
    handleEduSheetSelectionChange(select.dataset.eduSelect || '', select.value || '');
  });
}

if (commentInput) {
  commentInput.addEventListener('input', () => {
    if (activeCommentPostId) {
      commentDraftByPost[activeCommentPostId] = String(commentInput.value || '');
    }
    setCommentComposerState();
  });
}

if (commentImageInput) {
  commentImageInput.addEventListener('change', async () => {
    const file = commentImageInput.files && commentImageInput.files[0] ? commentImageInput.files[0] : null;
    const check = validateImageFile(file);
    if (!check.ok) {
      selectedCommentImage = null;
      commentImageInput.value = '';
      if (commentImageMeta) {
        commentImageMeta.textContent = check.message;
      }
      setCommentComposerState();
      return;
    }
    if (!file) {
      selectedCommentImage = null;
      if (commentImageMeta) {
        commentImageMeta.textContent = '未选择图片';
      }
      setCommentComposerState();
      return;
    }
    const compressed = await compressImageFile(file, { maxBytes: MAX_IMAGE_BYTES });
    if (!compressed.file) {
      selectedCommentImage = null;
      commentImageInput.value = '';
      if (commentImageMeta) {
        commentImageMeta.textContent = compressed.message || '图片处理失败';
      }
      setCommentComposerState();
      return;
    }
    selectedCommentImage = compressed.file;
    if (commentImageMeta) {
      const sizeText = `${Math.ceil(selectedCommentImage.size / 1024)}KB`;
      const suffix = compressed.wasCompressed ? ' · 已压缩' : '';
      commentImageMeta.textContent = `${selectedCommentImage.name}（${sizeText}）${suffix}`;
    }
    setCommentComposerState();
  });
}

if (commentForm) {
  commentForm.addEventListener('submit', (event) => {
    event.preventDefault();
    void submitComment();
  });
}

if (commentReplyCancelBtn) {
  commentReplyCancelBtn.addEventListener('click', () => {
    clearReplyTarget();
    if (commentInput) {
      commentInput.focus();
    }
  });
}

if (postImageInput) {
  postImageInput.addEventListener('change', async () => {
    const file = postImageInput.files && postImageInput.files[0] ? postImageInput.files[0] : null;
    const check = validateImageFile(file);
    if (!check.ok) {
      selectedPostImage = null;
      postImageInput.value = '';
      if (postImageMeta) {
        postImageMeta.textContent = check.message;
      }
      return;
    }
    if (!file) {
      selectedPostImage = null;
      if (postImageMeta) {
        postImageMeta.textContent = '未选择图片';
      }
      return;
    }
    const compressed = await compressImageFile(file, { maxBytes: MAX_IMAGE_BYTES });
    if (!compressed.file) {
      selectedPostImage = null;
      postImageInput.value = '';
      if (postImageMeta) {
        postImageMeta.textContent = compressed.message || '图片处理失败';
      }
      return;
    }
    selectedPostImage = compressed.file;
    if (postImageMeta) {
      const sizeText = `${Math.ceil(selectedPostImage.size / 1024)}KB`;
      const suffix = compressed.wasCompressed ? ' · 已压缩' : '';
      postImageMeta.textContent = `${selectedPostImage.name}（${sizeText}）${suffix}`;
    }
  });
}

if (closePostComposerBtn) {
  closePostComposerBtn.addEventListener('click', closePostComposer);
}

if (postComposerMask) {
  postComposerMask.addEventListener('click', closePostComposer);
}

if (postComposerForm) {
  postComposerForm.addEventListener('submit', (event) => {
    event.preventDefault();
    void submitPostComposer();
  });
}

if (commentList) {
  commentList.addEventListener('click', (event) => {
    const image = event.target.closest('img[data-image-viewer]');
    if (image) {
      openImageViewer(image.src, image.alt || '评论图片');
      return;
    }
    const retryBtn = event.target.closest('button[data-retry-comment-id]');
    if (retryBtn) {
      void retryComment(retryBtn.dataset.retryCommentId);
      return;
    }
    const replyBtn = event.target.closest('button[data-reply-comment-id]');
    if (replyBtn) {
      setReplyTarget(replyBtn.dataset.replyCommentId);
      return;
    }
    const likeBtn = event.target.closest('button[data-like-comment-id]');
    if (likeBtn) {
      const commentId = String(likeBtn.dataset.likeCommentId || '');
      if (!commentId) {
        return;
      }
      const wasLiked = likedCommentIds.has(commentId);
      const nextLiked = !wasLiked;
      const previousSet = new Set(likedCommentIds);
      if (wasLiked) {
        likedCommentIds.delete(commentId);
      } else {
        likedCommentIds.add(commentId);
      }
      saveCommentLikedSet(likedCommentIds, appState.clientAuth.userId);
      if (activeCommentPostId) {
        const list = ensureCommentStore(activeCommentPostId);
        const target = list.find((item) => String(item.id) === commentId);
        if (target) {
          target.likes = Math.max(0, Number(target.likes || 0) + (wasLiked ? -1 : 1));
        }
        renderCommentList();
      }
      void apiAdapter.toggleCommentLike(commentId, nextLiked).then((remote) => {
        if (!activeCommentPostId) {
          return;
        }
        const list = ensureCommentStore(activeCommentPostId);
        const target = list.find((item) => String(item.id) === commentId);
        if (!remote) {
          likedCommentIds.clear();
          previousSet.forEach((id) => likedCommentIds.add(id));
          saveCommentLikedSet(likedCommentIds, appState.clientAuth.userId);
          if (target) {
            target.likes = Math.max(0, Number(target.likes || 0) + (wasLiked ? 1 : -1));
          }
          renderCommentList();
          showToast('评论点赞失败，请重试');
          return;
        }
        if (target) {
          target.likes = Number(remote.likes || target.likes || 0);
        }
        if (remote.liked) {
          likedCommentIds.add(commentId);
        } else {
          likedCommentIds.delete(commentId);
        }
        saveCommentLikedSet(likedCommentIds, appState.clientAuth.userId);
        renderCommentList();
      });
      return;
    }
    const deleteBtn = event.target.closest('button[data-delete-comment-id]');
    if (deleteBtn) {
      let commentId = String(deleteBtn.dataset.deleteCommentId || '');
      if (!commentId) {
        const card = deleteBtn.closest('.comment-item');
        commentId = card ? String(card.dataset.commentId || '') : '';
      }
      requestDeleteComment(commentId);
      return;
    }
  });
}

Array.from(document.querySelectorAll('.category-item')).forEach((button) => {
  button.addEventListener('click', () => {
    const category = button.dataset.category || '分类频道';
    const localResults = searchMarketPosts(category);
    openSubpageListPage({
      title: category,
      subtitle: '分类频道',
      description: '该频道会展示对应主题的高赞帖子与问答。',
      items: localResults,
      sourceType: 'search',
      emptyText: '暂无该分类内容'
    });
  });
});

if (imageViewer) {
  imageViewer.addEventListener('click', (event) => {
    const target = event.target;
    if (!target) {
      return;
    }
    if (target === imageViewer || target === imageViewerImg || target.classList.contains('image-viewer-backdrop')) {
      closeImageViewer();
    }
  });
}

if (imageViewerClose) {
  imageViewerClose.addEventListener('click', closeImageViewer);
}

Array.from(document.querySelectorAll('.stat-item')).forEach((button) => {
  button.addEventListener('click', () => {
    const action = button.dataset.statAction || 'stats';
    const title = action === 'likedPosts' ? '我的获赞' : '我的帖子';
    if (action === 'likedPosts') {
      void openLikedPostsPage();
    } else {
      void openMyPostsPage();
    }
  });
});

Array.from(document.querySelectorAll('.menu-row, .profile-public-action[data-menu-action]')).forEach((button) => {
  button.addEventListener('click', () => {
    const action = button.dataset.menuAction || '';
    const label = button.querySelector('span') ? button.querySelector('span').textContent : '功能入口';
    if (action === 'myPosts') {
      void openMyPostsPage();
      return;
    }
    if (action === 'likedPosts') {
      void openLikedPostsPage();
      return;
    }
    if (action === 'publicName') {
      openPublicNameSheet();
      return;
    }
    if (action === 'wechatBind') {
      openWechatAuthPage();
      return;
    }
    openSubpageSheet({
      title: label || '功能入口',
      subtitle: '我的设置',
      body: `<p>该功能已切换到独立页面，后续接入服务接口与管理配置。</p>`,
      actionLabel: '',
      action: null
    });
  });
});

detailTabButtons.forEach((tab) => {
  tab.addEventListener('click', () => {
    const next = tab.dataset.detailTab === 'saved' ? 'saved' : 'likes';
    activeDetailTab = next;
    renderDetailTabs();
    detailSheetTitle.textContent = next === 'likes' ? '收到的赞' : '收藏列表';
    void loadInboxDetail(next).then(() => {
      renderInboxDetailList();
    });
    void markInboxRead(next);
    renderInboxDetailList();
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && detailSheet && !detailSheet.hidden) {
    closeInboxDetailSheet();
  }

  if (event.key === 'Escape' && postDetailSheet && !postDetailSheet.hidden) {
    closePostDetailSheet();
  }

  if (event.key === 'Escape' && searchResultSheet && !searchResultSheet.hidden) {
    closeSearchResultSheet();
  }

  if (event.key === 'Escape' && subpageSheet && !subpageSheet.hidden) {
    closeSubpageSheet();
  }

  if (event.key === 'Escape' && errandSheet && !errandSheet.hidden) {
    closeErrandPage();
  }

  if (event.key === 'Escape' && crossGroupSheet && !crossGroupSheet.hidden) {
    closeCrossGroupPage();
  }

  if (event.key === 'Escape' && commentSheet && !commentSheet.hidden) {
    closeCommentSheet();
  }

  if (event.key === 'Escape' && wikiDetailSheet && !wikiDetailSheet.hidden) {
    closeWikiDetailSheet();
  }

  if (event.key === 'Escape' && eduSheet && !eduSheet.hidden) {
    closeEduSheet();
  }

  if (event.key === 'Escape' && postComposerSheet && !postComposerSheet.hidden) {
    closePostComposer();
  }

  if (event.key === 'Escape' && imageViewer && !imageViewer.hidden) {
    closeImageViewer();
  }
});

document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    clearIdleTimer();
    clearUnreadPollingTimer();
    return;
  }

  setUserIdle(false);
  resetIdleCountdown();
  void refreshVisibleClientState({ force: true });
  resumeUnreadPolling({ resetBackoff: true });
});

if (copyUsageBtn) {
  copyUsageBtn.addEventListener('click', async () => {
    const content = [
      '1. “搜索”仅用于论坛帖子检索，并支持最近搜索与排序。',
      '2. “知识库”页仅基于知识库回答，并提供可点击来源。',
      '3. “我的”页可查看消息中心详情与教务入口。',
      '4. 首页优质帖子会进入知识库自进化队列。'
    ].join('\n');

    const fallbackCopy = () => {
      const textArea = document.createElement('textarea');
      textArea.value = content;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
    };

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(content);
      } else {
        fallbackCopy();
      }

      const old = copyUsageBtn.textContent;
      copyUsageBtn.textContent = '已复制';
      setTimeout(() => {
        copyUsageBtn.textContent = old;
      }, 1200);
    } catch (error) {
      fallbackCopy();
      copyUsageBtn.textContent = '已复制';
      setTimeout(() => {
        copyUsageBtn.textContent = '复制使用说明';
      }, 1200);
    }
  });
}

const weekdayMap = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
const now = new Date();
if (todaySentence) {
  todaySentence.textContent = `${weekdayMap[now.getDay()]} · ${now.getMonth() + 1}月${now.getDate()}日，欢迎回来`;
}
syncHeaderGreeting();

// Initial render
applyLikedStateToLocalFeed();
setActiveFeedFilter(appState.activeFeedFilter || 'all');
renderHomeHotTopics();
setSearchSort(appState.searchSort || 'hot', false);
renderRecentSearches();

if (marketQuery) {
  marketQuery.value = appState.lastSearch || '';
}
void runMarketSearch({ persistRecent: false, openResultPage: false });

renderErrandSummary();
renderWikiHistory();
syncKnowledgeComposerUi();
renderProfileInbox();
updateProfileDot();
setActiveView(appState.lastTab || 'home');
setCommentComposerState();
updateCommentReplyMeta();

setNetworkHint(API_CONFIG.enabled ? (navigator.onLine ? 'online' : 'offline') : 'local');

async function bootstrapClientAuth() {
  let usedWechatCode = false;
  try {
    const params = new URLSearchParams(window.location.search || '');
    const wxCode = String(params.get('wx_code') || '').trim();
    const wxName = String(params.get('wx_name') || '').trim();
    if (wxCode) {
      const ok = await loginWithWechatCode(wxCode, wxName);
      if (ok) {
        usedWechatCode = true;
      }
    }
  } catch (error) {
    // ignore
  }

  if (!usedWechatCode) {
    await ensureClientSession();
  }
  await hydrateRemoteState();
}

if (typeof window !== 'undefined') {
  window.CampusClientAuth = {
    loginWithWechatCode,
    bindWechatByCode,
    ensureClientSession,
    logoutClient,
    getSession() {
      return {
        userId: Number(appState.clientAuth.userId || 0),
        username: String(appState.clientAuth.username || ''),
        displayName: String(appState.clientAuth.displayName || ''),
        token: String(appState.clientAuth.token || ''),
        refreshToken: String(appState.clientAuth.refreshToken || '')
      };
    }
  };
}

void bootstrapClientAuth();
startUnreadPolling();

document.addEventListener('pointerdown', handleUserActivity, { passive: true });
document.addEventListener('touchstart', handleUserActivity, { passive: true });
document.addEventListener('scroll', handleUserActivity, { passive: true });
document.addEventListener('keydown', handleUserActivity);

window.addEventListener('focus', () => {
  void refreshVisibleClientState({ force: true });
  handleUserActivity();
  resumeUnreadPolling({ resetBackoff: true });
});

window.addEventListener('online', () => {
  setNetworkHint('online');
  showToast('网络已恢复，正在同步消息');
  setUserIdle(false);
  resetIdleCountdown();
  void hydrateRemoteState();
  resumeUnreadPolling({ immediate: true, resetBackoff: true });
});

window.addEventListener('offline', () => {
  setNetworkHint('offline');
  showToast('当前离线，已切换本地模式');
  clearUnreadPollingTimer();
});

function openWechatAuthPage() {
  openSubpageSheet({
    title: '账号互通',
    subtitle: '小程序与网页端共用同一账号',
    body: `
      <div class="wechat-auth-panel">
        <div class="wechat-auth-hero">
          <strong>微信互通登录</strong>
          <p>网页端会接入你在小程序里的同一个账号，帖子、收藏、消息和知识对话记录都会保持联通。</p>
        </div>
        <div class="wechat-auth-steps">
          <div class="wechat-auth-step"><span>1</span><p>打开小程序“我的”页，进入“网页互通登录”。</p></div>
          <div class="wechat-auth-step"><span>2</span><p>复制小程序生成的一次性登录码。</p></div>
          <div class="wechat-auth-step"><span>3</span><p>把登录码粘贴到这里，完成网页端登录。</p></div>
        </div>
        <input id="webLoginCodeInput" type="text" maxlength="12" placeholder="请输入小程序生成的登录码" />
        <div class="wechat-auth-benefits">
          <span class="wechat-auth-benefit">同账号</span>
          <span class="wechat-auth-benefit">同收藏</span>
          <span class="wechat-auth-benefit">同消息</span>
          <span class="wechat-auth-benefit">同知识记录</span>
        </div>
      </div>
    `,
    actionLabel: '登录网页',
    action: () => {
      const input = subpageBody ? subpageBody.querySelector('#webLoginCodeInput') : null;
      const code = String(input ? input.value : '').trim();
      if (!code) {
        showToast('请先输入登录码');
        return false;
      }
      void (async () => {
        const data = await apiAdapter.exchangeWebLoginCode(code);
        if (!data || !appState.clientAuth || !appState.clientAuth.token) {
          showToast('登录码无效或已过期');
          return;
        }
        closeSubpageSheet();
        await hydrateRemoteState();
        showToast('网页账号已与小程序互通');
      })();
      return false;
    }
  });
}
