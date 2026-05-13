"""Transcribe pending episodes using OpenAI Whisper API."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import argparse
from openai import OpenAI
from supabase import create_client
from src.config import settings
from src.transcription.whisper import run_transcription_batch

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=3, help="Number of episodes to transcribe")
args = parser.parse_args()

db = create_client(settings.supabase_url, settings.supabase_service_key)
openai_client = OpenAI(api_key=settings.openai_api_key)
run_transcription_batch(db, openai_client, limit=args.limit)
