# Return-to-Print Printer Worker

Complete deployment guide for setting up the Raspberry Pi thermal receipt printer worker.

## Table of Contents

- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation Guide](#detailed-installation-guide)
- [Configuration](#configuration)
- [Testing](#testing)
- [Service Management](#service-management)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)
- [Updating](#updating)
- [Architecture](#architecture)

---

## Overview

The Return-to-Print printer worker is a Python service that runs on a Raspberry Pi and continuously polls a backend API for messages to print. When a message is received, it prints it on a USB thermal receipt printer and marks it as printed in the backend.

### What It Does

1. **Polls** the API every 5 seconds for unprinted messages
2. **Prints** messages on a thermal receipt printer via USB
3. **Marks** messages as printed in the backend database
4. **Recovers** automatically from network failures and printer disconnects
5. **Runs** as a systemd service, auto-starting on boot

---

## Hardware Requirements

### Required Hardware

- **Raspberry Pi**: Any of the following models
  - Raspberry Pi 3B+ or newer
  - Raspberry Pi 4 (1GB+ RAM)
  - Raspberry Pi 5
  - Raspberry Pi Zero 2 W (WiFi model)
  
- **Thermal Receipt Printer**: 
  - Rongta RP326 (recommended)
  - Or any ESC/POS compatible USB thermal printer
  
- **Accessories**:
  - USB-A to USB-B cable (printer connection)
  - MicroSD card (16GB+, Class 10 recommended)
  - 5V power supply for Raspberry Pi
  - Power supply for printer (if required)

### Network Connection

- WiFi or Ethernet connection to the internet
- Must be able to reach: `https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com`

---

## Prerequisites

### 1. Raspberry Pi OS Installation

Install Raspberry Pi OS (32-bit or 64-bit) on your Pi:

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash Raspberry Pi OS Lite or Desktop to your microSD card
3. Enable SSH during setup (recommended)
4. Configure WiFi if using wireless

### 2. Initial Pi Setup

Boot your Pi and complete initial setup:

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Set timezone (optional but recommended)
sudo raspi-config
# Navigate to: Localisation Options > Timezone

# Verify internet connection
ping -c 4 google.com
```

### 3. SSH Access (Recommended)

For remote development and monitoring:

```bash
# On Pi, enable SSH if not already enabled
sudo systemctl enable ssh
sudo systemctl start ssh

# Find Pi's IP address
hostname -I

# From your computer, connect via SSH
ssh pi@<PI_IP_ADDRESS>
# Default password: raspberry (change this!)
```

---

## Quick Start

### Automated Installation (Recommended)

If you have the repository already, use the installation script:

```bash
# Clone repository (if not already cloned)
cd ~
git clone https://github.com/andymccutcheon/return-to-print.git
cd return-to-print/pi-worker

# Make install script executable
chmod +x install.sh

# Run installation
./install.sh
```

The script will:
- Install all dependencies
- Configure USB permissions
- Update worker.py with your printer's USB IDs
- Install the systemd service
- Provide next steps

**After installation completes**, test the printer and start the service:

```bash
# Test printer connection
python3 test_printer.py

# If test passes, enable and start service
sudo systemctl enable printer-worker
sudo systemctl start printer-worker

# Check status
sudo systemctl status printer-worker
```

---

## Detailed Installation Guide

### Step 1: Clone Repository

```bash
cd ~
git clone https://github.com/andymccutcheon/return-to-print.git
cd return-to-print/pi-worker
```

### Step 2: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip git
```

### Step 3: Install Python Dependencies

```bash
pip3 install --user -r requirements.txt
```

This installs:
- `python-escpos` - ESC/POS printer control library
- `requests` - HTTP client for API communication

### Step 4: Find Printer USB IDs

Connect your printer to the Pi via USB and run:

```bash
lsusb
```

**Example output:**
```
Bus 001 Device 004: ID 0fe6:811e ICS Advent USB Printer
                       ^^^^:^^^^
                    Vendor:Product
```

**Note these IDs** - you'll need them for configuration:
- Vendor ID: `0fe6`
- Product ID: `811e`

### Step 5: Configure USB Permissions

Create a udev rule to allow non-root access to the printer:

```bash
# Create udev rule file (replace VID and PID with your IDs)
sudo nano /etc/udev/rules.d/99-thermal-printer.rules
```

Add this line (update with YOUR vendor and product IDs):
```
SUBSYSTEM=="usb", ATTR{idVendor}=="0fe6", ATTR{idProduct}=="811e", MODE="0666"
```

Save (Ctrl+O, Enter) and exit (Ctrl+X), then reload:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Step 6: Configure Worker Script

Edit `worker.py` to add your printer's USB IDs:

```bash
nano worker.py
```

Find these lines near the top and update:
```python
VENDOR_ID = 0x0fe6   # Update with your Vendor ID
PRODUCT_ID = 0x811e  # Update with your Product ID
```

Save and exit.

### Step 7: Test Printer Connection

Before setting up the service, test that the printer works:

```bash
python3 test_printer.py
```

Enter your USB IDs when prompted. If successful, you'll see a test receipt print.

**If test fails**, see [Troubleshooting](#troubleshooting) section.

### Step 8: Install Systemd Service

```bash
# Copy service file to systemd directory
sudo cp printer-worker.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable printer-worker

# Start service
sudo systemctl start printer-worker

# Check status
sudo systemctl status printer-worker
```

### Step 9: Verify Operation

Check that the worker is running and polling the API:

```bash
# View live logs
sudo journalctl -u printer-worker -f
```

You should see logs like:
```
Return-to-Print Printer Worker Starting
API Base URL: https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
Printer connected successfully
Entering polling loop...
```

**Test end-to-end:**

1. Go to https://www.returntoprint.xyz (or use the frontend)
2. Submit a test message
3. Watch the logs - you should see the message being fetched and printed
4. Check the printer - a receipt should print with your message!

---

## Configuration

All configuration is in the top section of `worker.py`:

```python
# Backend API Configuration
API_BASE = "https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod"

# USB Printer Configuration
VENDOR_ID = 0x0fe6   # Your printer's USB Vendor ID
PRODUCT_ID = 0x811e  # Your printer's USB Product ID

# Polling Configuration
POLL_INTERVAL_SECONDS = 5        # How often to check for messages
REQUEST_TIMEOUT_SECONDS = 10     # HTTP request timeout
PRINTER_RECONNECT_DELAY = 30     # Retry delay for printer connection

# Logging Configuration
LOG_LEVEL = logging.INFO         # Change to logging.DEBUG for verbose output
LOG_FILE = '/var/log/printer-worker.log'  # Log file location
```

**After changing configuration:**
```bash
sudo systemctl restart printer-worker
```

---

## Testing

### Test Printer Connection

Use the included test script to verify USB connection:

```bash
python3 test_printer.py
```

Enter your printer's USB IDs when prompted. A successful test prints a receipt.

### Test API Connectivity

Manually test API endpoints:

```bash
# Check for messages (should return {"message": null} if queue is empty)
curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/next-to-print

# Submit a test message via frontend or API
curl -X POST https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/message \
  -H "Content-Type: application/json" \
  -d '{"content":"Test message from Pi"}'
```

### Test Worker Manually

Run the worker in foreground (useful for debugging):

```bash
# Stop the service first
sudo systemctl stop printer-worker

# Run worker manually
python3 worker.py
```

You'll see all logs in real-time. Press Ctrl+C to stop.

**Restart service after testing:**
```bash
sudo systemctl start printer-worker
```

---

## Service Management

### Common Commands

```bash
# Start service
sudo systemctl start printer-worker

# Stop service
sudo systemctl stop printer-worker

# Restart service
sudo systemctl restart printer-worker

# Check status
sudo systemctl status printer-worker

# Enable auto-start on boot
sudo systemctl enable printer-worker

# Disable auto-start
sudo systemctl disable printer-worker

# View recent logs
sudo journalctl -u printer-worker -n 100

# Follow logs in real-time
sudo journalctl -u printer-worker -f

# View logs since today
sudo journalctl -u printer-worker --since today

# View logs with errors only
sudo journalctl -u printer-worker -p err
```

---

## Monitoring & Logs

### Viewing Logs

The worker logs to systemd journal. View logs with:

```bash
# Recent logs
sudo journalctl -u printer-worker -n 50

# Live tail
sudo journalctl -u printer-worker -f

# Filter by time
sudo journalctl -u printer-worker --since "1 hour ago"
sudo journalctl -u printer-worker --since "2025-11-24 10:00"

# Show only errors
sudo journalctl -u printer-worker -p err
```

### Log Levels

- **INFO**: Normal operations (message received, printed, marked)
- **WARNING**: Recoverable errors (printer disconnect, network timeout)
- **ERROR**: Serious errors (API failures, print failures)
- **DEBUG**: Detailed debugging info (enable in worker.py)

### Health Check

Verify the worker is operating correctly:

```bash
# Check if service is running
sudo systemctl is-active printer-worker

# Check if service is enabled
sudo systemctl is-enabled printer-worker

# View full status
sudo systemctl status printer-worker

# Check printer USB connection
lsusb | grep -i printer
```

### Log File

Logs are also written to `/var/log/printer-worker.log` (if configured):

```bash
tail -f /var/log/printer-worker.log
```

---

## Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Printer not found** | `USBNotFoundError` in logs | 1. Check USB cable connection<br>2. Verify printer is powered on<br>3. Run `lsusb` to confirm USB IDs<br>4. Update worker.py with correct IDs |
| **Permission denied** | `PermissionError` accessing USB | 1. Check udev rules: `ls -l /etc/udev/rules.d/99-thermal-printer.rules`<br>2. Verify USB IDs in udev rule match printer<br>3. Reload udev: `sudo udevadm control --reload-rules`<br>4. Reconnect printer or reboot Pi |
| **Network errors** | `ConnectionError` in logs | 1. Check internet: `ping google.com`<br>2. Test API: `curl https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/next-to-print`<br>3. Check WiFi signal strength<br>4. Verify firewall isn't blocking HTTPS |
| **Service won't start** | `systemctl status` shows failed | 1. Check logs: `sudo journalctl -u printer-worker -n 50`<br>2. Verify worker.py has USB IDs configured<br>3. Test manually: `python3 worker.py`<br>4. Check file permissions |
| **No messages printing** | Service running but nothing prints | 1. Check if messages exist: `curl ...next-to-print`<br>2. Submit test message via frontend<br>3. Check logs for errors<br>4. Verify printer has paper<br>5. Test printer with test_printer.py |
| **Duplicate prints** | Message prints multiple times | 1. Normal if mark-printed API call fails<br>2. Check API logs<br>3. Verify backend is reachable<br>4. Check network stability |

### Diagnostic Commands

```bash
# Check system status
systemctl status printer-worker

# View error logs
sudo journalctl -u printer-worker -p err --since today

# Test printer manually
python3 test_printer.py

# List USB devices
lsusb

# Check USB permissions
ls -l /dev/bus/usb/001/*  # Adjust bus number from lsusb

# Test API connectivity
curl -v https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod/printer/next-to-print

# Check Python dependencies
pip3 list | grep -E "python-escpos|requests"

# Verify network
ping -c 4 google.com

# Check disk space
df -h

# Check memory
free -h
```

### Getting Help

1. **Check logs first**: Most issues are visible in logs
2. **Test components individually**: Printer, network, API
3. **Run worker manually**: See errors in real-time with `python3 worker.py`
4. **Review configuration**: Verify USB IDs and API URL are correct

### Debug Mode

Enable detailed logging:

1. Edit worker.py
2. Change `LOG_LEVEL = logging.DEBUG`
3. Restart service: `sudo systemctl restart printer-worker`
4. View verbose logs: `sudo journalctl -u printer-worker -f`

---

## Updating

### Update Worker Code

When code changes are pushed to the repository:

```bash
# Navigate to repository
cd ~/return-to-print

# Pull latest changes
git pull origin main

# Restart service to use new code
sudo systemctl restart printer-worker

# Check logs to verify
sudo journalctl -u printer-worker -f
```

### Update Python Dependencies

If requirements.txt changes:

```bash
cd ~/return-to-print/pi-worker
pip3 install --user --upgrade -r requirements.txt
sudo systemctl restart printer-worker
```

### Update Configuration

To change API URL, USB IDs, or polling interval:

```bash
# Edit worker.py
nano ~/return-to-print/pi-worker/worker.py

# Update configuration section at the top

# Restart service
sudo systemctl restart printer-worker
```

---

## Architecture

### How It Works

```
┌─────────────────┐
│   Frontend      │ User submits message
│ (Next.js App)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend API   │ Stores message in DynamoDB
│  (AWS Lambda)   │ marked as printed=false
└────────┬────────┘
         │
         │ (Poll every 5 seconds)
         │
┌────────▼────────┐
│  Pi Worker      │ 1. GET /printer/next-to-print
│  (This Script)  │ 2. Print message on thermal printer
└────────┬────────┘ 3. POST /printer/mark-printed
         │
         ▼
┌─────────────────┐
│ Thermal Printer │ Prints receipt
│  (USB Device)   │
└─────────────────┘
```

### Components

1. **worker.py**: Main polling loop and print logic
2. **test_printer.py**: USB connection testing utility
3. **printer-worker.service**: Systemd service configuration
4. **install.sh**: Automated installation script
5. **requirements.txt**: Python dependencies

### API Endpoints Used

- **GET /printer/next-to-print**
  - Returns oldest unprinted message or null
  - Response: `{"message": {...}}`

- **POST /printer/mark-printed**
  - Marks message as printed
  - Body: `{"id": "message-uuid"}`
  - Response: `{"status": "ok", "id": "..."}`

### Print Format

Each message prints as a thermal receipt:

```
================================
     PENNANT MESSAGE
================================

[Message content here]

--------------------------------
    returntoprint.xyz
--------------------------------

[Paper cut]
```

---

## Security Considerations

- **No Authentication**: API is currently public (no API key required)
- **USB Permissions**: udev rules allow user-level access to printer
- **Network**: Worker connects to public API over HTTPS
- **Service User**: Runs as `pi` user (non-root)
- **Logging**: Logs written to system journal and log file

---

## Performance

- **CPU Usage**: Minimal (<5% on Pi 3B+)
- **Memory**: ~50MB RSS
- **Network**: ~1KB per poll (5 seconds)
- **Print Time**: ~2-3 seconds per message
- **Latency**: 0-5 seconds from submission to print start

---

## Support

### Documentation

- **This README**: Complete deployment guide
- **Backend API Docs**: `backend/README.md` in repository
- **Frontend Docs**: `frontend/README.md` in repository

### Useful Links

- API Base: https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod
- Frontend: https://www.returntoprint.xyz
- Repository: https://github.com/andymccutcheon/return-to-print

---

## License

Part of the Return-to-Print project.

---

**Happy printing! 🖨️**

If you encounter issues not covered in this guide, check the logs first with `sudo journalctl -u printer-worker -f` and review the [Troubleshooting](#troubleshooting) section.

