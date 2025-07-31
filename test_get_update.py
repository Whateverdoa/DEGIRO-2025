#!/usr/bin/env python3
"""
Test get_update method directly
"""

import os
import sys
sys.path.append('/Users/mike10h/PROJECTS/DEGIRO-2025')

from core.degiro_api import DeGiroAPIWrapper
import inspect

def test_get_update():
    """Test the get_update method"""
    try:
        # Create and connect API wrapper
        api_wrapper = DeGiroAPIWrapper()
        
        print("Connecting to DEGIRO API...")
        if not api_wrapper.connect():
            print("✗ Failed to connect to DEGIRO API")
            return
        
        print("✓ Successfully connected to DEGIRO API")
        
        # Get the API object
        api_obj = api_wrapper.api
        
        # Check get_update method signature
        if hasattr(api_obj, 'get_update'):
            print(f"\nget_update method signature: {inspect.signature(api_obj.get_update)}")
            
            # Try calling get_update with minimal parameters
            print("\nTrying get_update with empty request_list...")
            try:
                result = api_obj.get_update(request_list=[])
                print(f"Empty request result: {result}")
            except Exception as e:
                print(f"Empty request failed: {e}")
            
            # Try calling get_update with raw=True
            print("\nTrying get_update with raw=True...")
            try:
                result = api_obj.get_update(request_list=[], raw=True)
                print(f"Raw request result: {result}")
            except Exception as e:
                print(f"Raw request failed: {e}")
                
            # Try to find what request objects are available
            print("\nLooking for request/option classes...")
            try:
                # Try different import paths
                import_paths = [
                    'degiro_connector.trading.models.update_request',
                    'degiro_connector.trading.models.update_option',
                    'degiro_connector.trading.models',
                    'degiro_connector.trading.pb.update_pb2',
                    'degiro_connector.trading.pb',
                    'degiro_connector.trading.models.trading_pb2',
                ]
                
                for path in import_paths:
                    try:
                        module = __import__(path, fromlist=[''])
                        print(f"✓ Found module: {path}")
                        print(f"  Contents: {[item for item in dir(module) if not item.startswith('_')]}")
                    except ImportError:
                        print(f"✗ Module not found: {path}")
                        
            except Exception as e:
                print(f"Error exploring modules: {e}")
                
        else:
            print("✗ get_update method not found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_update()