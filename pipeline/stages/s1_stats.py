import json
from datetime import timedelta
from collections import Counter
import polars as pl
from rich import print
from lib.paths import MSGS_PARQUET, SITE_DATA
from lib.cache import stamp, fresh, mark

OUT = SITE_DATA / "stats.json"

def _basic_counts(df: pl.DataFrame) -> dict:
    by_sender = df.group_by("sender").agg(
        pl.len().alias("msgs"),
        pl.col("char_len").sum().alias("chars"),
        pl.col("text").cast(pl.String).fill_null("").str.split(" ").list.len().sum().alias("words"),
    ).to_dicts()
    return {"by_sender": by_sender, "total_msgs": int(df.height)}

def _per_day(df: pl.DataFrame) -> dict:
    d = df.with_columns(pl.col("ts").dt.date().alias("day"))
    per_day = d.group_by("day").agg(pl.len().alias("n")).sort("day").to_dicts()
    peak = max(per_day, key=lambda r: r["n"])
    span_days = (per_day[-1]["day"] - per_day[0]["day"]).days + 1
    avg = sum(r["n"] for r in per_day) / span_days
    return {
        "peak_day":  {"day": str(peak["day"]), "n": int(peak["n"])},
        "avg_per_day": round(avg, 2),
        "first_day": str(per_day[0]["day"]),
        "last_day":  str(per_day[-1]["day"]),
        "active_days": len(per_day),
        "span_days": span_days
    }

def _streak(df: pl.DataFrame) -> dict:
    days = sorted({r["day"] for r in df.with_columns(pl.col("ts").dt.date().alias("day")).select("day").to_dicts()})
    best = cur = 1
    best_end = cur_end = days[0]
    for i in range(1, len(days)):
        if (days[i] - days[i-1]).days == 1:
            cur += 1; cur_end = days[i]
            if cur > best:
                best, best_end = cur, cur_end
        else:
            cur = 1; cur_end = days[i]
    return {"longest_streak_days": best, "ends_on": str(best_end)}

def _hour_heatmap(df: pl.DataFrame) -> list[list[int]]:
    h = df.with_columns(
        pl.col("ts").dt.hour().alias("hr"),
        pl.col("ts").dt.weekday().alias("dow"),
    ).group_by(["dow", "hr"]).agg(pl.len().alias("n")).to_dicts()
    grid = [[0]*24 for _ in range(7)]
    for r in h:
        dow_idx = int(r["dow"]) - 1
        if 0 <= dow_idx < 7:
            grid[dow_idx][int(r["hr"])] = int(r["n"])
    return grid

def _late_night(df: pl.DataFrame) -> dict:
    late = df.filter(pl.col("ts").dt.hour() >= 23).group_by("sender").agg(pl.len().alias("n")).to_dicts()
    return {r["sender"]: int(r["n"]) for r in late}

def _first_last_of_day(df: pl.DataFrame, which: str) -> dict:
    d = df.with_columns(pl.col("ts").dt.date().alias("day"))
    agg = d.sort("ts", descending=(which == "last")).group_by("day").agg(pl.col("sender").first().alias("who"))
    cs = Counter(r["who"] for r in agg.to_dicts())
    return dict(cs)

def _reply_times(df: pl.DataFrame) -> dict:
    d = df.sort("ts")
    s = d["sender"].to_list()
    t = d["ts"].to_list()
    gaps_by = {"Sid": [], "Anisha": []}
    for i in range(1, len(s)):
        if s[i] != s[i-1]:
            delta = (t[i] - t[i-1]).total_seconds()
            if 0 < delta < 86400 * 2:
                key = s[i]
                if key in gaps_by:
                    gaps_by[key].append(delta)
    def median(xs): xs = sorted(xs); return xs[len(xs)//2] if xs else None
    return {k: round(median(v), 1) if v else None for k, v in gaps_by.items()}

def _apology(df: pl.DataFrame) -> dict:
    pat = r"(?i)\b(sorry|sry|maaf|sorry yaar|im sorry|i am sorry)\b"
    out = df.filter(pl.col("text").str.contains(pat)).group_by("sender").agg(pl.len().alias("n")).to_dicts()
    return {r["sender"]: int(r["n"]) for r in out}


import emoji as emoji_lib
import re as _re
from lib.gazetteer import STOPWORDS_EN, STOPWORDS_HI, ENDEARMENTS, PLACES, MENTION_TOPICS

_TOKEN = _re.compile(r"[A-Za-zऀ-ॿ]+")

def _top_words(df: pl.DataFrame, n: int = 50) -> dict:
    out = {}
    for sender in ["Sid", "Anisha"]:
        c = Counter()
        for t in df.filter(pl.col("sender") == sender)["text"].cast(pl.String).fill_null("").to_list():
            for w in _TOKEN.findall(t.lower()):
                if w in STOPWORDS_EN or w in STOPWORDS_HI or len(w) < 2:
                    continue
                c[w] += 1
        out[sender] = c.most_common(n)
    return out

def _signature_words(top: dict) -> dict:
    s = {w for w, _ in top["Sid"]}
    a = {w for w, _ in top["Anisha"]}
    return {
        "Sid_only":    sorted(list(s - a))[:30],
        "Anisha_only": sorted(list(a - s))[:30],
    }

def _emoji_freq(df: pl.DataFrame) -> dict:
    counts = {"Sid": Counter(), "Anisha": Counter()}
    for r in df.iter_rows(named=True):
        sender = r["sender"]
        if sender in counts:
            for ch in emoji_lib.distinct_emoji_list(r["text"] or ""):
                counts[sender][ch] += 1
    return {k: v.most_common(50) for k, v in counts.items()}

def _emoji_inflation(df: pl.DataFrame) -> dict:
    yr = df.with_columns(pl.col("ts").dt.year().alias("y"))
    out = {}
    for row in yr.iter_rows(named=True):
        y = row["y"]
        if row["text"] and "😂" in row["text"]:
            out[y] = out.get(y, 0) + 1
    return dict(sorted(out.items()))

def _punctuation(df: pl.DataFrame) -> dict:
    out = {}
    for sender in ["Sid", "Anisha"]:
        text = " ".join(t or "" for t in df.filter(pl.col("sender") == sender)["text"].to_list())
        out[sender] = {
            "exclam":  text.count("!"),
            "quest":   text.count("?"),
            "ellipsis": text.count("..."),
            "period":  text.count("."),
            "caps_msgs": sum(1 for line in text.split("\n") if line.isupper() and len(line) > 3),
        }
    return out

def _question_ratio(df: pl.DataFrame) -> dict:
    out = {}
    for sender in ["Sid", "Anisha"]:
        sub = df.filter(pl.col("sender") == sender)
        if sub.height == 0:
            out[sender] = 0.0; continue
        q = sub.filter(pl.col("text").str.ends_with("?")).height
        out[sender] = round(q / sub.height, 3)
    return out

def _endearments(df: pl.DataFrame) -> dict:
    out = {}
    for name in ENDEARMENTS:
        pat = rf"(?i)\b{name}+\b"
        ct = df.filter(pl.col("text").str.contains(pat)).group_by("sender").agg(pl.len().alias("n")).to_dicts()
        out[name] = {r["sender"]: int(r["n"]) for r in ct}
    return out

def _elongation_record(df: pl.DataFrame) -> dict:
    pat = _re.compile(r"(\w)\1{3,}")
    best = ("", 0, None)
    for r in df.iter_rows(named=True):
        text = r["text"] or ""
        for m in pat.finditer(text):
            if len(m.group(0)) > best[1]:
                best = (m.group(0), len(m.group(0)), r["sender"])
    return {"word": best[0], "len": best[1], "by": best[2]}

def _mentions(df: pl.DataFrame) -> dict:
    out = {topic: 0 for topic in MENTION_TOPICS}
    for r in df.iter_rows(named=True):
        low = (r["text"] or "").lower()
        for topic, words in MENTION_TOPICS.items():
            if any(w in low for w in words):
                out[topic] += 1
    return out

def _places(df: pl.DataFrame) -> dict:
    out = {p: 0 for p in PLACES}
    for r in df.iter_rows(named=True):
        low = (r["text"] or "").lower()
        for p in PLACES:
            if p in low:
                out[p] += 1
    return {k: v for k, v in sorted(out.items(), key=lambda x: -x[1]) if v > 0}

def _links(df: pl.DataFrame) -> dict:
    url = _re.compile(r"https?://[^\s]+")
    out = {"Sid": [], "Anisha": []}
    for r in df.iter_rows(named=True):
        sender = r["sender"]
        if sender in out:
            for u in url.findall(r["text"] or ""):
                out[sender].append({"url": u, "ts": str(r["ts"])})
    return {k: v[:200] for k, v in out.items()}

def _milestone_counts(df: pl.DataFrame) -> dict:
    phrases = ["i love you", "love you", "miss you", "shaadi", "marry"]
    out = {}
    for p in phrases:
        ct = df.filter(pl.col("text").str.to_lowercase().str.contains(p)).group_by("sender").agg(pl.len().alias("n")).to_dicts()
        out[p] = {r["sender"]: int(r["n"]) for r in ct}
    return out

def _photo_leaderboard(df: pl.DataFrame) -> dict:
    pic = df.filter(pl.col("media_type") == "image").with_columns(pl.col("ts").dt.year().alias("y"))
    out = pic.group_by(["y", "sender"]).agg(pl.len().alias("n")).to_dicts()
    res: dict = {}
    for r in out:
        res.setdefault(int(r["y"]), {})[r["sender"]] = int(r["n"])
    return dict(sorted(res.items()))


def run(force: bool = False):
    s = stamp("s1", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]")
        return
    df = pl.read_parquet(MSGS_PARQUET)

    out = {
        "counts":              _basic_counts(df),
        "per_day":             _per_day(df),
        "streak":              _streak(df),
        "hour_heatmap_dow_hr": _hour_heatmap(df),
        "late_night":          _late_night(df),
        "first_msg_of_day":    _first_last_of_day(df, "first"),
        "last_msg_of_day":     _first_last_of_day(df, "last"),
        "median_reply_seconds": _reply_times(df),
        "apologies":           _apology(df),
    }

    top = _top_words(df)
    out["top_words"]        = top
    out["signature_words"]  = _signature_words(top)
    out["emojis"]           = _emoji_freq(df)
    out["laugh_inflation"]  = _emoji_inflation(df)
    out["punctuation"]      = _punctuation(df)
    out["question_ratio"]   = _question_ratio(df)
    out["endearments"]      = _endearments(df)
    out["elongation"]       = _elongation_record(df)
    out["mentions"]         = _mentions(df)
    out["places"]           = _places(df)
    out["links_by_sender"]  = _links(df)
    out["milestone_phrases"] = _milestone_counts(df)
    out["photo_leaderboard"] = _photo_leaderboard(df)

    OUT.write_text(json.dumps(out, indent=2, default=str))
    mark(s)
    print(f"  [green]wrote {OUT}[/green]")
