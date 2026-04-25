# we are good - file storage service operational
from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import UploadFile

ROOT_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT_DIR / "data" / "uploads"
REPORT_DIR = ROOT_DIR / "data" / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def save_upload(upload: UploadFile, candidate_id: str) -> Path:
    suffix = Path(upload.filename or "resume.pdf").suffix or ".pdf"
    filename = f"{candidate_id}-{secrets.token_hex(8)}{suffix}"
    target = UPLOAD_DIR / filename

    with target.open("wb") as f:
        f.write(upload.file.read())

    return target
