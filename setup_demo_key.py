#!/usr/bin/env python3
"""
Demo API Key Setup for BIG API
This script creates a demo API key with credits for testing
"""

import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

def setup_demo_key():
    """Creates a demo API key with 10,000 credits"""

    # Connect to Redis
    try:
        kv = redis.from_url(os.environ.get("KV_URL"))
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return

    # Demo API key and user data
    demo_api_key = "big_live_demo_key_12345678901234567890"
    demo_user_data = {
        "user_id": "demo_user_001",
        "credits": 10000,
        "plan": "pro",
        "created_at": "2025-01-20",
        "last_used": "2025-01-20"
    }

    try:
        # Store demo API key
        kv.set(f"api_key:{demo_api_key}", json.dumps(demo_user_data))
        print(f"✅ Created demo API key: {demo_api_key}")
        print(f"✅ User ID: {demo_user_data['user_id']}")
        print(f"✅ Credits: {demo_user_data['credits']:,}")

        # Add some demo usage logs
        usage_logs = [
            {
                "timestamp": 1737340800,  # Jan 20, 2025
                "user_id": "demo_user_001",
                "api_key": "big_live_demo...",
                "credits_used": 10,
                "task_details": {
                    "task_count": 1,
                    "providers_used": ["dalle"],
                    "success_count": 1
                }
            },
            {
                "timestamp": 1737340200,  # 10 minutes earlier
                "user_id": "demo_user_001",
                "api_key": "big_live_demo...",
                "credits_used": 8,
                "task_details": {
                    "task_count": 1,
                    "providers_used": ["flux-kontext"],
                    "success_count": 1
                }
            },
            {
                "timestamp": 1737339600,  # 20 minutes earlier
                "user_id": "demo_user_001",
                "api_key": "big_live_demo...",
                "credits_used": 5,
                "task_details": {
                    "task_count": 1,
                    "providers_used": ["gemini"],
                    "success_count": 1
                }
            }
        ]

        # Add usage logs to Redis
        usage_key = f"usage:{demo_user_data['user_id']}"
        for log in usage_logs:
            kv.lpush(usage_key, json.dumps(log))

        print(f"✅ Added {len(usage_logs)} demo usage logs")

        print("\n🎉 Demo setup complete!")
        print("\n📋 Test the API:")
        print(f"   curl -X POST https://ai-image-bulk-mauf82umw-rishithay265s-projects.vercel.app/v1/jobs/create \\")
        print(f"     -H 'Authorization: Bearer {demo_api_key}' \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"tasks\": [{{\"prompt\": \"A test image\", \"provider\": \"dalle\", \"size\": \"1024x1024\"}}]}}'")

        print("\n📊 Check dashboard stats:")
        print(f"   curl -X GET https://ai-image-bulk-mauf82umw-rishithay265s-projects.vercel.app/v1/dashboard/stats \\")
        print(f"     -H 'Authorization: Bearer {demo_api_key}'")

    except Exception as e:
        print(f"❌ Failed to setup demo key: {e}")

if __name__ == "__main__":
    setup_demo_key()
