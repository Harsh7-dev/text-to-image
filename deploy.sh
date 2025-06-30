#!/bin/bash

# Text-to-Image API Deployment Script
echo "🚀 Text-to-Image API Deployment Helper"
echo "======================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your Replicate API token:"
    echo "REPLICATE_API_TOKEN=r8_your_actual_token_here"
    exit 1
fi

# Check if REPLICATE_API_TOKEN is set
if ! grep -q "REPLICATE_API_TOKEN=r8_" .env; then
    echo "❌ Error: REPLICATE_API_TOKEN not properly set in .env file!"
    echo "Please update your .env file with a valid Replicate API token."
    exit 1
fi

echo "✅ Environment configuration looks good!"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Text-to-Image API"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
echo "🎯 Next Steps for Railway Deployment:"
echo "====================================="
echo ""
echo "1. Push your code to GitHub:"
echo "   git remote add origin <your-github-repo-url>"
echo "   git push -u origin main"
echo ""
echo "2. Deploy to Railway:"
echo "   - Go to https://railway.app"
echo "   - Click 'New Project'"
echo "   - Select 'Deploy from GitHub repo'"
echo "   - Choose your repository"
echo ""
echo "3. Set Environment Variables in Railway:"
echo "   - Go to your project's 'Variables' tab"
echo "   - Add: REPLICATE_API_TOKEN = <your-token>"
echo ""
echo "4. Deploy and test:"
echo "   - Railway will automatically deploy your app"
echo "   - Visit your app URL to test the web interface"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "🔗 Useful Links:"
echo "   - Railway: https://railway.app"
echo "   - Replicate: https://replicate.com/account/api-tokens"
echo "   - This project: https://github.com/yourusername/text-to-image-api" 