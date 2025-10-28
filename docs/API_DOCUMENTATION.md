# BIG API - Complete API Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Quick Start](#quick-start)
4. [API Endpoints](#api-endpoints)
5. [Image Generation](#image-generation)
6. [Provider Guide](#provider-guide)
7. [Error Handling](#error-handling)
8. [Rate Limits](#rate-limits)
9. [Code Examples](#code-examples)

---

## Introduction

Welcome to BIG API (Bulk Image Generation API) - your unified gateway to 15+ state-of-the-art AI image generation models. Generate images at scale with a single API.

**Base URL**: `https://ai-image-bulk.vercel.app`

**Features**:
- 🎨 15+ AI image generation providers
- ⚡ Synchronous & asynchronous processing
- 📊 Real-time usage analytics
- 💳 Credit-based pricing
- 🔐 Secure API key authentication
- 📈 Scalable infrastructure

---

## Authentication

All API requests require authentication using an API key in the Authorization header.

### Getting Your API Key

1. Sign up at [bigapi.io/signup](https://bigapi.io/signup)
2. Navigate to Dashboard → API Keys
3. Click "Create New API Key"
4. Copy your key (starts with `big_live_`)

### Using Your API Key

```bash
Authorization: Bearer big_live_your_api_key_here
```

**Example**:
```bash
curl -H "Authorization: Bearer big_live_abc123..." https://api.bigapi.io/v1/jobs/create
```

---

## Quick Start

### Step 1: Install HTTP Client

```bash
# Python
pip install requests

# Node.js
npm install axios

# cURL (pre-installed on most systems)
```

### Step 2: Make Your First Request

```python
import requests

url = "https://ai-image-bulk.vercel.app/v1/jobs/create"
headers = {
    "Authorization": "Bearer big_live_your_api_key_here",
    "Content-Type": "application/json"
}
payload = {
    "tasks": [
        {
            "prompt": "A serene mountain landscape at sunset",
            "provider": "dalle"
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

---

## API Endpoints

### 1. Create Image Generation Job

**Endpoint**: `POST /v1/jobs/create`

Creates and processes an image generation job synchronously.

**Request Headers**:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "tasks": [
    {
      "prompt": "A beautiful sunset over the ocean",
      "provider": "dalle",
      "size": "1024x1024"
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Job completed successfully",
  "total_tasks": 1,
  "successful": 1,
  "failed": 0,
  "credits_used": 10,
  "credits_remaining": 9990,
  "results": [
    {
      "prompt": "A beautiful sunset over the ocean",
      "provider": "dalle",
      "status": "Success",
      "imageUrl": "https://..."
    }
  ]
}
```

**Parameters**:
- `tasks` (array, required): List of image generation tasks
  - `prompt` (string, required): Text description of the image
  - `provider` (string, required): Image generation provider (see Provider Guide)
  - Additional provider-specific parameters

**Limits**:
- Maximum 100 tasks per request
- Maximum prompt length: 480 tokens

---

### 2. Get Dashboard Statistics

**Endpoint**: `GET /v1/dashboard/stats`

Retrieves real-time statistics for your account.

**Request Headers**:
```
Authorization: Bearer YOUR_API_KEY
```

**Response** (200 OK):
```json
{
  "credits_remaining": 9990,
  "total_api_calls": 45,
  "total_images_generated": 150,
  "total_credits_used": 450,
  "success_rate": 98.5,
  "provider_usage": {
    "dalle": 20,
    "imagen-4": 15,
    "flux-kontext": 10
  },
  "recent_activity": [...]
}
```

---

### 3. Get Usage Analytics

**Endpoint**: `GET /v1/dashboard/usage`

Retrieves detailed usage analytics with time filtering.

**Query Parameters**:
- `period`: Time period (24h, 7d, 30d, 90d)

**Example**:
```
GET /v1/dashboard/usage?period=7d
```

**Response** (200 OK):
```json
{
  "period": "7d",
  "total_calls": 45,
  "total_credits": 450,
  "daily_usage": [
    {
      "date": "2025-01-20",
      "calls": 10,
      "credits": 100
    }
  ],
  "provider_usage": [
    {
      "provider": "dalle",
      "calls": 20,
      "credits": 200
    }
  ]
}
```

---

### 4. List API Keys

**Endpoint**: `GET /v1/api-keys`

Lists all API keys for your account.

**Response** (200 OK):
```json
{
  "api_keys": [
    {
      "id": "key_001",
      "name": "Production Key",
      "key": "big_live_abc...xyz",
      "created_at": "2025-01-15",
      "last_used": "2 hours ago",
      "requests_count": 1234
    }
  ]
}
```

---

## Image Generation

### Supported Providers

| Provider | Credits | Best For | Max Resolution |
|----------|---------|----------|----------------|
| **dalle** | 10 | General purpose, high quality | 1792x1024 |
| **imagen-4-ultra** | 12 | Ultra high quality, photorealism | 2K |
| **gpt-image-1** | 11 | Latest OpenAI, multimodal | 1536x1024 |
| **ideogram-v3** | 9 | Artistic styles, text-in-image | 2K |
| **imagen-4** | 9 | High quality, Google | 2K |
| **flux-kontext** | 8 | Creative, artistic | 1536x1024 |
| **seedream-4** | 8 | Fast, 4K support | 4K |
| **seedream-3** | 7 | Bilingual, fast | 2K |
| **minimax** | 7 | General purpose | 1024x1024 |
| **imagen-4-fast** | 7 | Fast generation | 1K |
| **flux-dev** | 6 | Development, testing | 1024x1024 |
| **imagen-3** | 6 | Standard quality | 1K |
| **qwen-image** | 6 | LoRA support | 1024x1024 |
| **gemini** | 5 | Fast, economical | 1024x1024 |
| **reve** | 5 | Fast, economical | 1024x1024 |

---

## Provider Guide

### DALL-E 3 (OpenAI)

```json
{
  "prompt": "A photorealistic cat wearing sunglasses",
  "provider": "dalle",
  "size": "1024x1024"
}
```

**Parameters**:
- `size`: "1024x1024", "1024x1792", "1792x1024"

---

### Imagen 4 Ultra (Google)

```json
{
  "prompt": "Professional portrait photography, studio lighting",
  "provider": "imagen-4-ultra",
  "aspect_ratio": "1:1",
  "image_size": "2K",
  "person_generation": "allow_adult"
}
```

**Parameters**:
- `aspect_ratio`: "1:1", "3:4", "4:3", "9:16", "16:9"
- `image_size`: "1K", "2K"
- `person_generation`: "dont_allow", "allow_adult", "allow_all"

---

### Seedream 4

```json
{
  "prompt": "A trendy restaurant with digital menu board",
  "provider": "seedream-4",
  "image_size": "auto_2K",
  "enhance_prompt_mode": "standard"
}
```

**Parameters**:
- `image_size`: "square_hd", "auto_2K", "auto_4K", or custom size
- `enhance_prompt_mode`: "standard", "fast"
- `enable_safety_checker`: true/false

---

### Ideogram V3

```json
{
  "prompt": "Vintage travel poster of Paris",
  "provider": "ideogram-v3",
  "style": "REALISTIC",
  "style_preset": "TRAVEL_POSTER",
  "rendering_speed": "BALANCED"
}
```

**Parameters**:
- `rendering_speed`: "TURBO", "BALANCED", "QUALITY"
- `style`: "AUTO", "GENERAL", "REALISTIC", "DESIGN"
- `style_preset`: 80+ options (POP_ART, WATERCOLOR, VINTAGE_POSTER, etc.)
- `negative_prompt`: String to exclude certain elements

---

### GPT Image 1 (OpenAI)

```json
{
  "prompt": "Cyberpunk cityscape at twilight",
  "provider": "gpt-image-1",
  "image_size": "1024x1024",
  "quality": "high",
  "background": "transparent",
  "openai_api_key": "sk-..."
}
```

**Parameters**:
- `image_size`: "auto", "1024x1024", "1536x1024", "1024x1536"
- `quality`: "auto", "low", "medium", "high"
- `background`: "auto", "transparent", "opaque"
- `openai_api_key`: Required (BYOK model)

---

### FLUX Models

```json
{
  "prompt": "Abstract geometric art, vibrant colors",
  "provider": "flux-kontext",
  "aspect_ratio": "16:9"
}
```

**Providers**: `flux-kontext`, `flux-dev`

**Parameters**:
- `aspect_ratio`: "1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16"

---

### Qwen-Image

```json
{
  "prompt": "Mount Fuji with cherry blossoms",
  "provider": "qwen-image",
  "image_size": "landscape_4_3",
  "guidance_scale": 2.5,
  "acceleration": "regular",
  "negative_prompt": "blurry, low quality"
}
```

**Parameters**:
- `image_size`: "square_hd", "landscape_4_3", "portrait_16_9", etc.
- `guidance_scale`: Float (default 2.5)
- `acceleration`: "none", "regular", "high"
- `negative_prompt`: String
- `num_inference_steps`: Integer (default 30)

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 402 | Payment Required | Insufficient credits |
| 403 | Forbidden | API key revoked or suspended |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

### Example Error Responses

**Insufficient Credits**:
```json
{
  "error": "Insufficient credits",
  "credits_needed": 50,
  "credits_available": 10,
  "message": "Purchase more credits at https://bigapi.io/dashboard/billing"
}
```

**Invalid API Key**:
```json
{
  "error": "Invalid API key",
  "message": "Get your API key from https://bigapi.io/dashboard/api-keys"
}
```

---

## Rate Limits

Rate limits are based on your subscription plan:

| Plan | Requests/Minute | Requests/Hour | Requests/Day |
|------|-----------------|---------------|--------------|
| Free | 10 | 100 | 500 |
| Starter | 60 | 1,000 | 10,000 |
| Pro | 120 | 5,000 | 50,000 |
| Enterprise | Custom | Custom | Custom |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

---

## Code Examples

### Python

```python
import requests
import json

class BIGAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://ai-image-bulk.vercel.app/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate_images(self, tasks):
        """Generate images from prompts"""
        response = requests.post(
            f"{self.base_url}/jobs/create",
            headers=self.headers,
            json={"tasks": tasks}
        )
        return response.json()

    def get_stats(self):
        """Get account statistics"""
        response = requests.get(
            f"{self.base_url}/dashboard/stats",
            headers=self.headers
        )
        return response.json()

# Usage
client = BIGAPIClient("big_live_your_key_here")

tasks = [
    {
        "prompt": "A serene mountain landscape",
        "provider": "dalle",
        "size": "1024x1024"
    },
    {
        "prompt": "Futuristic cityscape at night",
        "provider": "imagen-4",
        "aspect_ratio": "16:9"
    }
]

result = client.generate_images(tasks)
print(f"Generated {result['successful']} images")
print(f"Credits used: {result['credits_used']}")

for image in result['results']:
    if image['status'] == 'Success':
        print(f"Image URL: {image['imageUrl']}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class BIGAPIClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = 'https://ai-image-bulk.vercel.app/v1';
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }

    async generateImages(tasks) {
        const response = await axios.post(
            `${this.baseURL}/jobs/create`,
            { tasks },
            { headers: this.headers }
        );
        return response.data;
    }

    async getStats() {
        const response = await axios.get(
            `${this.baseURL}/dashboard/stats`,
            { headers: this.headers }
        );
        return response.data;
    }
}

// Usage
const client = new BIGAPIClient('big_live_your_key_here');

const tasks = [
    {
        prompt: 'A serene mountain landscape',
        provider: 'dalle',
        size: '1024x1024'
    },
    {
        prompt: 'Futuristic cityscape at night',
        provider: 'imagen-4',
        aspect_ratio: '16:9'
    }
];

client.generateImages(tasks)
    .then(result => {
        console.log(`Generated ${result.successful} images`);
        console.log(`Credits used: ${result.credits_used}`);

        result.results.forEach(image => {
            if (image.status === 'Success') {
                console.log(`Image URL: ${image.imageUrl}`);
            }
        });
    })
    .catch(error => {
        console.error('Error:', error.response.data);
    });
```

### cURL

```bash
# Single image generation
curl -X POST https://ai-image-bulk.vercel.app/v1/jobs/create \
  -H "Authorization: Bearer big_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "prompt": "A serene mountain landscape at sunset",
        "provider": "dalle",
        "size": "1024x1024"
      }
    ]
  }'

# Get statistics
curl -X GET https://ai-image-bulk.vercel.app/v1/dashboard/stats \
  -H "Authorization: Bearer big_live_your_key_here"

# Bulk generation with multiple providers
curl -X POST https://ai-image-bulk.vercel.app/v1/jobs/create \
  -H "Authorization: Bearer big_live_your_key_here" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

---

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```python
try:
    result = client.generate_images(tasks)
    if result['failed'] > 0:
        # Handle partial failures
        for task in result['results']:
            if task['status'] == 'Failed':
                print(f"Failed: {task['error']}")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 402:
        print("Insufficient credits - please top up")
    elif e.response.status_code == 429:
        print("Rate limit exceeded - please wait")
```

### 2. Optimize Credit Usage

- Use lower-cost providers for testing
- Batch requests when possible
- Monitor usage with dashboard analytics

### 3. Rate Limit Management

- Implement exponential backoff for rate limit errors
- Cache results when appropriate
- Upgrade plan for higher limits

### 4. Security

- Never expose API keys in client-side code
- Use environment variables for keys
- Rotate keys regularly
- Use separate keys for dev/prod

---

## Support

- 📧 Email: support@bigapi.io
- 📖 Documentation: https://docs.bigapi.io
- 💬 Discord: https://discord.gg/bigapi
- 🐛 Issues: https://github.com/bigapi/issues

---

## Changelog

### v1.0.0 (2025-01-27)
- Initial release
- 15 AI image generation providers
- Synchronous processing
- Real-time analytics
- Credit-based billing
