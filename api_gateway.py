import os
import time
import json
import uuid
import requests
from flask import Flask, request, jsonify, redirect
from openai import OpenAI
import redis

# ==============================================================================
# INITIALIZATION
# ==============================================================================

app = Flask(__name__)

# --- Connect to Vercel KV (Redis) for Job Tracking ---
try:
    kv = redis.from_url(os.environ.get("KV_URL"))
except Exception as e:
    print(f"CRITICAL: Could not connect to Vercel KV. Job processing will fail. Error: {e}")
    kv = None

# --- Initialize API Clients ---
try:
    openai_client = OpenAI()
except Exception as e:
    print(f"Warning: OpenAI client failed to initialize. DALL-E will be unavailable. Error: {e}")
    openai_client = None

# --- API Keys and Endpoints ---
BFL_API_KEY = os.environ.get("BFL_API_KEY")
REVE_API_KEY = os.environ.get("REVE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")

BFL_API_URL_BASE = "https://api.bfl.ai/v1/"
REVE_API_URL = "https://api.reve.com/v1/image/create"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image-preview:generateContent"
MINIMAX_API_URL = "https://api.minimax.io/v1/image_generation"

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
def create_job():
    """Create and process job synchronously - FIXED for Vercel"""
    if not request.json or 'tasks' not in request.json: 
        return jsonify({"error": "Request must be JSON with 'tasks' array."}), 400
    
    tasks = request.json['tasks']
    if not isinstance(tasks, list) or not tasks: 
        return jsonify({"error": "'tasks' must be a non-empty array."}), 400

    try:
        # Process all tasks synchronously
        results = process_job_sync(tasks)
        
        # Count successes and failures
        success_count = sum(1 for r in results if r["status"] == "Success")
        failure_count = len(results) - success_count
        
        return jsonify({
            "message": "Job completed successfully",
            "total_tasks": len(tasks),
            "successful": success_count,
            "failed": failure_count,
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Job processing failed: {str(e)}",
            "message": "Check your API keys and try again"
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

@app.route('/')
def index():
    return "Multi-Provider Bulk Image Generation API is running! (Synchronous Mode)"

if __name__ == '__main__':
    app.run(debug=True)
