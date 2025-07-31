# DEGIRO API Documentation

## Overview
This project uses the `degiro-connector` library (v3.0.29) to interact with DEGIRO's trading platform.

## Installation
```bash
pip install degiro-connector==3.0.29
```

## Authentication

### Basic Setup
```python
from degiro_connector.trading.api import API as TradingAPI
from degiro_connector.trading.models.credentials import build_credentials

# Option 1: Using config file
credentials = build_credentials(
    location="config/config.json"
)

# Option 2: Using environment variables with override
credentials = build_credentials(
    location="config/config.json",
    override={
        "username": "YOUR_USERNAME",
        "password": "YOUR_PASSWORD",
        "int_account": 12345678,  # Get from get_client_details()
        "totp_secret_key": "YOUR_TOTP_SECRET",  # For 2FA
    }
)

# Create API instance and connect
trading_api = TradingAPI(credentials=credentials)
trading_api.connect()
```

## Available Methods

### Account Information
- `get_client_details()` - Get client account details
- `get_account_info()` - Get account information
- `get_config()` - Get configuration

### Portfolio Data
- `get_portfolio()` - Get current portfolio positions
- `get_portfolio_total()` - Get portfolio totals
- `get_cash_funds()` - Get available cash

### Trading Operations
- `get_orders()` - Get open orders
- `get_transactions()` - Get transaction history
- `check_order()` - Check order status
- `confirm_order()` - Confirm an order
- `delete_order()` - Cancel an order

### Market Data
- `get_products_info()` - Get product information
- `search_products()` - Search for products
- `get_price_data()` - Get real-time prices

## Error Handling

```python
from degiro_connector.core.exceptions import (
    DeGiroConnectionError,
    DeGiroTimeoutError,
    DeGiroAPIError
)

try:
    trading_api.connect()
except DeGiroConnectionError as e:
    print(f"Connection error: {e}")
    if e.error_details:
        print(f"Details: {e.error_details}")
except DeGiroTimeoutError:
    print("Request timed out")
except DeGiroAPIError as e:
    print(f"API error: {e}")
```

## Common Operations

### Get Portfolio
```python
# Get portfolio positions
portfolio = trading_api.get_portfolio()
for position in portfolio['positions']:
    print(f"{position['product']['symbol']}: {position['size']} @ {position['price']}")

# Get portfolio totals
totals = trading_api.get_portfolio_total()
print(f"Total value: {totals['total']}")
```

### Search Products
```python
# Search for a product
results = trading_api.search_products(
    search_text="AAPL",
    limit=10,
    product_type_id=1  # Stocks
)

for product in results['products']:
    print(f"{product['symbol']} - {product['name']} ({product['isin']})")
```

### Get Product Info
```python
# Get detailed product information
product_ids = [96008, 1153605]  # Example product IDs
info = trading_api.get_products_info(product_list=product_ids)

for product_id, details in info.items():
    print(f"{details['name']}: €{details['lastPrice']}")
```

### Place Order (Example)
```python
# Check order first
order = {
    "product_id": 96008,
    "size": 10,
    "price": 100.50,
    "order_type": 0,  # Limited order
    "time_type": 1,   # Day order
    "buy_sell": "BUY"
}

# Check the order
checking_response = trading_api.check_order(order=order)
confirmation_id = checking_response["confirmationId"]

# Confirm the order
confirmation_response = trading_api.confirm_order(
    confirmation_id=confirmation_id,
    order=order
)
```

## Rate Limiting
The DEGIRO API has rate limits. Implement delays between requests:

```python
import time

def rate_limited_call(func, *args, **kwargs):
    result = func(*args, **kwargs)
    time.sleep(1)  # 1 second delay between calls
    return result
```

## Session Management
Sessions expire after ~30 minutes of inactivity. Implement session renewal:

```python
class SessionManager:
    def __init__(self, trading_api):
        self.api = trading_api
        self.last_activity = time.time()
    
    def ensure_connected(self):
        if time.time() - self.last_activity > 1800:  # 30 minutes
            self.api.connect()
        self.last_activity = time.time()
```

## Important Notes
1. **No Official API**: This uses reverse-engineered endpoints
2. **Terms of Service**: Automated trading violates DEGIRO's ToS
3. **Rate Limits**: Respect rate limits to avoid detection
4. **Session Timeout**: Sessions expire after ~30 minutes
5. **2FA Required**: Most accounts require TOTP authentication