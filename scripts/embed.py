"""Chunk and embed transcribed episodes into Supabase pgvector."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import argparse
from openai import OpenAI
from supabase import create_client
from src.config import settings
from src.embeddings.pipeline import run_embedding_batch

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=10, help="Number of episodes to embed")
args = parser.parse_args()

db = create_client(settings.supabase_url, settings.supabase_service_key)
openai_client = OpenAI(api_key=settings.openai_api_key)
run_embedding_batch(db, openai_client, limit=args.limit)
