# AWS Amplify Setup Guide for Return-to-Print

## Overview

AWS Amplify will host the Next.js frontend with automatic CI/CD from GitHub.

## Prerequisites

- GitHub repository: `return-to-print` (at /Users/andymccutcheon/Documents/GitHub/return-to-print)
- Repository must be pushed to GitHub
- AWS Amplify needs access to the GitHub repository

## Option 1: Setup via AWS Console (Recommended)

### Step 1: Navigate to AWS Amplify
1. Go to AWS Console → AWS Amplify
2. Region: **us-west-2**
3. Click "New app" → "Host web app"

### Step 2: Connect to GitHub
1. Select "GitHub" as the source
2. Click "Connect branch"
3. Authorize AWS Amplify to access your GitHub account
4. Select repository: **return-to-print**
5. Select branch: **main**

### Step 3: Configure Build Settings
1. App name: **return-to-print**
2. Environment name: **production**
3. Build settings will be auto-detected, or use the `amplify.yml` from this directory
4. Set root directory: **frontend/**

### Step 4: Add Environment Variables
Add the following environment variable:
- Key: `NEXT_PUBLIC_API_BASE_URL`
- Value: Will be provided after backend deployment (format: `https://[api-id].execute-api.us-west-2.amazonaws.com/prod`)

For now, use a placeholder:
- Value: `https://placeholder.execute-api.us-west-2.amazonaws.com/prod`

### Step 5: Review and Deploy
1. Review all settings
2. Click "Save and deploy"
3. Wait for first build to complete (5-10 minutes)

### Step 6: Note the URLs
After deployment completes, note:
- **App ID**: (e.g., d1234abcd)
- **Default domain**: (e.g., https://main.d1234abcd.amplifyapp.com)
- These will be needed for frontend agent

## Option 2: Setup via CloudFormation (Requires GitHub Token)

### Step 1: Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Scopes needed:
   - `repo` (all repo permissions)
4. Copy the token (you'll only see it once)

### Step 2: Deploy CloudFormation Stack
```bash
cd /Users/andymccutcheon/Documents/GitHub/return-to-print/infra

aws cloudformation deploy \
  --template-file amplify-app.yaml \
  --stack-name return-to-print-amplify \
  --parameter-overrides \
    GitHubRepository=https://github.com/YOUR_USERNAME/return-to-print \
    GitHubBranch=main \
    GitHubToken=YOUR_GITHUB_TOKEN \
    ApiBaseUrl=https://placeholder.execute-api.us-west-2.amazonaws.com/prod \
  --region us-west-2
```

### Step 3: Get Amplify App Details
```bash
aws cloudformation describe-stacks \
  --stack-name return-to-print-amplify \
  --region us-west-2 \
  --query 'Stacks[0].Outputs'
```

## Option 3: Setup via AWS CLI (Manual)

```bash
# Create the app (requires GitHub token)
aws amplify create-app \
  --name return-to-print \
  --repository https://github.com/YOUR_USERNAME/return-to-print \
  --access-token YOUR_GITHUB_TOKEN \
  --platform WEB \
  --build-spec file://amplify.yml \
  --environment-variables NEXT_PUBLIC_API_BASE_URL=https://placeholder.execute-api.us-west-2.amazonaws.com/prod \
  --region us-west-2

# Create branch connection
aws amplify create-branch \
  --app-id APP_ID_FROM_ABOVE \
  --branch-name main \
  --enable-auto-build \
  --region us-west-2

# Trigger first deployment
aws amplify start-job \
  --app-id APP_ID_FROM_ABOVE \
  --branch-name main \
  --job-type RELEASE \
  --region us-west-2
```

## Post-Setup Configuration

### Update Environment Variable (After Backend Deployment)
Once the backend API is deployed:
```bash
aws amplify update-app \
  --app-id YOUR_APP_ID \
  --environment-variables NEXT_PUBLIC_API_BASE_URL=https://[real-api-id].execute-api.us-west-2.amazonaws.com/prod \
  --region us-west-2

# Redeploy to pick up new env var
aws amplify start-job \
  --app-id YOUR_APP_ID \
  --branch-name main \
  --job-type RELEASE \
  --region us-west-2
```

## Configure Custom Domain (After DNS Propagation)

### Step 1: Wait for DNS Propagation
Ensure Route 53 nameservers are configured in Squarespace and propagated (24-48 hours).

### Step 2: Add Custom Domain in Amplify Console
1. Go to Amplify app → Domain management
2. Click "Add domain"
3. Select "returntoprint.xyz" (should appear if Route 53 is configured)
4. Configure subdomains:
   - `www.returntoprint.xyz` → main branch
   - `returntoprint.xyz` → redirect to www (or host on main branch)
5. Amplify will automatically:
   - Create DNS records in Route 53
   - Provision SSL certificate via ACM
   - Configure redirects

### Step 3: Wait for SSL Certificate
SSL certificate provisioning takes 5-15 minutes. Status will show in Amplify console.

### Step 4: Verify Custom Domain
Once complete, test:
- https://www.returntoprint.xyz (should load app)
- https://returntoprint.xyz (should redirect to www or load app)

## Troubleshooting

### Build Fails
- Check build logs in Amplify console
- Verify `frontend/package.json` exists with correct scripts
- Ensure Next.js dependencies are in `package.json`

### Environment Variable Not Working
- Verify variable name starts with `NEXT_PUBLIC_`
- Redeploy after changing environment variables
- Check build logs for confirmation

### Custom Domain Not Working
- Verify DNS propagation: `dig returntoprint.xyz NS`
- Check ACM certificate status in Amplify console
- Allow 5-15 minutes for SSL certificate provisioning

## Next Steps for Frontend Agent

Once Amplify is configured, provide Frontend Agent with:
1. Amplify app ID
2. Default domain URL
3. Environment variable configuration
4. Custom domain URL (after DNS propagates)

Frontend Agent will then create the Next.js application in the `frontend/` directory.

