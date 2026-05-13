"""Seed the podcast registry into Supabase."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
from src.config import settings
from src.registry.podcasts import PODCASTS
from src.ingestion.crawler import seed_podcasts

db = create_client(settings.supabase_url, settings.supabase_service_key)
seed_podcasts(db, PODCASTS)
