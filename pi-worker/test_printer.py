#!/usr/bin/env python3
"""
Test script for USB thermal printer connection.
Use this to verify your printer is connected and find the correct USB IDs.

Run: python3 test_printer.py
"""

import sys

try:
    from escpos.printer import Usb
    from escpos.exceptions import USBNotFoundError
except ImportError:
    print("ERROR: python-escpos not installed!")
    print("Install it with: pip3 install python-escpos")
    sys.exit(1)


def test_printer():
    """Test USB printer connection and print a test receipt."""
    print("=" * 60)
    print("Thermal Printer USB Connection Test")
    print("=" * 60)
    print()
    print("First, find your printer's USB IDs by running:")
    print("  lsusb")
    print()
    print("Look for your printer in the output. Example:")
    print("  Bus 001 Device 004: ID 0fe6:811e ICS Advent USB Printer")
    print("                         ^^^^:^^^^")
    print("                      Vendor:Product")
    print()
    print("-" * 60)
    print()
    
    # Get vendor ID
    vendor_input = input("Enter Vendor ID (e.g., 0fe6): ").strip()
    if not vendor_input:
        print("ERROR: Vendor ID required")
        sys.exit(1)
    
    # Get product ID
    product_input = input("Enter Product ID (e.g., 811e): ").strip()
    if not product_input:
        print("ERROR: Product ID required")
        sys.exit(1)
    
    # Convert hex strings to integers
    try:
        vendor_id = int(vendor_input, 16)
        product_id = int(product_input, 16)
    except ValueError:
        print("ERROR: Invalid hex format. Use format like: 0fe6")
        sys.exit(1)
    
    print()
    print(f"Attempting to connect to printer...")
    print(f"  Vendor ID:  0x{vendor_id:04x}")
    print(f"  Product ID: 0x{product_id:04x}")
    print()
    
    # Try to connect to printer
    try:
        printer = Usb(vendor_id, product_id)
        print("✓ SUCCESS: Printer connected!")
        print()
        
        # Print test receipt
        print("Printing test receipt...")
        printer.set(align='center', font='a', width=1, height=1)
        printer.text("=" * 32 + "\n")
        printer.text("TEST PRINT\n")
        printer.text("=" * 32 + "\n\n")
        
        printer.set(align='left', font='b', width=1, height=1)
        printer.text("If you can read this, your\n")
        printer.text("printer is working correctly!\n\n")
        
        printer.set(align='center', font='a', width=1, height=1)
        printer.text("-" * 32 + "\n")
        printer.text("returntoprint.xyz\n")
        printer.text("-" * 32 + "\n\n\n")
        
        printer.cut()
        
        print("✓ Test receipt printed successfully!")
        print()
        print("Next steps:")
        print(f"  1. Update worker.py with these IDs:")
        print(f"     VENDOR_ID = 0x{vendor_id:04x}")
        print(f"     PRODUCT_ID = 0x{product_id:04x}")
        print()
        print("  2. Set up USB permissions (if not root):")
        print("     See README.md for udev rules setup")
        print()
        
    except USBNotFoundError:
        print("✗ ERROR: Printer not found!")
        print()
        print("Troubleshooting:")
        print("  1. Check USB cable is connected")
        print("  2. Check printer is powered on")
        print("  3. Verify USB IDs with 'lsusb'")
        print("  4. Try running with sudo: sudo python3 test_printer.py")
        print()
        sys.exit(1)
    
    except PermissionError:
        print("✗ ERROR: Permission denied!")
        print()
        print("This usually means USB permissions are not set up.")
        print("Options:")
        print("  1. Run with sudo: sudo python3 test_printer.py")
        print("  2. Set up udev rules (see README.md)")
        print()
        sys.exit(1)
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print()
        print("Check that:")
        print("  - Printer is USB-connected and powered on")
        print("  - python-escpos is installed correctly")
        print("  - You're using the correct USB IDs")
        print()
        sys.exit(1)


if __name__ == '__main__':
    test_printer()

