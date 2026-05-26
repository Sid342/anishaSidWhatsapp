import polars as pl, json, re
from rich import print
from lib.paths import MSGS_PARQUET, CACHE
from lib.cache import stamp, fresh, mark

OUT = CACHE / "quote_candidates.jsonl"
KEYWORDS = re.compile(r"(?i)\b(love|miss|baby|bebu|beboo|cute|happy|sad|sorry|forever|promise|shaadi|marry|kiss|cuddle)\b")
LAUGH    = re.compile(r"(😂|🥹|😭|haha|lol|lmao)")
EMPH     = re.compile(r"(.)\1{3,}")


def _is_candidate(text: str) -> bool:
    L = len(text)
    if L < 20 or L > 280: return False
    if text.startswith("http"): return False
    score = 0
    if KEYWORDS.search(text): score += 2
    if LAUGH.search(text):    score += 1
    if EMPH.search(text):     score += 1
    if text.isupper() and L > 6: score += 1
    if text.count("\n") >= 2: score += 1
    return score >= 1


def run(force: bool = False):
    s = stamp("s3", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]"); return
    df = pl.read_parquet(MSGS_PARQUET).filter(pl.col("is_media") == False)
    rows = df.to_dicts()
    cands = [r for r in rows if _is_candidate(r["text"])]
    with OUT.open("w") as f:
        for r in cands:
            f.write(json.dumps({"ts": str(r["ts"]), "sender": r["sender"], "text": r["text"]}) + "\n")
    mark(s)
    print(f"  [green]{len(cands):,} candidates from {len(rows):,} msgs[/green]")
