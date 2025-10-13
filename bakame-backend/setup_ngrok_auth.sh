#!/bin/bash

echo "================================================================"
echo "NGROK AUTHENTICATION SETUP"
echo "================================================================"
echo ""
echo "To use ngrok, you need to:"
echo ""
echo "1. Sign up for a free account at:"
echo "   https://dashboard.ngrok.com/signup"
echo ""
echo "2. Get your authtoken from:"
echo "   https://dashboard.ngrok.com/get-started/your-authtoken"
echo ""
echo "3. Run this command with your token:"
echo "   ./ngrok config add-authtoken YOUR_AUTHTOKEN_HERE"
echo ""
echo "4. Then start ngrok:"
echo "   ./ngrok http 8000"
echo ""
echo "================================================================"

# If you have your authtoken, uncomment and update this line:
# ./ngrok config add-authtoken YOUR_AUTHTOKEN_HERE

# Then run ngrok
# ./ngrok http 8000