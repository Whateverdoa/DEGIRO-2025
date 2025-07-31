#!/usr/bin/env python3
"""Demo test to show data persistence without requiring DEGIRO connection."""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.models import Portfolio, Position, Product, ProductType
from core.database import init_database
from core.data_persistence import data_persistence
from core.logging_config import get_logger

logger = get_logger("persistence_demo")


def create_sample_portfolio() -> Portfolio:
    """Create a sample portfolio for testing."""
    # Create sample products
    products = [
        Product(
            id="12345",
            symbol="AAPL",
            name="Apple Inc.",
            isin="US0378331005",
            product_type=ProductType.STOCK,
            currency="USD",
            close_price=150.00
        ),
        Product(
            id="67890",
            symbol="MSFT",
            name="Microsoft Corporation",
            isin="US5949181045",
            product_type=ProductType.STOCK,
            currency="USD",
            close_price=300.00
        ),
        Product(
            id="11111",
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            isin="US9229087690",
            product_type=ProductType.ETF,
            currency="USD",
            close_price=220.00
        )
    ]
    
    # Create sample positions
    positions = [
        Position(
            product_id="12345",
            product=products[0],
            size=10,
            average_price=140.00,
            current_price=150.00,
            value=1500.00,
            unrealized_pnl=100.00,
            currency="USD"
        ),
        Position(
            product_id="67890",
            product=products[1],
            size=5,
            average_price=280.00,
            current_price=300.00,
            value=1500.00,
            unrealized_pnl=100.00,
            currency="USD"
        ),
        Position(
            product_id="11111",
            product=products[2],
            size=20,
            average_price=210.00,
            current_price=220.00,
            value=4400.00,
            unrealized_pnl=200.00,
            currency="USD"
        )
    ]
    
    # Create portfolio
    portfolio = Portfolio(
        positions=positions,
        total_value=10000.00,
        cash_balance=2600.00,  # 10000 - 7400 (positions value)
        total_invested=9600.00,
        total_pnl=400.00,
        total_pnl_percentage=4.17,
        currency="USD"
    )
    
    return portfolio


def demo_data_persistence():
    """Demonstrate data persistence functionality."""
    print("DEGIRO Trading Agent - Data Persistence Demo")
    print("=" * 55)
    
    # 1. Initialize Database
    print("1. Initializing database...")
    success = init_database(create_tables=True)
    if not success:
        print("❌ Failed to initialize database")
        return False
    print("✅ Database initialized successfully")
    
    # 2. Create Sample Portfolio
    print("\n2. Creating sample portfolio...")
    portfolio = create_sample_portfolio()
    print(f"✅ Sample portfolio created with {len(portfolio.positions)} positions")
    print(f"   Total value: ${portfolio.total_value:,.2f}")
    print(f"   Total P&L: ${portfolio.total_pnl:,.2f} ({portfolio.total_pnl_percentage:.2f}%)")
    
    # 3. Save Portfolio to Database
    print("\n3. Saving portfolio to database...")
    success = data_persistence.save_portfolio_snapshot(portfolio)
    if success:
        print("✅ Portfolio snapshot saved successfully")
    else:
        print("❌ Failed to save portfolio snapshot")
        return False
    
    # 4. Save Positions
    print("\n4. Saving positions to database...")
    success = data_persistence.save_positions(portfolio.positions)
    if success:
        print(f"✅ {len(portfolio.positions)} positions saved successfully")
    else:
        print("❌ Failed to save positions")
    
    # 5. Get Database Statistics
    print("\n5. Database statistics:")
    stats = data_persistence.get_database_stats()
    if "error" not in stats:
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print(f"   Error: {stats['error']}")
    
    # 6. Retrieve Portfolio History
    print("\n6. Portfolio history:")
    history = data_persistence.get_portfolio_history(days=1)
    print(f"   Found {len(history)} portfolio snapshots")
    if history:
        latest = history[0]
        print(f"   Latest: {latest['date']} - ${latest['total_value']:,.2f}")
    
    # 7. Performance Metrics
    print("\n7. Performance metrics:")
    performance = data_persistence.get_portfolio_performance(days=1)
    if "error" not in performance:
        print(f"   Period: {performance.get('period_days', 0)} days")
        print(f"   Data points: {performance.get('data_points', 0)}")
        if performance.get('data_points', 0) >= 2:
            print(f"   Total return: ${performance.get('total_return', 0):,.2f}")
            print(f"   Return %: {performance.get('total_return_percentage', 0):.2f}%")
    else:
        print(f"   Error: {performance['error']}")
    
    print("\n" + "=" * 55)
    print("✅ Data persistence demo completed successfully!")
    print("\nKey features demonstrated:")
    print("• Portfolio snapshots are automatically saved")
    print("• Historical data is tracked in SQLite database")
    print("• Performance metrics can be calculated")
    print("• Database location: data/degiro_trading.db")
    print("\nNow when you fetch real portfolio data, it will be")
    print("automatically saved and you can track changes over time!")
    
    return True


if __name__ == "__main__":
    success = demo_data_persistence()
    sys.exit(0 if success else 1)