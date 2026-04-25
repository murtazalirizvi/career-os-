<!-- we are good - practice questions location guide documented -->
# 📍 Where to See Practice Questions

## 🎯 Quick Answer

**Practice questions appear in the "Autopsy Results" panel** on the right side of the Rebound workspace after you:
1. Run Full Autopsy
2. Click "Generate Practice Questions"

---

## 📺 Visual Guide

### **Your Current Screen:**

```
┌─────────────────────────────────────────────────────────────────┐
│  The Rebound                                                    │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Generate...] │
├──────────────────────────┬──────────────────────────────────────┤
│                          │                                      │
│  Interview Details       │  Autopsy Results  ← LOOK HERE!      │
│  ─────────────────       │  ───────────────                    │
│                          │                                      │
│  Company: Acme           │  Running interview autopsy...        │
│  Role: Frontend Engineer │  Analyzing technical accuracy...     │
│                          │                                      │
│  [Voice Notes]           │                                      │
│  [Transcript]            │                                      │
│                          │                                      │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## 🔄 Step-by-Step: Where Questions Appear

### **Step 1: Before Running Autopsy**
```
┌─────────────────────────────────────┐
│  Autopsy Results                    │
│  ───────────────                    │
│                                     │
│  Run Full Autopsy to see results   │
│                                     │
└─────────────────────────────────────┘
```

---

### **Step 2: After Running Autopsy**
```
┌─────────────────────────────────────┐
│  Autopsy Results                    │
│  ───────────────                    │
│                                     │
│  Autopsy #25                        │
│  Overall Score: 64.14               │
│  Technical: 44.41 | Behavioral: 73  │
│  ⚠ False confidence: system design  │
│  Filler words: 8 | STAR: n/a        │
│                                     │
└─────────────────────────────────────┘
```

---

### **Step 3: After Clicking "Generate Practice Questions"**
```
┌─────────────────────────────────────────────────────────┐
│  Autopsy Results                                        │
│  ───────────────                                        │
│                                                         │
│  Autopsy #25                                            │
│  Overall Score: 64.14                                   │
│  Technical: 44.41 | Behavioral: 73.09                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🎯 Practice Questions                           │   │
│  │ Focus area: technical (score: 44.4/100)         │   │
│  │                                                  │   │
│  │ Q1: Design a distributed cache system.          │   │
│  │     Explain your consistency model and          │   │
│  │     trade-offs between CP and AP.               │   │
│  │                                                  │   │
│  │ Q2: How would you handle database migrations    │   │
│  │     with zero downtime in a microservices       │   │
│  │     architecture?                               │   │
│  │                                                  │   │
│  │ Q3: Explain the trade-offs between event-driven │   │
│  │     and request-response patterns for           │   │
│  │     inter-service communication.                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**👆 THIS IS WHERE YOU SEE THE QUESTIONS!**

---

## 🎨 Visual Indicators

### **Look for these visual cues:**

1. **Purple Badge:** 🎯 Practice Questions
2. **Purple Left Border:** On each question
3. **Focus Area:** Shows your weakness (technical/behavioral/strategic)
4. **Score:** Shows your weakness score (e.g., 44.4/100)
5. **Numbered Questions:** Q1, Q2, Q3

---

## 📱 Full Screen Layout

```
┌────────────────────────────────────────────────────────────────────────┐
│  Career OS                                                             │
├──┬────────────────────────────────────────────────────────────────────┤
│☰ │  The Rebound                                                       │
│  │  Post-interview autopsy — technical accuracy, behavioral critique  │
│📊│                                                                     │
│  │  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Generate...]    │
│📤│  ─────────────────────────────────────────────────────────────────│
│  │                                                                     │
│🔍│  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │  │ Interview Details    │  │ Autopsy Results                  │  │
│🎤│  │ ──────────────────   │  │ ───────────────                  │  │
│  │  │                      │  │                                  │  │
│📈│  │ Company: Acme        │  │ Autopsy #25                      │  │
│  │  │ Role: Frontend Eng   │  │ Overall Score: 64.14             │  │
│🎭│  │                      │  │                                  │  │
│  │  │ [Voice Notes]        │  │ 🎯 Practice Questions            │  │
│📖│  │ [Transcript]         │  │ Focus: technical (44.4/100)      │  │
│  │  │                      │  │                                  │  │
│🚪│  │                      │  │ Q1: Design a distributed...      │  │
│  │  │                      │  │ Q2: How would you handle...      │  │
│  │  │                      │  │ Q3: Explain the trade-offs...    │  │
│  │  └──────────────────────┘  └──────────────────────────────────┘  │
│  │                                                                     │
│  │  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │  │ Growth Trend         │  │ Recovery Actions                 │  │
│  │  └──────────────────────┘  └──────────────────────────────────┘  │
└──┴────────────────────────────────────────────────────────────────────┘
```

**Practice Questions appear in the TOP RIGHT panel** labeled "Autopsy Results"

---

## 🔍 Can't See Them? Troubleshooting

### **Problem 1: Questions not appearing**
**Solution:** 
1. Make sure you clicked "Run Full Autopsy" FIRST
2. Wait for autopsy to complete (5-10 seconds)
3. THEN click "Generate Practice Questions"
4. Wait 3-5 seconds for AI to generate

### **Problem 2: Button is grayed out**
**Solution:** Run Full Autopsy first! The button only works after you have autopsy scores.

### **Problem 3: Error message appears**
**Solution:** Check that `GEMINI_API_KEY` is set in `Backend/.env`

### **Problem 4: Panel is scrolled down**
**Solution:** Scroll up in the "Autopsy Results" panel to see the questions at the top

---

## 💡 Pro Tip: Copy Questions

**To save the questions:**
1. Select the question text with your mouse
2. Right-click → Copy
3. Paste into a document (Notion, Google Docs, etc.)
4. Practice answering them!

---

## 📊 What You'll See

### **Example Output:**
```
🎯 Practice Questions
Focus area: technical (score: 44.4/100)

Q1: Design a distributed cache system. Explain your consistency 
    model and trade-offs between CP and AP.

Q2: How would you handle database migrations with zero downtime 
    in a microservices architecture?

Q3: Explain the trade-offs between event-driven and request-response 
    patterns for inter-service communication.
```

---

## 🎯 Summary

**Location:** Rebound workspace → Autopsy Results panel (top right)  
**When:** After running Full Autopsy + clicking Generate Practice Questions  
**Look for:** Purple 🎯 badge and left border  
**Scroll:** May need to scroll up in the panel to see them  

---

**Now you know exactly where to find your practice questions! 🎉**
