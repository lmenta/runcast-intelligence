"""Transcription pipeline using OpenAI Whisper API.

For production scale, see modal_worker.py which runs Whisper on GPU.
For development and small batches, this module calls the OpenAI API directly
($0.006/minute — about $0.36 for a 60-minute episode).

Large files (>24MB) are split into chunks with ffmpeg before uploading.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import httpx
from pathlib import Path
from openai import OpenAI
from rich.console import Console
from supabase import Client
from tenacity import retry, stop_after_attempt, wait_exponential

console = Console()

MAX_BYTES = 24 * 1024 * 1024  # 24MB — safely under Whisper's 25MB limit


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def download_audio(audio_url: str, dest: Path) -> None:
    with httpx.stream("GET", audio_url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=8192):
                f.write(chunk)


def split_audio(audio_path: Path, chunk_dir: Path) -> list[Path]:
    """Split audio into ~20MB chunks using ffmpeg. Returns list of chunk paths."""
    # Get duration in seconds
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())
    file_size = audio_path.stat().st_size

    # Calculate chunk duration to stay under 24MB
    chunk_secs = int((MAX_BYTES / file_size) * duration * 0.95)
    chunk_secs = max(60, min(chunk_secs, 600))  # between 1 and 10 minutes per chunk

    chunk_pattern = str(chunk_dir / "chunk_%03d.mp3")
    subprocess.run(
        ["ffmpeg", "-i", str(audio_path), "-f", "segment",
         "-segment_time", str(chunk_secs), "-c", "copy",
         "-reset_timestamps", "1", chunk_pattern, "-y"],
        capture_output=True, check=True
    )
    return sorted(chunk_dir.glob("chunk_*.mp3"))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def _transcribe_chunk(chunk_path: Path, openai_client: OpenAI, offset_secs: float = 0.0) -> dict:
    with open(chunk_path, "rb") as f:
        response = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )
    return {
        "text": response.text,
        "segments": [
            {"start": seg.start + offset_secs, "end": seg.end + offset_secs, "text": seg.text}
            for seg in (response.segments or [])
        ],
    }


def transcribe_audio(audio_path: Path, openai_client: OpenAI) -> dict:
    """Transcribe audio — splits automatically if file exceeds 24MB."""
    if audio_path.stat().st_size <= MAX_BYTES:
        return _transcribe_chunk(audio_path, openai_client)

    # Split into chunks and transcribe each, stitching timestamps
    with tempfile.TemporaryDirectory() as chunk_dir:
        chunks = split_audio(audio_path, Path(chunk_dir))
        console.print(f"    Split into {len(chunks)} chunks")

        all_text = []
        all_segments = []
        offset = 0.0

        for i, chunk in enumerate(chunks):
            console.print(f"    Chunk {i+1}/{len(chunks)}...")
            if i > 0:
                import time; time.sleep(2)  # avoid Whisper rate limit
            result = _transcribe_chunk(chunk, openai_client, offset_secs=offset)
            all_text.append(result["text"])
            all_segments.extend(result["segments"])
            # Advance offset by this chunk's last segment end time
            if result["segments"]:
                offset = result["segments"][-1]["end"]

    return {"text": " ".join(all_text), "segments": all_segments}


def transcribe_episode(db: Client, openai_client: OpenAI, episode: dict) -> bool:
    """Download and transcribe a single episode. Returns True on success."""
    episode_id = episode["id"]
    title = episode["title"][:60]
    tmp_path = None

    console.print(f"  Transcribing: [cyan]{title}[/cyan]")
    db.table("episodes").update({"status": "transcribing"}).eq("id", episode_id).execute()

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        console.print(f"    Downloading audio...")
        download_audio(episode["audio_url"], tmp_path)
        file_size_mb = tmp_path.stat().st_size / 1_048_576
        console.print(f"    Downloaded {file_size_mb:.1f} MB — transcribing...")

        result = transcribe_audio(tmp_path, openai_client)
        tmp_path.unlink(missing_ok=True)

        db.table("episodes").update({
            "status": "transcribed",
            "transcript": json.dumps({"text": result["text"], "segments": result["segments"]}),
        }).eq("id", episode_id).execute()

        console.print(f"    [green]✓ Done[/green] — {len(result['text'].split()):,} words")
        return True

    except Exception as e:
        if tmp_path:
            tmp_path.unlink(missing_ok=True)
        db.table("episodes").update({"status": "failed", "error_msg": str(e)[:500]}).eq("id", episode_id).execute()
        console.print(f"    [red]✗ Failed: {e}[/red]")
        return False


def run_transcription_batch(db: Client, openai_client: OpenAI, limit: int = 5) -> None:
    """Transcribe the next batch of pending episodes."""
    console.rule("[bold blue]Transcription Batch")

    # Reset any stuck-in-transcribing episodes from previous failed runs
    db.table("episodes").update({"status": "pending"}).eq("status", "transcribing").execute()

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
