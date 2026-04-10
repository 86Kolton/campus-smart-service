from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4


MAX_IMAGE_BYTES = 1 * 1024 * 1024
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_IMAGE_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


class UploadService:
    def __init__(self) -> None:
        self.root = Path(__file__).resolve().parents[2] / "data" / "uploads"
        self.root.mkdir(parents=True, exist_ok=True)

    def save_image(self, content: bytes, file_name: str, mime_type: str, scope: str) -> dict:
        clean_name = Path(file_name or "upload").name
        ext = Path(clean_name).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXT:
            raise ValueError("image_format_not_supported")
        if mime_type and mime_type not in ALLOWED_IMAGE_MIME:
            raise ValueError("image_mime_not_supported")
        if len(content) > MAX_IMAGE_BYTES:
            raise ValueError("image_too_large")

        folder = self.root / scope
        folder.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        final_name = f"{ts}_{uuid4().hex[:10]}{ext}"
        path = folder / final_name
        path.write_bytes(content)

        return {
            "file_name": clean_name,
            "file_size": len(content),
            "mime_type": mime_type or "application/octet-stream",
            "storage_path": str(path),
            "public_url": f"/uploads/{scope}/{final_name}",
        }


upload_service = UploadService()
