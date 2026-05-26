import json, os
from rich import print
from anthropic import Anthropic
from lib.paths import CACHE, SITE_DATA
from lib.cache import stamp, fresh, mark
from lib.cost import log as cost_log

IN  = CACHE / "ranked_candidates.jsonl"
OUT = SITE_DATA / "quotes.json"
CHAPTERS_JSON = SITE_DATA / "chapter_seed.json"
MODEL = "claude-haiku-4-5-20251001"
BATCH = 50

SYS = """You rate WhatsApp messages between Sid and Anisha (a couple) for inclusion in a private memory book.
For each message, output one JSON object on its own line with these fields:
  i: integer index from input
  score: 1-5 (5 = unforgettable, very memorable, captures personality, funny, tender)
  why: <=12 words explaining why it's memorable
  tag: one of [funny, tender, sass, fight, plan, milestone, mundane]
Output nothing but JSON lines."""


def _chapter_for(ts: str, chapters: list) -> int:
    d = ts[:10]
    for c in chapters:
        if c["dateStart"] <= d <= c["dateEnd"]:
            return c["order"]
    return chapters[-1]["order"]


def run(force: bool = False):
    s = stamp("s5", [IN, CHAPTERS_JSON])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]"); return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set — export it before running s5_curate")

    cands = [json.loads(l) for l in IN.read_text().splitlines()]
    chapters = json.loads(CHAPTERS_JSON.read_text())
    client = Anthropic(api_key=api_key)
    rated = []

    total_batches = (len(cands) + BATCH - 1) // BATCH
    for start in range(0, len(cands), BATCH):
        batch = cands[start:start + BATCH]
        body = "\n".join(f"{i}\t{c['sender']}\t{c['text']}" for i, c in enumerate(batch))
        msg = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=[{"type": "text", "text": SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": body}],
        )
        u = msg.usage
        cost, total = cost_log("s5", MODEL,
            in_tok=u.input_tokens, out_tok=u.output_tokens,
            cached_in_tok=getattr(u, "cache_read_input_tokens", 0))
        print(f"  [dim]batch {start // BATCH + 1}/{total_batches}  ${total:.4f}[/dim]")
        for line in msg.content[0].text.splitlines():
            line = line.strip()
            if not line.startswith("{"): continue
            try:
                obj = json.loads(line)
                src = batch[int(obj["i"])]
                rated.append({**src, **obj, "chapter": _chapter_for(src["ts"], chapters)})
            except Exception:
                continue

    rated.sort(key=lambda r: (r["chapter"], -int(r.get("score", 0))))
    by_chap: dict = {}
    for r in rated:
        by_chap.setdefault(r["chapter"], []).append(r)
    top = {c: rows[:30] for c, rows in by_chap.items()}
    OUT.write_text(json.dumps(top, indent=2))
    mark(s)
    print(f"  [green]{sum(len(v) for v in top.values()):,} curated quotes saved[/green]")
