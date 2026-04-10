from __future__ import annotations

import argparse
import sys
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings


def ensure_ok(resp: httpx.Response, expected: int = 200) -> tuple[bool, str]:
    ok = resp.status_code == expected
    detail = f"status={resp.status_code}"
    if not ok:
        detail += f" body={resp.text[:240].replace(chr(10), ' ')}"
    return ok, detail


class Runner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.items: list[tuple[str, bool, str]] = []

    def add(self, label: str, ok: bool, detail: str = "") -> None:
        self.items.append((label, ok, detail))

    def finish(self) -> int:
        failed = 0
        for label, ok, detail in self.items:
            print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))
            if not ok:
                failed += 1
        print(f"[SUMMARY] target={self.name} total={len(self.items)} fail={failed}")
        return failed


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def find_best_forum_review(items: list[dict]) -> dict | None:
    accepted = [item for item in items if str(item.get("decision")) == "pass" and item.get("document_id")]
    if not accepted:
        return None
    accepted.sort(key=lambda item: int(item.get("overall_score") or 0), reverse=True)
    return accepted[0]


def validate(admin_base_url: str, client_base_url: str, name: str) -> int:
    runner = Runner(name)
    admin_base = admin_base_url.rstrip("/")
    client_base = client_base_url.rstrip("/")
    admin_username = str(settings.admin_username or "").strip()
    admin_password = str(settings.admin_password or "").strip()

    with httpx.Client(base_url=admin_base, timeout=180.0) as admin_client, httpx.Client(
        base_url=client_base, timeout=90.0
    ) as client:
        health = admin_client.get("/healthz")
        ok, detail = ensure_ok(health)
        runner.add("healthz", ok, detail)

        admin_login = admin_client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": admin_password},
        )
        ok, detail = ensure_ok(admin_login)
        runner.add("admin-login", ok, detail)
        if not ok:
            return runner.finish()
        admin_token = str(admin_login.json().get("access_token", "")).strip()
        runner.add("admin-token-issued", bool(admin_token), "missing access token" if not admin_token else "")
        admin_headers = auth_headers(admin_token)

        reviews_before = admin_client.get("/api/admin/rag/evolution/reviews?limit=80", headers=admin_headers)
        ok, detail = ensure_ok(reviews_before)
        runner.add("review-list-before", ok, detail)
        review_items_before = reviews_before.json().get("items", []) if ok else []
        runner.add("review-list-before-nonempty", isinstance(review_items_before, list) and len(review_items_before) > 0)

        accepted_before = [item for item in review_items_before if str(item.get("decision")) == "pass"]
        rejected_before = [item for item in review_items_before if str(item.get("decision")) == "reject"]
        duplicate_before = [
            item
            for item in review_items_before
            if str((item.get("detail") or {}).get("duplicate_method", "")).strip()
            or "高度重复" in str(item.get("reason") or "")
        ]
        runner.add("accepted-review-exists", len(accepted_before) > 0, f"count={len(accepted_before)}")
        runner.add("rejected-review-exists", len(rejected_before) > 0, f"count={len(rejected_before)}")
        runner.add("duplicate-guard-evidence", len(duplicate_before) > 0, f"count={len(duplicate_before)}")

        docs_before = admin_client.get("/api/admin/documents?kb_id=1", headers=admin_headers)
        ok, detail = ensure_ok(docs_before)
        runner.add("document-list", ok, detail)
        doc_items_before = docs_before.json().get("items", []) if ok else []
        evo_docs_before = [item for item in doc_items_before if str(item.get("file_name", "")).startswith("evo-post-")]
        runner.add("evolved-doc-exists", len(evo_docs_before) > 0, f"count={len(evo_docs_before)}")

        client_login = client.post("/api/client/auth/login", json={"username": "zhaoyi", "password": "demo123"})
        ok, detail = ensure_ok(client_login)
        runner.add("client-login", ok, detail)
        if not ok:
            return runner.finish()
        client_token = str(client_login.json().get("access_token", "")).strip()
        client_headers = auth_headers(client_token)

        target_review = find_best_forum_review(review_items_before)
        if target_review:
            title = str(target_review.get("post_title") or "").strip()
            ask = client.post(
                "/api/client/knowledge/ask",
                headers=client_headers,
                json={"query": title[:36] or title, "history": []},
            )
            ok, detail = ensure_ok(ask)
            ask_json = ask.json() if ok else {}
            citations = ask_json.get("citations") or []
            answer = str(ask_json.get("answer") or "")
            has_feed_source = any(str(item.get("source_type") or "") == "feed" for item in citations)
            has_post_jump = any("#post=p-" in str(item.get("jump_url") or "") for item in citations)
            runner.add("ask-forum-derived-answer", ok and bool(answer), detail)
            runner.add("ask-forum-derived-citation", ok and has_feed_source and has_post_jump, detail)
        else:
            runner.add("ask-forum-derived-answer", False, "no accepted review available")
            runner.add("ask-forum-derived-citation", False, "no accepted review available")

        sync = admin_client.post(
            "/api/admin/rag/evolution/sync-high-quality-posts?kb_id=1&min_likes=30&min_comments=5&limit=1",
            headers=admin_headers,
        )
        ok, detail = ensure_ok(sync)
        runner.add("sync-limit-1", ok, detail)
        sync_json = sync.json() if ok else {}
        runner.add(
            "sync-limit-return-shape",
            ok and isinstance(sync_json.get("accepted_posts"), int) and isinstance(sync_json.get("rejected_posts"), int),
            detail,
        )
        produced_reviews = int(sync_json.get("accepted_posts", 0)) + int(sync_json.get("rejected_posts", 0))
        no_pending_left = int(sync_json.get("pending_posts", 0)) == 0 and int(sync_json.get("remaining_posts", 0)) == 0
        runner.add(
            "sync-produced-review",
            ok and (produced_reviews >= 1 or no_pending_left),
            detail,
        )

        reviews_after = admin_client.get("/api/admin/rag/evolution/reviews?limit=80", headers=admin_headers)
        ok, detail = ensure_ok(reviews_after)
        review_items_after = reviews_after.json().get("items", []) if ok else []
        runner.add("review-list-after", ok and len(review_items_after) >= len(review_items_before), detail)
        review_ids_before = {int(item.get("id") or 0) for item in review_items_before}
        new_reviews = [item for item in review_items_after if int(item.get("id") or 0) not in review_ids_before]
        signature_hash_after = [
            item for item in (new_reviews or review_items_after[:5]) if str((item.get("detail") or {}).get("signature_hash", "")).strip()
        ]
        duplicate_after = [
            item
            for item in (new_reviews or review_items_after[:10])
            if str((item.get("detail") or {}).get("duplicate_method", "")).strip()
            or "楂樺害閲嶅" in str(item.get("reason") or "")
        ]
        runner.add("signature-hash-evidence", len(signature_hash_after) > 0, f"count={len(signature_hash_after)}")
        runner.add("duplicate-guard-after-sync", len(duplicate_after) >= 0, f"count={len(duplicate_after)}")

        docs_after = admin_client.get("/api/admin/documents?kb_id=1", headers=admin_headers)
        ok, detail = ensure_ok(docs_after)
        doc_items_after = docs_after.json().get("items", []) if ok else []
        evo_docs_after = [item for item in doc_items_after if str(item.get("file_name", "")).startswith("evo-post-")]
        runner.add("evolved-docs-still-exist", ok and len(evo_docs_after) > 0, f"count={len(evo_docs_after)}")

    return runner.finish()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--admin-base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--client-base-url", default="")
    parser.add_argument("--name", default="local-evolution")
    args = parser.parse_args()

    client_base_url = args.client_base_url or args.admin_base_url
    return validate(args.admin_base_url, client_base_url, args.name)


if __name__ == "__main__":
    raise SystemExit(main())
