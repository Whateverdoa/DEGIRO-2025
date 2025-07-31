#!/usr/bin/env python3
"""Test DEGIRO connection with TOTP authentication."""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set env vars before importing config
os.environ['ENVIRONMENT'] = 'development'
os.environ['DEGIRO_API_RATE_LIMIT'] = '60'
os.environ['MARKET_DATA_RATE_LIMIT'] = '120'
os.environ['MAX_POSITION_SIZE'] = '10000'
os.environ['MARKET_DATA_PROVIDER'] = 'yfinance'

from core.degiro_api import DeGiroAPIWrapper
from core.logging_config import setup_logging
from core.config import config_manager

# Setup logging
setup_logging(log_level='INFO')
logger = logging.getLogger(__name__)


def test_connection():
    """Test DEGIRO connection with TOTP authentication."""
    try:
        # Check if credentials are configured
        if not config_manager.get("degiro_username") or not config_manager.get("degiro_password"):
            logger.error("DEGIRO credentials not configured. Please set:")
            logger.error("- DEGIRO_USERNAME")
            logger.error("- DEGIRO_PASSWORD")
            logger.error("- DEGIRO_TOTP_SECRET (if 2FA is enabled)")
            return False
        
        # Initialize API
        logger.info("Initializing DEGIRO API...")
        api = DeGiroAPIWrapper()
        
        # Test connection
        logger.info("Testing connection to DEGIRO...")
        connected = api.connect()
        
        if connected:
            logger.info("✅ Successfully connected to DEGIRO!")
            
            # Test health check
            logger.info("Testing health check...")
            try:
                health = api.health_check()
                logger.info(f"Health status: {health}")
                logger.info("✅ Health check successful!")
            except Exception as e:
                logger.error(f"Failed health check: {e}")
            
            # Disconnect
            api.disconnect()
            logger.info("✅ Connection test completed successfully!")
            
            return True
        else:
            logger.error("Failed to connect to DEGIRO")
            return False
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Run the test
    success = test_connection()
    sys.exit(0 if success else 1)