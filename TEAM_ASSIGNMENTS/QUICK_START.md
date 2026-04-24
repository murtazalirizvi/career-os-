# Quick Start Guide — Career OS Team

**Read this first, then go to your member folder!**

---

## 🚀 Setup (Everyone Does This First)

### 1. Start Backend
```bash
cd Backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys (optional, features degrade gracefully)
python -m uvicorn app.main:app --reload --port 8000
```

**Test:** Open http://localhost:8000/docs

---

### 2. Start Frontend
```bash
cd Frontend
python serve.py
```

**Test:** Open http://localhost:5500

---

### 3. Find Your Task
Go to your assigned folder:
- **Member 1:** `MEMBER_1_Feature1_Dashboard_Integration/README.md`
- **Member 5:** `MEMBER_5_Dashboard_Analytics_Demo/README.md`
- **Member 3 (Lead):** `MEMBER_3_Feature3_Skill_Arbitrage_LEAD/README.md`
- **Member 2:** `MEMBER_2_Feature2_Feature4_Interviews/README.md`
- **Member 4:** `MEMBER_4_Feature5_JobTracker/README.md`

---

## 📁 File Ownership (Avoid Conflicts!)

### Backend Files
| File | Owner | Others |
|------|-------|--------|
| `Backend/app/api/feature1.py` | Member 1 | Read only |
| `Backend/app/api/feature2.py` | Member 2 | Read only |
| `Backend/app/api/feature3.py` | Member 3 | Read only |
| `Backend/app/api/feature4.py` | Member 2 | Read only |
| `Backend/app/api/feature5.py` | Member 4 | Read only |
| `Backend/app/api/jobs.py` | Member 4 | Read only |
| `Backend/app/api/metrics.py` | Member 5 | Read only |
| `Backend/app/main.py` | Member 5 | Read only (dashboard endpoint) |

### Frontend Files
| File | Lines | Owner |
|------|-------|-------|
| `Frontend/index.html` | 150-350 | Member 5 (Dashboard) |
| `Frontend/index.html` | 450-650 | Member 1 (Feature 1) |
| `Frontend/index.html` | 650-800 | Member 2 (Feature 2) |
| `Frontend/index.html` | 800-1100 | Member 3 (Feature 3) |
| `Frontend/index.html` | 1100-1300 | Member 2 (Feature 4) |
| `Frontend/index.html` | 1300-1500 | Member 4 (Feature 5) |
| `Frontend/index.html` | 350-450 | Member 4 (Job Tracker) |

| File | Lines | Owner |
|------|-------|-------|
| `Frontend/app.js` | 50-200 | Member 5 (Dashboard) |
| `Frontend/app.js` | 200-450 | Member 1 (Feature 1) |
| `Frontend/app.js` | 450-600 | Member 2 (Feature 2) |
| `Frontend/app.js` | 600-900 | Member 3 (Feature 3) |
| `Frontend/app.js` | 900-1100 | Member 2 (Feature 4) |
| `Frontend/app.js` | 1100-1300 | Member 4 (Feature 5) |
| `Frontend/app.js` | 1300-1500 | Member 4 (Job Tracker) |

---

## 🔗 API Endpoints Quick Reference

### Feature 1 (Member 1)
```
POST   /api/feature1/analyze
GET    /api/feature1/candidate/{id}/versions
GET    /api/feature1/candidate/{id}/latest
POST   /api/feature1/analyze-jd
```

### Feature 2 (Member 2)
```
POST   /api/feature2/interviews
GET    /api/feature2/interviews/{id}
POST   /api/feature2/interviews/{id}/regenerate-ai
```

### Feature 3 (Member 3 - Lead)
```
POST   /api/feature3/market-snapshot
POST   /api/feature3/gap-analysis
POST   /api/feature3/skill-sprint
POST   /api/feature3/roi-report
```

### Feature 4 (Member 2)
```
POST   /api/feature4/sessions
POST   /api/feature4/sessions/{id}/turns
POST   /api/feature4/sessions/{id}/finalize
```

### Feature 5 (Member 4)
```
POST   /api/feature5/sessions
GET    /api/feature5/sessions/{id}/linkedin-post
GET    /api/feature5/sessions/{id}/portfolio-site
```

### Job Tracker (Member 4)
```
GET    /api/jobs
POST   /api/jobs
PATCH  /api/jobs/{id}
DELETE /api/jobs/{id}
GET    /api/jobs/stats
```

### Dashboard (Member 5)
```
GET    /api/me/dashboard
GET    /api/metrics/activity
GET    /api/metrics/feature-usage
```

---

## 🧪 Test Data

### Test Candidate IDs
Use these for consistency:
- Member 1: `test-001`
- Member 2: `test-002`
- Member 3: `test-003`
- Member 4: `test-004`
- Member 5: `test-005`

### Test Resume
Located at: `Backend/data/uploads/candidate-001-10705845b8b21e61.pdf`

### Test Job Description
```
We're looking for a Senior Backend Engineer with 5+ years of experience.
Required skills: Python, FastAPI, PostgreSQL, Docker, Kubernetes, AWS.
Nice to have: Redis, Kafka, GraphQL.
```

---

## ⏰ Checkpoints

| Time | What | Who |
|------|------|-----|
| **6:00 PM Today** | Kickoff standup | All members |
| **12:00 AM Midnight** | Integration checkpoint | All members |
| **6:00 AM Tomorrow** | Final rehearsal | All members |
| **9:30 AM Tomorrow** | Submission deadline | All members |

---

## 🚨 If You're Stuck

1. **Check your README** — common issues section
2. **Ask in team channel** — someone might know
3. **Ask Team Lead (Member 3)** — they'll help or reassign
4. **Check API docs** — http://localhost:8000/docs

---

## 🎬 Demo Order

1. **Member 5** — Problem intro (30 sec)
2. **Member 1** — Feature 1 demo (30 sec)
3. **Member 3** — Feature 3 demo (45 sec)
4. **Member 2** — Feature 4 demo (45 sec)
5. **Member 5** — Dashboard + closing (30 sec)

**Total:** 3 minutes

---

## 📦 What's Already Done

✅ Backend API structure (all endpoints exist)  
✅ Database models (SQLModel)  
✅ Analysis engines (5 features)  
✅ Gemini integration (AI layer)  
✅ Frontend HTML structure  
✅ Basic styling (Tailwind CSS)  

**What You Need to Do:**
- Connect frontend to backend (API calls)
- Display results in UI
- Add loading states and error handling
- Test and polish
- Prepare demo

---

## 💡 Pro Tips

1. **Test early, test often** — don't wait until the end
2. **Commit frequently** — every 30-60 minutes
3. **Communicate blockers immediately** — don't suffer in silence
4. **Focus on your feature first** — integration comes later
5. **Keep it simple** — working > perfect

---

## 🏆 Success = Working Demo

**Judges care about:**
- Does it work? (40 points)
- Is the problem real? (20 points)
- Is AI integrated meaningfully? (10 points)
- Is the code quality good? (10 points)
- Is the demo clear? (20 points)

**They don't care about:**
- Perfect UI
- Every edge case handled
- Production-ready code
- 100% test coverage

---

**Now go to your member folder and start building! 🚀**
