from __future__ import annotations

from pathlib import Path
from uuid import uuid4


MAX_DOCUMENT_BYTES = 5 * 1024 * 1024
ALLOWED_DOCUMENT_EXT = {".txt", ".md", ".csv", ".json", ".log"}
ALLOWED_DOCUMENT_MIME = {
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
    ".csv": {"text/csv", "text/plain", "application/vnd.ms-excel", "application/octet-stream"},
    ".json": {"application/json", "text/json", "text/plain", "application/octet-stream"},
    ".log": {"text/plain", "application/octet-stream"},
}


class DocumentUploadService:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[2] / "data" / "kb_documents"
        self.root.mkdir(parents=True, exist_ok=True)

    def save_document(self, content: bytes, file_name: str, mime_type: str) -> dict:
        clean_name = Path(file_name or "document.txt").name
        ext = Path(clean_name).suffix.lower()
        if ext not in ALLOWED_DOCUMENT_EXT:
            raise ValueError("document_format_not_supported")
        if not content:
            raise ValueError("document_empty")
        if len(content) > MAX_DOCUMENT_BYTES:
            raise ValueError("document_too_large")

        safe_mime = str(mime_type or "").split(";", 1)[0].strip().lower() or "application/octet-stream"
        if safe_mime not in ALLOWED_DOCUMENT_MIME.get(ext, set()):
            raise ValueError("document_mime_not_supported")

        try:
            content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("document_encoding_not_supported") from exc

        final_name = f"{uuid4().hex}{ext}"
        path = self.root / final_name
        path.write_bytes(content)
        return {
            "file_name": clean_name,
            "file_ext": ext.removeprefix("."),
            "file_size": len(content),
            "mime_type": safe_mime,
            "storage_path": str(path.resolve()),
        }


document_upload_service = DocumentUploadService()
