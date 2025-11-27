# Frontend Agent - Critical Context & Handoff

## 🎯 Backend API is Live - You Can Start Building!

The backend API is deployed and tested. All endpoints are working in production.

---

## Critical Information You Need

### 1. API Gateway Base URL (REQUIRED)
```
https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

**Environment Variable Name:**
```bash
NEXT_PUBLIC_API_BASE_URL=https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

---

### 2. The Two Endpoints You Need

#### POST /message - Create a Message
```typescript
// Request
POST ${API_BASE}/message
Content-Type: application/json
{
  "content": "Message text (1-280 characters)"
}

// Success Response (201)
{
  "id": "uuid",
  "content": "Message text",
  "created_at": "2025-11-24T03:53:48.980757Z",
  "printed": "false",  // String, not boolean!
  "printed_at": null
}

// Error Response (400)
{
  "Code": "BadRequestError",
  "Message": "Content too long: 281 characters (max 280)"
}
```

#### GET /messages/recent - Get Recent Messages
```typescript
// Request
GET ${API_BASE}/messages/recent

// Success Response (200)
{
  "messages": [
    {
      "id": "uuid",
      "content": "...",
      "created_at": "2025-11-24T03:53:48.980757Z",
      "printed": "false",  // String "true" or "false"
      "printed_at": null or "2025-11-24T03:54:00Z"
    }
  ]
}
```

---

## Quick Start Code

### Environment Setup
```bash
# In Amplify Console → Environment Variables
NEXT_PUBLIC_API_BASE_URL=https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod

# Or for local development (.env.local)
NEXT_PUBLIC_API_BASE_URL=https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

### Minimal Working Example
```tsx
'use client';
import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL!;

export default function MessagePrinter() {
  const [content, setContent] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch recent messages on mount
  useEffect(() => {
    fetchMessages();
  }, []);

  async function fetchMessages() {
    try {
      const res = await fetch(`${API_BASE}/messages/recent`);
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    
    const trimmed = content.trim();
    if (!trimmed) {
      setError('Message cannot be empty');
      return;
    }
    
    if (trimmed.length > 280) {
      setError('Message too long (max 280 characters)');
      return;
    }
    
    setLoading(true);
    
    try {
      const res = await fetch(`${API_BASE}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: trimmed }),
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.Message || 'Failed to send message');
      }
      
      // Success!
      setContent('');
      await fetchMessages(); // Refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
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
          rows={4}
          style={{ width: '100%' }}
        />
        <p>{content.length} / 280 characters</p>
        
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        <button type="submit" disabled={loading || !content.trim()}>
          {loading ? 'Sending...' : 'Send to Printer'}
        </button>
      </form>

      <h2>Recent Messages</h2>
      {messages.length === 0 ? (
        <p>No messages yet. Send the first one!</p>
      ) : (
        <ul>
          {messages.map((msg) => (
            <li key={msg.id}>
              <strong>{new Date(msg.created_at).toLocaleString()}</strong>
              <p>{msg.content}</p>
              {msg.printed === 'true' && <span>✓ Printed</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

## Important Notes

### 1. CORS is Enabled ✅
The API has CORS enabled for all origins. Your frontend can call it from any domain without issues.

### 2. `printed` is a String, Not Boolean!
```typescript
// ⚠️ IMPORTANT: printed is "true" or "false" (string)
if (message.printed === 'true') {  // ✅ Correct
if (message.printed === true) {     // ❌ Wrong! Will never match
```

This is because DynamoDB's Global Secondary Index requires string values.

### 3. Validation Rules
- **Content is required** (after trimming whitespace)
- **Max 280 characters** (after trimming)
- **Min 1 character** (after trimming)

The backend will return `400 Bad Request` if these are violated.

### 4. Error Handling
```typescript
try {
  const res = await fetch(`${API_BASE}/message`, { /* ... */ });
  
  if (!res.ok) {
    const errorData = await res.json();
    // errorData.Message contains the error message
    // errorData.Code === "BadRequestError" for validation errors
    throw new Error(errorData.Message || 'Request failed');
  }
  
  const data = await res.json();
  // Success!
} catch (err) {
  // Handle error in UI
}
```

### 5. Message Ordering
Messages in `/messages/recent` are sorted **newest first** (descending by `created_at`).

---

## What You DON'T Need

You do **NOT** need to implement:
- ❌ `/printer/next-to-print` (for Pi worker only)
- ❌ `/printer/mark-printed` (for Pi worker only)
- ❌ Authentication (API is currently public)
- ❌ Pagination (API returns max 10 messages)

---

## Testing the API Before You Build

You can test the API directly with curl:

```bash
# Test creating a message
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/message \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from frontend team!"}'

# Test getting recent messages
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/messages/recent
```

---

## AWS Amplify Configuration

### Setup Steps
1. **Connect GitHub** to AWS Amplify (if not already done)
2. **Select branch**: `main`
3. **Root directory**: `frontend/`
4. **Framework**: Auto-detect (should find Next.js)
5. **Add environment variable**:
   - Key: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod`
6. **Deploy**: Push to `main` branch → auto-builds

### Build Settings (amplify.yml)
The Infrastructure Agent already created `infra/amplify.yml`. You can customize if needed.

---

## Infrastructure Already Provisioned

✅ **Domain**: `returntoprint.xyz` (DNS configured in Route 53)  
✅ **DynamoDB**: Table ready with GSI for efficient queries  
✅ **Lambda**: Backend deployed and tested  
✅ **CloudWatch**: Logging and monitoring active  
✅ **IAM Roles**: All permissions configured  

You just need to build the frontend!

---

## UI/UX Recommendations

### Must-Have Features
1. **Message Form**: Textarea with character counter (280 max)
2. **Submit Button**: Disabled when empty or loading
3. **Recent Messages List**: Show last 10 messages with timestamps
4. **Printed Indicator**: Visual indicator for printed messages (✓)
5. **Error Messages**: Clear feedback for validation errors

### Nice-to-Have Features
1. **Auto-refresh**: Poll `/messages/recent` every 30 seconds
2. **Success animation**: Visual feedback when message is sent
3. **Empty state**: Friendly message when no messages exist
4. **Character warning**: Visual warning at 260+ characters
5. **Responsive design**: Mobile-friendly layout

### Styling Suggestions
- **Modern & Clean**: Simple, receipt-printer aesthetic
- **Monospace font**: For message display (thermal printer vibe)
- **High contrast**: Easy to read
- **Fun touches**: Subtle printer animations or sounds

---

## Detailed Documentation

For comprehensive details, see:
- **API Reference**: `backend/README.md`
- **Integration Guide**: `backend/HANDOFF_TO_FRONTEND.md`
- **Deployment Info**: `backend/DEPLOYMENT_INFO.md`

---

## Support

If you encounter issues:
1. Check CloudWatch logs: `/aws/lambda/message-printer-api-prod`
2. Test API directly with curl commands above
3. Review error responses (they're descriptive)
4. Check CORS is working (should be fine for all origins)

---

## Summary Checklist

Before you start building, verify you have:
- ✅ API Gateway URL: `https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod`
- ✅ Environment variable name: `NEXT_PUBLIC_API_BASE_URL`
- ✅ Two endpoints: `POST /message`, `GET /messages/recent`
- ✅ Validation rules: 1-280 chars, non-empty after trim
- ✅ Remember: `printed` is a string ("true"/"false"), not boolean
- ✅ CORS enabled: Works from any domain

---

## Quick Test

Run this in your browser console (any page):
```javascript
fetch('https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/messages/recent')
  .then(r => r.json())
  .then(data => console.log('Recent messages:', data.messages))
```

If you see messages (or an empty array), the API is working!

---

**Status**: ✅ Backend Ready - Frontend Can Start Immediately  
**Last Updated**: 2025-11-24  
**Backend Version**: 1.0.0

**Let's build a beautiful frontend! 🎨**

