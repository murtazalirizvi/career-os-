# 🎯 The Rebound - Complete User Guide

## 📖 Table of Contents
1. [What is The Rebound?](#what-is-the-rebound)
2. [Where to Find Everything](#where-to-find-everything)
3. [All 4 Buttons Explained](#all-4-buttons-explained)
4. [Where Practice Questions Appear](#where-practice-questions-appear)
5. [What Recovery Actions Do](#what-recovery-actions-do)
6. [Step-by-Step Workflow](#step-by-step-workflow)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 What is The Rebound?

**The Rebound** is your AI-powered post-interview autopsy tool. It analyzes your interview performance and provides:

✅ **Technical Accuracy Score** - How well you answered technical questions  
✅ **Behavioral Quality Score** - STAR format, storytelling, impact  
✅ **Strategic Recovery Readiness** - Your follow-up potential  
✅ **Practice Questions** - 3 AI-generated questions targeting your weakest area  
✅ **Recovery Actions** - Follow-up emails, study plans, negotiation scripts  
✅ **Growth Trend** - Track improvement over multiple interviews  

---

## 📍 Where to Find Everything

### Full Screen Layout:

```
┌──────────────────────────────────────────────────────────────────┐
│  Career OS                                    [User] [Logout]    │
├──────────────────────────────────────────────────────────────────┤
│  The Rebound                                                     │
│  Post-interview autopsy — technical accuracy, behavioral...      │
│                                                                  │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Generate...] │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ┌────────────────────────┬─────────────────────────────────┐  │
│  │ 1. Interview Details   │ 2. Autopsy Results              │  │
│  │    ─────────────────   │    ───────────────              │  │
│  │                        │                                 │  │
│  │ Company: [input]       │ Overall Score: 64.14            │  │
│  │ Role: [input]          │ Technical: 44.41                │  │
│  │ Round: [dropdown]      │ Behavioral: 73.09               │  │
│  │ Vibe: [dropdown]       │ Recovery: 85                    │  │
│  │                        │                                 │  │
│  │ Voice Notes:           │ ⚠ False confidence zones        │  │
│  │ [textarea]             │ Filler words: 8                 │  │
│  │                        │                                 │  │
│  │ Transcript:            │ 🎯 Practice Questions           │  │
│  │ [textarea]             │ Focus: technical (44.4/100)     │  │
│  │                        │ Q1: Design a distributed...     │  │
│  │ Audio URL: [input]     │ Q2: How would you handle...     │  │
│  │ ☐ Use AssemblyAI       │ Q3: Explain the trade-offs...   │  │
│  │                        │                                 │  │
│  └────────────────────────┴─────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────┬─────────────────────────────────┐  │
│  │ 3. Growth Trend        │ 4. Recovery Actions             │  │
│  │    ─────────────       │    ────────────────             │  │
│  │                        │                                 │  │
│  │ Overall delta: +12.5   │ ☑ Follow-up Email:              │  │
│  │ Technical: +8.3        │ "Dear [Interviewer],            │  │
│  │ Behavioral: +15.2      │ Thank you for..."               │  │
│  │ Strategic: +14.1       │                                 │  │
│  │ Interviews: 4          │ ☑ Study Plan:                   │  │
│  │                        │ "Focus on system design..."     │  │
│  │                        │                                 │  │
│  │                        │ ☑ Resilience Prompt:            │  │
│  │                        │ "Every interview is practice"   │  │
│  │                        │                                 │  │
│  └────────────────────────┴─────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Panel Locations:
1. **Interview Details** - Top-left (input fields)
2. **Autopsy Results** - Top-right (scores + practice questions)
3. **Growth Trend** - Bottom-left (progress tracking)
4. **Recovery Actions** - Bottom-right (follow-up emails, study plans)

---

## 🔘 All 4 Buttons Explained

### Button 1: Run Full Autopsy

**What it does:** Complete AI analysis of your interview performance

**Requirements:**
- Company name
- Role name
- Interview round (Technical/Behavioral/Final)
- Interviewer vibe (Friendly/Neutral/Tough)
- Voice notes/debrief OR transcript

**What you get:**
- Overall score (0-100)
- Technical accuracy score
- Behavioral quality score
- Strategic recovery readiness
- False confidence zones
- Filler word count
- Recovery actions

**Time:** 30-60 seconds

---

### Button 2: Quick Debrief

**What it does:** Fast 30-second analysis without full autopsy

**Requirements:**
- Just your notes or transcript (no other fields required)

**What you get:**
- Hardest question identified
- Immediate action tip
- Overall sentiment

**Use case:** When you're in a hurry or want instant feedback

---

### Button 3: Load Trend

**What it does:** Shows your performance over time across multiple interviews

**Requirements:**
- At least 2 completed autopsies
- Uses your Candidate ID

**What you get:**
- Overall delta (improvement score)
- Technical trend
- Behavioral trend
- Strategic trend
- Interview count

**Use case:** Track improvement after 3-4 interviews

---

### Button 4: Generate Practice Questions

**What it does:** Creates 3 AI-powered practice questions targeting your weakest area

**Requirements:**
- Must run "Full Autopsy" first
- AI identifies your lowest score dimension

**What you get:**
- 3 progressively challenging questions
- Focus area (technical/behavioral/strategic)
- Weakness score
- Questions tailored to your role

**Time:** 5-10 seconds

---

## 📍 Where Practice Questions Appear

### Location: "Autopsy Results" Panel (Top-Right)

Practice questions appear **BELOW** the autopsy scores with **purple styling**:

```
┌─────────────────────────────────────┐
│  Autopsy Results                    │
│  ───────────────                    │
│                                     │
│  Autopsy #25                        │
│  Overall Score: 64.14               │
│  Technical: 44.41                   │
│  Behavioral: 73.09                  │
│  Recovery: 85                       │
│                                     │
│  ⚠ False confidence: system design  │
│  Filler words: 8 | STAR: n/a        │
│                                     │
│  ┌──────────────────────────────┐   │
│  │ 🎯 Practice Questions        │   │
│  │ ─────────────────────        │   │
│  │ Focus area: technical        │   │
│  │ (score: 44.4/100)            │   │
│  │                              │   │
│  │ Q1: Design a distributed     │   │
│  │ caching system that handles  │   │
│  │ 1M requests/sec...           │   │
│  │                              │   │
│  │ Q2: How would you handle     │   │
│  │ race conditions in a         │   │
│  │ multi-threaded environment...│   │
│  │                              │   │
│  │ Q3: Explain the trade-offs   │   │
│  │ between SQL and NoSQL for    │   │
│  │ a social media feed...       │   │
│  └──────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
        ↑
   QUESTIONS APPEAR HERE!
```

### Visual Indicators:
- **Purple border** on the left
- **Purple heading** "🎯 Practice Questions"
- **Purple text** for question numbers
- **Light purple background**

---

## 🔄 What Recovery Actions Do

### Location: "Recovery Actions" Panel (Bottom-Right)

Recovery actions are your **post-interview playbook** with 5 key components:

### 1. Follow-Up Email Template 📧
**Purpose:** Send to interviewer within 24 hours  
**Content:** Professional thank-you email with specific interview details  
**Why:** Shows professionalism, keeps you top-of-mind, can turn "maybe" into "yes"

### 2. Clarification Script 💬
**Purpose:** Address questions you struggled with  
**Content:** Better answer to weak questions with technical depth  
**Why:** Shows you can learn from mistakes, demonstrates growth mindset

### 3. Study Plan / Patch 📚
**Purpose:** Fix knowledge gaps in your weakest area  
**Content:** 7-day study plan with specific topics and resources  
**Why:** Turns weaknesses into strengths, prevents repeating mistakes

### 4. Negotiation Guide 💰
**Purpose:** Maximize compensation if you get an offer  
**Content:** Scripts, leverage points, non-salary negotiables  
**Why:** Prevents leaving money on the table, shows confidence

### 5. Resilience Prompt 💪
**Purpose:** Stay motivated after rejection or tough interviews  
**Content:** Motivational message reframing failure as learning  
**Why:** Prevents discouragement, keeps you applying

---

## 🚀 Step-by-Step Workflow

### Workflow 1: After Your Interview (Full Analysis)

```
Step 1: Fill in Interview Details
├─ Company: Acme Corp
├─ Role: Frontend Engineer
├─ Round: Technical
├─ Vibe: Neutral
└─ Notes: "I struggled with system design questions..."

Step 2: Click "Run Full Autopsy"
└─ Wait 30-60 seconds for AI analysis

Step 3: Review Autopsy Results (Top-Right Panel)
├─ Overall Score: 64.14
├─ Technical: 44.41 ⚠ WEAK!
├─ Behavioral: 73.09 ✅ STRONG
└─ Recovery: 85 ✅ STRONG

Step 4: Click "Generate Practice Questions"
└─ Wait 5-10 seconds for AI generation

Step 5: Review Practice Questions (Top-Right Panel)
├─ Focus: technical (44.4/100)
├─ Q1: Design a distributed caching system...
├─ Q2: How would you handle race conditions...
└─ Q3: Explain SQL vs NoSQL trade-offs...

Step 6: Review Recovery Actions (Bottom-Right Panel)
├─ Follow-up email: Send within 24h
├─ Study plan: 7-day system design focus
└─ Resilience prompt: Stay motivated

Step 7: Take Action
├─ Send follow-up email (within 24h)
├─ Start study plan (within 48h)
└─ Practice questions (within 1 week)
```

---

### Workflow 2: Quick Feedback (Fast Analysis)

```
Step 1: Add Notes or Transcript
└─ "I struggled with the caching question..."

Step 2: Click "Quick Debrief"
└─ Wait 10-20 seconds

Step 3: Review Quick Results (Top-Right Panel)
├─ Hardest question: "Design a caching system"
├─ Immediate action: "Study distributed systems"
└─ Sentiment: Neutral

Step 4: Decide Next Steps
├─ If helpful: Run Full Autopsy for deeper analysis
└─ If sufficient: Move on to next interview
```

---

### Workflow 3: Track Progress (Multiple Interviews)

```
Step 1: Complete 2+ Full Autopsies
├─ Interview 1: Overall 64.14
├─ Interview 2: Overall 72.50
└─ Interview 3: Overall 78.25

Step 2: Click "Load Trend"
└─ Wait 5 seconds

Step 3: Review Growth Trend (Bottom-Left Panel)
├─ Overall delta: +14.11 ✅ IMPROVING!
├─ Technical: +18.3 ✅ STRONG GROWTH
├─ Behavioral: +12.5 ✅ STEADY GROWTH
└─ Interviews: 3

Step 4: Celebrate & Adjust
├─ Celebrate improvements
├─ Focus on remaining weak areas
└─ Continue applying study plans
```

---

## ⚠️ Troubleshooting

### Problem 1: "I don't see practice questions!"

**Solutions:**
1. ✅ Run "Full Autopsy" first (required)
2. ✅ Click "Generate Practice Questions" button
3. ✅ Wait 5-10 seconds for AI generation
4. ✅ Scroll down in "Autopsy Results" panel
5. ✅ Check you're looking in the RIGHT panel (top-right, not top-left)

---

### Problem 2: "Button is grayed out"

**Solutions:**
- **Run Full Autopsy:** Fill in all required fields first
- **Quick Debrief:** Add notes or transcript first
- **Load Trend:** Complete at least 2 autopsies first
- **Generate Practice Questions:** Run Full Autopsy first

---

### Problem 3: "Autopsy failed"

**Solutions:**
1. ✅ Check you filled in ALL required fields:
   - Company name
   - Role name
   - Interview round
   - Interviewer vibe
   - Notes OR transcript (at least one)
2. ✅ Check backend is running (http://localhost:8000)
3. ✅ Check Gemini API key is set in Backend/.env
4. ✅ Try again (sometimes API is temporarily unavailable)

---

### Problem 4: "Recovery actions are empty"

**Solutions:**
- Recovery actions only appear AFTER running Full Autopsy
- If still empty, check backend logs for errors
- Ensure Gemini API is working (test with Quick Debrief)

---

### Problem 5: "Trend shows no data"

**Solutions:**
- You need at least 2 completed autopsies
- Ensure you're using the same Candidate ID for all interviews
- Check that autopsies were saved successfully (check database)

---

## 💡 Pro Tips

### Tip 1: Use All Features Together
Don't just run autopsy - use the full workflow:
1. Run Full Autopsy
2. Generate Practice Questions
3. Review Recovery Actions
4. Send Follow-Up Email
5. Complete Study Plan
6. Track Progress with Load Trend

### Tip 2: Practice Questions Out Loud
- Don't just read practice questions
- Answer them out loud
- Record yourself
- Time yourself (2-3 minutes per question)
- Compare to your original interview answers

### Tip 3: Customize Recovery Actions
- Don't copy-paste follow-up email verbatim
- Add specific details from your interview
- Personalize study plan based on your learning style
- Share your progress on LinkedIn

### Tip 4: Track Trends Early
- Start tracking after 2-3 interviews
- Look for patterns (e.g., technical always low)
- Use delta scores to measure improvement velocity
- Celebrate wins, focus on weak areas

### Tip 5: Use Quick Debrief for Phone Screens
- Full Autopsy is overkill for 15-minute phone screens
- Quick Debrief gives instant feedback
- Save Full Autopsy for technical/final rounds

---

## 📊 Success Metrics

### Track These Over Time:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Overall Score** | 75+ | Run Full Autopsy |
| **Technical Score** | 70+ | Run Full Autopsy |
| **Behavioral Score** | 75+ | Run Full Autopsy |
| **Filler Words** | <5 | Run Full Autopsy |
| **Follow-Up Response Rate** | 50%+ | Track email replies |
| **Offer Rate** | 20%+ | Track offers received |
| **Score Improvement** | +10/month | Use Load Trend |

---

## 🎯 Quick Reference

### When to Use Each Button:

| Button | When to Use | Time Required |
|--------|-------------|---------------|
| **Run Full Autopsy** | After every important interview | 30-60 sec |
| **Quick Debrief** | After phone screens or quick rounds | 10-20 sec |
| **Load Trend** | After 2+ interviews to track progress | 5 sec |
| **Generate Practice Questions** | After Full Autopsy to practice | 5-10 sec |

### Where to Find Each Feature:

| Feature | Location | Panel |
|---------|----------|-------|
| **Autopsy Scores** | Top-right | Autopsy Results |
| **Practice Questions** | Top-right | Autopsy Results (below scores) |
| **Recovery Actions** | Bottom-right | Recovery Actions |
| **Growth Trend** | Bottom-left | Growth Trend |
| **Input Fields** | Top-left | Interview Details |

---

## 📚 Additional Resources

For more detailed guides, see:
- **REBOUND_BUTTONS_EXPLAINED.md** - Deep dive into each button
- **PRACTICE_QUESTIONS_LOCATION.md** - Visual guide to finding practice questions
- **RECOVERY_ACTIONS_EXPLAINED.md** - Complete explanation of recovery actions
- **Feature2_API_Examples.md** - API documentation for developers

---

## 🎓 Summary

**The Rebound is your complete post-interview toolkit:**

1. **Run Full Autopsy** → Get comprehensive analysis
2. **Generate Practice Questions** → Practice your weak areas
3. **Review Recovery Actions** → Follow up and improve
4. **Load Trend** → Track progress over time

**Remember:** The best candidates aren't those who never fail - they're the ones who learn fastest from failure.

---

**Last Updated:** April 25, 2026  
**Feature:** The Rebound (Feature 2 - Interview Autopsy)  
**Version:** 2.0
