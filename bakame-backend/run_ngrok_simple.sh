#!/bin/bash

# Simple ngrok runner for Telnyx webhook testing

echo "================================================================"
echo "STARTING NGROK TUNNEL FOR TELNYX WEBHOOK TESTING"
echo "================================================================"
echo ""
echo "📌 This will create a temporary public URL for your backend"
echo "📌 Use this URL in your Telnyx portal for testing"
echo ""
echo "Starting ngrok on port 8000..."
echo "================================================================"
echo ""

cd /home/runner/workspace/bakame-backend
./ngrok http 8000