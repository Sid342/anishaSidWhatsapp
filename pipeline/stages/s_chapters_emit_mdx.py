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
