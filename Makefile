.PHONY: install setup crawl transcribe embed dev api

install:
	python -m venv .venv && .venv/bin/pip install -q fastapi uvicorn httpx feedparser \
		supabase openai anthropic python-dotenv pydantic pydantic-settings tenacity rich

setup:
	@echo "Seeding podcasts and crawling feeds..."
	.venv/bin/python scripts/seed_podcasts.py
	.venv/bin/python scripts/crawl.py

check-feeds:
	.venv/bin/python scripts/check_feeds.py

transcribe:
	.venv/bin/python scripts/transcribe.py --limit 3

embed:
	.venv/bin/python scripts/embed.py --limit 10

search:
	@read -p "Query: " q; .venv/bin/python scripts/search_test.py "$$q"

api:
	.venv/bin/uvicorn src.api.main:app --reload --port 8000

dev:
	cd frontend && npm run dev
