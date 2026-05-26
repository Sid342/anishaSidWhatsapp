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
