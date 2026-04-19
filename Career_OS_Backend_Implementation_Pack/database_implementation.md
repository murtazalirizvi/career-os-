# Career-OS: SQLite Optimization & Data Modeling

This guide ensures SQLite performs like a production-grade relational engine.

## 1. Critical Performance Tuning
- **WAL Mode (Write-Ahead Logging):** Essential for multi-user concurrency.
    - *Setup:* `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;`
- **Connection Pooling:** Even though SQLite is file-based, use SQLAlchemy's `StaticPool` for in-memory testing or standard pooling for file-based to manage connections.

## 2. Relational Schema Design (SQLModel/SQLAlchemy)
### Table: Users
- `id`: UUID (Primary Key)
- `email`: String (Unique, Indexed)
- `hashed_password`: String
- `created_at`: DateTime

### Table: Resumes
- `id`: UUID
- `user_id`: ForeignKey(users.id)
- `file_path`: String
- `raw_text`: Text
- `analysis_json`: JSON (Stores the heatmap data)

### Table: Interviews
- `id`: UUID
- `user_id`: ForeignKey(users.id)
- `persona_type`: String (e.g., "Architect", "Founder")
- `transcript`: JSON (List of dicts: {"role": "ai", "content": "..."})
- `feedback_score`: Float

## 3. Indexing Strategy
- **Index on Foreign Keys:** Always index `user_id` in `resumes` and `interviews` tables for fast dashboard loading.
- **Search Optimization:** Create a FTS5 (Full Text Search) virtual table if implementing a search feature for old interview questions.

## 4. Data Integrity & Transactions
- **Atomic Operations:** Wrap AI result saving in a transaction block.
- **Cleanup Jobs:** Implement a daily cron (Python script) to delete "Guest" resumes older than 24 hours to keep the `.sqlite` file size optimized.
