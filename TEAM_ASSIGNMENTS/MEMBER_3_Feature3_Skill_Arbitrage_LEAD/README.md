# Member 3: Feature 3 (Skill Arbitrage) — TEAM LEAD

**Role:** Project Lead + Most Complex Feature  
**Estimated Time:** 5-6 hours  
**Priority:** 🔴 CRITICAL — This is your competitive differentiator

---

## 🎯 Your Mission

Build the most technically impressive feature: real-time market intelligence + skill gap analysis + personalized learning paths. This is what sets Career OS apart from every other hackathon project.

**As Team Lead, you also:**
- Coordinate with all members
- Make scope decisions if time runs short
- Answer technical questions from judges

---

## 📁 Your Files

### Backend Files (YOUR TERRITORY)
```
Backend/app/api/feature3.py          📝 All Feature 3 endpoints (500+ lines)
Backend/app/analysis/feature3_engine.py   📝 Core logic (5 engines: Market, Gap, Sprint, Future, ROI)
Backend/app/models.py                ⚠️  READ ONLY (Feature3 models)
Backend/app/schemas_feature3.py      ⚠️  READ ONLY (Feature3 schemas)
Backend/.env                         📝 Add API keys here
```

### Frontend Files (YOUR TERRITORY)
```
Frontend/index.html                  📝 Lines 800-1100 (Feature 3 workspace)
Frontend/app.js                      📝 Lines 600-900 (Feature 3 handlers)
Frontend/styles.css                  📝 Feature 3 specific styles
```

### External APIs You'll Use
```
Adzuna API      → Live job market data
Reed API        → Additional job listings
Gemini API      → AI-powered learning paths
```

---

## ✅ Task Checklist

### Phase 1: Backend Setup & API Testing (Hour 1)

#### Check API Keys
**File:** `Backend/.env`

```bash
# Required for live data
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
REED_API_KEY=your_reed_key_here

# Required for AI features
GEMINI_API_KEY=your_gemini_key_here
```

**Get API Keys:**
- Adzuna: https://developer.adzuna.com (free tier: 250 calls/month)
- Reed: https://www.reed.co.uk/developers (free tier: 100 calls/day)
- Gemini: https://aistudio.google.com (free tier: 60 requests/minute)

---

#### Test Backend Endpoints

**Start Backend:**
```bash
cd Backend
python -m uvicorn app.main:app --reload --port 8000
```

**Test Market Snapshot:**
```bash
curl -X POST "http://localhost:8000/api/feature3/market-snapshot" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-lead",
    "target_role": "Software Engineer",
    "region": "US",
    "remote_only": false,
    "salary_currency": "USD"
  }'
```

**Expected Response:**
```json
{
  "snapshot_id": 1,
  "candidate_id": "test-lead",
  "target_role": "Software Engineer",
  "region": "US",
  "jobs_count": 150,
  "clustering": {
    "frontend": 45,
    "backend": 60,
    "data": 25,
    "cloud": 20
  },
  "demand_supply": {
    "demand_score": 8.5,
    "supply_score": 6.2,
    "market_heat": "hot"
  },
  "salary_map": {
    "min": 80000,
    "median": 120000,
    "max": 180000,
    "currency": "USD"
  },
  "remote_market": {
    "remote_percentage": 65,
    "hybrid_percentage": 25,
    "onsite_percentage": 10
  },
  "market_commentary": "Strong demand for backend engineers with Python/FastAPI skills..."
}
```

---

**Test Gap Analysis:**
```bash
curl -X POST "http://localhost:8000/api/feature3/gap-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "market_snapshot_id": 1,
    "candidate_id": "test-lead",
    "current_skills": ["python", "fastapi", "sql", "docker"],
    "resume_text": "Experienced backend engineer with Python and FastAPI..."
  }'
```

**Expected Response:**
```json
{
  "gap_id": 1,
  "match_score": 72.5,
  "gap_to_top10_score": 15.3,
  "current_skills": ["python", "fastapi", "sql", "docker"],
  "target_skills": ["python", "fastapi", "sql", "docker", "kubernetes", "aws", "redis"],
  "missing_skills": ["kubernetes", "aws", "redis"],
  "radar_chart": {
    "labels": ["Backend", "Frontend", "Data", "Cloud", "AI"],
    "your_scores": [85, 40, 60, 55, 30],
    "top10_scores": [95, 70, 80, 90, 60]
  },
  "roadmap": [
    {
      "skill": "kubernetes",
      "priority": "high",
      "estimated_days": 14,
      "resources": ["kubernetes.io/docs", "udemy.com/kubernetes-course"]
    }
  ],
  "ai_learning_path": "Start with Kubernetes fundamentals..."
}
```

---

### Phase 2: Frontend Connection (Hour 2-3)

#### Market Snapshot UI
**File:** `Frontend/index.html` lines 800-900

**Components to Build:**

1. **Input Form**
```html
<div class="feature3-input">
  <input type="text" id="targetRole" placeholder="e.g., Software Engineer" />
  <input type="text" id="region" placeholder="e.g., US, UK, Remote" />
  <label>
    <input type="checkbox" id="remoteOnly" />
    Remote only
  </label>
  <select id="salaryCurrency">
    <option value="USD">USD</option>
    <option value="GBP">GBP</option>
    <option value="PKR">PKR</option>
  </select>
  <button onclick="runMarketSnapshot()">Analyze Market</button>
</div>
```

2. **Market Snapshot Results**
```html
<div class="market-results" id="marketResults" style="display:none;">
  <div class="stat-card">
    <h3>Jobs Found</h3>
    <p class="big-number" id="jobsCount">--</p>
  </div>
  
  <div class="stat-card">
    <h3>Market Heat</h3>
    <p class="market-heat" id="marketHeat">--</p>
  </div>
  
  <div class="stat-card">
    <h3>Median Salary</h3>
    <p class="big-number" id="medianSalary">--</p>
  </div>
  
  <div class="clustering-chart">
    <h3>Skill Clustering</h3>
    <canvas id="clusteringChart"></canvas>
  </div>
  
  <div class="commentary">
    <h3>AI Market Commentary</h3>
    <p id="marketCommentary">--</p>
  </div>
</div>
```

---

#### Gap Analysis UI
**File:** `Frontend/index.html` lines 900-1000

**Components to Build:**

1. **Skills Input**
```html
<div class="gap-input">
  <h3>Your Current Skills</h3>
  <textarea id="currentSkills" placeholder="python, fastapi, sql, docker..."></textarea>
  
  <button onclick="runGapAnalysis()">Analyze Skill Gap</button>
</div>
```

2. **Radar Chart**
```html
<div class="radar-container">
  <h3>Skill Gap Radar</h3>
  <canvas id="skillRadarChart"></canvas>
  <p class="match-score">Match Score: <span id="matchScore">--</span>%</p>
</div>
```

3. **Learning Roadmap**
```html
<div class="roadmap">
  <h3>Personalized Learning Roadmap</h3>
  <div id="roadmapList"></div>
</div>
```

---

#### JavaScript Implementation
**File:** `Frontend/app.js` lines 600-900

```javascript
async function runMarketSnapshot() {
  const targetRole = document.getElementById('targetRole').value;
  const region = document.getElementById('region').value;
  const remoteOnly = document.getElementById('remoteOnly').checked;
  const currency = document.getElementById('salaryCurrency').value;
  
  if (!targetRole || !region) {
    alert('Please enter target role and region');
    return;
  }
  
  // Show loading
  document.getElementById('marketResults').innerHTML = '<p>Loading market data...</p>';
  document.getElementById('marketResults').style.display = 'block';
  
  try {
    const response = await fetch('http://localhost:8000/api/feature3/market-snapshot', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        candidate_id: getCurrentCandidateId(),
        target_role: targetRole,
        region: region,
        remote_only: remoteOnly,
        salary_currency: currency
      })
    });
    
    if (!response.ok) throw new Error('Market snapshot failed');
    
    const data = await response.json();
    displayMarketResults(data);
    
    // Store snapshot_id for gap analysis
    window.currentSnapshotId = data.snapshot_id;
    
  } catch (error) {
    console.error('Market snapshot error:', error);
    alert('Failed to fetch market data. Using cached results.');
  }
}

function displayMarketResults(data) {
  document.getElementById('jobsCount').textContent = data.jobs_count;
  document.getElementById('marketHeat').textContent = data.demand_supply.market_heat.toUpperCase();
  document.getElementById('medianSalary').textContent = 
    `${data.salary_map.currency} ${data.salary_map.median.toLocaleString()}`;
  document.getElementById('marketCommentary').textContent = data.market_commentary;
  
  // Render clustering chart
  renderClusteringChart(data.clustering);
}

function renderClusteringChart(clustering) {
  const ctx = document.getElementById('clusteringChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(clustering),
      datasets: [{
        label: 'Job Postings',
        data: Object.values(clustering),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {beginAtZero: true}
      }
    }
  });
}

async function runGapAnalysis() {
  if (!window.currentSnapshotId) {
    alert('Please run market snapshot first');
    return;
  }
  
  const currentSkills = document.getElementById('currentSkills').value
    .split(',')
    .map(s => s.trim().toLowerCase())
    .filter(s => s);
  
  if (currentSkills.length === 0) {
    alert('Please enter your current skills');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/feature3/gap-analysis', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        market_snapshot_id: window.currentSnapshotId,
        candidate_id: getCurrentCandidateId(),
        current_skills: currentSkills,
        resume_text: ''  // Optional: fetch from Feature 1 if available
      })
    });
    
    if (!response.ok) throw new Error('Gap analysis failed');
    
    const data = await response.json();
    displayGapResults(data);
    
  } catch (error) {
    console.error('Gap analysis error:', error);
    alert('Failed to analyze skill gap');
  }
}

function displayGapResults(data) {
  document.getElementById('matchScore').textContent = Math.round(data.match_score);
  
  // Render radar chart
  renderRadarChart(data.radar_chart);
  
  // Display roadmap
  const roadmapHtml = data.roadmap.map(item => `
    <div class="roadmap-item priority-${item.priority}">
      <h4>${item.skill}</h4>
      <p>Priority: ${item.priority} | Est. ${item.estimated_days} days</p>
      <ul>
        ${item.resources.map(r => `<li><a href="${r}" target="_blank">${r}</a></li>`).join('')}
      </ul>
    </div>
  `).join('');
  document.getElementById('roadmapList').innerHTML = roadmapHtml;
}

function renderRadarChart(radarData) {
  const ctx = document.getElementById('skillRadarChart').getContext('2d');
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: radarData.labels,
      datasets: [
        {
          label: 'Your Skills',
          data: radarData.your_scores,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.2)'
        },
        {
          label: 'Top 10%',
          data: radarData.top10_scores,
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.2)'
        }
      ]
    },
    options: {
      scales: {
        r: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
}

function getCurrentCandidateId() {
  // Get from localStorage or auth token
  return localStorage.getItem('candidateId') || 'test-lead';
}
```

---

### Phase 3: Advanced Features (Hour 4)

#### Skill Sprint Creation
**Endpoint:** `POST /api/feature3/skill-sprint`

**UI Component:**
```html
<div class="sprint-creator">
  <h3>Create Learning Sprint</h3>
  <select id="sprintSkill">
    <!-- Populated from gap analysis missing skills -->
  </select>
  <button onclick="createSprint()">Start 7-Day Sprint</button>
</div>

<div class="sprint-plan" id="sprintPlan" style="display:none;">
  <h3>Your 7-Day Learning Plan</h3>
  <div id="dayPlan"></div>
  <button onclick="takeQuiz()">Take Quiz</button>
</div>
```

---

#### ROI Report
**Endpoint:** `POST /api/feature3/roi-report`

**UI Component:**
```html
<div class="roi-report">
  <h3>ROI Analysis</h3>
  <div class="roi-stat">
    <p>Callback Probability Increase</p>
    <p class="big-number" id="callbackIncrease">--</p>
  </div>
  <div class="roi-stat">
    <p>Lifetime Earnings Delta</p>
    <p class="big-number" id="earningsDelta">--</p>
  </div>
</div>
```

---

### Phase 4: Testing & Edge Cases (Hour 5)

#### Test Scenarios

**Test 1: Software Engineer (US)**
```javascript
{
  target_role: "Software Engineer",
  region: "US",
  current_skills: ["python", "javascript", "sql"]
}
// Expected: High demand, missing cloud skills
```

**Test 2: Data Scientist (UK)**
```javascript
{
  target_role: "Data Scientist",
  region: "UK",
  current_skills: ["python", "pandas", "sql"]
}
// Expected: Medium demand, missing ML skills
```

**Test 3: Product Manager (Remote)**
```javascript
{
  target_role: "Product Manager",
  region: "Remote",
  current_skills: ["agile", "roadmapping"]
}
// Expected: Lower demand, missing technical skills
```

---

#### Handle API Failures

**Fallback Strategy:**
```python
# In Backend/app/analysis/feature3_engine.py

def _fetch_jobs_with_fallback(target_role, region):
    try:
        # Try Adzuna first
        jobs = _fetch_adzuna_jobs(target_role, region)
        if len(jobs) > 0:
            return jobs
    except Exception as e:
        logger.warning(f"Adzuna failed: {e}")
    
    try:
        # Try Reed as backup
        jobs = _fetch_reed_jobs(target_role, region)
        if len(jobs) > 0:
            return jobs
    except Exception as e:
        logger.warning(f"Reed failed: {e}")
    
    # Use mock data as last resort
    return _generate_mock_jobs(target_role, region)
```

---

### Phase 5: Demo Preparation (Hour 6)

#### Your Demo Section (1:00-1:45)

**Script:**
> "Now let's talk about market intelligence. I'll enter 'Senior Backend Engineer' as my target role and 'US' as the region. Watch as we pull live job data from Adzuna and Reed APIs.
>
> Here's what we found: 150 job postings, market heat is 'HOT', median salary is $120,000. The clustering shows 60% are backend-focused, 30% full-stack, 10% data engineering.
>
> Now for the skill gap analysis. I'll enter my current skills: Python, FastAPI, SQL, Docker. Here's the radar chart — it compares me to the top 10% of candidates. See these red areas? Those are my gaps: Kubernetes, AWS, and Redis.
>
> The system generates a personalized 7-day learning sprint for Kubernetes — my highest-priority gap. Day 1: fundamentals, Day 2: pods and deployments, Day 3: services and networking... Here's a quiz to test my knowledge.
>
> And here's the ROI: closing this gap increases my callback probability by 23% and adds $15,000 to my lifetime earnings. This isn't generic career advice — this is data-driven arbitrage."

---

## 🧪 Testing Checklist

- [ ] Market snapshot returns real data (or mock if APIs fail)
- [ ] Clustering chart renders correctly
- [ ] Gap analysis calculates match score
- [ ] Radar chart displays your skills vs top 10%
- [ ] Learning roadmap shows prioritized skills
- [ ] Skill sprint creates 7-day plan
- [ ] ROI report calculates earnings delta
- [ ] All features work without API keys (graceful degradation)

---

## 🚨 Common Issues & Fixes

### Issue 1: API rate limits exceeded
**Fix:** Implement caching (already in code at line 50 of `feature3.py`)

### Issue 2: Radar chart not rendering
**Fix:** Ensure Chart.js is loaded and data format matches

### Issue 3: Gemini learning path empty
**Fix:** Check `GEMINI_API_KEY` in `.env`, fallback to heuristic roadmap

### Issue 4: Slow API responses
**Fix:** Add timeout (20 seconds) and show loading spinner

---

## 📞 Leadership Coordination

### With Member 1 (Feature 1)
- Feature 3 can use `raw_resume_text` from Feature 1 for skill extraction
- Coordinate on `candidate_id` format

### With Member 5 (Dashboard)
- Dashboard needs `Feature3GapSnapshot.match_score` for readiness calculation
- Share test data so they can test integration

### With Member 2 & 4
- Check progress at Hour 3 and Hour 6
- Make scope decisions if anyone is blocked

---

## ⏰ Timeline

| Hour | Task |
|------|------|
| 1 | Backend testing + API setup |
| 2-3 | Frontend connection |
| 4 | Advanced features (sprint, ROI) |
| 5 | Testing + edge cases |
| 6 | Demo prep + team coordination |

---

## 🏆 Success Criteria

- [ ] Market snapshot works with real or mock data
- [ ] Radar chart visualizes skill gaps
- [ ] Learning roadmap generates correctly
- [ ] Demo runs smoothly
- [ ] Can answer judge questions about algorithms
- [ ] Team is coordinated and on track

---

**You've got the hardest feature, but also the most impressive one. Make it shine! 🚀**
