import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env in parent project folder
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

DISCOGS_TOKEN = os.getenv("DISCOGS_TOKEN")
if not DISCOGS_TOKEN:
    raise RuntimeError("Missing DISCOGS_TOKEN in parent .env")