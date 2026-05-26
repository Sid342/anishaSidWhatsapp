import polars as pl
from rich import print
from lib.parser import parse_chat_text
from lib.paths import CHAT_TXT, MSGS_PARQUET
from lib.cache import stamp, fresh, mark

def run(force: bool = False):
    s = stamp("s0", [CHAT_TXT])
    if fresh(s) and not force and MSGS_PARQUET.exists():
        print("  [dim]cached, skipping[/dim]")
        return

    text = CHAT_TXT.read_text(encoding="utf-8")
    msgs = parse_chat_text(text)
    df = pl.DataFrame({
        "ts":         [m.ts for m in msgs],
        "sender":     [m.sender for m in msgs],
        "text":       [m.text for m in msgs],
        "is_media":   [m.is_media for m in msgs],
        "media_type": [m.media_type for m in msgs],
    }).with_columns(
        pl.col("ts").cast(pl.Datetime("us")),
        pl.col("text").cast(pl.String).fill_null("").str.len_chars().alias("char_len"),
    )
    MSGS_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(MSGS_PARQUET)
    mark(s)
    print(f"  [green]parsed {len(df):,} msgs[/green]")
