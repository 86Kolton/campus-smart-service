from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_studio_qa_debug_refreshes_stale_client_token() -> None:
    studio_js = read_text("backend/app/static/studio/studio.js")
    studio_html = read_text("backend/app/static/studio/index.html")

    assert "isTokenInvalidError" in studio_js
    assert "createApiError" in studio_js
    assert "authScope = auth ? \"admin\" : (finalHeaders.Authorization ? \"client\" : \"none\")" in studio_js
    assert "resetClientDebugToken" in studio_js
    assert "token_expired" in studio_js
    assert "客户端调试 token 已失效，已自动刷新后重试。" in studio_js
    assert "payload = await request();" in studio_js
    assert "studio.js?v=20260519-config-clarity" in studio_html


def test_studio_exposes_document_review_editor_and_adoption_repair() -> None:
    studio_js = read_text("backend/app/static/studio/studio.js")
    studio_html = read_text("backend/app/static/studio/index.html")
    studio_css = read_text("backend/app/static/studio/studio.css")

    assert 'id="docEditor"' in studio_html
    assert 'id="btnRepairAdoptions"' in studio_html
    assert "/api/admin/documents/${encodeURIComponent(id)}/content" in studio_js
    assert "/api/admin/feed/adoptions/repair?limit=1000" in studio_js
    assert "保存并重新入库" in studio_js
    assert "不保留此条" in studio_js
    assert "openKbDocuments" in studio_js
    assert "data-action=\"open-kb-docs\"" in studio_js
    assert "state.selectedDocument = null;" in studio_js
    assert "document_pdf_text_empty" in studio_js
    assert "DOCUMENT_OCR_MODEL" in studio_js
    assert "document_ocr_failed" in studio_js
    assert ".xls,.xlsx,.ppt,.pptx,.odt,.ods,.odp" in studio_html
    assert ".png,.jpg,.jpeg,.webp,.bmp,.tif,.tiff" in studio_html
    assert "qdrant_optional_local_fallback" in studio_js
    assert "evolution_ai_review_config" in studio_js
    assert "当前 AI 审核已配置为复用 QA" in studio_js
    assert "自进化 AI 审核已就绪：当前复用 QA" in studio_js
    assert "复用 QA_BASE_URL，无需单独填写" in studio_js
    assert "复用 QA_API_KEY，无需单独填写" in studio_js
    assert "复用 QA_MODEL，无需单独填写" in studio_js
    assert "AI审核 ${status.evolution_ai_review_provider || \"-\"}" in studio_js
    assert "config-group-notice" in studio_css
    assert ".status-pill.warn" in studio_css
    assert "doc-content-editor" in studio_css
