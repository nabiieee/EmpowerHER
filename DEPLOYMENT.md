# 🚀 Deploy EmpowerHer to Vercel + Railway

## Current Issue
Your full-stack app (React frontend + FastAPI backend) isn't working on Vercel because:
- Vercel is optimized for frontend deployments
- Python/FastAPI backends need separate deployment
- API calls fail because backend isn't accessible

## Solution: Separate Deployments

### Step 1: Deploy Backend to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Deploy backend
cd backend
railway init
railway up
```

Get your backend URL from Railway dashboard (e.g., `https://your-app.up.railway.app`)

### Step 2: Update Frontend Environment
Edit `frontend/.env.production`:
```env
VITE_API_URL=https://your-railway-app.up.railway.app
```

### Step 3: Deploy Frontend to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

Or connect your GitHub repo to Vercel dashboard.

### Step 4: Set Environment Variables in Vercel
In Vercel dashboard → Project Settings → Environment Variables:
```
VITE_API_URL=https://your-railway-app.up.railway.app
```

## Alternative: Deploy Backend to Render
1. Go to https://render.com
2. Create Web Service from GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

## Testing Deployment
1. Frontend: Visit Vercel URL
2. Backend: Visit `your-backend-url/api/health`
3. Full app: Try submitting a query on the frontend

## Troubleshooting
- **API calls failing**: Check VITE_API_URL is set correctly
- **CORS errors**: Backend CORS settings might need updating for production domain
- **Build failing**: Ensure all dependencies are in requirements.txt