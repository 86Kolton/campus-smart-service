from pydantic import BaseModel


class ChunkResult(BaseModel):
    chunk_id: str
    text: str
    token_count: int
    section: str


class RetrievedContext(BaseModel):
    chunk_id: str
    text: str
    score: float

