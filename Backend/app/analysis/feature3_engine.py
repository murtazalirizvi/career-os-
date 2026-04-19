from __future__ import annotations

import math
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from statistics import mean
from typing import Any, Dict, List, Sequence, Set, Tuple

import httpx

from . import gemini_client

SKILL_LEXICON = {
    "react",
    "typescript",
    "javascript",
    "python",
    "fastapi",
    "django",
    "sql",
    "postgres",
    "mysql",
    "redis",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "terraform",
    "kafka",
    "grpc",
    "graphql",
    "node",
    "nextjs",
    "pandas",
    "numpy",
    "spark",
    "airflow",
    "dbt",
    "llm",
    "prompting",
    "agents",
    "rag",
    "ci",
    "cd",
    "testing",
    "playwright",
    "pytest",
    "webassembly",
    "rust",
    "go",
}

CLUSTER_MAP = {
    "frontend": {"react", "typescript", "javascript", "nextjs", "graphql", "playwright"},
    "backend": {"python", "fastapi", "django", "node", "grpc", "sql", "redis", "kafka", "testing", "pytest"},
    "data": {"pandas", "numpy", "spark", "airflow", "dbt", "sql", "python"},
    "cloud": {"docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ci", "cd"},
    "agentic_ai": {"llm", "prompting", "agents", "rag", "python"},
    "systems": {"rust", "go", "webassembly", "kafka", "grpc"},
}

DECLINING_TECH = {
    "jquery": 0.72,
    "php-legacy": 0.61,
    "manual-qa-only": 0.54,
    "onprem-only": 0.47,
}

EMERGING_2027 = {
    "agent-orchestration": 0.88,
    "ai-safety-engineering": 0.81,
    "edge-inference": 0.76,
    "platform-internal-devex": 0.72,
    "event-native-data-products": 0.69,
}

CURATED_LINKS = {
    "react": [
        {"title": "React official docs", "url": "https://react.dev/learn"},
        {"title": "Advanced React patterns", "url": "https://www.youtube.com/watch?v=3XaXKiXtNjw"},
    ],
    "typescript": [
        {"title": "TypeScript handbook", "url": "https://www.typescriptlang.org/docs/"},
        {"title": "Type narrowing and generics", "url": "https://www.youtube.com/watch?v=ahCwqrYpIuM"},
    ],
    "sql": [
        {"title": "Use The Index, Luke", "url": "https://use-the-index-luke.com/"},
        {"title": "SQL tuning fundamentals", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
    ],
    "kubernetes": [
        {"title": "Kubernetes basics", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
        {"title": "Production k8s patterns", "url": "https://www.youtube.com/watch?v=2vMEQ5zs1ko"},
    ],
    "llm": [
        {"title": "LLM engineering handbook", "url": "https://www.youtube.com/watch?v=dOxUroR57xs"},
        {"title": "RAG patterns", "url": "https://www.pinecone.io/learn/retrieval-augmented-generation/"},
    ],
}


def _extract_skills_from_jd(job_description: str) -> Set[str]:
    """Extract technology terms from the job description to augment static lexicon."""
    tech_pattern = re.compile(
        r"\b([A-Z][a-zA-Z0-9+#]*(?:\.js|\.NET|JS)?|"
        r"[a-z]+(?:js|ts|py|sql|db|api|sdk|cli|ui|css|ml|ai|llm))\b"
    )
    candidates = set(tech_pattern.findall(job_description or ""))
    stopwords = {
        "The", "And", "For", "Are", "With", "This", "That", "From", "Have", "Will",
        "Your", "More", "Also", "Can", "Not", "But", "You", "All", "Any", "Our"
    }
    return {w.lower() for w in candidates if len(w) >= 2 and len(w) <= 20 and w not in stopwords}


class MarketIntelligenceEngine:
    def __init__(self, timeout_seconds: float = 6.0) -> None:
        self.timeout_seconds = timeout_seconds
        self._working_lexicon: Set[str] = set(SKILL_LEXICON)

    def build_market_snapshot(
        self,
        target_role: str,
        region: str,
        remote_only: bool,
        search_terms: Sequence[str],
    ) -> Dict[str, Any]:
        dynamic_skills = _extract_skills_from_jd(" ".join(search_terms or []))
        self._working_lexicon = SKILL_LEXICON | dynamic_skills
        jobs, source_meta = self._aggregate_jobs(target_role, region, remote_only, search_terms)
        clusters = self._cluster_tech_stacks(jobs)
        demand_supply = self._demand_supply_ratio(jobs)
        salary_map = self._salary_skill_map(jobs)
        remote_market = self._remote_filter_analytics(jobs)

        return {
            "jobs": jobs[:120],
            "tech_stack_clusters": clusters,
            "demand_supply_ratio": demand_supply,
            "salary_to_skill_map": salary_map,
            "remote_opportunity_filter": remote_market,
            "source_meta": source_meta,
        }

    def _aggregate_jobs(
        self,
        target_role: str,
        region: str,
        remote_only: bool,
        search_terms: Sequence[str],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        terms = [target_role, *search_terms]
        adzuna_jobs = self._fetch_adzuna(terms, region)
        reed_jobs = self._fetch_reed(terms, region)
        linkedin_like = self._fetch_public_feed("linkedin", terms, region)
        indeed_like = self._fetch_public_feed("indeed", terms, region)
        octoverse_like = self._fetch_octoverse_proxy(terms, region)

        merged = adzuna_jobs + reed_jobs + linkedin_like + indeed_like + octoverse_like
        if remote_only:
            merged = [j for j in merged if j.get("remote", False)]

        if not merged:
            merged = self._mock_jobs(target_role, region, remote_only)

        deduped = {}
        for job in merged:
            key = f"{job.get('title','').lower()}::{job.get('company','').lower()}::{job.get('location','').lower()}"
            deduped[key] = job

        jobs = list(deduped.values())
        jobs.sort(key=lambda x: x.get("salary_mid", 0), reverse=True)

        source_meta = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "target_role": target_role,
            "region": region,
            "remote_only": remote_only,
            "data_sources_used": {
                "adzuna": len(adzuna_jobs),
                "reed": len(reed_jobs),
                "linkedin_public_proxy": len(linkedin_like),
                "indeed_public_proxy": len(indeed_like),
                "github_octoverse_proxy": len(octoverse_like),
                "fallback_mock": 0 if merged else len(jobs),
            },
            "total_jobs": len(jobs),
        }
        return jobs, source_meta

    def _fetch_octoverse_proxy(self, terms: Sequence[str], region: str) -> List[Dict[str, Any]]:
        query = " ".join(t for t in terms if t).strip()
        if not query:
            return []

        headers = {"Accept": "application/vnd.github+json", "User-Agent": "career-os-feature3"}
        params = {
            "q": f"{query} in:name,description stars:>20",
            "sort": "stars",
            "order": "desc",
            "per_page": 10,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                res = client.get("https://api.github.com/search/repositories", headers=headers, params=params)
                if res.status_code >= 400:
                    return []
                payload = res.json()
        except Exception:
            return []

        rows: List[Dict[str, Any]] = []
        for item in payload.get("items", [])[:8]:
            topics = [t.lower() for t in item.get("topics", [])]
            language = (item.get("language") or "").lower()
            stars = float(item.get("stargazers_count") or 0)
            forks = float(item.get("forks_count") or 0)
            lexicon = self._working_lexicon

            synthetic_salary = min(120000.0, 25000.0 + stars * 55 + forks * 35)
            skills = sorted(set([x for x in topics if x in lexicon] + ([language] if language in lexicon else [])))

            rows.append(
                {
                    "source": "github_octoverse_proxy",
                    "title": f"{item.get('name', 'repo')} signals for {query}",
                    "company": item.get("owner", {}).get("login", "github"),
                    "location": region,
                    "remote": True,
                    "salary_min": max(15000.0, synthetic_salary * 0.82),
                    "salary_max": synthetic_salary,
                    "salary_mid": (max(15000.0, synthetic_salary * 0.82) + synthetic_salary) / 2,
                    "skills": skills or self._extract_skills(f"{item.get('name', '')} {item.get('description', '')}"),
                    "url": item.get("html_url", ""),
                }
            )
        return rows

    def _fetch_adzuna(self, terms: Sequence[str], region: str) -> List[Dict[str, Any]]:
        app_id = os.getenv("ADZUNA_APP_ID", "")
        app_key = os.getenv("ADZUNA_APP_KEY", "")
        if not app_id or not app_key:
            return []

        query = " ".join(t for t in terms if t).strip()
        if not query:
            return []

        url = f"https://api.adzuna.com/v1/api/jobs/{region.lower()}/search/1"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 30,
            "what": query,
            "content-type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                res = client.get(url, params=params)
                if res.status_code >= 400:
                    return []
                payload = res.json()
        except Exception:
            return []

        rows = []
        for item in payload.get("results", []):
            desc = item.get("description", "")
            title = item.get("title", "")
            company = (item.get("company") or {}).get("display_name", "Unknown")
            location = ((item.get("location") or {}).get("display_name") or "Unknown").strip()
            salary_min = float(item.get("salary_min") or 0)
            salary_max = float(item.get("salary_max") or 0)
            salary_mid = (salary_min + salary_max) / 2 if salary_min and salary_max else max(salary_min, salary_max)
            rows.append(
                {
                    "source": "adzuna",
                    "title": title,
                    "company": company,
                    "location": location,
                    "remote": "remote" in desc.lower() or "remote" in title.lower(),
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_mid": salary_mid,
                    "skills": self._extract_skills(f"{title} {desc}"),
                    "url": item.get("redirect_url", ""),
                }
            )
        return rows

    def _fetch_reed(self, terms: Sequence[str], region: str) -> List[Dict[str, Any]]:
        api_key = os.getenv("REED_API_KEY", "")
        if not api_key:
            return []

        query = " ".join(t for t in terms if t).strip()
        if not query:
            return []

        url = "https://www.reed.co.uk/api/1.0/search"
        headers = {"Authorization": f"Basic {api_key}"}
        params = {"keywords": query, "locationName": region, "resultsToTake": 30}

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                res = client.get(url, params=params, headers=headers)
                if res.status_code >= 400:
                    return []
                payload = res.json()
        except Exception:
            return []

        rows = []
        for item in payload.get("results", []):
            title = item.get("jobTitle", "")
            desc = item.get("jobDescription", "")
            salary_min = float(item.get("minimumSalary") or 0)
            salary_max = float(item.get("maximumSalary") or 0)
            salary_mid = (salary_min + salary_max) / 2 if salary_min and salary_max else max(salary_min, salary_max)
            rows.append(
                {
                    "source": "reed",
                    "title": title,
                    "company": item.get("employerName", "Unknown"),
                    "location": item.get("locationName", "Unknown"),
                    "remote": "remote" in (item.get("locationName", "") + " " + desc).lower(),
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_mid": salary_mid,
                    "skills": self._extract_skills(f"{title} {desc}"),
                    "url": item.get("jobUrl", ""),
                }
            )
        return rows

    def _fetch_public_feed(self, source: str, terms: Sequence[str], region: str) -> List[Dict[str, Any]]:
        query = " ".join(terms).lower()
        if not query:
            return []

        seeds = [
            ("Senior Fullstack Engineer", ["react", "typescript", "python", "sql", "docker"], 45000, 70000, True),
            ("Backend Engineer", ["python", "fastapi", "postgres", "redis", "kubernetes"], 42000, 68000, False),
            ("Data Engineer", ["python", "sql", "spark", "airflow", "dbt"], 48000, 76000, True),
            ("AI Platform Engineer", ["python", "llm", "agents", "kubernetes", "aws"], 55000, 92000, True),
        ]

        rows = []
        for idx, (title, skills, smin, smax, remote) in enumerate(seeds):
            if any(term.lower() in title.lower() for term in terms if term):
                rows.append(
                    {
                        "source": source,
                        "title": title,
                        "company": f"{source.title()}-Org-{idx + 1}",
                        "location": region,
                        "remote": remote,
                        "salary_min": smin,
                        "salary_max": smax,
                        "salary_mid": (smin + smax) / 2,
                        "skills": skills,
                        "url": "",
                    }
                )
        return rows

    def _mock_jobs(self, target_role: str, region: str, remote_only: bool) -> List[Dict[str, Any]]:
        base = [
            {
                "source": "mock",
                "title": f"{target_role} I",
                "company": "Nimbus Labs",
                "location": region,
                "remote": True,
                "salary_min": 22000,
                "salary_max": 34000,
                "salary_mid": 28000,
                "skills": ["javascript", "react", "typescript", "testing"],
                "url": "",
            },
            {
                "source": "mock",
                "title": f"{target_role} II",
                "company": "Stratus Systems",
                "location": region,
                "remote": False,
                "salary_min": 28000,
                "salary_max": 46000,
                "salary_mid": 37000,
                "skills": ["python", "fastapi", "sql", "docker", "ci"],
                "url": "",
            },
            {
                "source": "mock",
                "title": f"Senior {target_role}",
                "company": "Atlas AI",
                "location": region,
                "remote": True,
                "salary_min": 52000,
                "salary_max": 90000,
                "salary_mid": 71000,
                "skills": ["python", "kubernetes", "llm", "agents", "terraform"],
                "url": "",
            },
        ]
        if remote_only:
            return [x for x in base if x["remote"]]
        return base

    def _extract_skills(self, text: str) -> List[str]:
        low = text.lower()
        return sorted({skill for skill in self._working_lexicon if skill in low})

    def _cluster_tech_stacks(self, jobs: Sequence[Dict[str, Any]]) -> Dict[str, List[str]]:
        present = set()
        for job in jobs:
            present.update([s.lower() for s in job.get("skills", [])])

        clusters: Dict[str, List[str]] = {}
        for name, members in CLUSTER_MAP.items():
            hit = sorted(present.intersection(members))
            if hit:
                clusters[name] = hit

        leftovers = sorted(present.difference(set().union(*CLUSTER_MAP.values())))
        if leftovers:
            clusters["other"] = leftovers
        return clusters

    def _demand_supply_ratio(self, jobs: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        demand = Counter()
        for job in jobs:
            demand.update(job.get("skills", []))

        ratios: Dict[str, Dict[str, float]] = {}
        total = max(1, len(jobs))
        for skill, count in demand.most_common(20):
            demand_pct = count / total
            supply_proxy = 0.22 + (0.9 / (1 + math.exp(-(2.5 - demand_pct * 5))))
            ratio = demand_pct / max(supply_proxy, 0.08)
            ratios[skill] = {
                "demand_pct": round(demand_pct, 4),
                "supply_proxy": round(supply_proxy, 4),
                "ratio": round(ratio, 4),
                "market_label": "hot" if ratio > 0.7 else "balanced" if ratio > 0.45 else "crowded",
            }
        return ratios

    def _salary_skill_map(self, jobs: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        salary_points = defaultdict(list)
        for job in jobs:
            sal = float(job.get("salary_mid") or 0)
            if sal <= 0:
                continue
            for skill in job.get("skills", []):
                salary_points[skill].append(sal)

        salary_map = {}
        for skill, values in salary_points.items():
            salary_map[skill] = {
                "avg_salary": round(mean(values), 2),
                "max_salary": round(max(values), 2),
                "min_salary": round(min(values), 2),
                "sample_size": float(len(values)),
            }
        return dict(sorted(salary_map.items(), key=lambda x: x[1]["avg_salary"], reverse=True)[:20])

    def _remote_filter_analytics(self, jobs: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
        if not jobs:
            return {
                "remote_ratio": 0.0,
                "onsite_ratio": 0.0,
                "global_competition_score": 0.0,
                "regional_competition_score": 0.0,
            }

        remote_jobs = [j for j in jobs if j.get("remote", False)]
        remote_ratio = len(remote_jobs) / len(jobs)
        onsite_ratio = 1 - remote_ratio

        global_comp = min(100.0, 45 + remote_ratio * 60)
        regional_comp = min(100.0, 35 + onsite_ratio * 55)

        return {
            "remote_ratio": round(remote_ratio, 4),
            "onsite_ratio": round(onsite_ratio, 4),
            "global_competition_score": round(global_comp, 2),
            "regional_competition_score": round(regional_comp, 2),
            "recommended_focus": "remote+local blend" if 0.35 < remote_ratio < 0.75 else "remote-heavy" if remote_ratio >= 0.75 else "regional-first",
        }


class SkillGapEngine:
    def build_gap_analysis(
        self,
        current_skills: Sequence[str],
        years_experience: float,
        market_snapshot: Dict[str, Any],
        github_username: str,
        historical_rows: Sequence[Any],
    ) -> Dict[str, Any]:
        current = sorted({s.strip().lower() for s in current_skills if s.strip()})
        demand_ratio = market_snapshot.get("demand_supply_ratio", {})
        salary_map = market_snapshot.get("salary_to_skill_map", {})

        target_skills = [k for k, _ in sorted(demand_ratio.items(), key=lambda x: x[1].get("ratio", 0), reverse=True)[:16]]
        missing = [s for s in target_skills if s not in current]

        match_score = self._match_score(current, target_skills, years_experience)
        top10_score = self._top10_gap_score(match_score)

        radar = self._radar_chart(current, target_skills)
        roadmap = self._roadmap_to_90(current, target_skills, years_experience)
        niche = self._niche_recommendations(demand_ratio, salary_map, current)
        github_validation = self._validate_github_projects(github_username, target_skills)
        history = self._historical_gap_tracking(historical_rows, match_score)

        # Gemini: AI-powered personalized learning path
        ai_learning_path = self._gemini_learning_path(current, missing[:6], years_experience)

        return {
            "current_skills": current,
            "target_skills": target_skills,
            "missing_skills": missing,
            "match_score": round(match_score, 2),
            "gap_to_top10_score": round(top10_score, 2),
            "radar_chart": radar,
            "roadmap_to_90": roadmap,
            "niche_recommendations": niche,
            "github_project_validation": github_validation,
            "historical_gap_tracking": history,
            "ai_learning_path": ai_learning_path,
        }

    def _gemini_learning_path(
        self,
        current_skills: Sequence[str],
        missing_skills: Sequence[str],
        years_experience: float,
    ) -> Dict[str, Any]:
        """Generate a personalized AI learning path using Gemini."""
        if not gemini_client.is_available() or not missing_skills:
            return {}

        prompt = (
            f"You are a senior engineering career coach. A developer has {years_experience:.1f} years experience.\n"
            f"Current skills: {', '.join(list(current_skills)[:10])}\n"
            f"Top missing skills for market demand: {', '.join(missing_skills)}\n\n"
            "Create a focused 30-day learning plan. For each of the top 3 missing skills provide:\n"
            "- One free resource (title + URL)\n"
            "- One mini-project idea (1 sentence)\n"
            "- One interview talking point (1 sentence)\n\n"
            "Format as plain text with skill names as headers. Be specific and actionable."
        )

        raw = gemini_client.generate(prompt, temperature=0.3, max_tokens=600)
        if not raw:
            return {}

        return {
            "generated": True,
            "plan": raw,
            "skills_covered": list(missing_skills[:3]),
        }

    def _match_score(self, current: Sequence[str], target: Sequence[str], years_experience: float) -> float:
        if not target:
            return 35.0
        overlap = len(set(current).intersection(target)) / len(target)
        exp_boost = min(12.0, years_experience * 2.8)
        return max(0.0, min(100.0, 20 + overlap * 68 + exp_boost))

    def _top10_gap_score(self, match_score: float) -> float:
        top10_cut = 88.0
        return max(0.0, top10_cut - match_score)

    def _radar_chart(self, current: Sequence[str], target: Sequence[str]) -> Dict[str, Any]:
        categories = {
            "frontend": {"react", "typescript", "javascript", "nextjs"},
            "backend": {"python", "fastapi", "sql", "redis", "kafka", "testing"},
            "data": {"pandas", "numpy", "spark", "airflow", "dbt"},
            "cloud": {"docker", "kubernetes", "aws", "gcp", "azure", "terraform"},
            "ai": {"llm", "agents", "rag", "prompting"},
        }

        user = set(current)
        market = set(target)
        axes = []
        for name, members in categories.items():
            market_need = max(1, len(market.intersection(members)))
            user_have = len(user.intersection(members))
            score = min(100.0, (user_have / market_need) * 100)
            axes.append({"axis": name, "user": round(score, 2), "market_target": 100.0})

        return {
            "type": "radar",
            "axes": axes,
            "labels": [x["axis"] for x in axes],
        }

    def _roadmap_to_90(self, current: Sequence[str], target: Sequence[str], years_experience: float) -> Dict[str, Any]:
        missing = [s for s in target if s not in current]
        high_priority = missing[:6]
        medium_priority = missing[6:12]

        phases = [
            {
                "phase": "0-2 weeks",
                "goal": "Close critical demand gaps",
                "actions": [f"Build one mini-project showcasing {skill}." for skill in high_priority[:3]]
                or ["Polish and benchmark one existing project for market relevance."],
            },
            {
                "phase": "3-5 weeks",
                "goal": "Reach interview-safe depth",
                "actions": [f"Write trade-off notes and tests for {skill}." for skill in high_priority[3:6]]
                or ["Run three timed mock interview drills with architecture trade-offs."],
            },
            {
                "phase": "6-8 weeks",
                "goal": "Push to top decile signal",
                "actions": [f"Add production-grade evidence for {skill}." for skill in medium_priority[:3]]
                or ["Add observability, CI gates, and measurable impact metrics."],
            },
        ]

        baseline = self._match_score(current, target, years_experience)
        projected = min(96.0, baseline + 18.0 + min(10, len(high_priority) * 1.3))
        return {
            "current_match": round(baseline, 2),
            "projected_match_after_plan": round(projected, 2),
            "target_match": 90.0,
            "phases": phases,
        }

    def _niche_recommendations(
        self,
        demand_ratio: Dict[str, Dict[str, float]],
        salary_map: Dict[str, Dict[str, float]],
        current_skills: Sequence[str],
    ) -> List[Dict[str, Any]]:
        rows = []
        current = set(current_skills)
        for skill, ratio_data in demand_ratio.items():
            if skill in current:
                continue
            salary = salary_map.get(skill, {}).get("avg_salary", 0.0)
            rarity = 1.0 / max(ratio_data.get("supply_proxy", 0.15), 0.06)
            demand = ratio_data.get("demand_pct", 0.0)
            score = (demand * 70) + (rarity * 18) + min(25, salary / 4000)
            rows.append(
                {
                    "skill": skill,
                    "opportunity_score": round(score, 2),
                    "why": f"Demand {demand:.2f}, low supply proxy {ratio_data.get('supply_proxy', 0):.2f}, salary leverage {salary:.0f}.",
                }
            )
        rows.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return rows[:8]

    def _validate_github_projects(self, github_username: str, target_skills: Sequence[str]) -> Dict[str, Any]:
        if not github_username:
            return {
                "github_connected": False,
                "coverage_score": 0.0,
                "matched_skills": [],
                "warnings": ["GitHub username not provided; project validation skipped."],
            }

        url = f"https://api.github.com/users/{github_username}/repos"
        repos = []
        try:
            with httpx.Client(timeout=5.0, headers={"Accept": "application/vnd.github+json"}) as client:
                res = client.get(url)
                if res.status_code < 400:
                    repos = res.json()[:40]
        except Exception:
            repos = []

        lang_map = {
            "python": "python",
            "typescript": "typescript",
            "javascript": "javascript",
            "go": "go",
            "rust": "rust",
        }
        seen = set()
        for repo in repos:
            lang = (repo.get("language") or "").strip().lower()
            if lang in lang_map:
                seen.add(lang_map[lang])

        target = set(target_skills)
        matched = sorted(seen.intersection(target))
        coverage = (len(matched) / max(1, min(10, len(target)))) * 100

        warnings = []
        if not repos:
            warnings.append("Could not fetch public repositories or none found.")
        if coverage < 35:
            warnings.append("Add one portfolio project for each top demand skill in your roadmap.")

        return {
            "github_connected": bool(repos),
            "public_repo_count": len(repos),
            "matched_skills": matched,
            "coverage_score": round(coverage, 2),
            "warnings": warnings,
        }

    def _historical_gap_tracking(self, historical_rows: Sequence[Any], new_match_score: float) -> Dict[str, Any]:
        monthly = defaultdict(list)
        for row in historical_rows:
            created = row.created_at
            month_key = f"{created.year}-{created.month:02d}"
            monthly[month_key].append(float(row.match_score))

        now = datetime.now(timezone.utc)
        month_key = f"{now.year}-{now.month:02d}"
        monthly[month_key].append(new_match_score)

        snapshots = []
        for month, values in sorted(monthly.items()):
            snapshots.append({"month": month, "avg_match_score": round(mean(values), 2), "samples": len(values)})

        if len(snapshots) < 2:
            trend = {"monthly_delta": 0.0, "confidence": 0.2}
        else:
            trend = {
                "monthly_delta": round(snapshots[-1]["avg_match_score"] - snapshots[0]["avg_match_score"], 2),
                "confidence": round(min(0.95, 0.3 + len(snapshots) * 0.12), 2),
            }

        return {"monthly_snapshots": snapshots, "trend": trend}


class SprintEngine:
    def build_sprint(self, primary_skill: str, target_role: str) -> Dict[str, Any]:
        skill = primary_skill.lower().strip()
        links = CURATED_LINKS.get(skill, [{"title": "Skill docs", "url": "https://developer.mozilla.org/"}])

        day_plan = []
        for day in range(1, 8):
            if day in (1, 2):
                objective = "Foundations and syntax fluency"
            elif day == 3:
                objective = "Checkpoint quiz and corrections"
            elif day in (4, 5):
                objective = "Build and refine MVP core"
            else:
                objective = "Production polish and interview narrative"

            day_plan.append(
                {
                    "day": day,
                    "objective": objective,
                    "resource": links[(day - 1) % len(links)],
                    "deliverable": f"Artifact for {skill} day {day}: commit, notes, and benchmark evidence.",
                }
            )

        mvp_prompt = {
            "title": f"7-day MVP: {skill.title()} proof project for {target_role}",
            "brief": (
                f"Build a compact but production-minded project where {skill} is central. "
                "Include README architecture, test plan, and one measurable metric improvement."
            ),
            "acceptance_criteria": [
                "Runs locally with setup steps under 10 minutes.",
                "Has at least one automated test path.",
                "Documents one trade-off and one scaling path.",
            ],
        }

        quiz = {
            "day": 3,
            "questions": [
                f"Explain one core trade-off when using {skill} in production.",
                f"Describe a failure mode in {skill} and how to mitigate it.",
                "Provide a short STAR answer describing your implementation impact.",
            ],
            "pass_mark": 70.0,
        }

        resume_injector = {
            "template": "Engineered <feature> using <skill> to improve <metric> by <delta>% while handling <constraint>.",
            "checks": ["action verb", "measurable metric", "trade-off mention", "business/user impact"],
        }

        peer_tags = [
            skill,
            target_role.lower().replace(" ", "-"),
            "sprint-7-day",
        ]

        return {
            "curated_day_plan": day_plan,
            "mvp_prompt": mvp_prompt,
            "quick_quiz": quiz,
            "resume_injector": resume_injector,
            "peer_group_tags": peer_tags,
        }

    def evaluate_quiz(self, quiz: Dict[str, Any], answers: Sequence[str]) -> Dict[str, Any]:
        target_keywords = {"trade-off", "latency", "reliability", "impact", "constraint", "result", "metric", "test"}

        feedback = []
        score = 0.0
        for idx, answer in enumerate(answers[: len(quiz.get("questions", []))]):
            low = answer.lower()
            hit = sum(1 for k in target_keywords if k in low)
            ans_score = min(100.0, hit * 18.0 + min(28.0, len(answer.split()) * 0.7))
            score += ans_score
            if hit < 3:
                feedback.append(f"Answer {idx + 1}: add explicit trade-offs, metrics, and constraints.")

        question_count = max(1, len(quiz.get("questions", [])))
        final = score / question_count
        passed = final >= float(quiz.get("pass_mark", 70.0))
        if passed:
            feedback.append("Strong checkpoint. Move to MVP hardening and benchmark evidence.")

        return {
            "score": round(final, 2),
            "passed": passed,
            "feedback": feedback[:6],
        }

    def resume_inject(self, skill: str, project_name: str, baseline_context: str, impact_metric_hint: str) -> Dict[str, Any]:
        metric = impact_metric_hint or "latency, reliability, and delivery speed"
        context = baseline_context or "a production-like workflow under tight deadlines"

        bullets = [
            f"Engineered {project_name} using {skill} to improve {metric} while balancing maintainability and release risk.",
            f"Designed and implemented core {skill} workflows, reducing ambiguity through tests and clear API contracts.",
            f"Owned trade-off decisions in {context}, translating technical outcomes into measurable user and business impact.",
        ]

        linkedin = (
            f"Built {project_name} with a focused {skill} sprint: shipped tested features, documented architecture trade-offs, "
            f"and improved {metric}."
        )

        return {"star_bullets": bullets, "linkedin_snippet": linkedin}


class FutureEngine:
    def build_future_insights(self, current_skills: Sequence[str], market_snapshot: Dict[str, Any] | None) -> Dict[str, Any]:
        low = {s.lower() for s in current_skills}

        obsolescence = []
        for tech, risk in DECLINING_TECH.items():
            user_exposed = tech in low
            adjusted = min(0.99, risk + (0.08 if user_exposed else -0.05))
            obsolescence.append(
                {
                    "skill_or_pattern": tech,
                    "risk_score": round(adjusted * 100, 2),
                    "user_exposed": user_exposed,
                    "action": "decrease reliance" if adjusted > 0.6 else "monitor",
                }
            )

        forecast = {
            "year": 2027,
            "top_emerging_domains": [
                {"domain": k, "confidence": round(v * 100, 2)} for k, v in EMERGING_2027.items()
            ],
            "recommendation": "Prioritize agentic workflows, platform engineering, and data product reliability.",
        }

        agentic_score = self._agentic_score(low)
        pivot = self._pivot_advice(low)
        freeze = self._hiring_freeze_alert(market_snapshot)

        return {
            "obsolescence_tracker": obsolescence,
            "forecast_2027": forecast,
            "agentic_ai_score": agentic_score,
            "industry_pivot_advice": pivot,
            "hiring_freeze_alert": freeze,
        }

    def _agentic_score(self, skills: set[str]) -> Dict[str, Any]:
        required = {"python", "llm", "agents", "rag", "testing", "ci"}
        hit = skills.intersection(required)
        score = (len(hit) / len(required)) * 100

        level = "advanced" if score >= 75 else "intermediate" if score >= 45 else "early"
        return {
            "score": round(score, 2),
            "level": level,
            "missing_capabilities": sorted(required.difference(skills)),
            "next_actions": [
                "Build one retrieval + agent orchestration demo with eval traces.",
                "Add CI checks for prompt regressions and latency budgets.",
            ],
        }

    def _pivot_advice(self, skills: set[str]) -> Dict[str, Any]:
        has_data = bool(skills.intersection({"spark", "airflow", "dbt", "sql"}))
        has_cloud = bool(skills.intersection({"docker", "kubernetes", "aws", "gcp", "azure", "terraform"}))
        has_ai = bool(skills.intersection({"llm", "agents", "rag"}))

        if has_ai and has_cloud:
            target = "AI Platform / MLOps"
        elif has_data and has_cloud:
            target = "Data Platform Engineering"
        elif has_data:
            target = "Analytics Engineering"
        else:
            target = "Fullstack Product Engineering"

        return {
            "recommended_pivot": target,
            "rationale": [
                "Pivot chosen from existing transferable skills to minimize retooling time.",
                "Prioritizes sectors with stronger medium-term demand resilience.",
            ],
            "starter_move": "Ship one portfolio case study aligned to target pivot in the next 14 days.",
        }

    def _hiring_freeze_alert(self, market_snapshot: Dict[str, Any] | None) -> Dict[str, Any]:
        jobs = (market_snapshot or {}).get("jobs", [])
        if not jobs:
            sentiment = 0.52
        else:
            remote_ratio = (market_snapshot or {}).get("remote_opportunity_filter", {}).get("remote_ratio", 0.5)
            salary_mean = mean([j.get("salary_mid", 0) for j in jobs]) if jobs else 0
            sentiment = min(0.95, max(0.1, 0.35 + remote_ratio * 0.28 + min(0.22, salary_mean / 300000)))

        freeze_risk = 1 - sentiment
        return {
            "market_sentiment_score": round(sentiment * 100, 2),
            "freeze_risk_score": round(freeze_risk * 100, 2),
            "alert_level": "high" if freeze_risk > 0.6 else "medium" if freeze_risk > 0.35 else "low",
            "playbook": [
                "Increase referral-driven applications during high-risk windows.",
                "Shift to firms with visible hiring velocity and recent engineering openings.",
            ],
        }


class RoiEngine:
    def build_roi(
        self,
        current_salary_usd: float,
        target_path: str,
        gap_snapshot: Dict[str, Any] | None,
        market_snapshot: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        match_score = float((gap_snapshot or {}).get("match_score", 40.0))
        gap = float((gap_snapshot or {}).get("gap_to_top10_score", 48.0))

        impact = self._match_rate_impact(match_score)
        callback = self._callback_probability(match_score, gap)
        ltv = self._lifetime_value(current_salary_usd, target_path, market_snapshot)
        path_compare = self._path_comparison(current_salary_usd)
        stories = self._success_stories(match_score)

        return {
            "skill_impact": impact,
            "callback_probability": callback,
            "lifetime_value": ltv,
            "path_comparison": path_compare,
            "success_stories": stories,
        }

    def _match_rate_impact(self, match_score: float) -> Dict[str, Any]:
        baseline = 0.06
        projected = min(0.42, baseline + match_score / 240)
        return {
            "baseline_match_rate": round(baseline * 100, 2),
            "projected_match_rate": round(projected * 100, 2),
            "delta_points": round((projected - baseline) * 100, 2),
        }

    def _callback_probability(self, match_score: float, gap: float) -> Dict[str, Any]:
        linear = max(0.02, min(0.82, 0.03 + match_score * 0.0062 - gap * 0.0025))
        return {
            "probability": round(linear * 100, 2),
            "confidence": round(min(0.9, 0.45 + match_score / 200), 2),
            "drivers": [
                "Higher skill-market match increases recruiter shortlist probability.",
                "Closing top-decile gap compounds callback odds across roles.",
            ],
        }

    def _lifetime_value(self, current_salary_usd: float, target_path: str, market_snapshot: Dict[str, Any] | None) -> Dict[str, Any]:
        path_multiplier = {
            "fullstack": 1.48,
            "data": 1.56,
            "ml": 1.72,
            "platform": 1.62,
        }.get(target_path.lower(), 1.45)

        market_salary = 0.0
        if market_snapshot:
            salaries = [j.get("salary_mid", 0) for j in market_snapshot.get("jobs", []) if j.get("salary_mid", 0) > 0]
            if salaries:
                market_salary = mean(salaries)

        target_salary = max(current_salary_usd * path_multiplier, market_salary)
        annual_delta = max(0.0, target_salary - current_salary_usd)
        five_year_value = annual_delta * 5.4

        return {
            "current_salary_usd": round(current_salary_usd, 2),
            "projected_salary_usd": round(target_salary, 2),
            "annual_delta_usd": round(annual_delta, 2),
            "five_year_value_delta_usd": round(five_year_value, 2),
        }

    def _path_comparison(self, current_salary_usd: float) -> Dict[str, Any]:
        paths = {
            "fullstack": current_salary_usd * 1.48,
            "data-engineering": current_salary_usd * 1.56,
            "platform-engineering": current_salary_usd * 1.62,
        }
        ordered = sorted(paths.items(), key=lambda x: x[1], reverse=True)
        return {
            "paths": [{"path": k, "projected_salary_usd": round(v, 2)} for k, v in ordered],
            "recommended": ordered[0][0],
        }

    def _success_stories(self, match_score: float) -> List[Dict[str, Any]]:
        benchmark_bucket = "top_quartile" if match_score >= 72 else "mid_quartile" if match_score >= 52 else "early_stage"
        return [
            {
                "persona": "Backend career restarter",
                "timeline_weeks": 9,
                "match_rate_lift_points": 14.0,
                "result": "Moved from low callbacks to two final rounds.",
                "bucket": benchmark_bucket,
            },
            {
                "persona": "Frontend specialist pivoting to fullstack",
                "timeline_weeks": 11,
                "match_rate_lift_points": 17.5,
                "result": "Secured offer after closing cloud and API gaps.",
                "bucket": benchmark_bucket,
            },
        ]
