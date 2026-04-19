from __future__ import annotations

import re
from typing import List

TIMECODE_VTT_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}$")


def parse_vtt(vtt_text: str) -> List[str]:
    lines = [line.strip() for line in vtt_text.splitlines()]
    utterances: List[str] = []
    for line in lines:
        if not line or line.startswith("WEBVTT") or line.isdigit() or TIMECODE_VTT_RE.match(line):
            continue
        utterances.append(line)
    return utterances
