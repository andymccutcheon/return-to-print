# Return-to-Print Infrastructure Documentation

## Overview

This directory contains all Infrastructure as Code (IaC) for the Return-to-Print project, including AWS resource definitions, CI/CD pipeline configurations, and deployment scripts.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet Users                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Route 53   │  DNS: returntoprint.xyz
                    │  (Hosted    │  Nameservers configured in Squarespace
                    │   Zone)     │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
       ┌──────▼──────┐          ┌──────▼──────────┐
       │  AWS        │          │  API Gateway    │
       │  Amplify    │          │  + Lambda       │
       │  (Frontend) │          │  (Backend)      │
       └──────┬──────┘          └──────┬──────────┘
              │                         │
       ┌──────▼──────┐          ┌──────▼──────────┐
       │  GitHub     │          │  DynamoDB       │
       │  (CI/CD)    │          │  (Messages)     │
       └─────────────┘          └─────────────────┘
              │                         │
       ┌──────▼──────────────────────────▼──────────┐
       │         CloudWatch Monitoring               │
       │   (Logs, Metrics, Alarms, Dashboard)        │
       └─────────────────────────────────────────────┘
```

## Deployed Infrastructure

### ✅ Core Infrastructure (Stack: `return-to-print-infra`)

**Deployed Resources:**
- **DynamoDB Table**: `return-to-print-messages-prod`
  - Billing Mode: PAY_PER_REQUEST (on-demand)
  - Primary Key: `id` (String)
  - GSI: `PrintedStatusIndex` (printed + created_at)
  - Point-in-time recovery: Enabled
  - ARN: `arn:aws:dynamodb:us-west-2:809581002583:table/return-to-print-messages-prod`

- **Lambda Execution Role**: `return-to-print-lambda-role-prod`
  - Permissions: DynamoDB read/write, CloudWatch Logs
  - ARN: `arn:aws:iam::809581002583:role/return-to-print-lambda-role-prod`

- **CodeBuild Service Role**: `return-to-print-codebuild-role-prod`
  - Permissions: Deploy Lambda, API Gateway, CloudFormation
  - ARN: `arn:aws:iam::809581002583:role/return-to-print-codebuild-role-prod`

- **SNS Topic**: `return-to-print-alarms-prod`
  - Purpose: CloudWatch alarm notifications
  - ARN: `arn:aws:sns:us-west-2:809581002583:return-to-print-alarms-prod`

- **CloudWatch Log Groups**:
  - `/aws/lambda/return-to-print-api-prod` (30-day retention)
  - `/aws/apigateway/return-to-print-api-prod` (30-day retention)

**View Stack:**
```bash
aws cloudformation describe-stacks \
  --stack-name return-to-print-infra \
  --region us-west-2
```

### ✅ DNS Configuration (Route 53)

**Hosted Zone:**
- Domain: `returntoprint.xyz`
- Hosted Zone ID: `Z03595423QUR7NOOMU64T`
- Status: Active

**Nameservers (Configure in Squarespace):**
1. `ns-1738.awsdns-25.co.uk`
2. `ns-1398.awsdns-46.org`
3. `ns-233.awsdns-29.com`
4. `ns-662.awsdns-18.net`

**Action Required:** Update nameservers in Squarespace domain settings.
See [DNS_CONFIGURATION.md](./DNS_CONFIGURATION.md) for detailed instructions.

### ✅ Monitoring (Stack: `return-to-print-monitoring`)

**CloudWatch Dashboard:**
- Dashboard Name: `return-to-print-monitoring`
- URL: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring
- Metrics: DynamoDB, Lambda, API Gateway

**CloudWatch Alarms (6 total):**
- `return-to-print-dynamodb-throttled-reads`: DynamoDB UserErrors > 1
- `return-to-print-dynamodb-system-errors`: DynamoDB SystemErrors > 1
- `return-to-print-lambda-errors`: Lambda Errors > 5 in 5 minutes
- `return-to-print-lambda-throttles`: Lambda Throttles > 5 in 5 minutes
- `return-to-print-lambda-duration`: Lambda P99 Duration > 5 seconds
- (3 more API Gateway alarms will activate after backend deployment)

**View Alarms:**
```bash
aws cloudwatch describe-alarms \
  --alarm-name-prefix return-to-print \
  --region us-west-2
```

### 📋 Pending Setup (Requires Manual Steps)

#### 1. AWS Amplify (Frontend Hosting)
- **Status**: Configuration files created, requires GitHub connection
- **Templates**: `amplify.yml`, `amplify-app.yaml`
- **Guide**: [AMPLIFY_SETUP.md](./AMPLIFY_SETUP.md)
- **Action Required**: Connect to GitHub via AWS Console or CLI with token

#### 2. CodePipeline (Backend CI/CD)
- **Status**: Configuration files created, requires GitHub connection
- **Templates**: `backend-pipeline.yaml`, `buildspec.yml`
- **Guide**: [CODEPIPELINE_SETUP.md](./CODEPIPELINE_SETUP.md)
- **Action Required**: Set up pipeline with GitHub webhook

## Directory Structure

```
infra/
├── README.md                           # This file
├── DNS_CONFIGURATION.md                # Route 53 nameserver setup
├── AMPLIFY_SETUP.md                    # Amplify frontend setup guide
├── CODEPIPELINE_SETUP.md               # Backend CI/CD setup guide
│
├── core-infrastructure.yaml            # ✅ DEPLOYED: DynamoDB, IAM roles
├── template.yaml                       # SAM template (backend with Lambda)
├── monitoring.yaml                     # ✅ DEPLOYED: CloudWatch alarms/dashboard
├── amplify-app.yaml                    # Amplify CloudFormation template
├── backend-pipeline.yaml               # CodePipeline CloudFormation template
│
├── amplify.yml                         # Amplify build specification
├── buildspec.yml                       # CodeBuild build specification
│
└── policies/
    ├── lambda-execution-policy.json    # Lambda IAM policy (embedded in CF)
    └── codebuild-service-policy.json   # CodeBuild IAM policy (embedded in CF)
```

## Quick Start

### Prerequisites
- AWS CLI configured with credentials
- AWS Account: `809581002583`
- Region: `us-west-2`
- GitHub repository: `return-to-print`

### Verify Deployed Infrastructure
```bash
# Check all stacks
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --region us-west-2 \
  --query 'StackSummaries[?contains(StackName, `return-to-print`)].{Name:StackName,Status:StackStatus}' \
  --output table

# Check DynamoDB table
aws dynamodb describe-table \
  --table-name return-to-print-messages-prod \
  --region us-west-2 \
  --query 'Table.{Name:TableName,Status:TableStatus,Billing:BillingModeSummary.BillingMode}' \
  --output table

# Check Route 53 hosted zone
aws route53 list-hosted-zones \
  --query 'HostedZones[?Name==`returntoprint.xyz.`]' \
  --output table
```

## Next Steps

### For Project Owner (You)

1. **Configure DNS** (Required for custom domain)
   - [ ] Update Squarespace nameservers to Route 53 NS records
   - [ ] Wait 24-48 hours for DNS propagation
   - [ ] Verify: `dig returntoprint.xyz NS`

2. **Set Up Amplify** (Frontend Hosting)
   - [ ] Push code to GitHub if not already done
   - [ ] Follow [AMPLIFY_SETUP.md](./AMPLIFY_SETUP.md)
   - [ ] Connect GitHub via AWS Console (recommended)
   - [ ] Note Amplify app URL for frontend agent

3. **Set Up CodePipeline** (Backend CI/CD) - Optional
   - [ ] Follow [CODEPIPELINE_SETUP.md](./CODEPIPELINE_SETUP.md)
   - [ ] Or manually deploy backend with `chalice deploy`

4. **Configure Email Notifications** (Optional)
   - [ ] Subscribe to SNS topic: `return-to-print-alarms-prod`
   ```bash
   aws sns subscribe \
     --topic-arn arn:aws:sns:us-west-2:809581002583:return-to-print-alarms-prod \
     --protocol email \
     --notification-endpoint your-email@example.com \
     --region us-west-2
   ```
   - [ ] Confirm subscription via email

### For Backend Agent

**Prerequisites:** Core infrastructure is deployed. You can now:
- Create Chalice application in `../backend/` directory
- Use DynamoDB table: `return-to-print-messages-prod`
- Deploy with: `chalice deploy --stage prod`
- Lambda execution role is ready: `return-to-print-lambda-role-prod`

**Expected Output:** API Gateway URL in format:
```
https://[api-id].execute-api.us-west-2.amazonaws.com/prod
```

**Provide this URL to:**
- Frontend Agent (for `NEXT_PUBLIC_API_BASE_URL`)
- Hardware Agent (for Pi worker configuration)

### For Frontend Agent

**Prerequisites:** Amplify app must be configured first (see AMPLIFY_SETUP.md)

Once Amplify is ready:
- Create Next.js application in `../frontend/` directory
- Push to GitHub `main` branch
- Amplify will build and deploy automatically

**Environment Variable Needed:**
- `NEXT_PUBLIC_API_BASE_URL`: (from Backend Agent after deployment)

### For Hardware Agent

**Prerequisites:** Backend API must be deployed first

Configuration needed:
- API Gateway base URL: `https://[api-id].execute-api.us-west-2.amazonaws.com/prod`
- Use this URL in Pi worker script to poll for messages

## AWS Console Quick Links

- **CloudFormation Stacks**: https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2
- **DynamoDB Tables**: https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#tables
- **Route 53**: https://console.aws.amazon.com/route53/v2/hostedzones
- **CloudWatch Dashboard**: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring
- **CloudWatch Alarms**: https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#alarmsV2:
- **IAM Roles**: https://console.aws.amazon.com/iam/home#/roles

## Cost Estimation

Based on typical usage for a small personal project:

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| DynamoDB | < 1M requests/month, on-demand | $0.25 - $1.00 |
| Lambda | < 100K invocations/month | Free tier |
| API Gateway | < 1M requests/month | Free tier (first 12 months) |
| Route 53 | 1 hosted zone | $0.50/month |
| CloudWatch | Logs, metrics, alarms | $1.00 - $2.00 |
| Amplify | Build minutes, storage | Free tier |
| CodePipeline | 1 active pipeline | $1.00/month (if used) |
| **Total** | | **$2.75 - $5.00/month** |

### Cost Optimization Tips
- DynamoDB on-demand: Pay only for actual usage
- Lambda ARM64: 20% cheaper than x86
- Log retention: 30 days (not forever)
- Artifact cleanup: S3 lifecycle rules
- Free tier: Most services covered for 12 months

## Maintenance

### Update Infrastructure
```bash
cd /Users/andymccutcheon/Documents/GitHub/return-to-print/infra

# Update core infrastructure
aws cloudformation deploy \
  --template-file core-infrastructure.yaml \
  --stack-name return-to-print-infra \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-west-2

# Update monitoring
aws cloudformation deploy \
  --template-file monitoring.yaml \
  --stack-name return-to-print-monitoring \
  --region us-west-2
```

### View Logs
```bash
# Lambda logs
aws logs tail /aws/lambda/return-to-print-api-prod --follow --region us-west-2

# API Gateway logs (after backend deployment)
aws logs tail /aws/apigateway/return-to-print-api-prod --follow --region us-west-2

# CodeBuild logs (if pipeline is set up)
aws logs tail /aws/codebuild/return-to-print-backend-build --follow --region us-west-2
```

### Backup and Recovery

**DynamoDB Point-in-Time Recovery:**
- Enabled: Yes (continuous backups)
- Retention: 35 days
- Restore: AWS Console or CLI

```bash
# Create on-demand backup
aws dynamodb create-backup \
  --table-name return-to-print-messages-prod \
  --backup-name return-to-print-backup-$(date +%Y%m%d) \
  --region us-west-2
```

### Tear Down (Complete Infrastructure Deletion)

**⚠️ WARNING: This will delete all data. Cannot be undone.**

```bash
# Delete monitoring stack
aws cloudformation delete-stack \
  --stack-name return-to-print-monitoring \
  --region us-west-2

# Delete pipeline (if created)
aws cloudformation delete-stack \
  --stack-name return-to-print-pipeline \
  --region us-west-2

# Delete Amplify app (if created)
aws cloudformation delete-stack \
  --stack-name return-to-print-amplify \
  --region us-west-2

# Wait for above stacks to delete, then delete core infrastructure
aws cloudformation delete-stack \
  --stack-name return-to-print-infra \
  --region us-west-2

# Delete Route 53 hosted zone (manual - has cost)
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones --query 'HostedZones[?Name==`returntoprint.xyz.`].Id' --output text)
aws route53 delete-hosted-zone --id $HOSTED_ZONE_ID

# Delete S3 artifacts bucket (if pipeline was created)
aws s3 rb s3://return-to-print-pipeline-artifacts-us-west-2-809581002583 --force
```

## Troubleshooting

### DynamoDB Issues
```bash
# Check table status
aws dynamodb describe-table \
  --table-name return-to-print-messages-prod \
  --region us-west-2

# Scan table (view data)
aws dynamodb scan \
  --table-name return-to-print-messages-prod \
  --region us-west-2 \
  --max-items 10
```

### IAM Permission Issues
```bash
# Verify Lambda execution role
aws iam get-role \
  --role-name return-to-print-lambda-role-prod

# List attached policies
aws iam list-role-policies \
  --role-name return-to-print-lambda-role-prod
```

### CloudWatch Alarms
```bash
# Check alarm status
aws cloudwatch describe-alarms \
  --alarm-names return-to-print-lambda-errors \
  --region us-west-2

# View alarm history
aws cloudwatch describe-alarm-history \
  --alarm-name return-to-print-lambda-errors \
  --region us-west-2 \
  --max-records 5
```

## Security

### IAM Best Practices
- ✅ Least privilege policies (scoped to specific resources)
- ✅ No wildcard permissions in production roles
- ✅ Separate roles for each service
- ✅ No hardcoded credentials (uses IAM roles)

### Data Security
- ✅ DynamoDB encryption at rest (default AWS managed keys)
- ✅ HTTPS only (API Gateway, Amplify)
- ✅ S3 buckets with public access blocked
- ✅ Point-in-time recovery enabled

### Access Control
- ✅ CloudFormation manages all resources
- ✅ No manual console changes (IaC enforced)
- ⚠️ API Gateway currently has no authentication (add in future)

## Support

### Getting Help
- Review setup guides: `AMPLIFY_SETUP.md`, `CODEPIPELINE_SETUP.md`, `DNS_CONFIGURATION.md`
- Check AWS documentation: https://docs.aws.amazon.com/
- Review CloudWatch logs for errors
- Check CloudFormation stack events for deployment issues

### Common Issues

**DNS not propagating:**
- Wait 24-48 hours after updating nameservers
- Verify nameservers: `dig returntoprint.xyz NS`
- Use online DNS checker: https://dnschecker.org/

**Amplify build failing:**
- Check build logs in Amplify console
- Verify `frontend/package.json` exists
- Ensure all dependencies are listed

**Lambda errors:**
- Check CloudWatch logs: `/aws/lambda/return-to-print-api-prod`
- Verify DynamoDB table exists and is accessible
- Check IAM role permissions

## Version History

- **2025-11-24**: Initial infrastructure deployment
  - Core infrastructure stack deployed
  - Route 53 hosted zone created
  - CloudWatch monitoring configured
  - Documentation completed

---

**Infrastructure Status**: ✅ Core infrastructure deployed and operational

**Next Action**: Configure DNS nameservers in Squarespace, then set up Amplify for frontend hosting

