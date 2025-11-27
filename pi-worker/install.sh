#!/bin/bash
#
# Return-to-Print Printer Worker Installation Script
# 
# This script automates the installation and setup of the printer worker
# on a Raspberry Pi running Raspberry Pi OS (Debian-based).
#
# Usage: 
#   chmod +x install.sh
#   ./install.sh
#
# What it does:
# 1. Updates system packages
# 2. Installs Python3 and pip
# 3. Installs Python dependencies
# 4. Sets up USB permissions
# 5. Installs systemd service
# 6. Provides next steps
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Return-to-Print Worker Installer${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if running on Raspberry Pi OS
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}ERROR: Could not detect OS${NC}"
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "raspbian" ]] && [[ "$ID" != "debian" ]]; then
    echo -e "${YELLOW}WARNING: This script is designed for Raspberry Pi OS (Debian)${NC}"
    echo -e "${YELLOW}You are running: $PRETTY_NAME${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for sudo/root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}ERROR: Do not run this script as root or with sudo${NC}"
    echo "It will prompt for sudo when needed"
    exit 1
fi

echo -e "${GREEN}✓ OS check passed${NC}"
echo ""

# Step 1: Update system
echo -e "${BLUE}[1/6] Updating system packages...${NC}"
sudo apt update
echo -e "${GREEN}✓ System packages updated${NC}"
echo ""

# Step 2: Install Python3 and pip
echo -e "${BLUE}[2/6] Installing Python3 and pip...${NC}"
sudo apt install -y python3 python3-pip python3-venv git
echo -e "${GREEN}✓ Python3 and pip installed${NC}"
echo ""

# Step 3: Install Python dependencies
echo -e "${BLUE}[3/6] Installing Python dependencies...${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install --user --break-system-packages -r "$SCRIPT_DIR/requirements.txt"
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${RED}ERROR: requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Step 4: Configure USB permissions
echo -e "${BLUE}[4/6] Configuring USB permissions...${NC}"
echo ""
echo -e "${YELLOW}To configure USB permissions, we need your printer's USB IDs.${NC}"
echo "Run 'lsusb' to find your printer. Example output:"
echo "  Bus 001 Device 004: ID 0fe6:811e ICS Advent USB Printer"
echo "                         ^^^^:^^^^"
echo "                      Vendor:Product"
echo ""

# Run lsusb to show devices
echo "Connected USB devices:"
lsusb
echo ""

read -p "Enter Vendor ID (e.g., 0fe6): " VENDOR_ID
read -p "Enter Product ID (e.g., 811e): " PRODUCT_ID

if [ -z "$VENDOR_ID" ] || [ -z "$PRODUCT_ID" ]; then
    echo -e "${RED}ERROR: Both Vendor ID and Product ID are required${NC}"
    exit 1
fi

# Create udev rule
UDEV_RULE="SUBSYSTEM==\"usb\", ATTR{idVendor}==\"$VENDOR_ID\", ATTR{idProduct}==\"$PRODUCT_ID\", MODE=\"0666\""
UDEV_FILE="/etc/udev/rules.d/99-thermal-printer.rules"

echo "Creating udev rule: $UDEV_RULE"
echo "$UDEV_RULE" | sudo tee "$UDEV_FILE" > /dev/null

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo -e "${GREEN}✓ USB permissions configured${NC}"
echo ""

# Step 5: Update worker.py with USB IDs
echo -e "${BLUE}[5/6] Updating worker.py with USB IDs...${NC}"
WORKER_FILE="$SCRIPT_DIR/worker.py"

if [ -f "$WORKER_FILE" ]; then
    # Convert hex to 0x format for Python
    sed -i "s/VENDOR_ID = 0x0000/VENDOR_ID = 0x$VENDOR_ID/" "$WORKER_FILE"
    sed -i "s/PRODUCT_ID = 0x0000/PRODUCT_ID = 0x$PRODUCT_ID/" "$WORKER_FILE"
    echo -e "${GREEN}✓ worker.py updated with USB IDs${NC}"
else
    echo -e "${RED}ERROR: worker.py not found${NC}"
    exit 1
fi
echo ""

# Step 6: Install systemd service
echo -e "${BLUE}[6/6] Installing systemd service...${NC}"

SERVICE_FILE="$SCRIPT_DIR/printer-worker.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}ERROR: printer-worker.service not found${NC}"
    exit 1
fi

# Update service file with actual paths
TEMP_SERVICE="/tmp/printer-worker.service"
sed "s|/home/pi/return-to-print/pi-worker|$SCRIPT_DIR|g" "$SERVICE_FILE" > "$TEMP_SERVICE"

# Install service
sudo cp "$TEMP_SERVICE" /etc/systemd/system/printer-worker.service
sudo systemctl daemon-reload

echo -e "${GREEN}✓ Systemd service installed${NC}"
echo ""

# Installation complete
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Test the printer connection:"
echo "   ${YELLOW}python3 $SCRIPT_DIR/test_printer.py${NC}"
echo ""
echo "2. If test successful, enable and start the service:"
echo "   ${YELLOW}sudo systemctl enable printer-worker${NC}"
echo "   ${YELLOW}sudo systemctl start printer-worker${NC}"
echo ""
echo "3. Check service status:"
echo "   ${YELLOW}sudo systemctl status printer-worker${NC}"
echo ""
echo "4. View logs:"
echo "   ${YELLOW}sudo journalctl -u printer-worker -f${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Vendor ID:  0x$VENDOR_ID"
echo "  Product ID: 0x$PRODUCT_ID"
echo "  Worker:     $SCRIPT_DIR/worker.py"
echo "  Service:    /etc/systemd/system/printer-worker.service"
echo ""
echo -e "${GREEN}Happy printing! 🖨️${NC}"

