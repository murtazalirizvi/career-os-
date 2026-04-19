from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import cv2
import numpy as np

from . import gemini_client
from .benchmark import benchmark_score
from .pdf_utils import detect_nonstandard_fonts, extract_text_and_layout, render_page_gray
from .text_nlp import (
    buzzword_replacements,
    keyword_cloud_differential,
    missing_skill_prioritization,
    semantic_alignment_score,
    skill_frequency_health,
    synonym_suggestions,
    tokenize,
)

SECTION_HEADER_RE = re.compile(r"^(summary|experience|education|skills|projects|certifications|contact)\b", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-\(\)]{7,}\d)")
YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", re.I)

# ── 2.5: LRU cache for parsed resume text (avoids re-parsing same PDF) ────────
# Keyed by (candidate_id, resume_path_str) — holds up to 10 entries in memory.
@lru_cache(maxsize=10)
def _cached_resume_text(resume_path_str: str) -> tuple[str, tuple]:
    """
    Parse a PDF and return (text, layout_blocks_tuple).
    Cached so repeated calls for the same file skip PyMuPDF entirely.
    """
    path = Path(resume_path_str)
    text, blocks = extract_text_and_layout(path)
    return text, tuple(json.dumps(b, ensure_ascii=True) for b in blocks)


def _get_resume_text_and_blocks(resume_path: Path) -> tuple[str, List[Dict]]:
    text, blocks_json_tuple = _cached_resume_text(str(resume_path))
    blocks = [json.loads(b) for b in blocks_json_tuple]
    return text, blocks


class Feature1Engine:
    def __init__(self, resume_pdf_path: Path, job_description: str, job_category: str) -> None:
        self.resume_pdf_path = resume_pdf_path
        self.job_description = job_description
        self.job_category = job_category

    def run(self) -> Dict[str, Any]:
        # 2.5: Use LRU cache for PDF parsing — skips re-parse on repeated calls
        resume_text, layout_blocks = _get_resume_text_and_blocks(self.resume_pdf_path)
        gray = render_page_gray(self.resume_pdf_path)

        visual_result = self._analyze_visual_hierarchy(gray, layout_blocks)
        ats_result = self._analyze_ats(resume_text, layout_blocks)
        semantic_result = self._analyze_semantic(resume_text)
        benchmark_result = self._analyze_benchmark(resume_text, ats_result)

        overall = (
            visual_result["score"] * 0.28
            + ats_result["score"] * 0.24
            + semantic_result["score"] * 0.28
            + benchmark_result["score"] * 0.20
        )

        combined_recommendations = []
        for source in (visual_result, ats_result, semantic_result, benchmark_result):
            combined_recommendations.extend(source.get("recommendations", []))

        heuristic_recs = self._prioritize_recommendations(combined_recommendations)

        # 2.1: Gemini-powered natural language coaching on top of heuristic recs
        ai_recommendations = self._gemini_recommendations(
            resume_text=resume_text,
            heuristic_recs=heuristic_recs,
            scores={
                "overall": round(overall, 2),
                "visual": visual_result["score"],
                "ats": ats_result["score"],
                "semantic": semantic_result["score"],
                "benchmark": benchmark_result["score"],
            },
        )

        return {
            "score": {
                "overall": round(overall, 2),
                "visual_hierarchy": visual_result["score"],
                "ats_integrity": ats_result["score"],
                "semantic_match": semantic_result["score"],
                "competitive_benchmark": benchmark_result["score"],
            },
            "summaries": {
                "visual": visual_result["summary"],
                "ats": ats_result["summary"],
                "semantic": semantic_result["summary"],
                "benchmark": benchmark_result["summary"],
            },
            "metrics": {
                "visual": visual_result["metrics"],
                "ats": ats_result["metrics"],
                "semantic": semantic_result["metrics"],
                "benchmark": benchmark_result["metrics"],
            },
            "hot_zones": visual_result["hot_zones"],
            "recommendations": heuristic_recs,
            "ai_recommendations": ai_recommendations,
            "raw_resume_text": resume_text,
        }

    def _analyze_visual_hierarchy(self, gray: np.ndarray, layout_blocks: List[Dict]) -> Dict[str, Any]:
        h, w = gray.shape[:2]

        edges = cv2.Canny(gray, 80, 180)
        edge_density = float(np.count_nonzero(edges)) / max(float(h * w), 1.0)

        # Story 1: F-pattern signal from concentration in top-left zones.
        third_w = w // 3
        third_h = h // 3
        top_left = np.mean(gray[:third_h, :third_w])
        top_right = np.mean(gray[:third_h, third_w:])
        left_column = np.mean(gray[:, :third_w])
        f_pattern_signal = (255 - top_left) * 0.42 + (255 - left_column) * 0.40 + (255 - top_right) * 0.18

        # Story 2: Visual weight from font size + bold distribution.
        font_sizes = [b.get("font_size", 0.0) for b in layout_blocks] or [10.0]
        bold_weights = [b.get("bold_weight", 0.0) for b in layout_blocks] or [0.0]
        size_variation = float(np.std(font_sizes))
        bold_ratio = float(np.mean(bold_weights))

        # Story 3: 6-second blur test via Gaussian blur and salience retention.
        blurred = cv2.GaussianBlur(gray, (31, 31), 0)
        blur_contrast = float(np.std(blurred))

        # Story 4: Coordinate hot-zones from high-contrast connected components.
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        hot_zones: List[Dict[str, Any]] = []
        for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:8]:
            area = cv2.contourArea(cnt)
            if area < (h * w * 0.002):
                continue
            x, y, cw, ch = cv2.boundingRect(cnt)
            cx = round((x + cw / 2) / w, 4)
            cy = round((y + ch / 2) / h, 4)
            weight = round(min(1.0, area / (h * w * 0.08)), 4)
            hot_zones.append({"x": cx, "y": cy, "weight": weight, "label": "attention-cluster"})

        # Story 5: whitespace ratio.
        white_ratio = float(np.count_nonzero(gray > 245)) / max(float(h * w), 1.0)
        whitespace_score = 100.0 - min(60.0, abs(white_ratio - 0.35) * 180.0)

        f_score = max(0.0, min(100.0, f_pattern_signal / 2.55))
        visual_weight_score = max(0.0, min(100.0, 50 + size_variation * 8 + bold_ratio * 80))
        blur_score = max(0.0, min(100.0, blur_contrast * 1.8))
        zone_score = max(0.0, min(100.0, len(hot_zones) * 12.5 + edge_density * 180))

        final = round(f_score * 0.24 + visual_weight_score * 0.24 + blur_score * 0.20 + zone_score * 0.14 + whitespace_score * 0.18, 2)

        recommendations = []
        if whitespace_score < 80:
            recommendations.append("Increase whitespace toward a 30-40% ratio to reduce visual fatigue.")
        if f_score < 65:
            recommendations.append("Strengthen top-left hierarchy: move core achievements to upper left scan path.")
        if visual_weight_score < 70:
            recommendations.append("Increase contrast between headings and body text to sharpen visual weight.")

        summary = (
            f"Visual audit score {final:.1f}. F-pattern {f_score:.1f}, weight {visual_weight_score:.1f}, "
            f"blur salience {blur_score:.1f}, whitespace {whitespace_score:.1f}."
        )

        return {
            "score": final,
            "summary": summary,
            "hot_zones": hot_zones,
            "metrics": {
                "f_pattern_signal": round(f_score, 2),
                "visual_weight": round(visual_weight_score, 2),
                "blur_salience": round(blur_score, 2),
                "zone_density": round(zone_score, 2),
                "whitespace_ratio": round(white_ratio, 4),
            },
            "recommendations": recommendations,
        }

    def _analyze_ats(self, resume_text: str, layout_blocks: List[Dict]) -> Dict[str, Any]:
        # Story 1: Bot-view reconstruction is represented as normalized plain text.
        plain_text_len = len(resume_text)

        # Story 2: non-standard font detection.
        font_alerts = detect_nonstandard_fonts(self.resume_pdf_path)

        # Story 3: contact field mapping.
        has_email = bool(EMAIL_RE.search(resume_text))
        has_phone = bool(PHONE_RE.search(resume_text))

        # Story 4: header hierarchy check.
        lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
        section_hits = [line for line in lines if SECTION_HEADER_RE.search(line)]

        # Story 5: hidden text scanner heuristic from tiny font blocks.
        tiny_blocks = [b for b in layout_blocks if b.get("font_size", 0.0) < 6.0]

        contact_score = 100.0 if (has_email and has_phone) else 60.0 if (has_email or has_phone) else 20.0
        header_score = min(100.0, len(section_hits) * 15.0)
        font_score = max(0.0, 100.0 - len(font_alerts) * 20.0)
        hidden_text_score = max(0.0, 100.0 - len(tiny_blocks) * 12.0)
        parse_score = min(100.0, max(20.0, plain_text_len / 45.0))

        final = round(contact_score * 0.22 + header_score * 0.22 + font_score * 0.18 + hidden_text_score * 0.18 + parse_score * 0.20, 2)

        recommendations = []
        if not has_email:
            recommendations.append("Add a clearly parseable email near the top of page one.")
        if not has_phone:
            recommendations.append("Add a phone number in international-friendly format.")
        if len(section_hits) < 4:
            recommendations.append("Use standard section headers (Summary, Experience, Skills, Projects, Education).")
        if font_alerts:
            recommendations.append("Replace non-standard/Type3 fonts with ATS-friendly fonts (Calibri, Arial, Helvetica).")
        if tiny_blocks:
            recommendations.append("Avoid tiny or hidden text blocks that can trigger ATS quality issues.")

        summary = (
            f"ATS integrity {final:.1f}. Contact mapping {contact_score:.1f}, structure {header_score:.1f}, "
            f"font safety {font_score:.1f}, hidden-text safety {hidden_text_score:.1f}."
        )

        return {
            "score": final,
            "summary": summary,
            "metrics": {
                "plain_text_length": plain_text_len,
                "section_headers_detected": len(section_hits),
                "font_alert_count": len(font_alerts),
                "tiny_block_count": len(tiny_blocks),
                "email_found": has_email,
                "phone_found": has_phone,
                "font_alerts": font_alerts,
            },
            "recommendations": recommendations,
        }

    def _analyze_semantic(self, resume_text: str) -> Dict[str, Any]:
        differential = keyword_cloud_differential(self.job_description, resume_text)
        semantic_score = semantic_alignment_score(self.job_description, resume_text)
        skill_balance_score, skill_notes = skill_frequency_health(self.job_description, resume_text)
        synonyms = synonym_suggestions(self.job_description, resume_text)
        buzzword_fixes = buzzword_replacements(resume_text)
        missing_skills = missing_skill_prioritization(self.job_description, resume_text)

        top_deltas = dict(sorted(differential.items(), key=lambda x: abs(x[1]), reverse=True)[:12])
        missing_priority_weight = max(0.0, 100.0 - len(missing_skills) * 4.6)

        final = round(semantic_score * 0.50 + skill_balance_score * 0.30 + missing_priority_weight * 0.20, 2)

        recommendations = []
        recommendations.extend(synonyms[:5])
        recommendations.extend(buzzword_fixes[:5])
        if missing_skills:
            recommendations.append(f"Prioritize adding evidence-backed mentions for: {', '.join(missing_skills[:6])}.")

        summary = (
            f"Semantic match {final:.1f}. JD overlap {semantic_score:.1f}, frequency health {skill_balance_score:.1f}, "
            f"missing-skill pressure {100 - missing_priority_weight:.1f}."
        )

        return {
            "score": final,
            "summary": summary,
            "metrics": {
                "jd_resume_differential": top_deltas,
                "skill_frequency_notes": skill_notes,
                "missing_skills": missing_skills,
                "synonym_suggestions": synonyms,
            },
            "recommendations": recommendations,
        }

    def _analyze_benchmark(self, resume_text: str, ats_result: Dict[str, Any]) -> Dict[str, Any]:
        pages = max(1, self._estimate_page_count(resume_text))
        bullet_count = self._count_bullets(resume_text)
        years = self._extract_years_experience(resume_text)
        unique_skills = list({token for token in tokenize(resume_text) if len(token) > 2})

        result = benchmark_score(
            job_category=self.job_category,
            page_count=pages,
            bullet_count=bullet_count,
            years_experience_found=years,
            unique_skills=unique_skills,
        )

        percentile = round(min(99.0, 35.0 + result["score"] * 0.55), 2)
        result["summary"] += f" Estimated candidate percentile: P{percentile:.1f}."
        result["metrics"] = {
            "estimated_page_count": pages,
            "bullet_count": bullet_count,
            "years_experience_found": years,
            "market_percentile_estimate": percentile,
            "ats_structure_score": ats_result.get("score", 0.0),
            "rare_skill_hits": result.get("rare_hits", []),
            "subscores": result.get("subscores", {}),
        }
        return result

    @staticmethod
    def _estimate_page_count(resume_text: str) -> int:
        # Coarse approximation when exact metadata is not available.
        return max(1, math.ceil(len(resume_text) / 3200))

    @staticmethod
    def _count_bullets(text: str) -> int:
        return sum(1 for line in text.splitlines() if line.strip().startswith(("-", "*", "•")))

    @staticmethod
    def _extract_years_experience(text: str) -> float:
        matches = [float(m.group(1)) for m in YEARS_RE.finditer(text)]
        if not matches:
            return 0.0
        return max(matches)

    @staticmethod
    def _prioritize_recommendations(recommendations: List[str]) -> List[str]:
        deduped = []
        seen = set()
        for rec in recommendations:
            normalized = rec.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                deduped.append(rec.strip())
        return deduped[:20]

    def _gemini_recommendations(
        self,
        resume_text: str,
        heuristic_recs: List[str],
        scores: Dict[str, float],
    ) -> List[str]:
        """
        2.1: Use Gemini to rewrite terse heuristic recommendations into
        actionable, natural-language coaching paragraphs.
        Falls back to empty list if Gemini is unavailable.
        """
        if not gemini_client.is_available() or not resume_text.strip():
            return []

        recs_text = "\n".join(f"- {r}" for r in heuristic_recs[:8])
        prompt = (
            f"You are a professional resume coach. A candidate's resume scored:\n"
            f"  Overall: {scores['overall']:.1f}/100\n"
            f"  Visual hierarchy: {scores['visual']:.1f}/100\n"
            f"  ATS integrity: {scores['ats']:.1f}/100\n"
            f"  Semantic match: {scores['semantic']:.1f}/100\n"
            f"  Competitive benchmark: {scores['benchmark']:.1f}/100\n\n"
            f"Heuristic issues detected:\n{recs_text}\n\n"
            f"Resume excerpt (first 1200 chars):\n\"\"\"{resume_text[:1200]}\"\"\"\n\n"
            "Write exactly 5 coaching recommendations. Each must be:\n"
            "- One clear, actionable sentence (max 25 words)\n"
            "- Specific to this resume's actual content\n"
            "- Prioritized by impact on recruiter callback rate\n"
            "Format: numbered list 1-5. No headers, no extra text."
        )

        raw = gemini_client.generate(prompt, temperature=0.3, max_tokens=400)
        if not raw:
            return []

        lines = [
            re.sub(r"^\d+[\.\)]\s*", "", ln).strip()
            for ln in raw.splitlines()
            if ln.strip() and len(ln.strip()) > 10
        ]
        return [ln for ln in lines if ln][:5]


# ── 2.2: Standalone JD quality scorer ────────────────────────────────────────

def score_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Analyse a job description and return a quality score + actionable feedback.
    Used by POST /api/feature1/analyze-jd.
    """
    if not jd_text or not jd_text.strip():
        return {
            "quality_score": 0,
            "grade": "empty",
            "issues": ["Job description is empty."],
            "word_count": 0,
            "ai_feedback": "",
        }

    words = jd_text.split()
    word_count = len(words)
    issues: List[str] = []
    score = 100

    # Length checks
    if word_count < 80:
        issues.append("JD is too short (< 80 words) — semantic matching will be unreliable.")
        score -= 30
    elif word_count < 150:
        issues.append("JD is brief (< 150 words) — add responsibilities and required skills.")
        score -= 15

    # Skill signal
    tech_pattern = re.compile(
        r"\b(python|javascript|typescript|react|node|sql|aws|docker|kubernetes|"
        r"fastapi|django|postgres|redis|kafka|graphql|terraform|ci|cd|testing|"
        r"llm|machine learning|data|api|backend|frontend|fullstack)\b",
        re.I,
    )
    skill_hits = tech_pattern.findall(jd_text)
    if len(skill_hits) < 3:
        issues.append("JD mentions fewer than 3 recognisable technical skills — add specific stack requirements.")
        score -= 20

    # Responsibility signal
    if not re.search(r"\b(responsibilit|you will|you'll|duties|role involves)\b", jd_text, re.I):
        issues.append("JD lacks a responsibilities section — candidates can't self-screen effectively.")
        score -= 15

    # Seniority signal
    if not re.search(r"\b(\d+\+?\s*years?|senior|junior|mid|lead|staff|principal)\b", jd_text, re.I):
        issues.append("JD doesn't specify seniority level or years of experience required.")
        score -= 10

    score = max(0, min(100, score))
    grade = "excellent" if score >= 85 else "good" if score >= 65 else "fair" if score >= 45 else "poor"

    # Gemini enhancement
    ai_feedback = ""
    if gemini_client.is_available():
        prompt = (
            f"You are a hiring manager reviewing this job description:\n\n"
            f"\"\"\"{jd_text[:1500]}\"\"\"\n\n"
            "In 2 sentences, explain the single biggest weakness of this JD "
            "and how to fix it to attract better candidates. Be direct and specific."
        )
        ai_feedback = gemini_client.generate(prompt, temperature=0.3, max_tokens=150)

    return {
        "quality_score": score,
        "grade": grade,
        "word_count": word_count,
        "skill_hits": list(set(s.lower() for s in skill_hits)),
        "issues": issues,
        "ai_feedback": ai_feedback,
    }


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)
