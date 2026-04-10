from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminLoginPolicyResponse(BaseModel):
    max_attempts: int
    lock_minutes: int
    window_minutes: int


class DashboardResponse(BaseModel):
    knowledge_base_count: int
    document_count: int
    chunk_count: int
    today_qa_count: int
    failed_task_count: int


class KnowledgeBaseCreateRequest(BaseModel):
    name: str
    description: str = ""


class KnowledgeBaseItem(BaseModel):
    id: int
    name: str
    description: str
    status: str
    doc_count: int
    chunk_count: int


class KnowledgeBaseListResponse(BaseModel):
    items: list[KnowledgeBaseItem]


class IngestTaskItem(BaseModel):
    id: int
    kb_id: int
    document_id: int
    task_type: str
    status: str
    retry_count: int
    error_message: str
    created_at: str


class IngestTaskListResponse(BaseModel):
    items: list[IngestTaskItem]


class DocumentItem(BaseModel):
    id: int
    kb_id: int
    file_name: str
    file_ext: str
    file_size: int
    mime_type: str
    storage_path: str
    status: str
    chunk_count: int
    error_message: str
    uploaded_by: int
    created_at: str


class DocumentListResponse(BaseModel):
    items: list[DocumentItem]


class QALogItem(BaseModel):
    id: int
    query_text: str
    answer_text: str
    model_name: str
    latency_ms: int
    status: str
    created_at: str


class QALogListResponse(BaseModel):
    items: list[QALogItem]


class EvolutionSyncResponse(BaseModel):
    synced_posts: int
    skipped_posts: int
    accepted_posts: int = 0
    rejected_posts: int = 0
    indexed_documents: int = 0
    kb_id: int
    limit: int | None = None
    pending_posts: int = 0
    remaining_posts: int = 0
    reviewed_posts_skipped: int = 0


class EvolutionReviewItem(BaseModel):
    id: int
    kb_id: int
    post_id: str
    post_title: str
    decision: str
    overall_score: int
    reviewer_model: str
    reason: str
    document_id: int | None = None
    created_at: str
    detail: dict[str, object] = Field(default_factory=dict)


class EvolutionReviewListResponse(BaseModel):
    items: list[EvolutionReviewItem]


class AdoptCommentRequest(BaseModel):
    post_id: str
    comment_id: str
    prune_other_comments: bool = True
    hard_delete: bool = False


class AdoptCommentResponse(BaseModel):
    post_id: str
    comment_id: str
    adopted: bool
    pruned_count: int = 0
    hard_deleted: bool = False


class CleanupStalePostsResponse(BaseModel):
    days: int
    deleted_posts: int
    deleted_comments: int
    deleted_post_assets: int
    deleted_comment_assets: int


class AdoptionRecord(BaseModel):
    post_id: str
    post_title: str
    post_author_name: str
    adopted_comment_id: str
    adopted_user_name: str
    adopted_comment_text: str
    adopted_at: str


class AdoptionListResponse(BaseModel):
    items: list[AdoptionRecord]


class DevCheckItem(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class DevSelfCheckResponse(BaseModel):
    items: list[DevCheckItem]


class DevStatusResponse(BaseModel):
    app_env: str
    knowledge_base_count: int
    document_count: int
    failed_task_count: int
    qa_log_count: int
    qdrant_configured: bool
    qa_configured: bool
    rerank_configured: bool
    wechat_configured: bool
    embedding_provider: str
    embedding_configured: bool
    now_iso: str


class DevConfigResponse(BaseModel):
    masked: dict[str, str]
    editable_keys: list[str]


class DevConfigUpdateRequest(BaseModel):
    values: dict[str, str]


class DevClientDebugTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    display_name: str
    public_name: str
