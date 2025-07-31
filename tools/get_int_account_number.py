#!/usr/bin/env python3
"""
DeGiro Account Information Extractor
Extracts the int_account number required for portfolio operations.

Author: Clara Maintenance Engine
Date: 2025-01-31
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from degiro_connector.trading.api import API as TradingAPI
    from degiro_connector.trading.models.credentials import build_credentials
except ImportError as e:
    print(f"Error importing degiro_connector: {e}")
    print("Please ensure degiro-connector is installed: pip install degiro-connector")
    sys.exit(1)

def get_degiro_account_info():
    """
    Extract DeGiro account information including the critical int_account number.
    """
    # Load environment variables
    load_dotenv()
    
    username = os.getenv('DEGIRO_USERNAME')
    password = os.getenv('DEGIRO_PASSWORD')
    totp_secret = os.getenv('DEGIRO_TOTP_SECRET')
    
    if not username or not password:
        print("Error: DEGIRO_USERNAME and DEGIRO_PASSWORD must be set in .env file")
        return None
    
    try:
        print("Connecting to DeGiro...")
        
        # Build credentials with TOTP if available
        credentials_override = {
            'username': username,
            'password': password,
        }
        
        if totp_secret:
            credentials_override['totp_secret_key'] = totp_secret
            print("✓ Using TOTP secret for 2FA authentication")
        
        credentials = build_credentials(override=credentials_override)
        
        # Initialize API
        trading_api = TradingAPI(credentials=credentials)
        
        # Connect
        trading_api.connect()
        print("✓ Connection established")
        
        # Get client details
        print("Fetching client details...")
        client_details = trading_api.get_client_details()
        
        if client_details and 'data' in client_details:
            data = client_details['data']
            
            print("\n" + "="*50)
            print("DEGIRO ACCOUNT INFORMATION")
            print("="*50)
            
            # Extract key information
            int_account = data.get('intAccount')
            client_id = data.get('id')
            
            print(f"Client ID: {client_id}")
            print(f"Int Account: {int_account}")
            
            if int_account:
                print(f"\n✓ SUCCESS: int_account found: {int_account}")
                print("\nAdd this to your .env file:")
                print(f"DEGIRO_INT_ACCOUNT={int_account}")
                
                # Save to .env if not already present
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        env_content = f.read()
                    
                    if 'DEGIRO_INT_ACCOUNT' not in env_content:
                        with open(env_path, 'a') as f:
                            f.write(f"\nDEGIRO_INT_ACCOUNT={int_account}\n")
                        print(f"✓ Added DEGIRO_INT_ACCOUNT to .env file")
                    else:
                        print("ℹ DEGIRO_INT_ACCOUNT already exists in .env file")
                
                return {
                    'int_account': int_account,
                    'client_id': client_id,
                    'full_data': data
                }
            else:
                print("✗ ERROR: int_account not found in response")
                print("Full response data:")
                print(data)
                return None
        else:
            print("✗ ERROR: No data received from get_client_details()")
            print("Full response:")
            print(client_details)
            return None
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify credentials in .env file")
        print("2. Check if 2FA is enabled (may require additional setup)")
        print("3. Ensure account has API access permissions")
        return None
    
    finally:
        try:
            trading_api.logout()
            print("\n✓ Disconnected from DeGiro")
        except:
            pass

def main():
    """
    Main execution function.
    """
    print("DeGiro Account Information Extractor")
    print("Clara Maintenance Engine - Account Setup Tool")
    print("-" * 50)
    
    result = get_degiro_account_info()
    
    if result:
        print("\n" + "="*50)
        print("NEXT STEPS:")
        print("="*50)
        print("1. Verify the int_account was added to your .env file")
        print("2. Update your DeGiro API initialization to use int_account")
        print("3. Test portfolio access with the new configuration")
        print("4. Run portfolio_dashboard.py to verify data retrieval")
    else:
        print("\n" + "="*50)
        print("FAILED TO EXTRACT ACCOUNT INFO")
        print("="*50)
        print("Please check the error messages above and resolve issues.")

if __name__ == "__main__":
    main()