#!/bin/bash
# Setup secrets for DigitalOcean App Platform
# Run this before deployment to configure environment secrets

set -e

echo "=========================================="
echo "Fyn RAG - Configure Secrets"
echo "=========================================="

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl CLI not installed"
    exit 1
fi

APP_NAME="fyn-rag"

# Get App ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "${APP_NAME}" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo "Error: App not found. Deploy first using deploy.sh"
    exit 1
fi

echo "App ID: $APP_ID"
echo ""

# Function to set secret
set_secret() {
    local key=$1
    local value=$2

    if [ -z "$value" ]; then
        echo "Skipping $key (empty value)"
        return
    fi

    echo "Setting $key..."
    # Note: This is a placeholder - actual secret management
    # should be done through DigitalOcean console or API
}

echo ""
echo "=========================================="
echo "Configure the following secrets in DigitalOcean Console:"
echo "=========================================="
echo ""
echo "1. Go to: https://cloud.digitalocean.com/apps"
echo "2. Select your app: $APP_NAME"
echo "3. Go to Settings -> App-Level Environment Variables"
echo "4. Add these secrets:"
echo ""
echo "   DATABASE_URL = (auto-configured from managed DB)"
echo "   OPENAI_API_KEY = sk-proj-..."
echo "   ANTHROPIC_API_KEY = sk-ant-api03-..."
echo "   FRED_API_KEY = e63bf4ad4b21136be0b68c27e7e510d9"
echo "   TRADING_ECONOMICS_API_KEY = DB5A57F91781451:A8A888DFE5F9495"
echo "   REDDIT_CLIENT_ID = WBSAJYxDSmSCsCkpamtDEg"
echo "   REDDIT_CLIENT_SECRET = gjE8dKmJCXWBbaAG5Mr6zCA1itE7mg"
echo ""
echo "=========================================="
