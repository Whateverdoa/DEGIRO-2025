#!/usr/bin/env python3
"""Test DEGIRO connection with TOTP authentication."""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.degiro_api import DeGiroAPI
from core.logging_config import setup_logging
from core.config import Config

# Setup logging
setup_logging(log_level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection():
    """Test DEGIRO connection with TOTP authentication."""
    try:
        # Initialize configuration
        config = Config()
        
        # Check if credentials are configured
        if not config.get("degiro.username") or not config.get("degiro.password"):
            logger.error("DEGIRO credentials not configured. Please set:")
            logger.error("- DEGIRO_USERNAME")
            logger.error("- DEGIRO_PASSWORD")
            logger.error("- DEGIRO_TOTP_SECRET (if 2FA is enabled)")
            return False
        
        # Initialize API
        logger.info("Initializing DEGIRO API...")
        api = DeGiroAPI()
        
        # Test connection
        logger.info("Testing connection to DEGIRO...")
        await api.connect()
        
        logger.info("✅ Successfully connected to DEGIRO!")
        
        # Get account info
        logger.info("Fetching account information...")
        account_info = await api.get_account_info()
        logger.info(f"Account info: {account_info}")
        
        # Get portfolio
        logger.info("Fetching portfolio...")
        portfolio = await api.get_portfolio_data()
        logger.info(f"Portfolio has {len(portfolio)} positions")
        
        # Disconnect
        await api.disconnect()
        logger.info("✅ Connection test completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)