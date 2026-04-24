# Member 4: Feature 5 (Narrative Architect) + Job Tracker

**Estimated Time:** 4-5 hours  
**Priority:** 🟢 MEDIUM — Feature 5 mostly works, Job Tracker needs polish

---

## 🎯 Your Mission

1. **Feature 5 (Narrative Architect):** Test and polish the GitHub → narrative generation flow (already 80% done)
2. **Job Tracker:** Build the Kanban pipeline with drag-and-drop functionality

---

## 📁 Your Files

### Backend Files (YOUR TERRITORY)
```
Backend/app/api/feature5.py          📝 Narrative endpoints (mostly done)
Backend/app/api/jobs.py              📝 Job tracker CRUD + stats
Backend/app/analysis/feature5_engine.py   📝 Narrative generation logic
Backend/app/models.py                ⚠️  READ ONLY (Feature5NarrativeSession model)
Backend/app/models_jobs.py           ⚠️  READ ONLY (Job model)
Backend/app/schemas_feature5.py      ⚠️  READ ONLY (Feature5 schemas)
Backend/app/schemas_jobs.py          ⚠️  READ ONLY (Job schemas)
```

### Frontend Files (YOUR TERRITORY)
```
Frontend/index.html                  📝 Lines 1300-1500 (Feature 5 workspace)
                                     📝 Lines 350-450 (Job Tracker section)
Frontend/app.js                      📝 Lines 1100-1300 (Feature 5 handlers)
                                     📝 Lines 1300-1500 (Job Tracker handlers)
```

---

## ✅ Task Checklist

---

## 🎯 FEATURE 5: NARRATIVE ARCHITECT

### Phase 1: Backend Testing (Hour 1)

#### Test Create Session Endpoint
```bash
curl -X POST "http://localhost:8000/api/feature5/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-004",
    "repo_subpath": ".",
    "target_role": "Senior Backend Engineer",
    "tone": "deep_tech",
    "jd_text": "Looking for a backend engineer with microservices experience...",
    "resume_text": "5 years experience building scalable APIs...",
    "linkedin_text": "Passionate about distributed systems...",
    "github_repo": "https://github.com/username/project",
    "selected_projects": ["project-1", "project-2"]
  }'
```

**Expected Response:**
```json
{
  "session_id": 1,
  "candidate_id": "test-004",
  "deep_analysis": {
    "architecture_type": "microservice",
    "tech_stack": ["Python", "FastAPI", "Docker", "PostgreSQL"],
    "complexity_score": 7.5,
    "code_quality_score": 8.2
  },
  "narrative": {
    "problem_solution_narrative": [
      "Built a scalable API gateway handling 10K requests/second",
      "Implemented distributed caching with Redis to reduce latency by 40%"
    ],
    "impact_metrics": [
      "Reduced API response time from 500ms to 120ms",
      "Scaled system to support 100K daily active users"
    ]
  },
  "talk_track": {
    "elevator_pitch": "I build high-performance backend systems...",
    "technical_deep_dive": "In my latest project, I architected a microservices platform..."
  },
  "gap_analysis": {
    "resume_gaps": ["Missing quantified metrics in experience section"],
    "linkedin_gaps": ["Projects not mentioned on LinkedIn"],
    "github_gaps": ["README lacks architecture diagrams"]
  },
  "consistency_check": {
    "resume_overlap": 75,
    "linkedin_overlap": 60,
    "issues": ["LinkedIn mentions 'machine learning' but no ML code in GitHub"]
  }
}
```

---

### Phase 2: Frontend Testing & Polish (Hour 2)

#### Verify GitHub Input Field (Already Fixed)
**File:** `Frontend/index.html` lines 1300-1400

The GitHub URL input was recently added. Verify it's working:

```html
<div class="feature5-input">
  <h3>Input Configuration</h3>
  
  <label>GitHub Repository URL *</label>
  <input type="text" id="f5GithubRepo" placeholder="https://github.com/username/repo" required />
  <p class="hint">Public GitHub repository to analyze</p>
  
  <label>Target Role *</label>
  <input type="text" id="f5TargetRole" placeholder="e.g., Senior Backend Engineer" required />
  
  <label>Narrative Tone</label>
  <select id="f5Tone">
    <option value="deep_tech">Deep Tech (Technical depth)</option>
    <option value="impact">Impact-Focused (Business outcomes)</option>
    <option value="storytelling">Storytelling (Narrative flow)</option>
  </select>
  
  <label>Job Description (Optional)</label>
  <textarea id="f5JdText" placeholder="Paste job description for tailored narrative..." rows="4"></textarea>
  
  <label>Selected Projects (Optional)</label>
  <input type="text" id="f5SelectedProjects" placeholder="project-1, project-2" />
  <p class="hint">Comma-separated project names to focus on</p>
  
  <button onclick="generateNarrative()" class="btn-primary">Generate Narrative</button>
</div>
```

---

#### JavaScript Handler
**File:** `Frontend/app.js` lines 1100-1300

```javascript
async function generateNarrative() {
  const githubRepo = document.getElementById('f5GithubRepo').value;
  const targetRole = document.getElementById('f5TargetRole').value;
  const tone = document.getElementById('f5Tone').value;
  const jdText = document.getElementById('f5JdText').value;
  const selectedProjects = document.getElementById('f5SelectedProjects').value
    .split(',').map(s => s.trim()).filter(s => s);
  
  if (!githubRepo || !targetRole) {
    alert('Please enter GitHub repository URL and target role');
    return;
  }
  
  // Validate GitHub URL
  if (!githubRepo.startsWith('https://github.com/')) {
    alert('Please enter a valid GitHub URL (https://github.com/username/repo)');
    return;
  }
  
  // Show loading
  document.getElementById('f5Results').innerHTML = '<p>Analyzing repository and generating narrative...</p>';
  document.getElementById('f5Results').style.display = 'block';
  
  try {
    const response = await fetch('http://localhost:8000/api/feature5/sessions', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        candidate_id: getCurrentCandidateId(),
        repo_subpath: '.',
        target_role: targetRole,
        tone: tone,
        jd_text: jdText,
        resume_text: '',  // Optional: fetch from Feature 1 if available
        linkedin_text: '',
        github_repo: githubRepo,
        selected_projects: selectedProjects
      })
    });
    
    if (!response.ok) throw new Error('Narrative generation failed');
    
    const data = await response.json();
    displayNarrativeResults(data);
    
  } catch (error) {
    console.error('Narrative generation error:', error);
    alert('Failed to generate narrative. Check if the GitHub repo is public.');
  }
}

function displayNarrativeResults(data) {
  const resultsHtml = `
    <div class="narrative-results">
      <div class="section">
        <h3>Deep Analysis</h3>
        <p><strong>Architecture:</strong> ${data.deep_analysis.architecture_type}</p>
        <p><strong>Tech Stack:</strong> ${data.deep_analysis.tech_stack.join(', ')}</p>
        <p><strong>Complexity Score:</strong> ${data.deep_analysis.complexity_score}/10</p>
      </div>
      
      <div class="section">
        <h3>Problem-Solution Narrative</h3>
        <ul>
          ${data.narrative.problem_solution_narrative.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </div>
      
      <div class="section">
        <h3>Talk Track</h3>
        <h4>Elevator Pitch</h4>
        <p>${data.talk_track.elevator_pitch}</p>
        <h4>Technical Deep Dive</h4>
        <p>${data.talk_track.technical_deep_dive}</p>
      </div>
      
      <div class="section">
        <h3>Gap Analysis</h3>
        <h4>Resume Gaps</h4>
        <ul>${data.gap_analysis.resume_gaps.map(g => `<li>${g}</li>`).join('')}</ul>
        <h4>LinkedIn Gaps</h4>
        <ul>${data.gap_analysis.linkedin_gaps.map(g => `<li>${g}</li>`).join('')}</ul>
      </div>
      
      <div class="section">
        <h3>Consistency Check</h3>
        <p>Resume Overlap: ${data.consistency_check.resume_overlap}%</p>
        <p>LinkedIn Overlap: ${data.consistency_check.linkedin_overlap}%</p>
        ${data.consistency_check.issues.length > 0 ? 
          `<h4>Issues:</h4><ul>${data.consistency_check.issues.map(i => `<li>${i}</li>`).join('')}</ul>` 
          : '<p>✅ No consistency issues found</p>'}
      </div>
      
      <div class="export-buttons">
        <button onclick="exportLinkedInPost(${data.session_id})">Export LinkedIn Post</button>
        <button onclick="exportPortfolioSite(${data.session_id})">Export Portfolio Site</button>
      </div>
    </div>
  `;
  
  document.getElementById('f5Results').innerHTML = resultsHtml;
}

async function exportLinkedInPost(sessionId) {
  try {
    const response = await fetch(`http://localhost:8000/api/feature5/sessions/${sessionId}/linkedin-post`);
    const data = await response.json();
    
    // Copy to clipboard
    navigator.clipboard.writeText(data.post_text);
    alert('LinkedIn post copied to clipboard!');
  } catch (error) {
    console.error('Export error:', error);
    alert('Failed to export LinkedIn post');
  }
}

async function exportPortfolioSite(sessionId) {
  try {
    const response = await fetch(`http://localhost:8000/api/feature5/sessions/${sessionId}/portfolio-site`);
    const blob = await response.blob();
    
    // Download as ZIP
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'portfolio-site.zip';
    a.click();
  } catch (error) {
    console.error('Export error:', error);
    alert('Failed to export portfolio site');
  }
}
```

---

## 🎯 JOB TRACKER

### Phase 3: Backend Testing (Hour 3)

#### Test Job CRUD Endpoints

**Create Job:**
```bash
curl -X POST "http://localhost:8000/api/jobs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "company_name": "TechCorp",
    "role_title": "Senior Backend Engineer",
    "status": "applied",
    "job_url": "https://techcorp.com/careers/123",
    "notes": "Applied via LinkedIn",
    "salary_range": "$120K - $180K",
    "location": "San Francisco, CA",
    "remote_type": "hybrid"
  }'
```

**Get All Jobs:**
```bash
curl -X GET "http://localhost:8000/api/jobs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Job Status:**
```bash
curl -X PATCH "http://localhost:8000/api/jobs/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status": "interviewing"}'
```

**Get Pipeline Stats:**
```bash
curl -X GET "http://localhost:8000/api/jobs/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "applied": 5,
  "interviewing": 2,
  "offer": 1,
  "rejected": 3,
  "withdrawn": 0
}
```

---

### Phase 4: Job Tracker Frontend (Hour 4)

#### Build Kanban Board
**File:** `Frontend/index.html` lines 350-450

```html
<div class="job-tracker">
  <h2>Job Pipeline</h2>
  
  <div class="pipeline-stats">
    <div class="stat">
      <span class="stat-number" id="statsApplied">0</span>
      <span class="stat-label">Applied</span>
    </div>
    <div class="stat">
      <span class="stat-number" id="statsInterviewing">0</span>
      <span class="stat-label">Interviewing</span>
    </div>
    <div class="stat">
      <span class="stat-number" id="statsOffer">0</span>
      <span class="stat-label">Offers</span>
    </div>
    <div class="stat">
      <span class="stat-number" id="statsRejected">0</span>
      <span class="stat-label">Rejected</span>
    </div>
  </div>
  
  <button onclick="showAddJobModal()" class="btn-primary">+ Add Job</button>
  
  <div class="kanban-board">
    <div class="kanban-column" data-status="applied">
      <h3>Applied</h3>
      <div class="job-cards" id="columnApplied"></div>
    </div>
    
    <div class="kanban-column" data-status="interviewing">
      <h3>Interviewing</h3>
      <div class="job-cards" id="columnInterviewing"></div>
    </div>
    
    <div class="kanban-column" data-status="offer">
      <h3>Offer</h3>
      <div class="job-cards" id="columnOffer"></div>
    </div>
    
    <div class="kanban-column" data-status="rejected">
      <h3>Rejected</h3>
      <div class="job-cards" id="columnRejected"></div>
    </div>
  </div>
</div>

<!-- Add Job Modal -->
<div id="addJobModal" class="modal" style="display:none;">
  <div class="modal-content">
    <h3>Add New Job</h3>
    <input type="text" id="jobCompanyName" placeholder="Company Name" />
    <input type="text" id="jobRoleTitle" placeholder="Role Title" />
    <input type="text" id="jobUrl" placeholder="Job URL" />
    <input type="text" id="jobSalaryRange" placeholder="Salary Range (e.g., $120K - $180K)" />
    <input type="text" id="jobLocation" placeholder="Location" />
    <select id="jobRemoteType">
      <option value="onsite">On-site</option>
      <option value="remote">Remote</option>
      <option value="hybrid">Hybrid</option>
    </select>
    <textarea id="jobNotes" placeholder="Notes..." rows="3"></textarea>
    <button onclick="addJob()" class="btn-primary">Add Job</button>
    <button onclick="closeAddJobModal()" class="btn-secondary">Cancel</button>
  </div>
</div>
```

---

#### JavaScript Handler
**File:** `Frontend/app.js` lines 1300-1500

```javascript
async function loadJobTracker() {
  try {
    // Load stats
    const statsResponse = await fetch('http://localhost:8000/api/jobs/stats', {
      headers: {'Authorization': `Bearer ${getAuthToken()}`}
    });
    const stats = await statsResponse.json();
    
    document.getElementById('statsApplied').textContent = stats.applied || 0;
    document.getElementById('statsInterviewing').textContent = stats.interviewing || 0;
    document.getElementById('statsOffer').textContent = stats.offer || 0;
    document.getElementById('statsRejected').textContent = stats.rejected || 0;
    
    // Load jobs
    const jobsResponse = await fetch('http://localhost:8000/api/jobs', {
      headers: {'Authorization': `Bearer ${getAuthToken()}`}
    });
    const jobs = await jobsResponse.json();
    
    // Clear columns
    document.getElementById('columnApplied').innerHTML = '';
    document.getElementById('columnInterviewing').innerHTML = '';
    document.getElementById('columnOffer').innerHTML = '';
    document.getElementById('columnRejected').innerHTML = '';
    
    // Populate columns
    jobs.forEach(job => {
      const card = createJobCard(job);
      document.getElementById(`column${capitalize(job.status)}`).appendChild(card);
    });
    
    // Enable drag-and-drop
    enableDragAndDrop();
    
  } catch (error) {
    console.error('Job tracker load error:', error);
  }
}

function createJobCard(job) {
  const card = document.createElement('div');
  card.className = 'job-card';
  card.draggable = true;
  card.dataset.jobId = job.id;
  card.innerHTML = `
    <h4>${job.company_name}</h4>
    <p>${job.role_title}</p>
    <p class="job-meta">${job.location} • ${job.remote_type}</p>
    ${job.salary_range ? `<p class="job-salary">${job.salary_range}</p>` : ''}
    <p class="job-date">${new Date(job.created_at).toLocaleDateString()}</p>
  `;
  
  card.addEventListener('dragstart', handleDragStart);
  card.addEventListener('click', () => showJobDetails(job.id));
  
  return card;
}

function enableDragAndDrop() {
  const columns = document.querySelectorAll('.job-cards');
  
  columns.forEach(column => {
    column.addEventListener('dragover', handleDragOver);
    column.addEventListener('drop', handleDrop);
  });
}

function handleDragStart(e) {
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', e.target.dataset.jobId);
  e.target.style.opacity = '0.4';
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault();
  }
  e.dataTransfer.dropEffect = 'move';
  return false;
}

async function handleDrop(e) {
  if (e.stopPropagation) {
    e.stopPropagation();
  }
  
  const jobId = e.dataTransfer.getData('text/html');
  const newStatus = e.target.closest('.kanban-column').dataset.status;
  
  try {
    // Update job status
    await fetch(`http://localhost:8000/api/jobs/${jobId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({status: newStatus})
    });
    
    // Reload tracker
    loadJobTracker();
    
  } catch (error) {
    console.error('Job update error:', error);
    alert('Failed to update job status');
  }
  
  return false;
}

async function addJob() {
  const companyName = document.getElementById('jobCompanyName').value;
  const roleTitle = document.getElementById('jobRoleTitle').value;
  const jobUrl = document.getElementById('jobUrl').value;
  const salaryRange = document.getElementById('jobSalaryRange').value;
  const location = document.getElementById('jobLocation').value;
  const remoteType = document.getElementById('jobRemoteType').value;
  const notes = document.getElementById('jobNotes').value;
  
  if (!companyName || !roleTitle) {
    alert('Please enter company name and role title');
    return;
  }
  
  try {
    await fetch('http://localhost:8000/api/jobs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({
        company_name: companyName,
        role_title: roleTitle,
        status: 'applied',
        job_url: jobUrl,
        notes: notes,
        salary_range: salaryRange,
        location: location,
        remote_type: remoteType
      })
    });
    
    closeAddJobModal();
    loadJobTracker();
    
  } catch (error) {
    console.error('Add job error:', error);
    alert('Failed to add job');
  }
}

function showAddJobModal() {
  document.getElementById('addJobModal').style.display = 'block';
}

function closeAddJobModal() {
  document.getElementById('addJobModal').style.display = 'none';
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function getAuthToken() {
  return localStorage.getItem('authToken') || '';
}

// Load on page load
document.addEventListener('DOMContentLoaded', loadJobTracker);
```

---

### Phase 5: Testing & Polish (Hour 5)

#### Test Feature 5
- [ ] Generate narrative with public GitHub repo
- [ ] Verify all sections display correctly
- [ ] Test export LinkedIn post
- [ ] Test export portfolio site (optional)

#### Test Job Tracker
- [ ] Add 5 test jobs
- [ ] Drag job from "Applied" to "Interviewing"
- [ ] Verify stats update correctly
- [ ] Test job details modal

---

## 🧪 Testing Checklist

### Feature 5 Tests
- [ ] Valid GitHub URL → narrative generates
- [ ] Invalid GitHub URL → error message
- [ ] With job description → tailored narrative
- [ ] Without job description → generic narrative

### Job Tracker Tests
- [ ] Add job → appears in "Applied" column
- [ ] Drag job → status updates in backend
- [ ] Stats display correctly
- [ ] Empty state shows helpful message

---

## 🚨 Common Issues & Fixes

### Issue 1: GitHub repo analysis fails
**Fix:** Ensure repo is public, check if `github_repo` URL is valid

### Issue 2: Drag-and-drop not working
**Fix:** Check if `draggable="true"` is set on job cards

### Issue 3: Job stats not updating
**Fix:** Ensure `/api/jobs/stats` endpoint is called after status change

### Issue 4: Export buttons not working
**Fix:** Check if session_id is passed correctly to export functions

---

## 🎬 Demo Prep

### Feature 5 Demo (30 seconds)
> "Feature 5 analyzes your GitHub projects and builds a compelling narrative. I'll paste my repo URL and target role. The AI analyzes my code architecture, extracts impact metrics, and generates a talk track. Here's my elevator pitch, technical deep dive, and a consistency check across my resume, LinkedIn, and GitHub. I can export this as a LinkedIn post or portfolio site."

### Job Tracker Demo (15 seconds)
> "The job tracker ties everything together. Here's my pipeline: 5 applications, 2 interviews, 1 offer. I can drag jobs between stages, and the system tracks my progress."

---

## ⏰ Timeline

| Hour | Task |
|------|------|
| 1 | Feature 5 backend testing |
| 2 | Feature 5 frontend polish |
| 3 | Job tracker backend testing |
| 4 | Job tracker frontend (Kanban) |
| 5 | Testing + polish + demo prep |

---

## 🏆 Success Criteria

- [ ] Feature 5 generates narrative from GitHub
- [ ] Export functions work
- [ ] Job tracker displays all jobs
- [ ] Drag-and-drop updates status
- [ ] Stats display correctly
- [ ] Demo runs smoothly

---

**Feature 5 is mostly done — focus on making the job tracker slick! 📊**
