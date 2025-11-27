#!/usr/bin/env python3
"""
Return-to-Print Printer Worker
Polls backend API for messages and prints them on thermal receipt printer.

This worker runs continuously, polling the API every 5 seconds for new messages.
When a message is found, it prints it on the thermal printer and marks it as printed.

Hardware Requirements:
- Raspberry Pi (3B+, 4, 5, or Zero 2 W)
- USB thermal receipt printer (Rongta RP326 or compatible)
- USB cable connecting printer to Pi
- Internet connection (WiFi or Ethernet)

Author: Hardware Agent for Return-to-Print Project
"""

import time
import logging
import sys
import signal
from typing import Optional, Dict, Any
import requests
from escpos.printer import Usb
from escpos.exceptions import USBNotFoundError, Error as EscposError

# ============================================================================
# CONFIGURATION - Update these values for your setup
# ============================================================================

# Backend API Configuration
API_BASE = "https://y0i7a9r7q3.execute-api.us-west-2.amazonaws.com/prod"

# USB Printer Configuration
# Find these values by running: lsusb
# Example output: Bus 001 Device 004: ID 0fe6:811e
# Where 0fe6 is VENDOR_ID and 811e is PRODUCT_ID
VENDOR_ID = 0x0000   # UPDATE THIS: Your printer's USB Vendor ID
PRODUCT_ID = 0x0000  # UPDATE THIS: Your printer's USB Product ID

# Polling Configuration
POLL_INTERVAL_SECONDS = 5        # How often to check for new messages
REQUEST_TIMEOUT_SECONDS = 10     # HTTP request timeout
PRINTER_RECONNECT_DELAY = 30     # Seconds to wait before retrying printer connection

# Logging Configuration
LOG_LEVEL = logging.INFO         # Change to logging.DEBUG for verbose output
LOG_FILE = '/var/log/printer-worker.log'  # System log file

# ============================================================================
# LOGGING SETUP
# ============================================================================

# Configure logging to both stdout (for systemd journalctl) and file
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='a') if LOG_FILE else logging.NullHandler()
    ]
)
logger = logging.getLogger('printer-worker')


# ============================================================================
# PRINTER WORKER CLASS
# ============================================================================

class PrinterWorker:
    """
    Main worker class for polling API and printing messages.
    
    This class handles:
    - Connecting to USB thermal printer
    - Polling API for new messages
    - Printing messages with proper formatting
    - Marking messages as printed in the backend
    - Error recovery and reconnection logic
    """
    
    def __init__(self, api_base: str, vendor_id: int, product_id: int):
        """
        Initialize the printer worker.
        
        Args:
            api_base: Base URL for the backend API
            vendor_id: USB Vendor ID of the printer (hex)
            product_id: USB Product ID of the printer (hex)
        """
        self.api_base = api_base
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.printer = None
        self.running = True
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False
    
    def connect_printer(self) -> bool:
        """
        Attempt to connect to USB thermal printer.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.printer = Usb(self.vendor_id, self.product_id)
            logger.info(
                f"Printer connected successfully "
                f"(VID: {hex(self.vendor_id)}, PID: {hex(self.product_id)})"
            )
            return True
        
        except USBNotFoundError:
            logger.error(
                f"Printer not found - check USB connection and power "
                f"(VID: {hex(self.vendor_id)}, PID: {hex(self.product_id)})"
            )
            self.printer = None
            return False
        
        except PermissionError:
            logger.error(
                "Permission denied accessing USB printer. "
                "Make sure udev rules are configured correctly."
            )
            self.printer = None
            return False
        
        except Exception as e:
            logger.error(f"Failed to connect to printer: {e}", exc_info=True)
            self.printer = None
            return False
    
    def get_next_message(self) -> Optional[Dict[str, Any]]:
        """
        Fetch next unprinted message from API.
        
        Returns:
            dict: Message object with id, content, created_at, printed fields
            None: If no messages available or request failed
        """
        try:
            response = requests.get(
                f"{self.api_base}/printer/next-to-print",
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
            
            message = data.get('message')
            if message:
                logger.debug(f"Retrieved message {message['id']} from API")
            else:
                logger.debug("No messages available to print")
            
            return message
        
        except requests.exceptions.Timeout:
            logger.warning("API request timed out - network may be slow")
            return None
        
        except requests.exceptions.ConnectionError:
            logger.warning("Failed to connect to API - check internet connection")
            return None
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e.response.status_code} - {e}")
            return None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch next message: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error fetching message: {e}", exc_info=True)
            return None
    
    def print_message(self, message_data: dict) -> bool:
        """
        Print message content on thermal receipt printer.
        
        Formats the message with:
        - Header with RECEIPT ME branding
        - To: field
        - Message ID
        - Date/time
        - From: field
        - Message content (bigger font)
        - Footer with domain
        - Paper cut at the end
        
        Args:
            message_data: Dictionary with keys: content, name, created_at, message_number
        
        Returns:
            bool: True if print successful, False otherwise
        """
        if not self.printer:
            logger.error("Cannot print - printer not connected")
            return False
        
        try:
            from datetime import datetime
            
            # Extract message data
            content = message_data.get('content', '')
            sender_name = message_data.get('name', 'Anonymous')
            created_at = message_data.get('created_at', '')
            message_number = int(message_data.get('message_number', 0))  # Convert to int
            
            # Parse timestamp and convert to Mountain Time (MST/MDT)
            try:
                from datetime import timezone, timedelta
                
                # Parse UTC timestamp
                dt_utc = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                # Convert to Mountain Time (UTC-7)
                # Note: This doesn't handle DST automatically. For proper DST handling, use pytz
                mountain_offset = timedelta(hours=-7)
                dt_mountain = dt_utc.astimezone(timezone(mountain_offset))
                
                date_str = dt_mountain.strftime('%m/%d/%Y')
                time_str = dt_mountain.strftime('%I:%M %p MST')
            except:
                date_str = "N/A"
                time_str = "N/A"
            
            # Format message number as 3-digit (001, 002, etc.)
            msg_id = f"{message_number:03d}"
            
            # Print header - RECEIPT ME in EXTRA large bold
            self.printer.set(align='center', font='a', width=4, height=4, bold=True)
            self.printer.text("RECEIPT\n")
            self.printer.text("ME\n\n")
            self.printer.set(align='center', font='a', width=1, height=1, bold=False)
            self.printer.text("=" * 48 + "\n\n")
            
            # Print To: field (normal size)
            self.printer.set(align='left', font='a', width=1, height=1, bold=True)
            self.printer.text("TO: ")
            self.printer.set(bold=False)
            self.printer.text("Andy, Annie, Newt & Harold\n\n")
            
            # Print Message ID (normal size)
            self.printer.set(bold=True)
            self.printer.text("MSG: ")
            self.printer.set(bold=False)
            self.printer.text(f"#{msg_id}\n\n")
            
            # Print Date/Time (normal size)
            self.printer.set(bold=True)
            self.printer.text("DATE: ")
            self.printer.set(bold=False)
            self.printer.text(f"{date_str}\n")
            self.printer.set(bold=True)
            self.printer.text("TIME: ")
            self.printer.set(bold=False)
            self.printer.text(f"{time_str}\n\n")
            
            # Print From: field (normal size)
            self.printer.set(bold=True)
            self.printer.text("FROM: ")
            self.printer.set(bold=False)
            self.printer.text(f"{sender_name}\n\n")
            
            # Separator
            self.printer.set(align='center')
            self.printer.text("-" * 48 + "\n\n")
            
            # Print message content (BIGGER FONT - stands out from metadata)
            self.printer.set(align='left', font='a', width=3, height=3, bold=False)
            self.printer.text(content + "\n\n")
            
            # Print footer
            self.printer.set(align='center', font='a', width=1, height=1)
            self.printer.text("-" * 48 + "\n")
            self.printer.text("receiptme.xyz\n")
            self.printer.text("-" * 48 + "\n\n\n")
            
            # Cut paper
            self.printer.cut()
            
            logger.info(f"Message #{msg_id} printed successfully")
            return True
        
        except USBNotFoundError:
            logger.error("Printer disconnected during print operation")
            self.printer = None  # Force reconnection
            return False
        
        except EscposError as e:
            logger.error(f"Printer error: {e}")
            return False
        
        except Exception as e:
            logger.error(f"Failed to print message: {e}", exc_info=True)
            return False
    
    def mark_as_printed(self, message_id: str) -> bool:
        """
        Mark message as printed via API.
        
        Args:
            message_id: UUID of the message to mark as printed
        
        Returns:
            bool: True if successfully marked, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_base}/printer/mark-printed",
                json={"id": message_id},
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            logger.info(f"Message {message_id} marked as printed")
            return True
        
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout marking message {message_id} as printed")
            return False
        
        except requests.exceptions.ConnectionError:
            logger.warning(f"Network error marking message {message_id} as printed")
            return False
        
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"API error marking message as printed: "
                f"{e.response.status_code} - {e}"
            )
            return False
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to mark message as printed: {e}")
            return False
        
        except Exception as e:
            logger.error(
                f"Unexpected error marking message as printed: {e}",
                exc_info=True
            )
            return False
    
    def run(self):
        """
        Main worker loop.
        
        Continuously polls the API for new messages, prints them,
        and marks them as printed. Handles all error conditions
        gracefully and attempts automatic recovery.
        
        Loop behavior:
        1. Check if printer is connected, reconnect if needed
        2. Poll API for next unprinted message
        3. If message found, print it
        4. If print successful, mark as printed in API
        5. Wait POLL_INTERVAL_SECONDS before next iteration
        6. Repeat until shutdown signal received
        """
        logger.info("=" * 60)
        logger.info("Return-to-Print Printer Worker Starting")
        logger.info("=" * 60)
        logger.info(f"API Base URL: {self.api_base}")
        logger.info(f"Printer VID:PID: {hex(self.vendor_id)}:{hex(self.product_id)}")
        logger.info(f"Poll Interval: {POLL_INTERVAL_SECONDS} seconds")
        logger.info("=" * 60)
        
        # Validate configuration
        if self.vendor_id == 0x0000 or self.product_id == 0x0000:
            logger.error(
                "ERROR: Printer USB IDs not configured! "
                "Update VENDOR_ID and PRODUCT_ID in worker.py"
            )
            logger.error("Run 'lsusb' to find your printer's USB IDs")
            logger.error("Then update the configuration section at the top of worker.py")
            return
        
        while self.running:
            try:
                # Ensure printer is connected
                if not self.printer:
                    logger.info("Attempting to connect to printer...")
                    if not self.connect_printer():
                        logger.warning(
                            f"Printer not available, retrying in "
                            f"{PRINTER_RECONNECT_DELAY} seconds..."
                        )
                        time.sleep(PRINTER_RECONNECT_DELAY)
                        continue
                
                # Get next message from API
                message = self.get_next_message()
                if not message:
                    # No messages to print, wait and try again
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue
                
                # Extract message details
                message_id = message['id']
                content = message['content']
                sender_name = message.get('name', 'Anonymous')
                created_at = message.get('created_at', 'unknown')
                message_number = int(message.get('message_number', 0))  # Convert to int
                
                # Log message details (truncate long messages in log)
                content_preview = content[:50] + "..." if len(content) > 50 else content
                logger.info(
                    f"Processing message #{message_number:03d} from {sender_name} "
                    f"(created: {created_at})"
                )
                logger.info(f"Content: {content_preview}")
                
                # Print the message
                if self.print_message(message):
                    # Successfully printed, now mark as printed in backend
                    if self.mark_as_printed(message_id):
                        logger.info(f"✓ Message {message_id[:8]}... completed successfully")
                    else:
                        logger.warning(
                            f"⚠ Message {message_id[:8]}... printed but failed to "
                            f"mark as printed - may be reprinted"
                        )
                else:
                    logger.error(
                        f"✗ Failed to print message {message_id[:8]}... "
                        f"- will retry on next poll"
                    )
                    # Don't mark as printed, will retry
                
                # Brief pause between messages
                time.sleep(2)
            
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                self.running = False
            
            except Exception as e:
                logger.error(
                    f"Unexpected error in main loop: {e}",
                    exc_info=True
                )
                # Wait before retrying to avoid tight error loop
                time.sleep(POLL_INTERVAL_SECONDS)
        
        # Cleanup
        logger.info("Shutting down gracefully...")
        if self.printer:
            try:
                self.printer.close()
                logger.info("Printer connection closed")
            except Exception as e:
                logger.warning(f"Error closing printer: {e}")
        
        logger.info("Printer worker stopped")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the worker script."""
    try:
        worker = PrinterWorker(API_BASE, VENDOR_ID, PRODUCT_ID)
        worker.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

