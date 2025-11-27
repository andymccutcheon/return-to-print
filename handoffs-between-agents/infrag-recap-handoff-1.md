# Infrastructure Agent - Deployment Recap for Other Agents

## 🎉 Summary: Core Infrastructure Fully Deployed

As the **Infrastructure/DevOps Agent**, I have successfully provisioned all AWS resources in **us-west-2** for the Return-to-Print project. The foundation is ready for application development.

---

## ✅ What's Deployed and Ready

### 1. **DynamoDB Database** - READY FOR USE
- **Table Name**: `return-to-print-messages-prod`
- **Region**: `us-west-2`
- **Billing**: PAY_PER_REQUEST (on-demand, scales automatically)
- **Primary Key**: `id` (String)
- **Global Secondary Index**: `PrintedStatusIndex`
  - Partition Key: `printed` (String) 
  - Sort Key: `created_at` (String)
  - Use this for efficient "next unprinted message" queries
- **Features**: Point-in-time recovery enabled, DynamoDB Streams enabled
- **Status**: ✅ ACTIVE and ready for reads/writes

### 2. **IAM Roles** - READY FOR USE
- **Lambda Execution Role**: `return-to-print-lambda-role-prod`
  - ARN: `arn:aws:iam::809581002583:role/return-to-print-lambda-role-prod`
  - Permissions: Full DynamoDB access to messages table, CloudWatch Logs
  - **Backend Agent**: Use this role when deploying Lambda functions

- **CodeBuild Service Role**: `return-to-print-codebuild-role-prod`
  - ARN: `arn:aws:iam::809581002583:role/return-to-print-codebuild-role-prod`
  - Permissions: Deploy Lambda, API Gateway, CloudFormation

### 3. **DNS (Route 53)** - CONFIGURED, NEEDS NAMESERVER UPDATE
- **Domain**: returntoprint.xyz
- **Hosted Zone ID**: Z03595423QUR7NOOMU64T
- **Status**: Created, waiting for nameserver delegation
- **Nameservers** (configure in Squarespace):
  ```
  ns-1738.awsdns-25.co.uk
  ns-1398.awsdns-46.org
  ns-233.awsdns-29.com
  ns-662.awsdns-18.net
  ```
- **Action Required**: Update Squarespace DNS to point to these nameservers
- **Timeline**: 24-48 hours for propagation after update

### 4. **CloudWatch Monitoring** - ACTIVE
- **Dashboard**: `return-to-print-monitoring`
  - View at: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring
- **Alarms**: 6 configured (DynamoDB throttles/errors, Lambda errors/duration/throttles)
- **Log Groups**: 
  - `/aws/lambda/return-to-print-api-prod` (30-day retention)
  - `/aws/apigateway/return-to-print-api-prod` (30-day retention)
- **SNS Topic**: `arn:aws:sns:us-west-2:809581002583:return-to-print-alarms-prod`

### 5. **Infrastructure as Code** - ALL FILES CREATED
- Location: `/Users/andymccutcheon/Documents/GitHub/return-to-print/infra/`
- 14 files created (templates, build specs, policies, documentation)
- Everything version-controlled and reproducible

---

## 🚀 Agent-Specific Handoff Instructions

### For **BACKEND AGENT** - ✅ START NOW

**You have everything you need to begin!**

#### What You Can Do Now:
1. Create Chalice application in `backend/` directory
2. Implement the 4 REST API endpoints:
   - `POST /message` - Create new message
   - `GET /messages/recent` - List recent messages
   - `GET /printer/next-to-print` - Get oldest unprinted message
   - `POST /printer/mark-printed` - Mark message as printed
3. Deploy to AWS Lambda

#### Key Configuration Details:
```python
# DynamoDB Configuration
TABLE_NAME = "return-to-print-messages-prod"
REGION = "us-west-2"

# Table Schema
Primary Key: id (String UUID)
Attributes: content, created_at, printed (boolean), printed_at

# For "next unprinted" queries, use:
GSI: PrintedStatusIndex
Query: printed = "false", sort by created_at ascending
```

#### Deployment:
```bash
cd backend
chalice deploy --stage prod
```

#### What You'll Get:
After deployment, Chalice will output an **API Gateway URL** like:
```
https://[api-id].execute-api.us-west-2.amazonaws.com/prod
```

#### ⚠️ IMPORTANT - Share This URL With:
1. **Frontend Agent**: For `NEXT_PUBLIC_API_BASE_URL` environment variable
2. **Hardware Agent**: For Pi worker API polling configuration
3. **Infrastructure Agent** (me): To update Amplify environment variables

---

### For **FRONTEND AGENT** - ⏳ AMPLIFY SETUP REQUIRED FIRST

**Prerequisites**: Amplify app must be configured before you can deploy

#### Current Status:
- ✅ Amplify configuration files ready (`infra/amplify.yml`, `infra/amplify-app.yaml`)
- ⏳ **Needs manual setup**: Connect GitHub repo to AWS Amplify
- 📖 Setup guide: `/Users/andymccutcheon/Documents/GitHub/return-to-print/infra/AMPLIFY_SETUP.md`

#### Recommended Approach:
1. **Set up Amplify via AWS Console** (easiest):
   - Go to AWS Amplify in us-west-2
   - Click "New app" → "Host web app"
   - Connect GitHub repo: `andymccutcheon/return-to-print`
   - Branch: `main`
   - Root directory: `frontend/`
   - Amplify will auto-detect Next.js

2. **Add Environment Variable** (initially use placeholder):
   ```
   NEXT_PUBLIC_API_BASE_URL = https://placeholder.execute-api.us-west-2.amazonaws.com/prod
   ```
   *(Update with real URL after Backend Agent deploys)*

#### What You Can Do Next:
1. Create Next.js app in `frontend/` directory
2. Implement:
   - Message submission form (textarea + submit button)
   - Recent messages display (list view)
   - Call backend API using `NEXT_PUBLIC_API_BASE_URL`
3. Push to `main` branch → Amplify auto-builds and deploys

#### Expected Output:
- **Amplify URL**: `https://main.d[app-id].amplifyapp.com`
- **Custom Domain** (after DNS propagates): `https://www.returntoprint.xyz`

---

### For **HARDWARE AGENT** - ⏳ WAIT FOR BACKEND DEPLOYMENT

**Prerequisites**: Backend Agent must deploy API first

#### What You Need From Backend Agent:
- **API Gateway Base URL**: `https://[api-id].execute-api.us-west-2.amazonaws.com/prod`

#### API Endpoints You'll Call:
1. **Poll for messages** (call every 5-10 seconds):
   ```
   GET /printer/next-to-print
   ```
   Returns: `{message: {id, content, created_at, printed}}` or `{message: null}`

2. **Mark as printed** (after successful print):
   ```
   POST /printer/mark-printed
   Body: {id: "message-uuid"}
   ```
   Returns: `{status: "ok", id: "message-uuid"}`

#### Your Implementation:
1. Create Python worker script in `pi-worker/` directory
2. Poll API in loop
3. Print via USB using `python-escpos`
4. Mark printed via API
5. Handle errors and retry logic
6. Set up as systemd service for auto-start

#### No AWS Credentials Needed on Pi:
The API is public (no authentication yet), so Pi worker just needs the URL.

---

## 📋 Pending Manual Configuration

### 1. **DNS Nameservers** (For Custom Domain)
- **Action**: Update Squarespace domain settings for `returntoprint.xyz`
- **Guide**: `infra/DNS_CONFIGURATION.md`
- **Urgency**: Not blocking development, but needed for custom domain
- **Timeline**: Allow 24-48 hours for propagation after update

### 2. **Amplify App Connection** (For Frontend Deployment)
- **Action**: Connect GitHub to AWS Amplify via Console
- **Guide**: `infra/AMPLIFY_SETUP.md`
- **Urgency**: Required before Frontend Agent can deploy
- **Timeline**: 5-10 minutes to configure

### 3. **CodePipeline** (Optional - For Backend CI/CD)
- **Action**: Set up automated backend deployments
- **Guide**: `infra/CODEPIPELINE_SETUP.md`
- **Urgency**: Optional (can deploy manually with `chalice deploy`)
- **Alternative**: Manual deployments work fine for now

---

## 💡 Development Workflow

### Recommended Order:
1. ✅ **Infrastructure** - DONE
2. 🔵 **Backend Agent** - START NOW (no blockers)
3. 🔵 **Amplify Setup** - Owner configures GitHub connection
4. 🔵 **Frontend Agent** - After Amplify is ready
5. 🔵 **Hardware Agent** - After Backend provides API URL

### Parallel Work Possible:
- Backend and Amplify setup can happen simultaneously
- Frontend and Hardware agents can prepare code while waiting

---

## 📊 Quick Reference

### AWS Console Links (us-west-2):
- **DynamoDB Tables**: https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#tables
- **CloudFormation Stacks**: https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2
- **CloudWatch Dashboard**: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring
- **Route 53 Hosted Zone**: https://console.aws.amazon.com/route53/v2/hostedzones#ListRecordSets/Z03595423QUR7NOOMU64T

### CLI Verification Commands:
```bash
# Check DynamoDB table
aws dynamodb describe-table --table-name return-to-print-messages-prod --region us-west-2

# List CloudFormation stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE --region us-west-2

# View CloudWatch alarms
aws cloudwatch describe-alarms --alarm-name-prefix return-to-print --region us-west-2
```

---

## 💰 Current Cost: ~$2/month

All infrastructure optimized for cost:
- DynamoDB: On-demand (pay per request)
- Lambda: Free tier eligible
- CloudWatch: 30-day log retention
- Route 53: $0.50/month hosted zone

---

## 📞 Infrastructure Support

All documentation is in: `/Users/andymccutcheon/Documents/GitHub/return-to-print/infra/`

**Key Files**:
- `README.md` - Complete infrastructure guide
- `DEPLOYMENT_SUMMARY.md` - Detailed deployment report
- `INFRASTRUCTURE_STATUS.md` - Current status overview
- `DNS_CONFIGURATION.md` - Nameserver setup
- `AMPLIFY_SETUP.md` - Frontend hosting setup
- `CODEPIPELINE_SETUP.md` - Backend CI/CD setup

**Need Help?** Check the documentation first, or reach out to Infrastructure Agent.

---

## ✅ Infrastructure Agent - Mission Complete!

All infrastructure provisioning tasks are done. The platform is stable, secure, and ready for application development. Backend Agent can start immediately!

**Status**: 🟢 **OPERATIONAL** - Ready for application deployment