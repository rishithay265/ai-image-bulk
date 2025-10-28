# 🎨 BIG API - Bulk Image Generation API

> **Unified gateway to 15+ state-of-the-art AI image generation models**

Generate images at scale with a single, powerful API. Access DALL-E 3, Imagen 4, FLUX, GPT Image 1, Ideogram V3, and more through one simple interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/big-api)

## 🚀 Features

- **15+ AI Providers**: DALL-E 3, Imagen 4 Ultra, GPT Image 1, Ideogram V3, FLUX, Seedream, Qwen, and more
- **Unified API**: One endpoint for all providers
- **Synchronous Processing**: Get results immediately (Vercel-optimized)
- **Credit System**: Pay-as-you-go pricing with transparent costs
- **Real-time Analytics**: Track usage, costs, and performance
- **Comprehensive Documentation**: Full API docs with examples
- **User Dashboard**: Manage API keys, view analytics, purchase credits
- **Secure Authentication**: Supabase-powered auth with JWT
- **Rate Limiting**: Fair usage policies per plan tier
- **99.9% Uptime**: Production-ready infrastructure

## 📦 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/big-api.git
cd big-api
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env.local
# Edit .env.local with your API keys
```

### 3. Setup Supabase Database

```bash
# Run the migration in Supabase SQL Editor
cat supabase/migrations/001_initial_schema.sql | supabase db execute
```

### 4. Run Locally

```bash
python api_gateway.py
# API runs on http://localhost:5000
```

### 5. Deploy to Vercel

```bash
vercel deploy
```

## 🎯 Usage Example

```python
import requests

url = "https://ai-image-bulk.vercel.app/v1/jobs/create"
headers = {
    "Authorization": "Bearer big_live_your_api_key",
    "Content-Type": "application/json"
}
payload = {
    "tasks": [
        {
            "prompt": "A serene mountain landscape at sunset, photorealistic",
            "provider": "dalle",
            "size": "1024x1024"
        },
        {
            "prompt": "Futuristic cityscape with neon lights, cyberpunk style",
            "provider": "imagen-4",
            "aspect_ratio": "16:9"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

print(f"Generated {result['successful']} images")
print(f"Credits used: {result['credits_used']}")
for image in result['results']:
    print(f"Image URL: {image['imageUrl']}")
```

## 📊 Supported Providers

| Provider | Credits | Max Resolution | Best For |
|----------|---------|----------------|----------|
| **DALL-E 3** | 10 | 1792x1024 | General purpose, high quality |
| **Imagen 4 Ultra** | 12 | 2K | Photorealism, ultra quality |
| **GPT Image 1** | 11 | 1536x1024 | Latest OpenAI, multimodal |
| **Ideogram V3** | 9 | 2K | Artistic styles, 80+ presets |
| **Imagen 4** | 9 | 2K | High quality, Google |
| **FLUX Kontext** | 8 | 1536x1024 | Creative, artistic |
| **Seedream 4** | 8 | 4K | Fast, bilingual, 4K |
| **Seedream 3** | 7 | 2K | Fast, text-in-image |
| **Minimax** | 7 | 1024x1024 | General purpose |
| **Imagen 4 Fast** | 7 | 1K | Fast generation |
| **FLUX Dev** | 6 | 1024x1024 | Development |
| **Imagen 3** | 6 | 1K | Standard quality |
| **Qwen-Image** | 6 | 1024x1024 | LoRA support |
| **Gemini** | 5 | 1024x1024 | Fast, economical |
| **Reve** | 5 | 1024x1024 | Fast, economical |

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js        │
│  Frontend       │  ← User Dashboard
│  (Supabase Auth)│
└────────┬────────┘
         │
    ┌────▼────┐
    │ Vercel  │
    │ Edge    │
    └────┬────┘
         │
┌────────▼─────────┐
│ Flask API        │
│ (api_gateway.py) │  ← Main API Gateway
└─────────┬────────┘
          │
    ┌─────▼─────┐
    │ Supabase  │
    │ PostgreSQL│  ← User data, API keys, usage logs
    └───────────┘
          │
    ┌─────▼─────┐
    │ Redis/KV  │  ← Caching, rate limiting
    └───────────┘
          │
    ┌─────▼────────────────────┐
    │ External AI APIs         │
    ├──────────────────────────┤
    │ • OpenAI (DALL-E, GPT-1) │
    │ • Google (Imagen, Gemini)│
    │ • BFL.AI (FLUX)          │
    │ • fal.ai (5 providers)   │
    │ • Minimax, Reve          │
    └──────────────────────────┘
```

## 📁 Project Structure

```
ai-image-bulk/
├── api_gateway.py          # Main Flask API
├── setup_demo_key.py       # Demo API key setup
├── requirements.txt        # Python dependencies
├── vercel.json            # Vercel deployment config
├── payload.json           # Example payloads
├── .env.local             # Environment variables
├── .env.example           # Example env file
│
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql  # Database schema
│
├── docs/
│   ├── API_DOCUMENTATION.md        # Complete API docs
│   └── SETUP_GUIDE.md              # Setup instructions
│
├── frontend/              # Next.js frontend (to be added)
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
│
└── tests/                 # Test suite
    ├── test_api.py
    └── test_providers.py
```

## 🔧 Environment Variables

### Required

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Image Generation Providers
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
FAL_KEY=...
BFL_API_KEY=...
# ... (see .env.example for full list)
```

### Optional

```bash
# Redis/Vercel KV (for caching)
KV_URL=redis://...

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 💳 Pricing

### Free Tier
- ✅ 100 credits on signup
- ✅ 10 requests/minute
- ✅ Access to basic providers
- ✅ Community support

### Starter - $29/month
- ✅ 5,000 credits/month
- ✅ 60 requests/minute
- ✅ All providers
- ✅ Email support

### Pro - $99/month
- ✅ 25,000 credits/month
- ✅ 120 requests/minute
- ✅ Priority processing
- ✅ Dedicated support
- ✅ Custom integrations

### Enterprise - Custom
- ✅ Custom credit allocation
- ✅ Unlimited rate limits
- ✅ SLA guarantee
- ✅ Account manager
- ✅ White-label options

## 📚 Documentation

- [📖 API Documentation](./docs/API_DOCUMENTATION.md) - Complete API reference
- [🔐 Authentication Guide](./docs/AUTHENTICATION.md) - Auth setup
- [🎨 Provider Guide](./docs/PROVIDERS.md) - Provider-specific docs
- [⚙️ Setup Guide](./docs/SETUP_GUIDE.md) - Installation instructions
- [🧪 Examples](./examples/) - Code examples

## 🛠️ Development

### Run Tests

```bash
pytest tests/
```

### Run Linter

```bash
flake8 api_gateway.py
black api_gateway.py
```

### Setup Demo Data

```bash
python setup_demo_key.py
```

## 🚀 Deployment

### Deploy to Vercel

```bash
vercel --prod
```

### Configure Vercel Environment Variables

```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add OPENAI_API_KEY
# ... add all required env vars
```

## 🔒 Security

- ✅ API keys hashed with bcrypt
- ✅ Row Level Security (RLS) on Supabase
- ✅ JWT token authentication
- ✅ Rate limiting per user
- ✅ CORS protection
- ✅ Input validation
- ✅ SQL injection prevention

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for DALL-E 3 and GPT Image 1
- Google for Imagen and Gemini
- BFL.AI for FLUX models
- fal.ai for hosting multiple models
- Supabase for auth and database
- Vercel for hosting

## 📞 Support

- 📧 Email: support@bigapi.io
- 💬 Discord: [Join our community](https://discord.gg/bigapi)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/big-api/issues)
- 📚 Docs: [Documentation](https://docs.bigapi.io)

## 🗺️ Roadmap

- [ ] Video generation support
- [ ] Image-to-image transformations
- [ ] Image upscaling
- [ ] Batch processing webhooks
- [ ] GraphQL API
- [ ] Python SDK
- [ ] TypeScript SDK
- [ ] CLI tool
- [ ] Zapier integration
- [ ] Make.com integration

---

Made with ❤️ by the BIG API Team
