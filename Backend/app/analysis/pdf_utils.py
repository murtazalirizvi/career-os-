# we are good - PDF processing utilities working correctly
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import fitz  # PyMuPDF
import numpy as np


def extract_text_and_layout(pdf_path: Path) -> Tuple[str, List[Dict]]:
    doc = fitz.open(pdf_path)
    text_parts: List[str] = []
    blocks: List[Dict] = []

    for page_index, page in enumerate(doc):
        text = page.get_text("text")
        text_parts.append(text)

        raw_blocks = page.get_text("dict").get("blocks", [])
        for block in raw_blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue

                line_text = " ".join(span.get("text", "") for span in spans).strip()
                if not line_text:
                    continue

                bbox = line.get("bbox", [0, 0, 0, 0])
                avg_size = sum(span.get("size", 0.0) for span in spans) / max(len(spans), 1)
                bold_weight = sum(1 for span in spans if "bold" in span.get("font", "").lower()) / max(len(spans), 1)

                blocks.append(
                    {
                        "page": page_index,
                        "text": line_text,
                        "bbox": bbox,
                        "font_size": avg_size,
                        "bold_weight": bold_weight,
                    }
                )

    return "\n".join(text_parts), blocks


def render_page_gray(pdf_path: Path, page_index: int = 0, scale: float = 1.25) -> np.ndarray:
    doc = fitz.open(pdf_path)
    page = doc[page_index]
    matrix = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

    # Convert RGB to grayscale via weighted projection.
    if pix.n >= 3:
        gray = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]).astype(np.uint8)
    else:
        gray = arr[:, :, 0]
    return gray


def detect_nonstandard_fonts(pdf_path: Path) -> List[str]:
    doc = fitz.open(pdf_path)
    font_alerts: List[str] = []

    for page_index, page in enumerate(doc):
        fonts = page.get_fonts(full=True)
        for font in fonts:
            font_name = str(font[3])
            if "type3" in font_name.lower():
                font_alerts.append(f"Page {page_index + 1}: possible Type3 font '{font_name}' detected.")
            if any(ord(ch) > 127 for ch in font_name):
                font_alerts.append(f"Page {page_index + 1}: non-standard font name '{font_name}' detected.")

    return font_alerts
