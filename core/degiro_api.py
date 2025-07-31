"""DEGIRO API wrapper with error handling and rate limiting."""

import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from functools import wraps
import threading
from degiro_connector.trading.api import API, Credentials
from degiro_connector.core.exceptions import DeGiroConnectionError
from core.logging_config import get_logger, trading_log, TRADING_INFO
from core.config import settings
from core.security import degiro_credentials
from core.human_behavior import HumanBehavior, HumanlikeDegiroSession
from core.exceptions import (
    handle_degiro_error,
    AuthenticationError,
    SessionExpiredError,
    RateLimitError,
    APITimeoutError
)
from core.api_monitor import api_monitor, monitored_api_call


logger = get_logger("degiro_api")


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        with self.lock:
            now = time.time()
            # Remove old calls outside time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                # Need to wait
                oldest_call = self.calls[0]
                wait_time = self.time_window - (now - oldest_call) + 0.1
                logger.debug(f"Rate limit reached, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                # Recursive call to clean up and check again
                return self.wait_if_needed()
            
            # Record this call
            self.calls.append(now)


def rate_limited(func):
    """Decorator for rate-limited API calls."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.rate_limiter.wait_if_needed()
        return func(self, *args, **kwargs)
    return wrapper


def with_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {wait_time}s: {e}"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
            
            raise last_exception
        return wrapper
    return decorator


class DeGiroAPIWrapper:
    """Wrapper around DeGiro API with enhanced functionality."""
    
    def __init__(self):
        self.api = None
        self.rate_limiter = RateLimiter(
            max_calls=settings.degiro_api_rate_limit,
            time_window=60
        )
        self.session_start_time = None
        self.last_activity_time = None
        self._is_connected = False
        self.human_session = HumanlikeDegiroSession()
        
    @property
    def is_connected(self) -> bool:
        """Check if API is connected and session is valid."""
        if not self._is_connected or not self.api:
            return False
            
        # Check session timeout (assume 30 minutes)
        if self.last_activity_time:
            if datetime.now() - self.last_activity_time > timedelta(minutes=30):
                logger.warning("Session may have timed out")
                self._is_connected = False
                
        return self._is_connected
    
    def connect(self) -> bool:
        """
        Connect to DeGiro API.
        
        Returns:
            True if connection successful
        """
        try:
            # Human-like behavior before login
            self.human_session.before_action("login")
            
            # Validate credentials
            if not degiro_credentials.validate_credentials():
                degiro_credentials.setup_credentials(interactive=False)
                
            creds = degiro_credentials.get_credentials()
            
            if not creds["username"] or not creds["password"]:
                logger.error("Missing DEGIRO credentials")
                return False
            
            # Add random delay before connecting (human reading login page)
            HumanBehavior.random_delay(1, 3)
            
            # Create credentials object
            int_account = creds.get("int_account")
            if int_account:
                int_account = int(int_account)  # Convert to integer
                logger.info(f"Using int_account: {int_account}")
            
            credentials = Credentials(
                int_account=int_account,
                username=creds["username"],
                password=creds["password"],
                totp_secret_key=creds.get("totp_secret")
            )
            
            # Initialize API
            self.api = API(credentials=credentials)
            
            # Connect
            self.api.connect()
            
            self._is_connected = True
            self.session_start_time = datetime.now()
            self.last_activity_time = datetime.now()
            self.human_session.session_start = datetime.now()
            
            # Human-like delay after successful login
            HumanBehavior.random_delay(2, 5)
            self.human_session.after_action()
            
            logger.info("Successfully connected to DEGIRO API")
            trading_log(logger, f"TRADING: Connected to DEGIRO for user {creds['username'][:3]}***")
            
            return True
            
        except DeGiroConnectionError as e:
            custom_error = handle_degiro_error(e)
            logger.error(f"Failed to connect to DEGIRO API: {custom_error.message}")
            if custom_error.details:
                logger.debug(f"Error details: {custom_error.details}")
            self._is_connected = False
            
            # Re-raise specific errors for better handling upstream
            if isinstance(custom_error, AuthenticationError):
                raise custom_error
            
            # Record connection failure
            api_monitor.record_session_event("connection_failed", {
                "error_type": type(custom_error).__name__,
                "error_message": custom_error.message
            })
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from DeGiro API."""
        try:
            if self.api:
                self.api.logout()
                logger.info("Disconnected from DEGIRO API")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
        finally:
            self._is_connected = False
            self.api = None
    
    def ensure_connected(self):
        """Ensure API is connected, reconnect if necessary."""
        if not self.is_connected:
            logger.info("API not connected, attempting to connect...")
            if not self.connect():
                raise ConnectionError("Failed to connect to DEGIRO API")
    
    @rate_limited
    @with_retry(max_retries=2)
    @monitored_api_call("get_portfolio")
    def get_portfolio(self) -> Dict[str, Any]:
        """
        Get current portfolio positions using degiro-connector's get_update method
        with comprehensive portfolio data parser.
        
        Returns:
            Dictionary containing portfolio data
        """
        if not self.is_connected:
            raise SessionExpiredError("Not connected to DEGIRO API")
            
        # Human-like behavior before API call
        self.human_session.before_action("portfolio_check")
        HumanBehavior.random_delay(0.5, 2.0)
        
        try:
            # Import the required classes
            from degiro_connector.trading.models.account import UpdateRequest, UpdateOption
            
            # Create update requests for portfolio data
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
            
            # Get all data in one call
            account_update = self.api.get_update(
                request_list=[
                    portfolio_request,
                    total_portfolio_request,
                    cash_funds_request
                ],
                raw=True
            )
            
            # Use the comprehensive portfolio parser
            parsed_data = self._parse_portfolio_data(account_update)
            
            self.last_activity_time = datetime.now()
            self.human_session.after_action()
            
            logger.info(f"Retrieved portfolio with {len(parsed_data['positions'])} positions")
            trading_log(logger, f"TRADING: Portfolio retrieved - {len(parsed_data['positions'])} positions, €{parsed_data['total_value']:.2f} total")
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to get portfolio: {e}")
            raise
    
    def _parse_portfolio_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse DEGIRO API response into structured portfolio data.
        
        Args:
            api_response: Raw response from DEGIRO API get_update call
            
        Returns:
            Processed portfolio data dictionary
        """
        try:
            positions = []
            total_value = 0
            cash_balance = 0
            invested_amount = 0
            unrealized_pl = 0
            
            # Extract portfolio data from the response
            portfolio_data = api_response.get('portfolio', {}).get('value', [])
            
            # Get product IDs for securities (filter out cash positions)
            product_ids = []
            for item in portfolio_data:
                position_id = item.get('id', '')
                if str(position_id).isdigit():  # Only numeric IDs are securities
                    product_ids.append(int(position_id))
            
            # Fetch product information for all securities at once
            product_info_map = {}
            if product_ids:
                try:
                    products_response = self.api.get_products_info(product_list=product_ids)
                    
                    # Parse product information
                    if hasattr(products_response, 'data') and products_response.data:
                        for product_id, product_data in products_response.data.items():
                            try:
                                symbol = getattr(product_data, 'symbol', 'Unknown')
                                name = getattr(product_data, 'name', 'Unknown')
                            except AttributeError:
                                # Try dictionary access
                                symbol = product_data.get('symbol', 'Unknown') if isinstance(product_data, dict) else 'Unknown'
                                name = product_data.get('name', 'Unknown') if isinstance(product_data, dict) else 'Unknown'
                            
                            product_info_map[str(product_id)] = {
                                'symbol': symbol,
                                'name': name
                            }
                    elif isinstance(products_response, dict):
                        for product_id, product_data in products_response.items():
                            if isinstance(product_data, dict):
                                product_info_map[str(product_id)] = {
                                    'symbol': product_data.get('symbol', 'Unknown'),
                                    'name': product_data.get('name', 'Unknown')
                                }
                except Exception as e:
                    logger.warning(f"Failed to fetch product info: {e}")
            
            # Process each position
            for item in portfolio_data:
                position_id = item.get('id', '')
                values = {v['name']: v.get('value') for v in item.get('value', [])}
                
                position_type = values.get('positionType', '')
                size = values.get('size', 0)
                price = values.get('price', 0)
                value = values.get('value', 0)
                pl_base = values.get('plBase', {})
                
                # Get product information
                product_info = product_info_map.get(str(position_id), {})
                symbol = product_info.get('symbol', 'Unknown')
                name = product_info.get('name', 'Unknown')
                
                # Handle cash positions
                if position_type == 'CASH':
                    cash_balance += value
                    symbol = position_id  # Use the cash currency as symbol
                    name = f"Cash ({position_id})"
                elif position_type == 'PRODUCT' and size != 0:
                    invested_amount += abs(value)
                    if isinstance(pl_base, dict):
                        unrealized_pl += sum(pl_base.values())
                
                total_value += value
                
                position_data = {
                    'id': position_id,
                    'symbol': symbol,
                    'name': name,
                    'size': size,
                    'price': price,
                    'value': value,
                    'unrealized_pl': sum(pl_base.values()) if isinstance(pl_base, dict) else 0,
                    'position_type': position_type
                }
                
                positions.append(position_data)
            
            return {
                'positions': positions,
                'total_value': total_value,
                'cash_balance': cash_balance,
                'invested_amount': invested_amount,
                'unrealized_pl': unrealized_pl
            }
            
        except Exception as e:
            logger.error(f"Error parsing portfolio data: {e}")
            return {
                'positions': [],
                'total_value': 0,
                'cash_balance': 0,
                'invested_amount': 0,
                'unrealized_pl': 0
            }
    
    @rate_limited
    @with_retry(max_retries=3)
    @monitored_api_call("search_products")
    def search_products(self, search_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products by text.
        
        Args:
            search_text: Search query
            limit: Maximum number of results
            
        Returns:
            List of product dictionaries
        """
        self.ensure_connected()
        
        # Human-like behavior
        self.human_session.before_action("search")
        HumanBehavior.typing_delay(len(search_text))
        
        try:
            # Search products using degiro-connector API
            search_results = self.api.search_products(
                search_text=search_text,
                limit=limit,
                offset=0,
                product_type_id=None  # Search all product types
            )
            
            self.last_activity_time = datetime.now()
            
            results = []
            if search_results and 'products' in search_results:
                for product in search_results['products']:
                    results.append({
                        "id": product.get('id'),
                        "name": product.get('name'),
                        "symbol": product.get('symbol'),
                        "isin": product.get('isin'),
                        "product_type": product.get('productTypeId'),
                        "currency": product.get('currency'),
                        "exchange_id": product.get('exchangeId')
                    })
            
            # Simulate reading search results
            if results:
                HumanBehavior.simulate_reading_time(len(str(results)) // 20)
            
            self.human_session.after_action()
            
            logger.info(f"Found {len(results)} products for '{search_text}'")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            raise
    
    @rate_limited
    @with_retry(max_retries=3)
    def get_transactions(self, from_date: datetime, to_date: datetime) -> List[Dict[str, Any]]:
        """
        Get transaction history.
        
        Args:
            from_date: Start date
            to_date: End date
            
        Returns:
            List of transaction dictionaries
        """
        self.ensure_connected()
        
        try:
            # Get transactions using degiro-connector API
            transactions = self.api.get_transactions(
                from_date=from_date.strftime("%d/%m/%Y"),
                to_date=to_date.strftime("%d/%m/%Y"),
                group_transactions_by_order=False
            )
            
            self.last_activity_time = datetime.now()
            
            results = []
            if transactions and 'data' in transactions:
                for tx in transactions['data']:
                    results.append({
                        "id": tx.get('id'),
                        "date": tx.get('date'),
                        "product_id": tx.get('productId'),
                        "quantity": tx.get('quantity', 0),
                        "price": tx.get('price', 0),
                        "total_amount": tx.get('totalPlusFeeInBaseCurrency', 0),
                        "transaction_type": tx.get('buysell', 'UNKNOWN')
                    })
            
            logger.info(f"Retrieved {len(results)} transactions")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            raise
    
    @rate_limited
    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed product information.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product information dictionary
        """
        self.ensure_connected()
        
        try:
            products_info = self.api.get_products_info(
                product_list=[product_id],
                raw=False
            )
            
            self.last_activity_time = datetime.now()
            
            if products_info and str(product_id) in products_info:
                product = products_info[str(product_id)]
                return {
                    "id": product_id,
                    "name": product.get('name', ''),
                    "symbol": product.get('symbol', ''),
                    "isin": product.get('isin', ''),
                    "close_price": product.get('closePrice', 0),
                    "bid_price": product.get('bidPrice', 0),
                    "ask_price": product.get('askPrice', 0),
                    "currency": product.get('currency', '')
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get product info: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on API connection.
        
        Returns:
            Health status dictionary
        """
        health = {
            "connected": self.is_connected,
            "session_duration": None,
            "last_activity": None,
            "rate_limit_status": {
                "calls_made": len(self.rate_limiter.calls),
                "max_calls": self.rate_limiter.max_calls,
                "time_window": self.rate_limiter.time_window
            }
        }
        
        if self.session_start_time:
            health["session_duration"] = str(datetime.now() - self.session_start_time)
            
        if self.last_activity_time:
            health["last_activity"] = self.last_activity_time.isoformat()
            
        return health


# Global API instance
degiro_api = DeGiroAPIWrapper()