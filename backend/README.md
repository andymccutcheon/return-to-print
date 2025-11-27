# Message Printer API - Backend

A serverless REST API built with AWS Chalice for managing a message queue that prints to a physical receipt printer via Raspberry Pi.

## Architecture

- **Framework**: AWS Chalice (Python serverless microframework)
- **Compute**: AWS Lambda
- **API**: Amazon API Gateway (REST API with CORS)
- **Database**: Amazon DynamoDB with Global Secondary Index
- **Region**: us-west-2
- **Language**: Python 3.11+ with type hints

## Project Structure

```
backend/
├── message_printer_api/
│   ├── app.py                 # Main Chalice app (route handlers)
│   ├── chalicelib/
│   │   ├── __init__.py
│   │   ├── db.py              # DynamoDB operations
│   │   ├── models.py          # Data models/types
│   │   └── validators.py     # Input validation
│   ├── requirements.txt       # Python dependencies
│   └── .chalice/
│       ├── config.json        # Chalice configuration
│       └── policy.json        # IAM policy reference
├── tests/
│   ├── test_api.py            # API integration tests
│   ├── test_db.py             # Database operation tests
│   ├── test_validators.py    # Validation logic tests
│   └── requirements-test.txt  # Test dependencies
└── README.md
```

## API Endpoints

### 1. POST /message
Create a new message to be printed.

**Request:**
```json
{
  "content": "Message text here (1-280 characters)"
}
```

**Success Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Message text here",
  "created_at": "2025-11-24T10:30:00Z",
  "printed": "false",
  "printed_at": null
}
```

**Error Responses:**
- `400`: Invalid content (empty, whitespace only, or > 280 characters)
- `500`: Internal server error

---

### 2. GET /messages/recent
Get the 10 most recent messages, sorted by creation time (newest first).

**Success Response (200):**
```json
{
  "messages": [
    {
      "id": "uuid",
      "content": "...",
      "created_at": "2025-11-24T10:30:00Z",
      "printed": "true",
      "printed_at": "2025-11-24T10:31:00Z"
    }
  ]
}
```

**Error Responses:**
- `500`: Internal server error

---

### 3. GET /printer/next-to-print
Get the oldest unprinted message for the Raspberry Pi worker.

**Success Response (200) - Message available:**
```json
{
  "message": {
    "id": "uuid",
    "content": "...",
    "created_at": "2025-11-24T10:30:00Z",
    "printed": "false",
    "printed_at": null
  }
}
```

**Success Response (200) - No messages:**
```json
{
  "message": null
}
```

**Error Responses:**
- `500`: Internal server error

---

### 4. POST /printer/mark-printed
Mark a message as printed (called by Raspberry Pi worker after successful print).

**Request:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (200):**
```json
{
  "status": "ok",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses:**
- `400`: Missing or invalid id
- `500`: Internal server error

---

### 5. GET /health
Health check endpoint for monitoring.

**Success Response (200):**
```json
{
  "status": "healthy"
}
```

## Setup & Installation

### Prerequisites
- Python 3.11 or higher
- AWS CLI configured with appropriate credentials
- Access to the `return-to-print-messages-prod` DynamoDB table in us-west-2

### Local Development Setup

1. **Clone the repository:**
```bash
cd backend/message_printer_api
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install test dependencies (optional):**
```bash
pip install -r ../tests/requirements-test.txt
```

### Running Locally

Start the local development server:
```bash
chalice local --port 8000
```

The API will be available at `http://localhost:8000`

Test the endpoints:
```bash
# Create a message
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello from local!"}'

# Get recent messages
curl http://localhost:8000/messages/recent

# Get next to print
curl http://localhost:8000/printer/next-to-print

# Health check
curl http://localhost:8000/health
```

## Testing

Run the test suite:
```bash
cd backend
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_validators.py -v
pytest tests/test_db.py -v
pytest tests/test_api.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=message_printer_api --cov-report=html
```

## Deployment

### Deploy to AWS

Deploy to production:
```bash
cd backend/message_printer_api
chalice deploy --stage prod
```

Deploy to development:
```bash
chalice deploy --stage dev
```

After deployment, Chalice will output:
```
Resources deployed:
  - Lambda ARN: arn:aws:lambda:us-west-2:...
  - Rest API URL: https://[api-id].execute-api.us-west-2.amazonaws.com/prod/
```

**IMPORTANT**: Copy the API Gateway URL and share it with:
1. Frontend Agent - for `NEXT_PUBLIC_API_BASE_URL` environment variable
2. Hardware Agent - for Pi worker API polling configuration

### View Logs

View CloudWatch logs:
```bash
chalice logs --name message-printer-api
```

Tail logs in real-time:
```bash
chalice logs --name message-printer-api --follow
```

### Delete Deployment

Remove deployed resources:
```bash
chalice delete --stage prod
```

## Configuration

### Environment Variables

The application uses the following environment variables (configured in `.chalice/config.json`):

- `DYNAMODB_TABLE`: DynamoDB table name (default: `return-to-print-messages-prod`)

### DynamoDB Schema

**Table Name**: `return-to-print-messages-prod`

**Primary Key:**
- Partition Key: `id` (String) - UUID v4

**Attributes:**
- `id` (String) - Unique identifier
- `content` (String) - Message text (1-280 characters)
- `created_at` (String) - ISO 8601 timestamp
- `printed` (String) - "true" or "false" (string for GSI compatibility)
- `printed_at` (String, nullable) - ISO 8601 timestamp when printed

**Global Secondary Index:**
- Name: `PrintedStatusIndex`
- Partition Key: `printed` (String)
- Sort Key: `created_at` (String)
- Purpose: Efficient queries for unprinted messages in chronological order

### IAM Permissions

The Lambda function uses the pre-provisioned IAM role:
- Role: `return-to-print-lambda-role-prod`
- ARN: `arn:aws:iam::809581002583:role/return-to-print-lambda-role-prod`

Required permissions:
- DynamoDB: PutItem, GetItem, UpdateItem, Query, Scan on messages table and indexes
- CloudWatch Logs: CreateLogGroup, CreateLogStream, PutLogEvents

## Development Guidelines

### Code Quality
- All functions have type hints
- All public functions have docstrings
- PEP 8 compliant (88 character line length)
- Comprehensive error handling with structured logging

### Type Checking
```bash
mypy message_printer_api/app.py
mypy message_printer_api/chalicelib/
```

### Linting
```bash
pylint message_printer_api/app.py
```

### Adding New Dependencies
1. Add to `requirements.txt`
2. Ensure Lambda compatibility
3. Keep package size minimal (< 50MB for optimal cold starts)

## Integration Points

### Frontend Integration
The frontend needs the API Gateway URL after deployment:
```bash
NEXT_PUBLIC_API_BASE_URL=https://[api-id].execute-api.us-west-2.amazonaws.com/prod
```

The frontend will call:
- `POST /message` - to create new messages
- `GET /messages/recent` - to display recent messages

### Hardware (Raspberry Pi) Integration
The Pi worker needs the API Gateway URL:
```python
API_BASE = "https://[api-id].execute-api.us-west-2.amazonaws.com/prod"
```

The Pi worker will:
1. Poll `GET /printer/next-to-print` every 5-10 seconds
2. Print the message content
3. Call `POST /printer/mark-printed` with the message ID

## Troubleshooting

### Common Issues

**Issue: "Unable to import module 'app'"**
- Ensure all dependencies are in `requirements.txt`
- Check Lambda deployment package size

**Issue: "DynamoDB table not found"**
- Verify table name in `.chalice/config.json`
- Confirm you're deploying to the correct region (us-west-2)

**Issue: "Access Denied" errors**
- Verify IAM role has correct permissions
- Check that `iam_role_arn` in config.json is correct

**Issue: Slow queries for unprinted messages**
- Ensure Global Secondary Index `PrintedStatusIndex` exists
- Verify `get_next_unprinted()` is using the index (not scanning)

### Viewing Errors in CloudWatch

1. Go to AWS CloudWatch Console (us-west-2)
2. Navigate to Log Groups
3. Find `/aws/lambda/message-printer-api-prod`
4. View recent log streams

## Performance Considerations

- **Cold Starts**: Lambda cold start ~500ms, warm ~50ms
- **DynamoDB**: On-demand billing scales automatically
- **API Gateway**: Throttling set at 100 requests/second (configurable)
- **Lambda Timeout**: Set to 10 seconds
- **Lambda Memory**: 256MB (adjust based on usage patterns)

## Security

- **CORS**: Enabled for all endpoints (currently allows all origins)
- **Authentication**: Not implemented (public API - consider adding API keys for production)
- **Input Validation**: All inputs validated before processing
- **Error Messages**: Generic errors returned to prevent information leakage

## Monitoring

CloudWatch Dashboard: `return-to-print-monitoring`

Key Metrics:
- Lambda Invocations
- Lambda Errors
- Lambda Duration
- DynamoDB Read/Write Capacity
- API Gateway 4xx/5xx Errors

CloudWatch Alarms configured for:
- Lambda errors > 5 in 5 minutes
- DynamoDB throttling
- Lambda duration > 5 seconds

## Support

For infrastructure-related issues, contact the Infrastructure Agent.
For API bugs or feature requests, open an issue in the repository.

---

**Status**: ✅ Ready for Deployment
**Last Updated**: 2025-11-24

