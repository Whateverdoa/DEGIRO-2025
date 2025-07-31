"""Integration tests for DEGIRO API connection and operations."""

import pytest
import os
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from core.degiro_api import DeGiroAPIWrapper, RateLimiter
from core.portfolio_service import PortfolioService
from core.models import Portfolio, Position, Product, ProductType
from core.config import settings
from core.exceptions import AuthenticationError
from degiro_connector.core.exceptions import DeGiroConnectionError


class TestDegiroAPIIntegration:
    """Test suite for DEGIRO API integration."""
    
    @pytest.fixture
    def api_wrapper(self):
        """Create API wrapper instance for testing."""
        return DeGiroAPIWrapper()
    
    @pytest.fixture
    def mock_credentials(self):
        """Mock credentials for testing."""
        return {
            "username": "test_user",
            "password": "test_pass",
            "totp_secret": "TEST_SECRET_KEY"
        }
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response data."""
        return {
            "portfolio": {
                "positions": [
                    {
                        "productId": "1234567",
                        "size": 10,
                        "price": 150.50,
                        "value": 1505.00
                    }
                ]
            },
            "totalPortfolio": {
                "total": 10000.00,
                "cash": 5000.00
            },
            "cashFunds": {
                "EUR": {"value": 5000.00}
            }
        }

    def test_api_initialization(self, api_wrapper):
        """Test API wrapper initialization."""
        assert api_wrapper.api is None
        assert api_wrapper.rate_limiter is not None
        assert not api_wrapper.is_connected
        assert api_wrapper.session_start_time is None
        assert api_wrapper.last_activity_time is None

    def test_rate_limiter(self):
        """Test rate limiting functionality."""
        rate_limiter = RateLimiter(max_calls=2, time_window=1)
        
        # First two calls should pass immediately
        start = time.time()
        rate_limiter.wait_if_needed()
        rate_limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed < 0.1
        
        # Third call should wait
        start = time.time()
        rate_limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed >= 0.9  # Should wait at least 0.9 seconds

    @patch('core.degiro_api.degiro_credentials.get_credentials')
    @patch('core.degiro_api.API')
    def test_successful_connection(self, mock_api_class, mock_get_creds, api_wrapper, mock_credentials):
        """Test successful API connection."""
        # Setup mocks
        mock_get_creds.return_value = mock_credentials
        mock_api_instance = Mock()
        mock_api_class.return_value = mock_api_instance
        
        # Test connection
        result = api_wrapper.connect()
        
        assert result is True
        assert api_wrapper._is_connected is True
        assert api_wrapper.session_start_time is not None
        assert api_wrapper.last_activity_time is not None
        mock_api_instance.connect.assert_called_once()

    @patch('core.degiro_api.degiro_credentials.get_credentials')
    @patch('core.degiro_api.API')
    def test_connection_failure(self, mock_api_class, mock_get_creds, api_wrapper, mock_credentials):
        """Test API connection failure handling."""
        # Setup mocks
        mock_get_creds.return_value = mock_credentials
        mock_api_instance = Mock()
        mock_api_instance.connect.side_effect = DeGiroConnectionError("Authentication failed", {})
        mock_api_class.return_value = mock_api_instance
        
        # Test connection - should raise AuthenticationError
        with pytest.raises(AuthenticationError):
            api_wrapper.connect()
        
        assert not api_wrapper._is_connected

    @patch('core.degiro_api.degiro_credentials.get_credentials')
    def test_missing_credentials(self, mock_get_creds, api_wrapper):
        """Test connection with missing credentials."""
        mock_get_creds.return_value = {"username": "", "password": ""}
        
        result = api_wrapper.connect()
        
        assert result is False
        assert not api_wrapper._is_connected

    def test_session_timeout_detection(self, api_wrapper):
        """Test session timeout detection."""
        # Simulate connected state
        api_wrapper._is_connected = True
        api_wrapper.api = Mock()
        api_wrapper.last_activity_time = datetime.now() - timedelta(minutes=35)
        
        assert not api_wrapper.is_connected

    @patch('core.degiro_api.API')
    def test_get_portfolio_success(self, mock_api_class, api_wrapper, mock_api_response):
        """Test successful portfolio retrieval."""
        # Setup mock API
        mock_api_instance = Mock()
        mock_api_instance.get_portfolio.return_value = mock_api_response["portfolio"]
        mock_api_instance.get_portfolio_total.return_value = mock_api_response["totalPortfolio"]
        mock_api_instance.get_cash_funds.return_value = mock_api_response["cashFunds"]
        api_wrapper.api = mock_api_instance
        api_wrapper._is_connected = True
        
        # Test portfolio retrieval
        result = api_wrapper.get_portfolio()
        
        assert result is not None
        assert "positions" in result
        assert "total_value" in result
        assert "cash" in result
        assert result["total_value"] == 10000.00
        assert result["cash"] == 5000.00
        assert len(result["positions"]) == 1

    @patch('core.degiro_api.API')
    def test_search_products(self, mock_api_class, api_wrapper):
        """Test product search functionality."""
        # Setup mock API
        mock_api_instance = Mock()
        mock_api_instance.search_products.return_value = {
            "products": [
                {
                    "id": "123",
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "isin": "US0378331005",
                    "productTypeId": 1,
                    "currency": "USD",
                    "exchangeId": "NASDAQ"
                }
            ]
        }
        api_wrapper.api = mock_api_instance
        api_wrapper._is_connected = True
        
        # Test search
        results = api_wrapper.search_products("AAPL", limit=5)
        
        assert len(results) == 1
        assert results[0]["symbol"] == "AAPL"
        assert results[0]["name"] == "Apple Inc."
        mock_api_instance.search_products.assert_called_with(
            search_text="AAPL",
            limit=5,
            offset=0,
            product_type_id=None
        )

    @patch('core.degiro_api.API')
    def test_get_transactions(self, mock_api_class, api_wrapper):
        """Test transaction history retrieval."""
        # Setup mock API
        mock_api_instance = Mock()
        mock_api_instance.get_transactions.return_value = {
            "data": [
                {
                    "id": "TX123",
                    "date": "2024-01-10",
                    "productId": "1234567",
                    "quantity": 10,
                    "price": 150.00,
                    "totalPlusFeeInBaseCurrency": 1505.00,
                    "buysell": "BUY"
                }
            ]
        }
        api_wrapper.api = mock_api_instance
        api_wrapper._is_connected = True
        
        # Test transaction retrieval
        from_date = datetime(2024, 1, 1)
        to_date = datetime(2024, 1, 31)
        results = api_wrapper.get_transactions(from_date, to_date)
        
        assert len(results) == 1
        assert results[0]["id"] == "TX123"
        assert results[0]["transaction_type"] == "BUY"
        mock_api_instance.get_transactions.assert_called_with(
            from_date="01/01/2024",
            to_date="31/01/2024",
            group_transactions_by_order=False
        )

    @patch('core.degiro_api.API')
    def test_get_product_info(self, mock_api_class, api_wrapper):
        """Test product info retrieval."""
        # Setup mock API
        mock_api_instance = Mock()
        mock_api_instance.get_products_info.return_value = {
            "1234567": {
                "name": "Apple Inc.",
                "symbol": "AAPL",
                "isin": "US0378331005",
                "closePrice": 150.50,
                "bidPrice": 150.45,
                "askPrice": 150.55,
                "currency": "USD"
            }
        }
        api_wrapper.api = mock_api_instance
        api_wrapper._is_connected = True
        
        # Test product info retrieval
        result = api_wrapper.get_product_info("1234567")
        
        assert result["name"] == "Apple Inc."
        assert result["symbol"] == "AAPL"
        assert result["close_price"] == 150.50

    def test_health_check(self, api_wrapper):
        """Test API health check."""
        # Setup connected state
        api_wrapper._is_connected = True
        api_wrapper.session_start_time = datetime.now() - timedelta(minutes=10)
        api_wrapper.last_activity_time = datetime.now() - timedelta(minutes=1)
        api_wrapper.rate_limiter.calls = [time.time(), time.time() - 30]
        
        health = api_wrapper.health_check()
        
        assert health["connected"] is True
        assert health["session_duration"] is not None
        assert health["last_activity"] is not None
        assert health["rate_limit_status"]["calls_made"] == 2

    @patch('core.degiro_api.API')
    def test_retry_mechanism(self, mock_api_class, api_wrapper):
        """Test retry mechanism on API failures."""
        # Setup mock API that fails twice then succeeds
        mock_api_instance = Mock()
        mock_api_instance.get_portfolio.side_effect = [
            DeGiroConnectionError("Timeout", {}),
            ConnectionError("Network error"), 
            {"positions": []}  # Success on third try
        ]
        api_wrapper.api = mock_api_instance
        api_wrapper._is_connected = True
        
        # Test with retry decorator
        with patch('time.sleep'):  # Skip actual delays in test
            result = api_wrapper.get_portfolio()
        
        assert result is not None
        assert mock_api_instance.get_portfolio.call_count == 3

    def test_ensure_connected(self, api_wrapper):
        """Test ensure_connected functionality."""
        # Test when not connected
        api_wrapper._is_connected = False
        
        with patch.object(api_wrapper, 'connect', return_value=False):
            with pytest.raises(ConnectionError):
                api_wrapper.ensure_connected()
        
        # Test when already connected
        api_wrapper._is_connected = True
        api_wrapper.ensure_connected()  # Should not raise


class TestPortfolioServiceIntegration:
    """Test suite for portfolio service integration."""
    
    @pytest.fixture
    def portfolio_service_instance(self):
        """Create portfolio service instance."""
        return PortfolioService()
    
    @pytest.fixture
    def mock_portfolio_data(self):
        """Mock portfolio data from API."""
        return {
            "positions": [
                {
                    "product_id": "1234567",
                    "size": 10,
                    "price": 150.50,
                    "value": 1505.00,
                    "product_info": {
                        "symbol": "AAPL",
                        "name": "Apple Inc.",
                        "isin": "US0378331005",
                        "currency": "USD",
                        "productType": "STOCK"
                    }
                }
            ],
            "total_value": 10000.00,
            "cash": 5000.00,
            "timestamp": datetime.now().isoformat()
        }

    @patch.object(DeGiroAPIWrapper, 'get_portfolio')
    def test_get_portfolio_integration(self, mock_get_portfolio, portfolio_service_instance, mock_portfolio_data):
        """Test portfolio retrieval through service."""
        mock_get_portfolio.return_value = mock_portfolio_data
        
        portfolio = portfolio_service_instance.get_portfolio()
        
        assert portfolio is not None
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.positions) == 1
        assert portfolio.total_value == 10000.00
        assert portfolio.cash_balance == 5000.00

    def test_portfolio_caching(self, portfolio_service_instance):
        """Test portfolio caching mechanism."""
        # Create mock portfolio
        mock_portfolio = Portfolio(
            positions=[],
            total_value=10000.00,
            cash_balance=5000.00,
            total_invested=10000.00,
            total_pnl=0,
            total_pnl_percentage=0,
            currency="EUR"
        )
        
        # Set cache
        portfolio_service_instance._portfolio_cache = mock_portfolio
        portfolio_service_instance._cache_timestamp = datetime.now()
        
        # Get portfolio (should use cache)
        with patch.object(portfolio_service_instance, '_fetch_portfolio_data') as mock_fetch:
            result = portfolio_service_instance.get_portfolio()
            mock_fetch.assert_not_called()
        
        assert result == mock_portfolio

    def test_portfolio_analytics(self, portfolio_service_instance):
        """Test portfolio analytics generation."""
        # Create test portfolio
        portfolio = Portfolio(
            positions=[
                Position(
                    product_id="123",
                    product=Product(
                        id="123",
                        symbol="AAPL",
                        name="Apple Inc.",
                        product_type=ProductType.STOCK,
                        currency="USD"
                    ),
                    size=10,
                    average_price=140,
                    current_price=150,
                    value=1500,
                    unrealized_pnl=100,
                    currency="USD"
                )
            ],
            total_value=10000,
            cash_balance=8500,
            total_invested=10000,
            total_pnl=100,
            total_pnl_percentage=1.0,
            currency="EUR"
        )
        
        analytics = portfolio_service_instance.get_portfolio_analytics(portfolio)
        
        assert analytics["summary"]["total_value"] == 10000
        assert analytics["summary"]["number_of_positions"] == 1
        assert len(analytics["top_gainers"]) == 1
        assert analytics["top_gainers"][0]["symbol"] == "AAPL"

    def test_export_portfolio_json(self, portfolio_service_instance):
        """Test portfolio export in JSON format."""
        portfolio = Portfolio(
            positions=[],
            total_value=10000,
            cash_balance=10000,
            total_invested=10000,
            total_pnl=0,
            total_pnl_percentage=0,
            currency="EUR"
        )
        
        json_export = portfolio_service_instance.export_portfolio(portfolio, format="json")
        
        assert isinstance(json_export, str)
        assert "total_value" in json_export
        assert "10000" in json_export

    def test_product_type_mapping(self, portfolio_service_instance):
        """Test DEGIRO product type mapping."""
        assert portfolio_service_instance._map_product_type("STOCK") == ProductType.STOCK
        assert portfolio_service_instance._map_product_type("ETF") == ProductType.ETF
        assert portfolio_service_instance._map_product_type("UNKNOWN") == ProductType.STOCK


# Integration test for end-to-end flow
@pytest.mark.integration
class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.skipif(
        not os.getenv("DEGIRO_USERNAME"),
        reason="Requires real DEGIRO credentials"
    )
    def test_real_api_connection(self):
        """Test real API connection (requires credentials)."""
        api = DeGiroAPIWrapper()
        
        # Attempt connection
        connected = api.connect()
        
        if connected:
            # Test basic operations
            portfolio = api.get_portfolio()
            assert portfolio is not None
            
            # Disconnect
            api.disconnect()
        else:
            pytest.skip("Could not connect to DEGIRO API")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])