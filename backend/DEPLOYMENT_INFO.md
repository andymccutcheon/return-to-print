# Backend API - Deployment Information

## 🎉 Deployment Status: LIVE

The backend API has been successfully deployed and all endpoints are verified working!

---

## API Gateway URL

```
https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/
```

**Region**: us-west-2  
**Stage**: prod  
**Lambda ARN**: `arn:aws:lambda:us-west-2:809581002583:function:message-printer-api-prod`

---

## Verified Endpoints

All endpoints have been tested and are operational:

### ✅ Health Check
```bash
GET /health
# Response: {"status": "healthy"}
```

### ✅ Create Message
```bash
POST /message
Content-Type: application/json
Body: {"content": "Your message here"}

# Response (201):
{
  "id": "uuid",
  "content": "Your message here",
  "created_at": "ISO8601 timestamp",
  "printed": "false",
  "printed_at": null
}
```

### ✅ Get Recent Messages
```bash
GET /messages/recent

# Response (200):
{
  "messages": [...]
}
```

### ✅ Get Next to Print
```bash
GET /printer/next-to-print

# Response (200):
{
  "message": {...} or null
}
```

### ✅ Mark as Printed
```bash
POST /printer/mark-printed
Content-Type: application/json
Body: {"id": "message-uuid"}

# Response (200):
{
  "status": "ok",
  "id": "message-uuid"
}
```

---

## For Frontend Agent

### Environment Variable Required

Add this to your Amplify environment variables or `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

### Endpoints to Use

**1. Create Message (from form submission)**
```javascript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/message`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ content: userMessage })
});
const message = await response.json();
```

**2. Get Recent Messages (for display)**
```javascript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/messages/recent`);
const data = await response.json();
const messages = data.messages;
```

### CORS Configuration
✅ CORS is enabled for all endpoints - cross-origin requests from frontend will work

---

## For Hardware Agent (Raspberry Pi)

### Configuration

Update your Pi worker script with:

```python
API_BASE = "https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod"
```

### Polling Workflow

**1. Poll for Next Message (every 5-10 seconds)**
```python
import requests

response = requests.get(f"{API_BASE}/printer/next-to-print")
data = response.json()

if data['message']:
    message_id = data['message']['id']
    content = data['message']['content']
    # Print the message...
```

**2. Mark as Printed (after successful print)**
```python
response = requests.post(
    f"{API_BASE}/printer/mark-printed",
    json={'id': message_id}
)
```

### Error Handling
- If `next-to-print` returns `{"message": null}`, no messages in queue
- Implement retry logic for network failures
- Log all API calls for debugging

---

## Database Integration

The API is connected to:
- **Table**: `return-to-print-messages-prod`
- **Region**: us-west-2
- **GSI**: `PrintedStatusIndex` (for efficient unprinted queries)
- **IAM Role**: `return-to-print-lambda-role-prod`

All database operations use the Global Secondary Index for optimal performance.

---

## Monitoring & Logs

### CloudWatch Logs
```bash
# View logs
aws logs tail /aws/lambda/message-printer-api-prod --follow --region us-west-2

# Or use Chalice CLI
cd backend/message_printer_api
source venv/bin/activate
chalice logs --name message-printer-api --follow
```

### CloudWatch Dashboard
Dashboard: `return-to-print-monitoring`  
URL: https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards:name=return-to-print-monitoring

### Alarms
Alarms are configured for:
- Lambda errors
- Lambda duration > 5 seconds
- DynamoDB throttling

---

## Testing the API

### Create Test Message
```bash
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/message \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from the API!"}'
```

### Get Recent Messages
```bash
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/messages/recent
```

### Get Next to Print
```bash
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/next-to-print
```

### Mark as Printed
```bash
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/mark-printed \
  -H "Content-Type: application/json" \
  -d '{"id":"YOUR-MESSAGE-ID-HERE"}'
```

---

## Redeployment

To redeploy after code changes:

```bash
cd backend/message_printer_api
source venv/bin/activate
chalice deploy --stage prod
```

The API Gateway URL will remain the same across deployments.

---

## Performance Characteristics

- **Cold Start**: ~500ms
- **Warm Response**: ~50-100ms
- **Lambda Timeout**: 10 seconds
- **Lambda Memory**: 256MB
- **API Gateway Throttling**: 100 requests/second (default)

---

## Next Steps

1. **Frontend Agent**: Configure `NEXT_PUBLIC_API_BASE_URL` and integrate the two endpoints
2. **Hardware Agent**: Configure `API_BASE` and implement polling loop
3. **Infrastructure Agent**: Update any documentation with API Gateway URL

---

## Support

- **CloudWatch Logs**: `/aws/lambda/message-printer-api-prod`
- **GitHub Repo**: `return-to-print/backend/`
- **Documentation**: `backend/README.md`

---

**Backend Agent - Status**: ✅ **COMPLETE**  
**Deployment Date**: 2025-11-24  
**API Version**: 1.0.0

