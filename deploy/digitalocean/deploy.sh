#!/bin/bash
# DigitalOcean Deployment Script for Fyn RAG
# Usage: ./deploy.sh

set -e

echo "=========================================="
echo "Fyn RAG - DigitalOcean Deployment"
echo "=========================================="

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Error: doctl CLI not installed"
    echo "Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check authentication
if ! doctl auth list &> /dev/null; then
    echo "Error: Not authenticated with DigitalOcean"
    echo "Run: doctl auth init"
    exit 1
fi

# Variables
APP_NAME="fyn-rag"
SPEC_FILE="./app.yaml"

echo "Checking existing app..."
if doctl apps list --format Name --no-header | grep -q "^${APP_NAME}$"; then
    echo "App exists. Updating..."
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "${APP_NAME}" | awk '{print $1}')
    doctl apps update $APP_ID --spec $SPEC_FILE
else
    echo "Creating new app..."
    doctl apps create --spec $SPEC_FILE
fi

echo "=========================================="
echo "Deployment initiated!"
echo "=========================================="
echo ""
echo "Monitor deployment:"
echo "  doctl apps list"
echo ""
echo "View logs:"
echo "  doctl apps logs $APP_NAME"
echo ""
echo "Get app URL:"
echo "  doctl apps get $APP_NAME --format DefaultIngress"
