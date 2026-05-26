import polars as pl
from rich import print
from transformers import pipeline
from lib.paths import MSGS_PARQUET, CACHE
from lib.cache import stamp, fresh, mark

OUT = CACHE / "sentiment.parquet"
MAX_ROWS = 50_000


def run(force: bool = False):
    s = stamp("s_nlp", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]"); return
    df = pl.read_parquet(MSGS_PARQUET).filter(
        (pl.col("is_media") == False) &
        (pl.col("text").str.len_chars() >= 8)
    )
    if len(df) > MAX_ROWS:
        df = df.sample(n=MAX_ROWS, seed=42)
        print(f"  [dim]sampled {MAX_ROWS:,} rows for speed[/dim]")
    rows = df.select(["ts", "sender", "text"]).to_dicts()
    clf = pipeline("sentiment-analysis",
                   model="distilbert-base-uncased-finetuned-sst-2-english",
                   truncation=True)
    sents = clf([r["text"][:200] for r in rows], batch_size=64)
    for r, sent in zip(rows, sents):
        r["sentiment"] = sent["label"]
        r["score"]     = float(sent["score"])
        r["ts"] = str(r["ts"])
    pl.DataFrame(rows).write_parquet(OUT)
    mark(s)
    print(f"  [green]{len(rows):,} rows scored[/green]")
