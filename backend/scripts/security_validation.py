from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import uuid4

import httpx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def ensure_status(resp: httpx.Response, expected: int | set[int]) -> tuple[bool, str]:
    expected_codes = expected if isinstance(expected, set) else {expected}
    ok = resp.status_code in expected_codes
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


def validate(admin_base_url: str, client_base_url: str, name: str) -> int:
    runner = Runner(name)
    admin_base = admin_base_url.rstrip("/")
    client_base = client_base_url.rstrip("/")
    admin_username = str(settings.admin_username or "").strip()
    admin_password = str(settings.admin_password or "").strip()

    with httpx.Client(base_url=admin_base, timeout=90.0, follow_redirects=False) as admin_client, httpx.Client(
        base_url=client_base,
        timeout=90.0,
        follow_redirects=False,
    ) as client:
        health_admin = admin_client.get("/healthz")
        ok, detail = ensure_status(health_admin, 200)
        runner.add("admin-healthz", ok, detail)

        health_client = client.get("/healthz")
        ok, detail = ensure_status(health_client, 200)
        runner.add("client-healthz", ok, detail)

        client_guard = client.get("/api/client/profile/summary")
        ok, detail = ensure_status(client_guard, 401)
        runner.add("client-auth-guard", ok, detail)

        bad_client_login = client.post(
            "/api/client/auth/login",
            json={"username": "zhaoyi", "password": "definitely-wrong"},
        )
        ok, detail = ensure_status(bad_client_login, 401)
        runner.add("client-invalid-login", ok, detail)

        admin_guard = admin_client.get("/api/admin/dashboard/summary")
        ok, detail = ensure_status(admin_guard, 401)
        runner.add("admin-auth-guard", ok, detail)

        bad_admin_login = admin_client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": f"{admin_password}-wrong"},
            headers={"User-Agent": f"security-precheck-{uuid4().hex}"},
        )
        ok, detail = ensure_status(bad_admin_login, 401)
        runner.add("admin-invalid-login", ok, detail)

        attack_headers = {"User-Agent": f"security-guard-{uuid4().hex}"}
        blocked = False
        for _ in range(max(2, int(settings.admin_login_max_attempts or 5)) + 1):
            resp = admin_client.post(
                "/api/admin/auth/login",
                json={"username": admin_username, "password": f"{admin_password}-wrong"},
                headers=attack_headers,
            )
            if resp.status_code == 429:
                blocked = True
                runner.add("admin-login-lock-triggered", True, f"status=429 detail={resp.text[:120]}")
                break
        if not blocked:
            runner.add("admin-login-lock-triggered", False, "did not reach 429 after repeated failures")

        if blocked:
            blocked_with_correct_password = admin_client.post(
                "/api/admin/auth/login",
                json={"username": admin_username, "password": admin_password},
                headers=attack_headers,
            )
            ok, detail = ensure_status(blocked_with_correct_password, 429)
            runner.add("admin-login-lock-enforced", ok, detail)

        good_admin_login = admin_client.post(
            "/api/admin/auth/login",
            json={"username": admin_username, "password": admin_password},
            headers={"User-Agent": f"security-good-{uuid4().hex}"},
        )
        ok, detail = ensure_status(good_admin_login, 200)
        runner.add("admin-login-success", ok, detail)
        admin_token = str(good_admin_login.json().get("access_token", "")).strip() if ok else ""
        runner.add("admin-token-issued", bool(admin_token), "missing access token" if not admin_token else "")

        if admin_token:
            admin_summary = admin_client.get("/api/admin/dashboard/summary", headers=auth_headers(admin_token))
            ok, detail = ensure_status(admin_summary, 200)
            runner.add("admin-summary-after-login", ok, detail)

        if admin_base != client_base:
            user_domain_studio = client.get("/studio/")
            ok, detail = ensure_status(user_domain_studio, {404, 403})
            runner.add("client-domain-hide-studio", ok, detail)

            user_domain_admin_api = client.post(
                "/api/admin/auth/login",
                json={"username": admin_username, "password": admin_password},
            )
            ok, detail = ensure_status(user_domain_admin_api, {403, 404})
            runner.add("client-domain-block-admin-api", ok, detail)
        else:
            runner.add("client-domain-hide-studio", True, "single-domain local validation skipped")
            runner.add("client-domain-block-admin-api", True, "single-domain local validation skipped")

    return runner.finish()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--admin-base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--client-base-url", default="")
    parser.add_argument("--name", default="local-security")
    args = parser.parse_args()

    client_base_url = args.client_base_url or args.admin_base_url
    return validate(args.admin_base_url, client_base_url, args.name)


if __name__ == "__main__":
    raise SystemExit(main())
