from pathlib import Path

REPO     = Path(__file__).resolve().parents[2]
DATA     = REPO / "data"
CACHE    = REPO / "cache"
SITE     = REPO / "site"
SITE_DATA = SITE / "src" / "data"
SITE_PUB  = SITE / "public"

CHAT_TXT = DATA / "_chat.txt"
MSGS_PARQUET = DATA / "messages.parquet"

CACHE.mkdir(exist_ok=True)
SITE_DATA.mkdir(parents=True, exist_ok=True)
