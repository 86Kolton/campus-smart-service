from __future__ import annotations

import hashlib

import httpx

from app.core.config import settings


class WechatService:
    @staticmethod
    def _mock_openid(code: str) -> str:
        seed = str(code or "").strip() or "mock"
        digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()
        return f"wx_mock_{digest[:24]}"

    @staticmethod
    def _is_configured() -> bool:
        return bool(str(settings.wechat_app_id or "").strip() and str(settings.wechat_app_secret or "").strip())

    async def code_to_openid(self, code: str) -> tuple[str, bool]:
        safe_code = str(code or "").strip()
        if not safe_code:
            raise ValueError("wechat_code_required")

        is_configured = self._is_configured()
        if not is_configured and settings.wechat_mock_effective:
            return self._mock_openid(safe_code), True
        if not is_configured:
            raise ValueError("wechat_not_configured")

        params = {
            "appid": str(settings.wechat_app_id or "").strip(),
            "secret": str(settings.wechat_app_secret or "").strip(),
            "js_code": safe_code,
            "grant_type": "authorization_code",
        }
        url = str(settings.wechat_code2session_url or "").strip() or "https://api.weixin.qq.com/sns/jscode2session"
        timeout = max(3, int(settings.wechat_timeout_seconds or 10))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:
            raise ValueError("wechat_code2session_failed") from exc

        errcode = payload.get("errcode")
        if errcode not in (None, 0, "0"):
            raise ValueError(f"wechat_code2session_{errcode}")

        openid = str(payload.get("openid") or "").strip()
        if not openid:
            raise ValueError("wechat_openid_missing")

        return openid, False


wechat_service = WechatService()
