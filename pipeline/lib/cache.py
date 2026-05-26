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
