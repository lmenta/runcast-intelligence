"""Search logic: embed query → vector search → LLM RAG answer."""

from __future__ import annotations

from openai import OpenAI
from supabase import Client

from src.api.models import SearchRequest, SearchResponse, SourceChunk

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
RAG_MODEL = "anthropic/claude-haiku-4-5"

RAG_SYSTEM_PROMPT = """You are an expert running coach assistant with deep knowledge from hundreds of podcast episodes.
Answer questions using ONLY the transcript excerpts provided. Be specific and cite the source episodes.
If the excerpts don't contain enough to answer well, say so honestly — don't invent information.
Write in a clear, direct style — like a knowledgeable coach giving practical advice."""


def _format_sources_for_prompt(sources: list[SourceChunk]) -> str:
    lines = []
    for i, s in enumerate(sources, 1):
        ts = f" (~{s.timestamp_str})" if s.timestamp_str else ""
        lines.append(f"[{i}] {s.podcast_name} — \"{s.episode_title}\"{ts}\n{s.excerpt}\n")
    return "\n".join(lines)


def search(
    request: SearchRequest,
    db: Client,
    openai_client: OpenAI,
    llm_client: OpenAI,
) -> SearchResponse:
    # 1. Embed the query
    query_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=request.query,
    ).data[0].embedding

    # 2. Vector similarity search
    rows = db.rpc("search_chunks", {
        "query_embedding": query_embedding,
        "match_count": request.limit,
        "min_similarity": request.min_similarity,
    }).execute().data or []

    if not rows:
        return SearchResponse(
            answer="I couldn't find relevant content for that question. Try rephrasing or asking something more specific.",
            sources=[],
            query=request.query,
        )

    sources = [
        SourceChunk(
            chunk_id=row["chunk_id"],
            episode_id=row["episode_id"],
            podcast_name=row["podcast_name"],
            episode_title=row["episode_title"],
            published_at=row.get("published_at"),
            excerpt=row["content"],
            start_secs=row.get("start_secs"),
            similarity=row["similarity"],
        )
        for row in rows
    ]

    # 3. RAG — call LLM via OpenRouter
    context = _format_sources_for_prompt(sources)
    response = llm_client.chat.completions.create(
        model=RAG_MODEL,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {request.query}\n\nTranscript excerpts:\n{context}"},
        ],
    )

    return SearchResponse(
        answer=response.choices[0].message.content,
        sources=sources,
        query=request.query,
    )
