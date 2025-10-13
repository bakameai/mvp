#!/usr/bin/env python3
"""
Start ngrok and display the public URL for Telnyx webhook testing
"""

import subprocess
import json
import time
import requests
import sys

def start_ngrok():
    """Start ngrok in the background and get the public URL"""
    
    print("🚀 Starting ngrok tunnel on port 8000...")
    print("-" * 60)
    
    # Start ngrok in the background
    process = subprocess.Popen(
        ['./ngrok', 'http', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd='/home/runner/workspace/bakame-backend'
    )
    
    # Give ngrok time to start
    time.sleep(3)
    
    try:
        # Get the public URL from ngrok's API
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        
        # Find the HTTPS tunnel
        https_url = None
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                https_url = tunnel['public_url']
                break
        
        if https_url:
            print(f"✅ Ngrok tunnel created successfully!")
            print(f"\n📍 Public URL: {https_url}")
            print(f"\n🔗 Telnyx Webhook URL: {https_url}/telnyx/incoming")
            print("-" * 60)
            print("\n📋 INSTRUCTIONS FOR TELNYX:")
            print(f"1. Copy this URL: {https_url}/telnyx/incoming")
            print("2. Go to your Telnyx Portal")
            print("3. Update your phone number's webhook URL")
            print("4. Select 'Call Control' and 'API v2'")
            print("5. Save the configuration")
            print("\n⚠️  This URL is temporary and will change when ngrok restarts!")
            print("-" * 60)
            
            # Test the URL
            print("\n🧪 Testing the public URL...")
            test_response = requests.post(
                f"{https_url}/telnyx/incoming",
                json={"test": "ping"},
                timeout=5
            )
            
            if test_response.status_code == 200:
                print("✅ Webhook endpoint is reachable from the internet!")
                print(f"Response: {test_response.json()}")
            else:
                print(f"⚠️  Got status {test_response.status_code}")
                
        else:
            print("❌ Could not find HTTPS tunnel URL")
            print("Check if ngrok is running properly")
            
    except Exception as e:
        print(f"❌ Error getting ngrok URL: {str(e)}")
        print("\nTrying alternative method...")
        print("Run: cd bakame-backend && ./ngrok http 8000")
        print("Then check the URL in the ngrok interface")
    
    return process

if __name__ == "__main__":
    print("=" * 60)
    print("NGROK TUNNEL FOR TELNYX TESTING")
    print("=" * 60)
    
    try:
        ngrok_process = start_ngrok()
        
        print("\n✅ Ngrok is running in the background")
        print("Press Ctrl+C to stop the tunnel")
        print("-" * 60)
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping ngrok...")
        if 'ngrok_process' in locals():
            ngrok_process.terminate()
        print("✅ Ngrok stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)