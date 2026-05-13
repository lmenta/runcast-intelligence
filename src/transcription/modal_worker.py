"""Production transcription worker on Modal (serverless GPU).

Runs Whisper large-v3 on an A10G GPU. ~10x cheaper than OpenAI API at scale,
and faster for long episodes. Triggered by the daily cron via Modal's scheduler.

Usage:
    modal run src/transcription/modal_worker.py --episode-id <uuid>
    modal deploy src/transcription/modal_worker.py  # deploy as scheduled job
"""

import modal

app = modal.App("running-podcast-transcription")

# Container image with Whisper + ffmpeg
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("openai-whisper", "httpx", "supabase", "python-dotenv")
)

# Secrets — set these with: modal secret create running-podcast SUPABASE_URL=... etc.
secrets = [modal.Secret.from_name("running-podcast")]


@app.function(
    image=image,
    secrets=secrets,
    gpu="A10G",
    timeout=3600,  # 1h max per episode
    retries=2,
)
def transcribe_episode_gpu(episode_id: str) -> dict:
    """Transcribe a single episode using Whisper large-v3 on GPU."""
    import os, json, tempfile, whisper, httpx
    from pathlib import Path
    from supabase import create_client

    db = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    episode = db.table("episodes").select("*").eq("id", episode_id).single().execute().data
    db.table("episodes").update({"status": "transcribing"}).eq("id", episode_id).execute()

    model = whisper.load_model("large-v3")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        with httpx.stream("GET", episode["audio_url"], follow_redirects=True, timeout=120) as r:
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_bytes(8192):
                    f.write(chunk)

        result = model.transcribe(str(tmp_path), verbose=False)
        transcript = {
            "text": result["text"],
            "segments": [
                {"start": s["start"], "end": s["end"], "text": s["text"]}
                for s in result["segments"]
            ],
        }

        db.table("episodes").update({
            "status": "transcribed",
            "transcript": json.dumps(transcript),
        }).eq("id", episode_id).execute()

        return {"episode_id": episode_id, "words": len(result["text"].split())}

    except Exception as e:
        db.table("episodes").update({"status": "failed", "error_msg": str(e)[:500]}).eq("id", episode_id).execute()
        raise
    finally:
        tmp_path.unlink(missing_ok=True)


@app.function(
    image=image,
    secrets=secrets,
    schedule=modal.Cron("0 3 * * *"),  # 3am daily
)
def daily_transcription_job():
    """Scheduled job: transcribe all pending episodes."""
    import os
    from supabase import create_client

    db = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    pending = db.table("episodes").select("id").eq("status", "pending").limit(20).execute().data

    if not pending:
        print("No pending episodes.")
        return

    print(f"Transcribing {len(pending)} episodes on GPU...")
    for result in transcribe_episode_gpu.map([ep["id"] for ep in pending]):
        print(f"Done: {result}")
