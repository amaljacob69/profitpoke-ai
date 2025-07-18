#!/bin/bash

# Google Cloud Monitoring Alerts Setup for ProfitPoke AI
# This script creates monitoring alerts for your Cloud Run service

set -e

PROJECT_ID="profit-poke"
SERVICE_NAME="profitpoke-api"
REGION="us-central1"
NOTIFICATION_EMAIL="hotelapp.01@gmail.com"

echo "🚨 Setting up Google Cloud Monitoring alerts for ProfitPoke AI..."

# Enable Cloud Monitoring API
echo "📊 Enabling Cloud Monitoring API..."
gcloud services enable monitoring.googleapis.com

# Create notification channel for email alerts
echo "📧 Creating email notification channel..."
NOTIFICATION_CHANNEL=$(gcloud alpha monitoring channels create \
    --display-name="ProfitPoke AI Alerts" \
    --type=email \
    --channel-labels=email_address=${NOTIFICATION_EMAIL} \
    --format="value(name)" 2>/dev/null | tail -1)

echo "✅ Created notification channel: ${NOTIFICATION_CHANNEL}"

# Alert 1: 5xx Error Rate Spike
echo "🔥 Creating 5xx error rate alert..."
cat > /tmp/5xx-error-alert.yaml << EOF
displayName: "ProfitPoke AI - High 5xx Error Rate"
documentation:
  content: "5xx error rate is above 5% for ProfitPoke AI service"
conditions:
- displayName: "5xx error rate condition"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="${SERVICE_NAME}" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
    comparison: COMPARISON_GREATER_THAN
    thresholdValue: 5
    duration: 300s
    aggregations:
    - alignmentPeriod: 60s
      perSeriesAligner: ALIGN_RATE
      crossSeriesReducer: REDUCE_SUM
      groupByFields:
      - resource.labels.service_name
combiner: OR
enabled: true
notificationChannels:
- ${NOTIFICATION_CHANNEL}
alertStrategy:
  autoClose: 1800s
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/5xx-error-alert.yaml

# Alert 2: High Latency for /recommend endpoint
echo "⚡ Creating high latency alert for /recommend endpoint..."
cat > /tmp/high-latency-alert.yaml << EOF
displayName: "ProfitPoke AI - High Latency on /recommend"
documentation:
  content: "Response time for /recommend endpoint is above 10 seconds"
conditions:
- displayName: "High latency condition"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="${SERVICE_NAME}" AND metric.type="run.googleapis.com/request_latencies"'
    comparison: COMPARISON_GREATER_THAN
    thresholdValue: 10000
    duration: 300s
    aggregations:
    - alignmentPeriod: 60s
      perSeriesAligner: ALIGN_DELTA
      crossSeriesReducer: REDUCE_PERCENTILE_95
      groupByFields:
      - resource.labels.service_name
combiner: OR
enabled: true
notificationChannels:
- ${NOTIFICATION_CHANNEL}
alertStrategy:
  autoClose: 1800s
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/high-latency-alert.yaml

# Alert 3: High CPU Usage
echo "🔥 Creating high CPU usage alert..."
cat > /tmp/high-cpu-alert.yaml << EOF
displayName: "ProfitPoke AI - High CPU Usage"
documentation:
  content: "CPU utilization is above 80% for ProfitPoke AI service"
conditions:
- displayName: "High CPU condition"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="${SERVICE_NAME}" AND metric.type="run.googleapis.com/container/cpu/utilizations"'
    comparison: COMPARISON_GREATER_THAN
    thresholdValue: 0.8
    duration: 300s
    aggregations:
    - alignmentPeriod: 60s
      perSeriesAligner: ALIGN_MEAN
      crossSeriesReducer: REDUCE_MEAN
      groupByFields:
      - resource.labels.service_name
combiner: OR
enabled: true
notificationChannels:
- ${NOTIFICATION_CHANNEL}
alertStrategy:
  autoClose: 1800s
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/high-cpu-alert.yaml

# Alert 4: High Memory Usage
echo "💾 Creating high memory usage alert..."
cat > /tmp/high-memory-alert.yaml << EOF
displayName: "ProfitPoke AI - High Memory Usage"
documentation:
  content: "Memory utilization is above 85% for ProfitPoke AI service"
conditions:
- displayName: "High memory condition"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="${SERVICE_NAME}" AND metric.type="run.googleapis.com/container/memory/utilizations"'
    comparison: COMPARISON_GREATER_THAN
    thresholdValue: 0.85
    duration: 300s
    aggregations:
    - alignmentPeriod: 60s
      perSeriesAligner: ALIGN_MEAN
      crossSeriesReducer: REDUCE_MEAN
      groupByFields:
      - resource.labels.service_name
combiner: OR
enabled: true
notificationChannels:
- ${NOTIFICATION_CHANNEL}
alertStrategy:
  autoClose: 1800s
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/high-memory-alert.yaml

# Alert 5: Service Availability
echo "🌐 Creating service availability alert..."
cat > /tmp/availability-alert.yaml << EOF
displayName: "ProfitPoke AI - Service Down"
documentation:
  content: "ProfitPoke AI service is not responding or has low request rate"
conditions:
- displayName: "Low request rate condition"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND resource.labels.service_name="${SERVICE_NAME}" AND metric.type="run.googleapis.com/request_count"'
    comparison: COMPARISON_LESS_THAN
    thresholdValue: 1
    duration: 600s
    aggregations:
    - alignmentPeriod: 60s
      perSeriesAligner: ALIGN_RATE
      crossSeriesReducer: REDUCE_SUM
      groupByFields:
      - resource.labels.service_name
combiner: OR
enabled: true
notificationChannels:
- ${NOTIFICATION_CHANNEL}
alertStrategy:
  autoClose: 1800s
EOF

gcloud alpha monitoring policies create --policy-from-file=/tmp/availability-alert.yaml

# Cleanup temporary files
rm -f /tmp/*-alert.yaml

echo "✅ All monitoring alerts have been created successfully!"
echo ""
echo "📊 Monitoring Dashboard: https://console.cloud.google.com/monitoring/dashboards"
echo "🚨 Alert Policies: https://console.cloud.google.com/monitoring/alerting/policies"
echo "📧 Notifications will be sent to: ${NOTIFICATION_EMAIL}"
echo ""
echo "🔧 Alert Summary:"
echo "- 5xx Error Rate > 5% for 5 minutes"
echo "- Request Latency > 10 seconds for 5 minutes"
echo "- CPU Usage > 80% for 5 minutes"
echo "- Memory Usage > 85% for 5 minutes"
echo "- Service Down (no requests for 10 minutes)"
