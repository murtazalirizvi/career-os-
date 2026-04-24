# Member 5: Dashboard + Analytics + Demo Preparation

**Sitting with:** Member 1 (Feature 1)  
**Estimated Time:** 5-6 hours  
**Priority:** 🔴 CRITICAL — You own the demo delivery

---

## 🎯 Your Mission

Build the unified dashboard that integrates all features, create the analytics/metrics views, and prepare the 3-minute demo pitch. You're the integration point for the entire platform.

---

## 📁 Your Files

### Backend Files (YOUR TERRITORY)
```
Backend/app/main.py                  📝 Lines 100-180 (/api/me/dashboard endpoint)
Backend/app/api/metrics.py           📝 Analytics endpoints
Backend/app/api/core.py              📝 Core utility endpoints
Backend/app/models.py                ⚠️  READ ONLY (all models)
```

### Frontend Files (YOUR TERRITORY)
```
Frontend/index.html                  📝 Lines 150-350 (Dashboard section)
Frontend/app.js                      📝 Lines 50-200 (Dashboard handlers)
Frontend/styles.css                  📝 Dashboard-specific styles
```

### Demo Files (YOU CREATE)
```
DEMO_SCRIPT.md                       📝 3-minute pitch script
DEMO_BACKUP_VIDEO.mp4                📹 Recorded backup demo
```

---

## ✅ Task Checklist

### Phase 1: Dashboard Backend (Hour 1-2)

#### Fix `/api/me/dashboard` Endpoint
**File:** `Backend/app/main.py` lines 100-180

**Current Issues:**
- Endpoint exists but may not be fully tested
- Needs to aggregate data from Features 1, 2, 3

**Your Tasks:**
- [ ] Test the endpoint: `GET /api/me/dashboard` with Authorization header
- [ ] Verify it returns: user info, latest Feature 1 analysis, job pipeline counts, readiness score
- [ ] Fix any bugs in the readiness score calculation
- [ ] Add error handling for missing data

**Test Command:**
```bash
# First, create a test user and get a token
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Then test dashboard
curl -X GET "http://localhost:8000/api/me/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "user": {
    "candidate_id": "test-001",
    "email": "test@example.com",
    "full_name": "Test User"
  },
  "latest_analysis": {
    "analysis_id": 1,
    "overall_score": 87.5,
    "created_at": "2026-04-24T10:30:00Z"
  },
  "job_pipeline": {
    "applied": 5,
    "interviewing": 2,
    "offer": 1,
    "rejected": 3
  },
  "total_jobs": 11,
  "readiness_score": 85.3,
  "generated_at": "2026-04-24T12:00:00Z"
}
```

---

#### Create Analytics Endpoints
**File:** `Backend/app/api/metrics.py`

- [ ] Implement `/api/metrics/activity` — user activity over time
- [ ] Implement `/api/metrics/feature-usage` — which features are used most
- [ ] Implement `/api/metrics/success-rate` — application → interview → offer conversion

**Code Template:**
```python
@router.get("/api/metrics/activity")
def get_activity_metrics(
    candidate_id: str,
    days: int = 30,
    session: Session = Depends(get_session)
):
    # Query AnalyticsEvent table
    events = session.exec(
        select(AnalyticsEvent)
        .where(AnalyticsEvent.user_id == candidate_id)
        .where(AnalyticsEvent.occurred_at_utc >= datetime.now() - timedelta(days=days))
    ).all()
    
    # Group by date
    activity_by_date = {}
    for event in events:
        date_key = event.occurred_at_utc.date().isoformat()
        activity_by_date[date_key] = activity_by_date.get(date_key, 0) + 1
    
    return {"activity": activity_by_date}
```

---

### Phase 2: Dashboard Frontend (Hour 3-4)

#### Build Dashboard UI
**File:** `Frontend/index.html` lines 150-350

**Components to Build:**

1. **Readiness Score Card** (big number, color-coded)
```html
<div class="readiness-card">
  <div class="score-circle" id="readinessScore">--</div>
  <p class="score-label">Career Readiness Score</p>
  <p class="score-hint">Based on resume, skills, and interview performance</p>
</div>
```

2. **Latest Resume Analysis Card**
```html
<div class="analysis-card">
  <h3>Latest Resume Analysis</h3>
  <div class="score-breakdown">
    <div class="score-item">
      <span>Visual</span>
      <span id="visualScore">--</span>
    </div>
    <div class="score-item">
      <span>ATS</span>
      <span id="atsScore">--</span>
    </div>
    <div class="score-item">
      <span>Semantic</span>
      <span id="semanticScore">--</span>
    </div>
    <div class="score-item">
      <span>Benchmark</span>
      <span id="benchmarkScore">--</span>
    </div>
  </div>
</div>
```

3. **Job Pipeline Card**
```html
<div class="pipeline-card">
  <h3>Job Pipeline</h3>
  <div class="pipeline-stats">
    <div class="stat">
      <span class="stat-number" id="appliedCount">0</span>
      <span class="stat-label">Applied</span>
    </div>
    <div class="stat">
      <span class="stat-number" id="interviewingCount">0</span>
      <span class="stat-label">Interviewing</span>
    </div>
    <div class="stat">
      <span class="stat-number" id="offerCount">0</span>
      <span class="stat-label">Offers</span>
    </div>
  </div>
</div>
```

4. **Activity Chart** (use Chart.js)
```html
<div class="chart-card">
  <h3>Activity (Last 30 Days)</h3>
  <canvas id="activityChart"></canvas>
</div>
```

---

#### Dashboard JavaScript
**File:** `Frontend/app.js` lines 50-200

```javascript
async function loadDashboard() {
  const token = localStorage.getItem('authToken');
  if (!token) {
    window.location.href = '/login.html';
    return;
  }
  
  try {
    // Show loading state
    document.getElementById('readinessScore').textContent = '...';
    
    // Fetch dashboard data
    const response = await fetch('http://localhost:8000/api/me/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) throw new Error('Failed to load dashboard');
    
    const data = await response.json();
    
    // Update readiness score
    const readinessScore = Math.round(data.readiness_score);
    document.getElementById('readinessScore').textContent = readinessScore;
    document.getElementById('readinessScore').className = 
      readinessScore >= 80 ? 'score-high' : 
      readinessScore >= 60 ? 'score-medium' : 'score-low';
    
    // Update resume analysis
    if (data.latest_analysis) {
      document.getElementById('visualScore').textContent = 
        data.latest_analysis.overall_score || '--';
    }
    
    // Update job pipeline
    document.getElementById('appliedCount').textContent = 
      data.job_pipeline.applied || 0;
    document.getElementById('interviewingCount').textContent = 
      data.job_pipeline.interviewing || 0;
    document.getElementById('offerCount').textContent = 
      data.job_pipeline.offer || 0;
    
    // Load activity chart
    loadActivityChart();
    
  } catch (error) {
    console.error('Dashboard error:', error);
    showError('Failed to load dashboard. Please try again.');
  }
}

async function loadActivityChart() {
  const response = await fetch('http://localhost:8000/api/metrics/activity');
  const data = await response.json();
  
  const ctx = document.getElementById('activityChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: Object.keys(data.activity),
      datasets: [{
        label: 'Activity',
        data: Object.values(data.activity),
        borderColor: 'rgb(59, 130, 246)',
        tension: 0.1
      }]
    }
  });
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadDashboard);
```

---

### Phase 3: Integration Testing (Hour 5) — COORDINATE WITH MEMBER 1

- [ ] Member 1 uploads a resume → check if dashboard updates
- [ ] Verify readiness score calculation is correct
- [ ] Test with missing data (no Feature 1 analysis yet)
- [ ] Test with complete data (all features have data)

**Integration Test Flow:**
1. Member 1 uploads resume (Feature 1)
2. You refresh dashboard → latest analysis should appear
3. Readiness score should update
4. Job pipeline should show counts

---

### Phase 4: Demo Preparation (Hour 6)

#### Write Demo Script
**File:** `TEAM_ASSIGNMENTS/MEMBER_5_Dashboard_Analytics_Demo/DEMO_SCRIPT.md`

**Structure:**
```markdown
# Career OS Demo Script (3 minutes)

## [0:00-0:30] Problem Introduction
**Speaker:** Member 5 (You)
**Script:**
"Job hunting in 2025 is broken. Talented people lose opportunities not because of what they lack, but because they lack intelligence at the right moment. Career OS changes that."

## [0:30-1:00] Feature 1 Demo
**Speaker:** Member 1
**Script:**
"Let me upload my resume and a job description. Our AI analyzes it across four dimensions..."

## [1:00-1:45] Feature 3 Demo
**Speaker:** Team Lead (Member 3)
**Script:**
"Now let's see how you stack up in the market..."

## [1:45-2:15] Feature 4 Demo
**Speaker:** Member 2
**Script:**
"Practice against our AI interviewer personas..."

## [2:15-2:45] Dashboard Integration
**Speaker:** Member 5 (You)
**Script:**
"Everything feeds into your unified readiness score. Resume quality, skill gaps, interview performance — one number that tells you if you're ready to apply."

## [2:45-3:00] Closing
**Speaker:** Member 5 (You)
**Script:**
"This is how we turn guessing into intelligence. Five features, one platform, built in 18 hours."
```

---

#### Record Backup Demo Video

**Why:** In case live demo fails (network issues, bugs)

**Tools:**
- OBS Studio (free screen recorder)
- Loom (web-based)
- Windows Game Bar (Win+G)

**Recording Checklist:**
- [ ] Record full 3-minute walkthrough
- [ ] Show all 5 features working
- [ ] Include voiceover explaining each feature
- [ ] Export as MP4 (max 100MB)
- [ ] Upload to Google Drive or YouTube (unlisted)

---

### Phase 5: Polish & Final Testing (Hour 7-8)

- [ ] Add loading spinners to all async operations
- [ ] Add error messages for failed API calls
- [ ] Test on different screen sizes (desktop, tablet)
- [ ] Fix any visual bugs (alignment, colors, spacing)
- [ ] Run through entire user journey 3 times

---

## 🧪 Testing Checklist

### Test 1: Fresh User
- Create new account
- Dashboard should show empty state
- Upload resume → dashboard updates

### Test 2: Active User
- Use existing account with data
- Dashboard shows all metrics
- Charts render correctly

### Test 3: Error Handling
- Disconnect backend → dashboard shows error message
- Invalid token → redirects to login

---

## 🚨 Common Issues & Fixes

### Issue 1: Dashboard shows "undefined" scores
**Fix:** Check if `/api/me/dashboard` returns null for missing data, handle gracefully

### Issue 2: Charts not rendering
**Fix:** Ensure Chart.js is loaded: `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`

### Issue 3: Readiness score calculation wrong
**Fix:** Check `Backend/app/main.py` line 150 — verify averaging logic

### Issue 4: CORS errors
**Fix:** Backend already has CORS enabled, check if frontend URL is correct

---

## 📞 Coordination Points

### With Member 1 (Feature 1)
- **Test together after Hour 4** — upload resume, check dashboard
- **Agree on `candidate_id` format** for testing
- **Share test accounts** so both can test integration

### With Team Lead (Member 3)
- **Get Feature 3 demo talking points** for the script
- **Coordinate demo timing** — who speaks when

### With Member 2 (Feature 2/4)
- **Get Feature 2 and 4 demo snippets** for the script

### With Member 4 (Feature 5)
- **Get Feature 5 demo snippet** for the script

---

## 🎬 Your Demo Sections

### Opening (0:00-0:30)
> "Job hunting is a black box. You submit resumes without knowing how they're read. You walk out of interviews without understanding why you failed. You apply to roles without knowing if your skills are competitive. Career OS tears open that black box with five AI-powered intelligence engines."

### Dashboard Walkthrough (2:15-2:45)
> "Everything feeds into this unified dashboard. Your readiness score — 85 out of 100 — is calculated from your resume quality, skill gaps, and interview performance. Here's your job pipeline: 5 applications, 2 interviews, 1 offer. The activity chart shows you've been actively improving over the past month. This isn't just tracking — this is intelligence."

### Closing (2:45-3:00)
> "This is Career OS. Five features, one platform, built in 18 hours. We turn guessing into intelligence. Thank you."

---

## ⏰ Timeline

| Hour | Task |
|------|------|
| 1-2 | Dashboard backend endpoints |
| 3-4 | Dashboard frontend UI |
| 5 | Integration testing with Member 1 |
| 6 | Demo script + backup video |
| 7-8 | Polish + final testing |

---

## 🏆 Success Criteria

- [ ] Dashboard loads and displays real data
- [ ] Readiness score calculates correctly
- [ ] Charts render properly
- [ ] Integration with Feature 1 works
- [ ] Demo script is written and rehearsed
- [ ] Backup video is recorded
- [ ] Team knows who speaks when in demo

---

**You're the glue that holds this together. Let's make it shine! 🚀**
