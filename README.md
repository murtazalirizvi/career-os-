# Career OS — AI-Powered Career Intelligence Platform

> **Last Updated:** April 25, 2026  
> **Status:** Production Ready ✅  
> **Version:** 1.0.0  
> Built for the modern job seeker who is tired of guessing.

---

## The Problem

Job hunting in 2025 is broken — not because opportunities don't exist, but because candidates operate blind. They submit resumes without knowing how an ATS or hiring manager actually reads them. They walk out of interviews without understanding why they failed. They apply to roles without knowing whether their skills are even competitive in the current market. They practice interviews with generic questions that bear no resemblance to the real thing. And when it's time to tell their story — on LinkedIn, in a portfolio, in a pitch — they struggle to connect their technical work to a compelling narrative.

The result: talented people lose opportunities not because of what they lack, but because they lack the right intelligence at the right moment.

---

## The Real-World Connection

Every year, millions of candidates go through hundreds of applications, rejections, and interviews with almost zero structured feedback. Career coaches are expensive and inaccessible. Job boards give you listings but no insight. LinkedIn tells you who got hired, not why. The gap between "I applied" and "I got the offer" is a black box.

Career OS tears open that black box.

---

## What We Built

Career OS is a full-stack, AI-augmented career intelligence platform with five deeply integrated analysis engines, each targeting a specific failure point in the job search lifecycle.

### Feature 1 — Hiring Manager Lens (Resume Analyzer)

Upload your resume and a job description. The engine scores your resume across four dimensions:

- **Visual Hierarchy** — eye-tracking simulation using computer vision (OpenCV) to identify where attention lands and where it drops off
- **ATS Integrity** — checks for non-standard fonts, missing sections, and keyword gaps that cause automated rejection
- **Semantic Match** — NLP-based alignment between your resume language and the job description
- **Competitive Benchmark** — compares your resume against role-category norms

Gemini 2.0 Flash then generates natural-language coaching recommendations on top of the heuristic scores. You get a version history, a "Ready to Apply" badge when you cross the threshold, and a downloadable report.

### Feature 2 — Interview Rebound (Post-Interview Autopsy)

After an interview — whether you passed or failed — you log your notes, paste your transcript (or upload a VTT file), and the engine performs a full autopsy:

- Technical depth scoring (did you explain tradeoffs, not just answers?)
- Behavioral signal analysis (confidence words vs. hedge words, filler detection)
- Tone and emotional state mapping
- Strategic action plan for the next round or next company
- AssemblyAI integration for audio transcription

Gemini generates a personalized debrief with specific things to fix before the next interview. Reminders are scheduled automatically.

### Feature 3 — Skill Arbitrage (Market Intelligence + Gap Analysis)

Enter a target role and region. The engine pulls live job market data (Adzuna, Reed APIs) and runs:

- **Market Snapshot** — demand/supply clustering, salary mapping, remote market analysis
- **Skill Gap Analysis** — radar chart comparing your current skills to what the top 10% of candidates have
- **Skill Sprint** — a day-by-day learning plan for your highest-priority gap skill, with quizzes and resume injection snippets
- **Future Insight** — obsolescence risk scoring, 2027 skill forecasts, agentic AI readiness score
- **ROI Report** — callback probability uplift and lifetime earnings delta from closing specific gaps

### Feature 4 — Persona Play (AI Mock Interviewer)

Practice against four distinct interviewer archetypes:

| Persona | Style |
|---|---|
| Stone-Faced Architect | Deep architecture pressure, minimal feedback |
| Rushed Founder | High-speed interruptions, priority pivots |
| Non-Tech HR | ELI5 framing, clarity stress test |
| Deep-Diver | Layered why-question chains |

Each session is dynamically tailored to your target role and optionally a specific company. Gemini generates the questions. After each answer, you get real-time coaching hints, deep logic scoring, and a final synthesis report. Sessions can be shared via a token link.

### Feature 5 — Narrative Architect (Story Builder)

Point the engine at your GitHub repo and paste your resume and LinkedIn text. It:

- Analyzes your codebase architecture (microservice vs. MVC, tech stack, complexity)
- Builds a problem-solution narrative from your actual project work
- Generates a talk track for interviews and pitches
- Identifies gaps between your GitHub reality and your resume claims
- Exports LinkedIn posts, portfolio site content, and a consistency check across all three surfaces

---

## How It All Connects

Every feature feeds a unified **Readiness Score** on the dashboard — a composite of your resume score, latest interview autopsy score, and skill gap match score. The job tracker (Kanban pipeline) ties applications to specific analyses so you can see which resume version you used for which company and what happened.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLModel |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI | Google Gemini 2.0 Flash |
| Transcription | AssemblyAI |
| Job Market Data | Adzuna API, Reed API |
| Computer Vision | OpenCV, NumPy |
| PDF Processing | PyMuPDF (fitz), ReportLab |
| NLP | Custom tokenizer + semantic alignment |
| Frontend | Vanilla JS, Tailwind CSS |
| Containerization | Docker, Docker Compose |

---

## Architecture

```
Frontend (HTML/JS/Tailwind)
        │
        ▼
FastAPI Backend (Career OS API)
        │
   ┌────┴────────────────────────────────────┐
   │                                         │
Analysis Engines (5 features)         Services Layer
   │                                    (storage, reporting)
   ├── Feature1Engine (CV + NLP)              │
   ├── Feature2Engine (transcript analysis)   │
   ├── Feature3Engine (market + gap)          │
   ├── Feature4Engine (persona play)          │
   └── Feature5Engine (narrative)             │
        │                                     │
        ▼                                     ▼
   Gemini 2.0 Flash (AI layer)         SQLite / PostgreSQL
```

All AI calls are best-effort with graceful degradation — if Gemini is unavailable, heuristic results are returned without failure.

---

## Quick Start

### Prerequisites
- Python 3.12+
- A Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Local Setup

```bash
# Backend
cd Backend
pip install -r requirements.txt
cp .env.example .env        # Add your API keys
python -m uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd Frontend
python serve.py
```

- Frontend: http://localhost:5500
- API + Docs: http://localhost:8000/docs

### Docker (one command)

```bash
cp Backend/.env.example Backend/.env   # Add your API keys
docker-compose up --build
```

### API Keys

| Key | Feature | Source |
|---|---|---|
| `GEMINI_API_KEY` | AI coaching across all features | [aistudio.google.com](https://aistudio.google.com) |
| `ASSEMBLYAI_API_KEY` | Audio transcription (Feature 2) | [assemblyai.com](https://www.assemblyai.com) |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Live job market data (Feature 3) | [developer.adzuna.com](https://developer.adzuna.com) |
| `REED_API_KEY` | Additional job listings (Feature 3) | [reed.co.uk/developers](https://www.reed.co.uk/developers) |

All keys are optional — features degrade gracefully without them.

---

## Key Design Decisions

- **Graceful AI degradation** — every Gemini call has a heuristic fallback, so the platform works even without an API key
- **Cross-feature data reuse** — resume text parsed in Feature 1 is stored and reused by Feature 5, avoiding redundant uploads
- **Version history** — every resume analysis is versioned so candidates can track improvement over time
- **Composite readiness score** — a single number that aggregates resume, interview, and skill gap signals
- **Rate limiting + security headers** — production-ready middleware out of the box

---

## Running Tests

```bash
cd Backend
pytest tests/ -v
```
