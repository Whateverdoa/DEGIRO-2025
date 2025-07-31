#!/usr/bin/env python3
"""
Test script to verify the updated get_portfolio method in DeGiroAPIWrapper.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.degiro_api import DeGiroAPIWrapper
import json

def test_portfolio_method():
    """Test the updated get_portfolio method."""
    print("Testing DeGiroAPIWrapper.get_portfolio() method...")
    
    # Initialize the wrapper
    wrapper = DeGiroAPIWrapper()
    
    try:
        # Connect to the API
        print("Connecting to DEGIRO API...")
        if wrapper.connect():
            print("✓ Connected successfully")
            
            # Test the get_portfolio method
            print("\nTesting get_portfolio method...")
            portfolio_data = wrapper.get_portfolio()
            
            print("✓ get_portfolio method executed successfully")
            print(f"\nPortfolio data structure:")
            print(f"- Positions: {len(portfolio_data.get('positions', []))}")
            print(f"- Total value: €{portfolio_data.get('total_value', 0):.2f}")
            print(f"- Cash balance: €{portfolio_data.get('cash_balance', 0):.2f}")
            print(f"- Invested amount: €{portfolio_data.get('invested_amount', 0):.2f}")
            print(f"- Unrealized P&L: €{portfolio_data.get('unrealized_pnl', 0):.2f}")
            print(f"- Timestamp: {portfolio_data.get('timestamp', 'N/A')}")
            
            # Show first few positions if any
            positions = portfolio_data.get('positions', [])
            if positions:
                print(f"\nFirst few positions:")
                for i, position in enumerate(positions[:3]):
                    print(f"  {i+1}. {position.get('symbol', 'Unknown')} - {position.get('size', 0)} shares @ €{position.get('price', 0):.2f}")
            else:
                print("\nNo positions found in portfolio")
                
        else:
            print("✗ Failed to connect to DEGIRO API")
            
    except Exception as e:
        print(f"✗ Error testing portfolio method: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_portfolio_method()