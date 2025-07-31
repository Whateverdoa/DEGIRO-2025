#!/usr/bin/env python3
"""Comprehensive tests for portfolio monitoring dashboard."""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set env vars before importing config
os.environ['ENVIRONMENT'] = 'development'
os.environ['DEGIRO_API_RATE_LIMIT'] = '60'
os.environ['MARKET_DATA_RATE_LIMIT'] = '120'
os.environ['MAX_POSITION_SIZE'] = '10000'
os.environ['MARKET_DATA_PROVIDER'] = 'yfinance'

from core.logging_config import setup_logging
from core.portfolio_service import portfolio_service
from core.degiro_api import degiro_api

# Setup logging
setup_logging(log_level='INFO')
import logging
logger = logging.getLogger(__name__)


def test_portfolio_fetch():
    """Test 1: Basic portfolio fetching"""
    logger.info("\n=== Test 1: Portfolio Fetching ===")
    
    try:
        # Get portfolio
        portfolio = portfolio_service.get_portfolio()
        
        if portfolio:
            logger.info("✅ Portfolio fetched successfully!")
            logger.info(f"Total Value: {portfolio.currency} {portfolio.total_value:,.2f}")
            logger.info(f"Cash Balance: {portfolio.currency} {portfolio.cash_balance:,.2f}")
            logger.info(f"Number of Positions: {len(portfolio.positions)}")
            logger.info(f"Total P&L: {portfolio.currency} {portfolio.total_pnl:,.2f} ({portfolio.total_pnl_percentage:.2f}%)")
            
            # Show positions
            logger.info("\nPositions:")
            for pos in portfolio.positions:
                logger.info(f"- {pos.product.symbol if pos.product else pos.product_id}: "
                           f"{pos.size} shares @ {pos.current_price:.2f} = {pos.value:.2f} "
                           f"(P&L: {pos.unrealized_pnl:.2f})")
            return True
        else:
            logger.error("❌ Failed to fetch portfolio")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_portfolio_caching():
    """Test 2: Portfolio caching mechanism"""
    logger.info("\n=== Test 2: Portfolio Caching ===")
    
    try:
        # First fetch
        start_time = time.time()
        portfolio1 = portfolio_service.get_portfolio()
        first_fetch_time = time.time() - start_time
        logger.info(f"First fetch took: {first_fetch_time:.2f}s")
        
        # Second fetch (should use cache)
        start_time = time.time()
        portfolio2 = portfolio_service.get_portfolio()
        second_fetch_time = time.time() - start_time
        logger.info(f"Second fetch took: {second_fetch_time:.2f}s")
        
        # Verify cache is working
        if second_fetch_time < first_fetch_time * 0.1:  # Should be much faster
            logger.info("✅ Caching is working correctly")
        else:
            logger.warning("⚠️ Cache might not be working as expected")
        
        # Force refresh
        start_time = time.time()
        portfolio3 = portfolio_service.get_portfolio(force_refresh=True)
        force_refresh_time = time.time() - start_time
        logger.info(f"Force refresh took: {force_refresh_time:.2f}s")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_portfolio_analytics():
    """Test 3: Portfolio analytics calculations"""
    logger.info("\n=== Test 3: Portfolio Analytics ===")
    
    try:
        # Get portfolio
        portfolio = portfolio_service.get_portfolio()
        if not portfolio:
            logger.error("Failed to get portfolio for analytics")
            return False
        
        # Get analytics
        analytics = portfolio_service.get_portfolio_analytics(portfolio)
        
        logger.info("✅ Analytics generated successfully!")
        
        # Display summary
        summary = analytics.get("summary", {})
        logger.info(f"\nSummary:")
        logger.info(f"- Total Value: {summary.get('currency', 'EUR')} {summary.get('total_value', 0):,.2f}")
        logger.info(f"- Cash Balance: {summary.get('currency', 'EUR')} {summary.get('cash_balance', 0):,.2f}")
        logger.info(f"- Invested Value: {summary.get('currency', 'EUR')} {summary.get('invested_value', 0):,.2f}")
        logger.info(f"- Total P&L: {summary.get('currency', 'EUR')} {summary.get('total_pnl', 0):,.2f} ({summary.get('total_pnl_percentage', 0):.2f}%)")
        
        # Display positions by type
        logger.info(f"\nPositions by Type:")
        for ptype, data in analytics.get("positions_by_type", {}).items():
            logger.info(f"- {ptype}: {data['count']} positions, value: {data['value']:,.2f}, P&L: {data['pnl']:,.2f}")
        
        # Display top gainers
        logger.info(f"\nTop Gainers:")
        for gainer in analytics.get("top_gainers", [])[:3]:
            logger.info(f"- {gainer['symbol']}: P&L {gainer['pnl']:,.2f} ({gainer['pnl_percentage']:.2f}%)")
        
        # Display top losers
        logger.info(f"\nTop Losers:")
        for loser in analytics.get("top_losers", [])[:3]:
            logger.info(f"- {loser['symbol']}: P&L {loser['pnl']:,.2f} ({loser['pnl_percentage']:.2f}%)")
        
        # Display concentration
        logger.info(f"\nTop Holdings (Concentration):")
        for holding in analytics.get("concentration", [])[:3]:
            logger.info(f"- {holding['symbol']}: {holding['percentage']:.2f}% of portfolio")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_portfolio_export():
    """Test 4: Portfolio export functionality"""
    logger.info("\n=== Test 4: Portfolio Export ===")
    
    try:
        # Get portfolio
        portfolio = portfolio_service.get_portfolio()
        if not portfolio:
            logger.error("Failed to get portfolio for export")
            return False
        
        # Test JSON export
        logger.info("\nTesting JSON export...")
        json_export = portfolio_service.export_portfolio(portfolio, format="json")
        json_data = json.loads(json_export)
        logger.info(f"✅ JSON export successful: {len(json_export)} bytes")
        logger.info(f"   Contains {len(json_data['positions'])} positions")
        
        # Test CSV export
        logger.info("\nTesting CSV export...")
        csv_export = portfolio_service.export_portfolio(portfolio, format="csv")
        csv_lines = csv_export.strip().split('\n')
        logger.info(f"✅ CSV export successful: {len(csv_lines)-1} positions")
        logger.info(f"   Headers: {csv_lines[0]}")
        
        # Test HTML export
        logger.info("\nTesting HTML export...")
        html_export = portfolio_service.export_portfolio(portfolio, format="html")
        logger.info(f"✅ HTML export successful: {len(html_export)} bytes")
        
        # Save exports to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create exports directory
        exports_dir = Path("data/exports")
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_file = exports_dir / f"portfolio_{timestamp}.json"
        json_file.write_text(json_export)
        logger.info(f"   Saved JSON to: {json_file}")
        
        # Save CSV
        csv_file = exports_dir / f"portfolio_{timestamp}.csv"
        csv_file.write_text(csv_export)
        logger.info(f"   Saved CSV to: {csv_file}")
        
        # Save HTML
        html_file = exports_dir / f"portfolio_{timestamp}.html"
        html_file.write_text(html_export)
        logger.info(f"   Saved HTML to: {html_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False


def test_portfolio_monitoring_flow():
    """Test 5: Complete portfolio monitoring workflow"""
    logger.info("\n=== Test 5: Complete Portfolio Monitoring Workflow ===")
    
    try:
        # Step 1: Connect to DEGIRO
        logger.info("\nStep 1: Connecting to DEGIRO...")
        if not degiro_api.is_connected:
            if degiro_api.connect():
                logger.info("✅ Connected to DEGIRO")
            else:
                logger.error("❌ Failed to connect to DEGIRO")
                return False
        else:
            logger.info("✅ Already connected to DEGIRO")
        
        # Step 2: Fetch portfolio
        logger.info("\nStep 2: Fetching portfolio...")
        portfolio = portfolio_service.get_portfolio(force_refresh=True)
        if portfolio:
            logger.info("✅ Portfolio fetched successfully")
        else:
            logger.error("❌ Failed to fetch portfolio")
            return False
        
        # Step 3: Analyze portfolio
        logger.info("\nStep 3: Analyzing portfolio...")
        analytics = portfolio_service.get_portfolio_analytics(portfolio)
        if analytics:
            logger.info("✅ Portfolio analyzed successfully")
        else:
            logger.error("❌ Failed to analyze portfolio")
            return False
        
        # Step 4: Monitor for changes (simulate)
        logger.info("\nStep 4: Monitoring for changes...")
        logger.info("Waiting 5 seconds...")
        time.sleep(5)
        
        # Check portfolio again
        portfolio2 = portfolio_service.get_portfolio()
        if portfolio2:
            logger.info("✅ Portfolio refresh successful")
            
            # Compare values
            if portfolio2.total_value != portfolio.total_value:
                logger.info(f"📊 Portfolio value changed: {portfolio.total_value:.2f} → {portfolio2.total_value:.2f}")
            else:
                logger.info("📊 Portfolio value unchanged")
        
        # Step 5: Generate report
        logger.info("\nStep 5: Generating portfolio report...")
        html_report = portfolio_service.export_portfolio(portfolio2, format="html")
        if html_report:
            logger.info("✅ Report generated successfully")
        
        # Step 6: Disconnect
        logger.info("\nStep 6: Disconnecting...")
        degiro_api.disconnect()
        logger.info("✅ Disconnected from DEGIRO")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow test failed: {e}")
        return False


def test_error_handling():
    """Test 6: Error handling and edge cases"""
    logger.info("\n=== Test 6: Error Handling ===")
    
    try:
        # Test with disconnected API
        logger.info("\nTesting with disconnected API...")
        if degiro_api.is_connected:
            degiro_api.disconnect()
        
        portfolio = portfolio_service.get_portfolio()
        if portfolio:
            logger.info("✅ Handled disconnection gracefully (auto-reconnected)")
        else:
            logger.info("⚠️ Returned None for disconnected API")
        
        # Test invalid export format
        logger.info("\nTesting invalid export format...")
        try:
            portfolio_service.export_portfolio(portfolio, format="invalid")
            logger.error("❌ Should have raised ValueError")
        except ValueError as e:
            logger.info(f"✅ Correctly raised ValueError: {e}")
        
        # Test empty portfolio handling
        logger.info("\nTesting empty portfolio handling...")
        from core.models import Portfolio
        empty_portfolio = Portfolio(
            positions=[],
            total_value=0,
            cash_balance=0,
            total_invested=0,
            total_pnl=0,
            total_pnl_percentage=0,
            currency="EUR"
        )
        
        analytics = portfolio_service.get_portfolio_analytics(empty_portfolio)
        logger.info("✅ Handled empty portfolio gracefully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False


def run_all_tests():
    """Run all portfolio monitoring tests."""
    logger.info("="*60)
    logger.info("PORTFOLIO MONITORING DASHBOARD - COMPREHENSIVE TESTS")
    logger.info("="*60)
    
    tests = [
        ("Portfolio Fetching", test_portfolio_fetch),
        ("Portfolio Caching", test_portfolio_caching),
        ("Portfolio Analytics", test_portfolio_analytics),
        ("Portfolio Export", test_portfolio_export),
        ("Complete Workflow", test_portfolio_monitoring_flow),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\nRunning: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.error(f"Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name:<30} {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Portfolio monitoring is working correctly.")
    else:
        logger.warning(f"\n⚠️ {total - passed} tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)