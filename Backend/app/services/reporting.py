from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .storage import REPORT_DIR


def write_markdown_report(analysis_id: int, payload: Dict[str, Any]) -> Path:
    report_path = REPORT_DIR / f"feature1-analysis-{analysis_id}.md"

    score = payload["score"]
    summaries = payload["summaries"]
    metrics = payload["metrics"]
    recommendations = payload["recommendations"]

    lines = [
        f"# Feature 1 Diagnostic Report #{analysis_id}",
        "",
        "## Scorecard",
        f"- Overall: {score['overall']}",
        f"- Visual Hierarchy: {score['visual_hierarchy']}",
        f"- ATS Integrity: {score['ats_integrity']}",
        f"- Semantic Match: {score['semantic_match']}",
        f"- Competitive Benchmark: {score['competitive_benchmark']}",
        "",
        "## Summaries",
        f"- Visual: {summaries['visual']}",
        f"- ATS: {summaries['ats']}",
        f"- Semantic: {summaries['semantic']}",
        f"- Benchmark: {summaries['benchmark']}",
        "",
        "## Prioritized Recommendations",
    ]

    for rec in recommendations:
        lines.append(f"- {rec}")

    lines.extend(
        [
            "",
            "## Metrics (Raw JSON)",
            "```json",
            json.dumps(metrics, indent=2, ensure_ascii=True),
            "```",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
