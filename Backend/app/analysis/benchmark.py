from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BaselineProfile:
    recommended_pages: int
    bullets_min: int
    bullets_max: int
    years_required: int


BASELINES: Dict[str, BaselineProfile] = {
    "frontend": BaselineProfile(recommended_pages=1, bullets_min=10, bullets_max=28, years_required=2),
    "backend": BaselineProfile(recommended_pages=1, bullets_min=12, bullets_max=30, years_required=2),
    "fullstack": BaselineProfile(recommended_pages=1, bullets_min=12, bullets_max=32, years_required=3),
    "data": BaselineProfile(recommended_pages=1, bullets_min=9, bullets_max=24, years_required=2),
}


def pick_baseline(job_category: str) -> BaselineProfile:
    return BASELINES.get(job_category.lower(), BASELINES["frontend"])


def benchmark_score(
    job_category: str,
    page_count: int,
    bullet_count: int,
    years_experience_found: float,
    unique_skills: List[str],
) -> Dict:
    base = pick_baseline(job_category)

    length_score = 100.0 - abs(page_count - base.recommended_pages) * 18.0

    if bullet_count < base.bullets_min:
        bullet_score = 100.0 - (base.bullets_min - bullet_count) * 5.0
    elif bullet_count > base.bullets_max:
        bullet_score = 100.0 - (bullet_count - base.bullets_max) * 3.6
    else:
        bullet_score = 100.0

    seniority_gap = max(0.0, base.years_required - years_experience_found)
    seniority_score = max(0.0, 100.0 - seniority_gap * 25.0)

    # USP discovery: extra credit for rare skill markers.
    rare_markers = {"webrtc", "webassembly", "rust", "kafka", "grpc", "onnx", "terraform"}
    rare_hits = sorted({s.lower() for s in unique_skills if s.lower() in rare_markers})
    usp_bonus = min(12.0, len(rare_hits) * 3.0)

    overall = max(0.0, min(100.0, (length_score * 0.24 + bullet_score * 0.28 + seniority_score * 0.38) + usp_bonus))

    summary = (
        f"Template fit score {overall:.1f}. Length {length_score:.1f}, bullet density {bullet_score:.1f}, "
        f"seniority alignment {seniority_score:.1f}."
    )

    recommendations = []
    if length_score < 80:
        recommendations.append("Adjust resume length closer to 1 page for early-career roles.")
    if bullet_score < 80:
        recommendations.append("Rebalance bullet count to improve skim-ability and specificity.")
    if seniority_score < 80:
        recommendations.append("Clarify years of ownership and impact to align with role seniority.")
    if rare_hits:
        recommendations.append(f"Highlight unique strengths: {', '.join(rare_hits)}.")

    return {
        "score": round(overall, 2),
        "summary": summary,
        "recommendations": recommendations,
        "rare_hits": rare_hits,
        "subscores": {
            "length": round(length_score, 2),
            "bullet_density": round(bullet_score, 2),
            "seniority": round(seniority_score, 2),
        },
    }
