# 🚀 Deploy to Vercel - Quick Guide

## Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

## Step 2: Login to Vercel

```bash
vercel login
```

## Step 3: Deploy Backend

```bash
# Make sure you're in the project root
cd C:\Users\info\Desktop\bulk-image-gen\ai-image-bulk

# Deploy
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** big-api-backend (or your choice)
- **Directory?** ./ (current directory)
- **Override settings?** No

## Step 4: Add Environment Variables

After deployment, add these environment variables in Vercel Dashboard:

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Add the following (one by one):

```bash
SUPABASE_URL=https://ureidlleripigzhkowwx.supabase.co
```

```bash
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVyZWlkbGxlcmlwaWd6aGtvd3d4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTYyMTk1NCwiZXhwIjoyMDc3MTk3OTU0fQ.f7ie0fo01Ay96oIYIhkwcVxdw-5WaI69Ii2SvAOnEPg
```

**Add your AI provider keys** (get these from their respective platforms):
```bash
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-key-here
FAL_KEY=your-key-here
BFL_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
MINIMAX_API_KEY=your-key-here
REVE_API_KEY=your-key-here
```

## Step 5: Redeploy with Environment Variables

```bash
vercel --prod
```

## Step 6: Get Your Backend URL

After deployment, Vercel will give you a URL like:
```
https://big-api-backend-xyz.vercel.app
```

**Save this URL!** You'll need it for the frontend.

---

## Deploy Frontend

```bash
cd frontend

# Deploy
vercel
```

Follow the prompts (same as backend)

## Add Frontend Environment Variables

Go to: **Vercel Dashboard → Frontend Project → Settings → Environment Variables**

Add:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://ureidlleripigzhkowwx.supabase.co
```

```bash
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVyZWlkbGxlcmlwaWd6aGtvd3d4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE2MjE5NTQsImV4cCI6MjA3NzE5Nzk1NH0.LPOYOKYI0au2gE3-vz5HCvDm1GizpQc7FyFiErQjwM0
```

```bash
NEXT_PUBLIC_API_URL=https://big-api-backend-xyz.vercel.app
```
(Replace with your actual backend URL from Step 6)

## Final Deploy

```bash
vercel --prod
```

---

## ✅ Done!

Your app is now live at:
- **Frontend**: `https://your-frontend.vercel.app`
- **Backend**: `https://your-backend.vercel.app`

---

## Quick Deploy Commands (After Initial Setup)

```bash
# Deploy backend
cd C:\Users\info\Desktop\bulk-image-gen\ai-image-bulk
vercel --prod

# Deploy frontend
cd frontend
vercel --prod
```

---

## Troubleshooting

### Backend shows errors?
1. Check environment variables are set in Vercel Dashboard
2. Check deployment logs: `vercel logs`

### Frontend can't connect to backend?
1. Update `NEXT_PUBLIC_API_URL` in frontend env vars
2. Make sure backend URL is correct
3. Check CORS is enabled in backend

### Database errors?
1. Make sure you ran the Supabase migration
2. Go to Supabase SQL Editor
3. Paste content from `supabase/migrations/001_initial_schema.sql`
4. Click Run

---

## First Time Setup After Deploy

1. **Run Database Migration**:
   - Go to: https://app.supabase.com/project/ureidlleripigzhkowwx/sql/new
   - Copy entire content of `supabase/migrations/001_initial_schema.sql`
   - Paste and click "Run"

2. **Test Your API**:
   ```bash
   curl https://your-backend.vercel.app
   ```

   Should return:
   ```json
   {
     "message": "BIG API - Bulk Image Generation API",
     "version": "1.0.0",
     "status": "operational"
   }
   ```

3. **Create Your First User**:
   - Go to your frontend URL
   - Click "Sign Up"
   - Create account
   - Login

4. **Generate API Key**:
   - Go to Dashboard → API Keys
   - Click "Create API Key"
   - Copy the key

5. **Test Image Generation**:
   ```bash
   curl -X POST https://your-backend.vercel.app/v1/jobs/create \
     -H "Authorization: Bearer big_live_your_key_here" \
     -H "Content-Type: application/json" \
     -d '{
       "tasks": [{
         "prompt": "A beautiful sunset",
         "provider": "dalle",
         "size": "1024x1024"
       }]
     }'
   ```

🎉 **You're live!**
