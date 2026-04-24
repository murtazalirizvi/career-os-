# Career OS — Team Task Assignments

**Project:** AI-Powered Career Intelligence Platform  
**Deadline:** Tomorrow 9:30 AM  
**Team:** 5 members  
**Status:** MVP ready, needs integration and polish

---

## 📂 Folder Structure

```
TEAM_ASSIGNMENTS/
│
├── README.md (this file — overview)
├── QUICK_START.md (read this first!)
├── MASTER_COORDINATION.md (team coordination plan)
│
├── MEMBER_1_Feature1_Dashboard_Integration/
│   └── README.md (Feature 1: Resume Analyzer)
│
├── MEMBER_5_Dashboard_Analytics_Demo/
│   └── README.md (Dashboard + Demo Preparation)
│
├── MEMBER_3_Feature3_Skill_Arbitrage_LEAD/
│   └── README.md (Feature 3: Market Intelligence — TEAM LEAD)
│
├── MEMBER_2_Feature2_Feature4_Interviews/
│   └── README.md (Feature 2: Interview Autopsy + Feature 4: Mock Interview)
│
└── MEMBER_4_Feature5_JobTracker/
    └── README.md (Feature 5: Narrative Architect + Job Tracker)
```

---

## 👥 Team Assignments

### Member 1: Feature 1 + Dashboard Integration
**Priority:** 🔴 CRITICAL PATH  
**Time:** 4-5 hours  
**Sitting with:** Member 5

**Tasks:**
- Resume upload and analysis flow
- Score display (visual, ATS, semantic, benchmark)
- Hot zones visualization
- Version history and comparison
- Integration with dashboard

**Why this matters:** Feature 1 is the entry point — if this doesn't work, nothing else matters.

---

### Member 5: Dashboard + Analytics + Demo
**Priority:** 🔴 CRITICAL PATH  
**Time:** 5-6 hours  
**Sitting with:** Member 1

**Tasks:**
- Build unified dashboard (readiness score, job pipeline)
- Create analytics endpoints and charts
- Write 3-minute demo script
- Record backup demo video
- Coordinate demo delivery

**Why this matters:** The dashboard is the integration point for all features. You own the first impression.

---

### Member 3 (You): Feature 3 — Skill Arbitrage (TEAM LEAD)
**Priority:** 🔴 CRITICAL — DIFFERENTIATOR  
**Time:** 5-6 hours  
**Working:** Solo

**Tasks:**
- Market snapshot (live job data from Adzuna/Reed APIs)
- Skill gap analysis with radar chart
- Personalized learning roadmap
- ROI calculation (callback probability, earnings delta)
- Team coordination and scope decisions

**Why this matters:** This is your competitive edge. No other team will have real-time market intelligence.

---

### Member 2: Feature 2 + Feature 4 (Interviews)
**Priority:** 🟡 HIGH  
**Time:** 5-6 hours  
**Working:** Solo

**Tasks:**
- **Feature 2:** Post-interview autopsy with transcript analysis
- **Feature 4:** AI mock interviewer with 4 persona types
- Both features showcase deep AI integration (Gemini)

**Why this matters:** These features demonstrate meaningful AI usage, not just cosmetic integration.

---

### Member 4: Feature 5 + Job Tracker
**Priority:** 🟢 MEDIUM  
**Time:** 4-5 hours  
**Working:** Solo

**Tasks:**
- **Feature 5:** Test and polish GitHub → narrative generation (80% done)
- **Job Tracker:** Build Kanban pipeline with drag-and-drop

**Why this matters:** Feature 5 is mostly working. Job tracker ties everything together.

---

## 🚀 Getting Started

### Step 1: Read QUICK_START.md
This has setup instructions and file ownership rules.

### Step 2: Go to Your Member Folder
Each folder has a complete README with:
- Task breakdown by hour
- Code examples
- Testing checklist
- Demo script
- Common issues and fixes

### Step 3: Start Building
- Backend is already running
- Frontend is already running
- API endpoints exist
- You just need to connect and polish

---

## 🔗 Critical Integration Points

### Member 1 ↔ Member 5
- Feature 1 analysis feeds dashboard readiness score
- **Test together after Hour 4**

### Member 3 ↔ Member 5
- Feature 3 gap analysis feeds dashboard
- **Share test candidate_id for integration**

### Member 1 → Member 3
- Feature 1 resume text used by Feature 3 for skill extraction
- **Ensure raw_resume_text is populated**

---

## ⏰ Coordination Schedule

| Time | Event | All Members |
|------|-------|-------------|
| **6:00 PM Today** | Kickoff Standup | ✅ Confirm tasks, share test data |
| **12:00 AM Midnight** | Integration Checkpoint | ✅ Demo progress, identify blockers |
| **6:00 AM Tomorrow** | Final Rehearsal | ✅ Run demo 3 times, record backup |
| **9:30 AM Tomorrow** | Submission Deadline | ✅ Submit and celebrate! |

---

## 🎬 Demo Flow (3 Minutes)

| Time | Speaker | Feature |
|------|---------|---------|
| 0:00-0:30 | Member 5 | Problem introduction |
| 0:30-1:00 | Member 1 | Feature 1 (Resume Analyzer) |
| 1:00-1:45 | Member 3 | Feature 3 (Skill Arbitrage) |
| 1:45-2:15 | Member 2 | Feature 4 (Mock Interview) |
| 2:15-2:45 | Member 5 | Dashboard integration |
| 2:45-3:00 | Member 5 | Closing |

---

## 🚨 If Time Runs Out

### Must Have (Keep)
- Feature 1: Resume upload + score
- Feature 3: Market snapshot + radar chart
- Dashboard: Readiness score
- Job Tracker: Basic CRUD

### Nice to Have (Cut)
- Feature 2: AssemblyAI webhook
- Feature 4: Video recording
- Feature 5: Export formats
- Job Tracker: Drag-and-drop

---

## 📞 Communication

**Team Channel:** [Discord/Slack/WhatsApp]  
**Video Calls:** [Zoom/Google Meet]  
**Shared Doc:** [Google Docs/Notion]

**Escalation:** If blocked, ping Team Lead (Member 3) immediately.

---

## 🏆 Success Criteria

### Minimum Viable Demo
- [ ] Feature 1 works (upload resume, get score)
- [ ] Feature 3 works (market snapshot, radar chart)
- [ ] Dashboard works (readiness score displays)
- [ ] Demo runs without errors
- [ ] Can answer judge questions

### Stretch Goals
- [ ] All 5 features working
- [ ] Drag-and-drop job tracker
- [ ] AI insights in all features
- [ ] Mobile responsive
- [ ] Backup demo video

---

## 💪 You've Got This!

**Remember:**
- 80% of the platform is already built
- You just need to connect the pieces
- The judges care about the story, not perfect code
- Feature 3 is your differentiator
- Work smart, not just hard

---

## 📚 Quick Links

- **QUICK_START.md** — Setup and file ownership
- **MASTER_COORDINATION.md** — Detailed coordination plan
- **Your Member Folder** — Your specific tasks
- **Backend API Docs** — http://localhost:8000/docs
- **Frontend** — http://localhost:5500

---

**Now go build something amazing! 🚀**
