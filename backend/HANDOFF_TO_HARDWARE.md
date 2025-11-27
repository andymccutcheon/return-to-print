# Backend API → Hardware Agent Handoff

## 🎯 Backend API is Ready for Pi Integration!

The REST API is deployed and all printer endpoints have been tested. You can now implement the Raspberry Pi worker.

---

## API Gateway Base URL

```
https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
```

---

## Configuration for Pi Worker

Add this to your Python worker script:

```python
API_BASE = "https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod"
```

---

## Endpoints You Need

### 1. Get Next Message to Print (GET /printer/next-to-print)

**Usage**: Poll this endpoint every 5-10 seconds to check for new messages

```python
import requests

response = requests.get(f"{API_BASE}/printer/next-to-print")
data = response.json()

if data['message']:
    # Message available to print
    message_id = data['message']['id']
    content = data['message']['content']
    created_at = data['message']['created_at']
    print(f"Got message to print: {content}")
else:
    # No messages in queue
    print("No messages to print")
```

**Response (200) - Message Available:**
```json
{
  "message": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "Message text here",
    "created_at": "2025-11-24T03:53:48.980757Z",
    "printed": "false",
    "printed_at": null
  }
}
```

**Response (200) - No Messages:**
```json
{
  "message": null
}
```

---

### 2. Mark Message as Printed (POST /printer/mark-printed)

**Usage**: Call this after successfully printing the message

```python
import requests

response = requests.post(
    f"{API_BASE}/printer/mark-printed",
    json={'id': message_id}
)

if response.status_code == 200:
    print(f"Message {message_id} marked as printed")
else:
    print(f"Error marking as printed: {response.status_code}")
```

**Request:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "status": "ok",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Complete Worker Script Template

```python
#!/usr/bin/env python3
"""
Raspberry Pi printer worker for Return-to-Print
Polls API for messages and prints them to receipt printer
"""

import time
import requests
from escpos.printer import Usb  # python-escpos library

# Configuration
API_BASE = "https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod"
POLL_INTERVAL = 5  # seconds

# Printer USB IDs (get from lsusb)
VENDOR_ID = 0x1234   # Replace with your printer's vendor ID
PRODUCT_ID = 0x5678  # Replace with your printer's product ID


def get_next_message():
    """Fetch the next message to print from the API."""
    try:
        response = requests.get(f"{API_BASE}/printer/next-to-print", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('message')
    except requests.RequestException as e:
        print(f"Error fetching next message: {e}")
        return None


def mark_as_printed(message_id):
    """Mark a message as printed in the API."""
    try:
        response = requests.post(
            f"{API_BASE}/printer/mark-printed",
            json={'id': message_id},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Error marking message as printed: {e}")
        return False


def print_message(printer, content):
    """Print message content to the receipt printer."""
    try:
        printer.set(align='center', text_type='B')
        printer.text("--- NEW MESSAGE ---\n\n")
        
        printer.set(align='left', text_type='normal')
        printer.text(content + "\n\n")
        
        printer.set(align='center', text_type='A')
        printer.text("returntoprint.xyz\n")
        printer.text("-" * 32 + "\n\n")
        
        printer.cut()
        return True
    except Exception as e:
        print(f"Error printing: {e}")
        return False


def main():
    """Main worker loop."""
    print("Starting printer worker...")
    print(f"Polling API at: {API_BASE}")
    
    # Initialize printer
    try:
        printer = Usb(VENDOR_ID, PRODUCT_ID)
        print("Printer connected successfully")
    except Exception as e:
        print(f"Error connecting to printer: {e}")
        print("Make sure printer is connected via USB")
        return
    
    print("Entering polling loop...")
    
    while True:
        try:
            # Get next message
            message = get_next_message()
            
            if message:
                message_id = message['id']
                content = message['content']
                
                print(f"Printing message: {content[:50]}...")
                
                # Print the message
                if print_message(printer, content):
                    # Mark as printed
                    if mark_as_printed(message_id):
                        print(f"Message {message_id} printed successfully")
                    else:
                        print(f"Warning: Printed but failed to mark as printed")
                else:
                    print(f"Failed to print message {message_id}")
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nShutting down printer worker...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
```

---

## Polling Strategy

**Recommended**: Poll every 5-10 seconds
- Too frequent: Wastes Lambda invocations and API Gateway requests
- Too infrequent: Delays message printing

**Handling No Messages:**
When `message` is `null`, just wait and poll again. This is normal.

---

## Error Handling

### Network Errors
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.Timeout:
    print("Request timed out, will retry")
except requests.ConnectionError:
    print("Network error, check internet connection")
except requests.HTTPError as e:
    print(f"HTTP error: {e.response.status_code}")
```

### Printer Errors
If printing fails:
1. Log the error
2. **DO NOT** mark as printed
3. Message will be retried on next poll

### API Errors
If marking-printed fails:
1. Log the error
2. Message may be re-printed (idempotency is okay)
3. Consider retry logic with exponential backoff

---

## Testing the API

Test the printer endpoints directly:

```bash
# Get next message (should return null if empty)
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/next-to-print

# Create a test message (using frontend endpoint)
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/message \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message for Pi"}'

# Get next message (should now return the message)
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/next-to-print

# Mark as printed (use the ID from previous response)
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/mark-printed \
  -H "Content-Type: application/json" \
  -d '{"id":"YOUR-MESSAGE-ID"}'
```

---

## Dependencies

Install required Python packages on the Pi:

```bash
pip3 install requests python-escpos
```

---

## Running as a Service

Create systemd service file: `/etc/systemd/system/printer-worker.service`

```ini
[Unit]
Description=Return-to-Print Printer Worker
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/return-to-print/pi-worker
ExecStart=/usr/bin/python3 /home/pi/return-to-print/pi-worker/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable printer-worker
sudo systemctl start printer-worker
sudo systemctl status printer-worker
```

View logs:
```bash
sudo journalctl -u printer-worker -f
```

---

## What You DON'T Need

You do **NOT** need to use these endpoints (they're for the frontend):
- ❌ `POST /message` (frontend creates messages)
- ❌ `GET /messages/recent` (frontend displays messages)

---

## No Authentication Required

The API is currently public (no API key required). This may change in the future, but for now you can call endpoints directly.

---

## Message Queue Behavior

- **FIFO**: Messages are processed oldest-first
- **Once-only**: Once marked as printed, message won't appear again
- **Idempotent**: Marking as printed multiple times is safe
- **Efficient**: Uses DynamoDB GSI for fast queries (no table scans)

---

## Questions?

Check the comprehensive API documentation:
- `backend/README.md` - Full API documentation
- `backend/DEPLOYMENT_INFO.md` - Deployment details

---

**Status**: ✅ Ready for Pi Integration  
**Last Updated**: 2025-11-24

