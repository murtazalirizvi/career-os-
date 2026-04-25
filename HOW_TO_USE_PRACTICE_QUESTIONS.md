# 🎯 How to Use Practice Questions Feature

## 📍 Quick Start Guide

### **Step 1: Open Rebound Workspace**
1. Go to http://localhost:5500
2. Sign in (or use existing session)
3. Click **"Rebound"** in the left sidebar (microphone icon)

---

### **Step 2: Fill Interview Details**
Fill in the form on the left:

**Required Fields:**
- **Company:** e.g., "Google"
- **Role:** e.g., "Backend Engineer"
- **Interview Round:** Technical / Screening / HR / Manager
- **Interviewer Vibe:** Friendly / Neutral / Cold / Hostile

**Optional Fields:**
- **Voice Notes / Debrief:** Your thoughts after the interview
- **Transcript / VTT:** Paste interview transcript
- **Audio URL:** Link to interview recording (if using AssemblyAI)

**Example:**
```
Company: Google
Role: Backend Engineer
Round: Technical
Vibe: Neutral

Voice Notes:
"I was asked about system design. Struggled with the database scaling question. 
Didn't explain sharding vs replication clearly. Used too many filler words."

Transcript:
"Interviewer: How would you scale a database to handle 10x traffic?
Me: Um, I think we could use sharding... maybe partitioning? 
I'm not sure about the exact approach..."
```

---

### **Step 3: Run Full Autopsy**
1. Click **"Run Full Autopsy"** button (blue button at top)
2. Wait 5-10 seconds for AI analysis
3. See your scores appear in the "Autopsy Results" panel:
   - Overall Score: e.g., 64.14
   - Technical Accuracy: 44.41
   - Behavioral: 73.09
   - Recovery: 85

---

### **Step 4: Generate Practice Questions**
1. Click **"Generate Practice Questions"** button (gray button at top)
2. Wait 3-5 seconds for Gemini AI to generate questions
3. See practice questions appear in the "Autopsy Results" panel

**What You'll See:**
```
🎯 Practice Questions
Focus area: technical (score: 44.4/100)

Q1: Design a distributed cache system. Explain your consistency model 
    and trade-offs between CP and AP.

Q2: How would you handle database migrations with zero downtime in a 
    microservices architecture?

Q3: Explain the trade-offs between event-driven and request-response 
    patterns for inter-service communication.
```

---

### **Step 5: Practice!**
1. **Copy the questions** to a document
2. **Practice answering** each question out loud
3. **Time yourself** (aim for 3-5 minutes per question)
4. **Record your answers** (optional) to review later
5. **Compare with ideal answers** (Google the topics)

---

## 🎯 Understanding Your Results

### **Weakness Categories**

#### **1. Technical (Red Flag)**
**What it means:** You lacked depth in technical explanations

**Example Questions:**
- "Design a URL shortener with 1M requests/second"
- "Explain CAP theorem and when to choose CP vs AP"
- "How would you debug a memory leak in production?"

**How to Practice:**
- Study system design patterns
- Practice explaining trade-offs
- Use STAR format for technical stories

---

#### **2. Behavioral (Yellow Flag)**
**What it means:** Your storytelling needs work (STAR format)

**Example Questions:**
- "Tell me about a time you disagreed with your manager"
- "Describe a project where you had to convince the team"
- "Give an example of when you failed and how you recovered"

**How to Practice:**
- Write 5 STAR stories
- Quantify impact (numbers, percentages)
- Practice out loud

---

#### **3. Strategic (Orange Flag)**
**What it means:** You need better follow-up and negotiation skills

**Example Questions:**
- "How would you negotiate a higher salary?"
- "What questions would you ask the interviewer?"
- "How do you handle rejection and stay motivated?"

**How to Practice:**
- Prepare 5 questions for interviewers
- Practice salary negotiation scripts
- Study company research techniques

---

## 💡 Pro Tips

### **Tip 1: Run Multiple Autopsies**
- Log 3-5 interviews
- Click "Load Trend" to see improvement
- Generate practice questions after each one

### **Tip 2: Focus on Your Weakest Area**
- If technical score is lowest → Practice system design
- If behavioral score is lowest → Write STAR stories
- If strategic score is lowest → Practice negotiation

### **Tip 3: Use with Persona Play (Feature 4)**
1. Generate practice questions in Rebound
2. Go to Persona Play workspace
3. Practice answering with AI interviewer
4. Get real-time feedback!

### **Tip 4: Track Your Progress**
- Save practice questions to a document
- Mark questions as "practiced"
- Re-generate after improving your skills

---

## 🚨 Troubleshooting

### **Problem: Button is grayed out**
**Solution:** Run Full Autopsy first! Practice questions need your scores.

### **Problem: "Gemini API unavailable" error**
**Solution:** Check that `GEMINI_API_KEY` is set in `Backend/.env`

### **Problem: Questions are too generic**
**Solution:** Add more details to your interview notes and transcript

### **Problem: Same questions every time**
**Solution:** This is expected - questions are based on your weakness category

---

## 📊 Example Workflow

### **Interview 1: Google (Failed)**
1. Run autopsy → Technical: 44/100
2. Generate questions → Get 3 system design questions
3. Practice for 1 week
4. Study distributed systems

### **Interview 2: Meta (Passed to Round 2)**
1. Run autopsy → Technical: 68/100 (improved!)
2. Generate questions → Get 3 advanced questions
3. Practice for 3 days

### **Interview 3: Stripe (Offer!)**
1. Run autopsy → Technical: 85/100 (ready!)
2. No practice needed - you're interview-ready! 🎉

---

## 🎯 Success Metrics

**You're ready when:**
- ✅ Technical score > 75
- ✅ Behavioral score > 80
- ✅ Strategic score > 70
- ✅ Can answer practice questions in < 5 minutes
- ✅ No filler words ("um", "like", "you know")

---

## 🚀 Next Steps

1. **Practice the questions** (30 minutes/day)
2. **Log your next interview** in Rebound
3. **Compare scores** - are you improving?
4. **Repeat** until you get offers! 🎉

---

**Remember:** Practice makes perfect! The more you practice, the better you'll perform in real interviews. Good luck! 🍀
