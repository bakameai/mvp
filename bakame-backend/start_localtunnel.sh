#!/bin/bash

echo "================================================================"
echo "🚇 LOCALTUNNEL FOR TELNYX WEBHOOK TESTING"
echo "================================================================"
echo ""
echo "Starting LocalTunnel on port 8000..."
echo "This will create a public URL without requiring any signup!"
echo ""
echo "================================================================"

# Start localtunnel
npx localtunnel --port 8000 --subdomain bakame-telnyx-test 2>&1