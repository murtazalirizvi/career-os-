from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Set, Tuple

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9\-\+\.]{1,}")

STOP_WORDS: Set[str] = {
    "the",
    "and",
    "with",
    "for",
    "that",
    "this",
    "from",
    "into",
    "your",
    "our",
    "you",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "will",
    "would",
    "can",
    "could",
    "should",
    "to",
    "of",
    "in",
    "on",
    "at",
}

SYNONYMS: Dict[str, List[str]] = {
    "single page application": ["spa"],
    "javascript": ["js"],
    "typescript": ["ts"],
    "artificial intelligence": ["ai"],
    "continuous integration": ["ci"],
    "continuous deployment": ["cd"],
    "microservices": ["services architecture"],
}

BUZZWORDS = {
    "hardworking",
    "team player",
    "self motivated",
    "go getter",
    "passionate",
    "results driven",
}

ACTION_VERBS = [
    "engineered",
    "designed",
    "optimized",
    "automated",
    "implemented",
    "migrated",
    "improved",
    "reduced",
]


def tokenize(text: str) -> List[str]:
    tokens = [m.group(0).lower() for m in TOKEN_PATTERN.finditer(text)]
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def frequency_map(tokens: Iterable[str]) -> Counter:
    return Counter(tokens)


def keyword_cloud_differential(job_description: str, resume_text: str) -> Dict[str, float]:
    jd_tokens = tokenize(job_description)
    resume_tokens = tokenize(resume_text)

    jd_count = frequency_map(jd_tokens)
    resume_count = frequency_map(resume_tokens)

    top_keywords = [k for k, _ in jd_count.most_common(50)]
    differential: Dict[str, float] = {}
    for keyword in top_keywords:
        jd_freq = jd_count[keyword] / max(len(jd_tokens), 1)
        resume_freq = resume_count[keyword] / max(len(resume_tokens), 1)
        differential[keyword] = round(jd_freq - resume_freq, 5)
    return differential


def synonym_suggestions(job_description: str, resume_text: str) -> List[str]:
    lower_jd = job_description.lower()
    lower_resume = resume_text.lower()
    suggestions: List[str] = []

    for long_form, alternatives in SYNONYMS.items():
        if long_form in lower_jd and long_form in lower_resume:
            alt = alternatives[0]
            suggestions.append(f"Use both '{long_form}' and '{alt}' to improve search coverage.")
        elif long_form in lower_jd and all(alt not in lower_resume for alt in alternatives):
            suggestions.append(f"Add synonym '{alternatives[0]}' for '{long_form}' where authentic.")

    return suggestions


def skill_frequency_health(job_description: str, resume_text: str) -> Tuple[float, Dict[str, str]]:
    differential = keyword_cloud_differential(job_description, resume_text)
    notes: Dict[str, str] = {}

    under = 0
    over = 0
    for key, diff in differential.items():
        if diff > 0.015:
            notes[key] = "under-represented"
            under += 1
        elif diff < -0.02:
            notes[key] = "potentially overstuffed"
            over += 1

    # Balanced profile gets highest score.
    score = max(0.0, 100.0 - (under * 2.4 + over * 3.2))
    return round(score, 2), notes


def buzzword_replacements(resume_text: str) -> List[str]:
    suggestions = []
    lower = resume_text.lower()
    for phrase in BUZZWORDS:
        if phrase in lower:
            action = ACTION_VERBS[len(suggestions) % len(ACTION_VERBS)]
            suggestions.append(f"Replace '{phrase}' with an action-based claim like '{action} X that improved Y by Z%'.")
    return suggestions


def missing_skill_prioritization(job_description: str, resume_text: str) -> List[str]:
    jd_tokens = tokenize(job_description)
    resume_tokens = set(tokenize(resume_text))
    jd_freq = frequency_map(jd_tokens)

    candidates = []
    for keyword, count in jd_freq.most_common(30):
        if keyword not in resume_tokens and len(keyword) > 2:
            priority = math.log(count + 1) * (1.4 if keyword.isalpha() else 1.0)
            candidates.append((priority, keyword))

    candidates.sort(reverse=True)
    return [kw for _, kw in candidates[:10]]


def semantic_alignment_score(job_description: str, resume_text: str) -> float:
    jd = set(tokenize(job_description))
    resume = set(tokenize(resume_text))
    if not jd:
        return 0.0
    overlap = len(jd.intersection(resume))
    score = 100.0 * overlap / len(jd)
    return round(score, 2)
