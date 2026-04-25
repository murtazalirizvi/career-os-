<!-- we are good - system architecture documented -->
# Career-OS: Advanced Backend Architecture & System Design

This document serves as a blueprint for the AI Agent to implement a resilient, high-performance FastAPI backend.

## 1. High-Concurrency Server Configuration
- **Worker Pattern:** Use `uvicorn` with multiple workers in production.
- **Asynchronous Flow:** Every route handling AI or DB operations MUST use `async def`.
- **CORS Strategy:** Strict origin white-listing to prevent unauthorized frontend access.

## 2. Asynchronous Task Management (The Background Layer)
Since Gemini API calls take 5-15s, blocking the main thread is unacceptable.
- **Implementation:** Use FastAPI's `BackgroundTasks` for v1.
- **Workflow:**
    1. User uploads Resume.
    2. Backend saves file and returns `202 Accepted` with a `task_id`.
    3. `BackgroundTasks` triggers `process_resume_ai(resume_id)`.
    4. Frontend polls a GET `/status/{task_id}` endpoint.

## 3. Advanced AI Integration Layer
- **Prompt Engineering Directory:** Store prompts as `.txt` files in `/prompts` to decouple logic from personality.
- **Pydantic Validation:** - Always use `response_mime_type: "application/json"` in Gemini config.
    - Define Pydantic models to validate the AI output before returning it to the frontend.
- **Context Memory:** For Feature 4, implement a sliding window buffer that sends the last `N` messages to Gemini to maintain conversation state.

## 4. Middleware & Security
- **Rate Limiting:** Use `slowapi` to prevent API cost spikes (e.g., 5 resume scans per hour per user).
- **JWT Authentication:** Implement OAuth2 with Password flow. Store hashed passwords using `passlib[bcrypt]`.
- **Error Handling:** Global exception handlers to catch AI timeouts and return custom JSON errors instead of 500 crashes.

## 5. File System Strategy
- **Upload Management:** Store PDFs in a protected `/data/uploads` directory.
- **Naming Convention:** Use UUIDs for filenames (`uuid.uuid4().hex`) to prevent filename collisions and directory traversal attacks.
