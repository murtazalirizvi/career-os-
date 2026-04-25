<!-- we are good - member 2 assignments documented and verified -->
# Member 2: Feature 2 (Interview Autopsy) + Feature 4 (Mock Interview)

**Estimated Time:** 5-6 hours  
**Priority:** 🟡 HIGH — Interview features showcase AI depth

---

## 🎯 Your Mission

Build two interview-focused features that demonstrate deep AI integration:
1. **Feature 2:** Post-interview autopsy with transcript analysis
2. **Feature 4:** AI mock interviewer with persona-based questioning

Both features share transcript processing logic and showcase Gemini's capabilities.

---

## 📁 Your Files

### Backend Files (YOUR TERRITORY)
```
Backend/app/api/feature2.py          📝 Interview autopsy endpoints
Backend/app/api/feature4.py          📝 Mock interview endpoints
Backend/app/analysis/feature2_engine.py   📝 Autopsy analysis logic
Backend/app/analysis/feature4_engine.py   📝 Persona play logic
Backend/app/analysis/vtt_parser.py   📝 Transcript parsing utilities
Backend/app/models.py                ⚠️  READ ONLY (Feature2/4 models)
Backend/app/schemas_feature2.py      ⚠️  READ ONLY (Feature2 schemas)
Backend/app/schemas_feature4.py      ⚠️  READ ONLY (Feature4 schemas)
```

### Frontend Files (YOUR TERRITORY)
```
Frontend/index.html                  📝 Lines 650-800 (Feature 2 workspace)
                                     📝 Lines 1100-1300 (Feature 4 workspace)
Frontend/app.js                      📝 Lines 450-600 (Feature 2 handlers)
                                     📝 Lines 900-1100 (Feature 4 handlers)
```

---

## ✅ Task Checklist

---

## 🎯 FEATURE 2: INTERVIEW AUTOPSY

### Phase 1: Backend Testing (Hour 1)

#### Test Create Interview Endpoint
```bash
curl -X POST "http://localhost:8000/api/feature2/interviews" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-002",
    "company_name": "TechCorp",
    "role_name": "Senior Backend Engineer",
    "interview_round": "technical",
    "lifecycle_stage": "phone_screen",
    "interview_outcome": "rejected",
    "interview_notes": "Asked about system design. Struggled with database scaling question.",
    "transcript_text": "Interviewer: Can you explain how you would scale a database? Candidate: Um, I think we could use sharding... maybe partitioning?",
    "transcript_vtt": "",
    "technical_expectations": ["system design", "database scaling", "caching"],
    "culture_vibe": "collaborative",
    "interviewer_friendliness": 7,
    "hardest_question_hint": "Database scaling under high load",
    "advanced_round_reached": false,
    "rejection_reason_hint": "Lacked depth in distributed systems",
    "company_stage": "scaleup"
  }'
```

**Expected Response:**
```json
{
  "interview_id": 1,
  "candidate_id": "test-002",
  "company_name": "TechCorp",
  "role_name": "Senior Backend Engineer",
  "ingestion_summary": {
    "total_words": 150,
    "question_count": 5,
    "filler_count": 8
  },
  "technical_analysis": {
    "depth_score": 45,
    "keyword_coverage": 60,
    "tradeoff_mentions": 2
  },
  "behavioral_analysis": {
    "confidence_score": 55,
    "hedge_count": 6,
    "tone": "anxious"
  },
  "strategic_actions": [
    "Study distributed database patterns",
    "Practice explaining tradeoffs clearly",
    "Reduce filler words"
  ],
  "overall_autopsy_score": 52,
  "ai_insights": "Your technical knowledge is present but lacks depth. Focus on explaining WHY you'd choose sharding over replication..."
}
```

---

### Phase 2: Frontend Upload Flow (Hour 2)

#### Build Interview Input Form
**File:** `Frontend/index.html` lines 650-750

```html
<div class="feature2-workspace">
  <h2>Feature 2: Interview Autopsy</h2>
  
  <div class="interview-form">
    <h3>Interview Details</h3>
    
    <input type="text" id="f2CompanyName" placeholder="Company Name" required />
    <input type="text" id="f2RoleName" placeholder="Role (e.g., Senior Backend Engineer)" required />
    
    <select id="f2InterviewRound">
      <option value="phone_screen">Phone Screen</option>
      <option value="technical">Technical Round</option>
      <option value="behavioral">Behavioral Round</option>
      <option value="system_design">System Design</option>
      <option value="final">Final Round</option>
    </select>
    
    <select id="f2Outcome">
      <option value="passed">Passed</option>
      <option value="rejected">Rejected</option>
      <option value="pending">Pending</option>
    </select>
    
    <textarea id="f2Notes" placeholder="Your notes about the interview..." rows="4"></textarea>
    
    <h4>Transcript (Optional)</h4>
    <textarea id="f2Transcript" placeholder="Paste interview transcript here..." rows="6"></textarea>
    
    <p class="hint">Or upload VTT file:</p>
    <input type="file" id="f2VttFile" accept=".vtt" />
    
    <h4>Context</h4>
    <input type="text" id="f2TechnicalExpectations" placeholder="Expected topics (comma-separated)" />
    <input type="text" id="f2CultureVibe" placeholder="Culture vibe (e.g., collaborative, fast-paced)" />
    <input type="number" id="f2Friendliness" min="1" max="10" placeholder="Interviewer friendliness (1-10)" />
    
    <button onclick="submitInterviewAutopsy()" class="btn-primary">Analyze Interview</button>
  </div>
  
  <div class="autopsy-results" id="f2Results" style="display:none;">
    <h3>Autopsy Report</h3>
    
    <div class="score-card">
      <p class="big-score" id="f2OverallScore">--</p>
      <p>Overall Autopsy Score</p>
    </div>
    
    <div class="analysis-sections">
      <div class="section">
        <h4>Technical Analysis</h4>
        <p>Depth Score: <span id="f2DepthScore">--</span></p>
        <p>Keyword Coverage: <span id="f2KeywordCoverage">--</span>%</p>
      </div>
      
      <div class="section">
        <h4>Behavioral Analysis</h4>
        <p>Confidence Score: <span id="f2ConfidenceScore">--</span></p>
        <p>Tone: <span id="f2Tone">--</span></p>
      </div>
      
      <div class="section">
        <h4>Strategic Actions</h4>
        <ul id="f2Actions"></ul>
      </div>
      
      <div class="section ai-insights">
        <h4>AI Coaching (Gemini)</h4>
        <p id="f2AiInsights">--</p>
      </div>
    </div>
  </div>
</div>
```

---

#### JavaScript Handler
**File:** `Frontend/app.js` lines 450-600

```javascript
async function submitInterviewAutopsy() {
  const companyName = document.getElementById('f2CompanyName').value;
  const roleName = document.getElementById('f2RoleName').value;
  const interviewRound = document.getElementById('f2InterviewRound').value;
  const outcome = document.getElementById('f2Outcome').value;
  const notes = document.getElementById('f2Notes').value;
  const transcript = document.getElementById('f2Transcript').value;
  const technicalExpectations = document.getElementById('f2TechnicalExpectations').value
    .split(',').map(s => s.trim()).filter(s => s);
  const cultureVibe = document.getElementById('f2CultureVibe').value;
  const friendliness = parseInt(document.getElementById('f2Friendliness').value) || 5;
  
  if (!companyName || !roleName) {
    alert('Please enter company name and role');
    return;
  }
  
  // Show loading
  document.getElementById('f2Results').innerHTML = '<p>Analyzing interview...</p>';
  document.getElementById('f2Results').style.display = 'block';
  
  try {
    const response = await fetch('http://localhost:8000/api/feature2/interviews', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        candidate_id: getCurrentCandidateId(),
        company_name: companyName,
        role_name: roleName,
        interview_round: interviewRound,
        lifecycle_stage: 'completed',
        interview_outcome: outcome,
        interview_notes: notes,
        transcript_text: transcript,
        transcript_vtt: '',
        technical_expectations: technicalExpectations,
        culture_vibe: cultureVibe,
        interviewer_friendliness: friendliness,
        hardest_question_hint: '',
        advanced_round_reached: outcome === 'passed',
        rejection_reason_hint: '',
        company_stage: 'scaleup'
      })
    });
    
    if (!response.ok) throw new Error('Autopsy failed');
    
    const data = await response.json();
    displayAutopsyResults(data);
    
  } catch (error) {
    console.error('Autopsy error:', error);
    alert('Failed to analyze interview');
  }
}

function displayAutopsyResults(data) {
  document.getElementById('f2OverallScore').textContent = data.overall_autopsy_score;
  document.getElementById('f2DepthScore').textContent = data.technical_analysis.depth_score;
  document.getElementById('f2KeywordCoverage').textContent = data.technical_analysis.keyword_coverage;
  document.getElementById('f2ConfidenceScore').textContent = data.behavioral_analysis.confidence_score;
  document.getElementById('f2Tone').textContent = data.behavioral_analysis.tone;
  
  // Display strategic actions
  const actionsHtml = data.strategic_actions.map(action => 
    `<li>${action}</li>`
  ).join('');
  document.getElementById('f2Actions').innerHTML = actionsHtml;
  
  // Display AI insights
  document.getElementById('f2AiInsights').textContent = data.ai_insights || 'No AI insights available';
  
  document.getElementById('f2Results').style.display = 'block';
}
```

---

## 🎯 FEATURE 4: MOCK INTERVIEW (PERSONA PLAY)

### Phase 3: Backend Testing (Hour 3)

#### Test Create Session Endpoint
```bash
curl -X POST "http://localhost:8000/api/feature4/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-002",
    "role_name": "Backend Engineer",
    "persona_mode": "stone_faced",
    "selected_persona": null,
    "target_company": "Google",
    "language": "english",
    "include_video": false
  }'
```

**Expected Response:**
```json
{
  "session_id": 1,
  "candidate_id": "test-002",
  "role_name": "Backend Engineer",
  "persona": {
    "key": "stone_faced",
    "label": "Stone-Faced Architect",
    "style": "minimal feedback, deep architecture pressure",
    "pressure": 9
  },
  "opening_questions": [
    {
      "question_type": "technical",
      "question_text": "Design a URL shortener. Walk me through your architecture.",
      "expected_depth": ["database choice", "collision handling", "scalability"]
    }
  ],
  "status": "active"
}
```

---

#### Test Turn Submission
```bash
curl -X POST "http://localhost:8000/api/feature4/sessions/1/turns" \
  -H "Content-Type: application/json" \
  -d '{
    "answer_text": "I would use a hash function to generate short codes, store them in a database with the original URL, and use Redis for caching frequently accessed URLs.",
    "question_index": 0
  }'
```

**Expected Response:**
```json
{
  "turn_id": 1,
  "realtime_feedback": {
    "depth_score": 65,
    "missing_topics": ["collision handling", "distributed systems"],
    "tone": "confident"
  },
  "whisper_hint": "Good start. Now explain how you'd handle hash collisions.",
  "next_question": {
    "question_text": "What happens when two URLs generate the same short code?",
    "question_type": "follow_up"
  }
}
```

---

### Phase 4: Frontend Mock Interview UI (Hour 4)

#### Build Session Interface
**File:** `Frontend/index.html` lines 1100-1300

```html
<div class="feature4-workspace">
  <h2>Feature 4: AI Mock Interview</h2>
  
  <div class="session-setup" id="f4Setup">
    <h3>Setup Mock Interview</h3>
    
    <input type="text" id="f4RoleName" placeholder="Target Role (e.g., Backend Engineer)" />
    
    <select id="f4Persona">
      <option value="stone_faced">Stone-Faced Architect (Pressure: 9/10)</option>
      <option value="rushed_founder">Rushed Founder (Pressure: 8/10)</option>
      <option value="non_tech_hr">Non-Tech HR (Pressure: 6/10)</option>
      <option value="deep_diver">Deep-Diver (Pressure: 9/10)</option>
      <option value="blind">Blind Mode (Random)</option>
    </select>
    
    <input type="text" id="f4TargetCompany" placeholder="Target Company (optional)" />
    
    <button onclick="startMockInterview()" class="btn-primary">Start Interview</button>
  </div>
  
  <div class="interview-session" id="f4Session" style="display:none;">
    <div class="persona-info">
      <h4 id="f4PersonaLabel">--</h4>
      <p id="f4PersonaStyle">--</p>
    </div>
    
    <div class="conversation">
      <div id="f4ConversationLog"></div>
    </div>
    
    <div class="answer-input">
      <textarea id="f4AnswerText" placeholder="Your answer..." rows="4"></textarea>
      <button onclick="submitAnswer()" class="btn-primary">Submit Answer</button>
    </div>
    
    <div class="realtime-feedback" id="f4Feedback" style="display:none;">
      <h4>Real-time Coaching</h4>
      <p id="f4WhisperHint">--</p>
      <p>Depth Score: <span id="f4DepthScore">--</span></p>
    </div>
    
    <button onclick="endSession()" class="btn-secondary">End Interview</button>
  </div>
  
  <div class="session-report" id="f4Report" style="display:none;">
    <h3>Interview Report</h3>
    <div id="f4ReportContent"></div>
  </div>
</div>
```

---

#### JavaScript Handler
**File:** `Frontend/app.js` lines 900-1100

```javascript
let currentSessionId = null;
let currentQuestionIndex = 0;

async function startMockInterview() {
  const roleName = document.getElementById('f4RoleName').value;
  const persona = document.getElementById('f4Persona').value;
  const targetCompany = document.getElementById('f4TargetCompany').value;
  
  if (!roleName) {
    alert('Please enter target role');
    return;
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/feature4/sessions', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        candidate_id: getCurrentCandidateId(),
        role_name: roleName,
        persona_mode: persona,
        selected_persona: persona === 'blind' ? null : persona,
        target_company: targetCompany,
        language: 'english',
        include_video: false
      })
    });
    
    if (!response.ok) throw new Error('Failed to start session');
    
    const data = await response.json();
    currentSessionId = data.session_id;
    
    // Display persona info
    document.getElementById('f4PersonaLabel').textContent = data.persona.label;
    document.getElementById('f4PersonaStyle').textContent = data.persona.style;
    
    // Display first question
    addToConversation('interviewer', data.opening_questions[0].question_text);
    
    // Show session UI
    document.getElementById('f4Setup').style.display = 'none';
    document.getElementById('f4Session').style.display = 'block';
    
  } catch (error) {
    console.error('Session start error:', error);
    alert('Failed to start mock interview');
  }
}

async function submitAnswer() {
  const answerText = document.getElementById('f4AnswerText').value;
  
  if (!answerText.trim()) {
    alert('Please enter your answer');
    return;
  }
  
  try {
    const response = await fetch(`http://localhost:8000/api/feature4/sessions/${currentSessionId}/turns`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        answer_text: answerText,
        question_index: currentQuestionIndex
      })
    });
    
    if (!response.ok) throw new Error('Failed to submit answer');
    
    const data = await response.json();
    
    // Add answer to conversation
    addToConversation('candidate', answerText);
    
    // Show real-time feedback
    document.getElementById('f4WhisperHint').textContent = data.whisper_hint;
    document.getElementById('f4DepthScore').textContent = data.realtime_feedback.depth_score;
    document.getElementById('f4Feedback').style.display = 'block';
    
    // Add next question
    if (data.next_question) {
      setTimeout(() => {
        addToConversation('interviewer', data.next_question.question_text);
        document.getElementById('f4AnswerText').value = '';
        document.getElementById('f4Feedback').style.display = 'none';
        currentQuestionIndex++;
      }, 2000);
    }
    
  } catch (error) {
    console.error('Answer submission error:', error);
    alert('Failed to submit answer');
  }
}

function addToConversation(speaker, text) {
  const log = document.getElementById('f4ConversationLog');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${speaker}`;
  messageDiv.innerHTML = `
    <strong>${speaker === 'interviewer' ? 'Interviewer' : 'You'}:</strong>
    <p>${text}</p>
  `;
  log.appendChild(messageDiv);
  log.scrollTop = log.scrollHeight;
}

async function endSession() {
  if (!confirm('Are you sure you want to end the interview?')) return;
  
  try {
    const response = await fetch(`http://localhost:8000/api/feature4/sessions/${currentSessionId}/finalize`, {
      method: 'POST'
    });
    
    if (!response.ok) throw new Error('Failed to finalize session');
    
    const data = await response.json();
    
    // Show report
    document.getElementById('f4Session').style.display = 'none';
    document.getElementById('f4Report').style.display = 'block';
    document.getElementById('f4ReportContent').innerHTML = `
      <p>Overall Score: ${data.synthesis.overall_score}</p>
      <h4>Strengths:</h4>
      <ul>${data.synthesis.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
      <h4>Areas to Improve:</h4>
      <ul>${data.synthesis.weaknesses.map(w => `<li>${w}</li>`).join('')}</ul>
    `;
    
  } catch (error) {
    console.error('Session end error:', error);
    alert('Failed to end session');
  }
}
```

---

### Phase 5: Testing & Polish (Hour 5-6)

#### Test Feature 2
- [ ] Submit interview with transcript → autopsy report generates
- [ ] Test with different outcomes (passed/rejected)
- [ ] Verify AI insights display correctly
- [ ] Test VTT file upload (optional)

#### Test Feature 4
- [ ] Start session with each persona
- [ ] Submit 3-4 answers → verify next questions adapt
- [ ] Check real-time feedback displays
- [ ] End session → verify final report

---

## 🧪 Testing Checklist

### Feature 2 Tests
- [ ] Autopsy with detailed transcript
- [ ] Autopsy with minimal notes
- [ ] Rejected interview analysis
- [ ] Passed interview analysis

### Feature 4 Tests
- [ ] Stone-Faced persona (high pressure)
- [ ] Non-Tech HR persona (ELI5 mode)
- [ ] Blind mode (random persona)
- [ ] 5-turn conversation flow

---

## 🚨 Common Issues & Fixes

### Issue 1: Transcript parsing fails
**Fix:** Check `Backend/app/analysis/vtt_parser.py` — ensure VTT format is valid

### Issue 2: Gemini insights empty
**Fix:** Check `GEMINI_API_KEY` in `.env`, fallback to heuristic feedback

### Issue 3: Mock interview questions too generic
**Fix:** Ensure `target_company` and `role_name` are passed to Gemini prompt

### Issue 4: Real-time feedback not showing
**Fix:** Check if `whisper_hint` is in API response, add error handling

---

## 🎬 Demo Prep

### Feature 2 Demo (30 seconds)
> "After an interview, you log your notes and paste the transcript. Our AI performs a full autopsy: technical depth, behavioral signals, tone analysis. Here's my score: 52 out of 100. The system tells me I lacked depth in distributed systems and used too many filler words. Gemini gives me specific coaching: 'Focus on explaining WHY you'd choose sharding over replication.'"

### Feature 4 Demo (45 seconds)
> "Now let's practice. I'll choose the Stone-Faced Architect persona — minimal feedback, high pressure. The AI asks: 'Design a URL shortener.' I answer... and here's the real-time coaching: 'Good start, but explain collision handling.' The next question adapts to my answer. After 5 turns, I get a full report with strengths and weaknesses."

---

## ⏰ Timeline

| Hour | Task |
|------|------|
| 1 | Feature 2 backend testing |
| 2 | Feature 2 frontend |
| 3 | Feature 4 backend testing |
| 4 | Feature 4 frontend |
| 5-6 | Testing + polish + demo prep |

---

## 🏆 Success Criteria

- [ ] Feature 2 autopsy works end-to-end
- [ ] Feature 4 mock interview runs 5+ turns
- [ ] AI insights display correctly
- [ ] Demo runs smoothly
- [ ] Both features showcase Gemini integration

---

**You've got the AI showcase features. Make them conversational and impressive! 🎤**
