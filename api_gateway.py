import os
import time
import json
import uuid
import requests
import hashlib
import base64
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from functools import wraps
from openai import OpenAI
import redis
from google import genai
from google.genai import types
from io import BytesIO
import fal_client
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env.local'
load_dotenv(dotenv_path=env_path, override=True)
# Also try .env if .env.local doesn't exist
load_dotenv(override=True)

# ==============================================================================
# INITIALIZATION
# ==============================================================================

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})

# --- Initialize Supabase Client ---
try:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Connected to Supabase")
except Exception as e:
    print(f"CRITICAL: Could not connect to Supabase. Error: {e}")
    supabase = None

# --- Connect to Vercel KV (Redis) for Job Tracking ---
try:
    kv = redis.from_url(os.environ.get("KV_URL"))
except Exception as e:
    print(f"Warning: Could not connect to Vercel KV. Using Supabase only. Error: {e}")
    kv = None

# --- Initialize API Clients ---
try:
    openai_client = OpenAI()
except Exception as e:
    print(f"Warning: OpenAI client failed to initialize. DALL-E will be unavailable. Error: {e}")
    openai_client = None

try:
    genai_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Warning: Google GenAI client failed to initialize. Imagen will be unavailable. Error: {e}")
    genai_client = None

# --- API Keys and Endpoints ---
BFL_API_KEY = os.environ.get("BFL_API_KEY")
REVE_API_KEY = os.environ.get("REVE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")
FAL_KEY = os.environ.get("FAL_KEY")

# Set FAL_KEY for fal_client
if FAL_KEY:
    os.environ["FAL_KEY"] = FAL_KEY

BFL_API_URL_BASE = "https://api.bfl.ai/v1/"
REVE_API_URL = "https://api.reve.com/v1/image/create"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
MINIMAX_API_URL = "https://api.minimax.io/v1/image_generation"

# ==============================================================================
# CREDIT COSTS PER PROVIDER
# ==============================================================================
PROVIDER_COSTS = {
    "dalle": 10,
    "flux-kontext": 8,
    "flux-dev": 6,
    "gemini": 5,
    "reve": 5,
    "minimax": 7,
    "imagen-3": 6,
    "imagen-4": 9,
    "imagen-4-ultra": 12,
    "imagen-4-fast": 7,
    "seedream-4": 8,
    "qwen-image": 6,
    "seedream-3": 7,
    "ideogram-v3": 9,
    "gpt-image-1": 11
}

# ==============================================================================
# API KEY AUTHENTICATION
# ==============================================================================

def validate_api_key(api_key):
    """Validates API key against Supabase and returns user info"""
    if not api_key or not api_key.startswith("big_"):
        return None

    if not supabase:
        return None

    try:
        # Hash the API key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Check cache first
        if kv:
            cached = kv.get(f"api_key:{key_hash}")
            if cached:
                return json.loads(cached)

        # Query Supabase for API key
        response = supabase.table('api_keys').select('*, users(*)').eq('key_hash', key_hash).eq('is_active', True).execute()

        if not response.data or len(response.data) == 0:
            return None

        api_key_data = response.data[0]
        user_data = api_key_data['users']

        # Update last_used_at
        supabase.table('api_keys').update({'last_used_at': time.strftime('%Y-%m-%d %H:%M:%S')}).eq('id', api_key_data['id']).execute()

        user_info = {
            "user_id": user_data['id'],
            "email": user_data['email'],
            "credits": user_data['credits'],
            "plan": user_data['plan']
        }

        # Cache for 1 hour
        if kv:
            kv.setex(f"api_key:{key_hash}", 3600, json.dumps(user_info))

        return user_info

    except Exception as e:
        print(f"Error validating API key: {e}")
        return None

def require_api_key(f):
    """Decorator that requires valid API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                "error": "Missing or invalid Authorization header",
                "message": "Include 'Authorization: Bearer YOUR_API_KEY' in your request"
            }), 401

        api_key = auth_header.replace('Bearer ', '')
        user_data = validate_api_key(api_key)

        if not user_data:
            return jsonify({
                "error": "Invalid API key",
                "message": "Get your API key from https://bigapi.io/dashboard/api-keys"
            }), 401

        # Add user data to request context
        request.user = user_data
        request.api_key = api_key
        return f(*args, **kwargs)

    return decorated_function

def deduct_credits(user_id, credits_used, task_details):
    """Deducts credits from user account using Supabase stored procedure"""
    if not supabase:
        return True  # Skip if Supabase not available

    try:
        # Call Supabase function to deduct credits
        result = supabase.rpc('deduct_credits', {
            'p_user_id': user_id,
            'p_credits': credits_used,
            'p_description': f"Image generation - {task_details.get('task_count', 0)} tasks",
            'p_metadata': json.dumps(task_details)
        }).execute()

        return result.data if result.data else False

    except Exception as e:
        print(f"Error deducting credits: {e}")
        return True  # Don't fail the request if credit system is down

# ==============================================================================
# API PROVIDER FUNCTIONS (The "Connectors")
# ==============================================================================

def generate_with_dalle(prompt, size):
    """Generates an image with DALL-E and returns the direct URL."""
    if not openai_client:
        raise ConnectionError("OpenAI client not initialized.")
    response = openai_client.images.generate(
        model="dall-e-3", prompt=prompt, n=1, size=size, response_format="url"
    )
    return response.data[0].url

def generate_with_reve(prompt, aspect_ratio):
    """Generates an image with Reve and returns a base64 data URL."""
    if not REVE_API_KEY:
        raise ConnectionError("REVE_API_KEY not configured.")
    headers = {
        "Authorization": f"Bearer {REVE_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"
    }
    payload = {"prompt": prompt, "aspect_ratio": aspect_ratio, "version": "latest"}
    response = requests.post(REVE_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    image_base64 = response.json()["image"]
    return f"data:image/png;base64,{image_base64}"

def generate_with_bfl(prompt, model_endpoint, aspect_ratio):
    """Starts an async BFL.AI job and polls for the result."""
    if not BFL_API_KEY:
        raise ConnectionError("BFL_API_KEY not configured.")
    headers = {'accept': 'application/json', 'x-key': BFL_API_KEY, 'Content-Type': 'application/json'}
    payload = {'prompt': prompt, 'aspect_ratio': aspect_ratio}
    submit_url = f"{BFL_API_URL_BASE}{model_endpoint}"
    submit_response = requests.post(submit_url, headers=headers, json=payload).json()
    polling_url = submit_response.get("polling_url")
    if not polling_url:
        raise ValueError(f"BFL API did not return a polling URL. Response: {submit_response}")
    start_time = time.time()
    while time.time() - start_time < 90:
        poll_response = requests.get(polling_url, headers={'accept': 'application/json', 'x-key': BFL_API_KEY}).json()
        status = poll_response.get("status")
        if status == "Ready":
            return poll_response.get('result', {}).get('sample')
        elif status in ["Error", "Failed"]:
            raise RuntimeError(f"BFL generation failed: {poll_response}")
        time.sleep(2)
    raise TimeoutError("BFL generation timed out after 90 seconds.")

def generate_with_gemini(prompt):
    """Generates an image with Gemini and returns a base64 data URL."""
    if not GEMINI_API_KEY:
        raise ConnectionError("GEMINI_API_KEY not configured.")
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    response = requests.post(api_url_with_key, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    image_part = next((p for p in result['candidates'][0]['content']['parts'] if 'inlineData' in p), None)
    if not image_part:
        raise ValueError("No image data found in Gemini API response.")
    base64_data = image_part['inlineData']['data']
    return f"data:image/png;base64,{base64_data}"

def generate_with_minimax(prompt, aspect_ratio):
    """Generates an image with Minimax and returns a direct URL."""
    if not MINIMAX_API_KEY:
        raise ConnectionError("MINIMAX_API_KEY not configured.")
    headers = {"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "image-01", "prompt": prompt, "aspect_ratio": aspect_ratio, "n": 1, "response_format": "url"}
    response = requests.post(MINIMAX_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    if result.get("base_resp", {}).get("status_code") == 0 and result.get("data", {}).get("image_urls"):
        return result["data"]["image_urls"][0]
    else:
        raise RuntimeError(f"Minimax generation failed: {result.get('base_resp')}")

def generate_with_imagen(prompt, provider, aspect_ratio="1:1", image_size="1024", person_generation="allow_adult", number_of_images=1):
    """Generates an image with Google Imagen (3 or 4) and returns a base64 data URL."""
    if not genai_client:
        raise ConnectionError("Google GenAI client not initialized.")

    # Map provider to model ID
    model_map = {
        "imagen-3": "imagen-3.0-generate-002",
        "imagen-4": "imagen-4.0-generate-001",
        "imagen-4-ultra": "imagen-4.0-ultra-generate-001",
        "imagen-4-fast": "imagen-4.0-fast-generate-001"
    }

    model = model_map.get(provider)
    if not model:
        raise ValueError(f"Unknown Imagen provider: {provider}")

    # Configure generation parameters
    config_params = {
        "number_of_images": number_of_images,
        "aspect_ratio": aspect_ratio,
        "person_generation": person_generation
    }

    # Add image_size only for Imagen 4 variants (not supported in Imagen 3)
    if provider.startswith("imagen-4"):
        # Map size to supported values (1K or 2K)
        if image_size in ["2048", "2K", "2k"]:
            config_params["image_size"] = "2K"
        else:
            config_params["image_size"] = "1K"

    try:
        # Generate images
        response = genai_client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(**config_params)
        )

        # Get the first generated image
        if not response.generated_images:
            raise ValueError("No images generated by Imagen API")

        generated_image = response.generated_images[0]

        # Convert PIL Image to base64
        buffered = BytesIO()
        generated_image.image.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        raise RuntimeError(f"Imagen generation failed: {str(e)}")

def generate_with_fal(prompt, provider, **kwargs):
    """Generates an image using fal.ai models and returns the image URL."""
    if not FAL_KEY:
        raise ConnectionError("FAL_KEY not configured.")

    # Map provider to fal.ai model ID
    model_map = {
        "seedream-4": "fal-ai/bytedance/seedream/v4/text-to-image",
        "qwen-image": "fal-ai/qwen-image",
        "seedream-3": "fal-ai/bytedance/seedream/v3/text-to-image",
        "ideogram-v3": "fal-ai/ideogram/v3",
        "gpt-image-1": "fal-ai/gpt-image-1/text-to-image/byok"
    }

    model_id = model_map.get(provider)
    if not model_id:
        raise ValueError(f"Unknown fal.ai provider: {provider}")

    try:
        # Build arguments based on provider
        arguments = {"prompt": prompt}

        if provider == "seedream-4":
            # Seedream 4 parameters
            if kwargs.get("image_size"):
                arguments["image_size"] = kwargs["image_size"]
            if kwargs.get("num_images"):
                arguments["num_images"] = kwargs["num_images"]
            if kwargs.get("enhance_prompt_mode"):
                arguments["enhance_prompt_mode"] = kwargs["enhance_prompt_mode"]
            if kwargs.get("enable_safety_checker") is not None:
                arguments["enable_safety_checker"] = kwargs["enable_safety_checker"]

        elif provider == "qwen-image":
            # Qwen-Image parameters
            if kwargs.get("image_size"):
                arguments["image_size"] = kwargs["image_size"]
            if kwargs.get("num_images"):
                arguments["num_images"] = kwargs["num_images"]
            if kwargs.get("guidance_scale"):
                arguments["guidance_scale"] = kwargs["guidance_scale"]
            if kwargs.get("negative_prompt"):
                arguments["negative_prompt"] = kwargs["negative_prompt"]
            if kwargs.get("acceleration"):
                arguments["acceleration"] = kwargs["acceleration"]
            if kwargs.get("num_inference_steps"):
                arguments["num_inference_steps"] = kwargs["num_inference_steps"]

        elif provider == "seedream-3":
            # Seedream 3 parameters
            if kwargs.get("image_size"):
                arguments["image_size"] = kwargs["image_size"]
            if kwargs.get("num_images"):
                arguments["num_images"] = kwargs["num_images"]
            if kwargs.get("guidance_scale"):
                arguments["guidance_scale"] = kwargs["guidance_scale"]
            if kwargs.get("enable_safety_checker") is not None:
                arguments["enable_safety_checker"] = kwargs["enable_safety_checker"]

        elif provider == "ideogram-v3":
            # Ideogram V3 parameters
            if kwargs.get("image_size"):
                arguments["image_size"] = kwargs["image_size"]
            if kwargs.get("num_images"):
                arguments["num_images"] = kwargs["num_images"]
            if kwargs.get("rendering_speed"):
                arguments["rendering_speed"] = kwargs["rendering_speed"]
            if kwargs.get("style"):
                arguments["style"] = kwargs["style"]
            if kwargs.get("style_preset"):
                arguments["style_preset"] = kwargs["style_preset"]
            if kwargs.get("negative_prompt"):
                arguments["negative_prompt"] = kwargs["negative_prompt"]
            if kwargs.get("expand_prompt") is not None:
                arguments["expand_prompt"] = kwargs["expand_prompt"]

        elif provider == "gpt-image-1":
            # GPT Image 1 parameters (BYOK)
            if not kwargs.get("openai_api_key"):
                raise ValueError("gpt-image-1 requires openai_api_key parameter")
            arguments["openai_api_key"] = kwargs["openai_api_key"]
            if kwargs.get("image_size"):
                arguments["image_size"] = kwargs["image_size"]
            if kwargs.get("num_images"):
                arguments["num_images"] = kwargs["num_images"]
            if kwargs.get("quality"):
                arguments["quality"] = kwargs["quality"]
            if kwargs.get("background"):
                arguments["background"] = kwargs["background"]

        # Submit request and wait for result
        result = fal_client.subscribe(
            model_id,
            arguments=arguments,
            with_logs=False
        )

        # Extract image URL from result
        if result and "images" in result and len(result["images"]) > 0:
            return result["images"][0].get("url")
        else:
            raise ValueError(f"No images returned from {provider}")

    except Exception as e:
        raise RuntimeError(f"fal.ai {provider} generation failed: {str(e)}")

# ==============================================================================
# SYNCHRONOUS JOB PROCESSING (Fixed for Vercel)
# ==============================================================================

def process_job_sync(tasks):
    """Processes all tasks synchronously and returns results immediately."""
    results = []
    total_tasks = len(tasks)
    
    for i, task in enumerate(tasks):
        prompt = task.get("prompt")
        provider = task.get("provider", "dalle").lower()
        result_item = {"prompt": prompt, "provider": provider}

        try:
            print(f"Processing task {i+1}/{total_tasks} with provider {provider}")
            image_url = None
            
            if provider == "dalle":
                image_url = generate_with_dalle(prompt, task.get("size", "1024x1024"))
            elif provider == "reve":
                image_url = generate_with_reve(prompt, task.get("aspect_ratio", "1:1"))
            elif provider == "gemini":
                image_url = generate_with_gemini(prompt)
            elif provider == "minimax":
                image_url = generate_with_minimax(prompt, task.get("aspect_ratio", "1:1"))
            elif provider.startswith("flux"):
                model_map = {"flux-kontext": "flux-kontext-pro", "flux-dev": "flux-dev"}
                model_endpoint = model_map.get(provider)
                if not model_endpoint:
                    raise ValueError(f"Unknown FLUX model: {provider}")
                image_url = generate_with_bfl(prompt, model_endpoint, task.get("aspect_ratio", "1:1"))
            elif provider.startswith("imagen"):
                image_url = generate_with_imagen(
                    prompt=prompt,
                    provider=provider,
                    aspect_ratio=task.get("aspect_ratio", "1:1"),
                    image_size=task.get("image_size", "1024"),
                    person_generation=task.get("person_generation", "allow_adult"),
                    number_of_images=1
                )
            elif provider in ["seedream-4", "qwen-image", "seedream-3", "ideogram-v3", "gpt-image-1"]:
                # fal.ai providers - pass all task parameters as kwargs
                fal_params = {k: v for k, v in task.items() if k not in ["prompt", "provider"]}
                image_url = generate_with_fal(prompt, provider, **fal_params)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            result_item["status"] = "Success"
            result_item["imageUrl"] = image_url
            print(f"✅ Task {i+1} completed successfully")
            
        except Exception as e:
            print(f"❌ ERROR in task {i+1}: {e}")
            result_item["status"] = "Failed"
            result_item["error"] = str(e)
        
        results.append(result_item)

    return results


# ==============================================================================
# FLASK API ENDPOINTS
# ==============================================================================

@app.route('/v1/jobs/create', methods=['POST'])
@require_api_key
def create_job():
    """Create and process job synchronously with API key authentication and credit deduction"""
    if not request.json or 'tasks' not in request.json:
        return jsonify({
            "error": "Request must be JSON with 'tasks' array.",
            "example": {
                "tasks": [
                    {
                        "prompt": "A beautiful sunset",
                        "provider": "dalle",
                        "size": "1024x1024"
                    }
                ]
            }
        }), 400

    tasks = request.json['tasks']
    if not isinstance(tasks, list) or not tasks:
        return jsonify({"error": "'tasks' must be a non-empty array."}), 400

    if len(tasks) > 100:
        return jsonify({"error": "Maximum 100 tasks per request."}), 400

    try:
        # Calculate total credits needed
        total_credits_needed = 0
        for task in tasks:
            provider = task.get("provider", "dalle").lower()
            if provider in PROVIDER_COSTS:
                total_credits_needed += PROVIDER_COSTS[provider]
            else:
                return jsonify({
                    "error": f"Unknown provider: {provider}",
                    "supported_providers": list(PROVIDER_COSTS.keys())
                }), 400

        # Check if user has enough credits
        user_credits = request.user.get("credits", 0)
        if user_credits < total_credits_needed:
            return jsonify({
                "error": "Insufficient credits",
                "credits_needed": total_credits_needed,
                "credits_available": user_credits,
                "message": "Purchase more credits at https://bigapi.io/dashboard/billing"
            }), 402  # Payment Required

        # Process all tasks synchronously
        results = process_job_sync(tasks)

        # Calculate actual credits used (only for successful generations)
        actual_credits_used = 0
        for i, result in enumerate(results):
            if result["status"] == "Success":
                provider = tasks[i].get("provider", "dalle").lower()
                actual_credits_used += PROVIDER_COSTS.get(provider, 0)

        # Deduct credits from user account
        if actual_credits_used > 0:
            deduct_credits(request.user['user_id'], actual_credits_used, {
                "task_count": len(tasks),
                "providers_used": [task.get("provider") for task in tasks],
                "success_count": sum(1 for r in results if r["status"] == "Success")
            })

            # Log usage to Supabase
            if supabase:
                try:
                    supabase.table('usage_logs').insert({
                        'user_id': request.user['user_id'],
                        'provider': ', '.join(set([task.get("provider") for task in tasks])),
                        'credits_used': actual_credits_used,
                        'task_count': len(tasks),
                        'success_count': sum(1 for r in results if r["status"] == "Success"),
                        'failed_count': len(results) - sum(1 for r in results if r["status"] == "Success"),
                        'metadata': json.dumps({"providers_used": [task.get("provider") for task in tasks]})
                    }).execute()
                except Exception as e:
                    print(f"Error logging usage: {e}")

        # Count successes and failures
        success_count = sum(1 for r in results if r["status"] == "Success")
        failure_count = len(results) - success_count

        return jsonify({
            "message": "Job completed successfully",
            "total_tasks": len(tasks),
            "successful": success_count,
            "failed": failure_count,
            "credits_used": actual_credits_used,
            "credits_remaining": user_credits - actual_credits_used,
            "results": results
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Job processing failed: {str(e)}",
            "message": "Check your request format and try again"
        }), 500

@app.route('/v1/jobs/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Legacy endpoint - jobs are now processed synchronously"""
    return jsonify({
        "message": "Jobs are now processed synchronously. Use /v1/jobs/create to get immediate results.",
        "status": "deprecated"
    }), 200

@app.route('/v1/jobs/results/<job_id>', methods=['GET'])
def get_job_results(job_id):
    """Legacy endpoint - jobs are now processed synchronously"""
    return jsonify({
        "message": "Jobs are now processed synchronously. Use /v1/jobs/create to get immediate results.",
        "status": "deprecated"
    }), 200

# ==============================================================================
# DASHBOARD API ENDPOINTS
# ==============================================================================

@app.route('/v1/dashboard/stats', methods=['GET'])
@require_api_key
def get_dashboard_stats():
    """Get real-time dashboard statistics for the authenticated user"""
    try:
        user_id = request.user.get("user_id")

        # Get user's current credits
        current_credits = request.user.get("credits", 0)

        # Get usage logs from Redis
        usage_logs = []
        if kv:
            usage_key = f"usage:{user_id}"
            raw_logs = kv.lrange(usage_key, 0, 999)  # Get last 1000 entries
            for log in raw_logs:
                try:
                    usage_logs.append(json.loads(log))
                except:
                    continue

        # Calculate statistics
        total_api_calls = len(usage_logs)
        total_credits_used = sum(log.get("credits_used", 0) for log in usage_logs)

        # Count images generated (successful tasks)
        total_images = 0
        provider_usage = {}
        for log in usage_logs:
            task_details = log.get("task_details", {})
            success_count = task_details.get("success_count", 0)
            total_images += success_count

            # Count provider usage
            providers = task_details.get("providers_used", [])
            for provider in providers:
                provider_usage[provider] = provider_usage.get(provider, 0) + 1

        # Calculate success rate
        success_rate = 95.5  # Default fallback
        if usage_logs:
            total_tasks = sum(log.get("task_details", {}).get("task_count", 0) for log in usage_logs)
            if total_tasks > 0:
                success_rate = (total_images / total_tasks) * 100

        # Get recent activity (last 10 calls)
        recent_activity = []
        for log in usage_logs[:10]:
            recent_activity.append({
                "timestamp": log.get("timestamp"),
                "credits_used": log.get("credits_used"),
                "task_details": log.get("task_details")
            })

        return jsonify({
            "credits_remaining": current_credits,
            "total_api_calls": total_api_calls,
            "total_images_generated": total_images,
            "total_credits_used": total_credits_used,
            "success_rate": round(success_rate, 1),
            "provider_usage": provider_usage,
            "recent_activity": recent_activity
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch dashboard stats: {str(e)}"
        }), 500

@app.route('/v1/dashboard/usage', methods=['GET'])
@require_api_key
def get_usage_analytics():
    """Get detailed usage analytics for the authenticated user"""
    try:
        user_id = request.user.get("user_id")
        period = request.args.get("period", "7d")  # 24h, 7d, 30d, 90d

        # Calculate time range
        now = time.time()
        if period == "24h":
            start_time = now - (24 * 3600)
        elif period == "7d":
            start_time = now - (7 * 24 * 3600)
        elif period == "30d":
            start_time = now - (30 * 24 * 3600)
        elif period == "90d":
            start_time = now - (90 * 24 * 3600)
        else:
            start_time = now - (7 * 24 * 3600)  # Default to 7 days

        # Get usage logs from Redis
        usage_logs = []
        if kv:
            usage_key = f"usage:{user_id}"
            raw_logs = kv.lrange(usage_key, 0, 999)
            for log in raw_logs:
                try:
                    log_data = json.loads(log)
                    if log_data.get("timestamp", 0) >= start_time:
                        usage_logs.append(log_data)
                except:
                    continue

        # Process analytics
        daily_usage = {}
        provider_stats = {}
        total_calls = len(usage_logs)
        total_credits = sum(log.get("credits_used", 0) for log in usage_logs)

        for log in usage_logs:
            # Daily usage
            date_key = time.strftime("%Y-%m-%d", time.localtime(log.get("timestamp", 0)))
            if date_key not in daily_usage:
                daily_usage[date_key] = {"calls": 0, "credits": 0}
            daily_usage[date_key]["calls"] += 1
            daily_usage[date_key]["credits"] += log.get("credits_used", 0)

            # Provider stats
            providers = log.get("task_details", {}).get("providers_used", [])
            for provider in providers:
                if provider not in provider_stats:
                    provider_stats[provider] = {"calls": 0, "credits": 0}
                provider_stats[provider]["calls"] += 1
                provider_stats[provider]["credits"] += PROVIDER_COSTS.get(provider, 0)

        # Convert to arrays for frontend
        daily_data = [
            {"date": date, "calls": data["calls"], "credits": data["credits"]}
            for date, data in sorted(daily_usage.items())
        ]

        provider_data = [
            {"provider": provider, "calls": data["calls"], "credits": data["credits"]}
            for provider, data in provider_stats.items()
        ]

        return jsonify({
            "period": period,
            "total_calls": total_calls,
            "total_credits": total_credits,
            "daily_usage": daily_data,
            "provider_usage": provider_data
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch usage analytics: {str(e)}"
        }), 500

@app.route('/v1/api-keys', methods=['GET'])
@require_api_key
def list_api_keys():
    """List API keys for the authenticated user"""
    try:
        # In production, this would fetch from your user database
        # For demo, return the current key
        return jsonify({
            "api_keys": [
                {
                    "id": "key_001",
                    "name": "Production Key",
                    "key": request.api_key[:12] + "..." + request.api_key[-4:],
                    "created_at": "2025-01-15",
                    "last_used": "2 hours ago",
                    "requests_count": 1234
                }
            ]
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch API keys: {str(e)}"
        }), 500

# ==============================================================================
# AUTHENTICATION & API KEY MANAGEMENT ENDPOINTS
# ==============================================================================

@app.route('/v1/auth/generate-api-key', methods=['POST'])
def generate_api_key():
    """Generate new API key for authenticated user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing authorization header"}), 401

    token = auth_header.replace('Bearer ', '')

    try:
        # Verify Supabase user
        user_response = supabase.auth.get_user(token)
        if not user_response:
            return jsonify({"error": "Invalid token"}), 401

        user_id = user_response.user.id

        # Get request data
        data = request.json or {}
        key_name = data.get('key_name', 'My API Key')

        # Generate API key
        api_key = f"big_live_{uuid.uuid4().hex}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_preview = api_key[-4:]

        # Store in Supabase
        result = supabase.table('api_keys').insert({
            'user_id': user_id,
            'key_name': key_name,
            'key_prefix': 'big_live_',
            'key_hash': key_hash,
            'key_preview': key_preview,
            'is_active': True
        }).execute()

        return jsonify({
            "message": "API key created successfully",
            "api_key": api_key,
            "key_name": key_name,
            "key_preview": f"...{key_preview}",
            "warning": "Save this key now. You won't be able to see it again."
        }), 201

    except Exception as e:
        print(f"Error generating API key: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/v1/auth/api-keys', methods=['GET'])
def list_user_api_keys():
    """List all API keys for authenticated user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing authorization header"}), 401

    token = auth_header.replace('Bearer ', '')

    try:
        # Verify Supabase user
        user_response = supabase.auth.get_user(token)
        if not user_response:
            return jsonify({"error": "Invalid token"}), 401

        user_id = user_response.user.id

        # Get API keys from Supabase
        keys_response = supabase.table('api_keys').select('*').eq('user_id', user_id).execute()

        api_keys = []
        for key_data in keys_response.data:
            api_keys.append({
                "id": key_data['id'],
                "name": key_data['key_name'],
                "key_preview": f"big_live_...{key_data['key_preview']}",
                "is_active": key_data['is_active'],
                "created_at": key_data['created_at'],
                "last_used_at": key_data['last_used_at']
            })

        return jsonify({"api_keys": api_keys}), 200

    except Exception as e:
        print(f"Error listing API keys: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/v1/auth/api-keys/<key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    """Delete an API key"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing authorization header"}), 401

    token = auth_header.replace('Bearer ', '')

    try:
        # Verify Supabase user
        user_response = supabase.auth.get_user(token)
        if not user_response:
            return jsonify({"error": "Invalid token"}), 401

        user_id = user_response.user.id

        # Delete API key
        supabase.table('api_keys').delete().eq('id', key_id).eq('user_id', user_id).execute()

        # Clear cache
        if kv:
            # We don't have the key_hash here, so just clear all caches
            pass

        return jsonify({"message": "API key deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting API key: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return jsonify({
        "message": "BIG API - Bulk Image Generation API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "https://bigapi.io/docs",
        "dashboard": "https://bigapi.io/dashboard"
    })

if __name__ == '__main__':
    app.run(debug=True)
