from __future__ import annotations

import json
import random
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any, Dict, List, Sequence

FILLER_RE = re.compile(r"\b(um+|uh+|like|you know|basically|actually)\b", re.I)
NEGATIVE_RE = re.compile(r"\b(stuck|panic|anxious|freeze|hopeless|desperate)\b", re.I)
POSITIVE_RE = re.compile(r"\b(calm|curious|clear|confident|structured|focused)\b", re.I)
HEDGE_RE = re.compile(r"\b(maybe|perhaps|not sure|i think|probably|kind of)\b", re.I)
TRADEOFF_WORDS = {"trade-off", "tradeoff", "latency", "consistency", "reliability", "scale", "cost"}


@dataclass
class PersonaProfile:
    key: str
    label: str
    style: str
    pressure: int
    question_tempo: str
    reinforcement: str


PERSONAS: Dict[str, PersonaProfile] = {
    "stone_faced": PersonaProfile(
        key="stone_faced",
        label="Stone-Faced Architect",
        style="minimal feedback, deep architecture pressure",
        pressure=9,
        question_tempo="steady",
        reinforcement="none",
    ),
    "rushed_founder": PersonaProfile(
        key="rushed_founder",
        label="Rushed Founder",
        style="high speed interruptions and priority pivots",
        pressure=8,
        question_tempo="rapid",
        reinforcement="low",
    ),
    "non_tech_hr": PersonaProfile(
        key="non_tech_hr",
        label="Non-Tech HR",
        style="ELI5 framing and clarity stress test",
        pressure=6,
        question_tempo="moderate",
        reinforcement="medium",
    ),
    "deep_diver": PersonaProfile(
        key="deep_diver",
        label="Deep-Diver",
        style="layered why-question chains",
        pressure=9,
        question_tempo="deep",
        reinforcement="low",
    ),
}


class Feature4PersonaPlayEngine:
    def select_persona(self, persona_mode: str, selected_persona: str | None = None) -> PersonaProfile:
        if persona_mode == "blind":
            return random.choice(list(PERSONAS.values()))

        key = (selected_persona or persona_mode or "stone_faced").strip().lower()
        return PERSONAS.get(key, PERSONAS["stone_faced"])

    def opening_questions(self, persona: PersonaProfile, role_name: str) -> List[Dict[str, Any]]:
        return [
            {
                "type": "baseline",
                "question": f"In 90 seconds, explain a recent {role_name} project and your biggest trade-off.",
                "persona_tone": persona.style,
            },
            {
                "type": "tradeoff_trigger",
                "question": "What downside did your chosen approach introduce, and why did you accept it?",
                "persona_tone": persona.style,
            },
            {
                "type": "scale_up_scenario",
                "question": "Traffic is now 15x and latency SLO dropped to 120ms. What changes first?",
                "persona_tone": persona.style,
            },
            {
                "type": "behavioral_trap",
                "question": "A teammate blocks your release and blames your design publicly. How do you respond?",
                "persona_tone": persona.style,
            },
            {
                "type": "negotiation_curveball",
                "question": "Before we continue, what compensation range are you targeting and why?",
                "persona_tone": persona.style,
            },
        ]

    def analyze_realtime(
        self,
        utterance: str,
        response_latency_ms: int,
        audio_pitch_variance: float,
        silent_seconds: float,
        gaze_focus_ratio: float,
    ) -> Dict[str, Any]:
        low = utterance.lower()
        filler_hits = FILLER_RE.findall(low)

        filler_score = max(0.0, 100.0 - len(filler_hits) * 5.5)
        pitch_confidence = max(0.0, min(100.0, 95 - abs(audio_pitch_variance - 0.55) * 120))
        silence_freeze_score = max(0.0, min(100.0, 100 - silent_seconds * 8 - response_latency_ms / 700))

        pos = len(POSITIVE_RE.findall(low))
        neg = len(NEGATIVE_RE.findall(low))
        sentiment = max(-1.0, min(1.0, (pos - neg) / 4))

        tone_label = "calm" if sentiment > 0.2 else "desperate" if sentiment < -0.25 else "mixed"
        gaze_score = max(0.0, min(100.0, gaze_focus_ratio * 100))

        return {
            "filler_tracker": {
                "count": len(filler_hits),
                "examples": filler_hits[:8],
                "score": round(filler_score, 2),
            },
            "pitch_analysis": {
                "variance": round(audio_pitch_variance, 3),
                "confidence_score": round(pitch_confidence, 2),
                "upspeak_risk": "high" if audio_pitch_variance > 0.95 else "medium" if audio_pitch_variance > 0.75 else "low",
            },
            "silence_detection": {
                "silent_seconds": round(silent_seconds, 2),
                "response_latency_ms": response_latency_ms,
                "freeze_risk": "high" if (silent_seconds > 6 or response_latency_ms > 9000) else "medium" if (silent_seconds > 3 or response_latency_ms > 4500) else "low",
                "score": round(silence_freeze_score, 2),
            },
            "tone_correlation": {
                "sentiment_score": round(sentiment, 2),
                "label": tone_label,
            },
            "gaze_tracking": {
                "focus_ratio": round(gaze_focus_ratio, 3),
                "eye_contact_score": round(gaze_score, 2),
                "label": "stable" if gaze_score >= 70 else "drifting" if gaze_score >= 45 else "avoidant",
            },
        }

    def deep_logic_probe(self, persona: PersonaProfile, utterance: str) -> Dict[str, Any]:
        low = utterance.lower()
        has_tradeoff = any(tok in low for tok in TRADEOFF_WORDS)
        has_hedge = bool(HEDGE_RE.search(low))

        collaborative_debug = {
            "prompt": "You have this bug: p95 latency spikes after cache warm-up. Walk me through your first 3 debug steps.",
            "expectation": ["hypothesis", "measurement", "rollback/fix plan"],
        }

        return {
            "tradeoff_trigger": "Quantify the downside and justify why it was acceptable under constraints.",
            "scale_up_scenario": "Assume 10x reads and 5x writes; redesign critical path in two minutes.",
            "collaborative_debugging": collaborative_debug,
            "behavioral_trap": "A senior dismisses your design in front of team. What do you do in the next 5 minutes?",
            "negotiation_curveball": "Share your compensation ask and the impact evidence behind it.",
            "analysis": {
                "tradeoff_depth": "strong" if has_tradeoff and not has_hedge else "needs_depth",
                "hedge_detected": has_hedge,
            },
        }

    def whisper_hint(self, realtime: Dict[str, Any], deep_logic: Dict[str, Any]) -> str:
        silence = realtime["silence_detection"]["freeze_risk"]
        filler_count = realtime["filler_tracker"]["count"]
        tone = realtime["tone_correlation"]["label"]

        if silence == "high":
            return "Pause. Use a 3-step frame: context, trade-off, decision. Speak one line at a time."
        if filler_count >= 6:
            return "Reduce fillers by slowing pace 15%. End each sentence with one concrete metric or decision."
        if tone == "desperate":
            return "Reset tone: be concise, neutral, and evidence-first. Mention measurable impact before opinion."
        if deep_logic["analysis"]["tradeoff_depth"] == "needs_depth":
            return "Add explicit downside + mitigation. Interviewers reward transparent trade-off thinking."
        return "Good control. Keep answers in STAR + trade-off format."

    def next_question(self, persona: PersonaProfile, turn_index: int, deep_logic: Dict[str, Any]) -> Dict[str, Any]:
        cycle = [
            ("tradeoff_trigger", deep_logic["tradeoff_trigger"]),
            ("scale_up_scenario", deep_logic["scale_up_scenario"]),
            ("collaborative_debugging", deep_logic["collaborative_debugging"]["prompt"]),
            ("behavioral_trap", deep_logic["behavioral_trap"]),
            ("negotiation_curveball", deep_logic["negotiation_curveball"]),
        ]
        kind, question = cycle[turn_index % len(cycle)]
        return {"type": kind, "question": question, "persona_tone": persona.style}

    def summarize_realtime(self, signals: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        if not signals:
            return {
                "filler_avg": 0.0,
                "confidence_avg": 0.0,
                "freeze_risk_avg": 0.0,
                "tone_label": "unknown",
                "gaze_avg": 0.0,
            }

        filler = mean(s["filler_tracker"]["score"] for s in signals)
        confidence = mean(s["pitch_analysis"]["confidence_score"] for s in signals)
        freeze = mean(s["silence_detection"]["score"] for s in signals)
        gaze = mean(s["gaze_tracking"]["eye_contact_score"] for s in signals)
        sentiment = mean(s["tone_correlation"]["sentiment_score"] for s in signals)

        tone_label = "calm" if sentiment > 0.15 else "desperate" if sentiment < -0.2 else "mixed"
        return {
            "filler_avg": round(filler, 2),
            "confidence_avg": round(confidence, 2),
            "freeze_risk_avg": round(freeze, 2),
            "tone_label": tone_label,
            "gaze_avg": round(gaze, 2),
        }

    def finalize_feedback(
        self,
        persona: PersonaProfile,
        turns: Sequence[Dict[str, Any]],
        previous_summaries: Sequence[Dict[str, Any]],
    ) -> Dict[str, Any]:
        signals = [t["realtime"] for t in turns]
        summary = self.summarize_realtime(signals)

        logic_depth = self._logic_depth_score(turns)
        behavioral = (summary["filler_avg"] * 0.25 + summary["gaze_avg"] * 0.2 + summary["freeze_risk_avg"] * 0.2 + summary["confidence_avg"] * 0.35)
        overall = logic_depth * 0.52 + behavioral * 0.48

        transcript = self._transcript_breakdown(turns)
        heatmap = self._improvement_heatmap(summary, previous_summaries)
        alternatives = self._senior_alternatives(turns)
        badges = self._badges(persona, overall, logic_depth, summary)
        pass_status = {
            "passed": overall >= 72 and logic_depth >= 68,
            "threshold_overall": 72.0,
            "threshold_logic": 68.0,
            "persona": persona.key,
        }

        scorecard = {
            "logic_depth": round(logic_depth, 2),
            "behavioral_control": round(behavioral, 2),
            "confidence_delivery": round(summary["confidence_avg"], 2),
            "overall": round(overall, 2),
        }

        return {
            "scorecard": scorecard,
            "transcript_breakdown": transcript,
            "improvement_heatmap": heatmap,
            "senior_answer_alternatives": alternatives,
            "badges": badges,
            "pass_status": pass_status,
        }

    def synthesize_media(
        self,
        session_id: int,
        transcript_breakdown: Sequence[Dict[str, Any]],
        voice_style: str,
        avatar_style: str,
        language: str,
        environment_theme: str,
    ) -> Dict[str, Any]:
        highlights = " ".join(item.get("coach_hint", "") for item in transcript_breakdown[:3]).strip() or "Keep answers concise and trade-off driven."

        if language.lower() == "hinglish":
            multilingual = {
                "primary": "hinglish",
                "sample_line": "Main issue ko 3 steps mein explain karunga: context, trade-off, aur final decision.",
                "fallback": "english",
            }
        else:
            multilingual = {
                "primary": "english",
                "sample_line": "I will structure the answer in context, trade-off, and decision.",
                "fallback": "hinglish",
            }

        low_latency_audio = {
            "voice_style": voice_style,
            "estimated_latency_ms": 180,
            "ssml": f"<speak><prosody rate='95%'>{highlights}</prosody></speak>",
            "stream_protocol": "websocket-chunked",
        }

        lip_sync_avatar = {
            "avatar_style": avatar_style,
            "lip_sync_model": "viseme-lite-v1",
            "animation_fps": 30,
            "render_hint": "Use low-latency keyframe interpolation for smooth mouth motion.",
        }

        environment_simulation = {
            "theme": environment_theme,
            "presets": ["zoom", "office", "startup-war-room", "minimal-studio"],
            "selected": environment_theme,
        }

        return {
            "session_id": session_id,
            "low_latency_audio": low_latency_audio,
            "lip_sync_avatar": lip_sync_avatar,
            "environment_simulation": environment_simulation,
            "multilingual_pack": multilingual,
        }

    def share_packet(self, session_id: int) -> Dict[str, Any]:
        token = secrets.token_urlsafe(16)
        expires_at = datetime.now(timezone.utc) + timedelta(days=14)
        return {
            "session_id": session_id,
            "share_token": token,
            "expires_at": expires_at,
            "review_url": f"/api/feature4/share/{token}",
        }

    def compare_heatmap(self, left: Dict[str, Any], right: Dict[str, Any], candidate_id: str, left_id: int, right_id: int) -> Dict[str, Any]:
        delta = {
            "overall": round(right["scorecard"]["overall"] - left["scorecard"]["overall"], 2),
            "logic_depth": round(right["scorecard"]["logic_depth"] - left["scorecard"]["logic_depth"], 2),
            "behavioral_control": round(right["scorecard"]["behavioral_control"] - left["scorecard"]["behavioral_control"], 2),
            "confidence_delivery": round(right["scorecard"]["confidence_delivery"] - left["scorecard"]["confidence_delivery"], 2),
        }

        narrative = [
            f"Overall delta is {delta['overall']:+.2f} points.",
            f"Logic depth shifted by {delta['logic_depth']:+.2f}; focus on explicit downside analysis.",
            f"Behavioral control shifted by {delta['behavioral_control']:+.2f}; keep reducing freeze and filler spikes.",
        ]

        return {
            "candidate_id": candidate_id,
            "left_session": left_id,
            "right_session": right_id,
            "delta": delta,
            "narrative": narrative,
        }

    def _logic_depth_score(self, turns: Sequence[Dict[str, Any]]) -> float:
        if not turns:
            return 0.0

        scores = []
        for t in turns:
            utter = t["utterance"].lower()
            trade_hits = sum(1 for w in TRADEOFF_WORDS if w in utter)
            hedge = len(HEDGE_RE.findall(utter))
            score = min(100.0, 35 + trade_hits * 16 - hedge * 7 + len(utter.split()) * 0.22)
            scores.append(max(0.0, score))

        return float(mean(scores))

    def _transcript_breakdown(self, turns: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows = []
        for idx, t in enumerate(turns, start=1):
            rt = t["realtime"]
            hint = self.whisper_hint(rt, t["deep_logic"])
            rows.append(
                {
                    "line": idx,
                    "question_type": t["question"]["type"],
                    "candidate_excerpt": t["utterance"][:220],
                    "filler_score": rt["filler_tracker"]["score"],
                    "freeze_score": rt["silence_detection"]["score"],
                    "tone": rt["tone_correlation"]["label"],
                    "coach_hint": hint,
                }
            )
        return rows

    def _improvement_heatmap(self, current_summary: Dict[str, Any], previous_summaries: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        if not previous_summaries:
            baseline = {"filler_avg": current_summary["filler_avg"], "confidence_avg": current_summary["confidence_avg"], "freeze_risk_avg": current_summary["freeze_risk_avg"], "gaze_avg": current_summary["gaze_avg"]}
        else:
            baseline = {
                "filler_avg": mean(s.get("filler_avg", 0) for s in previous_summaries),
                "confidence_avg": mean(s.get("confidence_avg", 0) for s in previous_summaries),
                "freeze_risk_avg": mean(s.get("freeze_risk_avg", 0) for s in previous_summaries),
                "gaze_avg": mean(s.get("gaze_avg", 0) for s in previous_summaries),
            }

        return {
            "baseline": {k: round(v, 2) for k, v in baseline.items()},
            "current": {k: round(v, 2) for k, v in current_summary.items() if k.endswith("_avg")},
            "delta": {
                "filler_control": round(current_summary["filler_avg"] - baseline["filler_avg"], 2),
                "confidence": round(current_summary["confidence_avg"] - baseline["confidence_avg"], 2),
                "freeze_control": round(current_summary["freeze_risk_avg"] - baseline["freeze_risk_avg"], 2),
                "gaze_stability": round(current_summary["gaze_avg"] - baseline["gaze_avg"], 2),
            },
        }

    def _senior_alternatives(self, turns: Sequence[Dict[str, Any]]) -> List[Dict[str, str]]:
        out = []
        for t in turns[:5]:
            question = t["question"]["question"]
            alt = (
                "Senior framing: start with architecture boundary, quantify trade-off, "
                "name failure mode, then close with measurable impact and rollback path."
            )
            out.append({"question": question[:180], "senior_version": alt})
        return out

    def _badges(self, persona: PersonaProfile, overall: float, logic_depth: float, summary: Dict[str, Any]) -> Dict[str, Any]:
        badges = []
        if overall >= 85:
            badges.append("Persona Master")
        if logic_depth >= 80:
            badges.append("Trade-off Commander")
        if summary["freeze_risk_avg"] >= 75:
            badges.append("Composure Under Fire")
        if summary["gaze_avg"] >= 80:
            badges.append("Executive Presence")

        return {
            "persona": persona.label,
            "earned": badges,
            "all_available": ["Persona Master", "Trade-off Commander", "Composure Under Fire", "Executive Presence"],
        }


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)
