"""Transcription pipeline using OpenAI Whisper API.

For production scale, see modal_worker.py which runs Whisper on GPU.
For development and small batches, this module calls the OpenAI API directly
($0.006/minute — about $0.36 for a 60-minute episode).
"""

from __future__ import annotations

import tempfile
import httpx
from pathlib import Path
from openai import OpenAI
from rich.console import Console
from supabase import Client
from tenacity import retry, stop_after_attempt, wait_exponential

console = Console()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def download_audio(audio_url: str, dest: Path) -> None:
    """Download an audio file to a local path."""
    with httpx.stream("GET", audio_url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=8192):
                f.write(chunk)


def transcribe_audio(audio_path: Path, openai_client: OpenAI) -> dict:
    """Send audio to OpenAI Whisper API and return transcript with segments."""
    with open(audio_path, "rb") as audio_file:
        response = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",  # includes word-level timestamps
            timestamp_granularities=["segment"],
        )
    return {
        "text": response.text,
        "segments": [
            {
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
            }
            for seg in (response.segments or [])
        ],
    }


def transcribe_episode(db: Client, openai_client: OpenAI, episode: dict) -> bool:
    """Download and transcribe a single episode. Returns True on success."""
    episode_id = episode["id"]
    title = episode["title"][:60]

    console.print(f"  Transcribing: [cyan]{title}[/cyan]")

    # Mark as in-progress
    db.table("episodes").update({"status": "transcribing"}).eq("id", episode_id).execute()

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        console.print(f"    Downloading audio...")
        download_audio(episode["audio_url"], tmp_path)
        file_size_mb = tmp_path.stat().st_size / 1_048_576
        console.print(f"    Downloaded {file_size_mb:.1f} MB — sending to Whisper...")

        result = transcribe_audio(tmp_path, openai_client)
        tmp_path.unlink(missing_ok=True)

        import json
        db.table("episodes").update({
            "status": "transcribed",
            "transcript": json.dumps({
                "text": result["text"],
                "segments": result["segments"],
            }),
        }).eq("id", episode_id).execute()

        word_count = len(result["text"].split())
        console.print(f"    [green]✓ Done[/green] — {word_count:,} words transcribed")
        return True

    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        db.table("episodes").update({"status": "failed", "error_msg": str(e)[:500]}).eq("id", episode_id).execute()
        console.print(f"    [red]✗ Failed: {e}[/red]")
        return False


def run_transcription_batch(db: Client, openai_client: OpenAI, limit: int = 5) -> None:
    """Transcribe the next batch of pending episodes."""
    console.rule("[bold blue]Transcription Batch")

    result = db.table("episodes").select(
        "id, title, audio_url, podcast_id"
    ).eq("status", "pending").order("published_at", desc=True).limit(limit).execute()

    episodes = result.data
    if not episodes:
        console.print("[yellow]No pending episodes to transcribe.[/yellow]")
        return

    console.print(f"Transcribing {len(episodes)} episodes...")
    ok = sum(transcribe_episode(db, openai_client, ep) for ep in episodes)
    console.rule(f"[bold green]{ok}/{len(episodes)} episodes transcribed successfully")
