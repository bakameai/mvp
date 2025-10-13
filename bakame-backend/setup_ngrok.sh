#!/bin/bash

# Setup ngrok for testing Telnyx webhooks

echo "Setting up ngrok for webhook testing..."

# Download ngrok if it doesn't exist
if [ ! -f "ngrok" ]; then
    echo "Downloading ngrok..."
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    rm ngrok-v3-stable-linux-amd64.tgz
    echo "✅ ngrok downloaded"
else
    echo "✅ ngrok already exists"
fi

# Make executable
chmod +x ngrok

echo ""
echo "Starting ngrok tunnel on port 8000..."
echo "Press Ctrl+C to stop the tunnel"
echo ""

# Start ngrok
./ngrok http 8000 --log stdout