# Google Cloud Run + Firebase Hosting Deployment Guide

This guide walks you through deploying ProfitPoke AI to Google Cloud Run with Firebase Hosting integration for a serverless, scalable solution.

## Prerequisites

1. **Google Cloud Platform Account** with billing enabled
2. **Firebase Project** (can be the same as GCP project)
3. **Docker Desktop** installed and running
4. **Google Cloud CLI** installed
5. **Firebase CLI** installed
6. **Git** with your code pushed to a repository

## Step 1: Setup Google Cloud Platform

1. **Create or Select a GCP Project**:
   ```bash
   # List existing projects
   gcloud projects list
   
   # Create new project (optional)
   gcloud projects create your-project-id --name="ProfitPoke AI"
   
   # Set active project
   gcloud config set project your-project-id
   ```

2. **Enable Billing** for your project in the GCP Console

3. **Install and Initialize Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase init hosting
   ```

## Step 2: Configure Environment Variables

Create a `.env` file locally (already exists) with your API keys:
```env
FLASK_SECRET_KEY=your_flask_secret_key_here
KITE_API_KEY=your_kite_api_key_here
KITE_API_SECRET=your_kite_api_secret_here
GROK_API_KEY=your_grok_api_key_here
FLASK_ENV=production
```

## Step 3: Deploy to Cloud Run

### Option A: Using the Automated Script

1. **Update the deployment script**:
   Edit `deploy-cloudrun.sh` and set your project ID:
   ```bash
   PROJECT_ID="your-actual-project-id"  # Replace with your project ID
   ```

2. **Export environment variables**:
   ```bash
   export KITE_API_KEY="your_kite_api_key_here"
   export KITE_API_SECRET="your_kite_api_secret_here"
   export GROK_API_KEY="your_grok_api_key_here"
   export FLASK_SECRET_KEY="your_flask_secret_key_here"
   ```

3. **Run the deployment script**:
   ```bash
   ./deploy-cloudrun.sh
   ```

### Option B: Manual Deployment

1. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Build and push Docker image**:
   ```bash
   # Build the image
   docker build -t gcr.io/your-project-id/profitpoke-api .
   
   # Configure Docker auth
   gcloud auth configure-docker
   
   # Push to Container Registry
   docker push gcr.io/your-project-id/profitpoke-api
   ```

4. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy profitpoke-api \
       --image=gcr.io/your-project-id/profitpoke-api \
       --platform=managed \
       --region=us-central1 \
       --allow-unauthenticated \
       --memory=1Gi \
       --cpu=1 \
       --max-instances=10 \
       --set-env-vars="FLASK_ENV=production,KITE_API_KEY=your_key,KITE_API_SECRET=your_secret,GROK_API_KEY=your_grok_key,FLASK_SECRET_KEY=your_flask_key"
   ```

## Step 4: Configure Firebase Hosting

1. **Update Firebase configuration**:
   The `firebase.json` file is already configured to route all requests to your Cloud Run service.

2. **Update the service URL in firebase.json** (if needed):
   Replace `profitpoke-api` with your actual Cloud Run service name if different.

3. **Deploy Firebase Hosting**:
   ```bash
   firebase deploy --only hosting
   ```

## Step 5: Custom Domain (Optional)

1. **Add custom domain in Firebase Console**:
   - Go to Firebase Console → Hosting
   - Click "Add custom domain"
   - Follow the DNS configuration steps

2. **Or use Cloud Run domain mapping**:
   ```bash
   gcloud run domain-mappings create \
       --service=profitpoke-api \
       --domain=yourdomain.com \
       --region=us-central1
   ```

## Step 6: Monitoring and Logs

1. **View Cloud Run logs**:
   ```bash
   gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=profitpoke-api"
   ```

2. **Monitor in GCP Console**:
   - Go to Cloud Run → profitpoke-api
   - Check metrics, logs, and health

## Deployment Architecture

```
User Request → Firebase Hosting → Cloud Run Service
                     ↓
              Static Assets (CDN)
                     ↓
            Flask App (Serverless)
                     ↓
              External APIs (Kite, Grok)
```

## Benefits of This Setup

- **Serverless**: Pay only for actual usage
- **Auto-scaling**: Handles traffic spikes automatically
- **Global CDN**: Firebase Hosting provides fast static asset delivery
- **HTTPS**: Automatic SSL certificates
- **Custom domains**: Easy domain configuration
- **Zero downtime deployments**: Rolling updates

## Troubleshooting

1. **Build Errors**:
   ```bash
   # Check Docker build locally
   docker build -t test-image .
   docker run -p 8080:8080 test-image
   ```

2. **Environment Variables**:
   ```bash
   # Update env vars without redeploying
   gcloud run services update profitpoke-api \
       --region=us-central1 \
       --set-env-vars="NEW_VAR=value"
   ```

3. **Service Logs**:
   ```bash
   gcloud logs read "resource.type=cloud_run_revision" --limit=50
   ```

## Costs

- **Cloud Run**: $0.40 per million requests + compute time
- **Firebase Hosting**: $0.15/GB storage + $0.15/GB transfer
- **Container Registry**: $0.10/GB storage

For typical usage, expect $5-20/month for a small to medium app.

## Security Notes

- Environment variables are encrypted at rest
- All traffic is HTTPS only
- Container runs as non-root user
- No persistent storage (stateless)
- API keys are not exposed in the client

## Next Steps

1. Set up monitoring and alerting
2. Configure custom domain
3. Set up CI/CD pipeline with GitHub Actions
4. Add database if needed (Cloud SQL, Firestore)
5. Implement caching with Redis (Cloud Memorystore)
