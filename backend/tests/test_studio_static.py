from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_studio_qa_debug_refreshes_stale_client_token() -> None:
    studio_js = read_text("backend/app/static/studio/studio.js")

    assert "isTokenInvalidError" in studio_js
    assert "resetClientDebugToken" in studio_js
    assert "客户端调试 token 已失效，已自动刷新后重试。" in studio_js
    assert "payload = await request();" in studio_js
