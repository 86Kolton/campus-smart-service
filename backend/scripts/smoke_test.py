from __future__ import annotations

import os
from pathlib import Path
import sys
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

# Make `app` package importable when running script from backend/scripts.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Force local SQLite for quick smoke test execution.
os.environ.setdefault("POSTGRES_URL", "sqlite:///./smoke_test.db")
os.environ.setdefault("QDRANT_URL", "")
os.environ.setdefault("QA_BASE_URL", "")
os.environ.setdefault("QA_API_KEY", "")
os.environ.setdefault("QA_MODEL", "")

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models.post import Post  # noqa: E402


def _admin_credentials() -> tuple[str, str]:
    username = str(settings.admin_username or "").strip()
    password = str(settings.admin_password or "").strip()
    if not username or not password:
        raise SystemExit("admin credentials are not configured in backend/.env")
    return username, password


def run() -> None:
    db_file = Path("smoke_test.db")
    if db_file.exists():
        db_file.unlink()

    checks: list[tuple[str, bool, str]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))

    with TestClient(app) as client:
        with SessionLocal() as db:
            cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=45)
            for row in db.query(Post).filter(Post.author_id == 1).all():
                row.created_at = cutoff
            db.commit()

        add("health", client.get("/healthz").status_code == 200)

        client_login = client.post(
            "/api/client/auth/login",
            json={"username": "zhaoyi", "password": "demo"},
        )
        token_ok = client_login.status_code == 200 and client_login.json().get("access_token")
        add("client-login", bool(token_ok))
        refresh_token = client_login.json().get("refresh_token", "")
        client_headers = {"Authorization": f"Bearer {client_login.json().get('access_token', '')}"} if token_ok else {}

        add("feed", client.get("/api/client/feed/list", headers=client_headers).status_code == 200)
        add(
            "post-create-with-image",
            client.post(
                "/api/client/feed/post/create-with-image",
                headers=client_headers,
                data={
                    "category": "study",
                    "title": "smoke post 1",
                    "content": "content 1",
                    "tags": '["test"]',
                },
                files={"image": ("a.png", b"fake-png", "image/png")},
            ).status_code
            == 200,
        )
        add(
            "post-create-2",
            client.post(
                "/api/client/feed/post/create",
                headers=client_headers,
                json={"category": "study", "title": "smoke post 2", "content": "content 2", "tags": ["test"]},
            ).status_code
            == 200,
        )
        add(
            "post-create-3",
            client.post(
                "/api/client/feed/post/create",
                headers=client_headers,
                json={"category": "study", "title": "smoke post 3", "content": "content 3", "tags": ["test"]},
            ).status_code
            == 200,
        )
        add(
            "post-rate-limit",
            client.post(
                "/api/client/feed/post/create",
                headers=client_headers,
                json={"category": "study", "title": "smoke post 4", "content": "content 4", "tags": ["test"]},
            ).status_code
            == 429,
        )
        add(
            "comment-create",
            client.post(
                "/api/client/feed/comment/create",
                headers=client_headers,
                json={"post_id": "p-1", "content": "smoke test", "client_id": "smoke-1"},
            ).status_code
            == 200,
        )
        add(
            "comment-create-with-image",
            client.post(
                "/api/client/feed/comment/create-with-image",
                headers=client_headers,
                data={"post_id": "p-1", "content": "smoke image", "client_id": "smoke-2"},
                files={"image": ("b.jpg", b"fake-jpg", "image/jpeg")},
            ).status_code
            == 200,
        )
        reply_resp = client.post(
            "/api/client/feed/comment/create",
            headers=client_headers,
            json={
                "post_id": "p-1",
                "content": "reply smoke",
                "client_id": "smoke-reply-1",
                "reply_to_comment_id": "c-1",
                "reply_to_author": "@清晨图书馆人",
            },
        )
        reply_ok = reply_resp.status_code == 200
        reply_payload = reply_resp.json() if reply_ok else {}
        add("comment-reply-create", reply_ok and str(reply_payload.get("reply_to_author", "")).startswith("@"))
        comment_resp = client.get(
            "/api/client/feed/comments",
            headers=client_headers,
            params={"post_id": "p-1", "page": 1, "page_size": 5},
        )
        comment_ok = comment_resp.status_code == 200
        comment_payload = comment_resp.json() if comment_ok else {}
        add(
            "comment-page",
            comment_ok
            and "items" in comment_payload
            and "total" in comment_payload
            and "has_more" in comment_payload,
        )
        search_resp = client.get(
            "/api/client/search/posts",
            headers=client_headers,
            params={"q": "A1", "sort": "hot", "page": 1, "page_size": 2},
        )
        search_ok = search_resp.status_code == 200
        search_payload = search_resp.json() if search_ok else {}
        add(
            "search",
            search_ok
            and "items" in search_payload
            and "total" in search_payload
            and "has_more" in search_payload,
        )
        add("unread", client.get("/api/client/messages/unread-count", headers=client_headers).status_code == 200)
        add("recent-save", client.post("/api/client/search/recent", headers=client_headers, json={"keyword": "空教室"}).status_code == 200)
        qa_resp = client.post(
            "/api/client/knowledge/ask",
            headers=client_headers,
            json={"query": "A1-307 晚自习", "history": []},
        )
        qa_ok = qa_resp.status_code == 200
        qa_payload = qa_resp.json() if qa_ok else {}
        add("knowledge-citations", qa_ok and isinstance(qa_payload.get("citations"), list))
        qa_deep = client.post(
            "/api/client/knowledge/ask",
            headers=client_headers,
            json={"query": "A1-307 晚自习", "history": [], "deep_thinking": True},
        )
        qa_deep_ok = qa_deep.status_code == 200
        qa_deep_payload = qa_deep.json() if qa_deep_ok else {}
        add("knowledge-deep", qa_deep_ok and "rerank_used" in qa_deep_payload)

        refresh_resp = client.post("/api/client/auth/refresh", json={"refresh_token": refresh_token})
        add("refresh-token", refresh_resp.status_code == 200)

        admin_username, admin_password = _admin_credentials()
        login_resp = client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": admin_password},
        )
        token_ok = login_resp.status_code == 200 and login_resp.json().get("access_token")
        add("admin-login", bool(token_ok))
        admin_headers = {"Authorization": f"Bearer {login_resp.json().get('access_token', '')}"} if token_ok else {}

        add("kb", client.get("/api/admin/kb", headers=admin_headers).status_code == 200)
        add("dashboard", client.get("/api/admin/dashboard/summary", headers=admin_headers).status_code == 200)
        add("devtools-status", client.get("/api/admin/devtools/status", headers=admin_headers).status_code == 200)
        add("devtools-self-check", client.post("/api/admin/devtools/self-check", headers=admin_headers).status_code == 200)
        add("devtools-config", client.get("/api/admin/devtools/config", headers=admin_headers).status_code == 200)
        add("evolution", client.post("/api/admin/rag/evolution/sync-high-quality-posts", headers=admin_headers).status_code == 200)
        add(
            "adopt-comment",
            client.post(
                "/api/admin/feed/adopt-comment",
                headers=admin_headers,
                json={"post_id": "p-1", "comment_id": "c-1", "prune_other_comments": True, "hard_delete": False},
            ).status_code
            == 200,
        )
        add("adoption-list", client.get("/api/admin/feed/adoptions", headers=admin_headers).status_code == 200)
        add(
            "cleanup-stale",
            client.post("/api/admin/maintenance/cleanup-stale-posts?days=7", headers=admin_headers).status_code == 200,
        )
        add("edu-auth-guard", client.get("/api/client/edu/overview").status_code == 401)
        add(
            "edu-overview",
            client.get(
                "/api/client/edu/overview",
                headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
            ).status_code
            == 200,
        )
        add(
            "edu-grades-term",
            client.get(
                "/api/client/edu/grades",
                params={"term": "2024-2025春学期"},
                headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
            ).status_code
            == 200,
        )
        add(
            "edu-schedule-week",
            client.get(
                "/api/client/edu/schedule",
                params={"week_no": 12},
                headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
            ).status_code
            == 200,
        )
        add(
            "edu-exams",
            client.get(
                "/api/client/edu/exams",
                headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
            ).status_code
            == 200,
        )
        add(
            "edu-free-campus",
            client.get(
                "/api/client/edu/free-classrooms",
                params={"campus": "五四路校区"},
                headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
            ).status_code
            == 200,
        )
        add(
            "edu-free-building",
            client.get(
                "/api/client/edu/free-classrooms",
                params={"campus": "七一路校区", "building": "A4座"},
                headers={**client_headers, "X-Edu-Session": "demo-edu-session"},
            ).status_code
            == 200,
        )
        studio_resp = client.get("/studio/")
        add("studio-page", studio_resp.status_code == 200 and "校园知识工作台" in studio_resp.text)

    failed = [item for item in checks if not item[1]]
    for name, ok, detail in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")

    print(f"TOTAL={len(checks)} FAIL={len(failed)}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
