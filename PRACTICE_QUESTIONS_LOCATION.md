# 📍 Where to See Practice Questions - Visual Guide

## 🎯 Quick Answer

Practice questions appear in the **"Autopsy Results"** panel (top-right) **AFTER** you:
1. ✅ Run Full Autopsy
2. ✅ Click "Generate Practice Questions"

---

## 📺 Step-by-Step Visual Guide

### Step 1: Before Running Autopsy

```
┌────────────────────────────────────────────────────────────┐
│  The Rebound                                               │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Gen...] │
├──────────────────────────┬─────────────────────────────────┤
│                          │                                 │
│  Interview Details       │  Autopsy Results                │
│  ─────────────────       │  ───────────────                │
│                          │                                 │
│  Company: [input]        │  Run Full Autopsy to see        │
│  Role: [input]           │  results                        │
│                          │                                 │
└──────────────────────────┴─────────────────────────────────┘
```

**Status:** Empty - need to run autopsy first

---

### Step 2: After Running Full Autopsy

```
┌────────────────────────────────────────────────────────────┐
│  The Rebound                                               │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Gen...] │
│                                      ↑ CLICK THIS NEXT     │
├──────────────────────────┬─────────────────────────────────┤
│                          │                                 │
│  Interview Details       │  Autopsy Results                │
│  ─────────────────       │  ───────────────                │
│                          │                                 │
│  Company: Acme Corp      │  Autopsy #25                    │
│  Role: Frontend Engineer │  Overall Score: 64.14           │
│  Round: Technical        │  Technical: 44.41 ⚠ WEAK!      │
│  Vibe: Neutral           │  Behavioral: 73.09              │
│                          │  Recovery: 85                   │
│  Voice Notes:            │                                 │
│  "I struggled with       │  ⚠ False confidence:            │
│   system design..."      │  system design, caching         │
│                          │                                 │
│                          │  Filler words: 8                │
│                          │  STAR compliance: n/a           │
│                          │                                 │
└──────────────────────────┴─────────────────────────────────┘
```

**Status:** Autopsy complete - now click "Generate Practice Questions"

---

### Step 3: After Clicking "Generate Practice Questions"

```
┌────────────────────────────────────────────────────────────┐
│  The Rebound                                               │
│  [Run Full Autopsy] [Quick Debrief] [Load Trend] [Gen...] │
├──────────────────────────┬─────────────────────────────────┤
│                          │                                 │
│  Interview Details       │  Autopsy Results                │
│  ─────────────────       │  ───────────────                │
│                          │                                 │
│  Company: Acme Corp      │  Autopsy #25                    │
│  Role: Frontend Engineer │  Overall Score: 64.14           │
│  Round: Technical        │  Technical: 44.41               │
│  Vibe: Neutral           │  Behavioral: 73.09              │
│                          │  Recovery: 85                   │
│  Voice Notes:            │                                 │
│  "I struggled with       │  ⚠ False confidence:            │
│   system design..."      │  system design, caching         │
│                          │                                 │
│                          │  Filler words: 8                │
│                          │                                 │
│                          │  ┌──────────────────────────┐   │
│                          │  │ 🎯 Practice Questions    │   │
│                          │  │ ─────────────────────    │   │
│                          │  │ Focus area: technical    │   │
│                          │  │ (score: 44.4/100)        │   │
│                          │  │                          │   │
│                          │  │ Q1: Design a distributed │   │
│                          │  │ caching system that      │   │
│                          │  │ handles 1M requests/sec. │   │
│                          │  │ How would you ensure     │   │
│                          │  │ consistency?             │   │
│                          │  │                          │   │
│                          │  │ Q2: How would you handle │   │
│                          │  │ race conditions in a     │   │
│                          │  │ multi-threaded web       │   │
│                          │  │ server?                  │   │
│                          │  │                          │   │
│                          │  │ Q3: Explain the          │   │
│                          │  │ trade-offs between SQL   │   │
│                          │  │ and NoSQL for a social   │   │
│                          │  │ media feed.              │   │
│                          │  └──────────────────────────┘   │
│                          │                                 │
└──────────────────────────┴─────────────────────────────────┘
                                    ↑
                              QUESTIONS APPEAR HERE!
```

**Status:** ✅ Practice questions generated and displayed!

---

## 🎨 Visual Styling

Practice questions have **distinctive purple styling**:
- **Purple border** on the left side
- **Purple heading** "🎯 Practice Questions"
- **Purple text** for question numbers (Q1, Q2, Q3)
- **Light purple background**

This makes them easy to spot in the Autopsy Results panel!

---

## 📱 On Smaller Screens

On mobile or smaller screens, the layout stacks vertically:

```
┌─────────────────────────────┐
│  Interview Details          │
│  ─────────────────          │
│  Company: Acme Corp         │
│  Role: Frontend Engineer    │
└─────────────────────────────┘

┌─────────────────────────────┐
│  Autopsy Results            │
│  ───────────────            │
│  Overall Score: 64.14       │
│  Technical: 44.41           │
│                             │
│  🎯 Practice Questions      │
│  Focus: technical (44.4)    │
│                             │
│  Q1: Design a distributed...│
│  Q2: How would you handle...│
│  Q3: Explain the trade-offs.│
└─────────────────────────────┘
```

---

## ⚠️ Troubleshooting

### "I don't see practice questions!"

**Check these:**
1. ✅ Did you run "Full Autopsy" first?
2. ✅ Did you click "Generate Practice Questions"?
3. ✅ Did you wait 5-10 seconds for AI generation?
4. ✅ Are you looking in the **right panel** (Autopsy Results, not Interview Details)?

### "I see autopsy results but no questions"

**Solution:** Click the **"Generate Practice Questions"** button in the top-right header.

### "Button is grayed out"

**Solution:** Run "Full Autopsy" first. Practice questions need autopsy scores to identify your weakest area.

---

## 🎯 Exact Location Summary

| Element | Location |
|---------|----------|
| **Button** | Top-right header, 4th button |
| **Results** | "Autopsy Results" panel (top-right quadrant) |
| **Position** | Below autopsy scores, above recovery actions |
| **Styling** | Purple border, purple heading, purple text |

---

## 🚀 Pro Tip

**Scroll down** in the Autopsy Results panel if you don't see practice questions immediately. On smaller screens or with long autopsy results, you may need to scroll to see them.

---

**Last Updated:** April 25, 2026
**Feature:** Rebound Practice Questions
