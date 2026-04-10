from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

os.environ["POSTGRES_URL"] = "sqlite:///./pytest_e2e.db"
os.environ["QDRANT_URL"] = ""
os.environ["QA_BASE_URL"] = ""
os.environ["QA_API_KEY"] = ""
os.environ["QA_MODEL"] = ""

from app.core.config import settings
from app.core.passwords import PBKDF2_ALGORITHM, hash_password, needs_password_rehash, verify_password
from app.core.database import SessionLocal
from app.models.post import Post
from app.models.post_adoption import PostAdoption
from app.models.user import User

DB_FILE = Path("pytest_e2e.db")
if DB_FILE.exists():
    DB_FILE.unlink()

from app.main import app  # noqa: E402
from app.services.document_upload_service import MAX_DOCUMENT_BYTES, document_upload_service  # noqa: E402
from app.services.evolution_service import evolution_service  # noqa: E402
from app.services.knowledge_cache_service import knowledge_cache_service  # noqa: E402
from app.services.wechat_service import wechat_service  # noqa: E402
from scripts.seed_hbu_kb import seed_local_documents  # noqa: E402


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


def test_backend_e2e_flow() -> None:
    with TestClient(app) as client:
        seed_local_documents(kb_id=1, ensure_bootstrap=False, force_reindex=True)
        knowledge_cache_service.rebuild_chunks()

        health = client.get("/healthz")
        assert health.status_code == 200

        client_login = _client_login(client, username="zhaoyi")
        assert client_login.get("public_name")
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

        # Multi-user isolation: user B can like/comment, cannot delete A's comment.
        user_b_name = f"user_b_{uuid4().hex[:8]}"
        b_register = client.post(
            "/api/client/auth/register",
            json={"username": user_b_name, "display_name": "userB", "password": "demo123"},
        )
        assert b_register.status_code == 200, b_register.text
        b_token = str(b_register.json().get("access_token", ""))
        b_headers = {"Authorization": f"Bearer {b_token}"}

        a_comment = client.post(
            "/api/client/feed/comment/create",
            json={"post_id": post_id, "content": "comment by A", "client_id": "pytest-A"},
            headers=client_headers,
        )
        assert a_comment.status_code == 200
        a_comment_id = str(a_comment.json().get("id", ""))
        assert a_comment_id.startswith("c-")

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
        assert claim_errand.json().get("item", {}).get("publisher_contact")

        my_errands = client.get("/api/client/errands/my", headers=client_headers)
        assert my_errands.status_code == 200
        assert any(str(item.get("id")) == errand_id for item in (my_errands.json().get("items") or []))

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

        web_login_exchange_repeat = client.post(
            "/api/client/auth/web-login-exchange",
            json={"code": code_value},
        )
        assert web_login_exchange_repeat.status_code == 401

        refresh = client.post(
            "/api/client/auth/refresh",
            json={"refresh_token": client_refresh},
        )
        assert refresh.status_code == 200
        refreshed_token = str(refresh.json().get("access_token", ""))
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
            content=b"%PDF-1.7",
            file_name="report.pdf",
            mime_type="application/pdf",
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
