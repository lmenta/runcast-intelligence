"""Split transcripts into overlapping chunks, preserving timestamps."""

from __future__ import annotations
import json


CHUNK_SIZE = 500      # target tokens per chunk
CHUNK_OVERLAP = 50   # overlap between chunks


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def chunk_transcript(transcript_json: str) -> list[dict]:
    """
    Split a transcript into overlapping chunks with timestamp metadata.

    Returns a list of:
        {"content": str, "start_secs": float, "end_secs": float, "chunk_index": int}
    """
    data = json.loads(transcript_json)
    segments = data.get("segments", [])

    # Fall back to splitting plain text if no segments
    if not segments:
        return _chunk_plain_text(data.get("text", ""))

    chunks = []
    current_text = ""
    current_start = None
    current_end = None
    chunk_index = 0
    overlap_buffer = ""

    for seg in segments:
        seg_text = seg["text"].strip()
        if not seg_text:
            continue

        if current_start is None:
            current_start = seg.get("start", 0)

        current_text += " " + seg_text
        current_end = seg.get("end", 0)

        if estimate_tokens(current_text) >= CHUNK_SIZE:
            chunks.append({
                "content": current_text.strip(),
                "start_secs": current_start,
                "end_secs": current_end,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

            # Keep last N tokens as overlap for the next chunk
            words = current_text.split()
            overlap_words = words[-CHUNK_OVERLAP:] if len(words) > CHUNK_OVERLAP else words
            overlap_buffer = " ".join(overlap_words)
            current_text = overlap_buffer
            current_start = current_end  # approximate

    # Flush remaining text
    if current_text.strip():
        chunks.append({
            "content": current_text.strip(),
            "start_secs": current_start or 0,
            "end_secs": current_end or 0,
            "chunk_index": chunk_index,
        })

    return chunks


def _chunk_plain_text(text: str) -> list[dict]:
    """Fallback chunker for transcripts with no segment timestamps."""
    words = text.split()
    chunks = []
    i = 0
    chunk_index = 0
    while i < len(words):
        chunk_words = words[i: i + CHUNK_SIZE]
        chunks.append({
            "content": " ".join(chunk_words),
            "start_secs": None,
            "end_secs": None,
            "chunk_index": chunk_index,
        })
        i += CHUNK_SIZE - CHUNK_OVERLAP
        chunk_index += 1
    return chunks
