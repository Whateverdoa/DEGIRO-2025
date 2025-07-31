#!/usr/bin/env python3
"""
Test script to verify degiro-connector API usage
"""

import os
import sys
sys.path.append('/Users/mike10h/PROJECTS/DEGIRO-2025')

from core.degiro_api import DeGiroAPIWrapper
from core.security import degiro_credentials

def test_degiro_connector_api():
    """Test the correct degiro-connector API methods"""
    try:
        # Get credentials
        creds = degiro_credentials.get_credentials()
        print(f"Credentials loaded: username={creds.get('username', 'N/A')}")
        print(f"Int account: {creds.get('int_account', 'N/A')}")
        
        # Create API wrapper
        api_wrapper = DeGiroAPIWrapper()
        
        # Connect to the API
        print("\nConnecting to DEGIRO API...")
        if not api_wrapper.connect():
            print("✗ Failed to connect to DEGIRO API")
            return
        
        print("✓ Successfully connected to DEGIRO API")
        
        # Check if the API object has the expected methods
        api_obj = api_wrapper.api
        print(f"\nAPI object type: {type(api_obj)}")
        print(f"API object methods: {[method for method in dir(api_obj) if not method.startswith('_')]}")
        
        # Try to find the correct method for portfolio data
        if hasattr(api_obj, 'get_update'):
            print("\n✓ Found get_update method")
            
            # Try to import UpdateRequest and UpdateOption
            try:
                from degiro_connector.trading.models.account import UpdateRequest, UpdateOption
                print("✓ Successfully imported UpdateRequest and UpdateOption")
                
                # Test portfolio request
                print("\nTesting portfolio data retrieval...")
                
                # Create update request for portfolio
                portfolio_request = UpdateRequest(
                    option=UpdateOption.PORTFOLIO,
                    last_updated=0
                )
                
                # Get portfolio data
                portfolio_response = api_obj.get_update(
                    request_list=[portfolio_request],
                    raw=True
                )
                
                print(f"Portfolio response type: {type(portfolio_response)}")
                print(f"Portfolio response keys: {portfolio_response.keys() if isinstance(portfolio_response, dict) else 'Not a dict'}")
                
                if isinstance(portfolio_response, dict) and 'portfolio' in portfolio_response:
                    portfolio_data = portfolio_response['portfolio']
                    print(f"Portfolio data type: {type(portfolio_data)}")
                    if isinstance(portfolio_data, dict) and 'value' in portfolio_data:
                        positions = portfolio_data['value']
                        print(f"Number of positions: {len(positions)}")
                        for i, position in enumerate(positions[:3]):  # Show first 3 positions
                            print(f"Position {i+1}: {position}")
                    else:
                        print(f"Portfolio data: {portfolio_data}")
                else:
                    print(f"Full response: {portfolio_response}")
                
                # Test total portfolio request
                print("\nTesting total portfolio data retrieval...")
                
                total_portfolio_request = UpdateRequest(
                    option=UpdateOption.TOTAL_PORTFOLIO,
                    last_updated=0
                )
                
                total_response = api_obj.get_update(
                    request_list=[total_portfolio_request],
                    raw=True
                )
                
                print(f"Total portfolio response: {total_response}")
                
            except ImportError as e:
                print(f"✗ Failed to import UpdateRequest/UpdateOption: {e}")
                
        else:
            print("✗ get_update method not found")
            
        # Check for other potential methods
        potential_methods = ['get_portfolio', 'get_portfolio_total', 'get_cash_funds']
        for method_name in potential_methods:
            if hasattr(api_obj, method_name):
                print(f"✓ Found {method_name} method")
            else:
                print(f"✗ {method_name} method not found")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_degiro_connector_api()