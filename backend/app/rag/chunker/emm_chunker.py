from app.schemas.rag import ChunkResult


class EMMChunker:
    def chunk(self, doc_id: str, text: str, max_chars: int = 900, overlap_chars: int = 120) -> list[ChunkResult]:
        # Placeholder "semantic" chunker: paragraph-first split with overlap fallback.
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        chunks: list[ChunkResult] = []
        buf = ""
        idx = 1
        for para in paragraphs:
            if len(buf) + len(para) + 1 <= max_chars:
                buf = f"{buf}\n{para}".strip()
                continue
            if buf:
                chunks.append(
                    ChunkResult(
                        chunk_id=f"{doc_id}_{idx:04d}",
                        text=buf,
                        token_count=max(1, len(buf) // 2),
                        section="auto",
                    )
                )
                idx += 1
                tail = buf[-overlap_chars:] if overlap_chars > 0 else ""
                buf = f"{tail}\n{para}".strip()
            else:
                chunks.append(
                    ChunkResult(
                        chunk_id=f"{doc_id}_{idx:04d}",
                        text=para[:max_chars],
                        token_count=max(1, len(para[:max_chars]) // 2),
                        section="auto",
                    )
                )
                idx += 1
        if buf:
            chunks.append(
                ChunkResult(
                    chunk_id=f"{doc_id}_{idx:04d}",
                    text=buf,
                    token_count=max(1, len(buf) // 2),
                    section="auto",
                )
            )
        return chunks


emm_chunker = EMMChunker()

