#!/usr/bin/env python3
"""
Debug script to investigate product info structure from DEGIRO API
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.degiro_api import DeGiroAPIWrapper
from core.logging_config import setup_logging

# Load environment variables
load_dotenv('.env.dev')

# Setup logging
logger = setup_logging()

def debug_product_info():
    """Debug product info retrieval"""
    
    # Initialize API wrapper
    api = DeGiroAPIWrapper()
    
    try:
        # Connect to API
        print("Connecting to DEGIRO API...")
        if not api.connect():
            print("❌ Failed to connect")
            return
        
        print("✓ Connected successfully\n")
        
        # Get portfolio data first to get position IDs
        from degiro_connector.trading.models.account import UpdateRequest, UpdateOption
        
        portfolio_request = UpdateRequest(
            option=UpdateOption.PORTFOLIO,
            last_updated=0
        )
        
        account_update = api.api.get_update(
            request_list=[portfolio_request],
            raw=True
        )
        
        print("=== EXTRACTING POSITION IDs ===")
        position_ids = []
        
        if account_update and "portfolio" in account_update:
            portfolio_data = account_update["portfolio"]
            if isinstance(portfolio_data, dict) and "value" in portfolio_data:
                for item in portfolio_data["value"]:
                    if item.get('name') == 'positionrow':
                        position_id = item.get('id', '')
                        if position_id:
                            position_ids.append(position_id)
                            print(f"Found position ID: {position_id}")
        
        if not position_ids:
            print("No position IDs found")
            return
        
        print(f"\n=== TESTING PRODUCT INFO FOR {len(position_ids)} POSITIONS ===")
        
        for pos_id in position_ids:
            print(f"\n--- Position ID: {pos_id} ---")
            
            try:
                # Test get_products_info
                product_info = api.api.get_products_info(product_list=[pos_id])
                
                print(f"Product info type: {type(product_info)}")
                print(f"Product info: {product_info}")
                
                # Check if it has data attribute
                if hasattr(product_info, 'data'):
                    print(f"Has 'data' attribute: {product_info.data}")
                    if pos_id in product_info.data:
                        product_data = product_info.data[pos_id]
                        print(f"Product data type: {type(product_data)}")
                        print(f"Product data: {product_data}")
                        
                        # Try to get symbol and name
                        if hasattr(product_data, 'symbol'):
                            print(f"Symbol: {product_data.symbol}")
                        if hasattr(product_data, 'name'):
                            print(f"Name: {product_data.name}")
                        
                        # List all attributes
                        print(f"All attributes: {dir(product_data)}")
                
                # Check if it's a dictionary
                elif isinstance(product_info, dict):
                    print(f"Is dictionary with keys: {list(product_info.keys())}")
                    if pos_id in product_info:
                        product_data = product_info[pos_id]
                        print(f"Product data: {product_data}")
                        if isinstance(product_data, dict):
                            print(f"Symbol: {product_data.get('symbol', 'Not found')}")
                            print(f"Name: {product_data.get('name', 'Not found')}")
                
            except Exception as e:
                print(f"Error getting product info for {pos_id}: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        api.disconnect()

if __name__ == "__main__":
    debug_product_info()