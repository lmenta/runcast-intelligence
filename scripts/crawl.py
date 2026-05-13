"""Run the RSS crawler manually or via cron."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
from src.config import settings
from src.ingestion.crawler import run_crawl

db = create_client(settings.supabase_url, settings.supabase_service_key)
run_crawl(db)
