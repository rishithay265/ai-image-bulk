# 🚀 BIG API Setup Guide

Complete guide to setting up the BIG API full-stack application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Supabase Setup](#supabase-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [API Provider Keys](#api-provider-keys)
6. [Deployment](#deployment)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.9+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **Git**: [Download](https://git-scm.com/)
- **Vercel CLI** (optional): `npm install -g vercel`

### Required Accounts

- **Supabase**: [Sign up](https://supabase.com)
- **Vercel**: [Sign up](https://vercel.com) (for deployment)
- **Stripe**: [Sign up](https://stripe.com) (for payments - optional)

---

## Supabase Setup

### Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click **"New Project"**
3. Fill in project details:
   - **Name**: big-api
   - **Database Password**: (save this securely)
   - **Region**: Choose closest to your users
4. Click **"Create New Project"**

### Step 2: Run Database Migration

1. Go to **SQL Editor** in Supabase dashboard
2. Click **"New Query"**
3. Copy the entire content from `supabase/migrations/001_initial_schema.sql`
4. Paste into the SQL editor
5. Click **"Run"**
6. Verify success (should see "Success. No rows returned")

### Step 3: Get API Keys

1. Go to **Settings** → **API**
2. Copy the following:
   - **Project URL**: `https://xxx.supabase.co`
   - **anon public**: Your anon key
   - **service_role**: Your service role key (keep secret!)

### Step 4: Configure Authentication

1. Go to **Authentication** → **Providers**
2. Enable **Email** authentication
3. Configure email templates (optional):
   - Go to **Authentication** → **Email Templates**
   - Customize signup confirmation email

### Step 5: Set Up Storage (Optional)

1. Go to **Storage**
2. Create a new bucket called `images`
3. Set bucket to **Public**
4. This will store generated images (optional feature)

---

## Backend Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/big-api.git
cd big-api
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local with your actual keys
```

**Required variables**:

```bash
# Supabase
SUPABASE_URL=https://ureidlleripigzhkowwx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Add your image generation API keys below
# (see API Provider Keys section)
```

### Step 5: Test Locally

```bash
python api_gateway.py
```

Visit `http://localhost:5000` - you should see:

```json
{
  "message": "BIG API - Bulk Image Generation API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

## Frontend Setup

### Step 1: Install Node Dependencies

```bash
cd frontend
npm install
```

### Step 2: Configure Environment

```bash
# Create .env.local in frontend directory
cp .env.example .env.local
```

**frontend/.env.local**:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://ureidlleripigzhkowwx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Step 3: Run Development Server

```bash
npm run dev
```

Visit `http://localhost:3000`

---

## API Provider Keys

To use all 15 image generation providers, you need API keys from each service.

### 1. OpenAI (DALL-E 3, GPT Image 1)

1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Sign up or login
3. Go to **API Keys**
4. Click **"Create new secret key"**
5. Copy key → Add to `.env.local` as `OPENAI_API_KEY`

**Cost**: Pay-as-you-go pricing

### 2. Google AI (Imagen, Gemini)

1. Go to [https://aistudio.google.com](https://aistudio.google.com)
2. Click **"Get API Key"**
3. Create new API key
4. Copy key → Add to `.env.local` as `GOOGLE_API_KEY`

**Cost**: Free tier available, then pay-as-you-go

### 3. fal.ai (5 providers: Seedream 4/3, Qwen, Ideogram V3, GPT Image 1)

1. Go to [https://fal.ai](https://fal.ai)
2. Sign up
3. Go to **Dashboard** → **API Keys**
4. Copy key → Add to `.env.local` as `FAL_KEY`

**Cost**: Credits-based, free tier available

### 4. BFL.AI (FLUX models)

1. Go to [https://api.bfl.ai](https://api.bfl.ai)
2. Sign up
3. Get API key from dashboard
4. Copy key → Add to `.env.local` as `BFL_API_KEY`

**Cost**: Credits-based

### 5. Minimax

1. Go to [https://platform.minimax.io](https://platform.minimax.io)
2. Register account
3. Get API key
4. Copy key → Add to `.env.local` as `MINIMAX_API_KEY`

**Cost**: Pay-as-you-go

### 6. Reve AI

1. Contact [https://reve.com](https://reve.com)
2. Get API access
3. Copy key → Add to `.env.local` as `REVE_API_KEY`

**Cost**: Enterprise pricing

### Optional: Vercel KV (Redis)

For caching and rate limiting:

1. Go to [https://vercel.com](https://vercel.com)
2. Create project
3. Go to **Storage** → **Create Database** → **KV**
4. Copy `KV_URL` → Add to `.env.local`

**Cost**: Free tier available

---

## Deployment

### Deploy Backend to Vercel

```bash
# From project root
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set up environment variables when prompted
```

### Add Environment Variables to Vercel

```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add OPENAI_API_KEY
vercel env add GOOGLE_API_KEY
vercel env add FAL_KEY
# ... add all your API keys
```

Or use Vercel Dashboard:

1. Go to project **Settings** → **Environment Variables**
2. Add each variable manually

### Deploy Frontend to Vercel

```bash
cd frontend
vercel

# Set frontend-specific env vars:
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add NEXT_PUBLIC_API_URL
```

### Deploy to Production

```bash
# Backend
vercel --prod

# Frontend
cd frontend
vercel --prod
```

---

## Testing

### Test API Locally

```bash
# Test root endpoint
curl http://localhost:5000

# Test with demo key (run setup_demo_key.py first)
python setup_demo_key.py

# Test image generation
curl -X POST http://localhost:5000/v1/jobs/create \
  -H "Authorization: Bearer big_live_demo_key_12345678901234567890" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

### Run Test Suite

```bash
pytest tests/ -v
```

### Test Frontend

```bash
cd frontend
npm run test
```

---

## Troubleshooting

### Common Issues

#### 1. "Could not connect to Supabase"

**Solution**:
- Verify `SUPABASE_URL` and keys in `.env.local`
- Check Supabase project is active
- Verify database migration ran successfully

#### 2. "Invalid API key" errors

**Solution**:
- Run `python setup_demo_key.py` to create test key
- Verify Redis/KV connection
- Check Supabase `api_keys` table has entries

#### 3. "Provider not available" errors

**Solution**:
- Verify you have API key for that provider
- Check provider-specific env variable is set
- Test provider API key independently

#### 4. CORS errors in frontend

**Solution**:
- Add frontend URL to Flask CORS config in `api_gateway.py`
- Verify API_URL in frontend `.env.local`

#### 5. Rate limit errors

**Solution**:
- Check your plan tier limits
- Verify KV/Redis is connected
- Clear rate limit cache in Redis

### Debug Mode

Enable debug logging:

```python
# In api_gateway.py
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Check Logs

**Vercel Logs**:
```bash
vercel logs
```

**Supabase Logs**:
- Go to Supabase Dashboard → Logs

---

## Next Steps

1. **Customize Landing Page**: Edit `frontend/app/page.tsx`
2. **Set Up Stripe**: Configure payment processing
3. **Add Webhooks**: Set up Stripe webhooks for subscriptions
4. **Custom Domain**: Add custom domain in Vercel
5. **Email Templates**: Customize Supabase email templates
6. **Monitoring**: Set up error tracking (Sentry)
7. **Analytics**: Add Google Analytics or Plausible

---

## Support

Need help? Contact us:

- 📧 Email: support@bigapi.io
- 💬 Discord: [Join community](https://discord.gg/bigapi)
- 📚 Docs: [docs.bigapi.io](https://docs.bigapi.io)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/big-api/issues)

---

## Security Checklist

Before going to production:

- [ ] Change all default passwords
- [ ] Enable Supabase RLS policies
- [ ] Set up API rate limiting
- [ ] Configure CORS properly
- [ ] Enable HTTPS only
- [ ] Set up backup strategy
- [ ] Configure Stripe webhooks
- [ ] Add error monitoring
- [ ] Set up logging
- [ ] Review security headers
- [ ] Enable 2FA on all services
- [ ] Rotate API keys regularly

---

**Congratulations!** 🎉 Your BIG API is now set up and ready to generate images at scale!
