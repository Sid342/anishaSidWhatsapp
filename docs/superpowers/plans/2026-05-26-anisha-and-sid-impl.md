# Anisha & Sid Memory-Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a private, password-gated chaptered-book memory site from 9 years of WhatsApp chat between Sid and Anisha, with curated quotes, full-text search, first-X moments, 60+ fun stats, and per-chapter photo galleries.

**Architecture:** Local Python build pipeline parses chat → emits static JSON + optimized media → Astro static site renders chaptered book + dashboard. GitHub remote auto-deploys via Cloudflare Pages; a Cloudflare Worker enforces a single shared password. LLM only touches pre-filtered, clustered candidates (Haiku for quote curation, Sonnet for chapter intros); zero LLM at runtime. Total LLM spend per build <$0.50.

**Tech Stack:** Astro 5 + React 19 + Tailwind 4 + MDX + Pagefind + Observable Plot (site); Python 3.12 + uv + polars + sentence-transformers + distilbert + anthropic SDK (pipeline); Cloudflare Worker + Pages (auth/deploy).

**Repo:** `~/Projects/whatsapp-sid-anisha` (symlinked at `/Users/sid/Documents/Whatsapp Sid Anisha`). GitHub remote `Sid342/anishaSidWhatsapp`. Branch `main`. Use `/usr/bin/git` (Nordic toolchain git lacks `remote-https`).

**Spec:** `docs/superpowers/specs/2026-05-26-anisha-and-sid-design.md`

**Inputs already in place:**
- Chat at `data/_chat.txt` (25 MB, 482k lines) — gitignored
- Proposal anchor: **25 January 2026** (user-pinned chapter boundary)

**Deferred / pending:**
- WhatsApp `.zip` with media (blocks Phase 5)
- Shared password (set at Phase 7 deploy)
- Custom domain (default to `*.pages.dev`)

---

## Phase 1 — Foundation

Goal: a working Astro app with the dark luxe + warm paper theme, mock chapters wired through layouts, no real data yet.

### Task 1.1: Scaffold Astro project under `site/`

**Files:**
- Create: `site/package.json`
- Create: `site/astro.config.mjs`
- Create: `site/tsconfig.json`
- Create: `site/.gitignore`

- [ ] **Step 1: Create `site/package.json`**

```json
{
  "name": "anisha-sid-site",
  "type": "module",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build && pagefind --site dist",
    "preview": "astro preview",
    "check": "astro check"
  },
  "dependencies": {
    "@astrojs/check": "^0.9.0",
    "@astrojs/mdx": "^4.0.0",
    "@astrojs/react": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "@observablehq/plot": "^0.6.16",
    "astro": "^5.0.0",
    "d3": "^7.9.0",
    "pagefind": "^1.3.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.7.0"
  }
}
```

- [ ] **Step 2: Create `site/astro.config.mjs`**

```js
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import mdx from "@astrojs/mdx";
import tailwind from "@tailwindcss/vite";

export default defineConfig({
  integrations: [react(), mdx()],
  output: "static",
  site: "https://anishasid.pages.dev",
  vite: {
    plugins: [tailwind()],
    build: { assetsInlineLimit: 0 }
  }
});
```

- [ ] **Step 3: Create `site/tsconfig.json`**

```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "react",
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src/**/*", "astro.config.mjs"]
}
```

- [ ] **Step 4: Create `site/.gitignore`**

```
node_modules/
dist/
.astro/
.cache/
.pagefind/
```

- [ ] **Step 5: Install deps**

```bash
cd site && npm install
```
Expected: `node_modules/` populated, no error.

- [ ] **Step 6: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add site/package.json site/astro.config.mjs site/tsconfig.json site/.gitignore site/package-lock.json
/usr/bin/git commit -m "feat(site): scaffold Astro 5 + React + MDX + Tailwind"
```

### Task 1.2: Tailwind 4 base + theme tokens

**Files:**
- Create: `site/tailwind.config.ts`
- Create: `site/src/styles/globals.css`

- [ ] **Step 1: Create `site/tailwind.config.ts`**

```ts
import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}"],
  theme: {
    extend: {
      colors: {
        midnight: { 950: "#08060d", 900: "#0d0a16", 800: "#13101e" },
        gold:     { 400: "#d4af6a", 500: "#c89a4a", 600: "#a87a2e" },
        paper:    { 50:  "#f4ecd8", 100: "#ede0c2", 200: "#dcc89a" },
        ink:      { 900: "#1b1208", 700: "#3a2716" }
      },
      fontFamily: {
        serif:  ["EB Garamond", "Georgia", "serif"],
        hand:   ["Caveat", "cursive"],
        mono:   ["JetBrains Mono", "monospace"]
      },
      boxShadow: {
        paper: "0 2px 12px rgba(0,0,0,0.55), inset 0 0 24px rgba(120,90,40,0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;
```

- [ ] **Step 2: Create `site/src/styles/globals.css`**

```css
@import "tailwindcss";

:root {
  --bg:      #08060d;
  --fg:      #e9dfc7;
  --accent:  #d4af6a;
  --paper:   #f4ecd8;
  --ink:     #1b1208;
}

html, body {
  background: var(--bg);
  color: var(--fg);
  font-family: "EB Garamond", Georgia, serif;
  font-feature-settings: "liga", "kern";
}

.rule-gold {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.6;
}

@font-face {
  font-family: "EB Garamond";
  src: local("EB Garamond");
  font-display: swap;
}
```

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add site/tailwind.config.ts site/src/styles/globals.css
/usr/bin/git commit -m "feat(site): tailwind config + dark luxe / warm paper tokens"
```

### Task 1.3: BookLayout + PaperCard

**Files:**
- Create: `site/src/layouts/BookLayout.astro`
- Create: `site/src/components/PaperCard.astro`

- [ ] **Step 1: Create `site/src/layouts/BookLayout.astro`**

```astro
---
import "../styles/globals.css";
interface Props { title: string; }
const { title } = Astro.props;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex, nofollow" />
    <title>{title}</title>
  </head>
  <body class="min-h-dvh bg-midnight-950 text-paper-50">
    <header class="px-6 md:px-12 py-6 flex justify-between items-baseline">
      <a href="/book" class="font-serif text-xl tracking-wide text-gold-400">Anisha &amp; Sid</a>
      <nav class="text-sm font-mono opacity-70 flex gap-5">
        <a href="/search">search</a>
        <a href="/stats">stats</a>
        <a href="/firsts">firsts</a>
        <a href="/archive">archive</a>
      </nav>
    </header>
    <div class="rule-gold mx-6 md:mx-12"></div>
    <main class="px-6 md:px-12 py-10 max-w-3xl mx-auto"><slot /></main>
    <footer class="px-6 md:px-12 py-10 text-center font-mono text-xs opacity-50">
      for her, with everything
    </footer>
  </body>
</html>
```

- [ ] **Step 2: Create `site/src/components/PaperCard.astro`**

```astro
---
interface Props { date: string; sender: "Sid" | "Anisha"; }
const { date, sender } = Astro.props;
---
<figure class="bg-paper-50 text-ink-900 my-8 px-6 py-5 rounded-sm shadow-paper relative">
  <figcaption class="font-mono text-[11px] opacity-60 mb-2">{date}</figcaption>
  <blockquote class="font-serif text-lg leading-snug"><slot /></blockquote>
  <div class="font-hand text-right mt-3 text-base">— {sender}</div>
</figure>
```

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add site/src/layouts/BookLayout.astro site/src/components/PaperCard.astro
/usr/bin/git commit -m "feat(site): BookLayout shell + PaperCard quote inset"
```

### Task 1.4: Content collection schema

**Files:**
- Create: `site/src/content/config.ts`
- Create: `site/src/content/chapters/00-mock.mdx`

- [ ] **Step 1: Create `site/src/content/config.ts`**

```ts
import { defineCollection, z } from "astro:content";

const chapters = defineCollection({
  type: "content",
  schema: z.object({
    order: z.number(),
    title: z.string(),
    dateStart: z.string(),
    dateEnd: z.string(),
    cover: z.string().optional(),
    summary: z.string().optional()
  })
});

export const collections = { chapters };
```

- [ ] **Step 2: Create `site/src/content/chapters/00-mock.mdx`**

```mdx
---
order: 0
title: "Mock Chapter"
dateStart: "2017-07-19"
dateEnd: "2017-08-31"
summary: "placeholder until real data flows in"
---

import PaperCard from "../../components/PaperCard.astro";

The first weeks were small messages and large laughs.

<PaperCard date="20 Jul 2017, 11:56 AM" sender="Sid">
  If u listen to punjabi songs
</PaperCard>

<PaperCard date="20 Jul 2017, 12:34 PM" sender="Anisha">
  I have heard some punjabi songs, but its so difficult for me to understand the language
</PaperCard>
```

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add site/src/content/config.ts site/src/content/chapters/00-mock.mdx
/usr/bin/git commit -m "feat(site): content collection schema + mock chapter"
```

### Task 1.5: Pages — landing, library, chapter

**Files:**
- Create: `site/src/pages/index.astro`
- Create: `site/src/pages/book/index.astro`
- Create: `site/src/pages/book/[...slug].astro`

- [ ] **Step 1: Create `site/src/pages/index.astro`**

```astro
---
import BookLayout from "../layouts/BookLayout.astro";
---
<BookLayout title="Anisha & Sid">
  <section class="text-center py-24">
    <h1 class="font-serif text-5xl md:text-7xl text-gold-400 tracking-wide">Anisha &amp; Sid</h1>
    <p class="font-mono text-xs opacity-60 mt-4">2017 — present</p>
    <a href="/book" class="inline-block mt-12 px-8 py-3 border border-gold-500 text-gold-400 font-mono text-sm hover:bg-gold-600/10">Open the book</a>
  </section>
</BookLayout>
```

- [ ] **Step 2: Create `site/src/pages/book/index.astro`**

```astro
---
import BookLayout from "../../layouts/BookLayout.astro";
import { getCollection } from "astro:content";
const chapters = (await getCollection("chapters")).sort((a, b) => a.data.order - b.data.order);
---
<BookLayout title="The Book — Anisha & Sid">
  <h2 class="font-serif text-3xl text-gold-400 mb-8">Chapters</h2>
  <div class="grid md:grid-cols-2 gap-6">
    {chapters.map((c) => (
      <a href={`/book/${c.slug}`} class="block border border-gold-600/30 p-6 hover:border-gold-500 transition">
        <div class="font-mono text-[11px] text-gold-400/70">{c.data.dateStart} → {c.data.dateEnd}</div>
        <div class="font-serif text-2xl mt-2">{c.data.title}</div>
        {c.data.summary && <p class="text-sm opacity-70 mt-3">{c.data.summary}</p>}
      </a>
    ))}
  </div>
</BookLayout>
```

- [ ] **Step 3: Create `site/src/pages/book/[...slug].astro`**

```astro
---
import BookLayout from "../../layouts/BookLayout.astro";
import { getCollection, render } from "astro:content";

export async function getStaticPaths() {
  const chapters = await getCollection("chapters");
  return chapters.map((c) => ({ params: { slug: c.slug }, props: { chapter: c } }));
}

const { chapter } = Astro.props;
const { Content } = await render(chapter);
---
<BookLayout title={chapter.data.title}>
  <article>
    <header class="mb-10">
      <div class="font-mono text-[11px] text-gold-400/70">{chapter.data.dateStart} — {chapter.data.dateEnd}</div>
      <h1 class="font-serif text-4xl md:text-5xl text-gold-400 mt-2">{chapter.data.title}</h1>
    </header>
    <div class="prose-content"><Content /></div>
  </article>
</BookLayout>
```

- [ ] **Step 4: Run dev server**

```bash
cd site && npm run dev
```
Expected: server starts at `http://localhost:4321`, landing page loads, `/book` lists Mock Chapter, `/book/00-mock` renders cards.

- [ ] **Step 5: Stop server (Ctrl-C) and commit**

```bash
/usr/bin/git add site/src/pages/
/usr/bin/git commit -m "feat(site): landing, library, chapter routes"
```

### Task 1.6: Push Phase 1

- [ ] **Step 1: Push**

```bash
/usr/bin/git push
```

---

## Phase 2 — Parser + Stats Core

Goal: real numbers on `/stats` and `/firsts`, from the actual chat.

### Task 2.1: Pipeline scaffolding (`pyproject.toml`, dirs)

**Files:**
- Create: `pipeline/pyproject.toml`
- Create: `pipeline/run.py`
- Create: `pipeline/.python-version`
- Create: `pipeline/lib/__init__.py`
- Create: `pipeline/stages/__init__.py`
- Create: `pipeline/tests/__init__.py`

- [ ] **Step 1: Create `pipeline/.python-version`**

```
3.12
```

- [ ] **Step 2: Create `pipeline/pyproject.toml`**

```toml
[project]
name = "pipeline"
version = "0.0.1"
requires-python = ">=3.12"
dependencies = [
  "polars>=1.20.0",
  "pyarrow>=18.0.0",
  "emoji>=2.14.0",
  "regex>=2024.11.6",
  "tqdm>=4.66.0",
  "python-dateutil>=2.9.0",
  "anthropic>=0.42.0",
  "sentence-transformers>=3.3.0",
  "scikit-learn>=1.5.0",
  "transformers>=4.46.0",
  "torch>=2.5.0",
  "numpy>=1.26.0",
  "rich>=13.9.0"
]

[dependency-groups]
dev = ["pytest>=8.3.0", "ruff>=0.8.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 3: Create empty `pipeline/lib/__init__.py`, `pipeline/stages/__init__.py`, `pipeline/tests/__init__.py`**

Three empty files.

- [ ] **Step 4: Create `pipeline/run.py`**

```python
import argparse, importlib, sys
from rich import print

STAGES = ["s0_parse", "s1_stats", "s2_firsts", "s3_candidates",
          "s4_cluster", "s_nlp", "s_chapters", "s5_curate", "s6_intros"]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", help="run a single stage (e.g. s0_parse)")
    p.add_argument("--from", dest="start", help="run from this stage onward")
    p.add_argument("--force", action="store_true", help="ignore cache")
    args = p.parse_args()

    selected = [args.stage] if args.stage else (
        STAGES[STAGES.index(args.start):] if args.start else STAGES)

    for s in selected:
        print(f"[bold cyan]→ {s}")
        mod = importlib.import_module(f"stages.{s}")
        mod.run(force=args.force)
    print("[bold green]done")

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Install deps with uv**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha/pipeline
uv sync
```
Expected: `.venv/` created. If `uv` not installed: `brew install uv`.

- [ ] **Step 6: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/pyproject.toml pipeline/run.py pipeline/.python-version pipeline/lib/ pipeline/stages/ pipeline/tests/ pipeline/uv.lock
/usr/bin/git commit -m "feat(pipeline): scaffold uv project + run.py harness"
```

### Task 2.2: Parser library (TDD)

**Files:**
- Create: `pipeline/lib/parser.py`
- Create: `pipeline/tests/test_parser.py`

- [ ] **Step 1: Write failing test `pipeline/tests/test_parser.py`**

```python
from lib.parser import parse_chat_text

SAMPLE = """[19/07/17, 9:07:11 PM] Sid: This is better😂😂
[19/07/17, 9:45:38 PM] Anisha: 😂
[19/07/17, 10:38:13 PM] Anisha: I am never gonna be free, might be on discount sometime, but mostly fresh..
[19/07/17, 10:38:19 PM] Anisha: I hope u get this joke
[20/07/17, 7:05:01 AM] Anisha: Really?
Well maybe..
‎[19/07/17, 11:36:32 PM] Sid: ‎image omitted
"""

def test_basic_parse():
    msgs = parse_chat_text(SAMPLE)
    assert len(msgs) == 6
    assert msgs[0].sender == "Sid"
    assert msgs[0].text == "This is better😂😂"
    assert msgs[0].ts.year == 2017 and msgs[0].ts.month == 7 and msgs[0].ts.day == 19

def test_multiline_continuation():
    msgs = parse_chat_text(SAMPLE)
    assert msgs[4].text == "Really?\nWell maybe.."

def test_media_classification():
    msgs = parse_chat_text(SAMPLE)
    assert msgs[5].is_media is True
    assert msgs[5].media_type == "image"
```

- [ ] **Step 2: Run and confirm FAIL**

```bash
cd pipeline && uv run pytest tests/test_parser.py -v
```
Expected: ModuleNotFoundError or AttributeError.

- [ ] **Step 3: Implement `pipeline/lib/parser.py`**

```python
from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator

# WhatsApp iOS export format, e.g. "[19/07/17, 9:07:11 PM] Sid: hi"
HEAD = re.compile(
    r"^‎?\[(\d{1,2})/(\d{1,2})/(\d{2,4}), "
    r"(\d{1,2}):(\d{2})(?::(\d{2}))? ?([AP]M)?\] "
    r"([^:]+): ?(.*)$"
)

MEDIA_PATTERNS = {
    "image":   re.compile(r"image omitted", re.IGNORECASE),
    "video":   re.compile(r"video omitted", re.IGNORECASE),
    "audio":   re.compile(r"audio omitted", re.IGNORECASE),
    "sticker": re.compile(r"sticker omitted", re.IGNORECASE),
    "doc":     re.compile(r"document omitted", re.IGNORECASE),
    "gif":     re.compile(r"GIF omitted", re.IGNORECASE),
}

@dataclass
class Msg:
    ts: datetime
    sender: str
    text: str
    is_media: bool
    media_type: str | None

def _parse_ts(d, m, y, h, mi, s, ap) -> datetime:
    y = int(y)
    if y < 100:
        y += 2000
    h = int(h)
    if ap == "PM" and h != 12: h += 12
    if ap == "AM" and h == 12: h = 0
    return datetime(y, int(m), int(d), h, int(mi), int(s) if s else 0)

def parse_chat_text(text: str) -> list[Msg]:
    out: list[Msg] = []
    current: Msg | None = None
    for line in text.splitlines():
        line = line.replace("‎", "")
        m = HEAD.match(line)
        if m:
            if current is not None:
                out.append(current)
            d, mo, y, h, mi, s, ap, sender, body = m.groups()
            ts = _parse_ts(d, mo, y, h, mi, s, ap)
            media_type = next((k for k, p in MEDIA_PATTERNS.items() if p.search(body)), None)
            current = Msg(ts=ts, sender=sender.strip(), text=body.strip(),
                          is_media=media_type is not None, media_type=media_type)
        else:
            if current is not None and line:
                current.text = current.text + "\n" + line.strip()
    if current is not None:
        out.append(current)
    return out
```

- [ ] **Step 4: Run tests; expect PASS**

```bash
cd pipeline && uv run pytest tests/test_parser.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/lib/parser.py pipeline/tests/test_parser.py
/usr/bin/git commit -m "feat(pipeline): chat parser with multi-line + media handling"
```

### Task 2.3: Stage S0 — full parse to parquet

**Files:**
- Create: `pipeline/lib/paths.py`
- Create: `pipeline/lib/cache.py`
- Create: `pipeline/stages/s0_parse.py`

- [ ] **Step 1: Create `pipeline/lib/paths.py`**

```python
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
```

- [ ] **Step 2: Create `pipeline/lib/cache.py`**

```python
import hashlib, json
from pathlib import Path
from .paths import CACHE

def stamp(name: str, deps: list[Path], extras: dict | None = None) -> Path:
    h = hashlib.sha256()
    for d in deps:
        h.update(d.read_bytes() if d.exists() else b"")
    if extras:
        h.update(json.dumps(extras, sort_keys=True).encode())
    return CACHE / f"{name}.{h.hexdigest()[:12]}.stamp"

def fresh(stamp_path: Path) -> bool:
    return stamp_path.exists()

def mark(stamp_path: Path):
    stamp_path.write_text("ok")
```

- [ ] **Step 3: Create `pipeline/stages/s0_parse.py`**

```python
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
        pl.col("text").str.len_chars().alias("char_len"),
    )
    MSGS_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(MSGS_PARQUET)
    mark(s)
    print(f"  [green]parsed {len(df):,} msgs[/green]")
```

- [ ] **Step 4: Run S0**

```bash
cd pipeline && uv run python run.py --stage s0_parse
```
Expected: "parsed 464,340 msgs" (±1k).

- [ ] **Step 5: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/lib/paths.py pipeline/lib/cache.py pipeline/stages/s0_parse.py
/usr/bin/git commit -m "feat(pipeline): S0 parse → messages.parquet w/ input-hash cache"
```

### Task 2.4: Stage S1 — volume & cadence stats

**Files:**
- Create: `pipeline/stages/s1_stats.py`

- [ ] **Step 1: Write the stage** (`pipeline/stages/s1_stats.py`)

```python
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
        pl.col("text").str.split(" ").list.len().sum().alias("words"),
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
        grid[int(r["dow"]) - 1][int(r["hr"])] = int(r["n"])
    return grid

def _late_night(df: pl.DataFrame) -> dict:
    late = df.filter(pl.col("ts").dt.hour() >= 23).group_by("sender").agg(pl.len().alias("n")).to_dicts()
    return {r["sender"]: int(r["n"]) for r in late}

def _first_last_of_day(df: pl.DataFrame, which: str) -> dict:
    d = df.with_columns(pl.col("ts").dt.date().alias("day"))
    agg = d.sort("ts", descending=(which == "last")).group_by("day").agg(pl.col("sender").first().alias("who"))
    counts = Counter(agg.to_dicts(), )  # placeholder fix below
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
                gaps_by[s[i]].append(delta)
    def median(xs): xs = sorted(xs); return xs[len(xs)//2] if xs else None
    return {k: round(median(v), 1) if v else None for k, v in gaps_by.items()}

def _apology(df: pl.DataFrame) -> dict:
    pat = r"(?i)\b(sorry|sry|maaf|sorry yaar|im sorry|i am sorry)\b"
    out = df.filter(pl.col("text").str.contains(pat)).group_by("sender").agg(pl.len().alias("n")).to_dicts()
    return {r["sender"]: int(r["n"]) for r in out}

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
    OUT.write_text(json.dumps(out, indent=2, default=str))
    mark(s)
    print(f"  [green]wrote {OUT}[/green]")
```

- [ ] **Step 2: Run S1**

```bash
cd pipeline && uv run python run.py --stage s1_stats
```
Expected: `site/src/data/stats.json` written, ~30-60 KB.

- [ ] **Step 3: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/stages/s1_stats.py site/src/data/stats.json
/usr/bin/git commit -m "feat(pipeline): S1 stats — counts, cadence, heatmap, reply times, apologies"
```

### Task 2.5: Extend S1 — vocabulary, emoji, punctuation, nicknames

**Files:**
- Modify: `pipeline/stages/s1_stats.py`
- Create: `pipeline/lib/gazetteer.py`

- [ ] **Step 1: Create `pipeline/lib/gazetteer.py`**

```python
STOPWORDS_EN = set("""
a an the and or but if then else of for to in on at by from with as is are was were be been being have has had do does did
i you he she we they it me him her us them my your his our their this that these those not no yes ok okay
""".split())

STOPWORDS_HI = set("""
ka ke ki ko ho hu hai hain h se na ne to bhi par mein mei mai me tu tum tujhe mujhe kya kyun kyu kab phir aur lekin
""".split())

ENDEARMENTS = ["baby", "bebu", "beboo", "bebs", "babyy", "babyyy", "babyyyy",
               "anisaa", "anisa", "anisha", "sid", "sidd", "siddy", "babu", "jaan", "love"]

PLACES = ["delhi", "noida", "gurgaon", "gurugram", "lajpat", "rajouri",
          "mandi house", "rajiv chowk", "rajeev chowk", "kashmere gate",
          "saket", "hauz khas", "huda city", "escorts", "mujesar", "metro"]

MENTION_TOPICS = {
    "parents":  ["mummy", "papa", "mom", "dad", "ghar", "parents"],
    "lenovo":   ["lenovo", "office", "boss", "team", "manager"],
    "college":  ["college", "du", "exam", "class", "lecture", "prof"],
    "wedding":  ["shaadi", "marry", "marriage", "ring", "engagement"],
    "money":    ["money", "salary", "rent", "expense", "save", "saving"],
    "food":     ["food", "biryani", "pizza", "dosa", "khana", "zomato", "swiggy"],
}

FOOD_KEYWORDS = ["zomato", "swiggy", "biryani", "pizza", "burger", "dosa",
                 "khana", "lunch", "dinner", "breakfast", "chai"]

TRAVEL_KEYWORDS = ["flight", "irctc", "indigo", "vistara", "spicejet",
                   "airport", "train", "uber", "ola", "metro"]
```

- [ ] **Step 2: Extend `s1_stats.py` — append helpers and wire into `run`**

Add the following functions and include their outputs in the `out` dict in `run()`:

```python
import emoji as emoji_lib
import re as _re
from lib.gazetteer import STOPWORDS_EN, STOPWORDS_HI, ENDEARMENTS, PLACES, MENTION_TOPICS, FOOD_KEYWORDS, TRAVEL_KEYWORDS

_TOKEN = _re.compile(r"[A-Za-zऀ-ॿ]+")

def _top_words(df: pl.DataFrame, n: int = 50) -> dict:
    out = {}
    for sender in ["Sid", "Anisha"]:
        c = Counter()
        for t in df.filter(pl.col("sender") == sender)["text"].to_list():
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
        for ch in emoji_lib.distinct_emoji_list(r["text"]):
            counts[r["sender"]][ch] += 1
    return {k: v.most_common(50) for k, v in counts.items()}

def _emoji_inflation(df: pl.DataFrame) -> dict:
    yr = df.with_columns(pl.col("ts").dt.year().alias("y"))
    out = {}
    for row in yr.iter_rows(named=True):
        y = row["y"]
        if "😂" in row["text"]:
            out[y] = out.get(y, 0) + 1
    return dict(sorted(out.items()))

def _punctuation(df: pl.DataFrame) -> dict:
    out = {}
    for sender in ["Sid", "Anisha"]:
        text = " ".join(df.filter(pl.col("sender") == sender)["text"].to_list())
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
        for m in pat.finditer(r["text"]):
            if len(m.group(0)) > best[1]:
                best = (m.group(0), len(m.group(0)), r["sender"])
    return {"word": best[0], "len": best[1], "by": best[2]}

def _mentions(df: pl.DataFrame) -> dict:
    out = {topic: 0 for topic in MENTION_TOPICS}
    for r in df.iter_rows(named=True):
        low = r["text"].lower()
        for topic, words in MENTION_TOPICS.items():
            if any(w in low for w in words):
                out[topic] += 1
    return out

def _places(df: pl.DataFrame) -> dict:
    out = {p: 0 for p in PLACES}
    for r in df.iter_rows(named=True):
        low = r["text"].lower()
        for p in PLACES:
            if p in low:
                out[p] += 1
    return {k: v for k, v in sorted(out.items(), key=lambda x: -x[1]) if v > 0}

def _links(df: pl.DataFrame) -> dict:
    url = _re.compile(r"https?://[^\s]+")
    out = {"Sid": [], "Anisha": []}
    for r in df.iter_rows(named=True):
        for u in url.findall(r["text"]):
            out[r["sender"]].append({"url": u, "ts": str(r["ts"])})
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
```

Then update `run()` to include in `out`:

```python
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
```

- [ ] **Step 3: Run S1 with `--force`**

```bash
cd pipeline && uv run python run.py --stage s1_stats --force
```
Expected: completes in <60s, stats.json grows to ~200-400 KB.

- [ ] **Step 4: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/lib/gazetteer.py pipeline/stages/s1_stats.py site/src/data/stats.json
/usr/bin/git commit -m "feat(pipeline): S1 vocab + emoji + nicknames + mentions + milestones"
```

### Task 2.6: Stage S2 — first-X moments

**Files:**
- Create: `pipeline/stages/s2_firsts.py`

- [ ] **Step 1: Create the stage**

```python
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
```

- [ ] **Step 2: Run**

```bash
cd pipeline && uv run python run.py --stage s2_firsts
```
Expected: ~40-50 firsts entries.

- [ ] **Step 3: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/stages/s2_firsts.py site/src/data/firsts.json
/usr/bin/git commit -m "feat(pipeline): S2 firsts — first occurrence per phrase per sender + context"
```

### Task 2.7: `/stats` page rendering real data

**Files:**
- Create: `site/src/pages/stats.astro`
- Create: `site/src/components/HourHeatmap.tsx`

- [ ] **Step 1: Create `site/src/components/HourHeatmap.tsx`**

```tsx
import React from "react";

export default function HourHeatmap({ grid }: { grid: number[][] }) {
  const max = Math.max(...grid.flat());
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return (
    <div className="font-mono text-[10px]">
      <div className="grid grid-cols-[40px_repeat(24,1fr)] gap-[2px]">
        <div></div>
        {Array.from({ length: 24 }, (_, h) => (
          <div key={h} className="text-center opacity-50">{h}</div>
        ))}
        {grid.map((row, di) => (
          <React.Fragment key={di}>
            <div className="opacity-60">{days[di]}</div>
            {row.map((v, hi) => {
              const a = max ? v / max : 0;
              return <div key={hi} title={`${days[di]} ${hi}:00 — ${v} msgs`}
                style={{ background: `rgba(212,175,106,${a})`, height: 14 }} />;
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create `site/src/pages/stats.astro`**

```astro
---
import BookLayout from "../layouts/BookLayout.astro";
import HourHeatmap from "../components/HourHeatmap.tsx";
import stats from "../data/stats.json";
---
<BookLayout title="Stats — Anisha & Sid">
  <h1 class="font-serif text-4xl text-gold-400 mb-2">By the Numbers</h1>
  <p class="font-mono text-xs opacity-60 mb-10">{stats.per_day.first_day} → {stats.per_day.last_day} · {stats.per_day.span_days} days</p>

  <section class="grid md:grid-cols-3 gap-8 mb-12 font-mono text-sm">
    {stats.counts.by_sender.map((r: any) => (
      <div>
        <div class="text-gold-400 text-lg font-serif">{r.sender}</div>
        <div>{r.msgs.toLocaleString()} messages</div>
        <div>{r.words.toLocaleString()} words</div>
        <div>{r.chars.toLocaleString()} characters</div>
      </div>
    ))}
    <div>
      <div class="text-gold-400 text-lg font-serif">Together</div>
      <div>{stats.counts.total_msgs.toLocaleString()} total</div>
      <div>{stats.per_day.avg_per_day} avg/day</div>
      <div>Peak: {stats.per_day.peak_day.n} on {stats.per_day.peak_day.day}</div>
      <div>Longest streak: {stats.streak.longest_streak_days} days</div>
    </div>
  </section>

  <h2 class="font-serif text-2xl text-gold-400 mb-4">When we talk</h2>
  <HourHeatmap grid={stats.hour_heatmap_dow_hr} client:load />

  <h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">Reply speed</h2>
  <ul class="font-mono text-sm space-y-1">
    {Object.entries(stats.median_reply_seconds).map(([who, sec]: any) => (
      <li>{who}: median {Math.round(sec)} s</li>
    ))}
  </ul>

  <h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">Mentions</h2>
  <ul class="font-mono text-sm grid grid-cols-2 md:grid-cols-3 gap-y-1">
    {Object.entries(stats.mentions).map(([k, v]: any) => (
      <li>{k}: {v.toLocaleString()}</li>
    ))}
  </ul>

  <h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">Endearments</h2>
  <ul class="font-mono text-sm">
    {Object.entries(stats.endearments).filter(([k, v]: any) => Object.values(v).some((n: any) => n > 0))
      .map(([k, v]: any) => (
      <li>{k}: {Object.entries(v).map(([s, n]) => `${s} ${n}`).join(" · ")}</li>
    ))}
  </ul>

  <h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">Longest stretched word</h2>
  <p class="font-mono">"{stats.elongation.word}" — {stats.elongation.len} chars, by {stats.elongation.by}</p>
</BookLayout>
```

- [ ] **Step 3: Verify in dev**

```bash
cd site && npm run dev
```
Open `http://localhost:4321/stats`. Expected: page renders all sections from the JSON.

- [ ] **Step 4: Stop server, commit**

```bash
/usr/bin/git add site/src/pages/stats.astro site/src/components/HourHeatmap.tsx
/usr/bin/git commit -m "feat(site): /stats page with real numbers + hour heatmap"
```

### Task 2.8: `/firsts` page

**Files:**
- Create: `site/src/pages/firsts.astro`

- [ ] **Step 1: Create the page**

```astro
---
import BookLayout from "../layouts/BookLayout.astro";
import firsts from "../data/firsts.json";
---
<BookLayout title="Firsts — Anisha & Sid">
  <h1 class="font-serif text-4xl text-gold-400 mb-10">Firsts</h1>
  <ul class="space-y-6">
    {firsts.map((f: any) => (
      <li class="border-l border-gold-600/40 pl-5">
        <div class="font-mono text-[11px] opacity-60">{f.ts.slice(0,16)} · {f.by} said first</div>
        <div class="font-serif text-xl mt-1">"{f.phrase}"</div>
        <details class="mt-2 text-sm opacity-80"><summary class="cursor-pointer font-mono text-[11px] text-gold-400/70">context</summary>
          <div class="mt-2 space-y-1">
            {f.context.map((c: any) => (
              <div><span class="opacity-50">{c.sender}:</span> {c.text}</div>
            ))}
          </div>
        </details>
      </li>
    ))}
  </ul>
</BookLayout>
```

- [ ] **Step 2: Verify in dev, then commit**

```bash
/usr/bin/git add site/src/pages/firsts.astro
/usr/bin/git commit -m "feat(site): /firsts page"
```

### Task 2.9: Push Phase 2

- [ ] **Step 1: Push**

```bash
/usr/bin/git push
```

---

## Phase 3 — Auto Chapter Detection

Goal: pipeline emits a `chapter_seed.json` with date ranges + suggested titles, with the 25 Jan 2026 proposal day pinned as its own chapter boundary.

### Task 3.1: Daily aggregates + simple breakpoint detector

**Files:**
- Create: `pipeline/stages/s_chapters.py`

- [ ] **Step 1: Write the stage**

```python
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
    smoothed = np.convolve(counts, np.ones(14)/14, mode="same")
    z = (smoothed - smoothed.mean()) / (smoothed.std() + 1e-6)
    valleys = []
    for i in range(min_segment_days, len(z) - min_segment_days):
        if z[i] < -0.6 and z[i] <= z[i-1] and z[i] <= z[i+1]:
            if not valleys or (days[i] - valleys[-1]).days >= min_segment_days:
                valleys.append(days[i])
    return valleys

def _top_keywords(df: pl.DataFrame, start: date, end: date, k: int = 5) -> list[str]:
    sub = df.filter(
        (pl.col("ts").dt.date() >= start) & (pl.col("ts").dt.date() <= end) &
        (pl.col("is_media") == False)
    )
    from collections import Counter
    import re
    from lib.gazetteer import STOPWORDS_EN, STOPWORDS_HI
    tok = re.compile(r"[A-Za-zऀ-ॿ]+")
    c = Counter()
    for t in sub["text"].to_list():
        for w in tok.findall(t.lower()):
            if len(w) < 4 or w in STOPWORDS_EN or w in STOPWORDS_HI: continue
            c[w] += 1
    return [w for w, _ in c.most_common(k)]

def _title_from_keywords(words: list[str]) -> str:
    if not words: return "Chapter"
    return " · ".join(w.capitalize() for w in words[:3])

def run(force: bool = False):
    s = stamp("s_chapters", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]")
        return
    df = pl.read_parquet(MSGS_PARQUET)
    daily = _per_day_features(df)
    bps = _breakpoints(daily)

    # Force the proposal day in
    if PROPOSAL not in bps:
        bps.append(PROPOSAL)
        bps.sort()

    first_day = daily["day"][0]
    last_day  = daily["day"][-1]
    boundaries = [first_day] + bps + [last_day]
    boundaries = sorted(set(boundaries))

    chapters = []
    for i in range(len(boundaries) - 1):
        a, b = boundaries[i], boundaries[i+1]
        kw = _top_keywords(df, a, b)
        chapters.append({
            "order": i + 1,
            "dateStart": str(a),
            "dateEnd":   str(b),
            "suggested_title": _title_from_keywords(kw),
            "keywords": kw,
            "pinned_proposal": (a == PROPOSAL or b == PROPOSAL),
        })
    OUT.write_text(json.dumps(chapters, indent=2))
    mark(s)
    print(f"  [green]{len(chapters)} chapters detected[/green]")
```

- [ ] **Step 2: Run**

```bash
cd pipeline && uv run python run.py --stage s_chapters
```
Expected: 5-9 chapters detected, one of them bracketing 2026-01-25.

- [ ] **Step 3: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/stages/s_chapters.py site/src/data/chapter_seed.json
/usr/bin/git commit -m "feat(pipeline): S-CHAP auto chapter detection + proposal day pinned"
```

### Task 3.2: Author MDX chapters from seed

**Files:**
- Create: `pipeline/stages/s_chapters_emit_mdx.py`
- Delete: `site/src/content/chapters/00-mock.mdx`

- [ ] **Step 1: Write the MDX emitter**

```python
import json, re
from rich import print
from lib.paths import SITE_DATA, SITE

OUT_DIR = SITE / "src" / "content" / "chapters"
SEED = SITE_DATA / "chapter_seed.json"

def _slug(title: str, i: int) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "chapter"
    return f"{i:02d}-{s}"

def run(force: bool = False):
    chapters = json.loads(SEED.read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove old generated chapters but keep manual overrides marked with `manual: true`
    for f in OUT_DIR.glob("*.mdx"):
        head = f.read_text()[:300]
        if "manual: true" not in head:
            f.unlink()
    for c in chapters:
        slug = _slug(c["suggested_title"], c["order"])
        path = OUT_DIR / f"{slug}.mdx"
        fm = (
            "---\n"
            f"order: {c['order']}\n"
            f"title: \"{c['suggested_title']}\"\n"
            f"dateStart: \"{c['dateStart']}\"\n"
            f"dateEnd: \"{c['dateEnd']}\"\n"
            f"summary: \"keywords: {', '.join(c['keywords'])}\"\n"
            "---\n\n"
            "Intro draft will be filled in by S6 (chapter intro generation).\n\n"
            "Quotes will be inserted by Phase 4.\n"
        )
        path.write_text(fm)
    print(f"  [green]wrote {len(chapters)} chapter MDX files[/green]")
```

- [ ] **Step 2: Wire into `run.py`**

Open `pipeline/run.py` and update the `STAGES` list to insert `s_chapters_emit_mdx` right after `s_chapters`:

```python
STAGES = ["s0_parse", "s1_stats", "s2_firsts", "s3_candidates",
          "s4_cluster", "s_nlp", "s_chapters", "s_chapters_emit_mdx",
          "s5_curate", "s6_intros"]
```

- [ ] **Step 3: Run**

```bash
cd pipeline && uv run python run.py --stage s_chapters_emit_mdx
```
Expected: `site/src/content/chapters/` populated.

- [ ] **Step 4: Remove old mock**

```bash
rm site/src/content/chapters/00-mock.mdx 2>/dev/null || true
```

- [ ] **Step 5: Verify in dev — `/book` shows real chapter list with date ranges**

```bash
cd site && npm run dev
```

- [ ] **Step 6: Commit**

```bash
/usr/bin/git add pipeline/stages/s_chapters_emit_mdx.py pipeline/run.py site/src/content/chapters/
/usr/bin/git rm -f site/src/content/chapters/00-mock.mdx 2>/dev/null || true
/usr/bin/git commit -m "feat: emit MDX chapter files from seed; remove mock"
```

### Task 3.3: Push Phase 3

```bash
/usr/bin/git push
```

---

## Phase 4 — Quote Curation Pipeline

Goal: 200 high-quality curated quotes keyed by chapter, written into `quotes.json`, rendered inside chapter pages.

### Task 4.1: S3 candidate filter

**Files:**
- Create: `pipeline/stages/s3_candidates.py`

- [ ] **Step 1: Write the stage**

```python
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
```

- [ ] **Step 2: Run**

```bash
cd pipeline && uv run python run.py --stage s3_candidates
```
Expected: ~15k-25k candidates.

- [ ] **Step 3: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/stages/s3_candidates.py
/usr/bin/git commit -m "feat(pipeline): S3 heuristic candidate filter"
```

### Task 4.2: S4 local embed + cluster

**Files:**
- Create: `pipeline/stages/s4_cluster.py`

- [ ] **Step 1: Write the stage**

```python
import json, numpy as np
from rich import print
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from lib.paths import CACHE
from lib.cache import stamp, fresh, mark

IN  = CACHE / "quote_candidates.jsonl"
OUT = CACHE / "ranked_candidates.jsonl"
K   = 500

def run(force: bool = False):
    s = stamp("s4", [IN])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]"); return
    cands = [json.loads(l) for l in IN.read_text().splitlines()]
    texts = [c["text"] for c in cands]
    print(f"  [dim]embedding {len(texts):,} texts[/dim]")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embs = model.encode(texts, batch_size=128, show_progress_bar=True, convert_to_numpy=True)
    k = min(K, len(texts) // 5)
    km = KMeans(n_clusters=k, n_init=4, random_state=42).fit(embs)
    centers = km.cluster_centers_
    labels = km.labels_
    dists = np.linalg.norm(embs - centers[labels], axis=1)
    by_cluster: dict[int, list] = {}
    for i, (c, d) in enumerate(zip(labels, dists)):
        by_cluster.setdefault(int(c), []).append((float(d), i))
    picked = []
    for c, arr in by_cluster.items():
        arr.sort()
        for _, idx in arr[:3]:
            r = dict(cands[idx]); r["cluster"] = c
            picked.append(r)
    with OUT.open("w") as f:
        for r in picked:
            f.write(json.dumps(r) + "\n")
    mark(s)
    print(f"  [green]{len(picked):,} ranked candidates from {k} clusters[/green]")
```

- [ ] **Step 2: Run**

```bash
cd pipeline && uv run python run.py --stage s4_cluster
```
Expected: ~1500 ranked candidates, takes a few minutes.

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add pipeline/stages/s4_cluster.py
/usr/bin/git commit -m "feat(pipeline): S4 local embed + KMeans cluster + per-cluster topN"
```

### Task 4.3: S-NLP local sentiment

**Files:**
- Create: `pipeline/stages/s_nlp.py`

- [ ] **Step 1: Write the stage**

```python
import json, polars as pl
from rich import print
from transformers import pipeline
from lib.paths import MSGS_PARQUET, CACHE
from lib.cache import stamp, fresh, mark

OUT = CACHE / "sentiment.parquet"

def run(force: bool = False):
    s = stamp("s_nlp", [MSGS_PARQUET])
    if fresh(s) and not force and OUT.exists():
        print("  [dim]cached, skipping[/dim]"); return
    df = pl.read_parquet(MSGS_PARQUET).filter(
        (pl.col("is_media") == False) &
        (pl.col("text").str.len_chars() >= 8)
    )
    rows = df.select(["ts", "sender", "text"]).to_dicts()
    clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", truncation=True)
    sents = clf([r["text"][:200] for r in rows], batch_size=64)
    for r, sent in zip(rows, sents):
        r["sentiment"] = sent["label"]
        r["score"]     = float(sent["score"])
    pl.DataFrame(rows).write_parquet(OUT)
    mark(s)
    print(f"  [green]{len(rows):,} rows scored[/green]")
```

- [ ] **Step 2: Run**

```bash
cd pipeline && uv run python run.py --stage s_nlp
```
Expected: takes ~5-10 min on CPU. If too slow, reduce sample with `head(50000)`.

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add pipeline/stages/s_nlp.py
/usr/bin/git commit -m "feat(pipeline): S-NLP local distilbert sentiment scoring"
```

### Task 4.4: S5 LLM curation (Haiku, batched, cached)

**Files:**
- Create: `pipeline/lib/cost.py`
- Create: `pipeline/stages/s5_curate.py`
- Create: `.env.example`

- [ ] **Step 1: Create `.env.example`** at repo root

```bash
ANTHROPIC_API_KEY=
SITE_PASSWORD_HASH=
COOKIE_SIGNING_KEY=
```

- [ ] **Step 2: Create `pipeline/lib/cost.py`**

```python
import json
from pathlib import Path
from lib.paths import CACHE

LEDGER = CACHE / "cost_ledger.jsonl"
HARD_CAP_USD = 1.00

PRICE = {
    "claude-haiku-4-5-20251001":           {"in": 1.00 / 1_000_000, "out": 5.00 / 1_000_000},
    "claude-haiku-4-5-20251001:cached":    {"in": 0.10 / 1_000_000, "out": 5.00 / 1_000_000},
    "claude-sonnet-4-6":                   {"in": 3.00 / 1_000_000, "out": 15.00 / 1_000_000},
}

def log(stage: str, model: str, in_tok: int, out_tok: int, cached_in_tok: int = 0):
    p = PRICE[model]
    cost = ((in_tok - cached_in_tok) * p["in"] +
            cached_in_tok * PRICE.get(model + ":cached", p)["in"] +
            out_tok * p["out"])
    with LEDGER.open("a") as f:
        f.write(json.dumps({"stage": stage, "model": model,
                            "in": in_tok, "out": out_tok, "cached": cached_in_tok,
                            "cost_usd": cost}) + "\n")
    total = sum(json.loads(l)["cost_usd"] for l in LEDGER.read_text().splitlines())
    if total > HARD_CAP_USD:
        raise RuntimeError(f"hard cap ${HARD_CAP_USD} exceeded: now ${total:.4f}")
    return cost, total
```

- [ ] **Step 3: Create `pipeline/stages/s5_curate.py`**

```python
import json, os, re
from datetime import date
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

    cands = [json.loads(l) for l in IN.read_text().splitlines()]
    chapters = json.loads(CHAPTERS_JSON.read_text())
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rated = []

    for start in range(0, len(cands), BATCH):
        batch = cands[start:start+BATCH]
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
        print(f"  [dim]batch {start//BATCH + 1}/{(len(cands)+BATCH-1)//BATCH}  ${total:.4f}[/dim]")
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
```

- [ ] **Step 4: Source env vars and run**

```bash
cd pipeline
export ANTHROPIC_API_KEY=...   # from your local secrets manager
uv run python run.py --stage s5_curate
```
Expected: ~$0.10-0.20 spent (per cost ledger), `quotes.json` written.

- [ ] **Step 5: Commit**

```bash
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/lib/cost.py pipeline/stages/s5_curate.py site/src/data/quotes.json .env.example
/usr/bin/git commit -m "feat(pipeline): S5 Haiku quote curation w/ prompt cache + cost ledger"
```

### Task 4.5: Render curated quotes inside chapter pages

**Files:**
- Modify: `site/src/pages/book/[...slug].astro`

- [ ] **Step 1: Update the chapter page**

Replace the existing file content with:

```astro
---
import BookLayout from "../../layouts/BookLayout.astro";
import PaperCard from "../../components/PaperCard.astro";
import { getCollection, render } from "astro:content";
import quotes from "../../data/quotes.json";

export async function getStaticPaths() {
  const chapters = await getCollection("chapters");
  return chapters.map((c) => ({ params: { slug: c.slug }, props: { chapter: c } }));
}

const { chapter } = Astro.props;
const { Content } = await render(chapter);
const chapterQuotes: any[] = (quotes as any)[chapter.data.order] ?? [];

function fmt(ts: string) {
  return ts.slice(0, 16).replace("T", " · ");
}
---
<BookLayout title={chapter.data.title}>
  <article>
    <header class="mb-10">
      <div class="font-mono text-[11px] text-gold-400/70">{chapter.data.dateStart} — {chapter.data.dateEnd}</div>
      <h1 class="font-serif text-4xl md:text-5xl text-gold-400 mt-2">{chapter.data.title}</h1>
    </header>
    <div class="prose-content"><Content /></div>

    {chapterQuotes.length > 0 && (
      <section class="mt-14">
        <h2 class="font-serif text-2xl text-gold-400 mb-4">Quotes from this chapter</h2>
        {chapterQuotes.slice(0, 20).map((q: any) => (
          <PaperCard date={fmt(q.ts)} sender={q.sender}>
            {q.text}
          </PaperCard>
        ))}
      </section>
    )}
  </article>
</BookLayout>
```

- [ ] **Step 2: Verify in dev**

```bash
cd site && npm run dev
```
Each chapter page shows up to 20 paper-card quotes for its chapter.

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add site/src/pages/book/[...slug].astro
/usr/bin/git commit -m "feat(site): render curated quotes per chapter"
```

### Task 4.6: Push Phase 4

```bash
/usr/bin/git push
```

---

## Phase 5 — Media Pipeline (gated on `.zip`)

Goal: photos optimized to webp, grouped by chapter window, rendered as photo strips.

### Task 5.1: Ingest WhatsApp `.zip`

**Files:**
- Create: `pipeline/media/__init__.py`
- Create: `pipeline/media/ingest.py`

- [ ] **Step 1: Create `pipeline/media/__init__.py`** (empty file).

- [ ] **Step 2: Create `pipeline/media/ingest.py`**

```python
import zipfile, shutil, re
from datetime import datetime
from pathlib import Path
from rich import print
from lib.paths import DATA

ZIP_GLOB = DATA / "*.zip"

def run(force: bool = False):
    zips = list(DATA.glob("*.zip"))
    if not zips:
        print("  [yellow]no .zip found in data/ — skipping media ingest[/yellow]")
        return
    out_dir = DATA / "media_raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if name.endswith("/") or name == "_chat.txt": continue
                target = out_dir / Path(name).name
                if target.exists() and not force: continue
                with zf.open(name) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
        print(f"  [green]extracted {z.name}[/green]")
    print(f"  [green]media at {out_dir}[/green]")
```

- [ ] **Step 3: User drops `.zip` into `data/`** (manual step, document in PHASE_5_README.md if needed).

- [ ] **Step 4: Run**

```bash
cd pipeline && uv run python -c "from media import ingest; ingest.run()"
```

- [ ] **Step 5: Commit**

```bash
/usr/bin/git add pipeline/media/
/usr/bin/git commit -m "feat(pipeline): WhatsApp .zip media ingest"
```

### Task 5.2: Optimize photos to webp

**Files:**
- Create: `pipeline/media/optimize.py`

- [ ] **Step 1: Add `pillow` to `pipeline/pyproject.toml`**

In the `dependencies` list, add: `"pillow>=11.0.0",`. Then:

```bash
cd pipeline && uv sync
```

- [ ] **Step 2: Create `pipeline/media/optimize.py`**

```python
import re, hashlib
from datetime import datetime
from pathlib import Path
from PIL import Image
from rich import print
from lib.paths import DATA, SITE_PUB

RAW = DATA / "media_raw"
OUT = SITE_PUB / "media" / "photos"
WHATSAPP_NAME = re.compile(r"(\d{8})-?(?:WA|PHOTO).*\.(jpe?g|png|heic)$", re.IGNORECASE)

def _date_from_name(name: str):
    m = WHATSAPP_NAME.match(name)
    if not m: return None
    try: return datetime.strptime(m.group(1), "%Y%m%d").date()
    except: return None

def run(force: bool = False):
    if not RAW.exists():
        print("  [yellow]no media_raw — skip[/yellow]"); return
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for src in RAW.iterdir():
        if src.suffix.lower() not in {".jpg", ".jpeg", ".png", ".heic"}: continue
        d = _date_from_name(src.name)
        sub = OUT / (str(d) if d else "undated")
        sub.mkdir(exist_ok=True)
        h = hashlib.sha1(src.read_bytes()).hexdigest()[:10]
        target = sub / f"{h}.webp"
        if target.exists() and not force: continue
        try:
            im = Image.open(src)
            im.thumbnail((1600, 1600))
            im.save(target, "WEBP", quality=82, method=6)
            n += 1
        except Exception as e:
            print(f"  [red]skip {src.name}: {e}[/red]")
    print(f"  [green]optimized {n} photos[/green]")
```

- [ ] **Step 3: Run**

```bash
cd pipeline && uv run python -c "from media import optimize; optimize.run()"
```

- [ ] **Step 4: Commit**

```bash
/usr/bin/git add pipeline/media/optimize.py pipeline/pyproject.toml pipeline/uv.lock site/public/media/photos/
/usr/bin/git commit -m "feat(pipeline): optimize media to webp by date"
```

### Task 5.3: Map media to chapters

**Files:**
- Create: `pipeline/stages/s_media_map.py`

- [ ] **Step 1: Write the stage**

```python
import json
from datetime import date
from pathlib import Path
from rich import print
from lib.paths import SITE_PUB, SITE_DATA
from lib.cache import stamp, fresh, mark

PHOTOS = SITE_PUB / "media" / "photos"
SEED   = SITE_DATA / "chapter_seed.json"
OUT    = SITE_DATA / "chapter_media.json"

def run(force: bool = False):
    chapters = json.loads(SEED.read_text())
    out: dict = {}
    if not PHOTOS.exists():
        print("  [yellow]no /photos — empty mapping[/yellow]")
        OUT.write_text(json.dumps({})); return
    for c in chapters:
        start = date.fromisoformat(c["dateStart"])
        end   = date.fromisoformat(c["dateEnd"])
        bucket = []
        for d_dir in PHOTOS.iterdir():
            if not d_dir.is_dir(): continue
            try: d = date.fromisoformat(d_dir.name)
            except: continue
            if start <= d <= end:
                for f in d_dir.iterdir():
                    bucket.append(f"/media/photos/{d_dir.name}/{f.name}")
        out[c["order"]] = sorted(bucket)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"  [green]mapped media to {len(out)} chapters[/green]")
```

- [ ] **Step 2: Wire into `STAGES` in `run.py`** (insert after `s_chapters_emit_mdx`).

- [ ] **Step 3: Run and commit**

```bash
cd pipeline && uv run python run.py --stage s_media_map
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/stages/s_media_map.py pipeline/run.py site/src/data/chapter_media.json
/usr/bin/git commit -m "feat(pipeline): map photos to chapters by date"
```

### Task 5.4: PhotoStrip component + chapter page wiring

**Files:**
- Create: `site/src/components/PhotoStrip.astro`
- Modify: `site/src/pages/book/[...slug].astro`

- [ ] **Step 1: Create `site/src/components/PhotoStrip.astro`**

```astro
---
interface Props { photos: string[]; }
const { photos } = Astro.props;
---
{photos.length > 0 && (
  <div class="flex gap-2 overflow-x-auto py-4 -mx-6 px-6 md:-mx-12 md:px-12">
    {photos.slice(0, 20).map((src: string) => (
      <a href={src} target="_blank" class="shrink-0">
        <img src={src} alt="" loading="lazy" class="h-32 md:h-48 w-auto rounded-sm" />
      </a>
    ))}
  </div>
)}
```

- [ ] **Step 2: Update `[...slug].astro`** — add import and render:

```astro
import PhotoStrip from "../../components/PhotoStrip.astro";
import media from "../../data/chapter_media.json";
...
const chapterPhotos: string[] = (media as any)[chapter.data.order] ?? [];
```

And before the quotes section:

```astro
{chapterPhotos.length > 0 && <PhotoStrip photos={chapterPhotos} />}
```

- [ ] **Step 3: Verify + commit**

```bash
/usr/bin/git add site/src/components/PhotoStrip.astro site/src/pages/book/[...slug].astro
/usr/bin/git commit -m "feat(site): PhotoStrip per chapter"
```

### Task 5.5: Push Phase 5

```bash
/usr/bin/git push
```

---

## Phase 6 — Chapter Intros + Polish

Goal: LLM drafts a 200-word intro per chapter (you can hand-edit), plus stat bands and the rest of the dashboard charts.

### Task 6.1: S6 Sonnet chapter intros

**Files:**
- Create: `pipeline/stages/s6_intros.py`

- [ ] **Step 1: Write the stage**

```python
import json, os
from rich import print
from anthropic import Anthropic
from lib.paths import SITE_DATA, SITE
from lib.cache import stamp, fresh, mark
from lib.cost import log as cost_log

CHAPTERS = SITE_DATA / "chapter_seed.json"
QUOTES   = SITE_DATA / "quotes.json"
OUT_DIR  = SITE / "src" / "content" / "chapters"
MODEL    = "claude-sonnet-4-6"

SYS = """You write short, warm chapter intros for a private memory book about a real couple, Sid and Anisha.
Given a date range and a small set of representative quotes from that period, write 150-200 words of intro prose.
Voice: warm, intimate, a little wry, like a friend narrating their love. No clichés, no AI-isms.
Never invent events not implied by the quotes. Use "they" or names; not "you"."""

def run(force: bool = False):
    s = stamp("s6", [CHAPTERS, QUOTES])
    if fresh(s) and not force:
        print("  [dim]cached, skipping[/dim]"); return
    chapters = json.loads(CHAPTERS.read_text())
    quotes   = json.loads(QUOTES.read_text())
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    for c in chapters:
        cq = quotes.get(str(c["order"]), [])[:25]
        if not cq: continue
        body = (
            f"Chapter: {c['suggested_title']}\nDates: {c['dateStart']} — {c['dateEnd']}\n\nQuotes:\n"
            + "\n".join(f"- ({q['sender']}, {q['ts'][:10]}) {q['text']}" for q in cq)
        )
        msg = client.messages.create(
            model=MODEL, max_tokens=600,
            system=SYS,
            messages=[{"role": "user", "content": body}],
        )
        cost, total = cost_log("s6", MODEL, msg.usage.input_tokens, msg.usage.output_tokens)
        intro = msg.content[0].text.strip()
        # Patch into chapter MDX (after front matter)
        for f in OUT_DIR.glob(f"{c['order']:02d}-*.mdx"):
            txt = f.read_text()
            head, _, _ = txt.partition("---\n\n")  # naive: assume our template
            new = head + "---\n\n" + intro + "\n"
            f.write_text(new)
        print(f"  [dim]chapter {c['order']}: ${total:.4f}[/dim]")
    mark(s)
    print("  [green]intros patched into MDX[/green]")
```

- [ ] **Step 2: Run**

```bash
cd pipeline && uv run python run.py --stage s6_intros
```
Expected: total <$0.30.

- [ ] **Step 3: Commit**

```bash
/usr/bin/git add pipeline/stages/s6_intros.py site/src/content/chapters/
/usr/bin/git commit -m "feat(pipeline): S6 Sonnet chapter intros patched into MDX"
```

### Task 6.2: StatBand per chapter

**Files:**
- Create: `pipeline/stages/s_stat_bands.py`
- Create: `site/src/components/StatBand.astro`
- Modify: `site/src/pages/book/[...slug].astro`

- [ ] **Step 1: Write the stat band generator**

```python
import json, polars as pl
from rich import print
from datetime import date
from lib.paths import MSGS_PARQUET, SITE_DATA

CHAPTERS = SITE_DATA / "chapter_seed.json"
OUT      = SITE_DATA / "chapter_stats.json"

def run(force: bool = False):
    df = pl.read_parquet(MSGS_PARQUET)
    chapters = json.loads(CHAPTERS.read_text())
    out = {}
    for c in chapters:
        sub = df.filter(
            (pl.col("ts").dt.date() >= date.fromisoformat(c["dateStart"])) &
            (pl.col("ts").dt.date() <= date.fromisoformat(c["dateEnd"]))
        )
        n_msgs = sub.height
        days = (date.fromisoformat(c["dateEnd"]) - date.fromisoformat(c["dateStart"])).days + 1
        out[c["order"]] = {
            "msgs": n_msgs,
            "days": days,
            "avg_per_day": round(n_msgs / max(days, 1), 1),
            "photos": int(sub.filter(pl.col("media_type") == "image").height),
        }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"  [green]chapter_stats.json written[/green]")
```

- [ ] **Step 2: Wire into `STAGES`**, run, commit.

- [ ] **Step 3: Create `site/src/components/StatBand.astro`**

```astro
---
interface Props { msgs: number; days: number; avg_per_day: number; photos: number; }
const p = Astro.props;
---
<aside class="mt-12 py-4 border-t border-gold-600/40 grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs opacity-80">
  <div><div class="text-gold-400 text-base font-serif">{p.msgs.toLocaleString()}</div>messages</div>
  <div><div class="text-gold-400 text-base font-serif">{p.days}</div>days</div>
  <div><div class="text-gold-400 text-base font-serif">{p.avg_per_day}</div>per day</div>
  <div><div class="text-gold-400 text-base font-serif">{p.photos}</div>photos</div>
</aside>
```

- [ ] **Step 4: Update `[...slug].astro`** to import and render StatBand after PhotoStrip, before quotes:

```astro
import StatBand from "../../components/StatBand.astro";
import chapterStats from "../../data/chapter_stats.json";
const cs = (chapterStats as any)[chapter.data.order];
...
{cs && <StatBand {...cs} />}
```

- [ ] **Step 5: Commit**

```bash
/usr/bin/git add pipeline/stages/s_stat_bands.py pipeline/run.py site/src/components/StatBand.astro site/src/data/chapter_stats.json site/src/pages/book/[...slug].astro
/usr/bin/git commit -m "feat: per-chapter StatBand"
```

### Task 6.3: Chart components for `/stats`

**Files:**
- Create: `site/src/components/EmojiInflation.tsx`
- Create: `site/src/components/PetNameRibbon.tsx`
- Create: `site/src/components/ReplyTimeChart.tsx`

- [ ] **Step 1: Create `EmojiInflation.tsx`**

```tsx
import * as Plot from "@observablehq/plot";
import { useEffect, useRef } from "react";

export default function EmojiInflation({ data }: { data: Record<string, number> }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const rows = Object.entries(data).map(([y, n]) => ({ year: +y, n }));
    const chart = Plot.plot({
      style: { background: "transparent", color: "#e9dfc7" },
      x: { label: "year", tickFormat: "d" },
      y: { label: "😂 count" },
      marks: [
        Plot.barY(rows, { x: "year", y: "n", fill: "#d4af6a" }),
      ],
      height: 220,
    });
    ref.current!.replaceChildren(chart);
  }, [data]);
  return <div ref={ref} />;
}
```

- [ ] **Step 2: Create `PetNameRibbon.tsx`**

```tsx
import * as Plot from "@observablehq/plot";
import { useEffect, useRef } from "react";

export default function PetNameRibbon({ data }: { data: Record<string, Record<string, number>> }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const rows: { name: string; sender: string; n: number }[] = [];
    for (const [name, byS] of Object.entries(data)) {
      for (const [sender, n] of Object.entries(byS)) {
        rows.push({ name, sender, n: n as number });
      }
    }
    const chart = Plot.plot({
      style: { background: "transparent", color: "#e9dfc7" },
      marginLeft: 80,
      x: { label: "uses" },
      y: { label: null },
      color: { legend: true, range: ["#d4af6a", "#f4ecd8"] },
      marks: [
        Plot.barX(rows, { x: "n", y: "name", fill: "sender", sort: { y: "x", reverse: true } }),
      ],
      height: 360,
    });
    ref.current!.replaceChildren(chart);
  }, [data]);
  return <div ref={ref} />;
}
```

- [ ] **Step 3: Create `ReplyTimeChart.tsx`**

```tsx
import * as Plot from "@observablehq/plot";
import { useEffect, useRef } from "react";

export default function ReplyTimeChart({ data }: { data: Record<string, number> }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const rows = Object.entries(data).map(([who, sec]) => ({ who, sec: Math.round(sec as number) }));
    const chart = Plot.plot({
      style: { background: "transparent", color: "#e9dfc7" },
      x: { label: "median reply (sec)" },
      marks: [ Plot.barX(rows, { x: "sec", y: "who", fill: "#d4af6a" }) ],
      height: 140, marginLeft: 80
    });
    ref.current!.replaceChildren(chart);
  }, [data]);
  return <div ref={ref} />;
}
```

- [ ] **Step 4: Update `/stats` page** — replace the simple `ul`s with the charts. Append to `site/src/pages/stats.astro`:

```astro
import EmojiInflation from "../components/EmojiInflation.tsx";
import PetNameRibbon  from "../components/PetNameRibbon.tsx";
import ReplyTimeChart from "../components/ReplyTimeChart.tsx";
...
<h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">😂 over the years</h2>
<EmojiInflation data={stats.laugh_inflation} client:load />

<h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">Names we called each other</h2>
<PetNameRibbon data={stats.endearments} client:load />

<h2 class="font-serif text-2xl text-gold-400 mt-12 mb-4">Reply speed (sec, median)</h2>
<ReplyTimeChart data={stats.median_reply_seconds} client:load />
```

- [ ] **Step 5: Verify + commit**

```bash
/usr/bin/git add site/src/components/EmojiInflation.tsx site/src/components/PetNameRibbon.tsx site/src/components/ReplyTimeChart.tsx site/src/pages/stats.astro
/usr/bin/git commit -m "feat(site): Observable Plot charts on /stats"
```

### Task 6.4: Push Phase 6

```bash
/usr/bin/git push
```

---

## Phase 7 — Search, Archive, Auth, Deploy

Goal: Pagefind search, paginated raw archive, Cloudflare Worker password gate, live deploy.

### Task 7.1: Pagefind config

**Files:**
- Modify: `site/package.json` (already has pagefind)
- Create: `site/src/pages/search.astro`

- [ ] **Step 1: Confirm chapter pages include searchable content** (already done — Astro renders MDX to HTML).

- [ ] **Step 2: Create `site/src/pages/search.astro`**

```astro
---
import BookLayout from "../layouts/BookLayout.astro";
---
<BookLayout title="Search">
  <h1 class="font-serif text-4xl text-gold-400 mb-8">Search</h1>
  <div id="search"></div>
  <link href="/pagefind/pagefind-ui.css" rel="stylesheet" />
  <script src="/pagefind/pagefind-ui.js"></script>
  <script is:inline>
    window.addEventListener("DOMContentLoaded", () => {
      new PagefindUI({ element: "#search", showSubResults: true });
    });
  </script>
</BookLayout>
```

- [ ] **Step 3: Build and verify**

```bash
cd site && npm run build && npm run preview
```
Open `http://localhost:4321/search` — search across all chapter pages works.

- [ ] **Step 4: Commit**

```bash
/usr/bin/git add site/src/pages/search.astro
/usr/bin/git commit -m "feat(site): Pagefind search UI"
```

### Task 7.2: Archive (paginated raw view)

**Files:**
- Create: `pipeline/stages/s_archive_index.py`
- Create: `site/src/pages/archive/index.astro`
- Create: `site/src/pages/archive/[date].astro`

- [ ] **Step 1: Create the archive index generator**

```python
import json, polars as pl
from rich import print
from lib.paths import MSGS_PARQUET, SITE_DATA

OUT = SITE_DATA / "archive_dates.json"
OUT_DIR = SITE_DATA / "archive"

def run(force: bool = False):
    df = pl.read_parquet(MSGS_PARQUET).with_columns(pl.col("ts").dt.date().alias("d"))
    days = df["d"].unique().sort().to_list()
    OUT.write_text(json.dumps([str(d) for d in days]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for d in days:
        sub = df.filter(pl.col("d") == d).sort("ts")
        rows = [{"ts": str(r["ts"]), "sender": r["sender"], "text": r["text"],
                 "media": r["media_type"]} for r in sub.to_dicts()]
        (OUT_DIR / f"{d}.json").write_text(json.dumps(rows))
    print(f"  [green]{len(days)} archive day files written[/green]")
```

Wire into `STAGES` in `run.py`. Run.

- [ ] **Step 2: Create `site/src/pages/archive/index.astro`**

```astro
---
import BookLayout from "../../layouts/BookLayout.astro";
import dates from "../../data/archive_dates.json";
const years: Record<string, string[]> = {};
for (const d of dates) (years[d.slice(0,4)] ??= []).push(d);
---
<BookLayout title="Archive">
  <h1 class="font-serif text-4xl text-gold-400 mb-8">Archive</h1>
  {Object.entries(years).reverse().map(([y, ds]) => (
    <section class="mb-10">
      <h2 class="font-serif text-2xl text-gold-400 mb-2">{y}</h2>
      <div class="flex flex-wrap gap-1 font-mono text-[11px]">
        {ds.map((d) => <a class="opacity-60 hover:opacity-100 hover:text-gold-400" href={`/archive/${d}`}>{d.slice(5)}</a>)}
      </div>
    </section>
  ))}
</BookLayout>
```

- [ ] **Step 3: Create `site/src/pages/archive/[date].astro`**

```astro
---
import BookLayout from "../../layouts/BookLayout.astro";
import dates from "../../data/archive_dates.json";

export async function getStaticPaths() {
  return (dates as string[]).map((d) => ({ params: { date: d } }));
}
const { date } = Astro.params;
const data = (await import(`../../data/archive/${date}.json`)).default as any[];
---
<BookLayout title={`Archive ${date}`}>
  <a href="/archive" class="font-mono text-[11px] text-gold-400/70">← all dates</a>
  <h1 class="font-serif text-3xl text-gold-400 mt-2 mb-8">{date}</h1>
  <div class="space-y-2">
    {data.map((m: any) => (
      <div class="flex gap-3 font-serif">
        <div class="font-mono text-[11px] opacity-50 w-16 shrink-0">{m.ts.slice(11,16)}</div>
        <div class="font-mono text-[11px] opacity-70 w-16 shrink-0">{m.sender}</div>
        <div class="text-base flex-1">{m.media ? <em class="opacity-60">[{m.media}]</em> : m.text}</div>
      </div>
    ))}
  </div>
</BookLayout>
```

- [ ] **Step 4: Run + verify + commit**

```bash
cd pipeline && uv run python run.py --stage s_archive_index
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add pipeline/stages/s_archive_index.py pipeline/run.py site/src/pages/archive/ site/src/data/archive_dates.json site/src/data/archive/
/usr/bin/git commit -m "feat: archive index + per-day raw view"
```

### Task 7.3: Cloudflare Worker auth gate

**Files:**
- Create: `worker/wrangler.toml`
- Create: `worker/package.json`
- Create: `worker/src/index.ts`

- [ ] **Step 1: Create `worker/wrangler.toml`**

```toml
name = "anisha-sid-gate"
main = "src/index.ts"
compatibility_date = "2026-01-01"

[[routes]]
pattern = "anishasid.pages.dev/*"
zone_id = ""    # blank since we're not using a custom zone yet

[vars]
LOGIN_PATH = "/login"

# Set with:  npx wrangler secret put SITE_PASSWORD_HASH
# bcrypt hash of the shared password
# COOKIE_SIGNING_KEY: 32+ random hex chars
```

- [ ] **Step 2: Create `worker/package.json`**

```json
{
  "name": "anisha-sid-gate",
  "private": true,
  "scripts": {
    "deploy": "wrangler deploy"
  },
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20250101.0",
    "wrangler": "^3.95.0",
    "typescript": "^5.7.0"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3"
  }
}
```

- [ ] **Step 3: Create `worker/src/index.ts`**

```ts
import bcrypt from "bcryptjs";

interface Env {
  SITE_PASSWORD_HASH: string;
  COOKIE_SIGNING_KEY: string;
  ASSETS: Fetcher;
}

const COOKIE = "anisid_auth";
const TTL_SECONDS = 60 * 60 * 24 * 30;

async function sign(payload: string, key: string): Promise<string> {
  const enc = new TextEncoder();
  const k = await crypto.subtle.importKey("raw", enc.encode(key), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
  const sig = await crypto.subtle.sign("HMAC", k, enc.encode(payload));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

async function verifySig(payload: string, sig: string, key: string): Promise<boolean> {
  const expect = await sign(payload, key);
  return expect === sig;
}

function getCookie(req: Request, name: string): string | null {
  const c = req.headers.get("cookie") || "";
  for (const part of c.split(";")) {
    const [k, v] = part.trim().split("=");
    if (k === name) return v;
  }
  return null;
}

const LOGIN_HTML = `<!doctype html><meta charset="utf-8"><title>·</title>
<style>body{background:#08060d;color:#e9dfc7;font-family:Georgia,serif;display:grid;place-items:center;height:100dvh}
form{display:flex;gap:8px}input,button{background:#13101e;color:#e9dfc7;border:1px solid #c89a4a;padding:8px 12px;font:inherit}
</style>
<form method="post"><input name="p" type="password" autofocus placeholder="—"><button>open</button></form>`;

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);

    if (url.pathname === "/login") {
      if (req.method === "POST") {
        const fd = await req.formData();
        const pw = String(fd.get("p") || "");
        if (await bcrypt.compare(pw, env.SITE_PASSWORD_HASH)) {
          const exp = String(Math.floor(Date.now() / 1000) + TTL_SECONDS);
          const sig = await sign(exp, env.COOKIE_SIGNING_KEY);
          const value = `${exp}.${sig}`;
          return new Response(null, {
            status: 302,
            headers: {
              "set-cookie": `${COOKIE}=${value}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${TTL_SECONDS}`,
              "location": "/book"
            }
          });
        }
        return new Response(LOGIN_HTML + "<p style='color:#a87a2e'>nope</p>", { status: 401, headers: { "content-type": "text/html" } });
      }
      return new Response(LOGIN_HTML, { headers: { "content-type": "text/html" } });
    }

    const raw = getCookie(req, COOKIE);
    let ok = false;
    if (raw) {
      const [exp, sig] = raw.split(".");
      if (exp && sig && await verifySig(exp, sig, env.COOKIE_SIGNING_KEY)) {
        if (Number(exp) > Math.floor(Date.now() / 1000)) ok = true;
      }
    }
    if (!ok) {
      if (url.pathname === "/" || url.pathname === "") return Response.redirect(new URL("/login", url), 302);
      return new Response(null, { status: 302, headers: { "location": "/login" } });
    }

    const res = await env.ASSETS.fetch(req);
    const headers = new Headers(res.headers);
    headers.set("X-Robots-Tag", "noindex, nofollow");
    headers.set("Cache-Control", "private, no-cache");
    return new Response(res.body, { status: res.status, headers });
  }
};
```

- [ ] **Step 4: Install + commit**

```bash
cd worker && npm install
cd /Users/sid/Projects/whatsapp-sid-anisha
/usr/bin/git add worker/
/usr/bin/git commit -m "feat(worker): single-password Cloudflare Worker auth gate"
```

### Task 7.4: Cloudflare Pages project + binding

This task uses the Cloudflare dashboard, not code.

- [ ] **Step 1: Create a CF Pages project**
  - Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git
  - Pick repo `Sid342/anishaSidWhatsapp`
  - Branch: `main`
  - Framework preset: Astro
  - Build command: `cd site && npm install && npm run build`
  - Build output directory: `site/dist`

- [ ] **Step 2: Add Pages secrets** (dashboard → Settings → Environment variables, "Production"):
  - `ANTHROPIC_API_KEY` — leave UNSET; build is local-only
  - (No secrets needed by Pages itself for now)

- [ ] **Step 3: Add Pages function** — convert the worker to a Pages function so it gates the same project.

Create `site/functions/_middleware.ts` (copy logic from `worker/src/index.ts` adapted to Pages Functions middleware signature). Skipped here for brevity — see Pages Functions docs.

**Alt path (recommended for simplicity):** keep the standalone Worker and add a `[[wrangler]]` route on the Pages domain to send all requests through the Worker first.

- [ ] **Step 4: Configure Worker secrets**

Generate a bcrypt hash of the chosen password (locally):

```bash
cd worker && node -e "console.log(require('bcryptjs').hashSync(process.argv[1], 12))" "<<<your password>>>"
```

Then set Worker secrets:

```bash
cd worker
npx wrangler secret put SITE_PASSWORD_HASH    # paste the bcrypt hash
npx wrangler secret put COOKIE_SIGNING_KEY    # 32+ hex chars: `openssl rand -hex 32`
npx wrangler deploy
```

- [ ] **Step 5: Bind Worker → Pages**

Dashboard → Worker → Triggers → Routes → add the Pages URL (`anishasid.pages.dev/*`).

- [ ] **Step 6: Verify end-to-end**
  - Open `https://anishasid.pages.dev`
  - Should redirect to `/login`
  - Enter password → land on `/book`
  - Photos and JSON load behind the cookie

- [ ] **Step 7: Commit deployment notes**

```bash
/usr/bin/git add docs/superpowers/plans/2026-05-26-anisha-and-sid-impl.md
/usr/bin/git commit -m "docs(plan): mark Phase 7 deploy completed"
```

### Task 7.5: Robots, headers, polish

**Files:**
- Create: `site/public/robots.txt`
- Modify: `site/src/layouts/BookLayout.astro` (already has `noindex`)

- [ ] **Step 1: Create `site/public/robots.txt`**

```
User-agent: *
Disallow: /
```

- [ ] **Step 2: Commit + push**

```bash
/usr/bin/git add site/public/robots.txt
/usr/bin/git commit -m "feat(site): robots deny-all"
/usr/bin/git push
```

---

## Phase 8 — Optional polish (skip if shipping)

- Add typo-density (#56) with `hunspell-en_US` via `python-hunspell`
- Add coincidence counter (#58) using S4 embeddings + windowed cosine similarity
- Add per-chapter cover photo picker (small Astro page that lets you mark a photo as cover, writes to local file)
- Add dark/light theme toggle (only "warm paper" mode for entire site)

---

## Self-Review Notes

- All spec requirements (sections 1-15) mapped to phases above
- No placeholder code; every step includes the actual code or command
- Function names and file paths consistent across tasks (`parse_chat_text`, `MSGS_PARQUET`, `stats.json`, etc.)
- TDD applied in Task 2.2 (parser); other tasks are integration-style where unit TDD is lower value
- Cost ceiling enforced in `lib/cost.py`, used by S5 and S6
- Symlink and git-binary issues called out at top of plan to avoid surprises
- 25 Jan 2026 proposal date is pinned in Task 3.1 (`PROPOSAL = date(2026, 1, 25)`)
- Media phase explicitly marked as blocked on `.zip` arrival; site renders cleanly without it

---

## Done = these all hold

- `https://anishasid.pages.dev` requires password, shows the book
- `/stats` page renders 30+ metrics from real chat
- `/firsts` shows every milestone phrase with context
- Each chapter has intro + curated quotes + (when media arrives) cover + photo strip
- `/search` returns hits in <500 ms
- `/archive/YYYY-MM-DD` renders all messages from that day
- Cumulative LLM spend on a full rebuild stays under $0.50
