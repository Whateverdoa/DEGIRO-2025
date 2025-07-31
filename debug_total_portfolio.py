#!/usr/bin/env python3

import sys
sys.path.append('/Users/mike10h/PROJECTS/DEGIRO-2025')

from core.degiro_api import DeGiroAPIWrapper
from degiro_connector.trading.models.trading_pb2 import UpdateRequest, UpdateOption

def main():
    try:
        # Initialize the API wrapper
        api = DeGiroAPIWrapper()
        
        # Get raw update data
        update_request = UpdateRequest()
        update_request.option = UpdateOption.PORTFOLIO
        
        update = api.trading_api.get_update(request=update_request)
        
        if hasattr(update, 'values') and update.values:
            for account_update in update.values:
                print(f"\nAccount Update Keys: {list(account_update.keys())}")
                
                # Check if totalPortfolio exists
                if "totalPortfolio" in account_update:
                    print("\n=== TOTAL PORTFOLIO FOUND ===")
                    total_portfolio = account_update["totalPortfolio"]
                    print(f"Total Portfolio Type: {type(total_portfolio)}")
                    print(f"Total Portfolio Keys: {list(total_portfolio.keys()) if isinstance(total_portfolio, dict) else 'Not a dict'}")
                    print(f"Total Portfolio Raw: {total_portfolio}")
                else:
                    print("\n=== NO TOTAL PORTFOLIO FOUND ===")
                    print("Available keys:", list(account_update.keys()))
                    
                    # Check for any key containing 'total'
                    total_keys = [k for k in account_update.keys() if 'total' in k.lower()]
                    if total_keys:
                        print(f"Keys containing 'total': {total_keys}")
                        for key in total_keys:
                            print(f"\n{key}: {account_update[key]}")
                
                break  # Only process first account
        else:
            print("No update values found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()