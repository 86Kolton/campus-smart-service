from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

os.environ["POSTGRES_URL"] = "sqlite:///./pytest_e2e.db"
os.environ["QDRANT_URL"] = ""
os.environ["QA_BASE_URL"] = ""
os.environ["QA_API_KEY"] = ""
os.environ["QA_MODEL"] = ""
os.environ["DOCUMENT_OCR_BASE_URL"] = ""
os.environ["DOCUMENT_OCR_API_KEY"] = ""
os.environ["DOCUMENT_OCR_MODEL"] = ""

from app.core.config import settings
from app.core.passwords import PBKDF2_ALGORITHM, hash_password, needs_password_rehash, verify_password
from app.core.security import decode_access_token
from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.message import MessageNotification
from app.models.knowledge import KnowledgeDocument
from app.models.post import Post
from app.models.post_adoption import PostAdoption
from app.models.post_like import PostLike
from app.models.post_save import PostSave
from app.models.user import User

DB_FILE = Path("pytest_e2e.db")
if DB_FILE.exists():
    DB_FILE.unlink()

from app.main import app  # noqa: E402
from app.rag.parser.document_parser import document_parser  # noqa: E402
from app.rag.pipeline import rag_pipeline  # noqa: E402
from app.services.document_upload_service import MAX_DOCUMENT_BYTES, document_upload_service  # noqa: E402
from app.services.evolution_service import evolution_service  # noqa: E402
from app.services.knowledge_cache_service import knowledge_cache_service  # noqa: E402
from app.services.maintenance_service import maintenance_service  # noqa: E402
from app.services.qa_provider import qa_provider  # noqa: E402
from app.services.wechat_service import wechat_service  # noqa: E402
from scripts.seed_hbu_kb import seed_local_documents  # noqa: E402


def _zip_bytes(files: dict[str, str]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _minimal_pdf_bytes(text: str = "Campus PDF") -> bytes:
    stream = f"BT /F1 18 Tf 72 720 Td ({text}) Tj ET".encode("latin1")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        b"5 0 obj\n<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream\nendobj\n",
    ]
    payload = b"%PDF-1.4\n"
    offsets = []
    for item in objects:
        offsets.append(len(payload))
        payload += item
    xref_offset = len(payload)
    payload += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        payload += f"{offset:010d} 00000 n \n".encode()
    payload += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    return payload


def _admin_credentials() -> tuple[str, str]:
    username = str(settings.admin_username or "").strip()
    password = str(settings.admin_password or "").strip()
    assert username and password, "admin credentials must be configured in backend/.env"
    return username, password


def _client_login(client: TestClient, username: str = "zhaoyi") -> dict:
    for password in ("demo", "demo123"):
        response = client.post(
            "/api/client/auth/login",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            return response.json()
    raise AssertionError(f"client login failed for {username}")


def _bind_wechat_for_test(client: TestClient, headers: dict[str, str], label: str) -> None:
    response = client.post(
        "/api/client/auth/wechat/bind",
        json={"code": f"pytest-bind-{label}-{uuid4().hex}"},
        headers=headers,
    )
    assert response.status_code == 200, response.text


def test_backend_e2e_flow() -> None:
    with TestClient(app) as client:
        seed_local_documents(kb_id=1, ensure_bootstrap=False, force_reindex=True)
        knowledge_cache_service.rebuild_chunks()

        health = client.get("/healthz")
        assert health.status_code == 200

        client_login = _client_login(client, username="zhaoyi")
        assert client_login.get("public_name")
        assert client_login.get("wechat_bound") is True
        client_token = str(client_login.get("access_token", ""))
        client_refresh = str(client_login.get("refresh_token", ""))
        assert client_token
        client_headers = {"Authorization": f"Bearer {client_token}"}

        feed = client.get("/api/client/feed/list", params={"filter": "all"}, headers=client_headers)
        assert feed.status_code == 200
        assert isinstance(feed.json().get("items"), list)
        feed_items = feed.json().get("items") or []
        if feed_items:
            first_feed_item = feed_items[0]
            assert "adopted" in first_feed_item
            assert "knowledge_ready" in first_feed_item
            assert "knowledge_review_decision" in first_feed_item
            assert "knowledge_review_reason" in first_feed_item

        create_post = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": "pytest e2e post",
                "content": "for regression",
                "tags": ["pytest", "e2e"],
            },
            headers=client_headers,
        )
        if create_post.status_code == 200:
            post_id = str(create_post.json().get("id", ""))
            assert post_id.startswith("p-")
        else:
            assert create_post.status_code == 429
            feed_items = feed.json().get("items", [])
            assert feed_items, "feed is empty and create post was rate-limited"
            post_id = str(feed_items[0].get("id", ""))
            assert post_id.startswith("p-")

        with SessionLocal() as db:
            next_post_id = int(db.scalar(select(func.max(Post.id))) or 0) + 1
            db.add(
                Post(
                    id=next_post_id,
                    author_id=int(client_login.get("user_id") or 1),
                    category="study",
                    title="pytest 跨校竞赛组队",
                    content="跨校同学一起互助，正在找组队伙伴。",
                    tags_json=json.dumps(["#跨校", "#互助", "#组队"], ensure_ascii=False),
                    likes_count=5,
                    comments_count=2,
                    status="published",
                    created_at=datetime.now(tz=timezone.utc),
                )
            )
            db.add(
                Post(
                    id=next_post_id + 1,
                    author_id=int(client_login.get("user_id") or 1),
                    category="study",
                    title="pytest 河北大学图书馆资源路线",
                    content="WEBVPN 校外访问和电子资源入口整理。",
                    tags_json=json.dumps(["#河北大学", "#图书馆", "#WEBVPN"], ensure_ascii=False),
                    likes_count=6,
                    comments_count=1,
                    status="published",
                    created_at=datetime.now(tz=timezone.utc),
                )
            )
            db.commit()

        cross_search = client.get(
            "/api/client/search/posts",
            params={"q": "跨校 组队", "sort": "hot"},
            headers=client_headers,
        )
        assert cross_search.status_code == 200
        assert any(item.get("title") == "pytest 跨校竞赛组队" for item in (cross_search.json().get("items") or []))

        compact_cross_search = client.get(
            "/api/client/search/posts",
            params={"q": "跨校组队", "sort": "hot"},
            headers=client_headers,
        )
        assert compact_cross_search.status_code == 200
        assert any(item.get("title") == "pytest 跨校竞赛组队" for item in (compact_cross_search.json().get("items") or []))

        mixed_search = client.get(
            "/api/client/search/posts",
            params={"q": "河北大学WEBVPN图书馆", "sort": "hot"},
            headers=client_headers,
        )
        assert mixed_search.status_code == 200
        assert any(item.get("title") == "pytest 河北大学图书馆资源路线" for item in (mixed_search.json().get("items") or []))

        # Multi-user isolation: user B can like/comment, cannot delete A's comment.
        user_b_name = f"user_b_{uuid4().hex[:8]}"
        b_register = client.post(
            "/api/client/auth/register",
            json={"username": user_b_name, "display_name": "userB", "password": "demo123"},
        )
        assert b_register.status_code == 200, b_register.text
        b_token = str(b_register.json().get("access_token", ""))
        b_headers = {"Authorization": f"Bearer {b_token}"}
        user_c_name = f"user_c_{uuid4().hex[:8]}"
        c_register = client.post(
            "/api/client/auth/register",
            json={"username": user_c_name, "display_name": "userC", "password": "demo123"},
        )
        assert c_register.status_code == 200, c_register.text
        c_token = str(c_register.json().get("access_token", ""))
        c_headers = {"Authorization": f"Bearer {c_token}"}

        unbound_post = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": "unbound user should not post",
                "content": "wechat binding is required before public writes",
                "tags": ["security"],
            },
            headers=b_headers,
        )
        assert unbound_post.status_code == 403
        assert unbound_post.json().get("detail") == "wechat_bind_required"

        unbound_like = client.post(
            "/api/client/feed/like",
            json={"post_id": post_id, "liked": True},
            headers=b_headers,
        )
        assert unbound_like.status_code == 403
        assert unbound_like.json().get("detail") == "wechat_bind_required"

        unbound_save = client.post(
            "/api/client/feed/save",
            json={"post_id": post_id, "saved": True},
            headers=b_headers,
        )
        assert unbound_save.status_code == 403
        assert unbound_save.json().get("detail") == "wechat_bind_required"

        unbound_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "unbound user should not comment", "client_id": "pytest-unbound"},
            headers=b_headers,
        )
        assert unbound_comment.status_code == 403
        assert unbound_comment.json().get("detail") == "wechat_bind_required"

        unbound_errand = client.post(
            "/api/client/errands",
            json={
                "task_type": "quick",
                "title": "unbound errand should fail",
                "reward": "5",
                "time": "soon",
                "pickup_location": "library",
                "destination": "dorm",
                "note": "security regression",
                "contact": "wechat",
            },
            headers=b_headers,
        )
        assert unbound_errand.status_code == 403
        assert unbound_errand.json().get("detail") == "wechat_bind_required"

        for edu_path in (
            "/api/client/edu/overview",
            "/api/client/edu/grades",
            "/api/client/edu/exams",
            "/api/client/edu/schedule",
            "/api/client/edu/free-classrooms",
        ):
            unbound_edu = client.get(
                edu_path,
                headers={**b_headers, "X-Edu-Session": "demo-edu-session"},
            )
            assert unbound_edu.status_code == 403
            assert unbound_edu.json().get("detail") == "wechat_bind_required"

        for private_path in (
            "/api/client/profile/summary",
            "/api/client/profile/settings",
            "/api/client/profile/my-posts",
            "/api/client/profile/liked-posts",
            "/api/client/messages/unread-count",
            "/api/client/messages/likes",
            "/api/client/messages/saved",
            "/api/client/errands/my",
        ):
            unbound_private = client.get(private_path, headers=b_headers)
            assert unbound_private.status_code == 403
            assert unbound_private.json().get("detail") == "wechat_bind_required"

        unbound_public_name = client.post(
            "/api/client/profile/public-name",
            json={"public_name": "未绑定同学"},
            headers=b_headers,
        )
        assert unbound_public_name.status_code == 403
        assert unbound_public_name.json().get("detail") == "wechat_bind_required"

        unbound_mark_read = client.post(
            "/api/client/messages/mark-read",
            json={"type": "likes"},
            headers=b_headers,
        )
        assert unbound_mark_read.status_code == 403
        assert unbound_mark_read.json().get("detail") == "wechat_bind_required"
        _bind_wechat_for_test(client, b_headers, "flow-b")

        a_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "comment by A", "client_id": "pytest-A"},
            headers=client_headers,
        )
        assert a_comment.status_code == 200
        a_comment_id = str(a_comment.json().get("id", ""))
        assert a_comment_id.startswith("c-")

        unbound_comment_like = client.post(
            "/api/client/feed/comment/like",
            json={"comment_id": a_comment_id, "liked": True},
            headers=c_headers,
        )
        assert unbound_comment_like.status_code == 403
        assert unbound_comment_like.json().get("detail") == "wechat_bind_required"

        b_like = client.post(
            "/api/client/feed/like",
            json={"post_id": post_id, "liked": True},
            headers=b_headers,
        )
        assert b_like.status_code == 200

        b_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "comment by B", "client_id": "pytest-B"},
            headers=b_headers,
        )
        assert b_comment.status_code == 200

        b_delete_forbidden = client.post(
            "/api/client/feed/comment/delete",
            json={"post_id": post_id, "comment_id": a_comment_id},
            headers=b_headers,
        )
        assert b_delete_forbidden.status_code == 403

        like_on = client.post(
            "/api/client/feed/like",
            json={"post_id": post_id, "liked": True},
            headers=client_headers,
        )
        assert like_on.status_code == 200
        assert like_on.json().get("liked") is True

        like_off = client.post(
            "/api/client/feed/like",
            json={"post_id": post_id, "liked": False},
            headers=client_headers,
        )
        assert like_off.status_code == 200
        assert like_off.json().get("liked") is False

        save_on = client.post(
            "/api/client/feed/save",
            json={"post_id": post_id, "saved": True},
            headers=client_headers,
        )
        assert save_on.status_code == 200
        assert save_on.json().get("saved") is True

        save_off = client.post(
            "/api/client/feed/save",
            json={"post_id": post_id, "saved": False},
            headers=client_headers,
        )
        assert save_off.status_code == 200
        assert save_off.json().get("saved") is False

        create_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "pytest comment", "client_id": "pytest-local-1"},
            headers=client_headers,
        )
        assert create_comment.status_code == 200
        comment_id = str(create_comment.json().get("id", ""))
        assert comment_id.startswith("c-")

        create_reply = client.post(
            "/api/client/feed/comment/create",
            json={
                "post_id": post_id,
                "content": "pytest nested reply",
                "client_id": "pytest-local-2",
                "reply_to_comment_id": comment_id,
                "reply_to_author": "@我",
            },
            headers=client_headers,
        )
        assert create_reply.status_code == 200
        reply_id = str(create_reply.json().get("id", ""))
        assert reply_id.startswith("c-")

        comment_like = client.post(
            "/api/client/feed/comment/like",
            json={"comment_id": comment_id, "liked": True},
            headers=client_headers,
        )
        assert comment_like.status_code == 200
        assert comment_like.json().get("liked") is True

        comment_unlike = client.post(
            "/api/client/feed/comment/like",
            json={"comment_id": comment_id, "liked": False},
            headers=client_headers,
        )
        assert comment_unlike.status_code == 200
        assert comment_unlike.json().get("liked") is False

        comment_list = client.get(
            "/api/client/feed/comments",
            params={"post_id": post_id, "page": 1, "page_size": 20},
            headers=client_headers,
        )
        assert comment_list.status_code == 200
        items = comment_list.json().get("items", [])
        assert any(str(row.get("id")) == comment_id for row in items)
        assert any(str(row.get("id")) == reply_id for row in items)

        comment_delete = client.post(
            "/api/client/feed/comment/delete",
            json={"post_id": post_id, "comment_id": comment_id},
            headers=client_headers,
        )
        assert comment_delete.status_code == 200
        assert comment_delete.json().get("deleted") is True
        assert int(comment_delete.json().get("deleted_count", 0)) >= 2
        deleted_ids = set(comment_delete.json().get("deleted_ids") or [])
        assert comment_id in deleted_ids
        assert reply_id in deleted_ids

        comment_list_after_delete = client.get(
            "/api/client/feed/comments",
            params={"post_id": post_id, "page": 1, "page_size": 20},
            headers=client_headers,
        )
        assert comment_list_after_delete.status_code == 200
        items_after = comment_list_after_delete.json().get("items", [])
        assert all(str(row.get("id")) != comment_id for row in items_after)
        assert all(str(row.get("id")) != reply_id for row in items_after)

        search = client.get(
            "/api/client/search/posts",
            params={"q": "pytest", "sort": "latest", "page": 1, "page_size": 10},
            headers=client_headers,
        )
        assert search.status_code == 200
        assert "items" in search.json()
        assert "total" in search.json()
        assert "has_more" in search.json()

        save_recent = client.post("/api/client/search/recent", json={"keyword": "pytest"}, headers=client_headers)
        assert save_recent.status_code == 200

        recent = client.get("/api/client/search/recent", headers=client_headers)
        assert recent.status_code == 200
        assert isinstance(recent.json().get("keywords"), list)

        messages = client.get("/api/client/messages/unread-count", headers=client_headers)
        assert messages.status_code == 200
        assert "likes_unread" in messages.json()
        assert "saved_unread" in messages.json()

        saved_messages = client.get("/api/client/messages/saved", headers=client_headers)
        assert saved_messages.status_code == 200
        assert isinstance(saved_messages.json().get("items"), list)

        profile = client.get("/api/client/profile/summary", headers=client_headers)
        assert profile.status_code == 200
        assert "name" in profile.json()
        assert "public_name" in profile.json()

        profile_settings = client.get("/api/client/profile/settings", headers=client_headers)
        assert profile_settings.status_code == 200
        assert profile_settings.json().get("public_name")

        update_public_name = client.post(
            "/api/client/profile/public-name",
            json={"public_name": "夜读观察员"},
            headers=client_headers,
        )
        assert update_public_name.status_code == 200
        assert update_public_name.json().get("public_name") == "夜读观察员"

        my_posts = client.get("/api/client/profile/my-posts", headers=client_headers)
        assert my_posts.status_code == 200
        assert isinstance(my_posts.json().get("items"), list)

        liked_posts = client.get("/api/client/profile/liked-posts", headers=client_headers)
        assert liked_posts.status_code == 200
        assert isinstance(liked_posts.json().get("items"), list)

        errands = client.get("/api/client/errands", headers=client_headers)
        assert errands.status_code == 200
        assert isinstance(errands.json().get("items"), list)

        create_errand = client.post(
            "/api/client/errands",
            json={
                "task_type": "quick",
                "title": "pytest 代取快递",
                "reward": "5",
                "time": "20 分钟内",
                "pickup_location": "南门驿站",
                "destination": "兰苑 2 号楼",
                "note": "测试任务",
                "contact": "站内私信 @夜读观察员",
            },
            headers=client_headers,
        )
        assert create_errand.status_code == 200
        errand_id = str(create_errand.json().get("id", ""))
        assert errand_id.startswith("e-")

        claim_errand = client.post(
            "/api/client/errands/action",
            json={"task_id": errand_id, "action": "claim"},
            headers=b_headers,
        )
        assert claim_errand.status_code == 200
        claimed_item = claim_errand.json().get("item", {})
        assert claimed_item.get("publisher_contact") == "站内私信 @夜读观察员"
        assert claimed_item.get("is_runner") is True
        assert claimed_item.get("can_view_contact") is True

        my_errands = client.get("/api/client/errands/my", headers=client_headers)
        assert my_errands.status_code == 200
        assert any(str(item.get("id")) == errand_id for item in (my_errands.json().get("items") or []))

        runner_my_errands = client.get("/api/client/errands/my", headers=b_headers)
        assert runner_my_errands.status_code == 200
        runner_match = [
            item for item in (runner_my_errands.json().get("items") or [])
            if str(item.get("id")) == errand_id
        ]
        assert runner_match
        assert runner_match[0].get("publisher_contact") == "站内私信 @夜读观察员"
        assert runner_match[0].get("is_runner") is True

        runner_pool_errands = client.get("/api/client/errands", headers=b_headers)
        assert runner_pool_errands.status_code == 200
        runner_pool_match = [
            item for item in (runner_pool_errands.json().get("items") or [])
            if str(item.get("id")) == errand_id
        ]
        assert runner_pool_match
        assert runner_pool_match[0].get("publisher_contact") == "站内私信 @夜读观察员"
        assert runner_pool_match[0].get("can_view_contact") is True

        create_second_errand = client.post(
            "/api/client/errands",
            json={
                "task_type": "delivery",
                "title": "pytest 再接一单",
                "reward": "6",
                "time": "30 分钟内",
                "pickup_location": "北门外卖架",
                "destination": "梅园 1 号楼",
                "note": "验证同一接单人可以接多个订单",
                "contact": "站内私信 @夜读观察员",
            },
            headers=client_headers,
        )
        assert create_second_errand.status_code == 200
        second_errand_id = str(create_second_errand.json().get("id", ""))
        assert second_errand_id.startswith("e-")

        claim_second_errand = client.post(
            "/api/client/errands/action",
            json={"task_id": second_errand_id, "action": "claim"},
            headers=b_headers,
        )
        assert claim_second_errand.status_code == 200
        assert claim_second_errand.json().get("item", {}).get("is_runner") is True

        runner_my_repeat = client.get("/api/client/errands/my", headers=b_headers)
        assert runner_my_repeat.status_code == 200
        runner_my_items = runner_my_repeat.json().get("items") or []
        runner_my_ids = {str(item.get("id")) for item in runner_my_items}
        assert {errand_id, second_errand_id}.issubset(runner_my_ids)
        for item in runner_my_items:
            if str(item.get("id")) in {errand_id, second_errand_id}:
                assert item.get("publisher_contact") == "站内私信 @夜读观察员"
                assert item.get("can_view_contact") is True

        stranger_errands = client.get("/api/client/errands", headers=c_headers)
        assert stranger_errands.status_code == 200
        stranger_match = [
            item for item in (stranger_errands.json().get("items") or [])
            if str(item.get("id")) == errand_id
        ]
        assert stranger_match
        assert stranger_match[0].get("publisher_contact") == "接单后可见"

        deliver_errand = client.post(
            "/api/client/errands/action",
            json={"task_id": errand_id, "action": "delivered"},
            headers=b_headers,
        )
        assert deliver_errand.status_code == 200, deliver_errand.text
        delivered_item = deliver_errand.json().get("item", {})
        assert delivered_item.get("status") == "waiting_confirm"
        assert delivered_item.get("publisher_contact") == "站内私信 @夜读观察员"

        runner_waiting_confirm = client.get("/api/client/errands/my", headers=b_headers)
        assert runner_waiting_confirm.status_code == 200
        waiting_match = [
            item for item in (runner_waiting_confirm.json().get("items") or [])
            if str(item.get("id")) == errand_id
        ]
        assert waiting_match
        assert waiting_match[0].get("status") == "waiting_confirm"
        assert waiting_match[0].get("publisher_contact") == "站内私信 @夜读观察员"

        confirm_errand = client.post(
            "/api/client/errands/action",
            json={"task_id": errand_id, "action": "confirm"},
            headers=client_headers,
        )
        assert confirm_errand.status_code == 200, confirm_errand.text

        runner_my_done = client.get("/api/client/errands/my", headers=b_headers)
        assert runner_my_done.status_code == 200
        runner_done_match = [
            item for item in (runner_my_done.json().get("items") or [])
            if str(item.get("id")) == errand_id
        ]
        assert runner_done_match
        assert runner_done_match[0].get("status") == "done"
        assert runner_done_match[0].get("publisher_contact") == "站内私信 @夜读观察员"

        knowledge = client.post(
            "/api/client/knowledge/ask",
            json={"query": "A1-307", "history": []},
            headers=client_headers,
        )
        assert knowledge.status_code == 200
        assert isinstance(knowledge.json().get("citations"), list)

        knowledge_deep = client.post(
            "/api/client/knowledge/ask",
            json={"query": "A1-307", "history": [], "deep_thinking": True},
            headers=client_headers,
        )
        assert knowledge_deep.status_code == 200
        assert "rerank_used" in knowledge_deep.json()

        knowledge_postal = client.post(
            "/api/client/knowledge/ask",
            json={"query": "河北大学邮编是多少", "history": []},
            headers=client_headers,
        )
        assert knowledge_postal.status_code == 200
        assert "071002" in str(knowledge_postal.json().get("answer", ""))
        assert knowledge_postal.json().get("citations")

        knowledge_isec = client.post(
            "/api/client/knowledge/ask",
            json={"query": "河北大学软件工程ISEC是什么", "history": []},
            headers=client_headers,
        )
        assert knowledge_isec.status_code == 200
        isec_payload = knowledge_isec.json()
        isec_citations = isec_payload.get("citations") or []
        assert any("intl.hbu.edu.cn" in str(item.get("jump_url", "")) for item in isec_citations)

        knowledge_course = client.post(
            "/api/client/knowledge/ask",
            json={"query": "选课", "history": []},
            headers=client_headers,
        )
        assert knowledge_course.status_code == 200
        course_answer = str(knowledge_course.json().get("answer", ""))
        assert course_answer
        assert "知识库中未检索到可支撑该问题的内容" not in course_answer

        knowledge_course_prefixed = client.post(
            "/api/client/knowledge/ask",
            json={"query": "娌冲寳澶у閫夎", "history": []},
            headers=client_headers,
        )
        assert knowledge_course_prefixed.status_code == 200
        prefixed_answer = str(knowledge_course_prefixed.json().get("answer", ""))
        assert prefixed_answer
        assert "淇℃伅涓嶈冻" not in prefixed_answer

        knowledge_greeting = client.post(
            "/api/client/knowledge/ask",
            json={"query": "你好", "history": []},
            headers=client_headers,
        )
        assert knowledge_greeting.status_code == 200
        assert "可以直接问我校区" in str(knowledge_greeting.json().get("answer", ""))

        web_login_code = client.post("/api/client/auth/web-login-code", headers=client_headers)
        assert web_login_code.status_code == 200
        code_value = str(web_login_code.json().get("code", ""))
        assert code_value

        web_login_exchange = client.post(
            "/api/client/auth/web-login-exchange",
            json={"code": code_value},
        )
        assert web_login_exchange.status_code == 200
        assert int(web_login_exchange.json().get("user_id", 0)) == int(client_login.get("user_id", 0))
        web_login_payload = web_login_exchange.json()
        assert web_login_payload.get("session_type") == "web"
        assert int(web_login_payload.get("expires_in", 0)) == 3600
        web_token = str(web_login_payload.get("access_token", ""))
        web_refresh_token = str(web_login_payload.get("refresh_token", ""))
        decoded_web_token = decode_access_token(web_token)
        assert decoded_web_token.get("sid") == "web"
        assert 3500 <= int(decoded_web_token.get("exp", 0)) - int(decoded_web_token.get("iat", 0)) <= 3700

        web_refresh_attempt = client.post(
            "/api/client/auth/refresh",
            json={"refresh_token": web_refresh_token},
        )
        assert web_refresh_attempt.status_code == 401
        assert web_refresh_attempt.json().get("detail") == "web_session_relogin_required"

        web_login_exchange_repeat = client.post(
            "/api/client/auth/web-login-exchange",
            json={"code": code_value},
        )
        assert web_login_exchange_repeat.status_code == 401

        logout_web_sessions = client.post("/api/client/auth/logout-web-sessions", headers=client_headers)
        assert logout_web_sessions.status_code == 200
        web_me_after_logout = client.get(
            "/api/client/auth/me",
            headers={"Authorization": f"Bearer {web_token}"},
        )
        assert web_me_after_logout.status_code == 401
        assert web_me_after_logout.json().get("detail") == "client_token_revoked"
        app_me_after_web_logout = client.get("/api/client/auth/me", headers=client_headers)
        assert app_me_after_web_logout.status_code == 200

        refresh = client.post(
            "/api/client/auth/refresh",
            json={"refresh_token": client_refresh},
        )
        if refresh.status_code == 200:
            refreshed_token = str(refresh.json().get("access_token", ""))
            assert refreshed_token
            client_headers = {"Authorization": f"Bearer {refreshed_token}"}
        else:
            assert refresh.status_code == 401
            refreshed_login = _client_login(client, username="zhaoyi")
            refreshed_token = str(refreshed_login.get("access_token", ""))
            assert refreshed_token
            client_headers = {"Authorization": f"Bearer {refreshed_token}"}

        wechat_login = client.post(
            "/api/client/auth/wechat/login",
            json={"code": "wxcode_e2e"},
        )
        assert wechat_login.status_code == 200

        wechat_bind = client.post(
            "/api/client/auth/wechat/bind",
            json={"code": "wxbind_e2e"},
            headers=client_headers,
        )
        assert wechat_bind.status_code == 200

        edu_guard = client.get("/api/client/edu/overview")
        assert edu_guard.status_code == 401

        edu_ok = client.get(
            "/api/client/edu/overview",
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_ok.status_code == 200
        edu_payload = edu_ok.json()
        assert edu_payload.get("student_id") == "20222605045"
        assert float(edu_payload.get("gpa", 0)) > 0
        assert len(edu_payload.get("available_terms") or []) >= 6
        assert len(edu_payload.get("campuses") or []) >= 3

        edu_grades = client.get(
            "/api/client/edu/grades",
            params={"term": "2024-2025春学期"},
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_grades.status_code == 200
        assert edu_grades.json().get("term") == "2024-2025春学期"
        assert len(edu_grades.json().get("terms") or []) >= 6
        assert float(edu_grades.json().get("term_credit", 0)) > 0
        assert len(edu_grades.json().get("items") or []) >= 6

        edu_schedule = client.get(
            "/api/client/edu/schedule",
            params={"week_no": 12},
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_schedule.status_code == 200
        assert int(edu_schedule.json().get("week_no", 0)) == 12
        assert 12 in (edu_schedule.json().get("weeks") or [])
        assert len(edu_schedule.json().get("items") or []) >= 4

        edu_exams = client.get(
            "/api/client/edu/exams",
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_exams.status_code == 200
        assert len(edu_exams.json().get("items") or []) >= 2

        edu_free_71 = client.get(
            "/api/client/edu/free-classrooms",
            params={"campus": "七一路校区"},
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_free_71.status_code == 200
        assert edu_free_71.json().get("campus") == "七一路校区"
        assert "A1座" in (edu_free_71.json().get("buildings") or [])
        assert len(edu_free_71.json().get("items") or []) >= 4

        edu_free_54 = client.get(
            "/api/client/edu/free-classrooms",
            params={"campus": "五四路校区"},
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_free_54.status_code == 200
        assert edu_free_54.json().get("campus") == "五四路校区"
        assert len(edu_free_54.json().get("items") or []) >= 3

        edu_free_building = client.get(
            "/api/client/edu/free-classrooms",
            params={"campus": "七一路校区", "building": "A4座"},
            headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
        )
        assert edu_free_building.status_code == 200
        assert edu_free_building.json().get("building") == "A4座"
        assert all(str(item.get("building")) == "A4座" for item in (edu_free_building.json().get("items") or []))

        admin_username, admin_password = _admin_credentials()
        login = client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": admin_password},
        )
        assert login.status_code == 200
        token = str(login.json().get("access_token", ""))
        assert token
        admin_headers = {"Authorization": f"Bearer {token}"}

        admin_endpoints = [
            ("/api/admin/dashboard/summary", "GET"),
            ("/api/admin/kb", "GET"),
            ("/api/admin/documents", "GET"),
            ("/api/admin/tasks", "GET"),
            ("/api/admin/logs/qa", "GET"),
            ("/api/admin/devtools/status", "GET"),
            ("/api/admin/devtools/config", "GET"),
            ("/api/admin/feed/adoptions", "GET"),
            ("/api/admin/rag/evolution/sync-high-quality-posts", "POST"),
            ("/api/admin/maintenance/cleanup-stale-posts?days=7", "POST"),
            ("/api/admin/maintenance/reconcile-interaction-counts", "POST"),
            ("/api/admin/devtools/self-check", "POST"),
        ]

        for endpoint, method in admin_endpoints:
            if method == "GET":
                resp = client.get(endpoint, headers=admin_headers)
            else:
                resp = client.post(endpoint, headers=admin_headers)
            assert resp.status_code == 200, f"{method} {endpoint} failed: {resp.status_code}"

        studio = client.get("/studio/")
        assert studio.status_code == 200
        assert "校园知识工作台" in studio.text

        logout = client.post(
            "/api/client/auth/logout",
            json={"refresh_token": client_refresh},
            headers=client_headers,
        )
        assert logout.status_code == 200


def test_deleted_post_and_comment_cleanup_message_counts() -> None:
    with TestClient(app) as client:
        suffix = uuid4().hex[:8]
        a_register = client.post(
            "/api/client/auth/register",
            json={"username": f"delete_a_{suffix}", "display_name": "delete A", "password": "demo123"},
        )
        assert a_register.status_code == 200, a_register.text
        b_register = client.post(
            "/api/client/auth/register",
            json={"username": f"delete_b_{suffix}", "display_name": "delete B", "password": "demo123"},
        )
        assert b_register.status_code == 200, b_register.text
        a_headers = {"Authorization": f"Bearer {a_register.json()['access_token']}"}
        b_headers = {"Authorization": f"Bearer {b_register.json()['access_token']}"}
        _bind_wechat_for_test(client, a_headers, "delete-a")
        _bind_wechat_for_test(client, b_headers, "delete-b")

        created = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"delete cleanup regression {suffix}",
                "content": "post deletion must clear related likes, saves, and notifications",
                "tags": ["regression"],
            },
            headers=a_headers,
        )
        assert created.status_code == 200, created.text
        post_id = str(created.json().get("id", ""))
        assert post_id.startswith("p-")

        b_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "comment like cleanup", "client_id": f"comment-{suffix}"},
            headers=b_headers,
        )
        assert b_comment.status_code == 200, b_comment.text
        comment_id = str(b_comment.json().get("id", ""))

        a_like_comment = client.post(
            "/api/client/feed/comment/like",
            json={"comment_id": comment_id, "liked": True},
            headers=a_headers,
        )
        assert a_like_comment.status_code == 200, a_like_comment.text
        b_unread_after_comment_like = client.get("/api/client/messages/unread-count", headers=b_headers)
        assert b_unread_after_comment_like.status_code == 200
        assert b_unread_after_comment_like.json().get("likes_total") == 1

        delete_comment = client.post(
            "/api/client/feed/comment/delete",
            json={"post_id": post_id, "comment_id": comment_id},
            headers=b_headers,
        )
        assert delete_comment.status_code == 200, delete_comment.text
        b_unread_after_comment_delete = client.get("/api/client/messages/unread-count", headers=b_headers)
        assert b_unread_after_comment_delete.status_code == 200
        assert b_unread_after_comment_delete.json().get("likes_total") == 0
        b_like_messages_after_comment_delete = client.get("/api/client/messages/likes", headers=b_headers)
        assert b_like_messages_after_comment_delete.status_code == 200
        assert all(
            str(item.get("post_id")) != post_id
            for item in (b_like_messages_after_comment_delete.json().get("items") or [])
        )

        b_like_post = client.post(
            "/api/client/feed/like",
            json={"post_id": post_id, "liked": True},
            headers=b_headers,
        )
        assert b_like_post.status_code == 200, b_like_post.text
        b_save_post = client.post(
            "/api/client/feed/save",
            json={"post_id": post_id, "saved": True},
            headers=b_headers,
        )
        assert b_save_post.status_code == 200, b_save_post.text

        a_summary_before_delete = client.get("/api/client/profile/summary", headers=a_headers)
        assert a_summary_before_delete.status_code == 200
        assert a_summary_before_delete.json().get("likes") == 1
        a_unread_before_delete = client.get("/api/client/messages/unread-count", headers=a_headers)
        assert a_unread_before_delete.status_code == 200
        assert a_unread_before_delete.json().get("likes_total") == 1
        b_unread_before_delete = client.get("/api/client/messages/unread-count", headers=b_headers)
        assert b_unread_before_delete.status_code == 200
        assert b_unread_before_delete.json().get("saved_total") == 1

        delete_post = client.post(
            "/api/client/feed/post/delete",
            json={"post_id": post_id},
            headers=a_headers,
        )
        assert delete_post.status_code == 200, delete_post.text
        assert delete_post.json().get("deleted") is True

        a_summary_after_delete = client.get("/api/client/profile/summary", headers=a_headers)
        assert a_summary_after_delete.status_code == 200
        assert a_summary_after_delete.json().get("likes") == 0
        a_unread_after_delete = client.get("/api/client/messages/unread-count", headers=a_headers)
        assert a_unread_after_delete.status_code == 200
        assert a_unread_after_delete.json().get("likes_total") == 0
        assert a_unread_after_delete.json().get("likes_unread") == 0
        a_like_messages_after_delete = client.get("/api/client/messages/likes", headers=a_headers)
        assert a_like_messages_after_delete.status_code == 200
        assert all(
            str(item.get("post_id")) != post_id
            for item in (a_like_messages_after_delete.json().get("items") or [])
        )

        b_unread_after_delete = client.get("/api/client/messages/unread-count", headers=b_headers)
        assert b_unread_after_delete.status_code == 200
        assert b_unread_after_delete.json().get("saved_total") == 0
        b_saved_after_delete = client.get("/api/client/messages/saved", headers=b_headers)
        assert b_saved_after_delete.status_code == 200
        assert all(str(item.get("post_id")) != post_id for item in (b_saved_after_delete.json().get("items") or []))
        b_liked_posts_after_delete = client.get("/api/client/profile/liked-posts", headers=b_headers)
        assert b_liked_posts_after_delete.status_code == 200
        assert all(str(item.get("id")) != post_id for item in (b_liked_posts_after_delete.json().get("items") or []))


def test_public_feed_hides_obvious_placeholder_artifacts() -> None:
    with TestClient(app) as client:
        suffix = uuid4().hex[:8]
        register = client.post(
            "/api/client/auth/register",
            json={"username": f"artifact_{suffix}", "display_name": "artifact user", "password": "demo123"},
        )
        assert register.status_code == 200, register.text
        headers = {"Authorization": f"Bearer {register.json()['access_token']}"}
        _bind_wechat_for_test(client, headers, "artifact")

        artifact = client.post(
            "/api/client/feed/post/create",
            json={"category": "study", "title": "1", "content": "1", "tags": ["smoke"]},
            headers=headers,
        )
        assert artifact.status_code == 200, artifact.text
        artifact_id = str(artifact.json().get("id", ""))

        real = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"河北大学图书馆自习路线复核 {suffix}",
                "content": "从图书馆官网和校园服务入口核对学习资源路线，适合演示真实校园帖子流。",
                "tags": ["图书馆", "河北大学"],
            },
            headers=headers,
        )
        assert real.status_code == 200, real.text
        real_id = str(real.json().get("id", ""))

        raw_artifact_id = int(artifact_id.replace("p-", ""))
        with SessionLocal() as db:
            row = db.get(Post, raw_artifact_id)
            assert row is not None
            row.likes_count = 999
            db.add(row)
            db.commit()

        feed = client.get("/api/client/feed/list", params={"filter": "all"}, headers=headers)
        assert feed.status_code == 200
        feed_ids = {str(item.get("id")) for item in (feed.json().get("items") or [])}
        assert artifact_id not in feed_ids
        assert real_id in feed_ids

        detail = client.get("/api/client/feed/post", params={"post_id": artifact_id}, headers=headers)
        assert detail.status_code == 404

        hot = client.get("/api/client/home/hot-topics", headers=headers)
        assert hot.status_code == 200
        assert artifact_id not in {str(item.get("post_id")) for item in (hot.json().get("items") or [])}

        search = client.get("/api/client/search/posts", params={"q": "1", "sort": "hot"}, headers=headers)
        assert search.status_code == 200
        assert artifact_id not in {str(item.get("post_id")) for item in (search.json().get("items") or [])}


def test_duplicate_comment_text_likes_are_all_listed() -> None:
    with TestClient(app) as client:
        suffix = uuid4().hex[:8]
        author = client.post(
            "/api/client/auth/register",
            json={"username": f"dup_comment_author_{suffix}", "display_name": "dup author", "password": "demo123"},
        )
        assert author.status_code == 200, author.text
        liker = client.post(
            "/api/client/auth/register",
            json={"username": f"dup_comment_liker_{suffix}", "display_name": "dup liker", "password": "demo123"},
        )
        assert liker.status_code == 200, liker.text
        author_headers = {"Authorization": f"Bearer {author.json()['access_token']}"}
        liker_headers = {"Authorization": f"Bearer {liker.json()['access_token']}"}
        _bind_wechat_for_test(client, author_headers, "dup-author")
        _bind_wechat_for_test(client, liker_headers, "dup-liker")

        post = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"duplicate comment like regression {suffix}",
                "content": "same comment text should still create separate like records",
                "tags": ["regression"],
            },
            headers=liker_headers,
        )
        assert post.status_code == 200, post.text
        post_id = str(post.json().get("id", ""))

        comment_ids: list[str] = []
        for idx in range(2):
            comment = client.post(
                "/api/client/feed/comment/create",
                json={"post_id": post_id, "content": "1", "client_id": f"dup-comment-{suffix}-{idx}"},
                headers=author_headers,
            )
            assert comment.status_code == 200, comment.text
            comment_ids.append(str(comment.json().get("id", "")))

        for comment_id in comment_ids:
            like = client.post(
                "/api/client/feed/comment/like",
                json={"comment_id": comment_id, "liked": True},
                headers=liker_headers,
            )
            assert like.status_code == 200, like.text

        unread = client.get("/api/client/messages/unread-count", headers=author_headers)
        assert unread.status_code == 200
        assert unread.json().get("likes_total") == 2

        likes = client.get("/api/client/messages/likes", headers=author_headers)
        assert likes.status_code == 200
        matching = [
            item for item in (likes.json().get("items") or [])
            if str(item.get("post_id")) == post_id and "评论赞：1" in str(item.get("main"))
        ]
        assert len(matching) == 2


def test_adoption_prune_and_maintenance_cleanup_cascade_related_rows() -> None:
    with TestClient(app) as client:
        suffix = uuid4().hex[:8]
        a_register = client.post(
            "/api/client/auth/register",
            json={"username": f"cascade_a_{suffix}", "display_name": "cascade A", "password": "demo123"},
        )
        assert a_register.status_code == 200, a_register.text
        b_register = client.post(
            "/api/client/auth/register",
            json={"username": f"cascade_b_{suffix}", "display_name": "cascade B", "password": "demo123"},
        )
        assert b_register.status_code == 200, b_register.text
        c_register = client.post(
            "/api/client/auth/register",
            json={"username": f"cascade_c_{suffix}", "display_name": "cascade C", "password": "demo123"},
        )
        assert c_register.status_code == 200, c_register.text
        a_headers = {"Authorization": f"Bearer {a_register.json()['access_token']}"}
        b_headers = {"Authorization": f"Bearer {b_register.json()['access_token']}"}
        c_headers = {"Authorization": f"Bearer {c_register.json()['access_token']}"}
        _bind_wechat_for_test(client, a_headers, "cascade-a")
        _bind_wechat_for_test(client, b_headers, "cascade-b")
        _bind_wechat_for_test(client, c_headers, "cascade-c")

        first_post = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"adoption cascade regression {suffix}",
                "content": "adoption pruning must clear hidden comment likes",
                "tags": ["regression"],
            },
            headers=a_headers,
        )
        assert first_post.status_code == 200, first_post.text
        first_post_id = str(first_post.json().get("id", ""))

        kept_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": first_post_id, "content": "kept comment", "client_id": f"kept-{suffix}"},
            headers=b_headers,
        )
        assert kept_comment.status_code == 200, kept_comment.text
        kept_comment_id = str(kept_comment.json().get("id", ""))
        hidden_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": first_post_id, "content": "hidden comment", "client_id": f"hidden-{suffix}"},
            headers=c_headers,
        )
        assert hidden_comment.status_code == 200, hidden_comment.text
        hidden_comment_id = str(hidden_comment.json().get("id", ""))

        like_hidden_comment = client.post(
            "/api/client/feed/comment/like",
            json={"comment_id": hidden_comment_id, "liked": True},
            headers=a_headers,
        )
        assert like_hidden_comment.status_code == 200, like_hidden_comment.text
        c_unread_before_adopt = client.get("/api/client/messages/unread-count", headers=c_headers)
        assert c_unread_before_adopt.status_code == 200
        assert c_unread_before_adopt.json().get("likes_total") == 1

        admin_username, admin_password = _admin_credentials()
        admin_login = client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": admin_password},
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        adopt = client.post(
            "/api/admin/feed/adopt-comment",
            json={"post_id": first_post_id, "comment_id": kept_comment_id, "prune_other_comments": True},
            headers=admin_headers,
        )
        assert adopt.status_code == 200, adopt.text
        assert int(adopt.json().get("pruned_count", 0)) >= 1
        c_unread_after_adopt = client.get("/api/client/messages/unread-count", headers=c_headers)
        assert c_unread_after_adopt.status_code == 200
        assert c_unread_after_adopt.json().get("likes_total") == 0
        with SessionLocal() as db:
            raw_hidden_comment_id = int(hidden_comment_id.replace("c-", ""))
            assert db.scalar(select(func.count()).select_from(CommentLike).where(CommentLike.comment_id == raw_hidden_comment_id)) == 0

        second_post = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"maintenance cascade regression {suffix}",
                "content": "maintenance cleanup must cascade all related rows",
                "tags": ["regression"],
            },
            headers=a_headers,
        )
        assert second_post.status_code == 200, second_post.text
        second_post_id = str(second_post.json().get("id", ""))
        second_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": second_post_id, "content": "stale comment", "client_id": f"stale-{suffix}"},
            headers=b_headers,
        )
        assert second_comment.status_code == 200, second_comment.text
        second_comment_id = str(second_comment.json().get("id", ""))
        assert client.post("/api/client/feed/like", json={"post_id": second_post_id, "liked": True}, headers=b_headers).status_code == 200
        assert client.post("/api/client/feed/save", json={"post_id": second_post_id, "saved": True}, headers=b_headers).status_code == 200
        assert client.post("/api/client/feed/comment/like", json={"comment_id": second_comment_id, "liked": True}, headers=a_headers).status_code == 200

        raw_second_post_id = int(second_post_id.replace("p-", ""))
        raw_second_comment_id = int(second_comment_id.replace("c-", ""))
        with SessionLocal() as db:
            stale_post = db.get(Post, raw_second_post_id)
            assert stale_post is not None
            stale_post.created_at = datetime.now(tz=timezone.utc) - timedelta(days=3)
            stale_post.adopted = False
            db.add(stale_post)
            db.commit()

        cleanup = maintenance_service.cleanup_stale_unadopted_posts(days=1)
        assert int(cleanup.get("deleted_posts", 0)) >= 1
        with SessionLocal() as db:
            assert db.get(Post, raw_second_post_id) is None
            assert db.scalar(select(func.count()).select_from(Comment).where(Comment.post_id == raw_second_post_id)) == 0
            assert db.scalar(select(func.count()).select_from(PostLike).where(PostLike.post_id == raw_second_post_id)) == 0
            assert db.scalar(select(func.count()).select_from(PostSave).where(PostSave.post_id == raw_second_post_id)) == 0
            assert db.scalar(select(func.count()).select_from(CommentLike).where(CommentLike.comment_id == raw_second_comment_id)) == 0
            assert (
                db.scalar(
                    select(func.count())
                    .select_from(MessageNotification)
                    .where(MessageNotification.source_post_id == raw_second_post_id)
                )
                == 0
            )


def test_maintenance_reconcile_interaction_counts() -> None:
    with TestClient(app) as client:
        suffix = uuid4().hex[:8]
        author_register = client.post(
            "/api/client/auth/register",
            json={"username": f"reconcile_author_{suffix}", "display_name": "reconcile A", "password": "demo123"},
        )
        assert author_register.status_code == 200, author_register.text
        liker_register = client.post(
            "/api/client/auth/register",
            json={"username": f"reconcile_liker_{suffix}", "display_name": "reconcile B", "password": "demo123"},
        )
        assert liker_register.status_code == 200, liker_register.text
        author_headers = {"Authorization": f"Bearer {author_register.json()['access_token']}"}
        liker_headers = {"Authorization": f"Bearer {liker_register.json()['access_token']}"}
        _bind_wechat_for_test(client, author_headers, "reconcile-author")
        _bind_wechat_for_test(client, liker_headers, "reconcile-liker")

        created = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"reconcile interaction counts {suffix}",
                "content": "counter cache should match real interaction rows after maintenance",
                "tags": ["regression"],
            },
            headers=author_headers,
        )
        assert created.status_code == 200, created.text
        post_id = str(created.json().get("id", ""))
        comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "count me once", "client_id": f"reconcile-{suffix}"},
            headers=liker_headers,
        )
        assert comment.status_code == 200, comment.text
        comment_id = str(comment.json().get("id", ""))
        assert client.post("/api/client/feed/like", json={"post_id": post_id, "liked": True}, headers=liker_headers).status_code == 200
        assert client.post("/api/client/feed/comment/like", json={"comment_id": comment_id, "liked": True}, headers=author_headers).status_code == 200

        raw_post_id = int(post_id.replace("p-", ""))
        raw_comment_id = int(comment_id.replace("c-", ""))
        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            db_comment = db.get(Comment, raw_comment_id)
            assert post is not None
            assert db_comment is not None
            post.likes_count = 91
            post.comments_count = 47
            db_comment.likes_count = 33
            db.add(post)
            db.add(db_comment)
            db.commit()

        admin_username, admin_password = _admin_credentials()
        admin_login = client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": admin_password},
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        repair = client.post("/api/admin/maintenance/reconcile-interaction-counts", headers=admin_headers)
        assert repair.status_code == 200, repair.text
        payload = repair.json()
        assert payload.get("fixed_post_likes", 0) >= 1
        assert payload.get("fixed_post_comments", 0) >= 1
        assert payload.get("fixed_comment_likes", 0) >= 1

        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            db_comment = db.get(Comment, raw_comment_id)
            assert post is not None
            assert db_comment is not None
            assert post.likes_count == 1
            assert post.comments_count == 1
            assert db_comment.likes_count == 1

        second_repair = client.post("/api/admin/maintenance/reconcile-interaction-counts", headers=admin_headers)
        assert second_repair.status_code == 200, second_repair.text
        second_payload = second_repair.json()
        assert second_payload.get("fixed_post_likes") == 0
        assert second_payload.get("fixed_post_comments") == 0
        assert second_payload.get("fixed_comment_likes") == 0


def test_knowledge_answer_uses_extractive_answer_for_short_keyword(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    doc_path = tmp_path / "webvpn.md"
    doc_path.write_text(
        "河北大学图书馆校外访问资料：校外访问电子资源时，先登录 WEBVPN，再进入图书馆电子资源页面。"
        "论文检索、数据库访问和文献传递不要依赖群内旧链接。",
        encoding="utf-8",
    )
    with SessionLocal() as db:
        next_doc_id = int(db.scalar(select(func.max(KnowledgeDocument.id))) or 0) + 1
        db.add(
            KnowledgeDocument(
                id=next_doc_id,
                kb_id=1,
                file_name=f"pytest-webvpn-{uuid4().hex[:8]}.md",
                file_ext="md",
                file_size=doc_path.stat().st_size,
                storage_path=str(doc_path),
                mime_type="text/markdown",
                status="indexed",
                chunk_count=1,
                error_message="",
                uploaded_by=1,
            )
        )
        db.commit()
    knowledge_cache_service.rebuild_chunks()

    async def unexpected_generate(query: str, contexts: list[str]) -> tuple[str, str]:
        raise AssertionError("short keyword questions should not wait for the external QA model")

    monkeypatch.setattr(qa_provider, "generate", unexpected_generate)

    with TestClient(app) as client:
        login = _client_login(client, username="zhaoyi")
        headers = {"Authorization": f"Bearer {login['access_token']}"}
        response = client.post(
            "/api/client/knowledge/ask",
            json={"query": "WEBVPN", "history": []},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        answer = str(payload.get("answer", ""))
        assert "WEBVPN" in answer
        assert "图书馆" in answer
        assert "刷赞风险" not in answer
        assert payload.get("citations")

        response = client.post(
            "/api/client/knowledge/ask",
            json={"query": "WEBVPN 怎么使用", "history": []},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        answer = str(payload.get("answer", ""))
        assert "WEBVPN" in answer
        assert payload.get("citations")

    cleaned = rag_pipeline._build_extractive_answer(
        "WEBVPN",
        [
            "# 校园论坛录用：校外查文献先确认 WEBVPN｜入口版 - 帖子编号：p-875",
            "5月18日学习提醒：校外访问校内资源时，先确认统一认证和 WEBVPN 是否可用，再进入图书馆电子资源。 #HBU真实数据 #河北大学 #WEBVPN",
            "河同学：图书馆和WEBVPN这两块确实应该放在一起看，查文献会顺很多。",
        ],
    )
    assert "校园论坛录用" not in cleaned
    assert "月18日" not in cleaned
    assert "#HBU真实数据" not in cleaned
    assert "河同学" not in cleaned
    assert "WEBVPN" in cleaned


def test_admin_login_rate_limit() -> None:
    user_agent = f"pytest-admin-guard-{uuid4().hex}"
    headers = {"User-Agent": user_agent}
    with TestClient(app) as client:
        username, password = _admin_credentials()
        policy = client.get("/api/admin/auth/policy")
        assert policy.status_code == 200
        policy_payload = policy.json()
        assert int(policy_payload.get("max_attempts", 0)) >= 2
        assert int(policy_payload.get("lock_minutes", 0)) >= 1

        blocked = False
        last_remaining = int(policy_payload["max_attempts"])
        for _ in range(max(1, int(settings.admin_login_max_attempts)) + 1):
            response = client.post(
                "/api/admin/auth/login",
                json={"username": username, "password": f"{password}-wrong"},
                headers=headers,
            )
            if response.status_code == 429:
                detail = response.json().get("detail", {})
                assert detail.get("code") == "admin_login_temporarily_blocked"
                assert int(detail.get("retry_after_seconds", 0)) > 0
                assert int(detail.get("remaining_attempts", -1)) == 0
                blocked = True
                break
            assert response.status_code == 401
            detail = response.json().get("detail", {})
            assert detail.get("code") == "invalid_admin_credentials"
            assert int(detail.get("lock_minutes", 0)) >= 1
            remaining_attempts = int(detail.get("remaining_attempts", -1))
            assert remaining_attempts >= 0
            assert remaining_attempts <= last_remaining
            last_remaining = remaining_attempts

        assert blocked, "admin login guard did not trigger"
        still_blocked = client.post(
            "/api/admin/auth/login",
            json={"username": username, "password": password},
            headers=headers,
        )
        assert still_blocked.status_code == 429
        assert still_blocked.json().get("detail", {}).get("code") == "admin_login_temporarily_blocked"


def test_evolution_candidate_priority_prefers_high_value_backlog() -> None:
    with TestClient(app):
        with SessionLocal() as db:
            author_id = int(db.execute(select(User.id).order_by(User.id.asc()).limit(1)).scalar_one())
            next_post_id = int(db.scalar(select(func.max(Post.id))) or 0) + 1
            next_adoption_id = int(db.scalar(select(func.max(PostAdoption.id))) or 0) + 1

            older_post_id = next_post_id
            newer_post_id = next_post_id + 1
            db.add(
                Post(
                    id=older_post_id,
                    author_id=author_id,
                    category="academic",
                    title="priority backlog candidate",
                    content=(
                        "Registration guidance with exact window, building, and fallback route. "
                        "Students can reuse this next week without guessing."
                    ),
                    tags_json=json.dumps(["#guide", "#registration"], ensure_ascii=False),
                    likes_count=68,
                    comments_count=8,
                    adopted=True,
                    status="published",
                    created_at=datetime.now(tz=timezone.utc) - timedelta(days=4),
                )
            )
            db.add(
                PostAdoption(
                    id=next_adoption_id,
                    post_id=older_post_id,
                    post_title="priority backlog candidate",
                    post_author_id=author_id,
                    post_author_name="priority-author",
                    adopted_comment_id=1,
                    adopted_user_id=author_id,
                    adopted_user_name="priority-user",
                    adopted_comment_text="Extra confirmation from the on-site queue.",
                    adopted_at=datetime.now(tz=timezone.utc) - timedelta(days=3),
                )
            )
            db.add(
                Post(
                    id=newer_post_id,
                    author_id=author_id,
                    category="market",
                    title="recent but thin candidate",
                    content="Short and generic note.",
                    tags_json=json.dumps(["#note"], ensure_ascii=False),
                    likes_count=30,
                    comments_count=5,
                    adopted=False,
                    status="published",
                    created_at=datetime.now(tz=timezone.utc) - timedelta(hours=1),
                )
            )
            db.commit()

        bundle = evolution_service._collect_candidates(
            kb_id=1,
            min_likes=30,
            min_comments=5,
            limit=1,
            include_reviewed=False,
        )
        items = list(bundle["items"])
        assert items
        top = items[0]
        assert int(top["post"].id) == older_post_id
        assert int(top.get("candidate_priority") or 0) > 0
        breakdown = list(top.get("candidate_priority_breakdown") or [])
        assert any(str(item.get("label")) == "forum_adoption_bonus" for item in breakdown)
        assert any(str(item.get("label")) == "pending_backlog_bonus" for item in breakdown)


def test_evolution_sync_is_persistent_and_non_duplicating() -> None:
    unique_title = f"pytest unique evo {uuid4().hex[:8]}"
    with SessionLocal() as db:
        author = db.execute(select(User).order_by(User.id.asc())).scalars().first()
        assert author is not None
        next_post_id = int(db.execute(select(func.max(Post.id))).scalar() or 0) + 1
        db.add(
            Post(
                id=next_post_id,
                author_id=int(author.id),
                category="study",
                title=unique_title,
                content="这是一条用于回归测试的唯一帖子，包含清晰地点、时间和建议，避免被历史重复内容拦截。",
                tags_json=json.dumps(["#测试", "#唯一帖子"], ensure_ascii=False),
                likes_count=88,
                comments_count=6,
                adopted=True,
                status="published",
                created_at=datetime.now(timezone.utc) - timedelta(days=4),
            )
        )
        db.commit()

    with TestClient(app) as client:
        username, password = _admin_credentials()
        login = client.post(
            "/api/admin/auth/login",
            json={"username": username, "password": password},
            headers={"User-Agent": f"pytest-evo-{uuid4().hex}"},
        )
        assert login.status_code == 200
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        docs_before = client.get("/api/admin/documents?kb_id=1", headers=admin_headers)
        assert docs_before.status_code == 200
        evo_before = sum(1 for row in (docs_before.json().get("items") or []) if str(row.get("file_name", "")).startswith("evo-post-"))

        sync_one = client.post(
            "/api/admin/rag/evolution/sync-high-quality-posts?kb_id=1&min_likes=0&min_comments=0&limit=200",
            headers=admin_headers,
        )
        assert sync_one.status_code == 200
        assert int(sync_one.json().get("accepted_posts", 0)) >= 1

        docs_after_one = client.get("/api/admin/documents?kb_id=1", headers=admin_headers)
        assert docs_after_one.status_code == 200
        evo_after_one = sum(1 for row in (docs_after_one.json().get("items") or []) if str(row.get("file_name", "")).startswith("evo-post-"))
        assert evo_after_one >= evo_before

        sync_two = client.post(
            "/api/admin/rag/evolution/sync-high-quality-posts?kb_id=1&min_likes=0&min_comments=0&limit=200",
            headers=admin_headers,
        )
        assert sync_two.status_code == 200
        assert int(sync_two.json().get("synced_posts", 0)) == 0
        assert int(sync_two.json().get("reviewed_posts_skipped", 0)) >= 1

        docs_after_two = client.get("/api/admin/documents?kb_id=1", headers=admin_headers)
        assert docs_after_two.status_code == 200
        evo_after_two = sum(1 for row in (docs_after_two.json().get("items") or []) if str(row.get("file_name", "")).startswith("evo-post-"))
        assert evo_after_two == evo_after_one

        reviews = client.get("/api/admin/rag/evolution/reviews?limit=200", headers=admin_headers)
        assert reviews.status_code == 200
        review_items = reviews.json().get("items") or []
        assert review_items
        assert any(str(item.get("post_id", "")).startswith("p-") for item in review_items)
        assert any((item.get("detail") or {}).get("threshold") is not None for item in review_items)
        assert any((item.get("detail") or {}).get("review_mode") for item in review_items)
        assert any(item.get("post_title") == unique_title for item in review_items)
        review_count_after = len(review_items)

        sync_three = client.post(
            "/api/admin/rag/evolution/sync-high-quality-posts?kb_id=1&min_likes=0&min_comments=0&limit=200",
            headers=admin_headers,
        )
        assert sync_three.status_code == 200
        assert int(sync_three.json().get("synced_posts", 0)) == 0

        reviews_after_repeat = client.get("/api/admin/rag/evolution/reviews?limit=200", headers=admin_headers)
        assert reviews_after_repeat.status_code == 200
        assert len(reviews_after_repeat.json().get("items") or []) == review_count_after


def test_admin_can_repair_missing_adoptions_and_see_evolution_overview() -> None:
    with TestClient(app) as client:
        suffix = uuid4().hex[:8]
        author = client.post(
            "/api/client/auth/register",
            json={"username": f"repair_author_{suffix}", "display_name": "repair author", "password": "demo123"},
        )
        commenter = client.post(
            "/api/client/auth/register",
            json={"username": f"repair_commenter_{suffix}", "display_name": "repair commenter", "password": "demo123"},
        )
        assert author.status_code == 200, author.text
        assert commenter.status_code == 200, commenter.text
        author_headers = {"Authorization": f"Bearer {author.json()['access_token']}"}
        commenter_headers = {"Authorization": f"Bearer {commenter.json()['access_token']}"}
        _bind_wechat_for_test(client, author_headers, "repair-author")
        _bind_wechat_for_test(client, commenter_headers, "repair-commenter")

        post = client.post(
            "/api/client/feed/post/create",
            json={
                "category": "study",
                "title": f"missing adoption repair {suffix}",
                "content": "A migrated adopted post should regain its adoption audit row.",
                "tags": ["regression"],
            },
            headers=author_headers,
        )
        assert post.status_code == 200, post.text
        post_id = str(post.json().get("id", ""))
        comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "This is the answer that should be restored.", "client_id": f"repair-{suffix}"},
            headers=commenter_headers,
        )
        assert comment.status_code == 200, comment.text

        raw_post_id = int(post_id.replace("p-", ""))
        with SessionLocal() as db:
            row = db.get(Post, raw_post_id)
            assert row is not None
            row.adopted = True
            db.add(row)
            orphan_post_id = int(db.scalar(select(func.max(Post.id))) or 0) + 1
            db.add(
                Post(
                    id=orphan_post_id,
                    author_id=int(row.author_id),
                    category="study",
                    title=f"orphan adopted flag {suffix}",
                    content="This migrated row has no comments and should not stay adopted.",
                    tags_json=json.dumps(["regression"], ensure_ascii=False),
                    likes_count=0,
                    comments_count=0,
                    adopted=True,
                    status="published",
                    created_at=datetime.now(tz=timezone.utc),
                )
            )
            db.commit()
            assert db.scalar(select(func.count()).select_from(PostAdoption).where(PostAdoption.post_id == raw_post_id)) == 0

        username, password = _admin_credentials()
        login = client.post(
            "/api/admin/auth/login",
            json={"username": username, "password": password},
            headers={"User-Agent": f"pytest-repair-{suffix}"},
        )
        assert login.status_code == 200, login.text
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        overview_before = client.get("/api/admin/rag/evolution/overview", headers=admin_headers)
        assert overview_before.status_code == 200
        assert int(overview_before.json().get("missing_adoption_records", 0)) >= 1

        repair = client.post("/api/admin/feed/adoptions/repair?limit=1000", headers=admin_headers)
        assert repair.status_code == 200, repair.text
        assert int(repair.json().get("created_adoptions", 0)) >= 1
        assert int(repair.json().get("cleared_orphan_adopted_flags", 0)) >= 1

        adoptions = client.get("/api/admin/feed/adoptions", headers=admin_headers)
        assert adoptions.status_code == 200
        assert any(str(item.get("post_id")) == post_id for item in (adoptions.json().get("items") or []))
        with SessionLocal() as db:
            orphan_post = db.get(Post, orphan_post_id)
            assert orphan_post is not None
            assert bool(orphan_post.adopted) is False


def test_admin_can_view_edit_reindex_and_delete_document_content(tmp_path: Path) -> None:
    doc_path = tmp_path / "manual.md"
    doc_path.write_text("# Original\n\nLibrary route notes.", encoding="utf-8")
    with SessionLocal() as db:
        next_doc_id = int(db.scalar(select(func.max(KnowledgeDocument.id))) or 0) + 1
        db.add(
            KnowledgeDocument(
                id=next_doc_id,
                kb_id=1,
                file_name=f"pytest-manual-{uuid4().hex[:8]}.md",
                file_ext="md",
                file_size=doc_path.stat().st_size,
                storage_path=str(doc_path),
                mime_type="text/markdown",
                status="indexed",
                chunk_count=1,
                error_message="",
                uploaded_by=1,
            )
        )
        db.commit()

    with TestClient(app) as client:
        username, password = _admin_credentials()
        login = client.post(
            "/api/admin/auth/login",
            json={"username": username, "password": password},
            headers={"User-Agent": f"pytest-doc-editor-{uuid4().hex}"},
        )
        assert login.status_code == 200, login.text
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        content = client.get(f"/api/admin/documents/{next_doc_id}/content", headers=admin_headers)
        assert content.status_code == 200, content.text
        assert "Library route notes" in content.json().get("content", "")

        updated_text = "# Updated\n\n河北大学图书馆 WEBVPN 访问路线已人工复核。"
        update = client.put(
            f"/api/admin/documents/{next_doc_id}/content",
            json={"content": updated_text, "reindex": True},
            headers=admin_headers,
        )
        assert update.status_code == 200, update.text
        assert "reindexed" in update.json().get("message", "")
        assert updated_text in doc_path.read_text(encoding="utf-8")

        refreshed = client.get(f"/api/admin/documents/{next_doc_id}/content", headers=admin_headers)
        assert refreshed.status_code == 200
        assert "人工复核" in refreshed.json().get("content", "")

        delete = client.delete(f"/api/admin/documents/{next_doc_id}", headers=admin_headers)
        assert delete.status_code == 200, delete.text
        assert not doc_path.exists()
        with SessionLocal() as db:
            assert db.get(KnowledgeDocument, next_doc_id) is None


def test_password_hashing_supports_legacy_rows() -> None:
    legacy_salt = "legacysalt"
    legacy_digest = hashlib.sha256(f"{legacy_salt}:demo123".encode("utf-8")).hexdigest()
    legacy_hash = f"sha256${legacy_salt}${legacy_digest}"
    current_hash = hash_password("demo123", salt="current-salt")

    assert current_hash.startswith(f"{PBKDF2_ALGORITHM}$")
    assert verify_password("demo123", current_hash)
    assert not needs_password_rehash(current_hash)

    assert verify_password("demo123", legacy_hash)
    assert needs_password_rehash(legacy_hash, legacy_salt)

    assert verify_password("demo123", "demo123")
    assert needs_password_rehash("demo123")


def test_document_upload_service_rejects_binary_and_uses_private_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    private_root = tmp_path / "kb_documents"
    private_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(document_upload_service, "root", private_root)

    saved = document_upload_service.save_document(
        content="security regression doc".encode("utf-8"),
        file_name="..\\notes.md",
        mime_type="text/markdown; charset=utf-8",
    )
    stored_path = Path(saved["storage_path"])

    assert saved["file_name"] == "notes.md"
    assert stored_path.is_file()
    assert stored_path.parent == private_root.resolve()
    assert "uploads" not in str(stored_path).lower()

    with pytest.raises(ValueError, match="document_format_not_supported"):
        document_upload_service.save_document(
            content=b"MZ",
            file_name="tool.exe",
            mime_type="application/octet-stream",
        )

    with pytest.raises(ValueError, match="document_encoding_not_supported"):
        document_upload_service.save_document(
            content=b"\xff\xfe\x00\x01",
            file_name="broken.txt",
            mime_type="text/plain",
        )

    with pytest.raises(ValueError, match="document_too_large"):
        document_upload_service.save_document(
            content=b"a" * (MAX_DOCUMENT_BYTES + 1),
            file_name="huge.txt",
            mime_type="text/plain",
        )


def test_document_upload_service_normalizes_common_documents_to_editable_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    private_root = tmp_path / "kb_documents"
    private_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(document_upload_service, "root", private_root)

    docx_content = _zip_bytes(
        {
            "word/document.xml": (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>Hebei University DOCX knowledge</w:t></w:r></w:p></w:body>"
                "</w:document>"
            )
        }
    )
    xlsx_content = _zip_bytes(
        {
            "xl/sharedStrings.xml": (
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                "<si><t>Course</t></si><si><t>Advanced Math</t></si></sst>"
            ),
            "xl/worksheets/sheet1.xml": (
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row>'
                '<c t="s"><v>0</v></c><c t="s"><v>1</v></c>'
                "</row></sheetData></worksheet>"
            ),
        }
    )
    pptx_content = _zip_bytes(
        {
            "ppt/slides/slide1.xml": (
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                "<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>Defense Slide</a:t></a:r></a:p>"
                "</p:txBody></p:sp></p:spTree></p:cSld></p:sld>"
            )
        }
    )
    cases = [
        (
            "notice.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            docx_content,
            "DOCX knowledge",
        ),
        ("notice.pdf", "application/pdf", _minimal_pdf_bytes("Campus PDF"), "Campus PDF"),
        ("notice.html", "text/html", b"<html><body><h1>Campus HTML</h1></body></html>", "Campus HTML"),
        (
            "notice.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            xlsx_content,
            "Advanced Math",
        ),
        (
            "notice.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            pptx_content,
            "Defense Slide",
        ),
    ]

    for file_name, mime_type, content, expected_text in cases:
        saved = document_upload_service.save_document(content=content, file_name=file_name, mime_type=mime_type)
        stored_path = Path(saved["storage_path"])
        stored_text = stored_path.read_text(encoding="utf-8")
        assert saved["file_ext"] == "md"
        assert saved["mime_type"] == "text/markdown"
        assert bytes(saved["ingest_content"]) == stored_path.read_bytes()
        assert expected_text in stored_text
        assert stored_path.parent == private_root.resolve()


def test_document_parser_uses_vision_ocr_for_scanned_pdf(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "document_ocr_enabled", True)
    monkeypatch.setattr(settings, "document_ocr_base_url", "https://ocr.example/v1")
    monkeypatch.setattr(settings, "document_ocr_api_key", "ocr-key")
    monkeypatch.setattr(settings, "document_ocr_model", "vision-ocr-model")
    monkeypatch.setattr(settings, "document_ocr_timeout_seconds", 9)
    monkeypatch.setattr(settings, "document_ocr_max_pages", 2)
    monkeypatch.setattr(document_parser, "_parse_pdf_with_pypdf", lambda content: "")
    monkeypatch.setattr(document_parser, "_parse_pdf_with_pymupdf", lambda content: "")
    monkeypatch.setattr(document_parser, "_render_pdf_pages_for_ocr", lambda content: [("image/png", b"fake-page")])

    captured: dict[str, object] = {}

    def fake_post(self: httpx.Client, url: str, json: dict | None = None, headers: dict | None = None) -> httpx.Response:
        captured["url"] = url
        captured["json"] = json or {}
        captured["headers"] = headers or {}
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "河北大学 OCR 入库内容"}}]},
            request=request,
        )

    monkeypatch.setattr(httpx.Client, "post", fake_post)

    text = document_parser.parse_bytes(b"%PDF-1.4\nscanned", "pdf")

    assert "河北大学 OCR 入库内容" in text
    assert captured["url"] == "https://ocr.example/v1/chat/completions"
    payload = captured["json"]
    assert isinstance(payload, dict)
    assert payload.get("model") == "vision-ocr-model"
    content_parts = payload["messages"][1]["content"]
    assert any(part.get("type") == "image_url" and "data:image/png;base64," in part["image_url"]["url"] for part in content_parts)
    assert captured["headers"] == {"Authorization": "Bearer ocr-key"}


def test_document_upload_service_normalizes_image_ocr_to_knowledge_markdown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    private_root = tmp_path / "kb_documents"
    private_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(document_upload_service, "root", private_root)
    monkeypatch.setattr(document_parser, "_ocr_images_with_model", lambda images, source_label: "OCR image knowledge")

    saved = document_upload_service.save_document(
        content=b"\x89PNG\r\n\x1a\n" + b"image-bytes",
        file_name="campus-map.png",
        mime_type="image/png",
    )

    stored_path = Path(saved["storage_path"])
    assert saved["file_ext"] == "md"
    assert saved["mime_type"] == "text/markdown"
    assert "OCR image knowledge" in stored_path.read_text(encoding="utf-8")
    assert bytes(saved["ingest_content"]) == stored_path.read_bytes()


def test_wechat_service_does_not_fallback_to_mock_when_configured_exchange_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "app_env", "development")
    monkeypatch.setattr(settings, "wechat_mock_enabled", True)
    monkeypatch.setattr(settings, "wechat_app_id", "wx-app-id")
    monkeypatch.setattr(settings, "wechat_app_secret", "wx-app-secret")
    monkeypatch.setattr(settings, "wechat_code2session_url", "https://example.invalid/jscode2session")
    monkeypatch.setattr(settings, "wechat_timeout_seconds", 3)

    async def fake_get(self: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response:
        raise httpx.ConnectError("boom", request=httpx.Request("GET", url, params=params))

    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    with pytest.raises(ValueError, match="wechat_code2session_failed"):
        asyncio.run(wechat_service.code_to_openid("wxcode-secure"))


def test_admin_client_debug_token_endpoint_issues_client_token() -> None:
    with TestClient(app) as client:
        username, password = _admin_credentials()
        login = client.post(
            "/api/admin/auth/login",
            json={"username": username, "password": password},
            headers={"User-Agent": f"pytest-devtools-{uuid4().hex}"},
        )
        assert login.status_code == 200
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        config = client.get("/api/admin/devtools/config", headers=admin_headers)
        assert config.status_code == 200
        assert "BOOTSTRAP_DEMO_DATA" in (config.json().get("editable_keys") or [])

        issued = client.post("/api/admin/devtools/client-debug-token", headers=admin_headers)
        assert issued.status_code == 200
        payload = issued.json()
        assert payload.get("access_token")
        assert int(payload.get("user_id", 0)) > 0

        me = client.get(
            "/api/client/auth/me",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )
        assert me.status_code == 200
        assert int(me.json().get("user_id", 0)) == int(payload["user_id"])


def test_devtools_reports_evolution_ai_review_reusing_qa(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "qa_base_url", "https://qa.example/v1")
    monkeypatch.setattr(settings, "qa_api_key", "qa-key")
    monkeypatch.setattr(settings, "qa_model", "qa-review-model")
    monkeypatch.setattr(settings, "evolution_ai_review_enabled", True)
    monkeypatch.setattr(settings, "evolution_ai_review_provider", "qa_reuse")
    monkeypatch.setattr(settings, "evolution_ai_review_base_url", "")
    monkeypatch.setattr(settings, "evolution_ai_review_api_key", "")
    monkeypatch.setattr(settings, "evolution_ai_review_model", "")

    with TestClient(app) as client:
        username, password = _admin_credentials()
        login = client.post(
            "/api/admin/auth/login",
            json={"username": username, "password": password},
            headers={"User-Agent": f"pytest-devtools-ai-review-{uuid4().hex}"},
        )
        assert login.status_code == 200
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        status = client.get("/api/admin/devtools/status", headers=admin_headers)
        assert status.status_code == 200
        assert status.json().get("evolution_ai_review_provider") == "qa_reuse"
        assert status.json().get("evolution_ai_review_configured") is True

        self_check = client.post("/api/admin/devtools/self-check", headers=admin_headers)
        assert self_check.status_code == 200
        rows = {item.get("name"): item for item in (self_check.json().get("items") or [])}
        assert rows.get("evolution_ai_review_config", {}).get("passed") is True
        assert rows.get("evolution_ai_review_config", {}).get("detail") == "ai_review_reuse_qa_ready"
