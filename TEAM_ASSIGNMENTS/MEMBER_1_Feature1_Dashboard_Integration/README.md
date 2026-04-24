# Member 1: Feature 1 (Resume Analyzer) + Dashboard Integration

**Sitting with:** Member 5 (Dashboard Lead)  
**Estimated Time:** 4-5 hours  
**Priority:** 🔴 CRITICAL PATH

---

## 🎯 Your Mission

Make Feature 1 (Resume Analyzer) work end-to-end and integrate it with the dashboard. This is the entry point of the entire platform — if this doesn't work, nothing else matters.

---

## 📁 Your Files

### Backend Files (DO NOT MODIFY OTHERS)
```
Backend/app/api/feature1.py          ✅ Already solid, test endpoints
Backend/app/analysis/feature1_engine.py   ✅ Core logic, mostly done
Backend/app/analysis/pdf_utils.py    ✅ PDF parsing utilities
Backend/app/analysis/text_nlp.py     ✅ NLP scoring logic
Backend/app/analysis/benchmark.py    ✅ Competitive benchmarking
Backend/app/models.py                ⚠️  READ ONLY (Feature1Analysis model)
Backend/app/schemas.py               ⚠️  READ ONLY (Feature1 schemas)
```

### Frontend Files (YOUR TERRITORY)
```
Frontend/index.html                  📝 Lines 450-650 (Feature 1 workspace section)
Frontend/app.js                      📝 Lines 200-450 (Feature 1 handlers)
Frontend/styles.css                  📝 Feature 1 specific styles
```

### Test Files
```
Backend/data/uploads/                📂 Test resume PDFs here
```

---

## ✅ Task Checklist

### Phase 1: Backend Testing (Hour 1)
- [ ] Start backend: `cd Backend && python -m uvicorn app.main:app --reload --port 8000`
- [ ] Test API docs: http://localhost:8000/docs
- [ ] Test `/api/feature1/analyze` endpoint with a sample resume
- [ ] Verify response includes: scores, hot_zones, recommendations, ai_recommendations
- [ ] Test `/api/feature1/candidate/{candidate_id}/versions` endpoint
- [ ] Test `/api/feature1/candidate/{candidate_id}/latest` endpoint

**Test Command:**
```bash
curl -X POST "http://localhost:8000/api/feature1/analyze" \
  -F "candidate_id=test-001" \
  -F "job_category=Software Engineer" \
  -F "job_description=Looking for a Python developer with FastAPI experience" \
  -F "resume=@Backend/data/uploads/candidate-001-10705845b8b21e61.pdf"
```

---

### Phase 2: Frontend Upload Flow (Hour 2)
- [ ] Fix the resume upload form in `Frontend/index.html`
- [ ] Add drag-and-drop support for PDF files
- [ ] Add file size validation (max 5MB)
- [ ] Add loading spinner during upload
- [ ] Display upload progress

**Code Location:** `Frontend/app.js` → `handleFeature1Upload()` function

**Expected Flow:**
1. User drags PDF → visual feedback
2. User clicks "Analyze Resume" → spinner shows
3. API call to `/api/feature1/analyze`
4. Response displays scores and recommendations

---

### Phase 3: Results Display (Hour 3)
- [ ] Display score breakdown (4 scores: visual, ATS, semantic, benchmark)
- [ ] Render hot zones visualization (eye-tracking heatmap)
- [ ] Show heuristic recommendations list
- [ ] Show AI recommendations (Gemini-powered)
- [ ] Display "Ready to Apply" badge if score > 90

**Code Location:** `Frontend/app.js` → `displayFeature1Results()` function

**Hot Zones Visualization:**
```javascript
// Pseudo-code for rendering hot zones
function renderHotZones(hotZones, resumeImageUrl) {
  const canvas = document.getElementById('hotZonesCanvas');
  const ctx = canvas.getContext('2d');
  
  // Draw resume image
  const img = new Image();
  img.src = resumeImageUrl;
  img.onload = () => {
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
    // Overlay hot zones
    hotZones.forEach(zone => {
      ctx.fillStyle = `rgba(255, 0, 0, ${zone.weight})`;
      ctx.fillRect(zone.x, zone.y, 50, 50);
    });
  };
}
```

---

### Phase 4: Version History (Hour 4)
- [ ] Fetch version history: `/api/feature1/candidate/{candidate_id}/versions`
- [ ] Display versions in a timeline/list
- [ ] Add "Compare Versions" button
- [ ] Implement version comparison view (side-by-side scores)

**Code Location:** `Frontend/app.js` → `loadFeature1Versions()` function

---

### Phase 5: Dashboard Integration (Hour 5) — COORDINATE WITH MEMBER 5
- [ ] Ensure Feature 1 data is saved with correct `candidate_id`
- [ ] Test that `/api/me/dashboard` returns latest Feature 1 analysis
- [ ] Verify dashboard displays Feature 1 score correctly
- [ ] Test readiness score calculation includes Feature 1 data

**Integration Point:**
```javascript
// Member 5 will call this from dashboard
fetch(`/api/feature1/candidate/${candidateId}/latest`)
  .then(r => r.json())
  .then(data => {
    // Display on dashboard
    document.getElementById('resumeScore').textContent = data.score.overall;
  });
```

---

## 🧪 Testing Checklist

Test with these 3 scenarios:

### Test 1: Perfect Resume
- Upload: `Backend/data/uploads/candidate-001-10705845b8b21e61.pdf`
- Expected: Score > 85, "Ready to Apply" badge shows

### Test 2: Poor Resume
- Create a simple text-only PDF with no formatting
- Expected: Low visual score, ATS warnings, recommendations list

### Test 3: Version Comparison
- Upload same resume twice with different job descriptions
- Expected: Version history shows 2 entries, comparison works

---

## 🚨 Common Issues & Fixes

### Issue 1: "File too large" error
**Fix:** Check `Backend/app/api/feature1.py` line 50 — increase `MAX_FILE_SIZE`

### Issue 2: Hot zones not rendering
**Fix:** Ensure `hotzones_json` is properly parsed from backend response

### Issue 3: Gemini recommendations empty
**Fix:** Check `Backend/.env` has `GEMINI_API_KEY` set (graceful degradation is OK)

### Issue 4: Version history not loading
**Fix:** Ensure `candidate_id` is consistent across uploads

---

## 📞 Coordination Points

### With Member 5 (Dashboard)
- **Share your test `candidate_id`** so they can test dashboard integration
- **Agree on data format** for readiness score calculation
- **Test together** after Hour 4

### With Member 3 (Feature 3)
- Feature 3 needs `raw_resume_text` from Feature 1 for skill extraction
- Ensure `Feature1Analysis.raw_resume_text` is populated

---

## 🎬 Demo Prep

Prepare this 30-second demo:

> "Let me show you Feature 1 — the Hiring Manager Lens. I'll upload my resume and paste a job description. Watch as our AI analyzes it across four dimensions: visual hierarchy using eye-tracking simulation, ATS integrity, semantic match with the job description, and competitive benchmarking. Here's my score breakdown — 87 overall. The system gives me specific recommendations: 'Add more quantified achievements,' 'Increase keyword density for Python and FastAPI.' And here's the AI coaching from Gemini: 'Your experience section is strong, but consider leading with impact metrics.' Now I'm ready to apply."

---

## ⏰ Timeline

| Hour | Task |
|------|------|
| 1 | Backend testing |
| 2 | Frontend upload flow |
| 3 | Results display |
| 4 | Version history |
| 5 | Dashboard integration with Member 5 |

---

## 🏆 Success Criteria

- [ ] Can upload a resume and get scores back
- [ ] Hot zones visualization renders
- [ ] Recommendations display correctly
- [ ] Version history works
- [ ] Dashboard shows latest Feature 1 score
- [ ] Demo runs smoothly without errors

---

**Questions? Ask Member 5 (sitting next to you) or ping the team lead.**
