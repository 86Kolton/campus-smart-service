import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import (
    CommentListResponse,
    CreateCommentRequest,
    CreateCommentResponse,
    CreatePostRequest,
    CreatePostResponse,
    DeleteCommentRequest,
    DeleteCommentResponse,
    DeletePostRequest,
    DeletePostResponse,
    FeedItem,
    FeedListResponse,
    HomeHotTopicResponse,
    ToggleCommentLikeRequest,
    ToggleCommentLikeResponse,
    ToggleLikeRequest,
    ToggleLikeResponse,
    ToggleSaveRequest,
    ToggleSaveResponse,
)
from app.services.comment_service import comment_service
from app.services.post_service import post_service
from app.services.upload_service import upload_service

router = APIRouter()


def _parse_tags(tags_raw: str | None) -> list[str]:
    if not tags_raw:
        return []
    text = str(tags_raw).strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except Exception:
        pass
    return [item.strip() for item in text.split(",") if item.strip()]


def _map_service_error(exc: ValueError) -> HTTPException:
    code = str(exc)
    if code == "post_rate_limit_30m_3":
        return HTTPException(status_code=429, detail="post_rate_limit_30m_3")
    if code in {"post_title_required", "post_content_required", "comment_content_required"}:
        return HTTPException(status_code=422, detail=code)
    if code in {"invalid_reply_target"}:
        return HTTPException(status_code=400, detail=code)
    if code in {"post_not_found", "comment_not_found"}:
        return HTTPException(status_code=404, detail=code)
    if code in {"comment_delete_forbidden", "post_delete_forbidden"}:
        return HTTPException(status_code=403, detail=code)
    if code in {"image_too_large", "image_format_not_supported", "image_mime_not_supported"}:
        return HTTPException(status_code=422, detail=code)
    return HTTPException(status_code=400, detail=code)


@router.get("/feed/list", response_model=FeedListResponse)
async def list_feed(
    filter: str = Query(default="all"),
    identity: ClientIdentity = Depends(require_client_identity),
) -> FeedListResponse:
    return FeedListResponse(items=post_service.list_posts(filter_name=filter, user_id=identity.user_id))


@router.get("/feed/post", response_model=FeedItem)
async def get_feed_post(
    post_id: str,
    identity: ClientIdentity = Depends(require_client_identity),
) -> FeedItem:
    item = post_service.get_post(post_id=post_id, user_id=identity.user_id)
    if not item:
        raise HTTPException(status_code=404, detail="post_not_found")
    return FeedItem(**item)


@router.post("/feed/like", response_model=ToggleLikeResponse)
async def toggle_like(
    payload: ToggleLikeRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> ToggleLikeResponse:
    return ToggleLikeResponse(
        **post_service.toggle_like(post_id=payload.post_id, liked=payload.liked, user_id=identity.user_id)
    )


@router.post("/feed/save", response_model=ToggleSaveResponse)
async def toggle_save(
    payload: ToggleSaveRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> ToggleSaveResponse:
    return ToggleSaveResponse(
        **post_service.toggle_save(post_id=payload.post_id, saved=payload.saved, user_id=identity.user_id)
    )


@router.post("/feed/post/create", response_model=CreatePostResponse)
async def create_post(
    payload: CreatePostRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> CreatePostResponse:
    try:
        row = post_service.create_post(
            category=payload.category,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
            author_id=identity.user_id,
            image_meta=None,
        )
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return CreatePostResponse(**row)


@router.post("/feed/post/create-with-image", response_model=CreatePostResponse)
async def create_post_with_image(
    category: str = Form(default="study"),
    title: str = Form(...),
    content: str = Form(...),
    tags: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    identity: ClientIdentity = Depends(require_client_identity),
) -> CreatePostResponse:
    image_meta = None
    if image:
        raw = await image.read()
        try:
            image_meta = upload_service.save_image(
                content=raw,
                file_name=image.filename or "post.jpg",
                mime_type=image.content_type or "",
                scope="posts",
            )
        except ValueError as exc:
            raise _map_service_error(exc) from exc

    try:
        row = post_service.create_post(
            category=category,
            title=title,
            content=content,
            tags=_parse_tags(tags),
            author_id=identity.user_id,
            image_meta=image_meta,
        )
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return CreatePostResponse(**row)


@router.get("/feed/comments", response_model=CommentListResponse)
async def list_comments(
    post_id: str,
    page: int = 1,
    page_size: int = 20,
    identity: ClientIdentity = Depends(require_client_identity),
) -> CommentListResponse:
    items = comment_service.list_comments(post_id=post_id, user_id=identity.user_id)
    start = max(0, (page - 1) * page_size)
    end = start + page_size
    sliced = items[start:end]
    total = len(items)
    return CommentListResponse(
        page=page,
        page_size=page_size,
        total=total,
        has_more=end < total,
        items=sliced,
    )


@router.post("/feed/comment/create", response_model=CreateCommentResponse)
async def create_comment(
    payload: CreateCommentRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> CreateCommentResponse:
    try:
        row = comment_service.create_comment(
            post_id=payload.post_id,
            content=payload.content,
            client_id=payload.client_id,
            user_id=identity.user_id,
            image_meta=None,
            reply_to_comment_id=payload.reply_to_comment_id,
            reply_to_author=payload.reply_to_author,
        )
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return CreateCommentResponse(**row)


@router.post("/feed/comment/create-with-image", response_model=CreateCommentResponse)
async def create_comment_with_image(
    post_id: str = Form(...),
    content: str = Form(default=""),
    client_id: str | None = Form(default=None),
    reply_to_comment_id: str | None = Form(default=None),
    reply_to_author: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    identity: ClientIdentity = Depends(require_client_identity),
) -> CreateCommentResponse:
    image_meta = None
    if image:
        raw = await image.read()
        try:
            image_meta = upload_service.save_image(
                content=raw,
                file_name=image.filename or "comment.jpg",
                mime_type=image.content_type or "",
                scope="comments",
            )
        except ValueError as exc:
            raise _map_service_error(exc) from exc

    try:
        row = comment_service.create_comment(
            post_id=post_id,
            content=content,
            client_id=client_id,
            user_id=identity.user_id,
            image_meta=image_meta,
            reply_to_comment_id=reply_to_comment_id,
            reply_to_author=reply_to_author,
        )
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return CreateCommentResponse(**row)


@router.post("/feed/comment/like", response_model=ToggleCommentLikeResponse)
async def toggle_comment_like(
    payload: ToggleCommentLikeRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> ToggleCommentLikeResponse:
    try:
        row = comment_service.toggle_comment_like(
            comment_id=payload.comment_id,
            liked=payload.liked,
            user_id=identity.user_id,
        )
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return ToggleCommentLikeResponse(**row)


@router.post("/feed/comment/delete", response_model=DeleteCommentResponse)
async def delete_comment(
    payload: DeleteCommentRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> DeleteCommentResponse:
    try:
        row = comment_service.delete_comment(
            post_id=payload.post_id,
            comment_id=payload.comment_id,
            user_id=identity.user_id,
        )
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return DeleteCommentResponse(**row)


@router.post("/feed/post/delete", response_model=DeletePostResponse)
async def delete_post(
    payload: DeletePostRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> DeletePostResponse:
    try:
        row = post_service.delete_post(post_id=payload.post_id, user_id=identity.user_id)
    except ValueError as exc:
        raise _map_service_error(exc) from exc
    return DeletePostResponse(**row)


@router.get("/home/hot-topics", response_model=HomeHotTopicResponse)
async def home_hot_topics(_identity: ClientIdentity = Depends(require_client_identity)) -> HomeHotTopicResponse:
    items = [
        {"id": "hot-1", "title": "二食堂错峰窗口实测", "heat": "9.8k"},
        {"id": "hot-2", "title": "A1-307 晚间自习位反馈", "heat": "8.6k"},
        {"id": "hot-3", "title": "周三调课通知集中帖", "heat": "7.9k"},
    ]
    return HomeHotTopicResponse(items=items)


@router.get("/profile/my-posts", response_model=FeedListResponse)
async def profile_my_posts(identity: ClientIdentity = Depends(require_client_identity)) -> FeedListResponse:
    return FeedListResponse(items=post_service.list_posts_by_author(user_id=identity.user_id))


@router.get("/profile/liked-posts", response_model=FeedListResponse)
async def profile_liked_posts(identity: ClientIdentity = Depends(require_client_identity)) -> FeedListResponse:
    return FeedListResponse(items=post_service.list_liked_posts(user_id=identity.user_id))

