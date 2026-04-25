<!-- we are good - Rebound complete guide documented -->
# 🎯 Rebound Workspace - Complete Visual Guide

## 📺 Full Screen Layout with Labels

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Career OS                                                    [User] [Logout] │
├──┬───────────────────────────────────────────────────────────────────────────┤
│  │  The Rebound                                                              │
│  │  Post-interview autopsy — technical accuracy, behavioral critique         │
│☰ │                                                                            │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐│
│📊│  │Run Full      │ │Quick         │ │Load          │ │Generate Practice ││
│  │  │Autopsy       │ │Debrief       │ │Trend         │ │Questions         ││
│📤│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘│
│  │  ─────────────────────────────────────────────────────────────────────────│
│🔍│                                                                            │
│  │  ┌─────────────────────────────┐  ┌──────────────────────────────────┐  │
│🎤│  │ Interview Details           │  │ Autopsy Results                  │  │
│  │  │ ─────────────────           │  │ ───────────────                  │  │
│📈│  │ Required fields             │  │ Technical + Behavioral           │  │
│  │  │                             │  │                                  │  │
│🎭│  │ Company: Acme               │  │ Autopsy #25                      │  │
│  │  │ Role: Frontend Engineer     │  │ Overall Score: 64.14             │  │
│📖│  │                             │  │ Technical: 44.41                 │  │
│  │  │ Interview Round: Technical  │  │ Behavioral: 73.09                │  │
│🚪│  │ Interviewer Vibe: Neutral   │  │ Recovery: 85                     │  │
│  │  │                             │  │                                  │  │
│  │  │ Voice Notes / Debrief:      │  │ ┌──────────────────────────────┐ │  │
│  │  │ ┌─────────────────────────┐ │  │ │ 🎯 Practice Questions        │ │  │
│  │  │ │ I struggled with system │ │  │ │ Focus: technical (44.4/100)  │ │  │
│  │  │ │ design questions...     │ │  │ │                              │ │  │
│  │  │ └─────────────────────────┘ │  │ │ Q1: Design a distributed...  │ │  │
│  │  │                             │  │ │                              │ │  │
│  │  │ Transcript / VTT:           │  │ │ Q2: How would you handle...  │ │  │
│  │  │ ┌─────────────────────────┐ │  │ │                              │ │  │
│  │  │ │ Interviewer: How would  │ │  │ │ Q3: Explain the trade-offs...│ │  │
│  │  │ │ you scale a database... │ │  │ └──────────────────────────────┘ │  │
│  │  │ └─────────────────────────┘ │  │                                  │  │
│  │  │                             │  │ ⚠ False confidence: system design│  │
│  │  │ Audio URL: (Optional)       │  │ Filler words: 8 | STAR: n/a      │  │
│  │  │ ☐ Use AssemblyAI            │  │                                  │  │
│  │  └─────────────────────────────┘  └──────────────────────────────────┘  │
│  │                                                                            │
│  │  ┌─────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │  │ Growth Trend                │  │ Recovery Actions                 │  │
│  │  │ ─────────────               │  │ ────────────────                 │  │
│  │  │ Across interviews           │  │ Emails, scripts, patches         │  │
│  │  │                             │  │                                  │  │
│  │  │ Overall delta: +0           │  │ ☑ Follow-up: Send within 24h    │  │
│  │  │ Interviews tracked: n/a     │  │   Subject: Thank you - Backend   │  │
│  │  │ Forecast: rising-readiness  │  │   [View full email template]     │  │
│  │  │ Expected offer: 6 weeks     │  │                                  │  │
│  │  │ Readiness score: 63.58      │  │ ☑ Study Plan: Distributed systems│  │
│  │  │                             │  │   - Day 1: CAP theorem           │  │
│  │  │                             │  │   - Day 2: Sharding vs replication│ │
│  │  │                             │  │   - Day 3: Build Redis project   │  │
│  │  │                             │  │                                  │  │
│  │  │                             │  │ 💪 Resilience: This interview    │  │
│  │  │                             │  │    produced diagnostic data      │  │
│  │  └─────────────────────────────┘  └──────────────────────────────────┘  │
└──┴───────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 What Each Section Does

### **1. Top Buttons (Action Bar)**

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│Run Full      │ │Quick         │ │Load          │ │Generate Practice │
│Autopsy       │ │Debrief       │ │Trend         │ │Questions         │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘
```

| Button | What It Does | When to Use |
|--------|--------------|-------------|
| **Run Full Autopsy** | Complete AI analysis of your interview | After every interview (main feature) |
| **Quick Debrief** | Fast 30-second analysis without transcript | When you want quick feedback |
| **Load Trend** | Show your improvement over time | After logging 2+ interviews |
| **Generate Practice Questions** | AI creates 3 practice questions | After running Full Autopsy |

---

### **2. Interview Details (Left Panel)**

```
┌─────────────────────────────┐
│ Interview Details           │
│ ─────────────────           │
│ Required fields             │
│                             │
│ Company: Acme               │
│ Role: Frontend Engineer     │
│ Interview Round: Technical  │
│ Interviewer Vibe: Neutral   │
│                             │
│ Voice Notes / Debrief:      │
│ [Your thoughts here]        │
│                             │
│ Transcript / VTT:           │
│ [Paste transcript here]     │
│                             │
│ Audio URL: (Optional)       │
│ ☐ Use AssemblyAI            │
└─────────────────────────────┘
```

**What to fill in:**
- **Company:** Where you interviewed (e.g., "Google")
- **Role:** Position (e.g., "Backend Engineer")
- **Round:** Type of interview (Technical, HR, Manager, Screening)
- **Vibe:** Interviewer's demeanor (Friendly, Neutral, Cold, Hostile)
- **Voice Notes:** Your thoughts after the interview
- **Transcript:** Paste the interview conversation
- **Audio URL:** Link to recording (if using AssemblyAI)

---

### **3. Autopsy Results (Top Right Panel)**

```
┌──────────────────────────────────┐
│ Autopsy Results                  │
│ ───────────────                  │
│ Technical + Behavioral           │
│                                  │
│ Autopsy #25                      │
│ Overall Score: 64.14             │
│ Technical: 44.41                 │
│ Behavioral: 73.09                │
│ Recovery: 85                     │
│                                  │
│ ┌──────────────────────────────┐ │
│ │ 🎯 Practice Questions        │ │
│ │ Focus: technical (44.4/100)  │ │
│ │                              │ │
│ │ Q1: Design a distributed...  │ │
│ │ Q2: How would you handle...  │ │
│ │ Q3: Explain the trade-offs...│ │
│ └──────────────────────────────┘ │
│                                  │
│ ⚠ False confidence: system design│
│ Filler words: 8 | STAR: n/a      │
└──────────────────────────────────┘
```

**What you see:**
- **Overall Score:** Your interview performance (0-100)
- **Technical Accuracy:** How well you explained technical concepts
- **Behavioral Quality:** STAR format, storytelling, confidence
- **Recovery Readiness:** Your ability to bounce back
- **Practice Questions:** 3 AI-generated questions (after clicking button)
- **Warnings:** False confidence areas, filler words, STAR compliance

---

### **4. Growth Trend (Bottom Left Panel)**

```
┌─────────────────────────────┐
│ Growth Trend                │
│ ─────────────               │
│ Across interviews           │
│                             │
│ Overall delta: +10          │
│ Interviews tracked: 3       │
│ Forecast: rising-readiness  │
│ Expected offer: 6 weeks     │
│ Readiness score: 78.5       │
└─────────────────────────────┘
```

**What you see:**
- **Overall delta:** How much you've improved (e.g., +10 points)
- **Interviews tracked:** Number of interviews logged
- **Forecast:** Trend prediction (rising-readiness, plateau, declining)
- **Expected offer window:** When you'll likely get an offer
- **Readiness score:** Current interview readiness (0-100)

---

### **5. Recovery Actions (Bottom Right Panel)**

```
┌──────────────────────────────────┐
│ Recovery Actions                 │
│ ────────────────                 │
│ Emails, scripts, patches         │
│                                  │
│ ☑ Follow-up: Send within 24h    │
│   Subject: Thank you - Backend   │
│   [View full email template]     │
│                                  │
│ ☑ Study Plan: Distributed systems│
│   - Day 1: CAP theorem           │
│   - Day 2: Sharding vs replication│
│   - Day 3: Build Redis project   │
│                                  │
│ 💪 Resilience: This interview    │
│    produced diagnostic data      │
└──────────────────────────────────┘
```

**What you see:**
- **Follow-up email:** Template to send to interviewer
- **Study plan:** What to learn before next interview
- **Practice drills:** Exercises to improve weak areas
- **Resilience prompt:** Motivation to keep going

---

## 🔄 Complete Workflow

### **Step 1: Fill Interview Details**
1. Enter company, role, round, vibe
2. Write your voice notes
3. Paste transcript (optional)

### **Step 2: Run Full Autopsy**
1. Click "Run Full Autopsy" button
2. Wait 5-10 seconds
3. See scores appear in "Autopsy Results"

### **Step 3: Generate Practice Questions**
1. Click "Generate Practice Questions" button
2. Wait 3-5 seconds
3. See 3 questions appear in "Autopsy Results" panel

### **Step 4: Review Recovery Actions**
1. Scroll down to "Recovery Actions" panel
2. Copy follow-up email template
3. Review study plan
4. Check off actions as you complete them

### **Step 5: Track Progress**
1. Log your next interview
2. Click "Load Trend" to see improvement
3. Compare scores over time

---

## 💡 Quick Tips

### **Tip 1: Where to See Practice Questions**
- **Location:** "Autopsy Results" panel (top right)
- **Look for:** Purple 🎯 badge
- **Scroll:** May need to scroll up to see them

### **Tip 2: What Recovery Actions Do**
- **Follow-up emails:** Send within 24 hours
- **Study plans:** Complete before next interview
- **Resilience prompts:** Read when feeling discouraged

### **Tip 3: Use All Features Together**
1. Run Full Autopsy → Get scores
2. Generate Practice Questions → Practice them
3. Review Recovery Actions → Follow up
4. Load Trend → Track improvement

---

## 🎯 Summary

| Panel | Location | What It Shows |
|-------|----------|---------------|
| **Interview Details** | Top Left | Input form |
| **Autopsy Results** | Top Right | Scores + Practice Questions |
| **Growth Trend** | Bottom Left | Improvement over time |
| **Recovery Actions** | Bottom Right | Follow-up emails + Study plans |

---

**Now you know exactly how to use every part of Rebound! 🚀**
