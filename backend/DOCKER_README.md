# Docker Setup for HoosStudying Backend

## Quick Start

### 1. Build and run locally:

```bash
docker build -t hoosstudying-backend .
docker run -p 8080:8080 --env-file .env hoosstudying-backend
```

### 2. Using Docker Compose:

```bash
docker-compose up --build
```

### 3. Test:

```bash
curl http://localhost:8080/
```

## Deploy to Google Cloud Run

### One-line deploy:

```bash
gcloud run deploy hoosstudying-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

See `DEPLOYMENT.md` for complete deployment instructions.

## Files Created

- `Dockerfile` - Container definition
- `docker-compose.yml` - Local development setup
- `.dockerignore` - Files to exclude from container
- `.gcloudignore` - Files to exclude from Cloud Run
- `cloudbuild.yaml` - Automated CI/CD configuration
- `DEPLOYMENT.md` - Complete deployment guide

## Environment Setup

1. Copy `.env.example` to `.env`
2. Fill in your credentials
3. Run: `docker-compose up`
