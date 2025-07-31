#!/usr/bin/env python3
"""
Debug script to examine the raw portfolio data structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.degiro_api import DeGiroAPIWrapper
import json

def debug_portfolio_data():
    """Debug the raw portfolio data structure."""
    print("Debugging portfolio data structure...")
    
    wrapper = DeGiroAPIWrapper()
    
    try:
        if wrapper.connect():
            print("✓ Connected successfully\n")
            
            # Import the required classes
            from degiro_connector.trading.models.account import UpdateRequest, UpdateOption
            
            # Get raw data for all portfolio-related requests
            portfolio_request = UpdateRequest(
                option=UpdateOption.PORTFOLIO,
                last_updated=0
            )
            
            total_portfolio_request = UpdateRequest(
                option=UpdateOption.TOTAL_PORTFOLIO,
                last_updated=0
            )
            
            cash_funds_request = UpdateRequest(
                option=UpdateOption.CASH_FUNDS,
                last_updated=0
            )
            
            # Get all data
            account_update = wrapper.api.get_update(
                request_list=[
                    portfolio_request,
                    total_portfolio_request,
                    cash_funds_request
                ],
                raw=True
            )
            
            print("Raw account update data:")
            print(json.dumps(account_update, indent=2, default=str))
            
            # Specifically examine totalPortfolio section
            if "totalPortfolio" in account_update:
                print("\n=== TOTAL PORTFOLIO SECTION ===")
                total_portfolio_data = account_update["totalPortfolio"]
                print(f"Type: {type(total_portfolio_data)}")
                print(f"Raw data: {total_portfolio_data}")
                
                if isinstance(total_portfolio_data, dict) and "value" in total_portfolio_data:
                    print("\nTotal Portfolio Values:")
                    for item in total_portfolio_data["value"]:
                        name = item.get("name", "Unknown")
                        value = item.get("value", 0)
                        print(f"  - {name}: {value}")
                else:
                    print("No 'value' key found in totalPortfolio data")
                        
            # Examine portfolio section
            if "portfolio" in account_update:
                print("\n=== PORTFOLIO SECTION ===")
                portfolio_data = account_update["portfolio"]
                print(f"Type: {type(portfolio_data)}")
                
                if isinstance(portfolio_data, dict) and "value" in portfolio_data:
                    positions = portfolio_data["value"]
                    print(f"Number of positions: {len(positions)}")
                    for i, position in enumerate(positions[:3]):  # Show first 3
                        print(f"  Position {i+1}: {position}")
                        
        else:
            print("✗ Failed to connect")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_portfolio_data()