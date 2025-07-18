#!/bin/bash

# Simple Google Cloud Monitoring Alerts Setup for ProfitPoke AI
set -e

PROJECT_ID="profit-poke"
SERVICE_NAME="profitpoke-api"
REGION="us-central1"
NOTIFICATION_EMAIL="hotelapp.01@gmail.com"

echo "🚨 Setting up Google Cloud Monitoring alerts for ProfitPoke AI..."

# Enable required APIs
echo "📊 Enabling required APIs..."
gcloud services enable monitoring.googleapis.com --quiet

# Create notification channel
echo "📧 Creating email notification channel..."
NOTIFICATION_CHANNEL_ID=$(gcloud alpha monitoring channels create \
    --display-name="ProfitPoke AI Alerts" \
    --type=email \
    --channel-labels=email_address=${NOTIFICATION_EMAIL} \
    --format="value(name)" --quiet)

echo "✅ Created notification channel: ${NOTIFICATION_CHANNEL_ID}"

echo ""
echo "✅ Monitoring setup completed!"
echo ""
echo "📊 Next steps:"
echo "1. Go to Google Cloud Console Monitoring: https://console.cloud.google.com/monitoring"
echo "2. Navigate to Alerting > Create Policy to set up custom alerts"
echo "3. Use these metrics for your alerts:"
echo ""
echo "🔥 5xx Error Rate Alert:"
echo "   Resource: Cloud Run Revision"
echo "   Metric: run.googleapis.com/request_count"
echo "   Filter: response_code_class=\"5xx\""
echo "   Threshold: > 5 errors per minute"
echo ""
echo "⚡ High Latency Alert:"
echo "   Resource: Cloud Run Revision"
echo "   Metric: run.googleapis.com/request_latencies"
echo "   Threshold: > 10000ms (10 seconds)"
echo ""
echo "🔥 High CPU Alert:"
echo "   Resource: Cloud Run Revision"  
echo "   Metric: run.googleapis.com/container/cpu/utilizations"
echo "   Threshold: > 80%"
echo ""
echo "💾 High Memory Alert:"
echo "   Resource: Cloud Run Revision"
echo "   Metric: run.googleapis.com/container/memory/utilizations"
echo "   Threshold: > 85%"
echo ""
echo "📧 Email notifications will be sent to: ${NOTIFICATION_EMAIL}"
