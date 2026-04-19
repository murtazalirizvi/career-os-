from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Sequence

import httpx

_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    "data",
}

_SECTION_PATTERNS = {
    "overview": re.compile(r"\b(overview|summary)\b", re.I),
    "architecture": re.compile(r"\b(architecture|design|system)\b", re.I),
    "setup": re.compile(r"\b(install|setup|run|quickstart)\b", re.I),
    "api": re.compile(r"\b(api|endpoint)\b", re.I),
    "testing": re.compile(r"\b(test|pytest|unit test)\b", re.I),
    "license": re.compile(r"\b(license)\b", re.I),
}

KEYWORDS_MICROSERVICE = {"gateway", "service", "docker-compose", "kubernetes", "grpc", "queue"}
KEYWORDS_MVC = {"models", "views", "controllers", "templates"}


class Feature5NarrativeEngine:
    def __init__(self) -> None:
        self.workspace_root = Path(__file__).resolve().parents[3]

    def build_full_session(
        self,
        *,
        repo_subpath: str,
        target_role: str,
        tone: str,
        jd_text: str,
        resume_text: str,
        linkedin_text: str,
        github_repo: str,
        selected_projects: Sequence[str] | None,
    ) -> Dict[str, Any]:
        repo_path = self._resolve_repo_path(repo_subpath)
        facts = self._collect_repo_facts(repo_path)
        facts["github_repo_insights"] = self._fetch_github_repo_insights(github_repo)

        deep = self._build_deep_analysis(facts)
        narrative = self._build_narrative(facts, target_role, tone, jd_text, selected_projects)
        talk = self._build_talk_track(facts, target_role, tone)
        gap = self._build_gap_analysis(facts)
        export_sync = self._build_export_sync(facts, narrative, target_role, jd_text)
        consistency = self.consistency_check(narrative, resume_text, linkedin_text)

        return {
            "deep_analysis": deep,
            "narrative": narrative,
            "talk_track": talk,
            "gap_analysis": gap,
            "export_sync": export_sync,
            "consistency_check": consistency,
        }

    def consistency_check(self, narrative: Dict[str, Any], resume_text: str, linkedin_text: str) -> Dict[str, Any]:
        resume_tokens = self._tokenize(resume_text)
        linkedin_tokens = self._tokenize(linkedin_text)
        narrative_tokens = self._tokenize(" ".join(narrative.get("epic_5_2", {}).get("problem_solution_narrative", [])))

        overlap_resume = self._overlap_score(narrative_tokens, resume_tokens)
        overlap_linkedin = self._overlap_score(narrative_tokens, linkedin_tokens)

        warnings: List[str] = []
        if overlap_resume < 0.25 and resume_text.strip():
            warnings.append("Narrative language has low overlap with resume terminology; align project names and metrics.")
        if overlap_linkedin < 0.25 and linkedin_text.strip():
            warnings.append("Narrative language has low overlap with LinkedIn summary; keep stack and impact claims consistent.")

        return {
            "resume_overlap": round(overlap_resume * 100, 2),
            "linkedin_overlap": round(overlap_linkedin * 100, 2),
            "consistency_score": round(((overlap_resume + overlap_linkedin) / 2) * 100, 2),
            "warnings": warnings,
            "status": "pass" if not warnings else "review",
        }

    def export_selected(self, export_sync: Dict[str, Any], include_sections: Sequence[str]) -> Dict[str, Any]:
        allowed = {
            "linkedin_sync": export_sync["epic_5_5"]["linkedin_sync"],
            "portfolio_website": export_sync["epic_5_5"]["portfolio_website"],
            "resume_optimizer": export_sync["epic_5_5"]["resume_optimizer"],
            "case_study_pdf": export_sync["epic_5_5"]["case_study_pdf"],
            "consistency_check": export_sync["epic_5_5"]["consistency_check"],
        }

        selected = [name for name in include_sections if name in allowed]
        payload = {name: allowed[name] for name in selected}

        lines = ["# Feature 5 Narrative Export Bundle", ""]
        for name in selected:
            lines.append(f"## {name.replace('_', ' ').title()}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(allowed[name], ensure_ascii=True, indent=2))
            lines.append("```")
            lines.append("")

        return {
            "exported_sections": selected,
            "markdown_bundle": "\n".join(lines),
            "payload": payload,
        }

    def _resolve_repo_path(self, repo_subpath: str) -> Path:
        rel = repo_subpath.strip() or "."
        path = (self.workspace_root / rel).resolve()
        if not str(path).startswith(str(self.workspace_root)):
            raise ValueError("repo_subpath must stay within workspace root")
        if not path.exists() or not path.is_dir():
            raise ValueError("repo_subpath must point to an existing directory")
        return path

    def _collect_repo_facts(self, repo_path: Path) -> Dict[str, Any]:
        files: List[Path] = []
        for root, dirs, names in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in _IGNORE_DIRS]
            for name in names:
                files.append(Path(root) / name)

        ext_counts: Dict[str, int] = {}
        py_files = 0
        js_files = 0
        tests = 0
        doc_lines = 0
        comment_lines = 0
        code_lines = 0
        latest_mtime = 0.0

        sampled_logic: List[str] = []
        for file_path in files:
            ext = file_path.suffix.lower() or "<none>"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            if ext == ".py":
                py_files += 1
            if ext in {".js", ".ts", ".tsx", ".jsx"}:
                js_files += 1
            if "test" in file_path.name.lower():
                tests += 1
            latest_mtime = max(latest_mtime, file_path.stat().st_mtime)

            if ext in {".py", ".js", ".ts", ".tsx", ".jsx", ".md"}:
                text = self._safe_read(file_path)
                lines = text.splitlines()
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                        comment_lines += 1
                    else:
                        code_lines += 1
                    if ext == ".md":
                        doc_lines += 1
                if ext in {".py", ".js", ".ts", ".tsx", ".jsx"} and len(sampled_logic) < 120:
                    sampled_logic.extend(lines[:30])

        readme = self._safe_read(repo_path / "README.md")
        has_frontend = (repo_path / "Frontend").exists() or (repo_path / "frontend").exists()
        has_backend = (repo_path / "Backend").exists() or (repo_path / "backend").exists()
        has_api_dir = any("api" in p.parts for p in files)
        has_models = any("models" in p.name.lower() for p in files)
        has_ci = any(p.name.lower() in {".github", "azure-pipelines.yml", "gitlab-ci.yml"} for p in files)

        folders = {p.parts[0] for p in (f.relative_to(repo_path) for f in files) if p.parts}
        projects = sorted(x for x in folders if x and not x.startswith("."))

        return {
            "repo_path": str(repo_path),
            "file_count": len(files),
            "ext_counts": ext_counts,
            "python_files": py_files,
            "javascript_files": js_files,
            "test_files": tests,
            "documentation_lines": doc_lines,
            "comment_lines": comment_lines,
            "code_lines": code_lines,
            "latest_activity": datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat() if latest_mtime else None,
            "readme": readme,
            "has_frontend": has_frontend,
            "has_backend": has_backend,
            "has_api_dir": has_api_dir,
            "has_models": has_models,
            "has_ci": has_ci,
            "sampled_logic": sampled_logic,
            "projects": projects,
            "all_file_names": [p.name.lower() for p in files],
        }

    def _build_deep_analysis(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        architecture_style = self._architecture_style(facts)
        sophistication = self._sophistication_score(facts)
        logic = self._logic_identification(facts)
        readme = self._readme_polisher(facts.get("readme", ""))
        tutorial = self._tutorial_detector(facts)

        return {
            "epic_5_1": {
                "architecture_mapping": architecture_style,
                "sophistication_scoring": sophistication,
                "logic_identification": logic,
                "readme_polisher": readme,
                "tutorial_detector": tutorial,
            }
        }

    def _build_narrative(
        self,
        facts: Dict[str, Any],
        target_role: str,
        tone: str,
        jd_text: str,
        selected_projects: Sequence[str] | None,
    ) -> Dict[str, Any]:
        project_list = list(selected_projects or facts.get("projects", []))[:4] or ["Career-OS"]
        stack = self._stack_summary(facts)
        tone_label = "Deep Tech" if tone == "deep_tech" else "Business"

        problems = [
            f"Designed a candidate-first platform to improve interview velocity for {target_role} applicants.",
            "Unified resume critique, interview autopsy, market arbitrage, and persona practice under one workflow.",
        ]
        if tone == "business":
            problems = [
                "Built an integrated product that shortens interview preparation cycles and raises profile quality.",
                "Connected resume, interview, and market readiness into one measurable command center.",
            ]

        stars = []
        for name in project_list:
            stars.append(
                {
                    "project": name,
                    "situation": "Candidates lacked evidence-backed story framing for interviews.",
                    "task": "Convert repository work into concise and credible narratives.",
                    "action": "Implemented automated architecture analysis, STAR generation, and claim-evidence warnings.",
                    "result": "Produced recruiter-friendly narratives with measurable impact placeholders and consistency checks.",
                }
            )

        tradeoffs = [
            {
                "decision": "Monolithic FastAPI backend with SQLite",
                "benefit": "Fast iteration and deterministic local development in beta.",
                "trade_off": "Limited horizontal scale versus distributed services.",
                "mitigation": "Schema-first modules and isolated engines make migration to managed DB straightforward.",
            },
            {
                "decision": "Heuristic-first narrative scoring",
                "benefit": "Low latency and transparent explanation without heavy model dependency.",
                "trade_off": "Less semantic nuance than full LLM pipelines.",
                "mitigation": "Expose confidence and evidence warnings for user review.",
            },
        ]

        metrics = [
            "Cut project explanation time from 10 minutes to under 2 minutes with prepared walk-through scripts.",
            "Increase narrative completeness score to 90%+ by enforcing STAR + evidence links.",
            "Raise interview callback probability by 12-25% through impact-focused profile copy.",
            "Reduce recruiter clarification follow-ups by 30% with aligned resume and LinkedIn claims.",
        ]

        if jd_text.strip():
            jd_tokens = sorted(list(self._tokenize(jd_text)))[:12]
            metrics.append(f"JD alignment tokens detected: {', '.join(jd_tokens[:8])}.")

        gap_reframing = [
            "Frame gap periods as targeted upskilling sprints with explicit outcomes.",
            "Tie learning periods to shipped repos, measurable milestones, and interview readiness gains.",
        ]

        return {
            "epic_5_2": {
                "problem_solution_narrative": problems,
                "star_summaries": stars,
                "tradeoff_documentation": tradeoffs,
                "impact_metrics": metrics,
                "narrative_personalization": {
                    "selected_tone": tone_label,
                    "stack_anchor": stack,
                    "voice_guidelines": self._tone_guidelines(tone),
                },
                "employment_gap_reframing": gap_reframing,
                "gemini_suggestions": self._maybe_gemini_suggestions(project_list, target_role, tone),
            }
        }

    def _build_talk_track(self, facts: Dict[str, Any], target_role: str, tone: str) -> Dict[str, Any]:
        projects = facts.get("projects", [])[:4] or ["Career-OS"]
        walkthrough = [
            "Open README and explain the user problem and success metric.",
            "Show backend API surface by feature and describe request/response contracts.",
            "Walk through one engine module to explain custom heuristics and design choices.",
            "Run tests to prove deterministic behavior and reliability.",
            "Demonstrate frontend command center and dedicated feature workspaces.",
            "Close with trade-offs, roadmap, and senior-level improvements.",
        ]

        gotchas = [
            "How do you validate that generated narratives are evidence-backed and not inflated?",
            "What happens when repository metadata is sparse or stale?",
            "How would you migrate from SQLite to Postgres without breaking API contracts?",
            "How do you prevent tutorial-style boilerplate from being scored as senior-level work?",
        ]

        practice = {
            "mode": "mock-github-review",
            "drills": [
                "90-second elevator pitch",
                "2-minute architecture defense",
                "edge-case Q&A under time pressure",
                "business-value summary for non-technical interviewer",
            ],
            "target_role": target_role,
        }

        metaphors = [
            "Narrative engine is a compiler: raw repo signals in, optimized interview story out.",
            "Gap analysis is technical debt analysis for your portfolio.",
            "Talk track script is a runbook for live production demos.",
        ]

        presentation = {
            "mode": "screen-share-clean",
            "recommended_layout": ["story first", "evidence panel", "trade-off panel", "metrics panel"],
            "tone_hint": "keep concise and technical" if tone == "deep_tech" else "lead with business outcomes",
            "project_highlights": projects,
        }

        return {
            "epic_5_3": {
                "code_walkthrough_script": walkthrough,
                "edge_case_anticipator": gotchas,
                "show_and_tell_practice": practice,
                "metaphor_generator": metaphors,
                "presentation_mode": presentation,
            }
        }

    def _build_gap_analysis(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        exts = facts.get("ext_counts", {})
        has_tests = facts.get("test_files", 0) > 0
        has_docs = facts.get("documentation_lines", 0) > 40
        has_frontend = facts.get("has_frontend", False)
        has_backend = facts.get("has_backend", False)

        missing = []
        if not has_tests:
            missing.append("Automated test coverage")
        if not has_docs:
            missing.append("Comprehensive architecture and runbook documentation")
        if not has_frontend:
            missing.append("User-facing interface or demo client")
        if not has_backend:
            missing.append("API/backend implementation")
        if ".yml" not in exts and ".yaml" not in exts:
            missing.append("CI pipeline configuration")

        feature_suggestion = {
            "title": "Production Telemetry + Experiment Dashboard",
            "why_senior": "Demonstrates observability, product thinking, and decision loops beyond feature coding.",
            "implementation_hint": "Add event tracking schema, retention dashboards, and alert thresholds for narrative quality drift.",
        }

        doc_score = self._documentation_score(facts)

        opensource = {
            "license_present": any("license" in n for n in facts.get("all_file_names", [])),
            "contributing_present": any("contributing" in n for n in facts.get("all_file_names", [])),
            "issue_templates_present": any("issue" in n and "template" in n for n in facts.get("all_file_names", [])),
            "encouragement": "Add CONTRIBUTING.md + issue templates and publish one good-first-issue ticket.",
            "github_repo_scan": facts.get("github_repo_insights", {}),
        }

        stale = {
            "latest_activity": facts.get("latest_activity"),
            "stale_risk": self._stale_risk(facts.get("latest_activity")),
            "recommendation": "Schedule a monthly maintenance commit and changelog note.",
        }

        return {
            "epic_5_4": {
                "coverage_report": {
                    "present_capabilities": {
                        "backend": has_backend,
                        "frontend": has_frontend,
                        "tests": has_tests,
                        "docs": has_docs,
                    },
                    "missing_coverage": missing,
                },
                "feature_suggestion": feature_suggestion,
                "documentation_score": doc_score,
                "open_source_encourager": opensource,
                "stale_date_alert": stale,
            }
        }

    def _build_export_sync(
        self,
        facts: Dict[str, Any],
        narrative: Dict[str, Any],
        target_role: str,
        jd_text: str,
    ) -> Dict[str, Any]:
        star_items = narrative["epic_5_2"]["star_summaries"]
        top_projects = [x["project"] for x in star_items[:3]]

        linkedin = {
            "headline": f"{target_role} | Portfolio built with evidence-backed storytelling and interview simulation",
            "project_description": "Built Career-OS, an integrated platform combining resume intelligence, interview autopsy, and narrative generation with FastAPI and a responsive frontend.",
            "achievement_bullets": [
                "Designed modular feature engines and API contracts for iterative product expansion.",
                "Implemented test-backed analytics workflows for deterministic coaching signals.",
                "Shipped recruiter-ready narrative exports with consistency and evidence checks.",
            ],
        }

        portfolio = {
            "one_click_template": {
                "hero": "From Raw Repos to Interview-Ready Storytelling",
                "sections": ["Problem", "Architecture", "Trade-offs", "Impact Metrics", "Live Demo"],
                "deploy_options": ["Vercel static site", "GitHub Pages", "Netlify"],
            },
            "content_blocks": star_items[:2],
        }

        resume_opt = self._resume_optimizer(top_projects, jd_text)

        case_study = {
            "title": "Narrative Architect Case Study",
            "markdown": self._case_study_markdown(facts, narrative),
            "pdf_render_hint": "Render markdown to PDF using pandoc or print stylesheet from frontend workspace.",
        }

        evidence_warnings = self._claim_evidence_warnings(facts, narrative)

        return {
            "epic_5_5": {
                "linkedin_sync": linkedin,
                "portfolio_website": portfolio,
                "resume_optimizer": resume_opt,
                "case_study_pdf": case_study,
                "consistency_check": {
                    "claim_evidence_soft_warnings": evidence_warnings,
                    "policy": "Warnings are advisory only and do not block export.",
                },
            }
        }

    def _architecture_style(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        file_names = set(facts.get("all_file_names", []))
        has_mvc = any(tok in file_names for tok in KEYWORDS_MVC) or facts.get("has_models", False)
        microservice_tokens = [k for k in KEYWORDS_MICROSERVICE if any(k in n for n in file_names)]

        style = "monolith"
        if microservice_tokens:
            style = "hybrid-monolith"
        if microservice_tokens and len(microservice_tokens) >= 3:
            style = "microservice-leaning"

        return {
            "identified_style": style,
            "signals": {
                "has_frontend": facts.get("has_frontend", False),
                "has_backend": facts.get("has_backend", False),
                "has_models": has_mvc,
                "api_modules": facts.get("has_api_dir", False),
                "microservice_markers": microservice_tokens,
            },
            "mapping_summary": "Project is modularized by feature engines and API layers inside a single deployable backend.",
        }

    def _sophistication_score(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        py_files = float(facts.get("python_files", 0))
        js_files = float(facts.get("javascript_files", 0))
        test_files = float(facts.get("test_files", 0))
        docs = float(facts.get("documentation_lines", 0))
        has_ci = 1.0 if facts.get("has_ci") else 0.0

        score = 25 + min(24, py_files * 0.9 + js_files * 0.7) + min(18, test_files * 2.5) + min(16, docs / 20) + has_ci * 7
        score = max(0.0, min(100.0, score))

        tier = "advanced" if score >= 78 else "intermediate" if score >= 55 else "foundational"
        return {
            "score": round(score, 2),
            "tier": tier,
            "breakdown": {
                "stack_depth": round(min(24, py_files * 0.9 + js_files * 0.7), 2),
                "testing_maturity": round(min(18, test_files * 2.5), 2),
                "documentation_maturity": round(min(16, docs / 20), 2),
                "delivery_hardening": round(has_ci * 7, 2),
            },
        }

    def _logic_identification(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        lines = facts.get("sampled_logic", [])
        logic_hits = 0
        boilerplate_hits = 0
        examples: List[str] = []

        custom_markers = ("if ", "for ", "while ", "try:", "except", "return", "score", "analysis", "heuristic")
        boilerplate_markers = ("from fastapi", "app = ", "router = ", "import React", "document.getElementById")

        for raw in lines:
            line = raw.strip().lower()
            if not line:
                continue
            if any(tok in line for tok in custom_markers):
                logic_hits += 1
                if len(examples) < 5 and len(raw.strip()) < 140:
                    examples.append(raw.strip())
            if any(tok in line for tok in boilerplate_markers):
                boilerplate_hits += 1

        ratio = logic_hits / max(1, logic_hits + boilerplate_hits)
        return {
            "custom_logic_ratio": round(ratio * 100, 2),
            "logic_density": "high" if ratio >= 0.6 else "medium" if ratio >= 0.38 else "low",
            "non_boilerplate_examples": examples,
        }

    def _readme_polisher(self, readme_text: str) -> Dict[str, Any]:
        present = {name: bool(pattern.search(readme_text)) for name, pattern in _SECTION_PATTERNS.items()}
        missing = [name for name, ok in present.items() if not ok]

        polished_outline = [
            "# Project",
            "## Overview",
            "## Architecture",
            "## Setup",
            "## API / Usage",
            "## Testing",
            "## Trade-offs",
            "## License",
        ]

        return {
            "present_sections": present,
            "missing_sections": missing,
            "recommended_outline": polished_outline,
            "quick_fix": "Add architecture diagram + testing command + trade-off notes to improve reviewer confidence.",
        }

    def _tutorial_detector(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        files = facts.get("all_file_names", [])
        tutorial_markers = [
            "todo",
            "weather-app",
            "tutorial",
            "hello-world",
            "bootcamp",
        ]
        tutorial_hits = [m for m in tutorial_markers if any(m in name for name in files)]

        originality_signals = []
        if facts.get("test_files", 0) >= 4:
            originality_signals.append("Meaningful test suite across features")
        if facts.get("documentation_lines", 0) > 150:
            originality_signals.append("Extensive product and feature requirements")
        if facts.get("python_files", 0) > 12 and facts.get("javascript_files", 0) > 0:
            originality_signals.append("Multi-layer architecture (frontend + backend + analysis engines)")

        confidence = 100 - min(80, len(tutorial_hits) * 20)
        if originality_signals:
            confidence = min(100, confidence + 15)

        return {
            "clone_risk_score": round(max(0, 100 - confidence), 2),
            "likely_original": confidence >= 65,
            "tutorial_markers": tutorial_hits,
            "originality_signals": originality_signals,
        }

    def _documentation_score(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        comments = float(facts.get("comment_lines", 0))
        code = float(facts.get("code_lines", 1))
        docs = float(facts.get("documentation_lines", 0))

        comment_ratio = comments / max(1.0, code)
        doc_ratio = docs / max(1.0, code)
        score = min(100.0, 40 + comment_ratio * 220 + doc_ratio * 120)

        return {
            "score": round(score, 2),
            "comment_ratio": round(comment_ratio, 4),
            "docs_to_code_ratio": round(doc_ratio, 4),
            "rating": "excellent" if score >= 80 else "good" if score >= 62 else "needs_work",
        }

    def _stale_risk(self, latest_activity_iso: str | None) -> str:
        if not latest_activity_iso:
            return "unknown"
        try:
            latest = datetime.fromisoformat(latest_activity_iso)
            delta_days = (datetime.now(timezone.utc) - latest).days
        except Exception:
            return "unknown"

        if delta_days <= 21:
            return "low"
        if delta_days <= 75:
            return "medium"
        return "high"

    def _resume_optimizer(self, projects: Sequence[str], jd_text: str) -> Dict[str, Any]:
        jd_tokens = self._tokenize(jd_text)
        ranked: List[Dict[str, Any]] = []
        for name in projects:
            name_tokens = self._tokenize(name)
            score = self._overlap_score(name_tokens, jd_tokens)
            ranked.append({
                "project": name,
                "jd_relevance_score": round(score * 100, 2),
                "reason": "Keyword overlap with target JD and architecture relevance.",
            })

        ranked.sort(key=lambda x: x["jd_relevance_score"], reverse=True)
        top = ranked[:3]

        return {
            "top_3_projects": top,
            "selection_guidance": "Prioritize projects that demonstrate scale, ownership, and measurable outcomes.",
        }

    def _claim_evidence_warnings(self, facts: Dict[str, Any], narrative: Dict[str, Any]) -> List[Dict[str, str]]:
        warnings: List[Dict[str, str]] = []
        metric_claims = narrative["epic_5_2"].get("impact_metrics", [])
        has_tests = facts.get("test_files", 0) > 0
        has_docs = facts.get("documentation_lines", 0) > 30

        for claim in metric_claims[:4]:
            if "callback" in claim.lower() and not has_tests:
                warnings.append(
                    {
                        "claim": claim,
                        "warning": "Callback lift claim lacks testing/experiment evidence in repo; present as hypothesis.",
                    }
                )
            elif "reduce" in claim.lower() and not has_docs:
                warnings.append(
                    {
                        "claim": claim,
                        "warning": "Reduction claim should reference benchmark notes or issue history.",
                    }
                )

        if not warnings:
            warnings.append(
                {
                    "claim": "All generated impact claims",
                    "warning": "Attach before/after metrics or commit references when presenting to interviewers.",
                }
            )
        return warnings

    def _stack_summary(self, facts: Dict[str, Any]) -> str:
        exts = facts.get("ext_counts", {})
        ranked = sorted(exts.items(), key=lambda x: x[1], reverse=True)
        top = [ext for ext, _ in ranked[:4] if ext != "<none>"]
        return ", ".join(top) if top else "python, javascript"

    def _tone_guidelines(self, tone: str) -> List[str]:
        if tone == "business":
            return [
                "Lead with business outcome in first sentence.",
                "Use fewer implementation details and more risk/impact framing.",
                "Translate architecture decisions into cost, speed, and reliability language.",
            ]
        return [
            "Lead with architecture and constraints.",
            "Quantify trade-offs and failure modes.",
            "Use concrete implementation details with performance context.",
        ]

    def _case_study_markdown(self, facts: Dict[str, Any], narrative: Dict[str, Any]) -> str:
        stars = narrative["epic_5_2"].get("star_summaries", [])
        lines = [
            "# Narrative Architect Case Study",
            "",
            "## Problem",
            "Candidates struggled to explain project impact with clear evidence and trade-offs.",
            "",
            "## Architecture",
            f"Repository analyzed from: {facts.get('repo_path')}",
            "Feature-based modular backend with analysis engines and UI workspace layers.",
            "",
            "## STAR Evidence",
        ]
        for idx, star in enumerate(stars[:3], start=1):
            lines.extend(
                [
                    f"### Story {idx}: {star.get('project')}",
                    f"- Situation: {star.get('situation')}",
                    f"- Task: {star.get('task')}",
                    f"- Action: {star.get('action')}",
                    f"- Result: {star.get('result')}",
                    "",
                ]
            )

        lines.extend(
            [
                "## Trade-offs",
                "Accepted monolith speed for beta execution while preserving modular migration paths.",
                "",
                "## Outcome",
                "Generated reusable interview scripts, LinkedIn copy, and consistency warnings to improve profile trust.",
            ]
        )
        return "\n".join(lines)

    def _safe_read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def _fetch_github_repo_insights(self, github_repo: str) -> Dict[str, Any]:
        repo = (github_repo or "").strip()
        if not repo:
            return {"status": "not_provided"}

        cleaned = repo.replace("https://github.com/", "").strip("/")
        if "/" not in cleaned:
            return {"status": "invalid", "detail": "Use owner/repo or full GitHub URL."}

        owner, name = cleaned.split("/", 1)
        base = f"https://api.github.com/repos/{owner}/{name}"
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "career-os-feature5"}

        try:
            with httpx.Client(timeout=7.0) as client:
                repo_res = client.get(base, headers=headers)
                if repo_res.status_code >= 400:
                    return {"status": "unavailable", "repo": cleaned, "http": repo_res.status_code}
                repo_payload = repo_res.json()

                issues_res = client.get(f"{base}/issues", params={"state": "open", "per_page": 50}, headers=headers)
                pulls_res = client.get(f"{base}/pulls", params={"state": "open", "per_page": 50}, headers=headers)

                issues = issues_res.json() if issues_res.status_code < 400 else []
                pulls = pulls_res.json() if pulls_res.status_code < 400 else []

                issue_count = len([x for x in issues if "pull_request" not in x]) if isinstance(issues, list) else 0
                pr_count = len(pulls) if isinstance(pulls, list) else 0

                return {
                    "status": "ok",
                    "repo": cleaned,
                    "stars": repo_payload.get("stargazers_count", 0),
                    "forks": repo_payload.get("forks_count", 0),
                    "open_issues": repo_payload.get("open_issues_count", issue_count),
                    "open_prs": pr_count,
                    "default_branch": repo_payload.get("default_branch", "main"),
                    "updated_at": repo_payload.get("updated_at"),
                    "has_issues_enabled": bool(repo_payload.get("has_issues", False)),
                }
        except Exception:
            return {"status": "error", "repo": cleaned}

    def _maybe_gemini_suggestions(self, project_list: Sequence[str], target_role: str, tone: str) -> List[str]:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return []

        prompt = (
            "Generate 3 concise, evidence-oriented interview narrative lines for these projects: "
            f"{', '.join(project_list[:4])}. Target role: {target_role}. Tone: {tone}. "
            "Return plain bullet lines only, max 18 words each."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        body = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, json=body)
                if res.status_code >= 400:
                    return []
                payload = res.json()
        except Exception:
            return []

        text_parts: List[str] = []
        for cand in payload.get("candidates", []):
            for part in ((cand.get("content") or {}).get("parts") or []):
                txt = str(part.get("text") or "").strip()
                if txt:
                    text_parts.append(txt)

        merged = "\n".join(text_parts)
        if not merged:
            return []

        lines = [
            re.sub(r"^[\-\*\d\.\)\s]+", "", ln).strip()
            for ln in merged.splitlines()
            if ln.strip()
        ]
        return lines[:3]

    def _tokenize(self, text: str) -> set[str]:
        return {x for x in re.findall(r"[a-zA-Z]{4,}", (text or "").lower())}

    def _overlap_score(self, left: Iterable[str], right: Iterable[str]) -> float:
        lset = set(left)
        rset = set(right)
        if not lset or not rset:
            return 0.0
        return len(lset.intersection(rset)) / len(lset)


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)
