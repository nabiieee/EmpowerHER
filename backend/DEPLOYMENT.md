# Deploy Backend to Railway

## 1. Create Railway Account
Go to https://railway.app and sign up/login

## 2. Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

## 3. Deploy Backend
```bash
cd backend
railway init
railway up
```

## 4. Set Environment Variables in Railway Dashboard
- SUPABASE_URL (if using Supabase)
- SUPABASE_KEY (if using Supabase)
- OPENAI_API_KEY (optional, for AI features)
- OPENAI_MODEL (optional)

## 5. Get the Backend URL
Railway will provide a URL like: `https://your-app-name.up.railway.app`

## Alternative: Deploy to Render
1. Go to https://render.com
2. Create new Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables as above