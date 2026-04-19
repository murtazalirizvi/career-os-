# Career-OS: API Implementation Details (Feature 1 - 5)

## Feature 1: The Lens (Resume Scoring)
- **Endpoint:** `POST /v1/resume/analyze`
- **Logic:** Parse PDF -> Clean Text -> Send to Gemini with JD -> Receive JSON Coordinates -> Store in SQLite -> Notify Frontend.

## Feature 2: The Rebound (Autopsy)
- **Endpoint:** `POST /v1/interview/analyze-failed`
- **Logic:** Receive user transcript/voice -> Gemini identifies "Gap" -> Cross-reference with `market_trends` -> Suggest fix.

## Feature 3: Skill-Arbitrage
- **Endpoint:** `GET /v1/market/trends`
- **Logic:** Check SQLite cache (if < 24h old) -> If old, trigger BackgroundTask to fetch from Adzuna API -> Update SQLite -> Return JSON.

## Feature 4: Persona-Play
- **Endpoint:** `POST /v1/interview/chat`
- **Logic:** Receive message -> Pull `Interview` history from SQLite -> Inject Persona Prompt -> Get Gemini Response -> Append to History -> Return.

## Feature 5: Narrative Architect
- **Endpoint:** `POST /v1/portfolio/sync`
- **Logic:** Receive GitHub URL -> `PyGithub` clones/scans README & file tree -> Gemini generates "Engineering Story" -> Store in `portfolio_analysis` table.
