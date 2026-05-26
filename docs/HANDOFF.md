# Handoff — Anisha & Sid Memory Site

**Date frozen:** 2026-05-26
**Frozen by:** Sid + Claude (interactive session)
**Resume by:** any developer or fresh Claude session

This doc + the spec + the impl plan are the complete pickup kit. Read this first, then the spec, then the plan.

---

## 1. What it is

Private, password-gated chaptered-book website built from 9 years of WhatsApp chat between Sid and Anisha (2017-07-19 → 2026-05-08, 478,167 messages). Random-surprise post-proposal gift. Proposal was 25 Jan 2026.

**Repo:** `https://github.com/Sid342/anishaSidWhatsapp` (private)
**Local:** `/Users/sid/Projects/whatsapp-sid-anisha` (symlinked at `/Users/sid/Documents/Whatsapp Sid Anisha`)
**Branch:** `main`
**Deploy target:** Cloudflare Pages → custom Worker auth gate

---

## 2. Status — what's done

Phases 1 and 2 complete and pushed. Phase 3 partially scaffolded but uncommitted.

| Phase | Scope | Status |
|---|---|---|
| 0 | Spec + impl plan + repo bootstrap | ✅ pushed (commits `b619d1c` → `cca7fda`) |
| 1 | Astro 5 site shell, dark luxe + warm paper theme, landing/book/chapter routes, mock chapter, Tailwind v4 via `@tailwindcss/vite` | ✅ pushed (`ff9b373` → `e8fe2d2`) |
| 2 | Python pipeline scaffold, parser (TDD, 3/3 tests pass), S0 parse → parquet, S1 stats (counts, cadence, heatmap, vocab, emoji, nicknames, mentions, milestones), S2 firsts, `/stats` + `/firsts` pages | ✅ pushed (`d303e67` → `4725a45`) |
| 3 | Auto chapter detection (S-CHAP) + MDX emit (`s_chapters_emit_mdx`) + 25 Jan 2026 proposal pin | ⏳ partial — see §6 |
| 4 | Quote curation (S3 → S4 → S-NLP → S5 Haiku) | ⏳ pending |
| 5 | Media pipeline (WhatsApp `.zip` → optimized webp + chapter mapping + PhotoStrip) | 🚧 **blocked on `.zip` arrival** |
| 6 | Sonnet chapter intros + StatBand + Observable Plot charts on `/stats` | ⏳ pending |
| 7 | Pagefind search, archive paginated route, Cloudflare Worker password gate, CF Pages deploy | ⏳ pending |

### Real numbers from current build
- 478,167 messages parsed
- 3,216 days span
- Peak day: 2023-11-19 (1,269 msgs)
- Longest consecutive-days streak: 429 days
- 48 first-X moments extracted
- `npm run build` succeeds, 5 pages emitted, Pagefind index runs (no content to index yet, that's fine)

---

## 3. Decisions locked (don't relitigate)

| Topic | Decision |
|---|---|
| Site framework | Astro 5 (static) + React 19 islands + MDX + Tailwind 4 (`@tailwindcss/vite`, NOT `@astrojs/tailwind` — that's the v3 adapter and broken on v4) |
| Pipeline language | Python 3.12 via `uv` |
| Search | Pagefind (static, sharded) |
| Charts | Observable Plot |
| Auth | Cloudflare Worker, single shared bcrypt-hashed password, signed cookie |
| Host | Cloudflare Pages auto-deploy from GitHub `main` |
| Domain | `*.pages.dev` default; no custom domain |
| LLM models | Haiku 4.5 for quote curation (S5, prompt-cached), Sonnet 4.6 for chapter intros (S6) |
| Cost cap | hard $1 total per build, enforced in `pipeline/lib/cost.py` |
| Repo path | `~/Projects/whatsapp-sid-anisha` (NOT iCloud Documents — git commit hangs there). Symlink at iCloud path for Finder convenience. |
| Visual aesthetic | Dark luxe midnight shell + warm-paper quote inserts (cream cards with soft shadow, hand-script signature) |
| Chapter spine | Auto-detected from chat data (volume valley + topic shift), user can rename in MDX. Proposal day 25 Jan 2026 force-pinned as a chapter boundary. |
| Privacy posture | Repo private, `noindex` everywhere, no 3rd-party analytics, raw chat + media never in git or deployed (gitignored), derived JSON + optimized webps only. |

---

## 4. Inputs needed before next milestones

| Input | Needed for | Status |
|---|---|---|
| `_chat.txt` | parser + stats | ✅ at `data/_chat.txt` (gitignored, 25 MB, 482,768 lines) |
| Proposal date | chapter pin | ✅ 2026-01-25 (hardcoded in `pipeline/stages/s_chapters.py`) |
| WhatsApp `.zip` with media | Phase 5 (photos) | ❌ drop into `data/` then run `pipeline/media/ingest.py` |
| Site password | Phase 7 (Worker secret) | ❌ pick at deploy time; bcrypt-hash it and set as `SITE_PASSWORD_HASH` Worker secret |
| `ANTHROPIC_API_KEY` env var | Phase 4 (S5 Haiku) + Phase 6 (S6 Sonnet) | ❌ local export only; never ship to CF |
| Custom domain | optional | ❌ default `*.pages.dev` OK |

---

## 5. Environment gotchas — DO NOT FORGET

1. **Git binary.** Nordic toolchain at `/opt/nordic/ncs/toolchains/.../bin/git` ships an incomplete git that lacks `remote-https`. Always use `/usr/bin/git` for any operation that talks to the GitHub remote. Plain `git` may resolve to the broken one.

2. **iCloud.** `/Users/sid/Documents` is iCloud — git commits hang there. Real repo lives at `/Users/sid/Projects/whatsapp-sid-anisha`. There is a symlink at `/Users/sid/Documents/Whatsapp Sid Anisha` for Finder convenience only; do not run git inside the iCloud path.

3. **Timestamp narrow-no-break space (U+202F).** iOS WhatsApp exports separate the time and AM/PM with U+202F (` `), not a regular space. The parser regex in `pipeline/lib/parser.py` already handles this; do not "simplify" the character class back to `\ ?`.

4. **`.gitignore` negation.** Root `.gitignore` has `data/` and `cache/` blanket-ignored, but `site/src/data/` is explicitly negated (`!site/src/data/`, `!site/src/data/*.json`). This is intentional — pipeline outputs that drive the site live there and MUST be tracked. Don't unify the patterns.

5. **Tailwind v4.** Use `@tailwindcss/vite` only. `@astrojs/tailwind` is the v3 adapter and incompatible with v4. The plan was patched post-Phase-1 to reflect this.

6. **`uv` is at `/opt/homebrew/bin/uv`.** If missing, `brew install uv`.

7. **`--legacy-peer-deps`** may be required for `npm install` in `site/` due to React 19 peer pinning. Past runs needed it.

8. **`messages.parquet` is gitignored.** Reproducible from `_chat.txt` via `uv run python run.py --stage s0_parse` (~30 s).

9. **iCloud-safe.** If accidentally running in the symlinked iCloud path, exit and `cd /Users/sid/Projects/whatsapp-sid-anisha` instead.

---

## 6. Phase 3 work-in-progress (uncommitted) at handoff time

Working tree has these untracked files when this doc was written:

```
pipeline/stages/s_chapters.py          # likely seeded from plan; verify before running
pipeline/uv.lock                       # SHOULD be tracked once verified
site/src/data/chapter_seed.json        # generator output if s_chapters.py was run
```

**Recommended pickup steps:**
1. `cd /Users/sid/Projects/whatsapp-sid-anisha`
2. Inspect `pipeline/stages/s_chapters.py` and confirm it matches the Phase 3 Task 3.1 spec in the impl plan; in particular the `PROPOSAL = date(2026, 1, 25)` pin must be present.
3. Run `cd pipeline && uv run python run.py --stage s_chapters` and inspect `site/src/data/chapter_seed.json`. Expect 5-9 chapters, one of which brackets `2026-01-25`.
4. Then Task 3.2 (`s_chapters_emit_mdx.py`) — emit MDX files, delete `site/src/content/chapters/00-mock.mdx`, run pipeline, verify chapter MDX matches the content-collection schema.
5. `cd site && npm run build` must succeed.
6. Commit per plan, then push.

---

## 7. Resumption command sheet

```bash
# 1. Land in the repo (real path, not iCloud)
cd /Users/sid/Projects/whatsapp-sid-anisha

# 2. Sanity checks
/usr/bin/git status
/usr/bin/git log --oneline -8

# 3. Site dev server (real numbers live)
cd site && npm install --legacy-peer-deps  # only if node_modules missing
npm run dev                                 # http://localhost:4321

# 4. Pipeline — full rebuild (5-10 min Phase 2 only; Phase 4 adds ~10 min for embeddings)
cd /Users/sid/Projects/whatsapp-sid-anisha/pipeline
uv sync                                     # only if .venv missing
uv run python run.py                        # runs all stages defined in STAGES list

# 5. Just a single stage
uv run python run.py --stage s0_parse
uv run python run.py --stage s1_stats --force   # --force ignores cache stamp

# 6. Tests
uv run pytest tests/ -v

# 7. Cost ledger
cat cache/cost_ledger.jsonl

# 8. Push (always uses /usr/bin/git)
/usr/bin/git push
```

---

## 8. Where to find what

| Need | Path |
|---|---|
| Spec (locked) | `docs/superpowers/specs/2026-05-26-anisha-and-sid-design.md` |
| Implementation plan (locked, 30+ tasks across 7 phases) | `docs/superpowers/plans/2026-05-26-anisha-and-sid-impl.md` |
| This handoff doc | `docs/HANDOFF.md` |
| Site source | `site/src/` |
| Pipeline source | `pipeline/` |
| Auth worker source | `worker/` (Phase 7, not yet created) |
| Raw chat (gitignored) | `data/_chat.txt` |
| Parquet (gitignored, regen via S0) | `data/messages.parquet` |
| Pipeline outputs (tracked) | `site/src/data/*.json` |
| Pipeline intermediates (gitignored) | `cache/*` |
| Cost ledger | `cache/cost_ledger.jsonl` |

---

## 9. Phase-3-onwards subagent prompts (ready to paste)

These are deliberately self-contained so a fresh Claude can dispatch them without re-deriving context.

### Phase 3 implementer

> Implement Phase 3 of the plan at `/Users/sid/Projects/whatsapp-sid-anisha/docs/superpowers/plans/2026-05-26-anisha-and-sid-impl.md`. Phases 1-2 done. Working tree has uncommitted `pipeline/stages/s_chapters.py` and `site/src/data/chapter_seed.json` — verify these match the Phase 3 spec, then complete Task 3.2 (`s_chapters_emit_mdx.py`, MDX emission, remove mock, wire into STAGES) and Task 3.3 (push). Use `/usr/bin/git`. Verify `cd site && npm run build` succeeds. Verify one chapter brackets 2026-01-25. Report DONE/BLOCKED.

### Phase 4 implementer (after Phase 3)

> Implement Phase 4 of the plan. Tasks 4.1-4.6: S3 candidate filter → S4 local embed + KMeans → S-NLP distilbert sentiment → S5 Haiku batched curation with prompt cache → render quotes per chapter. Add the heavy ML deps (`sentence-transformers`, `scikit-learn`, `transformers`, `torch`) to `pipeline/pyproject.toml`, run `uv sync`. Requires `ANTHROPIC_API_KEY` env var. Verify total cost < $0.50 via `cache/cost_ledger.jsonl`. Use `/usr/bin/git`. Report DONE/BLOCKED + cost figure.

### Phase 6 implementer (Phase 5 blocked, skip until .zip arrives)

> Implement Phase 6 of the plan. Tasks 6.1-6.4: S6 Sonnet chapter intros patched into MDX, S_STAT_BANDS per-chapter stats, EmojiInflation / PetNameRibbon / ReplyTimeChart React+Observable Plot charts on `/stats`. Requires `ANTHROPIC_API_KEY`. Verify build succeeds. Use `/usr/bin/git`.

### Phase 7 implementer

> Implement Phase 7 of the plan. Tasks 7.1-7.5: Pagefind UI + archive paginated route (`s_archive_index` stage) + Cloudflare Worker bcrypt auth gate (`worker/`) + Pages deploy notes + robots.txt deny. Worker file `worker/src/index.ts` uses `bcryptjs` and HMAC-signed cookies. Pages project + Worker route setup are dashboard-only — document the steps. Set Worker secrets `SITE_PASSWORD_HASH` and `COOKIE_SIGNING_KEY` via `npx wrangler secret put`. Use `/usr/bin/git`.

### Phase 5 implementer (only after .zip lands in `data/`)

> User dropped a WhatsApp `.zip` at `data/*.zip`. Implement Phase 5 of the plan. Tasks 5.1-5.5: ingest .zip to `data/media_raw/`, optimize photos to webp with `pillow`, build `s_media_map.py` to bucket photos by chapter date range, create PhotoStrip component, wire into chapter pages. Use `/usr/bin/git`. Photos commit to `site/public/media/photos/` (private repo, OK).

---

## 10. Cost so far

| Date | Stage | Model | Spend |
|---|---|---|---|
| — | nothing yet (Phase 4 S5 not run) | — | $0.00 |

Estimated total for full Phase 4 + Phase 6: ~$0.40 (Haiku + Sonnet). Hard cap $1.

---

## 11. Open questions for Sid (none blocking)

- Custom domain wanted later? (current default: `anishasid.pages.dev`)
- Reveal mechanic for showing site to Anisha? (currently: just send her the URL + password)
- Any chapters you want to rename or reorder after auto-detect runs?
- Voice notes / audio: keep counted but not playable, or extract and host with media? (current spec: count only)

---

## 12. Done = these all hold

- `https://*.pages.dev` requires password and shows the book
- `/stats` renders 30+ metrics from the real chat
- `/firsts` shows every milestone phrase with context
- Every chapter has intro + curated quotes + (post-media) cover + photo strip
- `/search` returns hits in <500 ms
- `/archive/YYYY-MM-DD` renders all messages from that day
- Full pipeline rebuild costs < $0.50

---

End of handoff. Read the spec next, then the impl plan. Resume at Phase 3.
