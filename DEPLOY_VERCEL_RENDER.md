# 🚀 LogVista Deployment Guide: Vercel (Frontend) + Render (Backend)

This guide walks you through deploying **LogVista** with **Vercel** hosting the React frontend and **Render** hosting the Flask backend API.

---

## 📋 Overview of the Architecture

```
                       ┌───────────────────────────────┐
                       │        End User Browser       │
                       └──────────────┬────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              │                                               │
              ▼ (HTTPS - Fast Global CDN)                     ▼ (HTTPS API Calls)
    ┌───────────────────────────┐                   ┌───────────────────────────┐
    │          VERCEL           │                   │          RENDER           │
    │      (React + Vite)       │                   │    (Flask + Gunicorn)     │
    │                           │                   │                           │
    │  • Serves UI Dashboard    │  VITE_API_BASE_URL│  • Log Parser & Heuristics│
    │  • Client-side Routing    │ ─────────────────>│  • MITRE ATT&CK Timeline  │
    │  • vercel.json rewrite    │                   │  • SQLite Database        │
    └───────────────────────────┘                   └───────────────────────────┘
```

---

## Step 1: Commit and Push Code to GitHub

Make sure your repository has the latest deployment-ready changes and that large datasets (`.csv` files and massive `.pkl` files) are excluded to avoid GitHub push limits.

In your terminal / PowerShell:

```bash
# Navigate to the repo directory
cd "d:\Logvista5 - Copy\Logvista2"

# Check your git status (make sure no 100MB+ files are being tracked)
git status

# Stage the modified and new deployment files
git add frontend/src/config.js frontend/src/pages/ frontend/vercel.json frontend/.env.example
git add backend_2/app.py backend_2/Procfile render.yaml .gitignore

# Commit the changes
git commit -m "feat: configure dynamic API URL, CORS, and deployment settings for Vercel and Render"

# Push to your GitHub repository
git push origin main
```

---

## Step 2: Deploy Backend to Render (Free Web Service)

1. Go to [Render.com](https://render.com) and log in (or sign up with your GitHub account).
2. Click **"New +"** in the top right and select **"Web Service"**.
3. Select **"Build and deploy from a Git repository"** and choose your repository:
   - Repository: `Minor_Project_Logvista` (or your repo name).
4. Configure the Web Service settings:

| Setting Field | Value |
|---|---|
| **Name** | `logvista-backend` (or any unique name you like) |
| **Region** | Choose closest to you (e.g., `Oregon (US West)` or `Frankfurt (EU)`) |
| **Branch** | `main` |
| **Root Directory** | `backend_2` *(or `Logvista2/backend_2` if deploying from root workspace)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120` |
| **Instance Type** | `Free` |

5. Add Environment Variables (click **"Advanced"** -> **"Add Environment Variable"**):
   - Key: `PYTHON_VERSION`, Value: `3.11.8`
   - Key: `FLASK_DEBUG`, Value: `False`

6. Click **"Create Web Service"**.
7. Wait 2–3 minutes for the build to complete. When deployment finishes, Render will provide your public backend URL:
   ```
   https://logvista-backend-xxxx.onrender.com
   ```
8. **Test your backend**: Open `https://logvista-backend-xxxx.onrender.com/health` in your browser. You should see:
   ```json
   {"message": "Log Investigation Framework Backend Running", "status": "ok"}
   ```

---

## Step 3: Deploy Frontend to Vercel

1. Go to [Vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **"Add New..."** -> **"Project"**.
3. Import your GitHub repository (`Minor_Project_Logvista`).
4. In the **Configure Project** screen:
   - **Framework Preset**: `Vite` (automatically detected)
   - **Root Directory**: Click `Edit` and select `frontend` *(or `Logvista2/frontend` depending on repository root)*.
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `dist` (default)
5. **Add Environment Variable** (CRITICAL STEP):
   - Expand the **"Environment Variables"** dropdown.
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: Your Render Backend URL from Step 2 (e.g. `https://logvista-backend-xxxx.onrender.com` — *no trailing slash*).
6. Click **"Deploy"**.
7. Vercel will build the frontend and output your live production URL:
   ```
   https://logvista-frontend-xxxx.vercel.app
   ```

---

## Step 4: Verify Full End-to-End System

1. Visit your Vercel URL in your browser.
2. Check the **Dashboard**: The KPI counters should fetch statistics directly from the live Render backend.
3. Test **Log Upload**:
   - Go to **Upload Logs** (`/upload`).
   - Drag and drop a test log file (or use sample event logs).
   - Verify the success notification appears.
4. Navigate to **Timeline Reconstruction** (`/timeline`) and **Threat Detection** (`/threats`):
   - Verify the AI timeline narration and forensic stages populate with real data.
5. Refresh the page on any sub-route (e.g., `/timeline` or `/threats`):
   - Notice that `vercel.json` prevents 404 errors by cleanly routing back to the single-page application!

---

## ⚠️ Important Note About Render's Free Tier

- **Spin-down / Cold Starts**: Render's free tier spins down the web service after 15 minutes of inactivity.
- When visiting the frontend after a period of dormancy, the first request may take ~30–45 seconds while Render boots up the container. Subsequent requests will be instantaneous.
- **Tip**: If you want the backend to stay awake continuously, you can use a free uptime monitor like [UptimeRobot](https://uptimerobot.com) to ping `https://your-backend.onrender.com/health` every 10 minutes.
