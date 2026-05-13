"""FastAPI application — search, browse, and podcast directory endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from supabase import create_client

from src.api.models import (
    EpisodeOut, PodcastOut, SearchRequest, SearchResponse,
)
from src.api.search import search as run_search, OPENROUTER_BASE_URL
from src.config import settings

app = FastAPI(
    title="Running Podcast Intelligence",
    description="Semantic search across hundreds of running podcast episodes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialise clients once at startup
db = create_client(settings.supabase_url, settings.supabase_service_key)
openai_client = OpenAI(api_key=settings.openai_api_key)
llm_client = OpenAI(api_key=settings.openrouter_api_key, base_url=OPENROUTER_BASE_URL)


# ── Search ───────────────────────────────────────────────────────────────────

@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    """Semantic search across all indexed podcast transcripts."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return run_search(request, db, openai_client, llm_client)


# ── Podcasts ─────────────────────────────────────────────────────────────────

@app.get("/api/podcasts", response_model=list[PodcastOut])
def list_podcasts() -> list[PodcastOut]:
    """Return all active podcasts in the registry."""
    result = db.table("podcasts").select("*").eq("active", True).order("name").execute()
    return [PodcastOut(**row) for row in result.data]


@app.get("/api/podcasts/{podcast_id}", response_model=PodcastOut)
def get_podcast(podcast_id: str) -> PodcastOut:
    result = db.table("podcasts").select("*").eq("id", podcast_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return PodcastOut(**result.data)


# ── Episodes ──────────────────────────────────────────────────────────────────

@app.get("/api/episodes", response_model=list[EpisodeOut])
def list_episodes(
    podcast_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
) -> list[EpisodeOut]:
    """Browse episodes with optional podcast or status filter."""
    q = db.table("episodes").select(
        "id, podcast_id, title, published_at, duration_secs, status, podcasts(name)"
    )
    if podcast_id:
        q = q.eq("podcast_id", podcast_id)
    if status:
        q = q.eq("status", status)
    result = q.order("published_at", desc=True).range(offset, offset + limit - 1).execute()

    episodes = []
    for row in result.data:
        podcast_name = (row.pop("podcasts", None) or {}).get("name")
        episodes.append(EpisodeOut(**row, podcast_name=podcast_name))
    return episodes


@app.get("/api/episodes/{episode_id}", response_model=EpisodeOut)
def get_episode(episode_id: str) -> EpisodeOut:
    result = db.table("episodes").select(
        "id, podcast_id, title, published_at, duration_secs, status, podcasts(name)"
    ).eq("id", episode_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Episode not found")
    row = result.data
    podcast_name = (row.pop("podcasts", None) or {}).get("name")
    return EpisodeOut(**row, podcast_name=podcast_name)


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def stats() -> dict:
    """Quick stats on the index size."""
    podcasts = db.table("podcasts").select("id", count="exact").eq("active", True).execute()
    ready = db.table("episodes").select("id", count="exact").eq("status", "ready").execute()
    chunks = db.table("chunks").select("id", count="exact").execute()
    return {
        "podcasts": podcasts.count,
        "episodes_indexed": ready.count,
        "chunks": chunks.count,
    }


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
