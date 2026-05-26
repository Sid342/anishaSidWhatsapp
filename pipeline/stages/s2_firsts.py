import json, polars as pl
from rich import print
from lib.paths import MSGS_PARQUET, SITE_DATA
from lib.cache import stamp, fresh, mark

OUT = SITE_DATA / "firsts.json"

PHRASES = [
    "i love you", "love you", "miss you", "missing you",
    "baby", "bebu", "beboo",
    "shaadi", "marry", "marriage", "ring", "engagement",
    "ily", "i miss u", "miss u",
    "promise", "forever",
    "good night", "good morning",
    "cute", "beautiful", "handsome",
    "first kiss", "kiss",
]

def _context(df: pl.DataFrame, idx: int, window: int = 3) -> list[dict]:
    lo = max(0, idx - window); hi = min(df.height, idx + window + 1)
    rows = df.slice(lo, hi - lo).to_dicts()
    return [{"ts": str(r["ts"]), "sender": r["sender"], "text": r["text"]} for r in rows]

def run(force: bool = False):
    s = stamp("s2", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]")
        return
    df = pl.read_parquet(MSGS_PARQUET).sort("ts").with_row_index("idx")
    found: list[dict] = []
    for phrase in PHRASES:
        for sender in ["Sid", "Anisha"]:
            sub = df.filter(
                (pl.col("sender") == sender) &
                pl.col("text").str.to_lowercase().str.contains(phrase, literal=True)
            ).head(1)
            if sub.height == 0: continue
            row = sub.to_dicts()[0]
            found.append({
                "phrase": phrase, "by": sender,
                "ts": str(row["ts"]),
                "text": row["text"],
                "context": _context(df, int(row["idx"])),
            })
    found.sort(key=lambda r: r["ts"])
    OUT.write_text(json.dumps(found, indent=2))
    mark(s)
    print(f"  [green]{len(found)} firsts written[/green]")
