#!/usr/bin/env python3
"""
Test script for the Telegram webhook
"""

import requests
import json

def test_webhook():
    """Test the webhook endpoint"""
    webhook_url = "https://geekscomputer232323.pythonanywhere.com/webhook/"
    
    # Test data (simulating a Telegram message)
    test_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "/start"
        }
    }
    
    try:
        print("🔄 Testing webhook...")
        print(f"URL: {webhook_url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook()
