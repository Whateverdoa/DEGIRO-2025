#!/usr/bin/env python3
"""Test script to verify data persistence functionality."""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.portfolio_service import portfolio_service
from core.database import init_database, db_manager
from core.data_persistence import data_persistence
from core.logging_config import get_logger

logger = get_logger("test_persistence")


def test_database_initialization():
    """Test database initialization."""
    print("=== Testing Database Initialization ===")
    
    # Initialize database
    success = init_database(create_tables=True)
    print(f"Database initialization: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test connection health
    health = db_manager.health_check()
    print(f"Database health check: {'✅ HEALTHY' if health else '❌ UNHEALTHY'}")
    
    # Get database stats
    stats = db_manager.get_stats()
    print(f"Database statistics: {stats}")
    
    return success


def test_portfolio_data_persistence():
    """Test portfolio data persistence functionality."""
    print("\n=== Testing Portfolio Data Persistence ===")
    
    try:
        # Get current portfolio (this should save to database automatically)
        print("Fetching portfolio data...")
        portfolio = portfolio_service.get_portfolio(force_refresh=True)
        
        if portfolio:
            print(f"✅ Portfolio fetched: {len(portfolio.positions)} positions")
            print(f"   Total value: {portfolio.total_value:.2f} {portfolio.currency}")
            
            # Get database statistics after saving
            db_stats = data_persistence.get_database_stats()
            print(f"✅ Database stats: {db_stats}")
            
            # Test portfolio history
            print("\nTesting portfolio history...")
            history = portfolio_service.get_portfolio_history(days=7)
            print(f"✅ Portfolio history: {len(history)} snapshots in last 7 days")
            
            if history:
                latest = history[0]
                print(f"   Latest snapshot: {latest['date']} - Value: {latest['total_value']:.2f}")
            
            # Test performance metrics
            print("\nTesting performance metrics...")
            performance = portfolio_service.get_portfolio_performance(days=7)
            if "error" not in performance:
                print(f"✅ Performance metrics calculated")
                print(f"   Data points: {performance.get('data_points', 0)}")
                print(f"   Period: {performance.get('period_days', 0)} days")
            else:
                print(f"⚠️ Performance metrics: {performance['error']}")
            
            return True
            
        else:
            print("❌ Failed to fetch portfolio data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing portfolio persistence: {e}")
        return False


def test_database_stats():
    """Test database statistics and monitoring."""
    print("\n=== Testing Database Statistics ===")
    
    try:
        # Get comprehensive database stats
        stats = portfolio_service.get_database_stats()
        
        if "error" not in stats:
            print("✅ Database statistics retrieved:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Database stats error: {stats['error']}")
            
        return "error" not in stats
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return False


def main():
    """Run all data persistence tests."""
    print("DEGIRO Trading Agent - Data Persistence Test")
    print("=" * 50)
    
    tests = [
        ("Database Initialization", test_database_initialization),
        ("Portfolio Data Persistence", test_portfolio_data_persistence),
        ("Database Statistics", test_database_stats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All data persistence tests passed!")
        print("\nData storage is now working:")
        print("• Portfolio snapshots are saved to database automatically")
        print("• Historical data tracking is enabled")
        print("• Performance metrics can be calculated")
        print("• SQLite database is initialized at: data/degiro_trading.db")
    else:
        print("⚠️ Some tests failed - check logs for details")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)