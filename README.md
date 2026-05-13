# RunCast Intelligence

Search across thousands of hours of running podcast transcripts. Ask anything — get answers with episode sources and timestamps.

**Stack:** Python · FastAPI · Next.js · Supabase (pgvector) · OpenAI Whisper · Railway · Vercel

---

## Setup

### 1. Prerequisites

- Python 3.11+
- Node 20+
- [Supabase](https://supabase.com) account (free tier works)
- [OpenAI](https://platform.openai.com) API key
- [Anthropic](https://console.anthropic.com) API key

### 2. Clone and install

```bash
git clone https://github.com/lmenta/runcast-intelligence
cd runcast-intelligence
make install
```

### 3. Environment variables

```bash
cp .env.example .env
# Fill in your keys
```

### 4. Supabase setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Open the SQL Editor and run both migration files in order:
   - `supabase/migrations/001_initial_schema.sql`
   - `supabase/migrations/002_add_transcript.sql`
3. Copy your **Project URL** and **service_role** key into `.env`

### 5. Seed and crawl

```bash
make setup        # seeds podcasts + crawls all RSS feeds
make check-feeds  # verify all feeds are reachable
```

### 6. Transcribe and embed

```bash
make transcribe   # transcribes 3 episodes (~$0.15)
make embed        # chunks + embeds transcribed episodes
```

### 7. Test search

```bash
make search
# Query: how do elites taper for a marathon?
```

---

## Running locally

```bash
make api   # FastAPI on http://localhost:8000
make dev   # Next.js on http://localhost:3000
```

---

## Deployment

### Backend → Railway

1. Connect this repo to [Railway](https://railway.app)
2. Add environment variables from `.env`
3. Railway will pick up `railway.toml` automatically

### Frontend → Vercel

1. Connect `frontend/` to [Vercel](https://vercel.com)
2. Set `NEXT_PUBLIC_API_URL` to your Railway backend URL
3. Set `NEXT_PUBLIC_USE_MOCK=false`

### Transcription at scale → Modal

```bash
pip install modal
modal secret create runcast SUPABASE_URL=... SUPABASE_SERVICE_KEY=... OPENAI_API_KEY=...
modal deploy src/transcription/modal_worker.py
```

This deploys a daily cron that transcribes new episodes on serverless GPU.

---

## Architecture

```
RSS Feeds ──► Crawler ──► Supabase (episodes)
                      └──► Modal Whisper ──► Transcripts
                                        └──► Embeddings ──► pgvector
                                                       └──► FastAPI + LLM ──► Next.js
```

## Cost estimate (low traffic)

| Service | Cost |
|---------|------|
| Supabase | Free tier |
| Railway | ~$5/month |
| Vercel | Free |
| Modal (transcription) | ~$0.05/hour of audio |
| OpenAI (embeddings) | ~$0.02/episode |
| LLM (search) | ~$0.001/query |
