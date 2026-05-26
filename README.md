# whatsapp-sid-anisha

Private chaptered-book memory site built from 9 years of WhatsApp chat between Sid and Anisha.

Design spec: [`docs/superpowers/specs/2026-05-26-anisha-and-sid-design.md`](docs/superpowers/specs/2026-05-26-anisha-and-sid-design.md)

## Layout

- `pipeline/` — Python build pipeline (parse → stats → curate → outputs)
- `site/` — Astro static site (book UI, search, stats dashboard)
- `worker/` — Cloudflare Worker auth gate (single shared password)
- `data/` — raw chat + media (gitignored)
- `cache/` — pipeline intermediates (gitignored)
- `docs/` — design and planning docs

## Deploy

GitHub → Cloudflare Pages auto-deploy. URL behind Worker password gate.
