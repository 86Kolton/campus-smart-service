import re

from app.rag.chunker.emm_chunker import emm_chunker
from app.rag.chunker.fallback_chunker import fallback_chunker
from app.rag.parser.document_parser import document_parser
from app.services.document_service import document_service
from app.services.embedding_service import embedding_service
from app.services.qdrant_service import qdrant_service
from app.services.store import store


class IngestService:
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

    def ingest_document(self, kb_id: int, document_id: int, file_ext: str, content: bytes) -> int:
        document_service.update_status(document_id, "parsing")
        text = document_parser.parse_bytes(content, file_ext=file_ext)
        if not text.strip():
            document_service.update_status(document_id, "failed", "Document parsing returned empty text")
            return 0

        document_service.update_status(document_id, "chunking")
        doc_ref = f"kb{kb_id}_doc{document_id}"
        chunks = emm_chunker.chunk(doc_ref, text)
        if not chunks:
            chunks = fallback_chunker.chunk(doc_ref, text)
        if not chunks:
            document_service.update_status(document_id, "failed", "Chunking returned empty chunks")
            return 0

        document_service.update_status(document_id, "embedding")
        rows = []
        source_meta = self._resolve_source_meta(text, kb_id)
        for idx, chunk in enumerate(chunks, start=1):
            rows.append(
                {
                    "id": int(f"{kb_id}{document_id}{idx}"),
                    "vector": embedding_service.embed(chunk.text),
                    "payload": {
                        "chunk_id": chunk.chunk_id,
                        "kb_id": kb_id,
                        "document_id": document_id,
                        "text": chunk.text,
                        "token_count": chunk.token_count,
                        "source_type": source_meta["source_type"],
                        "jump_url": source_meta["jump_url"],
                    },
                }
            )

        qdrant_service.upsert_chunks(rows)
        store.chunks.setdefault(kb_id, [])
        store.chunks[kb_id].extend(
            [
                {
                    "chunk_id": item["payload"]["chunk_id"],
                    "text": item["payload"]["text"],
                    "source_type": item["payload"].get("source_type", "kb"),
                    "jump_url": item["payload"].get("jump_url", ""),
                }
                for item in rows
            ]
        )
        document_service.set_chunk_count(document_id, len(chunks))
        document_service.update_status(document_id, "indexed")
        return len(chunks)


ingest_service = IngestService()
