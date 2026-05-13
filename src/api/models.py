from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_similarity: float = 0.4


class SourceChunk(BaseModel):
    chunk_id: str
    episode_id: str
    podcast_name: str
    episode_title: str
    published_at: Optional[datetime]
    excerpt: str
    start_secs: Optional[float]
    similarity: float

    @property
    def timestamp_str(self) -> Optional[str]:
        if self.start_secs is None:
            return None
        m, s = divmod(int(self.start_secs), 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


class SearchResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    query: str


class PodcastOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    cover_image: Optional[str]
    website: Optional[str]


class EpisodeOut(BaseModel):
    id: str
    podcast_id: str
    podcast_name: Optional[str] = None
    title: str
    published_at: Optional[datetime]
    duration_secs: Optional[int]
    status: str
