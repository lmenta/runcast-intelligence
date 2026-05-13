"""Test the search pipeline from the CLI before the frontend exists."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import argparse, json
import anthropic
from openai import OpenAI
from supabase import create_client
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.config import settings
from src.api.models import SearchRequest
from src.api.search import search

console = Console()

parser = argparse.ArgumentParser()
parser.add_argument("query", help="Search query")
parser.add_argument("--limit", type=int, default=8)
args = parser.parse_args()

db = create_client(settings.supabase_url, settings.supabase_service_key)
openai_client = OpenAI(api_key=settings.openai_api_key)
anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

console.rule(f"[bold blue]Search: {args.query}")
result = search(SearchRequest(query=args.query, limit=args.limit), db, openai_client, anthropic_client)

console.print(Panel(result.answer, title="Answer", border_style="green"))

console.print(f"\n[bold]Sources ({len(result.sources)}):[/bold]")
for i, s in enumerate(result.sources, 1):
    ts = f" @{s.timestamp_str}" if s.timestamp_str else ""
    console.print(f"  [{i}] [cyan]{s.podcast_name}[/cyan] — {s.episode_title[:50]}{ts}")
    console.print(f"      similarity={s.similarity:.3f}")
