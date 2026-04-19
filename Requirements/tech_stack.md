# Complete Tech Stack: Career-OS Platform

## 1. Frontend: Ultra-Lean Interface
- **Languages:** HTML5, CSS3, JavaScript (ES6+).
- **Framework:** Vanilla JS (No heavy frameworks like React to ensure speed and simplicity).
- **Styling:** Tailwind CSS (via CDN) for modern, responsive UI.
- **API Communication:** Fetch API for asynchronous calls to FastAPI.

## 2. Backend: High-Speed Engine
- **Framework:** FastAPI (Python 3.12+).
- **Server:** Uvicorn (ASGI).
- **AI Orchestration:** Google Generative AI Python SDK (Gemini 1.5 Pro).
- **Processing:** PyMuPDF (fitz) for PDF parsing; OpenCV for coordinate mapping.

## 3. Database: Portable Core
- **Engine:** SQLite.
- **ORM:** SQLModel (pydantic + sqlalchemy) for seamless data handling with FastAPI.
- **Migrations:** Alembic.

## 4. External Integrations
- **AI Model:** Gemini 1.5 Pro (Primary Brain).
- **Voice:** Web Speech API (Input) & ElevenLabs API (Output).
- **GitHub:** PyGithub for repository analysis.
- **Scraping:** BeautifulSoup4 & HTTPX.
