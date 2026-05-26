# Anisha & Sid — Private Chaptered-Book Memory Site

**Date:** 2026-05-26
**Author:** Sid (with Claude)
**Status:** Design locked, awaiting implementation plan

---

## 1. Purpose

A private, password-gated website that turns nine years of WhatsApp chat (2017-07-19 → 2026-05-08, ~464,340 messages) between Sid and Anisha into a chaptered book of their love story, complete with curated quotes, full searchable archive, "first-X" moments, and a fun statistics dashboard. Built as a random-surprise gift, post-proposal (proposal already happened in January 2026), with no fixed reveal date.

## 2. Scope and Non-Goals

**In scope**
- Static site with chaptered-book navigation
- Auto-detected chapters from chat data, manually editable
- Curated quote highlights (~10-30 per chapter)
- Full-text searchable raw archive
- First-X moments page
- Stats dashboard (60+ metrics, see Appendix A)
- Photo galleries per chapter from WhatsApp media export
- Single-shared-password gate, real server-side auth
- Hosted on Cloudflare Pages, repo on GitHub

**Out of scope (now)**
- Multi-user accounts, per-user notes/reactions
- Live editing UI / CMS
- Mobile app
- Real-time chat continuation
- Public-facing version
- Analytics dashboards beyond stats page
- I18N
- Email/PIN auth flows

## 3. Inputs Required from User

| Input | Status |
|---|---|
| `_chat.txt` WhatsApp export | Provided: `/Users/sid/Downloads/_chat.txt` (25 MB, 482k lines) |
| Original WhatsApp `.zip` with media files | **Pending** — Phase 5 (media pipeline) blocked until provided; chapters render text-only until then |
| Exact proposal date in January 2026 | **25 January 2026** (user-pinned chapter boundary) |
| ~8 chapter cover photos | Deferred — picked after auto-detect + media `.zip` arrival |
| Site password (shared with Anisha) | Deferred — Worker secret set at Phase 7 deploy time |
| Custom domain (optional) | Default to `*.pages.dev` (no custom domain) |

## 4. Architecture

```
┌───────────────────────────────────────────────┐
│  Source (gitignored)                          │
│  /data/_chat.txt + /data/media/               │
└──────────────────┬────────────────────────────┘
                   │  build-time only
                   ▼
┌───────────────────────────────────────────────┐
│  Python pipeline (local)                      │
│  S0 parse → S1 stats → S2 firsts → S3 cands   │
│  → S4 local embed/cluster → S-NLP             │
│  → S5 Haiku curate → S6 Sonnet intros         │
│  Outputs: site/data/*.json, site/public/media │
└──────────────────┬────────────────────────────┘
                   │  committed JSON + webps
                   ▼
┌───────────────────────────────────────────────┐
│  Astro site (Vite/React/MDX/Tailwind)         │
│  pages: /, /book, /book/[slug], /search,      │
│  /stats, /archive/[date], /firsts             │
│  Search via Pagefind, charts via Observable   │
└──────────────────┬────────────────────────────┘
                   │  git push to GitHub
                   ▼
┌───────────────────────────────────────────────┐
│  GitHub: Sid342/anishaSidWhatsapp (private)   │
│       │ webhook                               │
│       ▼                                       │
│  Cloudflare Pages auto-deploy                 │
│  + Cloudflare Worker (auth gate)              │
│  Site at *.pages.dev                          │
└───────────────────────────────────────────────┘
```

**Key invariant:** the LLM only sees pre-filtered, embedded, and clustered candidates — never raw chat at scale. The deployed site itself runs zero LLM at runtime.

## 5. Content Pipeline

| Stage | Purpose | Tokens | Tooling |
|---|---|---|---|
| S0 | Parse `_chat.txt` → `messages.parquet`. Multi-line coalesce, dedup, media-omitted classification, URL extraction. | 0 | Python regex + polars |
| S1 | Core stats: counts, cadence, response times, vocabulary, emoji, punctuation, nicknames, mentions, milestone counters, time-of-relationship math. (Metrics #1-49, 51-57, see Appendix A.) | 0 | polars + emoji lib + hunspell |
| S2 | First-X extractor: first occurrence + ±5-msg context window for keyword list (love, miss, baby, shaadi, ring, yes, etc.). | 0 | regex |
| S3 | Quote candidate filter: heuristics drop ~95% of 464k → ~20k. Length, emotion/keyword, reply-chain depth, all-caps, elongation pattern. | 0 | Python |
| S4 | Local embed + cluster: sentence-transformers MiniLM-L6 + KMeans to ~500 themes, top-3 per cluster. | 0 | sentence-transformers, sklearn |
| S-NLP | Sentiment + argument-window detection (distilbert-sst2). Powers fight-marker, sweetest/silent days, sentiment curve. | 0 | distilbert local |
| S5 | LLM curate: Haiku 4.5 batched, prompt-cached. Rates ~1500 candidates 1-5, tags chapter, 1-line "why memorable". Output ~200 best. | ~$0.15 first run, ~$0.02 cached re-run | `anthropic` SDK |
| S6 | Chapter intros: Sonnet 4.6, one call per chapter using ~50 curated quotes + first-X hits in range. Draft 200-word intro → MDX. | ~$0.20 first run | `anthropic` SDK |
| S-CHAP | Auto chapter detection: volume valleys + topic shifts + sentiment dips → `chapter_seed.json`. | 0 | clustering on daily aggregates |

**Total LLM spend per full build: <$0.50. Incremental rebuilds: <$0.05.** Stage outputs are hashed on inputs; unchanged stages skip.

## 6. Chapter Spine

Auto-detected by pipeline (S-CHAP), then user-editable in MDX. The Proposal chapter is **user-pinned** to the exact January 2026 date regardless of what auto-detect proposes; pipeline must split that day out as its own chapter boundary. Seed estimate from chat span:

1. **First Hello** — Jul 2017, pre-college flirty texts
2. **DU Days, Metro Days** — 2017-19, college, distance
3. **The Pandemic** — 2020-21
4. **Growing Up** — 2022-23, work, money, parents
5. **Lenovo & Life** — 2024-25, career pressure
6. **The Proposal** — Jan 2026, climax chapter
7. **Us, Now** — post-proposal → present

Each chapter page contains:
- Cover photo (user-picked from period media)
- 200-word intro (LLM draft → user-edited)
- 10-30 curated quote cards with date + sender
- Photo strip from window
- Mini-stat band (msgs in period, top emoji, etc.)
- Prev/next chapter nav
- "Open this period in archive" link

## 7. Page-Level UX

```
/             Landing: cover + Open button → password
/book         Library: chapter grid, 2×N
/book/[slug]  Chapter: hero photo, intro, quote cards, photo strip, stat band
/search       Pagefind search, results jump into archive
/stats        Full dashboard, 60+ metrics, charts
/archive/[d]  Paginated raw msgs, jump-to-date, sender filter
/firsts       First-X moments scroll
```

**Quote card component**
```
┌─ 14 Aug 2018, 11:47 PM ────────────────┐
│ Sid:                                    │
│ "Garmi ghanta. Ac to hoga class mein😂" │
│                          [view in chat] │
└─────────────────────────────────────────┘
```

## 8. Visual Aesthetic

**Hybrid: dark luxe shell + warm-paper inserts.**
- Dark midnight background, thin gold accent rules, large serif chapter headings
- Cinematic photo crops with soft vignette
- Quote cards rendered as cream paper insets with soft shadow, dark serif body, sender attribution
- Mono caption font for dates/metadata
- No emoji styling overrides (use system color emoji)
- Responsive: phone reads like a book; desktop adds margins, never feels app-y

## 9. Authentication, Hosting, Privacy

**Hosting**
- GitHub remote: `https://github.com/Sid342/anishaSidWhatsapp.git` (private)
- Deploy: Cloudflare Pages auto-deploy on push to `main`
- URL: `*.pages.dev` (or custom domain later)

**Auth — Cloudflare Worker password gate**
- Single shared password (bcrypt-hashed, stored as Worker secret)
- POST `/login` with password → sets signed cookie → access
- Worker checks cookie on every request, including media paths
- `/logout` clears cookie
- No email, no PIN, no multi-user

**Privacy**
- Repo private on GitHub
- `X-Robots-Tag: noindex`, robots.txt deny-all
- Media served from `/private/media/...` behind worker
- No third-party analytics; optional self-hosted Plausible later
- Raw `_chat.txt` and original WhatsApp media `.zip` never ship to CF — only derived JSON + optimized webps
- `.env` not committed; API keys local-only

## 10. Tech Stack Lockfile

| Layer | Choice |
|---|---|
| Site framework | Astro 5 |
| UI islands | React 19 |
| Styling | Tailwind 4 + CSS vars |
| Content auth | MDX |
| Search | Pagefind |
| Charts | Observable Plot |
| Pipeline lang | Python 3.12 + uv |
| Local NLP | sentence-transformers MiniLM-L6 + distilbert-sst2 |
| Emoji | `emoji` lib |
| LLM client | `anthropic` Python SDK, prompt caching enabled |
| Image opt | `sharp` via Astro Assets |
| Auth worker | Cloudflare Worker (TypeScript), bcrypt |
| Deploy | Cloudflare Pages |
| Repo | GitHub private |

## 11. Repository Layout

```
whatsapp-sid-anisha/
├── pipeline/
│   ├── pyproject.toml
│   ├── run.py
│   ├── stages/
│   │   ├── s0_parse.py
│   │   ├── s1_stats.py
│   │   ├── s2_firsts.py
│   │   ├── s3_candidates.py
│   │   ├── s4_cluster.py
│   │   ├── s5_curate.py
│   │   ├── s6_intros.py
│   │   ├── s_nlp.py
│   │   └── s_chapters.py
│   ├── media/{ingest.py, optimize.py}
│   ├── lib/{parser.py, gazetteer.py, cache.py, cost.py}
│   └── tests/
├── site/
│   ├── astro.config.mjs
│   ├── tailwind.config.ts
│   ├── package.json
│   ├── public/{fonts/, media/}
│   └── src/
│       ├── content/{config.ts, chapters/*.mdx}
│       ├── components/{QuoteCard, PaperCard, ChapterHero, StatBand, PetNameRibbon, EmojiHeatmap, HourHeatmap, ReplyTimeChart, ...}
│       ├── layouts/{BookLayout, PaperCard}
│       ├── pages/{index, book/, search, stats, archive/[date], firsts}
│       ├── data/{stats.json, firsts.json, quotes.json, chapter_seed.json, messages.index.json}  # messages.index.json = per-date offsets into sharded archive JSON for /archive pagination
│       └── styles/globals.css
├── worker/
│   ├── wrangler.toml
│   └── src/index.ts
├── data/           # gitignored: _chat.txt, media/, messages.parquet
├── cache/          # gitignored: pipeline intermediates
├── docs/superpowers/specs/2026-05-26-anisha-and-sid-design.md
├── .env.example
├── .gitignore
└── README.md
```

**Symlink convenience:** `/Users/sid/Documents/Whatsapp Sid Anisha` → `/Users/sid/Projects/whatsapp-sid-anisha` (real repo lives outside iCloud to avoid git-commit hangs).

## 12. Build Phases

| Phase | Days | Output |
|---|---|---|
| 1. Foundation | 1-2 | Astro shell, dark luxe + paper tokens, mock chapters running locally |
| 2. Parser + stats core | 2-3 | `/stats` and `/firsts` live with real numbers |
| 3. Auto chapter detect | 1-2 | `chapter_seed.json` reviewed |
| 4. Quote curation (S3-S5) | 1 | Real curated quotes per chapter |
| 5. Media pipeline | 1-2 | Hero + photo strips per chapter |
| 6. Chapter intros + polish | 1 | Book reads end-to-end, full stats dashboard |
| 7. Search, archive, auth, deploy | 2 | Live private URL behind password |

**Total: ~10-13 working days.** Each phase ships independently.

## 13. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Pagefind index too large (>50 MB) | Shard by chapter, lazy-load per route |
| Photo count blows repo size | Resize to webp ≤1600px, store via Git LFS if >1 GB |
| Parser misses multi-line edge cases | Test suite on synthetic + real samples |
| LLM costs creep over budget | Per-stage token logger in `lib/cost.py`; hard cap at $1 |
| Pipeline stage breaks → no resume | Input-hash cache lets unchanged stages skip |
| Sentiment/argument detection misclassifies | Mark all S-NLP-derived metrics as "estimated"; never surface as fact |
| Photos contain sensitive content | Manual review before commit; bulk-import gated behind `--include-media` flag |
| iCloud sync breaks git | Real repo at `~/Projects/whatsapp-sid-anisha`, symlinked into iCloud Documents |
| Forgot password | Worker secret rotatable; bcrypt re-hash and redeploy |

## 14. Success Criteria

- Anisha can open the site URL, enter shared password, read the entire book on phone and desktop
- All 60+ stats render with real numbers, no placeholders
- Search returns hits across 9 years of chat in <500 ms
- Every chapter has ≥10 curated quotes and ≥1 cover photo
- Build pipeline completes end-to-end in <15 min on M-series Mac
- Total LLM spend under $1 per full rebuild

## 15. Open Questions (resolved before plan)

| Q | Status |
|---|---|
| Hosting / deploy | Resolved: GitHub + Cloudflare Pages |
| Auth model | Resolved: Cloudflare Worker single-pwd |
| Chapter detection | Resolved: auto-detect, manually editable |
| Aesthetic | Resolved: dark luxe + warm paper |
| Proposal placement | Resolved: dedicated chapter, real Jan 2026 event |
| Repo path | Resolved: `~/Projects/whatsapp-sid-anisha` |

---

## Appendix A — Full Metrics Catalog (64 items)

### Volume / cadence (S1)
1. Total msgs, words, chars per person
2. Msgs/day avg, peak day
3. Drought days (>24h silent)
4. Longest streak of consecutive days w/ msgs
5. Hour × weekday heatmap
6. Late-night ratio (after 11pm)
7. Goodnight champion (last msg of day)
8. Good-morning champion (first msg of day)

### Response patterns (S1)
9. Median reply time per person
10. Reply-time drift per year
11. Left-on-read leaderboard (top 20)
12. N-text burst frequency
13. Conversation initiator after 2h silence
14. Reciprocity score (msg-length ratio)
15. Apology counter ("sorry"/"sry"/"maaf")

### Vocabulary (S1)
16. Top 50 words per person
17. Signature words (yours-but-not-hers and reverse)
18. Hinglish ratio per person, per year
19. Avg word/msg length drift
20. Caps-lock msg count
21. Punctuation profile (!/?/.../.)
22. Question-asker ratio

### Emoji (S1)
23. Top emojis overall + per person
24. Emoji-only msg count
25. 😂 inflation per year
26. ❤️ first appearance + count over time
27. Sticker/GIF count
28. Emoji drift cohort

### Nicknames (S1+S2)
29. Pet-name evolution timeline
30. Pet-name freq per year
31. Longest-elongation award (`babyyyyy…`)

### Topics / mentions (S1)
32. Mention counter (parents, Lenovo, college, metro, etc.)
33. Place mentions (Delhi, Lajpat, Mandi, Rajeev Chowk, …)
34. Movie/show extraction
35. All shared links by sender
36. Food orders mention scan

### Milestones (S1+S2)
37. "I love you" first + count + per year
38. "I miss you" first + count + per year
39. "Shaadi"/"marry" first + count + sender-first
40. Fight markers (S-NLP sentiment + apology cluster)
41. "Promise" count
42. Plans-made count

### Geo / travel (S1)
43. Metro station mention freq
44. Travel keyword scan (flight, IRCTC, indigo, …)

### Time-of-relationship math (S1)
45. Total days together
46. Estimated hours chatting
47. "Novels-of-Anisha-words" (word count ÷ 80,000)

### Curious / fun
48. Most-repeated phrase per person (S1, ngrams)
49. 😂😂 streak — longest consecutive days w/ laugh (S1)
50. Argument detector windows (S-NLP)
51. Sweetest 10 days (love/baby/❤️ density) (S1)
52. Silent 10 days (lowest volume window) (S1)
53. Drunk-text candidates (late + caps + typos) (S1)
54. Voice-note count + duration (S0)
55. Photo-share leaderboard by year (S0)
56. Typo-heavier person (S1, hunspell)
57. Texting-twin moments (within 2s both sides) (S1)
58. Coincidence count (shared idea within X min) (S-NLP+S4)

### Charts derived
59. Year-by-year msg volume bar
60. Sentiment proxy curve (monthly)
61. Pet-name evolution ribbon
62. Topic word-cloud per chapter
63. "Our song" — top YouTube link shared
64. Reply-time decay graph

---

## Appendix B — Cost Ledger

| Stage | First run | Cached re-run |
|---|---|---|
| S0–S4, S-NLP, S-CHAP | $0 (local CPU) | $0 |
| S5 (Haiku, batched, cached) | ~$0.15 | ~$0.02 |
| S6 (Sonnet, per-chapter) | ~$0.20 | $0 if chapters unchanged |
| **Total** | **<$0.50** | **<$0.05** |

Hard cap enforced in `pipeline/lib/cost.py` — pipeline aborts if cumulative cost crosses $1.
