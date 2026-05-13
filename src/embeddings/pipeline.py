"""Embedding pipeline: chunk transcripts → embed → store in Supabase pgvector."""

from __future__ import annotations

from openai import OpenAI
from rich.console import Console
from supabase import Client
from tenacity import retry, stop_after_attempt, wait_exponential

from src.embeddings.chunker import chunk_transcript

console = Console()

EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs per request


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
def embed_texts(texts: list[str], openai_client: OpenAI) -> list[list[float]]:
    """Embed a batch of texts. Returns list of embedding vectors."""
    response = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def embed_episode(db: Client, openai_client: OpenAI, episode: dict) -> bool:
    """Chunk, embed, and store a single episode's transcript. Returns True on success."""
    episode_id = episode["id"]
    title = episode["title"][:60]

    if not episode.get("transcript"):
        console.print(f"  [yellow]Skipping {title} — no transcript[/yellow]")
        return False

    console.print(f"  Embedding: [cyan]{title}[/cyan]")
    db.table("episodes").update({"status": "embedding"}).eq("id", episode_id).execute()

    try:
        chunks = chunk_transcript(episode["transcript"])
        if not chunks:
            raise ValueError("No chunks produced from transcript")

        console.print(f"    {len(chunks)} chunks — generating embeddings...")

        # Batch embed
        all_embeddings: list[list[float]] = []
        texts = [c["content"] for c in chunks]
        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i: i + EMBED_BATCH_SIZE]
            all_embeddings.extend(embed_texts(batch, openai_client))

        # Build rows for bulk insert
        rows = [
            {
                "episode_id": episode_id,
                "content": chunk["content"],
                "start_secs": chunk["start_secs"],
                "end_secs": chunk["end_secs"],
                "chunk_index": chunk["chunk_index"],
                "embedding": embedding,
            }
            for chunk, embedding in zip(chunks, all_embeddings)
        ]

        # Insert in batches of 50 (Supabase row size limit)
        for i in range(0, len(rows), 50):
            db.table("chunks").insert(rows[i: i + 50]).execute()

        db.table("episodes").update({"status": "ready"}).eq("id", episode_id).execute()
        console.print(f"    [green]✓ {len(chunks)} chunks stored[/green]")
        return True

    except Exception as e:
        db.table("episodes").update({"status": "failed", "error_msg": str(e)[:500]}).eq("id", episode_id).execute()
        console.print(f"    [red]✗ Failed: {e}[/red]")
        return False


def run_embedding_batch(db: Client, openai_client: OpenAI, limit: int = 10) -> None:
    """Embed the next batch of transcribed episodes."""
    console.rule("[bold blue]Embedding Batch")

    result = db.table("episodes").select(
        "id, title, transcript"
    ).eq("status", "transcribed").limit(limit).execute()

    episodes = result.data
    if not episodes:
        console.print("[yellow]No transcribed episodes to embed.[/yellow]")
        return

    console.print(f"Embedding {len(episodes)} episodes...")
    ok = sum(embed_episode(db, openai_client, ep) for ep in episodes)
    console.rule(f"[bold green]{ok}/{len(episodes)} episodes embedded and ready to search")
