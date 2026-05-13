"""RSS crawler — fetches and parses podcast feeds, inserts new episodes."""

from __future__ import annotations

import feedparser
import httpx
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from rich.console import Console
from supabase import Client

console = Console()


def parse_duration(duration_str: str | None) -> int | None:
    """Parse iTunes duration string (HH:MM:SS or seconds) to seconds."""
    if not duration_str:
        return None
    parts = duration_str.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])
    except (ValueError, IndexError):
        return None


def find_audio_url(entry) -> str | None:
    """Extract the MP3/audio URL from a feed entry's enclosures."""
    for enclosure in getattr(entry, "enclosures", []):
        if "audio" in enclosure.get("type", ""):
            return enclosure.get("href") or enclosure.get("url")
    return None


def parse_published_at(entry) -> datetime | None:
    try:
        if hasattr(entry, "published"):
            return parsedate_to_datetime(entry.published).astimezone(timezone.utc)
    except Exception:
        pass
    return None


def crawl_feed(rss_url: str) -> list[dict]:
    """Parse an RSS feed and return a list of episode dicts."""
    response = httpx.get(
        rss_url,
        follow_redirects=True,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0 (compatible; RunningPodcastBot/1.0)"},
    )
    response.raise_for_status()
    feed = feedparser.parse(response.text)
    episodes = []
    for entry in feed.entries:
        audio_url = find_audio_url(entry)
        if not audio_url:
            continue
        episodes.append({
            "guid": getattr(entry, "id", entry.get("link", "")),
            "title": getattr(entry, "title", "Untitled"),
            "description": getattr(entry, "summary", None),
            "published_at": parse_published_at(entry),
            "duration_secs": parse_duration(
                entry.get("itunes_duration") or
                getattr(entry, "itunes_duration", None)
            ),
            "audio_url": audio_url,
            "episode_number": getattr(entry, "itunes_episode", None),
            "season_number": getattr(entry, "itunes_season", None),
        })
    return episodes


def sync_podcast(db: Client, podcast_id: str, rss_url: str, name: str) -> int:
    """Crawl a feed and insert any new episodes. Returns count of new episodes."""
    console.print(f"  Crawling [cyan]{name}[/cyan]...")
    try:
        episodes = crawl_feed(rss_url)
    except Exception as e:
        console.print(f"  [red]Failed to parse feed: {e}[/red]")
        return 0

    if not episodes:
        console.print(f"  [yellow]No audio episodes found[/yellow]")
        return 0

    new_count = 0
    for ep in episodes:
        ep["podcast_id"] = podcast_id
        if ep.get("published_at"):
            ep["published_at"] = ep["published_at"].isoformat()
        try:
            db.table("episodes").insert(ep).execute()
            new_count += 1
        except Exception:
            # Duplicate guid — already indexed, skip silently
            pass

    console.print(f"  [green]+{new_count} new episodes[/green] ({len(episodes)} total in feed)")
    return new_count


def seed_podcasts(db: Client, podcasts: list[dict]) -> None:
    """Insert podcasts into the registry, skip if already exists."""
    for podcast in podcasts:
        try:
            db.table("podcasts").insert(podcast).execute()
            console.print(f"[green]✓[/green] Seeded: {podcast['name']}")
        except Exception:
            console.print(f"[yellow]–[/yellow] Already exists: {podcast['name']}")


def run_crawl(db: Client) -> None:
    """Main crawl job — called by cron or manually."""
    console.rule("[bold blue]Running Podcast Intelligence — RSS Crawl")

    result = db.table("podcasts").select("id, name, rss_url").eq("active", True).execute()
    podcasts = result.data

    if not podcasts:
        console.print("[yellow]No active podcasts in registry. Run seed first.[/yellow]")
        return

    total_new = 0
    for podcast in podcasts:
        total_new += sync_podcast(db, podcast["id"], podcast["rss_url"], podcast["name"])

    console.rule(f"[bold green]Done — {total_new} new episodes queued for transcription")
