from app.schemas.rag import ChunkResult


class FallbackChunker:
    def chunk(self, doc_id: str, text: str, size: int = 700) -> list[ChunkResult]:
        if not text:
            return []
        chunks: list[ChunkResult] = []
        i = 0
        part = 1
        while i < len(text):
            cut = text[i : i + size]
            chunks.append(
                ChunkResult(
                    chunk_id=f"{doc_id}_fb_{part:04d}",
                    text=cut,
                    token_count=max(1, len(cut) // 2),
                    section="fallback",
                )
            )
            i += size
            part += 1
        return chunks


fallback_chunker = FallbackChunker()

