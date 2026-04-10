from typing import Literal

from pydantic import BaseModel, Field


class ClientLoginRequest(BaseModel):
    username: str
    password: str


class ClientRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    display_name: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=6, max_length=64)


class ClientLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    display_name: str
    public_name: str


class ClientMeResponse(BaseModel):
    user_id: int
    username: str
    display_name: str
    public_name: str
    role: str
    status: str


class FeedItem(BaseModel):
    id: str
    category: str
    author_id: int
    author: str
    avatar: str
    level: str
    time: str
    title: str
    content: str
    tags: list[str]
    likes: int
    comments: int
    liked: bool
    saved: bool = False
    commented: bool
    adopted: bool
    knowledge_ready: bool = False
    knowledge_review_decision: str = ""
    knowledge_review_reason: str = ""
    image_url: str | None = None
    comments_preview: list[str] = Field(default_factory=list)
    can_delete: bool = False


class FeedListResponse(BaseModel):
    items: list[FeedItem]


class ToggleLikeRequest(BaseModel):
    post_id: str
    liked: bool


class ToggleLikeResponse(BaseModel):
    liked: bool
    likes: int


class ToggleSaveRequest(BaseModel):
    post_id: str
    saved: bool


class ToggleSaveResponse(BaseModel):
    saved: bool


class CommentItem(BaseModel):
    id: str
    author_id: int
    author: str
    content: str
    time: str
    created_at: str | None = None
    image_url: str | None = None
    likes: int = 0
    liked: bool = False
    parent_comment_id: str | None = None
    reply_to_author: str | None = None
    can_delete: bool = False


class CommentListResponse(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int = 0
    has_more: bool = False
    items: list[CommentItem]


class CreateCommentRequest(BaseModel):
    post_id: str
    content: str = Field(default="", max_length=500)
    client_id: str | None = None
    reply_to_comment_id: str | None = None
    reply_to_author: str | None = None


class CreateCommentResponse(CommentItem):
    pass


class ToggleCommentLikeRequest(BaseModel):
    comment_id: str
    liked: bool


class ToggleCommentLikeResponse(BaseModel):
    comment_id: str
    liked: bool
    likes: int


class DeleteCommentRequest(BaseModel):
    post_id: str
    comment_id: str


class DeleteCommentResponse(BaseModel):
    post_id: str
    comment_id: str
    deleted: bool
    deleted_count: int = 1
    deleted_ids: list[str] = Field(default_factory=list)


class CreatePostRequest(BaseModel):
    category: str = Field(default="study")
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=2000)
    tags: list[str] = Field(default_factory=list)


class CreatePostResponse(FeedItem):
    pass


class DeletePostRequest(BaseModel):
    post_id: str


class DeletePostResponse(BaseModel):
    post_id: str
    deleted: bool


class SearchPostItem(BaseModel):
    id: str
    post_id: str = ""
    title: str
    snippet: str
    content: str | None = None
    meta: str
    updated_at: str
    hot_score: int
    likes: int
    comments: int
    keywords: list[str]


class SearchPostsResponse(BaseModel):
    page: int = 1
    page_size: int = 30
    total: int = 0
    has_more: bool = False
    items: list[SearchPostItem]


class SearchRecentResponse(BaseModel):
    keywords: list[str]


class SearchRecentCreateRequest(BaseModel):
    keyword: str


class KnowledgeAskRequest(BaseModel):
    query: str
    history: list[dict] = Field(default_factory=list)
    deep_thinking: bool = False


class KnowledgeRelatedAnswerItem(BaseModel):
    id: str
    title: str
    snippet: str
    source_type: str = "kb"
    jump_url: str = ""
    score: float = 0.0


class KnowledgeAskResponse(BaseModel):
    answer: str
    route: str
    route_label: str
    source: str
    citations: list[dict] = Field(default_factory=list)
    related_answers: list[KnowledgeRelatedAnswerItem] = Field(default_factory=list)
    rerank_used: bool = False


class ClientRefreshRequest(BaseModel):
    refresh_token: str


class ClientLogoutRequest(BaseModel):
    refresh_token: str | None = None


class WechatLoginRequest(BaseModel):
    code: str
    display_name: str | None = None


class WechatBindRequest(BaseModel):
    code: str


class WebLoginCodeResponse(BaseModel):
    code: str
    expires_in: int
    expires_at: str


class WebLoginExchangeRequest(BaseModel):
    code: str = Field(min_length=4, max_length=16)


class UnreadCountResponse(BaseModel):
    likes_unread: int
    saved_unread: int
    likes_total: int = 0
    saved_total: int = 0


class MessageItem(BaseModel):
    id: str
    main: str
    meta: str
    post_id: str
    source_type: str
    saved: bool = False


class MessageListResponse(BaseModel):
    items: list[MessageItem]


class MarkReadRequest(BaseModel):
    type: Literal["likes", "saved", "all"]


class ProfileSummaryResponse(BaseModel):
    name: str
    public_name: str
    meta: str
    bind_state: str
    wechat_bound: bool = False
    posts: int
    likes: int
    feed_posts: int = 0
    errand_posts: int = 0
    likes_unread: int = 0


class ProfileSettingsResponse(BaseModel):
    display_name: str
    public_name: str
    bind_state: str
    wechat_bound: bool = False


class UpdatePublicNameRequest(BaseModel):
    public_name: str = Field(min_length=1, max_length=24)


class UpdatePublicNameResponse(BaseModel):
    public_name: str


class HomeHotTopicItem(BaseModel):
    id: str
    title: str
    heat: str


class HomeHotTopicResponse(BaseModel):
    items: list[HomeHotTopicItem]


class EduOverviewResponse(BaseModel):
    student_name: str
    student_id: str
    total_score: float
    gpa: float
    passed_courses: int
    failed_courses: int
    retake_courses: int
    term: str
    available_terms: list[str] = Field(default_factory=list)
    current_week: int = 1
    total_weeks: int = 18
    campuses: list[str] = Field(default_factory=list)


class EduGradeItem(BaseModel):
    course_name: str
    credit: float
    grade_point: float
    score: int
    status: str


class EduGradeListResponse(BaseModel):
    term: str
    terms: list[str] = Field(default_factory=list)
    term_credit: float = 0.0
    term_gpa: float = 0.0
    passed_count: int = 0
    pending_count: int = 0
    items: list[EduGradeItem]


class EduExamItem(BaseModel):
    course_name: str
    exam_type: str
    term: str
    exam_date: str
    exam_time: str
    exam_location: str
    exam_status: str


class EduExamListResponse(BaseModel):
    items: list[EduExamItem]


class EduScheduleItem(BaseModel):
    weekday: int
    section: int
    section_span: int = 1
    course_name: str
    location: str
    teacher: str
    weeks: str


class EduScheduleResponse(BaseModel):
    term: str = ""
    week_no: int
    weeks: list[int] = Field(default_factory=list)
    items: list[EduScheduleItem]


class EduFreeClassroomItem(BaseModel):
    building: str
    room: str
    idle_percent: int
    campus: str
    recommended: bool = False


class EduFreeClassroomResponse(BaseModel):
    campus: str
    campuses: list[str] = Field(default_factory=list)
    building: str = ""
    buildings: list[str] = Field(default_factory=list)
    items: list[EduFreeClassroomItem]


class ErrandActionItem(BaseModel):
    key: str
    label: str
    tone: str = "ghost"


class ErrandTimelineItem(BaseModel):
    key: str
    label: str
    value: str


class ErrandTaskItem(BaseModel):
    id: str
    task_type: str
    tag: str
    title: str
    reward: str
    time: str
    pickup_location: str
    destination: str
    location_summary: str
    note: str
    publisher_id: int
    publisher_name: str
    publisher_contact: str
    runner_id: int | None = None
    runner_name: str = ""
    runner_contact: str = ""
    status: str
    status_label: str
    status_tone: str
    relative_text: str
    created_at: str = ""
    accepted_at: str = ""
    delivered_at: str = ""
    confirmed_at: str = ""
    primary_action: ErrandActionItem
    timeline: list[ErrandTimelineItem] = Field(default_factory=list)
    can_delete: bool = False
    source_type: str = "errand"


class ErrandListResponse(BaseModel):
    items: list[ErrandTaskItem]


class CreateErrandRequest(BaseModel):
    task_type: str = Field(default="quick", max_length=32)
    title: str = Field(min_length=1, max_length=120)
    reward: str = Field(min_length=1, max_length=32)
    time: str = Field(min_length=1, max_length=64)
    pickup_location: str = Field(min_length=1, max_length=128)
    destination: str = Field(min_length=1, max_length=128)
    note: str = Field(default="", max_length=500)
    contact: str = Field(min_length=1, max_length=128)


class CreateErrandResponse(ErrandTaskItem):
    pass


class UpdateErrandStatusRequest(BaseModel):
    task_id: str
    action: Literal["claim", "delivered", "confirm", "cancel", "delete"]


class UpdateErrandStatusResponse(BaseModel):
    item: ErrandTaskItem
    message: str
