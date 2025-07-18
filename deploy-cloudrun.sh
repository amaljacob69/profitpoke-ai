#!/bin/bash

# Google Cloud Run Deployment Script for ProfitPoke AI
# This script deploys your Flask app to Google Cloud Run

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="profitpoke-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Starting Cloud Run deployment for ProfitPoke AI..."

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please authenticate with Google Cloud..."
    gcloud auth login
fi

# Set the project
echo "📋 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build the Docker image
echo "🏗️  Building Docker image..."
docker build -t ${IMAGE_NAME} .

# Configure Docker to use gcloud as a credential helper
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker

# Push the image to Container Registry
echo "📤 Pushing image to Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_NAME} \
    --platform=managed \
    --region=${REGION} \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --max-instances=10 \
    --set-env-vars="FLASK_ENV=production" \
    --set-env-vars="KITE_API_KEY=${KITE_API_KEY}" \
    --set-env-vars="KITE_API_SECRET=${KITE_API_SECRET}" \
    --set-env-vars="GROK_API_KEY=${GROK_API_KEY}" \
    --set-env-vars="FLASK_SECRET_KEY=${FLASK_SECRET_KEY}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform=managed \
    --region=${REGION} \
    --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "📝 Next steps:"
echo "1. Update your Firebase hosting configuration with this URL"
echo "2. Test the health endpoint: ${SERVICE_URL}/health"
echo "3. Deploy Firebase hosting: firebase deploy --only hosting"
echo ""
echo "🔧 To update environment variables later:"
echo "gcloud run services update ${SERVICE_NAME} \\"
echo "    --region=${REGION} \\"
echo "    --set-env-vars=\"KEY=value\""
