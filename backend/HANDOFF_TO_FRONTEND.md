# Backend API → Frontend Agent Handoff

## 🎯 Backend API is Ready for Integration!

The REST API is deployed and all endpoints have been tested. You can now integrate with the backend.

---

## API Gateway Base URL

```
https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

---

## Required Configuration

### Environment Variable

Add this to your Amplify environment variables or local `.env` file:

```bash
NEXT_PUBLIC_API_BASE_URL=https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

**In Amplify Console:**
1. Go to your app → Environment variables
2. Add: `NEXT_PUBLIC_API_BASE_URL` = `https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod`
3. Redeploy app

---

## Endpoints You Need

### 1. Create Message (POST /message)

**Usage**: When user submits the message form

```typescript
async function createMessage(content: string) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/message`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to create message');
  }
  
  return response.json();
}
```

**Request:**
```json
{
  "content": "Message text (1-280 characters)"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Message text",
  "created_at": "2025-11-24T03:53:48.980757Z",
  "printed": "false",
  "printed_at": null
}
```

**Error Handling:**
- `400`: Content is empty, whitespace, or > 280 characters
- `500`: Server error

---

### 2. Get Recent Messages (GET /messages/recent)

**Usage**: Load and display recent messages on the page

```typescript
async function getRecentMessages() {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE_URL}/messages/recent`
  );
  
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  
  const data = await response.json();
  return data.messages;
}
```

**Response (200):**
```json
{
  "messages": [
    {
      "id": "uuid",
      "content": "Message text",
      "created_at": "2025-11-24T03:53:48.980757Z",
      "printed": "true",
      "printed_at": "2025-11-24T03:54:00.123456Z"
    }
  ]
}
```

**Notes:**
- Returns up to 10 most recent messages
- Sorted by `created_at` descending (newest first)
- Empty array if no messages exist

---

## Example React Component

```tsx
import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL!;

export default function MessagePrinter() {
  const [content, setContent] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch recent messages on load
  useEffect(() => {
    fetchMessages();
  }, []);

  async function fetchMessages() {
    try {
      const res = await fetch(`${API_BASE}/messages/recent`);
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const trimmed = content.trim();
    if (!trimmed) return;
    
    setLoading(true);
    
    try {
      const res = await fetch(`${API_BASE}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: trimmed }),
      });
      
      if (!res.ok) {
        const error = await res.json();
        alert(`Error: ${error.Message || 'Failed to create message'}`);
        return;
      }
      
      // Success!
      setContent('');
      await fetchMessages(); // Refresh list
    } catch (error) {
      console.error('Failed to create message:', error);
      alert('Failed to create message');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>Send a Message to the Printer</h1>
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Type your message..."
          maxLength={280}
          required
        />
        <p>{content.length} / 280 characters</p>
        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send to Printer'}
        </button>
      </form>

      <h2>Recent Messages</h2>
      <ul>
        {messages.map((msg) => (
          <li key={msg.id}>
            <strong>{msg.created_at}</strong>: {msg.content}
            {msg.printed === 'true' && ' ✓ Printed'}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## CORS Configuration

✅ **CORS is enabled** - Your frontend can make requests from any domain

---

## Validation Rules

The backend enforces these rules:

- **Content required**: Cannot be empty or whitespace-only
- **Max length**: 280 characters (after trimming)
- **Min length**: At least 1 character (after trimming)

Handle these errors in your UI validation before submitting.

---

## Testing

You can test the API directly before integration:

```bash
# Create a test message
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/message \
  -H "Content-Type: application/json" \
  -d '{"content":"Test from frontend team"}'

# Get recent messages
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/messages/recent
```

---

## What You DON'T Need

You do **NOT** need to use these endpoints (they're for the Pi worker):
- ❌ `GET /printer/next-to-print`
- ❌ `POST /printer/mark-printed`

---

## Questions?

Check the comprehensive API documentation:
- `backend/README.md` - Full API documentation
- `backend/DEPLOYMENT_INFO.md` - Deployment details

---

**Status**: ✅ Ready for Frontend Integration  
**Last Updated**: 2025-11-24

