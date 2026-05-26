import json, polars as pl, numpy as np
from datetime import date
from rich import print
from lib.paths import MSGS_PARQUET, SITE_DATA
from lib.cache import stamp, fresh, mark

OUT = SITE_DATA / "chapter_seed.json"
PROPOSAL = date(2026, 1, 25)


def _per_day_features(df: pl.DataFrame) -> pl.DataFrame:
    d = df.with_columns(pl.col("ts").dt.date().alias("day"))
    return d.group_by("day").agg(
        pl.len().alias("n"),
        pl.col("text").str.len_chars().mean().alias("avg_len"),
        pl.col("text").str.contains(r"(?i)love|miss|baby|bebu|shaadi").sum().alias("warm"),
    ).sort("day")


def _breakpoints(daily: pl.DataFrame, min_segment_days: int = 90) -> list[date]:
    days = daily["day"].to_list()
    counts = np.array(daily["n"].to_list(), dtype=float)
    smoothed = np.convolve(counts, np.ones(14) / 14, mode="same")
    z = (smoothed - smoothed.mean()) / (smoothed.std() + 1e-6)
    valleys = []
    for i in range(min_segment_days, len(z) - min_segment_days):
        if z[i] < -0.6 and z[i] <= z[i - 1] and z[i] <= z[i + 1]:
            if not valleys or (days[i] - valleys[-1]).days >= min_segment_days:
                valleys.append(days[i])
    return valleys


def _top_keywords(df: pl.DataFrame, start: date, end: date, k: int = 5) -> list[str]:
    sub = df.filter(
        (pl.col("ts").dt.date() >= start)
        & (pl.col("ts").dt.date() <= end)
        & (pl.col("is_media") == False)
    )
    from collections import Counter
    import re
    from lib.gazetteer import STOPWORDS_EN, STOPWORDS_HI

    tok = re.compile(r"[A-Za-zऀ-ॿ]+")
    c = Counter()
    for t in sub["text"].to_list():
        for w in tok.findall(t.lower()):
            if len(w) < 4 or w in STOPWORDS_EN or w in STOPWORDS_HI:
                continue
            c[w] += 1
    return [w for w, _ in c.most_common(k)]


def _title_from_keywords(words: list[str]) -> str:
    if not words:
        return "Chapter"
    return " · ".join(w.capitalize() for w in words[:3])


def run(force: bool = False):
    s = stamp("s_chapters", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]")
        return
    df = pl.read_parquet(MSGS_PARQUET)
    daily = _per_day_features(df)
    bps = _breakpoints(daily)

    # Force the proposal day in as a mandatory chapter boundary
    if PROPOSAL not in bps:
        bps.append(PROPOSAL)
        bps.sort()

    first_day = daily["day"][0]
    last_day = daily["day"][-1]
    boundaries = [first_day] + bps + [last_day]
    boundaries = sorted(set(boundaries))

    chapters = []
    for i in range(len(boundaries) - 1):
        a, b = boundaries[i], boundaries[i + 1]
        kw = _top_keywords(df, a, b)
        chapters.append({
            "order": i + 1,
            "dateStart": str(a),
            "dateEnd": str(b),
            "suggested_title": _title_from_keywords(kw),
            "keywords": kw,
            "pinned_proposal": (a == PROPOSAL or b == PROPOSAL),
        })
    OUT.write_text(json.dumps(chapters, indent=2))
    mark(s)
    print(f"  [green]{len(chapters)} chapters detected[/green]")
