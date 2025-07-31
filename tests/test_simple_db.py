#!/usr/bin/env python3
"""Simple test to check database functionality."""

from core.database import init_database, db_manager

def test_simple_db():
    print("Testing database initialization...")
    
    # Initialize database
    success = init_database(create_tables=True)
    print(f"Database init: {'✅' if success else '❌'}")
    
    if success:
        # Test health
        health = db_manager.health_check()
        print(f"Health check: {'✅' if health else '❌'}")
        
        # Get stats
        stats = db_manager.get_stats()
        print(f"Stats: {stats}")
        
        return True
    return False

if __name__ == "__main__":
    test_simple_db()