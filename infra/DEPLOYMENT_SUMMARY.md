# Return-to-Print Infrastructure Deployment Summary

**Date**: November 24, 2025  
**Region**: us-west-2  
**AWS Account**: 809581002583  
**Status**: ✅ Core Infrastructure Deployed

---

## 🎉 Successfully Deployed

### 1. ✅ DynamoDB Table
- **Table Name**: `return-to-print-messages-prod`
- **Billing Mode**: PAY_PER_REQUEST (on-demand)
- **Status**: ACTIVE
- **Primary Key**: `id` (String, HASH)
- **Global Secondary Index**: `PrintedStatusIndex`
  - Partition Key: `printed` (String)
  - Sort Key: `created_at` (String)
- **Features**:
  - Point-in-time recovery enabled
  - DynamoDB Streams enabled
  - On-demand billing (pay per request)
- **ARN**: `arn:aws:dynamodb:us-west-2:809581002583:table/return-to-print-messages-prod`

**Verification**:
```bash
aws dynamodb describe-table --table-name return-to-print-messages-prod --region us-west-2
```

### 2. ✅ IAM Roles

#### Lambda Execution Role
- **Role Name**: `return-to-print-lambda-role-prod`
- **Permissions**: 
  - DynamoDB: PutItem, GetItem, UpdateItem, Query, Scan
  - CloudWatch: CreateLogGroup, CreateLogStream, PutLogEvents
- **ARN**: `arn:aws:iam::809581002583:role/return-to-print-lambda-role-prod`

#### CodeBuild Service Role
- **Role Name**: `return-to-print-codebuild-role-prod`
- **Permissions**:
  - CloudFormation: Stack operations
  - Lambda: Function management
  - API Gateway: API management
  - IAM: Role PassRole
  - S3: Artifact access
- **ARN**: `arn:aws:iam::809581002583:role/return-to-print-codebuild-role-prod`

### 3. ✅ Route 53 Hosted Zone
- **Domain**: returntoprint.xyz
- **Hosted Zone ID**: Z03595423QUR7NOOMU64T
- **Status**: Active

**Nameservers** (configure in Squarespace):
```
ns-1738.awsdns-25.co.uk
ns-1398.awsdns-46.org
ns-233.awsdns-29.com
ns-662.awsdns-18.net
```

**Next Step**: Update nameservers in Squarespace domain settings → [DNS_CONFIGURATION.md](./DNS_CONFIGURATION.md)

### 4. ✅ CloudWatch Monitoring

#### Log Groups (30-day retention)
- `/aws/lambda/return-to-print-api-prod`
- `/aws/apigateway/return-to-print-api-prod`

#### CloudWatch Alarms (6 created)
1. **return-to-print-dynamodb-throttled-reads**: UserErrors > 1
2. **return-to-print-dynamodb-system-errors**: SystemErrors > 1
3. **return-to-print-lambda-errors**: Errors > 5 in 5 minutes
4. **return-to-print-lambda-throttles**: Throttles > 5 in 5 minutes
5. **return-to-print-lambda-duration**: P99 Duration > 5 seconds
6. _(3 API Gateway alarms will activate after backend deployment)_

#### CloudWatch Dashboard
- **Dashboard Name**: return-to-print-monitoring
- **URL**: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring
- **Metrics Tracked**:
  - DynamoDB: Read/write capacity, errors
  - Lambda: Invocations, errors, duration, throttles
  - API Gateway: Requests, latency, errors (after backend deployment)

#### SNS Topic for Alarms
- **Topic Name**: return-to-print-alarms-prod
- **ARN**: `arn:aws:sns:us-west-2:809581002583:return-to-print-alarms-prod`
- **Action Required**: Subscribe your email to receive alarm notifications:
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:us-west-2:809581002583:return-to-print-alarms-prod \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region us-west-2
```

### 5. ✅ Infrastructure as Code Files

All infrastructure is now version-controlled:
```
infra/
├── README.md                       ✅ Comprehensive documentation
├── DNS_CONFIGURATION.md            ✅ Nameserver setup guide
├── AMPLIFY_SETUP.md                ✅ Frontend hosting guide
├── CODEPIPELINE_SETUP.md           ✅ Backend CI/CD guide
├── DEPLOYMENT_SUMMARY.md           ✅ This file
│
├── core-infrastructure.yaml        ✅ Deployed stack
├── monitoring.yaml                 ✅ Deployed stack
├── template.yaml                   ✅ SAM template (for backend)
├── amplify-app.yaml                📋 Ready to deploy
├── backend-pipeline.yaml           📋 Ready to deploy
│
├── amplify.yml                     ✅ Amplify build spec
├── buildspec.yml                   ✅ CodeBuild build spec
│
└── policies/
    ├── lambda-execution-policy.json    ✅ IAM policy
    └── codebuild-service-policy.json   ✅ IAM policy
```

---

## 📋 Pending Configuration (Requires Manual Steps)

### 1. DNS Configuration
**Action**: Update nameservers in Squarespace

**Steps**:
1. Log in to Squarespace domain management
2. Navigate to DNS settings for returntoprint.xyz
3. Replace existing nameservers with Route 53 nameservers (listed above)
4. Wait 24-48 hours for propagation

**Verification**:
```bash
dig returntoprint.xyz NS +short
```

Expected output (after propagation):
```
ns-1738.awsdns-25.co.uk.
ns-1398.awsdns-46.org.
ns-233.awsdns-29.com.
ns-662.awsdns-18.net.
```

**Guide**: [DNS_CONFIGURATION.md](./DNS_CONFIGURATION.md)

### 2. AWS Amplify (Frontend Hosting)
**Status**: Configuration files ready, requires GitHub connection

**Prerequisites**:
- GitHub repository must contain frontend code
- Repository: `andymccutcheon/return-to-print`

**Setup Options**:
1. **AWS Console** (Recommended): Manual connection to GitHub
2. **CloudFormation**: Requires GitHub Personal Access Token
3. **AWS CLI**: Requires GitHub token

**Guide**: [AMPLIFY_SETUP.md](./AMPLIFY_SETUP.md)

**After Setup**: Amplify will provide default URL like:
```
https://main.d[app-id].amplifyapp.com
```

### 3. CodePipeline (Backend CI/CD)
**Status**: Configuration files ready, optional (can deploy manually)

**Options**:
1. **Use CodePipeline**: Automatic deployment on git push
2. **Manual Deployment**: Run `chalice deploy` from local machine

**Guide**: [CODEPIPELINE_SETUP.md](./CODEPIPELINE_SETUP.md)

---

## 🔗 Integration Points for Other Agents

### For Backend Agent

**Ready to Start**: ✅ All prerequisites deployed

**What You Need**:
- **DynamoDB Table**: `return-to-print-messages-prod`
- **Lambda Execution Role**: `return-to-print-lambda-role-prod`
- **Region**: `us-west-2`

**Your Task**:
1. Create Chalice application in `../backend/` directory
2. Implement 4 API endpoints:
   - `POST /message` - Create new message
   - `GET /messages/recent` - Get recent messages
   - `GET /printer/next-to-print` - Get next unprinted message
   - `POST /printer/mark-printed` - Mark message as printed
3. Deploy with: `chalice deploy --stage prod`
4. Note API Gateway URL from deployment output

**Expected Output**:
```
https://[api-id].execute-api.us-west-2.amazonaws.com/prod
```

**Provide This URL To**:
- Frontend Agent (for `NEXT_PUBLIC_API_BASE_URL`)
- Hardware Agent (for Pi worker configuration)

### For Frontend Agent

**Prerequisites**: Amplify app must be configured first

**What You Need**:
- **Amplify App ID**: (from Amplify setup)
- **API Gateway URL**: (from Backend Agent after deployment)
- **Environment Variable**: `NEXT_PUBLIC_API_BASE_URL`

**Your Task**:
1. Create Next.js application in `../frontend/` directory
2. Implement message submission form
3. Implement recent messages display
4. Push to GitHub `main` branch
5. Amplify will auto-build and deploy

**Custom Domain** (after DNS propagates):
```
https://www.returntoprint.xyz
```

### For Hardware Agent

**Prerequisites**: Backend API must be deployed

**What You Need**:
- **API Gateway URL**: `https://[api-id].execute-api.us-west-2.amazonaws.com/prod`
- **Endpoints to Call**:
  - `GET /printer/next-to-print` - Poll for messages
  - `POST /printer/mark-printed` - Mark as printed

**Your Task**:
1. Create Python worker script in `../pi-worker/` directory
2. Poll API for unprinted messages
3. Print via USB using `python-escpos`
4. Mark as printed via API
5. Set up as systemd service

---

## 💰 Cost Estimate

Current monthly cost (with core infrastructure only):

| Resource | Cost |
|----------|------|
| DynamoDB (on-demand) | $0.25 - $1.00 |
| Route 53 Hosted Zone | $0.50 |
| CloudWatch Logs | $0.50 |
| CloudWatch Alarms | $0.60 (6 alarms × $0.10) |
| **Total** | **~$2.00/month** |

**After full deployment** (with Lambda, API Gateway, Amplify):
- Estimated: $2.75 - $5.00/month
- Most services covered by AWS Free Tier (first 12 months)

---

## 🔒 Security Features

- ✅ **IAM Least Privilege**: All roles scoped to specific resources
- ✅ **Encryption at Rest**: DynamoDB default encryption
- ✅ **HTTPS Only**: All endpoints use TLS
- ✅ **Public Access Blocked**: S3 buckets (when created)
- ✅ **Point-in-Time Recovery**: DynamoDB backups enabled
- ✅ **Log Retention**: 30 days (not forever, saves costs)
- ✅ **CloudWatch Alarms**: Proactive monitoring
- ⚠️ **No API Authentication**: Add in future phase

---

## 📊 CloudFormation Stacks

### Active Stacks
```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --region us-west-2 \
  --query 'StackSummaries[?contains(StackName, `return-to-print`)]'
```

**Expected Output**:
1. `return-to-print-infra` - Core infrastructure (DynamoDB, IAM)
2. `return-to-print-monitoring` - CloudWatch alarms and dashboard

### Stack Outputs
```bash
# Core infrastructure outputs
aws cloudformation describe-stacks \
  --stack-name return-to-print-infra \
  --region us-west-2 \
  --query 'Stacks[0].Outputs'

# Monitoring stack outputs
aws cloudformation describe-stacks \
  --stack-name return-to-print-monitoring \
  --region us-west-2 \
  --query 'Stacks[0].Outputs'
```

---

## 🚀 Quick Access Links

### AWS Console
- **CloudFormation**: https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2
- **DynamoDB**: https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#tables
- **Route 53**: https://console.aws.amazon.com/route53/v2/hostedzones#ListRecordSets/Z03595423QUR7NOOMU64T
- **CloudWatch Dashboard**: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring
- **CloudWatch Alarms**: https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#alarmsV2:
- **IAM Roles**: https://console.aws.amazon.com/iam/home#/roles

### CLI Commands
```bash
# View DynamoDB table
aws dynamodb describe-table --table-name return-to-print-messages-prod --region us-west-2

# View CloudWatch alarms
aws cloudwatch describe-alarms --alarm-name-prefix return-to-print --region us-west-2

# View Route 53 hosted zone
aws route53 get-hosted-zone --id Z03595423QUR7NOOMU64T

# Tail Lambda logs (after backend deployment)
aws logs tail /aws/lambda/return-to-print-api-prod --follow --region us-west-2
```

---

## ✅ Success Criteria Met

- ✅ All infrastructure defined as code
- ✅ DynamoDB table provisioned with GSI
- ✅ IAM roles follow least privilege
- ✅ CloudWatch alarms configured
- ✅ Route 53 hosted zone created
- ✅ All resources tagged consistently
- ✅ Infrastructure can be recreated from code
- ✅ Documentation complete
- 📋 CI/CD ready to configure (optional)
- 📋 Custom domain ready (after DNS propagation)

---

## 📝 Next Actions (Priority Order)

### Immediate (Today)
1. ✅ **DONE**: Core infrastructure deployed
2. ✅ **DONE**: Monitoring configured
3. ✅ **DONE**: Documentation created

### This Week
1. **Configure DNS**: Update Squarespace nameservers ([DNS_CONFIGURATION.md](./DNS_CONFIGURATION.md))
2. **Backend Development**: Backend Agent creates API ([../backend/](../backend/))
3. **Frontend Setup**: Configure Amplify ([AMPLIFY_SETUP.md](./AMPLIFY_SETUP.md))

### After Backend Deployed
1. **Update Amplify**: Set `NEXT_PUBLIC_API_BASE_URL` environment variable
2. **Frontend Development**: Frontend Agent creates UI
3. **Hardware Setup**: Hardware Agent creates Pi worker

### Optional Enhancements
1. Subscribe email to SNS alarm topic
2. Set up CodePipeline for automated backend deployments
3. Add API authentication (API keys or Cognito)
4. Set up custom domain for API Gateway

---

## 📞 Support

If you encounter issues:
1. Check [README.md](./README.md) for troubleshooting
2. Review setup guides in this directory
3. Check CloudWatch logs for errors
4. Verify CloudFormation stack events

---

**Infrastructure Deployment Complete! 🎉**

All core AWS resources are provisioned and ready for application development. The Backend, Frontend, and Hardware agents can now begin their work with the infrastructure in place.

