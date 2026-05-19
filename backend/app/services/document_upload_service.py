from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.rag.parser.document_parser import document_parser


MAX_DOCUMENT_BYTES = 10 * 1024 * 1024
ALLOWED_DOCUMENT_EXT = {
    ".txt",
    ".md",
    ".csv",
    ".tsv",
    ".json",
    ".log",
    ".yaml",
    ".yml",
    ".xml",
    ".rtf",
    ".doc",
    ".docx",
    ".pdf",
    ".html",
    ".htm",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}
ALLOWED_DOCUMENT_MIME = {
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
    ".csv": {"text/csv", "text/plain", "application/vnd.ms-excel", "application/octet-stream"},
    ".tsv": {"text/tab-separated-values", "text/plain", "application/octet-stream"},
    ".json": {"application/json", "text/json", "text/plain", "application/octet-stream"},
    ".log": {"text/plain", "application/octet-stream"},
    ".yaml": {"application/yaml", "application/x-yaml", "text/yaml", "text/plain", "application/octet-stream"},
    ".yml": {"application/yaml", "application/x-yaml", "text/yaml", "text/plain", "application/octet-stream"},
    ".xml": {"application/xml", "text/xml", "text/plain", "application/octet-stream"},
    ".rtf": {"application/rtf", "text/rtf", "application/octet-stream"},
    ".doc": {"application/msword", "application/octet-stream", "application/x-ole-storage"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
        "application/octet-stream",
    },
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".html": {"text/html", "application/xhtml+xml", "application/octet-stream"},
    ".htm": {"text/html", "application/xhtml+xml", "application/octet-stream"},
    ".xls": {"application/vnd.ms-excel", "application/octet-stream"},
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/zip",
        "application/octet-stream",
    },
    ".ppt": {"application/vnd.ms-powerpoint", "application/octet-stream"},
    ".pptx": {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/zip",
        "application/octet-stream",
    },
    ".odt": {"application/vnd.oasis.opendocument.text", "application/zip", "application/octet-stream"},
    ".ods": {"application/vnd.oasis.opendocument.spreadsheet", "application/zip", "application/octet-stream"},
    ".odp": {"application/vnd.oasis.opendocument.presentation", "application/zip", "application/octet-stream"},
    ".png": {"image/png", "application/octet-stream"},
    ".jpg": {"image/jpeg", "image/jpg", "application/octet-stream"},
    ".jpeg": {"image/jpeg", "image/jpg", "application/octet-stream"},
    ".webp": {"image/webp", "application/octet-stream"},
    ".bmp": {"image/bmp", "application/octet-stream"},
    ".tif": {"image/tiff", "application/octet-stream"},
    ".tiff": {"image/tiff", "application/octet-stream"},
}
NORMALIZED_DOCUMENT_EXT = {
    ".doc",
    ".docx",
    ".pdf",
    ".html",
    ".htm",
    ".xml",
    ".rtf",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
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

        parsed_text = document_parser.parse_bytes(content, ext.removeprefix("."))
        if not parsed_text.strip():
            raise ValueError("document_empty")

        storage_ext = ".md" if ext in NORMALIZED_DOCUMENT_EXT else ext
        storage_mime = "text/markdown" if ext in NORMALIZED_DOCUMENT_EXT else safe_mime
        if ext in NORMALIZED_DOCUMENT_EXT:
            stem = Path(clean_name).stem or "document"
            stored_content = f"# {stem}\n\n{parsed_text.strip()}\n".encode("utf-8")
        else:
            stored_content = parsed_text.encode("utf-8")

        final_name = f"{uuid4().hex}{storage_ext}"
        path = self.root / final_name
        path.write_bytes(stored_content)
        return {
            "file_name": clean_name,
            "file_ext": storage_ext.removeprefix("."),
            "file_size": len(stored_content),
            "mime_type": storage_mime,
            "storage_path": str(path.resolve()),
            "ingest_content": stored_content,
            "original_file_ext": ext.removeprefix("."),
            "original_file_size": len(content),
        }


document_upload_service = DocumentUploadService()
