from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Sequence

from .storage import REPORT_DIR


def write_feature2_journey_report(candidate_id: str, rows: Sequence[Any]) -> Path:
    path = REPORT_DIR / f"feature2-journey-{candidate_id}.md"

    lines = [
        f"# Career Journey Export: {candidate_id}",
        "",
        f"Total interviews analyzed: {len(rows)}",
        "",
        "## Interview Timeline",
    ]

    for row in rows:
        score = json.loads(row.score_json)
        analytics = json.loads(row.analytics_snapshot_json)
        lines.extend(
            [
                f"### Interview #{row.id} - {row.company_name} ({row.role_name})",
                f"- Round: {row.interview_round}",
                f"- Stage drop-off: {row.lifecycle_stage}",
                f"- Overall autopsy score: {score['overall_autopsy_score']}",
                f"- Rejection category: {analytics.get('rejection_category', 'unknown')}",
                "",
            ]
        )

    lines.extend(
        [
            "## Recommended Next Cycle",
            "- Run one mock interview focused on weakest technical area.",
            "- Improve STAR density and answer precision for behavioral rounds.",
            "- Send structured follow-up communication within 24h after interview.",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_reminders(ingestion: Dict[str, Any], strategic_actions: Dict[str, Any]) -> list[Dict[str, Any]]:
    challenge = ingestion.get("challenge_question", "technical clarification")
    reminders = strategic_actions.get("follow_up_cadence", [])
    payload = []
    for item in reminders:
        payload.append(
            {
                "type": "follow_up",
                "scheduled_at": item.get("scheduled_at"),
                "message": item.get("message"),
                "context": f"Reference challenge: {challenge}",
            }
        )
    return payload
