#!/usr/bin/env python3
"""
Extract TOTP secret from DEGIRO QR code image.

WARNING: Only use this during initial 2FA setup. 
Save the QR code image when DEGIRO displays it.
"""

import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def extract_totp_from_text(qr_text: str) -> str:
    """Extract TOTP secret from otpauth URL."""
    # Example: otpauth://totp/DEGIRO:username?secret=ABCDEF123456&issuer=DEGIRO
    
    # Try URL parsing first
    try:
        parsed = urlparse(qr_text)
        if parsed.scheme == 'otpauth':
            params = parse_qs(parsed.query)
            if 'secret' in params:
                return params['secret'][0]
    except:
        pass
    
    # Fallback to regex
    match = re.search(r'secret=([A-Z2-7]+)', qr_text)
    if match:
        return match.group(1)
    
    return None


def extract_totp_from_image(image_path: str) -> str:
    """Extract TOTP secret from QR code image."""
    try:
        # Try with pyzbar if available
        from pyzbar import pyzbar
        from PIL import Image
        
        image = Image.open(image_path)
        qr_codes = pyzbar.decode(image)
        
        for qr_code in qr_codes:
            qr_data = qr_code.data.decode('utf-8')
            secret = extract_totp_from_text(qr_data)
            if secret:
                return secret
                
    except ImportError:
        print("pyzbar not installed. Install with: pip install pyzbar pillow")
        print("On macOS: brew install zbar")
        print("On Ubuntu: sudo apt-get install libzbar0")
        return None
    except Exception as e:
        print(f"Error reading QR code: {e}")
        return None
    
    return None


def main():
    """Main function."""
    print("DEGIRO TOTP Secret Extractor")
    print("="*50)
    print("WARNING: This tool violates DEGIRO's terms of service.")
    print("Use at your own risk of account termination.")
    print("="*50)
    print()
    
    if len(sys.argv) > 1:
        # Command line argument provided
        input_data = sys.argv[1]
    else:
        # Interactive mode
        print("Enter one of the following:")
        print("1. Path to QR code image file")
        print("2. The otpauth:// URL from the QR code")
        print("3. Just the TOTP secret (base32 string)")
        print()
        input_data = input("Input: ").strip()
    
    if not input_data:
        print("No input provided")
        return
    
    secret = None
    
    # Check if it's a file path
    if Path(input_data).exists():
        print(f"\nExtracting from image: {input_data}")
        secret = extract_totp_from_image(input_data)
    # Check if it's an otpauth URL
    elif input_data.startswith("otpauth://"):
        print("\nExtracting from otpauth URL")
        secret = extract_totp_from_text(input_data)
    # Assume it's the secret directly
    else:
        # Validate it looks like a base32 secret
        if re.match(r'^[A-Z2-7]+$', input_data.upper()):
            secret = input_data.upper()
        else:
            print("Invalid input format")
            return
    
    if secret:
        print(f"\n✓ TOTP Secret extracted: {secret}")
        print(f"\nAdd this to your .env file:")
        print(f"DEGIRO_TOTP_SECRET={secret}")
        
        # Test the secret
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            code = totp.now()
            print(f"\nCurrent TOTP code: {code}")
            print(f"(Valid for ~{30 - (pyotp.TOTP(secret).interval - pyotp.TOTP(secret).now())} seconds)")
        except Exception as e:
            print(f"\nWarning: Could not generate test code: {e}")
    else:
        print("\n✗ Failed to extract TOTP secret")
        print("\nTips:")
        print("- Save the QR code image when DEGIRO shows it during 2FA setup")
        print("- Make sure the image is clear and not cropped")
        print("- Install required dependencies: pip install pyzbar pillow pyotp")


if __name__ == "__main__":
    main()