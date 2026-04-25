<!-- we are good - Rebound buttons explained -->
# 🎯 Rebound Buttons - Complete Guide

## 📍 Where Are These Buttons?

All buttons are located in the **top-right header** of the Rebound workspace:

```
┌────────────────────────────────────────────────────────────────┐
│  The Rebound                                                   │
│  Post-interview autopsy — technical accuracy, behavioral...    │
│                                                                │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Generate...] │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔘 Button 1: Run Full Autopsy

### What It Does:
Performs a **complete AI-powered analysis** of your interview performance.

### Requirements:
- Company name
- Role name
- Interview round (Technical/Behavioral/Final)
- Interviewer vibe (Friendly/Neutral/Tough)
- **Either** voice notes/debrief **OR** transcript

### What You Get:
✅ **Overall Score** (0-100)
✅ **Technical Accuracy Score** - How well you answered technical questions
✅ **Behavioral Quality Score** - STAR format, storytelling, impact
✅ **Strategic Recovery Readiness** - Your follow-up potential
✅ **False Confidence Zones** - Topics you thought you knew but didn't
✅ **Filler Word Count** - "Um", "like", "you know"
✅ **Recovery Actions** - Follow-up emails, study plans, negotiation scripts

### Where Results Appear:
**"Autopsy Results"** panel (top-right)

---

## 🔘 Button 2: Quick Debrief

### What It Does:
Provides a **fast 30-second analysis** without full autopsy.

### Requirements:
- Just your notes or transcript (no other fields required)

### What You Get:
✅ **Hardest Question** - AI extracts the toughest question you faced
✅ **Immediate Action** - One quick tip to improve next time
✅ **Sentiment** - Overall vibe (positive/neutral/negative)

### Use Case:
- When you're in a hurry
- When you want quick feedback without full analysis
- When you just finished an interview and want instant insights

### Where Results Appear:
**"Autopsy Results"** panel (top-right) - shows "Quick Debrief" section

---

## 🔘 Button 3: Load Trend

### What It Does:
Shows your **interview performance over time** across multiple interviews.

### Requirements:
- You must have completed at least 2 full autopsies
- Uses your Candidate ID to track history

### What You Get:
✅ **Overall Delta** - How much you've improved (+/- points)
✅ **Technical Trend** - Technical score progression
✅ **Behavioral Trend** - Behavioral score progression
✅ **Strategic Trend** - Recovery readiness progression
✅ **Interview Count** - Total interviews analyzed

### Use Case:
- Track your improvement over weeks/months
- See which areas are improving vs. declining
- Motivate yourself with progress data

### Where Results Appear:
**"Growth Trend"** panel (bottom-left)

---

## 🔘 Button 4: Generate Practice Questions

### What It Does:
Creates **3 AI-powered practice questions** targeting your **weakest area**.

### Requirements:
- You must run "Full Autopsy" first
- AI identifies your lowest score (technical/behavioral/strategic)

### What You Get:
✅ **3 Targeted Questions** - Progressively challenging
✅ **Focus Area** - Which dimension needs work (e.g., "technical")
✅ **Weakness Score** - Your current score in that area
✅ **Realistic Questions** - Tailored to your role (Frontend Engineer, PM, etc.)

### Example Output:
```
🎯 Practice Questions
Focus area: technical (score: 44.4/100)

Q1: Design a distributed caching system that handles 1M requests/sec...
Q2: How would you handle race conditions in a multi-threaded environment...
Q3: Explain the trade-offs between SQL and NoSQL for a social media feed...
```

### Where Results Appear:
**"Autopsy Results"** panel (top-right) - appears **below** the autopsy scores with purple styling

---

## 📍 Visual Layout - Where Everything Appears

```
┌──────────────────────────────────────────────────────────────────┐
│  The Rebound                                                     │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Generate...]  │
├────────────────────────────┬─────────────────────────────────────┤
│                            │                                     │
│  Interview Details         │  Autopsy Results  ← LOOK HERE!     │
│  ─────────────────         │  ───────────────                   │
│                            │                                     │
│  Company: [input]          │  Autopsy #25                        │
│  Role: [input]             │  Overall Score: 64.14               │
│  Round: [dropdown]         │  Technical: 44.41                   │
│  Vibe: [dropdown]          │  Behavioral: 73.09                  │
│                            │  Recovery: 85                       │
│  Voice Notes:              │                                     │
│  [textarea]                │  ⚠ False confidence: system design  │
│                            │  Filler words: 8 | STAR: n/a        │
│  Transcript:               │                                     │
│  [textarea]                │  ┌────────────────────────────────┐ │
│                            │  │ 🎯 Practice Questions          │ │
│                            │  │ Focus: technical (44.4/100)    │ │
│                            │  │                                │ │
│                            │  │ Q1: Design a distributed...    │ │
│                            │  │ Q2: How would you handle...    │ │
│                            │  │ Q3: Explain the trade-offs...  │ │
│                            │  └────────────────────────────────┘ │
│                            │                                     │
├────────────────────────────┼─────────────────────────────────────┤
│                            │                                     │
│  Growth Trend              │  Recovery Actions                   │
│  ─────────────             │  ────────────────                   │
│                            │                                     │
│  Overall delta: +12.5      │  ☑ Follow-up Email:                │
│  Technical: +8.3           │  "Dear [Interviewer],               │
│  Behavioral: +15.2         │  Thank you for the opportunity..."  │
│  Strategic: +14.1          │                                     │
│  Interviews: 4             │  ☑ Study Plan:                      │
│                            │  "Focus on system design patterns"  │
│                            │                                     │
│                            │  ☑ Resilience Prompt:               │
│                            │  "Every interview is practice..."   │
│                            │                                     │
└────────────────────────────┴─────────────────────────────────────┘
```

---

## 🎯 Recommended Workflow

### Step 1: After Your Interview
1. Fill in Company, Role, Round, Vibe
2. Add your notes or transcript
3. Click **"Run Full Autopsy"**
4. Wait 30-60 seconds for AI analysis

### Step 2: Review Results
1. Check your scores in **"Autopsy Results"** panel
2. Read false confidence zones and filler word count
3. Review recovery actions in **"Recovery Actions"** panel

### Step 3: Practice
1. Click **"Generate Practice Questions"**
2. Practice answering the 3 questions
3. Record yourself and analyze again

### Step 4: Track Progress
1. After 2+ interviews, click **"Load Trend"**
2. See your improvement over time
3. Celebrate wins, focus on weak areas

---

## 🚀 Pro Tips

### For Quick Debrief:
- Use immediately after interview while memory is fresh
- Great for phone screens or quick rounds
- Helps identify hardest question for deeper study

### For Practice Questions:
- Practice out loud, not just in your head
- Record yourself answering
- Time yourself (2-3 minutes per question)
- Compare your answer to what you said in the original interview

### For Load Trend:
- Do at least 3-4 interviews before checking trend
- Look for patterns (e.g., technical always low)
- Use delta scores to measure improvement velocity

---

## ❓ Common Questions

**Q: Why don't I see practice questions?**
A: You must run "Full Autopsy" first. Practice questions need autopsy scores to identify your weakest area.

**Q: Can I generate practice questions multiple times?**
A: Yes! Each time you click, AI generates new questions based on your current weakest dimension.

**Q: What if Quick Debrief and Full Autopsy give different results?**
A: Quick Debrief is a fast approximation. Full Autopsy is comprehensive and more accurate.

**Q: How many interviews do I need for Load Trend?**
A: Minimum 2, but 3-4 gives better trend visualization.

**Q: Where are Recovery Actions?**
A: Bottom-right panel. They include follow-up emails, study plans, and resilience prompts.

---

## 🎨 Visual Indicators

- **Purple border** = Practice Questions
- **Red/Orange** = False confidence zones or weak areas
- **Green** = Good scores (70+)
- **Blue** = Resilience prompts and strategic actions

---

**Last Updated:** April 25, 2026
**Feature:** Rebound (Feature 2 - Interview Autopsy)
