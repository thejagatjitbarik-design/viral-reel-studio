# ⚡ Viral Reel Studio — Automated AI Video Production Engine

An autonomous, agent-native vertical video engine that creates high-retention 9:16 Instagram Reels, YouTube Shorts, and TikToks.

## 🚀 Key Features

1. **📁 Upload Raw Video Mode:**
   - Upload any raw talking-head footage.
   - Speech transcribed automatically using OpenAI Whisper.
   - Generates synced dynamic subtitles with pill backgrounds and keyword highlights.
   - Automatically generates and composites floating glassmorphism motion graphic cards with smooth slide-in motion.
   - Generates synchronized sound effects (whooshes, pops, dings, clicks) and subtle lo-fi groove.
   - Mastered vocal compression and loudness normalization (-16 LUFS).

2. **✨ Prompt to Reel Mode:**
   - Input any topic or script idea.
   - Automatically synthesizes script.
   - Generates natural AI voiceover using Edge-TTS (English & Hindi voices supported).
   - Generates animated background canvas and motion cards with SFX.
   - Instant one-click render and preview.

---

## 🛠️ Step 1: Initialize & Push to GitHub

In your terminal or PowerShell inside this folder:

```bash
cd "C:\Users\kumar\.gemini\antigravity\scratch\viral-reel-studio-app"

# 1. Initialize git repository
git init
git add .
git commit -m "Initial commit: Viral Reel Studio Web App & Engine"

# 2. Create a new repository on GitHub:
# Go to https://github.com/new and create a repo named: viral-reel-studio

# 3. Link remote and push (replace YOUR_USERNAME):
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/viral-reel-studio.git
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Render (render.com)

1. **Sign in to Render:** Go to [render.com](https://render.com) and log in with your GitHub account.
2. **Create New Web Service:**
   * In the top-right, click **New +** ➔ **Web Service**.
   * Choose **Build and deploy from a Git repository**.
   * Select your newly created `viral-reel-studio` repository.
3. **Configure Settings:**
   * **Name:** `viral-reel-studio`
   * **Region:** Oregon (US West) or Frankfurt (EU)
   * **Branch:** `main`
   * **Runtime:** Select **Docker** (Render will automatically detect the `Dockerfile`!).
   * **Instance Type:** Starter (Recommended: 1 vCPU, 512MB–2GB RAM)
4. **Environment Variables:**
   * `PORT`: `10000`
   * `WHISPER_MODEL`: `base` (or `tiny` for low memory)
5. **Deploy:**
   * Click **Deploy Web Service**!
   * Render will automatically build the Docker container with FFmpeg, Whisper, and Edge-TTS.
   * In ~3 minutes, your live URL will be active (e.g. `https://viral-reel-studio.onrender.com`).

---

## 💻 Running Locally (Optional)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 10000
```
Open `http://localhost:10000` in your web browser.
