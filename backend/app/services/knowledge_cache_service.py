from __future__ import annotations

from pathlib import Path
import re

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeDocument
from app.rag.chunker.emm_chunker import emm_chunker
from app.rag.chunker.fallback_chunker import fallback_chunker
from app.rag.parser.document_parser import document_parser
from app.services.store import store


class KnowledgeCacheService:
    _SOURCE_URL_RE = re.compile(r"https?://\S+")

    def _resolve_source_meta(self, text: str, kb_id: int) -> dict:
        match = self._SOURCE_URL_RE.search(str(text or ""))
        jump_url = ""
        if match:
            jump_url = match.group(0).rstrip('.,;)]}>"')
        else:
            jump_url = f"/kb/{kb_id}"

        source_type = "feed" if "#post=p-" in jump_url else "document"
        return {"jump_url": jump_url, "source_type": source_type}

    def rebuild_chunks(self) -> dict[str, int]:
        next_chunks: dict[int, list[dict]] = {}
        docs_loaded = 0
        chunks_loaded = 0

        with SessionLocal() as db:
            docs = db.execute(
                select(KnowledgeDocument)
                .where(KnowledgeDocument.status == "indexed")
                .order_by(KnowledgeDocument.kb_id.asc(), KnowledgeDocument.id.asc())
            ).scalars().all()

        for doc in docs:
            storage_path = Path(str(doc.storage_path or "").strip())
            if not storage_path.exists() or not storage_path.is_file():
                continue

            try:
                content = storage_path.read_bytes()
                text = document_parser.parse_bytes(content, file_ext=str(doc.file_ext or "txt"))
            except Exception:
                continue

            if not text.strip():
                continue

            doc_ref = f"kb{int(doc.kb_id)}_doc{int(doc.id)}"
            chunks = emm_chunker.chunk(doc_ref, text) or fallback_chunker.chunk(doc_ref, text)
            if not chunks:
                continue

            bucket = next_chunks.setdefault(int(doc.kb_id), [])
            source_meta = self._resolve_source_meta(text, int(doc.kb_id))
            bucket.extend(
                [
                    {
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "source_type": source_meta["source_type"],
                        "jump_url": source_meta["jump_url"],
                    }
                    for chunk in chunks
                ]
            )
            docs_loaded += 1
            chunks_loaded += len(chunks)

        store.chunks = next_chunks
        return {"documents": docs_loaded, "chunks": chunks_loaded}


knowledge_cache_service = KnowledgeCacheService()
