from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any, Dict, List, Sequence, Tuple

TECH_KEYWORDS = {
    "api",
    "rest",
    "graphql",
    "sql",
    "database",
    "index",
    "latency",
    "cache",
    "concurrency",
    "thread",
    "async",
    "queue",
    "docker",
    "kubernetes",
    "react",
    "typescript",
    "python",
    "fastapi",
    "testing",
    "ci",
    "cd",
}

CONFIDENCE_WORDS = {"definitely", "obviously", "always", "sure", "certainly", "clearly", "100%"}
HEDGE_WORDS = {"maybe", "perhaps", "i think", "not sure", "probably", "kind of"}
WHY_DEPTH_WORDS = {"because", "tradeoff", "constraint", "latency", "scalability", "consistency", "reliability"}

POSITIVE_TONE = {"calm", "curious", "collaborative", "confident", "focused", "grateful"}
NEGATIVE_TONE = {"desperate", "panic", "anxious", "hopeless", "frustrated", "stuck"}

FILLER_PATTERN = re.compile(r"\b(um+|uh+|like|you know|basically|actually)\b", re.I)
QUESTION_PATTERN = re.compile(r"([^\n\r\?]{8,}\?)")
TIMECODE_VTT_RE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}$")


@dataclass
class ParsedTranscript:
    clean_text: str
    utterances: List[str]


class Feature2Engine:
    def __init__(
        self,
        interview_notes: str,
        transcript_text: str,
        transcript_vtt: str,
        technical_expectations: Sequence[str],
        culture_vibe: str,
        interviewer_friendliness: int,
        interview_round: str,
        lifecycle_stage: str,
        hardest_question_hint: str,
        advanced_round_reached: bool,
        rejection_reason_hint: str,
        interview_outcome: str,
    ) -> None:
        self.interview_notes = interview_notes.strip()
        self.transcript_text = transcript_text.strip()
        self.transcript_vtt = transcript_vtt.strip()
        self.technical_expectations = [x.strip() for x in technical_expectations if x.strip()]
        self.culture_vibe = culture_vibe.strip().lower()
        self.interviewer_friendliness = interviewer_friendliness
        self.interview_round = interview_round
        self.lifecycle_stage = lifecycle_stage
        self.hardest_question_hint = hardest_question_hint.strip()
        self.advanced_round_reached = advanced_round_reached
        self.rejection_reason_hint = rejection_reason_hint.strip().lower()
        self.interview_outcome = interview_outcome.strip().lower()

    def run(self) -> Dict[str, Any]:
        parsed = self._ingest_transcript()
        full_text = "\n".join([self.interview_notes, parsed.clean_text]).strip()

        ingestion = self._ingestion_analysis(parsed, full_text)
        technical = self._technical_analysis(full_text, ingestion["challenge_question"])
        behavioral = self._behavioral_analysis(full_text)
        strategic = self._strategic_actions(technical, behavioral, ingestion)
        score = self._scorecard(technical, behavioral, strategic)

        snapshot = {
            "rejection_category": self._rejection_category(technical, behavioral),
            "success_signal": "high" if self.advanced_round_reached else "low",
            "topic_signals": technical.get("topic_hits", []),
        }

        return {
            "ingestion": ingestion,
            "technical": technical,
            "behavioral": behavioral,
            "strategic_actions": strategic,
            "score": score,
            "analytics_snapshot": snapshot,
        }

    def quick_debrief(self, debrief_text: str) -> Dict[str, Any]:
        challenge = self._extract_hardest_question(debrief_text)
        failures = self._infer_failure_themes(debrief_text)
        next_actions = self._immediate_actions_from_themes(failures)
        return {
            "extracted_hardest_question": challenge,
            "top_failure_themes": failures,
            "immediate_next_actions": next_actions,
        }

    def _ingest_transcript(self) -> ParsedTranscript:
        if self.transcript_text:
            utterances = [u.strip() for u in self.transcript_text.splitlines() if u.strip()]
            return ParsedTranscript(clean_text="\n".join(utterances), utterances=utterances)

        if self.transcript_vtt:
            lines = [line.strip() for line in self.transcript_vtt.splitlines()]
            utterances = []
            for line in lines:
                if not line or line.startswith("WEBVTT") or line.isdigit() or TIMECODE_VTT_RE.match(line):
                    continue
                utterances.append(line)
            return ParsedTranscript(clean_text="\n".join(utterances), utterances=utterances)

        return ParsedTranscript(clean_text=self.interview_notes, utterances=[self.interview_notes] if self.interview_notes else [])

    def _ingestion_analysis(self, parsed: ParsedTranscript, full_text: str) -> Dict[str, Any]:
        challenge_question = self.hardest_question_hint or self._extract_hardest_question(full_text)

        vibe_score = self._culture_vibe_score(self.culture_vibe, self.interviewer_friendliness)
        lifecycle = self.lifecycle_stage.lower() if self.lifecycle_stage else self.interview_round.lower()

        return {
            "transcript_line_count": len(parsed.utterances),
            "culture_vibe": self.culture_vibe,
            "friendliness": self.interviewer_friendliness,
            "culture_score": vibe_score,
            "challenge_question": challenge_question,
            "lifecycle_stage": lifecycle,
            "voice_to_text_captured": bool(self.interview_notes),
            "vtt_parsed": bool(self.transcript_vtt),
        }

    def _technical_analysis(self, text: str, challenge_question: str) -> Dict[str, Any]:
        lower = text.lower()

        expectation_hits = [topic for topic in self.technical_expectations if topic.lower() in lower]
        topic_hits = sorted({kw for kw in TECH_KEYWORDS if kw in lower})

        semantic_correctness = min(100.0, 38.0 + len(expectation_hits) * 14.0 + len(topic_hits) * 1.7)
        depth_of_why = min(100.0, sum(lower.count(w) for w in WHY_DEPTH_WORDS) * 8.0 + 30.0)

        false_confidence_zones = self._detect_false_confidence(text)
        confidence_penalty = min(40.0, len(false_confidence_zones) * 8.0)

        perfect_response = self._generate_perfect_response(challenge_question, expectation_hits, topic_hits)
        remedial_links = self._remedial_links(expectation_hits or topic_hits)

        tech_score = max(0.0, min(100.0, semantic_correctness * 0.55 + depth_of_why * 0.45 - confidence_penalty))

        return {
            "semantic_correctness": round(semantic_correctness, 2),
            "depth_of_why": round(depth_of_why, 2),
            "false_confidence_zones": false_confidence_zones,
            "perfect_response": perfect_response,
            "remedial_links": remedial_links,
            "topic_hits": topic_hits,
            "expectation_hits": expectation_hits,
            "score": round(tech_score, 2),
        }

    def _behavioral_analysis(self, text: str) -> Dict[str, Any]:
        lower = text.lower()
        fillers = FILLER_PATTERN.findall(lower)

        answers = [x.strip() for x in text.split("?") if x.strip()]
        lengths = [len(a.split()) for a in answers] or [0]
        avg_len = mean(lengths)

        star_presence = {
            "situation": int("situation" in lower or "context" in lower),
            "task": int("task" in lower or "goal" in lower),
            "action": int("action" in lower or "i built" in lower or "i implemented" in lower),
            "result": int("result" in lower or "impact" in lower or "%" in lower),
        }
        star_score = sum(star_presence.values()) / 4.0 * 100.0

        asked_back = [q.strip() for q in QUESTION_PATTERN.findall(text) if len(q.split()) >= 5]
        question_quality = min(100.0, len(asked_back) * 20.0)

        tone_heatmap = self._tone_heatmap(text)

        length_score = 100.0
        if avg_len < 18:
            length_score = 60.0
        elif avg_len > 95:
            length_score = 58.0

        filler_penalty = min(35.0, len(fillers) * 2.2)

        behavior_score = max(0.0, min(100.0, star_score * 0.35 + question_quality * 0.25 + length_score * 0.25 + (100 - filler_penalty) * 0.15))

        return {
            "filler_word_count": len(fillers),
            "filler_examples": fillers[:10],
            "avg_answer_length_words": round(avg_len, 2),
            "length_score": round(length_score, 2),
            "star_validation": star_presence,
            "star_score": round(star_score, 2),
            "questions_asked_back": asked_back,
            "question_quality": round(question_quality, 2),
            "tone_heatmap": tone_heatmap,
            "score": round(behavior_score, 2),
        }

    def _strategic_actions(self, technical: Dict[str, Any], behavioral: Dict[str, Any], ingestion: Dict[str, Any]) -> Dict[str, Any]:
        clarification_email = self._clarification_email(ingestion["challenge_question"], technical["perfect_response"])

        now = datetime.now(timezone.utc)
        follow_up_cadence = [
            {
                "offset_hours": 24,
                "scheduled_at": (now + timedelta(hours=24)).isoformat(),
                "message": "Thank-you + concise clarification on one technical point.",
            },
            {
                "offset_hours": 168,
                "scheduled_at": (now + timedelta(days=7)).isoformat(),
                "message": "Polite follow-up asking for timeline and reaffirming fit.",
            },
        ]

        negotiation_scripts = self._negotiation_scripts()
        code_patch = self._post_failure_code_patch(ingestion["challenge_question"])
        resilience_prompt = self._resilience_prompt(technical, behavioral)

        recovery_score = min(
            100.0,
            35.0
            + (100 - min(40.0, len(technical.get("false_confidence_zones", [])) * 8.0)) * 0.25
            + behavioral.get("star_score", 0.0) * 0.2
            + behavioral.get("question_quality", 0.0) * 0.2,
        )

        return {
            "clarification_email": clarification_email,
            "follow_up_cadence": follow_up_cadence,
            "negotiation_scripts": negotiation_scripts,
            "post_failure_code_patch": code_patch,
            "resilience_prompt": resilience_prompt,
            "score": round(recovery_score, 2),
        }

    def _scorecard(self, technical: Dict[str, Any], behavioral: Dict[str, Any], strategic: Dict[str, Any]) -> Dict[str, float]:
        confidence_risk = min(100.0, len(technical["false_confidence_zones"]) * 16.0)
        overall = technical["score"] * 0.42 + behavioral["score"] * 0.32 + strategic["score"] * 0.26
        return {
            "technical_accuracy": round(technical["score"], 2),
            "behavioral_quality": round(behavioral["score"], 2),
            "strategic_recovery_readiness": round(strategic["score"], 2),
            "confidence_risk": round(confidence_risk, 2),
            "overall_autopsy_score": round(overall, 2),
        }

    def _culture_vibe_score(self, vibe: str, friendliness: int) -> float:
        vibe_bias = {
            "friendly": 20,
            "neutral": 0,
            "cold": -10,
            "hostile": -20,
        }.get(vibe, 0)
        return float(max(0, min(100, 50 + vibe_bias + friendliness * 4)))

    def _extract_hardest_question(self, text: str) -> str:
        questions = [q.strip() for q in QUESTION_PATTERN.findall(text)]
        if not questions:
            return "No explicit question found; capture verbally remembered hardest challenge."

        ranked = sorted(questions, key=lambda q: (sum(k in q.lower() for k in TECH_KEYWORDS), len(q)), reverse=True)
        return ranked[0]

    def _detect_false_confidence(self, text: str) -> List[Dict[str, Any]]:
        zones = []
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            low = s.lower()
            confidence_hits = [w for w in CONFIDENCE_WORDS if w in low]
            hedge_hits = [w for w in HEDGE_WORDS if w in low]
            technical_hits = [k for k in TECH_KEYWORDS if k in low]
            if confidence_hits and technical_hits and not any(word in low for word in WHY_DEPTH_WORDS):
                zones.append(
                    {
                        "sentence": s.strip()[:220],
                        "confidence_markers": confidence_hits,
                        "technical_markers": technical_hits[:4],
                        "risk": "high",
                    }
                )
            elif confidence_hits and hedge_hits:
                zones.append(
                    {
                        "sentence": s.strip()[:220],
                        "confidence_markers": confidence_hits,
                        "technical_markers": technical_hits[:4],
                        "risk": "medium",
                    }
                )
        return zones[:8]

    def _generate_perfect_response(self, challenge_question: str, expectations: List[str], topic_hits: List[str]) -> str:
        focus = expectations[:3] if expectations else topic_hits[:3]
        focus_line = ", ".join(focus) if focus else "core fundamentals"
        return (
            f"For the question '{challenge_question}', a stronger response should: (1) define the problem clearly, "
            f"(2) explain trade-offs using {focus_line}, (3) propose a pragmatic design, and (4) quantify impact "
            f"with latency, reliability, or user-value metrics."
        )

    def _remedial_links(self, skills: Sequence[str]) -> List[Dict[str, str]]:
        mapping = {
            "react": ("MDN React ecosystem basics", "https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks"),
            "typescript": ("TypeScript Handbook", "https://www.typescriptlang.org/docs/"),
            "sql": ("SQL Performance Tuning", "https://www.youtube.com/watch?v=HXV3zeQKqGY"),
            "api": ("REST API Design", "https://www.youtube.com/watch?v=7YcW25PHnAA"),
            "docker": ("Docker getting started", "https://docs.docker.com/get-started/"),
            "kubernetes": ("Kubernetes Basics", "https://kubernetes.io/docs/tutorials/kubernetes-basics/"),
            "fastapi": ("FastAPI docs", "https://fastapi.tiangolo.com/"),
            "testing": ("Python testing", "https://docs.pytest.org/"),
        }

        links = []
        for skill in skills:
            key = skill.lower()
            if key in mapping:
                title, url = mapping[key]
                links.append({"skill": key, "title": title, "url": url})

        if not links:
            links.append({"skill": "general", "title": "Interview prep fundamentals", "url": "https://www.youtube.com/watch?v=KdXAUst8bdo"})
        return links[:8]

    def _tone_heatmap(self, text: str) -> Dict[str, Any]:
        segments = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        bins = []
        for i, seg in enumerate(segments[:12]):
            low = seg.lower()
            pos = sum(word in low for word in POSITIVE_TONE)
            neg = sum(word in low for word in NEGATIVE_TONE)
            score = max(-1.0, min(1.0, (pos - neg) / 3.0))
            label = "calm" if score > 0.15 else "desperate" if score < -0.2 else "neutral"
            bins.append({"segment": i + 1, "score": round(score, 2), "label": label})

        avg = mean([b["score"] for b in bins]) if bins else 0.0
        return {
            "segments": bins,
            "average_sentiment": round(avg, 2),
            "overall_label": "calm" if avg > 0.15 else "desperate" if avg < -0.2 else "mixed",
        }

    def _clarification_email(self, challenge_question: str, perfect_response: str) -> str:
        return (
            "Subject: Follow-up and Clarification\n\n"
            "Hi Interview Team,\n\n"
            f"Thank you again for the conversation today. I wanted to briefly clarify one point from the discussion around: '{challenge_question}'.\n\n"
            f"My refined answer: {perfect_response}\n\n"
            "I appreciate your time and would be excited to continue in the process.\n\n"
            "Best,\nCandidate"
        )

    def _negotiation_scripts(self) -> Dict[str, str]:
        return {
            "offer_received": (
                "Thank you for the offer. I am excited about the role and team. Based on my scope ownership, impact history, "
                "and market range for this level, would you be open to discussing total compensation in the X-Y range?"
            ),
            "verbal_positive_signal": (
                "I am very interested and can move quickly. Could you share the expected level and compensation band so we can "
                "align early and avoid delays?"
            ),
        }

    def _post_failure_code_patch(self, challenge_question: str) -> Dict[str, str]:
        hint = challenge_question.lower()
        if "cache" in hint:
            return {
                "title": "Add LRU cache layer",
                "description": "Implement request-level LRU caching with TTL and benchmark p95 latency before/after.",
            }
        if "sql" in hint or "database" in hint:
            return {
                "title": "Optimize query path",
                "description": "Add indexes, remove N+1 patterns, and document EXPLAIN plan changes in repo notes.",
            }
        if "api" in hint:
            return {
                "title": "Harden API contracts",
                "description": "Add request validation, idempotency handling, and integration tests for edge cases.",
            }
        return {
            "title": "Stability patch",
            "description": "Add tests for the failed scenario, improve error handling, and include a concise postmortem note.",
        }

    def _resilience_prompt(self, technical: Dict[str, Any], behavioral: Dict[str, Any]) -> str:
        return (
            "Reframe: this interview produced diagnostic data, not a personal verdict. "
            f"Your next leverage points are technical depth ({technical['depth_of_why']}) and STAR precision ({behavioral['star_score']}). "
            "Convert one weak answer into a documented practice drill within 24 hours."
        )

    def _rejection_category(self, technical: Dict[str, Any], behavioral: Dict[str, Any]) -> str:
        if self.rejection_reason_hint:
            hint = self.rejection_reason_hint
            if any(x in hint for x in ["culture", "team fit", "communication"]):
                return "culture"
            if any(x in hint for x in ["salary", "budget", "compensation", "pay"]):
                return "pay"
            if any(x in hint for x in ["skill", "technical", "architecture", "coding"]):
                return "skill"

        if technical["score"] < behavioral["score"] - 10:
            return "skill"
        if behavioral["score"] < technical["score"] - 10:
            return "culture"
        return "mixed"

    def _infer_failure_themes(self, text: str) -> List[str]:
        low = text.lower()
        themes = []
        if any(k in low for k in ["stuck", "freeze", "blank"]):
            themes.append("freeze_under_pressure")
        if any(k in low for k in ["ramble", "too long", "unclear"]):
            themes.append("communication_clarity")
        if any(k in low for k in ["didn't know", "not sure", "missed"]):
            themes.append("technical_gaps")
        if any(k in low for k in ["culture", "fit", "attitude"]):
            themes.append("culture_alignment")
        return themes[:4] or ["insufficient_signal"]

    def _immediate_actions_from_themes(self, themes: List[str]) -> List[str]:
        action_map = {
            "freeze_under_pressure": "Practice 3 timed answers with a 90-second response cap.",
            "communication_clarity": "Rewrite 5 stories in strict STAR format with measurable results.",
            "technical_gaps": "Pick top 2 missing concepts and complete one focused drill each today.",
            "culture_alignment": "Prepare 3 collaboration stories emphasizing conflict resolution and ownership.",
            "insufficient_signal": "Record a full debrief within 15 minutes after your next interview.",
        }
        return [action_map[t] for t in themes if t in action_map]


def trend_from_rows(rows: Sequence[Any]) -> Dict[str, Any]:
    points = []
    for row in rows[-5:]:
        score = json.loads(row.score_json)
        points.append(
            {
                "interview_id": row.id,
                "created_at": row.created_at,
                "technical_accuracy": score["technical_accuracy"],
                "behavioral_quality": score["behavioral_quality"],
                "recovery_readiness": score["strategic_recovery_readiness"],
                "overall_score": score["overall_autopsy_score"],
            }
        )

    if not points:
        return {"points": [], "trend_summary": {"overall_delta": 0.0, "technical_delta": 0.0, "behavioral_delta": 0.0}}

    first, last = points[0], points[-1]
    return {
        "points": points,
        "trend_summary": {
            "overall_delta": round(last["overall_score"] - first["overall_score"], 2),
            "technical_delta": round(last["technical_accuracy"] - first["technical_accuracy"], 2),
            "behavioral_delta": round(last["behavioral_quality"] - first["behavioral_quality"], 2),
        },
    }


def readiness_forecast(rows: Sequence[Any]) -> Dict[str, Any]:
    if not rows:
        return {
            "readiness_score": 20.0,
            "forecast_label": "early-stage",
            "expected_offer_window_weeks": 16,
            "rationale": ["No interview history yet; collect at least 3 autopsies for stable forecast."],
        }

    scores = [json.loads(r.score_json)["overall_autopsy_score"] for r in rows[-5:]]
    avg = mean(scores)
    momentum = scores[-1] - scores[0] if len(scores) > 1 else 0.0

    readiness = max(0.0, min(100.0, avg * 0.8 + momentum * 0.5 + 15.0))

    if readiness >= 78:
        label = "high-readiness"
        window = 3
    elif readiness >= 60:
        label = "rising-readiness"
        window = 6
    elif readiness >= 42:
        label = "developing"
        window = 10
    else:
        label = "rebuild-phase"
        window = 14

    rationale = [
        f"Recent average autopsy score is {avg:.1f}.",
        f"Momentum across last interviews is {momentum:+.1f} points.",
        "Strengthen weak dimensions before increasing application volume.",
    ]

    return {
        "readiness_score": round(readiness, 2),
        "forecast_label": label,
        "expected_offer_window_weeks": window,
        "rationale": rationale,
    }
