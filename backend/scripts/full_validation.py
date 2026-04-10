from __future__ import annotations

import argparse
import json
import random
import string
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import httpx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings


def get_admin_credentials() -> tuple[str, str]:
    username = str(settings.admin_username or "").strip()
    password = str(settings.admin_password or "").strip()
    if not username or not password:
        raise SystemExit("admin credentials are not configured in backend/.env")
    return username, password


def now_suffix() -> str:
    stamp = int(time.time())
    tail = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    return f"{stamp}{tail}"


class ValidationRunner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.groups: dict[str, list[tuple[str, bool, str]]] = defaultdict(list)

    def add(self, group: str, name: str, ok: bool, detail: str = "") -> None:
        self.groups[group].append((name, ok, detail))

    def summary(self) -> tuple[int, int]:
        total = 0
        failed = 0
        for group, items in self.groups.items():
            group_total = len(items)
            group_failed = len([item for item in items if not item[1]])
            total += group_total
            failed += group_failed
            print(f"[GROUP] {group} total={group_total} fail={group_failed}")
            for name, ok, detail in items:
                print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))
        print(f"[SUMMARY] target={self.name} total={total} fail={failed}")
        return total, failed


def ensure_ok(resp: httpx.Response, expected: int = 200) -> tuple[bool, str]:
    ok = resp.status_code == expected
    detail = f"status={resp.status_code}"
    if not ok:
        body = resp.text[:240].replace("\n", " ")
        detail += f" body={body}"
    return ok, detail


def ensure_ok_or_not_found(resp: httpx.Response) -> tuple[bool, str]:
    ok = resp.status_code in {200, 404}
    detail = f"status={resp.status_code}"
    if not ok:
        body = resp.text[:240].replace("\n", " ")
        detail += f" body={body}"
    return ok, detail


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def build_users() -> tuple[dict[str, str], dict[str, str]]:
    suffix = now_suffix()
    user_a = {
        "username": f"smoke_a_{suffix}",
        "display_name": f"测试甲{suffix[-4:]}",
        "password": "demo123",
    }
    user_b = {
        "username": f"smoke_b_{suffix}",
        "display_name": f"测试乙{suffix[-4:]}",
        "password": "demo123",
    }
    return user_a, user_b


def cleanup_created_data(
    client: httpx.Client,
    runner: ValidationRunner,
    *,
    a_token: str,
    a_refresh: str,
    b_token: str,
    post_a_id: str,
    post_b_id: str,
    post_img_id: str,
    errand_id: str,
) -> None:
    if errand_id and a_token:
        try:
            resp = client.post(
                "/api/client/errands/action",
                headers=auth_headers(a_token),
                json={"task_id": errand_id, "action": "delete"},
            )
            ok, detail = ensure_ok_or_not_found(resp)
        except Exception as exc:
            ok, detail = False, f"cleanup_errand_exception={exc}"
        runner.add("cleanup", "delete-errand", ok, detail)

    for label, token, post_id in [
        ("delete-post-a", a_token, post_a_id),
        ("delete-post-b", b_token, post_b_id),
        ("delete-post-image", a_token, post_img_id),
    ]:
        if not token or not post_id:
            continue
        try:
            resp = client.post(
                "/api/client/feed/post/delete",
                headers=auth_headers(token),
                json={"post_id": post_id},
            )
            ok, detail = ensure_ok_or_not_found(resp)
        except Exception as exc:
            ok, detail = False, f"{label}_exception={exc}"
        runner.add("cleanup", label, ok, detail)

    if a_token and a_refresh:
        try:
            resp = client.post(
                "/api/client/auth/logout",
                headers=auth_headers(a_token),
                json={"refresh_token": a_refresh},
            )
            ok, detail = ensure_ok(resp, 200)
        except Exception as exc:
            ok, detail = False, f"logout_exception={exc}"
        runner.add("cleanup", "logout-a", ok, detail)


def validation_flow(
    *,
    base_url: str,
    admin_username: str,
    admin_password: str,
    name: str,
) -> int:
    runner = ValidationRunner(name)
    user_a, user_b = build_users()
    a_token = ""
    a_refresh = ""
    b_token = ""
    post_a_id = ""
    post_b_id = ""
    post_img_id = ""
    comment_b_id = ""
    errand_id = ""

    with httpx.Client(base_url=base_url.rstrip("/"), timeout=90.0) as client:
        try:
            health = client.get("/healthz")
            ok, detail = ensure_ok(health, 200)
            runner.add("auth", "healthz", ok, detail)

            reg_a = client.post("/api/client/auth/register", json=user_a)
            ok, detail = ensure_ok(reg_a, 200)
            runner.add("auth", "register-a", ok, detail)
            a_payload = reg_a.json() if ok else {}
            a_token = str(a_payload.get("access_token", ""))
            a_refresh = str(a_payload.get("refresh_token", ""))
            runner.add("auth", "register-a-token", bool(a_token and a_refresh), "missing token" if not (a_token and a_refresh) else "")

            reg_b = client.post("/api/client/auth/register", json=user_b)
            ok, detail = ensure_ok(reg_b, 200)
            runner.add("auth", "register-b", ok, detail)
            b_payload = reg_b.json() if ok else {}
            b_token = str(b_payload.get("access_token", ""))
            runner.add("auth", "register-b-token", bool(b_token), "missing token" if not b_token else "")

            me_a = client.get("/api/client/auth/me", headers=auth_headers(a_token))
            ok, detail = ensure_ok(me_a, 200)
            me_json = me_a.json() if ok else {}
            runner.add("auth", "me-a", ok and str(me_json.get("username")) == user_a["username"], detail)

            refresh_a = client.post("/api/client/auth/refresh", json={"refresh_token": a_refresh})
            ok, detail = ensure_ok(refresh_a, 200)
            refresh_json = refresh_a.json() if ok else {}
            refreshed_token = str(refresh_json.get("access_token", ""))
            runner.add("auth", "refresh-a", ok and bool(refreshed_token), detail)
            if refreshed_token:
                a_token = refreshed_token

            login_a = client.post("/api/client/auth/login", json={"username": user_a["username"], "password": user_a["password"]})
            ok, detail = ensure_ok(login_a, 200)
            runner.add("auth", "login-a", ok, detail)

            web_login_code = client.post(
                "/api/client/auth/web-login-code",
                headers=auth_headers(a_token),
            )
            ok, detail = ensure_ok(web_login_code, 200)
            web_login_code_json = web_login_code.json() if ok else {}
            login_code = str(web_login_code_json.get("code", ""))
            runner.add("auth", "web-login-code", ok and len(login_code) >= 6, detail)

            web_login_exchange = client.post(
                "/api/client/auth/web-login-exchange",
                json={"code": login_code},
            )
            ok, detail = ensure_ok(web_login_exchange, 200)
            web_login_exchange_json = web_login_exchange.json() if ok else {}
            runner.add(
                "auth",
                "web-login-exchange",
                ok and str(web_login_exchange_json.get("username", "")) == user_a["username"],
                detail,
            )

            feed_a = client.get("/api/client/feed/list", headers=auth_headers(a_token))
            ok, detail = ensure_ok(feed_a, 200)
            feed_json = feed_a.json() if ok else {}
            feed_items = feed_json.get("items") or []
            runner.add("feed", "feed-list", ok and isinstance(feed_items, list), detail)

            create_post_a = client.post(
                "/api/client/feed/post/create",
                headers=auth_headers(a_token),
                json={
                    "category": "study",
                    "title": f"验证贴 A {name}",
                    "content": "这是全链路验证创建的帖子，用于点赞、评论、收藏和删除回归。",
                    "tags": ["验证", "回归", "学习空间"],
                },
            )
            ok, detail = ensure_ok(create_post_a, 200)
            post_a = create_post_a.json() if ok else {}
            post_a_id = str(post_a.get("id", ""))
            runner.add("feed", "create-post-a", ok and post_a_id.startswith("p-"), detail)

            create_post_b = client.post(
                "/api/client/feed/post/create",
                headers=auth_headers(b_token),
                json={
                    "category": "market",
                    "title": f"验证贴 B {name}",
                    "content": "这是用于收藏列表回归的帖子，作者是测试乙。",
                    "tags": ["验证", "二手交易"],
                },
            )
            ok, detail = ensure_ok(create_post_b, 200)
            post_b = create_post_b.json() if ok else {}
            post_b_id = str(post_b.get("id", ""))
            runner.add("feed", "create-post-b", ok and post_b_id.startswith("p-"), detail)

            create_post_img = client.post(
                "/api/client/feed/post/create-with-image",
                headers=auth_headers(a_token),
                data={
                    "category": "study",
                    "title": f"图文验证贴 {name}",
                    "content": "带图片的发帖验证。",
                    "tags": json.dumps(["图文", "验证"], ensure_ascii=False),
                },
                files={"image": ("seed.png", b"fake-png", "image/png")},
            )
            ok, detail = ensure_ok(create_post_img, 200)
            post_img_json = create_post_img.json() if ok else {}
            post_img_id = str(post_img_json.get("id", ""))
            runner.add("feed", "create-post-with-image", ok and post_img_id.startswith("p-"), detail)

            like_post = client.post(
                "/api/client/feed/like",
                headers=auth_headers(b_token),
                json={"post_id": post_a_id, "liked": True},
            )
            ok, detail = ensure_ok(like_post, 200)
            like_json = like_post.json() if ok else {}
            runner.add("feed", "like-post", ok and like_json.get("liked") is True, detail)

            comment_b = client.post(
                "/api/client/feed/comment/create",
                headers=auth_headers(b_token),
                json={"post_id": post_a_id, "content": "测试乙的评论，用于评论链路验证。", "client_id": f"{name}-comment-b"},
            )
            ok, detail = ensure_ok(comment_b, 200)
            comment_json = comment_b.json() if ok else {}
            comment_b_id = str(comment_json.get("id", ""))
            runner.add("feed", "comment-create", ok and comment_b_id.startswith("c-"), detail)

            comment_like = client.post(
                "/api/client/feed/comment/like",
                headers=auth_headers(a_token),
                json={"comment_id": comment_b_id, "liked": True},
            )
            ok, detail = ensure_ok(comment_like, 200)
            comment_like_json = comment_like.json() if ok else {}
            runner.add("feed", "comment-like", ok and comment_like_json.get("liked") is True, detail)

            comment_list = client.get(
                "/api/client/feed/comments",
                headers=auth_headers(a_token),
                params={"post_id": post_a_id, "page": 1, "page_size": 20},
            )
            ok, detail = ensure_ok(comment_list, 200)
            comment_items = comment_list.json().get("items") if ok else []
            runner.add(
                "feed",
                "comment-list",
                ok and any(str(item.get("id")) == comment_b_id for item in (comment_items or [])),
                detail,
            )

            save_post = client.post(
                "/api/client/feed/save",
                headers=auth_headers(a_token),
                json={"post_id": post_b_id, "saved": True},
            )
            ok, detail = ensure_ok(save_post, 200)
            save_json = save_post.json() if ok else {}
            runner.add("feed", "save-post", ok and save_json.get("saved") is True, detail)

            delete_post_img = client.post(
                "/api/client/feed/post/delete",
                headers=auth_headers(a_token),
                json={"post_id": post_img_id},
            )
            ok, detail = ensure_ok(delete_post_img, 200)
            delete_json = delete_post_img.json() if ok else {}
            runner.add("feed", "delete-own-post", ok and delete_json.get("deleted") is True, detail)

            search = client.get(
                "/api/client/search/posts",
                headers=auth_headers(a_token),
                params={"q": "河北大学", "sort": "hot", "page": 1, "page_size": 10},
            )
            ok, detail = ensure_ok(search, 200)
            search_json = search.json() if ok else {}
            runner.add("knowledge", "search-posts", ok and isinstance(search_json.get("items"), list), detail)

            save_recent = client.post(
                "/api/client/search/recent",
                headers=auth_headers(a_token),
                json={"keyword": "河北大学 邮编"},
            )
            ok, detail = ensure_ok(save_recent, 200)
            runner.add("knowledge", "save-recent", ok, detail)

            recent = client.get("/api/client/search/recent", headers=auth_headers(a_token))
            ok, detail = ensure_ok(recent, 200)
            recent_json = recent.json() if ok else {}
            keywords = recent_json.get("keywords") or []
            runner.add("knowledge", "recent-list", ok and isinstance(keywords, list) and len(keywords) >= 1, detail)

            ask_precise = client.post(
                "/api/client/knowledge/ask",
                headers=auth_headers(a_token),
                json={"query": "河北大学邮编是多少", "history": []},
            )
            ok, detail = ensure_ok(ask_precise, 200)
            ask_precise_json = ask_precise.json() if ok else {}
            citations = ask_precise_json.get("citations") or []
            answer_text = str(ask_precise_json.get("answer", ""))
            runner.add("knowledge", "ask-precise", ok and bool(answer_text) and "071002" in answer_text, detail)
            runner.add("knowledge", "ask-precise-citations", ok and isinstance(citations, list) and len(citations) >= 1, detail)

            ask_fuzzy = client.post(
                "/api/client/knowledge/ask",
                headers=auth_headers(a_token),
                json={"query": "校况", "history": []},
            )
            ok, detail = ensure_ok(ask_fuzzy, 200)
            ask_fuzzy_json = ask_fuzzy.json() if ok else {}
            fuzzy_answer = str(ask_fuzzy_json.get("answer", ""))
            runner.add(
                "knowledge",
                "ask-fuzzy",
                ok and bool(fuzzy_answer) and "相关度" not in fuzzy_answer and "资料方向" not in fuzzy_answer,
                detail,
            )

            ask_deep = client.post(
                "/api/client/knowledge/ask",
                headers=auth_headers(a_token),
                json={"query": "河北大学软件工程 ISEC 是什么", "history": [], "deep_thinking": True},
            )
            ok, detail = ensure_ok(ask_deep, 200)
            ask_deep_json = ask_deep.json() if ok else {}
            deep_answer = str(ask_deep_json.get("answer", ""))
            deep_citations = ask_deep_json.get("citations") or []
            allowed_domains = ("hbu.edu.cn", "xxgk.hbu.edu.cn", "lib.hbu.cn", "yjsy.hbu.edu.cn", "jwc.hbu.edu.cn", "intl.hbu.edu.cn")
            citations_ok = any(any(domain in str(item.get("jump_url", "")) for domain in allowed_domains) for item in deep_citations)
            runner.add("knowledge", "ask-deep", ok and bool(deep_answer), detail)
            runner.add("knowledge", "ask-deep-official-source", ok and citations_ok, detail)

            errands_before = client.get("/api/client/errands", headers=auth_headers(b_token))
            ok, detail = ensure_ok(errands_before, 200)
            runner.add("errand", "list-before-create", ok and isinstance(errands_before.json().get("items"), list), detail)

            create_errand = client.post(
                "/api/client/errands",
                headers=auth_headers(a_token),
                json={
                    "task_type": "delivery",
                    "title": f"验证跑腿 {name}",
                    "reward": "6",
                    "time": "20 分钟内",
                    "pickup_location": "北食堂骑手取餐点",
                    "destination": "A 区教学楼门口",
                    "note": "接到后电话提醒即可。",
                    "contact": f"手机号：1390000{name[-4:]} / 微信：val_{name[-4:]}",
                },
            )
            ok, detail = ensure_ok(create_errand, 200)
            create_errand_json = create_errand.json() if ok else {}
            errand_id = str(create_errand_json.get("id", ""))
            runner.add("errand", "create-errand", ok and errand_id.startswith("e-"), detail)

            errands_hidden = client.get("/api/client/errands", headers=auth_headers(b_token))
            ok, detail = ensure_ok(errands_hidden, 200)
            hidden_items = errands_hidden.json().get("items") if ok else []
            hidden_item = next((item for item in (hidden_items or []) if str(item.get("id")) == errand_id), {})
            hidden_contact = str(hidden_item.get("publisher_contact", ""))
            runner.add("errand", "contact-hidden-before-claim", ok and "接单后可见" in hidden_contact, detail)

            claim_errand = client.post(
                "/api/client/errands/action",
                headers=auth_headers(b_token),
                json={"task_id": errand_id, "action": "claim"},
            )
            ok, detail = ensure_ok(claim_errand, 200)
            claim_json = claim_errand.json() if ok else {}
            claimed_item = claim_json.get("item") or {}
            claim_contact = str(claimed_item.get("publisher_contact", ""))
            runner.add("errand", "claim-errand", ok and bool(claim_contact) and "接单后可见" not in claim_contact, detail)

            delivered = client.post(
                "/api/client/errands/action",
                headers=auth_headers(b_token),
                json={"task_id": errand_id, "action": "delivered"},
            )
            ok, detail = ensure_ok(delivered, 200)
            delivered_json = delivered.json() if ok else {}
            runner.add("errand", "deliver-errand", ok and str((delivered_json.get("item") or {}).get("status")) == "waiting_confirm", detail)

            confirm = client.post(
                "/api/client/errands/action",
                headers=auth_headers(a_token),
                json={"task_id": errand_id, "action": "confirm"},
            )
            ok, detail = ensure_ok(confirm, 200)
            confirm_json = confirm.json() if ok else {}
            runner.add("errand", "confirm-errand", ok and str((confirm_json.get("item") or {}).get("status")) == "done", detail)

            my_errands = client.get("/api/client/errands/my", headers=auth_headers(a_token))
            ok, detail = ensure_ok(my_errands, 200)
            my_errand_items = my_errands.json().get("items") if ok else []
            runner.add("errand", "my-errands", ok and any(str(item.get("id")) == errand_id for item in (my_errand_items or [])), detail)

            summary = client.get("/api/client/profile/summary", headers=auth_headers(a_token))
            ok, detail = ensure_ok(summary, 200)
            summary_json = summary.json() if ok else {}
            runner.add("profile", "profile-summary", ok and int(summary_json.get("posts", 0)) >= 2, detail)

            settings = client.get("/api/client/profile/settings", headers=auth_headers(a_token))
            ok, detail = ensure_ok(settings, 200)
            settings_json = settings.json() if ok else {}
            runner.add("profile", "profile-settings", ok and bool(settings_json.get("public_name")), detail)

            new_public_name = f"微同学{name[-4:]}"
            update_public_name = client.post(
                "/api/client/profile/public-name",
                headers=auth_headers(a_token),
                json={"public_name": new_public_name},
            )
            ok, detail = ensure_ok(update_public_name, 200)
            update_json = update_public_name.json() if ok else {}
            runner.add("profile", "update-public-name", ok and str(update_json.get("public_name")) == new_public_name, detail)

            unread_a = client.get("/api/client/messages/unread-count", headers=auth_headers(a_token))
            ok, detail = ensure_ok(unread_a, 200)
            unread_a_json = unread_a.json() if ok else {}
            runner.add("profile", "unread-likes-for-a", ok and int(unread_a_json.get("likes_total", 0)) >= 1, detail)
            runner.add("profile", "saved-total-for-a", ok and int(unread_a_json.get("saved_total", 0)) >= 1, detail)

            likes_list_a = client.get("/api/client/messages/likes", headers=auth_headers(a_token))
            ok, detail = ensure_ok(likes_list_a, 200)
            likes_list_json = likes_list_a.json() if ok else {}
            likes_items = likes_list_json.get("items") or []
            runner.add("profile", "likes-list", ok and len(likes_items) >= 1, detail)

            saved_list_a = client.get("/api/client/messages/saved", headers=auth_headers(a_token))
            ok, detail = ensure_ok(saved_list_a, 200)
            saved_list_json = saved_list_a.json() if ok else {}
            saved_items = saved_list_json.get("items") or []
            runner.add("profile", "saved-list", ok and any(str(item.get("post_id")) == post_b_id for item in saved_items), detail)

            mark_read = client.post(
                "/api/client/messages/mark-read",
                headers=auth_headers(a_token),
                json={"type": "likes"},
            )
            ok, detail = ensure_ok(mark_read, 200)
            runner.add("profile", "mark-read", ok, detail)

            admin_login = client.post("/api/admin/auth/login", json={"username": admin_username, "password": admin_password})
            ok, detail = ensure_ok(admin_login, 200)
            admin_json = admin_login.json() if ok else {}
            admin_token = str(admin_json.get("access_token", ""))
            runner.add("admin", "admin-login", ok and bool(admin_token), detail)
            admin_headers = auth_headers(admin_token) if admin_token else {}

            for label, method, path in [
                ("dashboard-summary", "GET", "/api/admin/dashboard/summary"),
                ("kb-list", "GET", "/api/admin/kb"),
                ("document-list", "GET", "/api/admin/documents?kb_id=1"),
                ("qa-logs", "GET", "/api/admin/logs/qa"),
                ("devtools-status", "GET", "/api/admin/devtools/status"),
                ("devtools-config", "GET", "/api/admin/devtools/config"),
                ("tasks", "GET", "/api/admin/tasks"),
                ("evolution-sync", "POST", "/api/admin/rag/evolution/sync-high-quality-posts?kb_id=1&min_likes=999&min_comments=999&limit=1"),
                ("maintenance-cleanup", "POST", "/api/admin/maintenance/cleanup-stale-posts?days=7"),
            ]:
                try:
                    resp = client.get(path, headers=admin_headers) if method == "GET" else client.post(path, headers=admin_headers)
                    ok, detail = ensure_ok(resp, 200)
                except Exception as exc:
                    ok, detail = False, f"{label}_exception={exc}"
                runner.add("admin", label, ok, detail)

            studio = client.get("/studio/")
            ok, detail = ensure_ok(studio, 200)
            runner.add("admin", "studio-page", ok and "校园知识工作台" in studio.text, detail)
        finally:
            cleanup_created_data(
                client,
                runner,
                a_token=a_token,
                a_refresh=a_refresh,
                b_token=b_token,
                post_a_id=post_a_id,
                post_b_id=post_b_id,
                post_img_id=post_img_id,
                errand_id=errand_id,
            )

    _, failed = runner.summary()
    return failed


def main() -> None:
    admin_username, admin_password = get_admin_credentials()
    parser = argparse.ArgumentParser(description="Run grouped end-to-end validations against local or remote HTTP targets.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--admin-username", default=admin_username)
    parser.add_argument("--admin-password", default=admin_password)
    parser.add_argument("--name", default="local")
    args = parser.parse_args()

    failed = validation_flow(
        base_url=args.base_url,
        admin_username=args.admin_username,
        admin_password=args.admin_password,
        name=args.name,
    )
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
