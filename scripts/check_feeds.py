"""Validate all RSS feeds in the registry — check they're reachable and have audio."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.registry.podcasts import PODCASTS
from src.ingestion.crawler import crawl_feed
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Feed Check Results", show_lines=True)
table.add_column("Podcast", style="cyan")
table.add_column("Status", justify="center")
table.add_column("Episodes found", justify="right")
table.add_column("Latest episode")

for p in PODCASTS:
    try:
        eps = crawl_feed(p["rss_url"])
        latest = eps[0]["title"][:60] if eps else "—"
        table.add_row(p["name"], "[green]✓ OK[/green]", str(len(eps)), latest)
    except Exception as e:
        table.add_row(p["name"], "[red]✗ FAIL[/red]", "—", str(e)[:60])

console.print(table)
