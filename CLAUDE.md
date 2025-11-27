# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pennant** is an Internet-connected thermal receipt printer system that allows anyone to visit a website, type a message, and have it print on a physical Rongta RP326 receipt printer connected to a Raspberry Pi.

## Architecture

This is an **All-AWS architecture** with the following components:

1. **Frontend**: React/Next.js hosted on AWS Amplify
   - Simple web UI with textarea for message input
   - Displays recent messages
   - Calls backend API

2. **Backend**: API Gateway + Lambda (Python) + DynamoDB
   - REST API with endpoints for creating messages, fetching recent messages, and printer operations
   - DynamoDB table stores message queue with printed status tracking
   - Implemented using AWS Chalice framework

3. **Domain & DNS**: Amazon Route 53
   - Hosts domain and manages DNS routing to Amplify frontend

4. **CI/CD**:
   - Frontend: Amplify built-in CI/CD from GitHub `main` branch
   - Backend: AWS CodePipeline + CodeBuild for Lambda deployments

5. **Printer Worker**: Raspberry Pi 3B+ with Rongta RP326
   - Python script polls AWS API for unprinted messages
   - Prints via USB using `python-escpos` library
   - Marks messages as printed via API
   - Runs as systemd service

## Repository Structure

```
message-printer/
  frontend/        # React/Next.js frontend (Amplify-hosted)
  backend/         # Lambda/API Gateway (AWS Chalice)
  pi-worker/       # Raspberry Pi print worker
  infra/           # Optional: IaC (SAM/CloudFormation/CDK)
```

## Backend API Endpoints

- `POST /message` - Create a new message to print (max 280 chars)
- `GET /messages/recent` - Fetch 10 most recent messages
- `GET /printer/next-to-print` - Get oldest unprinted message
- `POST /printer/mark-printed` - Mark a message as printed

## DynamoDB Schema

**Table**: `messages`
- **PK**: `id` (string, UUID)
- **Attributes**:
  - `content` (string) - Message text
  - `created_at` (string, ISO8601)
  - `printed` (bool)
  - `printed_at` (string, nullable)
- **Optional GSI**: `printed` (PK) + `created_at` (SK) for efficient unprinted message queries

## Development Commands

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev          # Start development server
npm run build        # Production build
npm run start        # Start production server
```

### Backend (Chalice)
```bash
cd backend/message_printer_api
pip install chalice boto3
chalice local        # Local development server
chalice deploy --stage prod    # Deploy to AWS
```

### Pi Worker
```bash
cd pi-worker
pip3 install requests python-escpos
python3 worker.py    # Run worker script
```

## Environment Variables

### Frontend
- `NEXT_PUBLIC_API_BASE_URL` - Backend API base URL (e.g., `https://<api-id>.execute-api.<region>.amazonaws.com/prod`)

### Pi Worker
- Update `API_BASE` in `worker.py` with backend API URL
- Update `VENDOR_ID` and `PRODUCT_ID` with USB printer IDs from `lsusb`

## Key Implementation Notes

1. **CORS**: Backend API must enable CORS for frontend to communicate
2. **Message Validation**: 280 character limit enforced in backend
3. **Polling Interval**: Pi worker polls every few seconds for new messages
4. **Error Handling**: Pi worker should handle printer disconnects gracefully
5. **Systemd Service**: Pi worker runs as a service for reliability and auto-restart

## AWS Resources Setup

1. **DynamoDB**: Create `messages` table with `id` as primary key
2. **IAM**: Lambda needs DynamoDB read/write permissions
3. **API Gateway**: Configured automatically by Chalice
4. **Amplify**: Connect to GitHub repo, set frontend build settings
5. **Route 53**: Create hosted zone, attach to Amplify app for custom domain
