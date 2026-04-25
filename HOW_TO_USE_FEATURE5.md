# How to Use Feature 5 (Portfolio Narrator) - Your Own Tool

## The Problem
The external "Narrative Architect" tool you're trying to use has a bug - it clears the URL field after clicking "Run Analysis". This is NOT your Career OS application.

## The Solution
Use your **own Feature 5 (Portfolio Narrator)** which does the exact same thing and is already deployed and working!

---

## Step-by-Step Guide

### 1. Open Your Career OS Application
Go to: **https://career-os-production.up.railway.app/**

### 2. Sign In
- Use your email/password, OR
- Click "Sign in with Google"

### 3. Navigate to Narrative Workspace
- Look at the left sidebar
- Click the **"Narrative"** button (book icon - 📖)
- This opens Feature 5 workspace

### 4. Fill in the Form

#### Required Fields:
- **GitHub Repository URL**: `https://github.com/murtazalirizvi/career-os-`
- **Target Role**: `Senior Backend Engineer` (or whatever role you're targeting)

#### Optional Fields:
- **Tone**: Choose Professional, Conversational, or Technical
- **Job Description**: Paste the JD for better matching
- **Selected Projects**: Leave default or specify which parts to analyze

### 5. Click "Run Portfolio Narrator"
- The button is at the top right of the workspace
- Wait 30-60 seconds for analysis to complete

### 6. View Results
You'll get:
- **Deep Analysis**: Architecture quality, code sophistication
- **STAR Narratives**: Problem → Solution → Impact stories
- **Talk Tracks**: Interview Q&A preparation
- **Consistency Check**: Credibility warnings

### 7. Download Results
After analysis completes, you can:
- Click **".md"** button → Download markdown bundle
- Click **"PDF"** button → Download case study PDF
- Click **".zip"** button → Download portfolio site package

---

## What Feature 5 Does (Same as External Tool)

### 1. Deep Codebase Analysis
- Scans your repository structure
- Identifies custom logic vs boilerplate
- Analyzes architecture patterns
- Measures code sophistication

### 2. STAR Narrative Generation
- **S**ituation: What was the challenge?
- **T**ask: What did you need to accomplish?
- **A**ction: What did you build/implement?
- **R**esult: What was the impact?

### 3. Interview Talk Tracks
- Generates Q&A for common interview questions
- Tailored to your actual code
- Evidence-based responses

### 4. Consistency Checks
- Flags claims that lack code evidence
- Ensures credibility
- Prevents over-claiming

---

## Troubleshooting

### "Cannot reach backend server"
**Solution**: Make sure you added all environment variables to Railway:
- GEMINI_API_KEY ✅
- GOOGLE_CLIENT_ID ✅
- GOOGLE_CLIENT_SECRET ✅
- OPENROUTER_API_KEY ✅

### "Invalid GitHub URL"
**Solution**: Use exact format:
```
https://github.com/username/repo
```
No trailing slashes, no `.git` extension

### "No analysis found"
**Solution**: 
1. Make sure your repository is **public**
2. Check that the URL is correct
3. Verify Railway deployment is running

### "Session expired"
**Solution**: Refresh the page and sign in again

---

## Why Use Your Own Feature 5?

### ✅ Advantages:
1. **Already deployed** - No setup needed
2. **Integrated** - Works with your other features
3. **Your API keys** - Uses your Gemini API
4. **No rate limits** - Not shared with others
5. **Customizable** - You control the code
6. **Reliable** - No third-party dependencies

### ❌ External Tool Issues:
1. Bug: Clears URL field
2. Unknown rate limits
3. May require authentication
4. No control over fixes
5. Could go offline anytime

---

## Quick Test

1. Go to: https://career-os-production.up.railway.app/
2. Sign in
3. Click "Narrative" in sidebar
4. Enter: `https://github.com/murtazalirizvi/career-os-`
5. Enter role: `Senior Backend Engineer`
6. Click "Run Portfolio Narrator"
7. Wait for results

**Expected time**: 30-60 seconds
**Expected output**: Deep analysis + STAR narratives + Talk tracks

---

## Need Help?

If Feature 5 doesn't work:
1. Check Railway logs for errors
2. Verify GEMINI_API_KEY is set in Railway
3. Make sure repository is public
4. Check browser console (F12) for errors

---

## Summary

**Don't use the external tool** - it has bugs and you can't fix them.

**Use your own Feature 5** - it's already built, deployed, and working!

Your Career OS → Narrative workspace → Enter GitHub URL → Run Portfolio Narrator → Get results
