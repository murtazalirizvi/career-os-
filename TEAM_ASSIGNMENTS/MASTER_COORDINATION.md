# Career OS — Team Coordination Master Plan

**Deadline:** Tomorrow 9:30 AM  
**Team Size:** 5 members  
**Current Status:** MVP platform ready, needs integration and polish

---

## 👥 Team Structure

| Member | Role | Priority | Sitting With |
|--------|------|----------|--------------|
| **Member 1** | Feature 1 + Dashboard Integration | 🔴 CRITICAL | Member 5 |
| **Member 5** | Dashboard + Analytics + Demo | 🔴 CRITICAL | Member 1 |
| **You (Lead)** | Feature 3 (Skill Arbitrage) | 🔴 CRITICAL | Solo |
| **Member 2** | Feature 2 + Feature 4 (Interviews) | 🟡 HIGH | Solo |
| **Member 4** | Feature 5 + Job Tracker | 🟢 MEDIUM | Solo |

---

## 📂 Folder Structure

Each member has their own folder with:
- `README.md` — Complete task breakdown
- File ownership list
- Testing checklist
- Demo script
- Common issues & fixes

```
TEAM_ASSIGNMENTS/
├── MEMBER_1_Feature1_Dashboard_Integration/
│   └── README.md
├── MEMBER_5_Dashboard_Analytics_Demo/
│   └── README.md
├── MEMBER_3_Feature3_Skill_Arbitrage_LEAD/
│   └── README.md
├── MEMBER_2_Feature2_Feature4_Interviews/
│   └── README.md
├── MEMBER_4_Feature5_JobTracker/
│   └── README.md
└── MASTER_COORDINATION.md (this file)
```

---

## 🔗 Integration Points

### Critical Dependencies

**Member 1 → Member 5**
- Feature 1 analysis data feeds dashboard readiness score
- Endpoint: `/api/feature1/candidate/{id}/latest`
- **Coordination:** Test together after Hour 4

**Member 3 (You) → Member 5**
- Feature 3 gap analysis `match_score` feeds dashboard
- Endpoint: `/api/feature3/gap-analysis`
- **Coordination:** Share test `candidate_id` for integration testing

**Member 1 → Member 3 (You)**
- Feature 1 `raw_resume_text` used by Feature 3 for skill extraction
- Model: `Feature1Analysis.raw_resume_text`
- **Coordination:** Ensure resume text is populated

---

## ⏰ Coordination Schedule

### 6:00 PM Today — Kickoff Standup
**Location:** All members (video call or in-person)

**Agenda:**
- [ ] Confirm task assignments
- [ ] Share test `candidate_id` format (e.g., `test-001`, `test-002`)
- [ ] Agree on Git workflow (branch naming, commit frequency)
- [ ] Set up communication channel (Discord/Slack/WhatsApp)

**Deliverables:**
- Everyone has read their README
- Backend is running locally for everyone
- Frontend is running locally for everyone

---

### 12:00 AM Midnight — Integration Checkpoint
**Location:** All members

**Agenda:**
- [ ] Member 1 + Member 5: Demo Feature 1 → Dashboard integration
- [ ] Member 3 (You): Demo Feature 3 market snapshot + radar chart
- [ ] Member 2: Demo Feature 2 autopsy OR Feature 4 mock interview (at least one)
- [ ] Member 4: Demo Feature 5 narrative generation OR job tracker (at least one)
- [ ] Identify blockers and reassign if needed

**Deliverables:**
- At least 3 features working end-to-end
- Dashboard displays real data
- Demo script outline ready

---

### 6:00 AM Tomorrow — Final Rehearsal
**Location:** All members

**Agenda:**
- [ ] Full demo run-through (3 minutes)
- [ ] Fix critical bugs only (no new features)
- [ ] Record backup demo video
- [ ] Prepare for judge questions

**Deliverables:**
- Demo script finalized
- Backup video recorded
- Everyone knows their speaking part

---

## 🚨 Escalation Protocol

### If Someone is Blocked

**Step 1:** Post in team channel immediately (don't wait)

**Step 2:** Team Lead (Member 3) decides:
- Can another member help? (pair programming)
- Should we cut scope? (skip that sub-feature)
- Should we reassign? (swap tasks)

**Step 3:** Update the team at next checkpoint

---

### Scope Cut Priority (If Time Runs Out)

**Keep (Must Have):**
- Feature 1: Resume upload + score display
- Feature 3: Market snapshot + radar chart
- Dashboard: Readiness score + job pipeline
- Job Tracker: Basic CRUD (no drag-and-drop)

**Cut (Nice to Have):**
- Feature 2: AssemblyAI webhook (use manual transcript)
- Feature 4: Video recording (text-only mock interview)
- Feature 5: Export formats (just show narrative on screen)
- Job Tracker: Drag-and-drop (use status dropdown)

---

## 🎬 Demo Flow (3 Minutes)

### [0:00-0:30] Problem Introduction
**Speaker:** Member 5  
**Script:** "Job hunting is a black box. Career OS changes that."

### [0:30-1:00] Feature 1 Demo
**Speaker:** Member 1  
**Script:** "Upload resume, get AI-powered analysis across 4 dimensions."

### [1:00-1:45] Feature 3 Demo
**Speaker:** Member 3 (You)  
**Script:** "Real-time market intelligence + skill gap radar + learning roadmap."

### [1:45-2:15] Feature 4 Demo
**Speaker:** Member 2  
**Script:** "AI mock interviewer with persona-based questioning."

### [2:15-2:45] Dashboard Integration
**Speaker:** Member 5  
**Script:** "Everything feeds into unified readiness score."

### [2:45-3:00] Closing
**Speaker:** Member 5  
**Script:** "Five features, one platform, built in 18 hours."

---

## 📋 Git Workflow

### Branch Naming
```
member1/feature1-upload-flow
member5/dashboard-integration
member3/feature3-radar-chart
member2/feature2-autopsy
member4/job-tracker-kanban
```

### Commit Frequency
- Commit every 30-60 minutes
- Use descriptive messages: "Add resume upload validation" not "fix bug"

### Merge Strategy
- **Before midnight:** Everyone merges to `main` (integration checkpoint)
- **After midnight:** Only critical bug fixes merge to `main`

### Avoiding Conflicts
- Each member owns specific line ranges in `Frontend/app.js` and `Frontend/index.html`
- If you need to edit someone else's file, coordinate in team channel first

---

## 🧪 Testing Strategy

### Individual Testing (Each Member)
- Test your feature with 3 different inputs
- Test error cases (invalid input, API failure)
- Test on Chrome and Firefox

### Integration Testing (Pairs)
- Member 1 + Member 5: Feature 1 → Dashboard
- Member 3 + Member 5: Feature 3 → Dashboard
- All members: Full user journey (signup → upload resume → check dashboard)

### Demo Testing (All Members)
- Run demo 3 times before submission
- Time it (must be under 3 minutes)
- Prepare for judge questions

---

## 🏆 Success Metrics

### Minimum Viable Demo (Must Have)
- [ ] Feature 1 works (upload resume, get score)
- [ ] Feature 3 works (market snapshot, radar chart)
- [ ] Dashboard works (readiness score displays)
- [ ] Demo runs without errors
- [ ] Can answer judge questions

### Stretch Goals (Nice to Have)
- [ ] All 5 features working
- [ ] Drag-and-drop job tracker
- [ ] AI insights from Gemini in all features
- [ ] Mobile responsive
- [ ] Backup demo video recorded

---

## 📞 Communication Channels

### Team Channel (Discord/Slack/WhatsApp)
**Use for:**
- Quick questions
- Blocker alerts
- Integration coordination
- Memes to keep morale up 😄

### Video Calls (Zoom/Google Meet)
**Use for:**
- Scheduled standups (6 PM, 12 AM, 6 AM)
- Pair programming sessions
- Demo rehearsals

### Shared Doc (Google Docs/Notion)
**Use for:**
- Real-time task status updates
- Test credentials (candidate_id, auth tokens)
- Demo script edits

---

## 🎯 Judge Questions to Prepare For

### Technical Questions
- "How does the skill gap radar chart work?" → Member 3 answers
- "How do you handle API failures?" → Any member (graceful degradation)
- "What AI model are you using?" → Gemini 2.0 Flash
- "How do you ensure data privacy?" → SQLite local storage, no external data sharing

### Product Questions
- "Who is your target user?" → Job seekers who want data-driven insights
- "What's your competitive advantage?" → Real-time market intelligence (Feature 3)
- "How would you monetize this?" → Freemium model, premium features for power users

### Execution Questions
- "What was the hardest part?" → Integrating 5 features into unified dashboard
- "What would you do differently?" → Start with dashboard first, then build features
- "What's next?" → Mobile app, LinkedIn integration, recruiter dashboard

---

## 🚀 Final Checklist (Before Submission)

### Code Quality
- [ ] No console errors in browser
- [ ] No Python exceptions in backend logs
- [ ] All API endpoints return proper status codes
- [ ] Loading states for all async operations

### User Experience
- [ ] Error messages are user-friendly
- [ ] Success messages confirm actions
- [ ] Forms validate input before submission
- [ ] UI is consistent across features

### Demo Readiness
- [ ] Demo script printed/on screen
- [ ] Test data pre-loaded (resumes, jobs, etc.)
- [ ] Backup demo video uploaded
- [ ] All members know their speaking parts

### Documentation
- [ ] README.md is updated
- [ ] API endpoints documented
- [ ] Setup instructions tested
- [ ] Environment variables documented

---

## 💪 Team Motivation

**Remember:**
- You've already built 80% of the platform
- You just need to connect the pieces and polish
- The judges care more about the story than perfect code
- Feature 3 (market intelligence) is your differentiator
- You've got this! 🚀

---

## 📧 Emergency Contacts

**Team Lead (Member 3):** [Your contact]  
**Member 1:** [Contact]  
**Member 2:** [Contact]  
**Member 4:** [Contact]  
**Member 5:** [Contact]

---

**Let's build something amazing! 🔥**
