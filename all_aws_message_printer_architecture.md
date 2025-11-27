# Internet Message → Thermal Receipt Printer  
**Architecture: All-AWS (Route 53 + Amplify + API Gateway + Lambda + DynamoDB) + Raspberry Pi + Rongta RP326**

> This is an alternate version of the earlier plan: **everything web-related (domain, CI/CD, frontend, backend) runs on AWS**.

---

## 0. High-Level Architecture (All AWS)

**Goal:**  
Anyone visits `https://www.yourdomain.com`, types a message, and it prints on your physical Rongta RP326 receipt printer connected to a Raspberry Pi.

**Components:**

1. **Domain & DNS – Route 53**
   - Host your domain in **Amazon Route 53**.
   - `www.yourdomain.com` → AWS Amplify-hosted frontend.

2. **Frontend – React/Next.js on AWS Amplify Hosting**
   - Static or SPA frontend built from GitHub repo.
   - Amplify provides:
     - CI/CD (build on every merge to `main`).
     - Hosting + HTTPS.
     - Integration with custom domain via Route 53.

3. **Backend – API Gateway + Lambda + DynamoDB**
   - **API Gateway**: REST API endpoints consumed by frontend & Pi worker.
   - **Lambda (Python)**: application logic (create message, fetch next, mark printed).
   - **DynamoDB**: message queue storage.

4. **CI/CD – AWS**
   - **Frontend**: Amplify’s built-in CI/CD from GitHub `main`.
   - **Backend**: AWS CodePipeline + CodeBuild + CloudFormation/SAM from the same GitHub repo (or a second one).

5. **Printer Worker – Raspberry Pi 3B+ + Rongta RP326**
   - Python script running on Pi.
   - Polls the AWS API for messages.
   - Prints them via USB using `python-escpos`.
   - Marks them printed via API.
   - Runs as a `systemd` service.

---

## 1. Repository Structure

Single GitHub repo to drive everything:

```text
message-printer/
  frontend/        # React/Next.js frontend (Amplify-hosted)
  backend/         # Lambda/API Gateway (SAM/Chalice/etc.)
  pi-worker/       # Raspberry Pi print worker
  infra/           # Optional: IaC (SAM/CloudFormation/CDK)
  README.md
```

You can share this repo between:

- Amplify (for frontend CI/CD).
- CodePipeline (for backend CI/CD).

---

## 2. Domain & DNS (Route 53)

1. **Register or transfer your domain** to Route 53 (or just create a hosted zone if already registered elsewhere and you’re pointing NS records to Route 53).
2. In the hosted zone:
   - Create a **CNAME or ALIAS** for `www.yourdomain.com` → Amplify app (Amplify will guide this).
3. Amplify will automatically provision **HTTPS certificates** via ACM once the DNS is set correctly.

---

## 3. Frontend (AWS Amplify Hosting)

### 3.1 Scaffold Frontend

In `frontend/`, use React or Next.js. Example with Next.js:

```bash
cd frontend
npx create-next-app@latest .
```

You’ll build a simple page:

- `<textarea>` for message input.
- Button to submit.
- List of recent messages.

It will call the backend via an environment variable:

- `NEXT_PUBLIC_API_BASE_URL = https://<api-id>.execute-api.<region>.amazonaws.com/prod`

Example pseudo-code (`pages/index.tsx`):

```tsx
import { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL!;

export default function Home() {
  const [content, setContent] = useState("");
  const [messages, setMessages] = useState<any[]>([]);

  const fetchMessages = async () => {
    const res = await fetch(`${API_BASE}/messages/recent`);
    const data = await res.json();
    setMessages(data.messages || []);
  };

  const submitMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) return;

    const res = await fetch(`${API_BASE}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: trimmed }),
    });
    if (res.ok) {
      setContent("");
      await fetchMessages();
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  return (
    <main>
      <h1>Send a Message to the Printer</h1>
      <form onSubmit={submitMessage}>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={280}
          placeholder="Type your message..."
          required
        />
        <button type="submit">Send</button>
      </form>

      <h2>Recent Messages</h2>
      <ul>
        {messages.map((m) => (
          <li key={m.id}>
            <strong>{m.created_at}</strong>: {m.content}
          </li>
        ))}
      </ul>
    </main>
  );
}
```

### 3.2 Amplify CI/CD Setup

1. Go to **AWS Amplify → New app → Host web app**.
2. Connect GitHub, choose the `message-printer` repo.
3. Select `frontend/` as the root, `main` as the branch.
4. Amplify detects framework → configure build:
   - Build commands (in Amplify UI or `amplify.yml`):

     ```yaml
     version: 1
     frontend:
       phases:
         preBuild:
           commands:
             - cd frontend
             - npm install
         build:
           commands:
             - npm run build
       artifacts:
         baseDirectory: frontend/.next
         files:
           - '**/*'
       cache:
         paths:
           - frontend/node_modules/**/*
     ```

   (For a static export you might output to `frontend/out` instead; adjust `baseDirectory` accordingly.)

5. Set **environment variable** in Amplify:
   - `NEXT_PUBLIC_API_BASE_URL = https://<your-api-id>.execute-api.<region>.amazonaws.com/prod`

6. On every merge to `main`, Amplify will:
   - Pull latest code.
   - Build frontend.
   - Deploy to an Amplify URL and, once domain is attached, to `www.yourdomain.com`.

### 3.3 Attach Custom Domain

In Amplify:

1. Go to **Domain management → Add domain**.
2. Choose your Route 53 hosted domain.
3. Map `www` to your Amplify app.
4. Amplify creates DNS records in Route 53 automatically.
5. After propagation, `https://www.yourdomain.com` will show your app.

---

## 4. Backend (API Gateway + Lambda + DynamoDB)

We’ll keep the same API design as before, but now all within AWS.

### 4.1 API Design

Endpoints:

- `POST /message`
- `GET /messages/recent`
- `GET /printer/next-to-print`
- `POST /printer/mark-printed`

### 4.2 Data Model (DynamoDB)

Table: `messages`

- PK: `id` (string, UUID)
- Attributes:
  - `content` (string)
  - `created_at` (string, ISO8601)
  - `printed` (bool)
  - `printed_at` (string, nullable)
- Optional GSI:
  - GSI1: PK `printed`, SK `created_at` for efficient “next unprinted” queries.

### 4.3 Implementation: Python + Lambda (Chalice or SAM)

**Option: AWS Chalice (simple)**

In `backend/`:

```bash
cd backend
pip install chalice
chalice new-project message_printer_api
```

Update `backend/message_printer_api/app.py`:

```python
from chalice import Chalice, BadRequestError
from datetime import datetime
import uuid
import boto3

app = Chalice(app_name='message-printer-api')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('messages')

@app.route('/message', methods=['POST'], cors=True)
def create_message():
    body = app.current_request.json_body or {}
    content = (body.get('content') or '').strip()
    if not content:
        raise BadRequestError('Empty content')
    if len(content) > 280:
        raise BadRequestError('Message too long (max 280 chars)')

    msg_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + 'Z'
    item = {
        'id': msg_id,
        'content': content,
        'created_at': now,
        'printed': False,
        'printed_at': None,
    }
    table.put_item(Item=item)
    return item

@app.route('/messages/recent', methods=['GET'], cors=True)
def recent_messages():
    resp = table.scan()
    items = resp.get('Items', [])
    items.sort(key=lambda x: x['created_at'], reverse=True)
    return {'messages': items[:10]}

@app.route('/printer/next-to-print', methods=['GET'], cors=True)
def next_to_print():
    resp = table.scan()
    items = [i for i in resp.get('Items', []) if not i.get('printed')]
    if not items:
        return {'message': None}
    items.sort(key=lambda x: x['created_at'])
    return {'message': items[0]}

@app.route('/printer/mark-printed', methods=['POST'], cors=True)
def mark_printed():
    body = app.current_request.json_body or {}
    msg_id = body.get('id')
    if not msg_id:
        raise BadRequestError('Missing id')

    now = datetime.utcnow().isoformat() + 'Z'
    table.update_item(
        Key={'id': msg_id},
        UpdateExpression='SET printed = :p, printed_at = :t',
        ExpressionAttributeValues={':p': True, ':t': now}
    )
    return {'status': 'ok', 'id': msg_id}
```

### 4.4 Backend CI/CD – CodePipeline

You can:

- Start with simple `chalice deploy` from your laptop to get going.
- Then add **AWS CodePipeline**:

Pipeline structure:

1. **Source**: GitHub (same `message-printer` repo).
2. **Build**: CodeBuild project:
   - Install deps.
   - Run `cd backend/message_printer_api && chalice deploy --stage prod`.
3. **Deploy**: Either as part of the build or using CloudFormation if you export a SAM template.

Minimal `buildspec.yml` example (in `backend/`):

```yaml
version: 0.2

phases:
  install:
    commands:
      - pip install chalice
  build:
    commands:
      - cd backend/message_printer_api
      - chalice deploy --stage prod
artifacts:
  files:
    - '**/*'
```

Now each merge to `main` can trigger CodePipeline to redeploy your backend Lambda/API Gateway stack.

---

## 5. Raspberry Pi Worker (unchanged, still AWS-integrated)

The Pi side doesn’t care where the web lives—it just calls the API base URL.

### 5.1 Dependencies

On the Pi:

```bash
sudo apt update
sudo apt install python3-pip
pip3 install requests python-escpos
```

### 5.2 Worker Script (`pi-worker/worker.py`)

```python
import time
import requests
from escpos.printer import Usb  # python-escpos

API_BASE = "https://<your-api-id>.execute-api.<region>.amazonaws.com/prod"

# Replace with actual vendor/product IDs from `lsusb`
VENDOR_ID = 0x1234
PRODUCT_ID = 0x5678

