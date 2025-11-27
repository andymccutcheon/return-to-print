# CodePipeline Setup Guide for Return-to-Print Backend

## Overview

CodePipeline automates the deployment of the Python/Chalice backend to AWS Lambda whenever code is pushed to the `main` branch.

## Prerequisites

- Core infrastructure deployed (DynamoDB, IAM roles)
- GitHub repository with backend code
- GitHub Personal Access Token (for webhook integration)

## Pipeline Architecture

```
GitHub (main branch)
    ↓ (webhook trigger)
Source Stage
    ↓ (artifact)
Build Stage (CodeBuild)
    ↓ (runs buildspec.yml)
Deploy (Chalice deploy)
    ↓
Lambda + API Gateway Updated
```

## Option 1: Deploy via CloudFormation (Requires GitHub Token)

### Step 1: Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Scopes needed:
   - `repo` (all)
   - `admin:repo_hook` (write:repo_hook and read:repo_hook)
4. Copy the token

### Step 2: Deploy Pipeline Stack
```bash
cd /Users/andymccutcheon/Documents/GitHub/return-to-print/infra

aws cloudformation deploy \
  --template-file backend-pipeline.yaml \
  --stack-name return-to-print-pipeline \
  --parameter-overrides \
    GitHubRepository=andymccutcheon/return-to-print \
    GitHubBranch=main \
    GitHubToken=YOUR_GITHUB_TOKEN \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-west-2
```

### Step 3: Verify Pipeline
```bash
# Get pipeline details
aws cloudformation describe-stacks \
  --stack-name return-to-print-pipeline \
  --region us-west-2 \
  --query 'Stacks[0].Outputs'

# Check pipeline status
aws codepipeline get-pipeline-state \
  --name return-to-print-backend-pipeline \
  --region us-west-2
```

### Step 4: Trigger First Build
Push to main branch or manually trigger:
```bash
aws codepipeline start-pipeline-execution \
  --name return-to-print-backend-pipeline \
  --region us-west-2
```

## Option 2: Setup via AWS Console

### Step 1: Create S3 Artifact Bucket
```bash
aws s3 mb s3://return-to-print-pipeline-artifacts-us-west-2-809581002583 --region us-west-2

aws s3api put-public-access-block \
  --bucket return-to-print-pipeline-artifacts-us-west-2-809581002583 \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Step 2: Create CodeBuild Project
1. Go to AWS CodeBuild → Create project
2. Project configuration:
   - Name: `return-to-print-backend-build`
   - Source: GitHub
   - Repository: `andymccutcheon/return-to-print`
   - Branch: `main`
   - Buildspec: `infra/buildspec.yml`
3. Environment:
   - Image: `aws/codebuild/standard:7.0`
   - Compute: `BUILD_GENERAL1_SMALL`
   - Service role: Use existing `return-to-print-codebuild-role-prod`
4. Environment variables:
   - `DYNAMODB_TABLE`: `return-to-print-messages-prod`
   - `ENVIRONMENT`: `prod`
5. Artifacts: None (uses CodePipeline)
6. Create project

### Step 3: Create CodePipeline
1. Go to AWS CodePipeline → Create pipeline
2. Pipeline settings:
   - Name: `return-to-print-backend-pipeline`
   - Service role: Create new or use existing
   - Artifact store: Custom location → Select S3 bucket from Step 1
3. Source stage:
   - Source provider: GitHub (Version 2 recommended)
   - Connect to GitHub and authorize
   - Repository: `andymccutcheon/return-to-print`
   - Branch: `main`
   - Change detection: Use GitHub webhooks
4. Build stage:
   - Build provider: AWS CodeBuild
   - Project: `return-to-print-backend-build`
5. Deploy stage: Skip (handled by buildspec.yml)
6. Review and create

## Option 3: Manual Setup (No Pipeline)

If you prefer manual deployments without CI/CD:

```bash
# From your local machine
cd /Users/andymccutcheon/Documents/GitHub/return-to-print/backend

# Install Chalice if not already installed
pip install chalice

# Deploy manually
chalice deploy --stage prod
```

## Monitoring the Pipeline

### View Pipeline Executions
```bash
# List recent executions
aws codepipeline list-pipeline-executions \
  --pipeline-name return-to-print-backend-pipeline \
  --region us-west-2 \
  --max-results 5

# Get execution details
aws codepipeline get-pipeline-execution \
  --pipeline-name return-to-print-backend-pipeline \
  --pipeline-execution-id EXECUTION_ID \
  --region us-west-2
```

### View CodeBuild Logs
```bash
# List recent builds
aws codebuild list-builds-for-project \
  --project-name return-to-print-backend-build \
  --region us-west-2

# Get build details
aws codebuild batch-get-builds \
  --ids BUILD_ID \
  --region us-west-2
```

### CloudWatch Logs
Build logs are automatically sent to:
```
/aws/codebuild/return-to-print-backend-build
```

View logs:
```bash
aws logs tail /aws/codebuild/return-to-print-backend-build --follow --region us-west-2
```

## Pipeline Flow

### On Every Push to Main:
1. **Webhook triggers** pipeline automatically
2. **Source stage** downloads latest code from GitHub
3. **Build stage**:
   - Runs `buildspec.yml`
   - Installs Python 3.11 and dependencies
   - Navigates to `backend/` directory
   - Runs `chalice deploy --stage prod`
   - Lambda and API Gateway are updated
4. **Completion**: New backend is live

### Build Artifacts
Artifacts are stored in S3 bucket for 30 days, then automatically deleted.

## Troubleshooting

### Pipeline Fails at Source Stage
- Verify GitHub token has correct permissions
- Check webhook is registered in GitHub repository settings
- Ensure repository URL is correct

### Build Fails
- Check CodeBuild logs in CloudWatch
- Verify `buildspec.yml` path is correct: `infra/buildspec.yml`
- Ensure backend code exists in `backend/` directory
- Check IAM role permissions for CodeBuild

### Deploy Fails
- Verify Chalice configuration is correct
- Check Lambda execution role exists
- Ensure DynamoDB table is created
- Review Chalice deploy logs

### Webhook Not Triggering
- Verify webhook exists in GitHub repository → Settings → Webhooks
- Check webhook recent deliveries for errors
- Manually trigger pipeline to test: `aws codepipeline start-pipeline-execution`

## Cost Optimization

- CodePipeline: $1/month per active pipeline
- CodeBuild: ~$0.005 per build minute (Small instance)
- S3: ~$0.023/GB-month for artifacts (automatically cleaned up)
- Estimated cost: < $2/month for typical usage

## Security Best Practices

1. **GitHub Token**: Store securely, rotate regularly
2. **S3 Bucket**: Public access blocked
3. **IAM Roles**: Least privilege permissions
4. **Artifacts**: Encrypted at rest (S3 default)
5. **Logs**: Retained for 30 days only

## Next Steps

After pipeline is configured:
1. Backend Agent creates Chalice application in `backend/` directory
2. Push to `main` branch triggers automatic deployment
3. API Gateway URL is available in Chalice output
4. Update Amplify with API Gateway URL
5. Frontend can call the backend

## Getting API Gateway URL

After first successful deployment:
```bash
# From Chalice deployed output
cat backend/.chalice/deployed/prod.json | grep rest_api_url

# Or query API Gateway directly
aws apigateway get-rest-apis --region us-west-2 --query 'items[?name==`return-to-print-api-prod`]'
```

The API Gateway URL will be in format:
```
https://[api-id].execute-api.us-west-2.amazonaws.com/prod
```

Provide this URL to:
- **Frontend Agent**: For `NEXT_PUBLIC_API_BASE_URL` environment variable
- **Hardware Agent**: For Pi worker configuration

