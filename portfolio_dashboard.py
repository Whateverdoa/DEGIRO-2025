#!/usr/bin/env python3
"""Portfolio monitoring dashboard CLI."""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import colorama
from colorama import Fore, Style

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
from core.session_manager import session_manager
from core.database import init_database

# Initialize colorama for cross-platform colored output
colorama.init()

# Setup logging
import logging
setup_logging(log_level='WARNING')  # Keep it quiet for CLI
logger = logging.getLogger(__name__)


def format_currency(value: float, currency: str = "EUR") -> str:
    """Format currency value with color."""
    if value > 0:
        return f"{Fore.GREEN}{currency} {value:,.2f}{Style.RESET_ALL}"
    elif value < 0:
        return f"{Fore.RED}{currency} {value:,.2f}{Style.RESET_ALL}"
    else:
        return f"{currency} {value:,.2f}"


def format_percentage(value: float) -> str:
    """Format percentage with color."""
    if value > 0:
        return f"{Fore.GREEN}+{value:.2f}%{Style.RESET_ALL}"
    elif value < 0:
        return f"{Fore.RED}{value:.2f}%{Style.RESET_ALL}"
    else:
        return f"{value:.2f}%"


def display_portfolio_summary(portfolio):
    """Display portfolio summary."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}PORTFOLIO SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    print(f"Total Value:    {format_currency(portfolio.total_value, portfolio.currency)}")
    print(f"Cash Balance:   {format_currency(portfolio.cash_balance, portfolio.currency)}")
    print(f"Invested:       {format_currency(portfolio.total_value - portfolio.cash_balance, portfolio.currency)}")
    print(f"Total P&L:      {format_currency(portfolio.total_pnl, portfolio.currency)} ({format_percentage(portfolio.total_pnl_percentage)})")
    print(f"Positions:      {len(portfolio.positions)}")
    print(f"Last Update:    {portfolio.last_update.strftime('%Y-%m-%d %H:%M:%S')}")


def display_positions(portfolio):
    """Display portfolio positions as a table."""
    print(f"\n{Fore.CYAN}POSITIONS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*60}{Style.RESET_ALL}")
    
    if not portfolio.positions:
        print("No positions found.")
        return
    
    # Prepare data for table
    table_data = []
    for pos in portfolio.positions:
        symbol = pos.product.symbol if pos.product else pos.product_id
        name = pos.product.name if pos.product else "Unknown"
        # Truncate name if too long
        if len(name) > 30:
            name = name[:27] + "..."
        
        pnl_str = f"{pos.unrealized_pnl or 0:.2f}"
        pnl_pct_str = f"{pos.pnl_percentage or 0:.2f}%"
        
        # Color P&L
        if (pos.unrealized_pnl or 0) > 0:
            pnl_str = f"{Fore.GREEN}+{pnl_str}{Style.RESET_ALL}"
            pnl_pct_str = f"{Fore.GREEN}+{pnl_pct_str}{Style.RESET_ALL}"
        elif (pos.unrealized_pnl or 0) < 0:
            pnl_str = f"{Fore.RED}{pnl_str}{Style.RESET_ALL}"
            pnl_pct_str = f"{Fore.RED}{pnl_pct_str}{Style.RESET_ALL}"
        
        table_data.append([
            symbol,
            name,
            f"{pos.size:.2f}",
            f"{pos.average_price:.2f}",
            f"{pos.current_price or 0:.2f}",
            f"{pos.value or 0:,.2f}",
            pnl_str,
            pnl_pct_str
        ])
    
    headers = ["Symbol", "Name", "Qty", "Avg Price", "Current", "Value", "P&L", "P&L %"]
    print(tabulate(table_data, headers=headers, tablefmt="simple"))


def display_analytics(portfolio):
    """Display portfolio analytics."""
    analytics = portfolio_service.get_portfolio_analytics(portfolio)
    
    # Top gainers
    print(f"\n{Fore.GREEN}TOP GAINERS{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'-'*30}{Style.RESET_ALL}")
    for gainer in analytics.get("top_gainers", [])[:3]:
        print(f"{gainer['symbol']:<10} {Fore.GREEN}+{gainer['pnl']:.2f} (+{gainer['pnl_percentage']:.2f}%){Style.RESET_ALL}")
    
    # Top losers
    print(f"\n{Fore.RED}TOP LOSERS{Style.RESET_ALL}")
    print(f"{Fore.RED}{'-'*30}{Style.RESET_ALL}")
    for loser in analytics.get("top_losers", [])[:3]:
        print(f"{loser['symbol']:<10} {Fore.RED}{loser['pnl']:.2f} ({loser['pnl_percentage']:.2f}%){Style.RESET_ALL}")
    
    # Concentration
    print(f"\n{Fore.YELLOW}TOP HOLDINGS (CONCENTRATION){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'-'*30}{Style.RESET_ALL}")
    for holding in analytics.get("concentration", [])[:5]:
        print(f"{holding['symbol']:<10} {holding['percentage']:.1f}% of portfolio")
    
    # By type
    print(f"\n{Fore.CYAN}ALLOCATION BY TYPE{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*30}{Style.RESET_ALL}")
    for ptype, data in analytics.get("positions_by_type", {}).items():
        print(f"{ptype:<10} {data['count']} positions, {data['value']:,.2f}")


def live_monitor(refresh_interval: int = 30):
    """Live portfolio monitoring mode."""
    print(f"{Fore.CYAN}Starting live portfolio monitoring...{Style.RESET_ALL}")
    print(f"Refresh interval: {refresh_interval} seconds")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Clear screen (cross-platform)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Get portfolio
            portfolio = portfolio_service.get_portfolio(force_refresh=True)
            
            if portfolio:
                # Display header
                print(f"{Fore.YELLOW}DEGIRO Portfolio Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
                
                # Display portfolio
                display_portfolio_summary(portfolio)
                display_positions(portfolio)
                display_analytics(portfolio)
                
                # Status
                print(f"\n{Fore.CYAN}Status: Connected | Next refresh in {refresh_interval}s{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Failed to fetch portfolio data{Style.RESET_ALL}")
            
            # Wait for next refresh
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping portfolio monitor...{Style.RESET_ALL}")


def export_portfolio(format: str, output_file: str = None):
    """Export portfolio to file."""
    portfolio = portfolio_service.get_portfolio()
    
    if not portfolio:
        print(f"{Fore.RED}Failed to fetch portfolio{Style.RESET_ALL}")
        return
    
    # Export
    exported_data = portfolio_service.export_portfolio(portfolio, format=format)
    
    # Determine output file
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"portfolio_{timestamp}.{format}"
    
    # Save to file
    Path(output_file).write_text(exported_data)
    print(f"{Fore.GREEN}Portfolio exported to: {output_file}{Style.RESET_ALL}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="DEGIRO Portfolio Monitoring Dashboard")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show portfolio snapshot')
    show_parser.add_argument('-a', '--analytics', action='store_true', help='Include analytics')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Live portfolio monitoring')
    monitor_parser.add_argument('-r', '--refresh', type=int, default=30, help='Refresh interval in seconds')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export portfolio')
    export_parser.add_argument('format', choices=['json', 'csv', 'html'], help='Export format')
    export_parser.add_argument('-o', '--output', help='Output file path')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show portfolio history and performance')
    history_parser.add_argument('-d', '--days', type=int, default=30, help='Number of days to show (default: 30)')
    history_parser.add_argument('-p', '--performance', action='store_true', help='Show performance metrics')
    
    # Database command
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_parser.add_argument('--stats', action='store_true', help='Show database statistics')
    db_parser.add_argument('--init', action='store_true', help='Initialize database')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Connect to DEGIRO
    print(f"{Fore.CYAN}Connecting to DEGIRO...{Style.RESET_ALL}")
    if not degiro_api.is_connected:
        if not degiro_api.connect():
            print(f"{Fore.RED}Failed to connect to DEGIRO{Style.RESET_ALL}")
            sys.exit(1)
    
    try:
        if args.command == 'show':
            # Show portfolio snapshot
            portfolio = portfolio_service.get_portfolio()
            if portfolio:
                display_portfolio_summary(portfolio)
                display_positions(portfolio)
                if args.analytics:
                    display_analytics(portfolio)
            else:
                print(f"{Fore.RED}Failed to fetch portfolio{Style.RESET_ALL}")
        
        elif args.command == 'monitor':
            # Live monitoring
            live_monitor(args.refresh)
        
        elif args.command == 'export':
            # Export portfolio
            export_portfolio(args.format, args.output)
        
        elif args.command == 'history':
            # Show portfolio history
            display_portfolio_history(args.days, args.performance)
        
        elif args.command == 'db':
            # Database operations
            handle_database_command(args)
        
        else:
            # Default: show portfolio
            portfolio = portfolio_service.get_portfolio()
            if portfolio:
                display_portfolio_summary(portfolio)
                display_positions(portfolio)
            else:
                print(f"{Fore.RED}Failed to fetch portfolio{Style.RESET_ALL}")
    
    finally:
        # Disconnect
        degiro_api.disconnect()
        print(f"\n{Fore.CYAN}Disconnected from DEGIRO{Style.RESET_ALL}")


def display_portfolio_history(days: int, show_performance: bool = False):
    """Display portfolio history."""
    print(f"\n{Fore.CYAN}=== Portfolio History ({days} days) ==={Style.RESET_ALL}")
    
    # Get history
    history = portfolio_service.get_portfolio_history(days)
    
    if not history:
        print(f"{Fore.YELLOW}No portfolio history found. Start using the system to build history.{Style.RESET_ALL}")
        return
    
    # Display history table
    table_data = []
    for snapshot in history[-10:]:  # Show last 10 snapshots
        date = datetime.fromisoformat(snapshot['date']).strftime('%Y-%m-%d %H:%M')
        table_data.append([
            date,
            f"{snapshot['currency']} {snapshot['total_value']:,.2f}",
            f"{snapshot['currency']} {snapshot['cash_balance']:,.2f}",
            f"{snapshot['total_pnl']:+.2f}",
            f"{snapshot['total_pnl_percentage']:+.2f}%",
            snapshot['positions_count']
        ])
    
    headers = ["Date", "Total Value", "Cash", "P&L", "P&L %", "Positions"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    if show_performance:
        print(f"\n{Fore.CYAN}=== Performance Metrics ==={Style.RESET_ALL}")
        performance = portfolio_service.get_portfolio_performance(days)
        
        if "error" not in performance:
            print(f"Period: {performance['period_days']} days")
            print(f"Data points: {performance['data_points']}")
            print(f"Start value: {format_currency(performance['start_value'], 'EUR')}")
            print(f"End value: {format_currency(performance['end_value'], 'EUR')}")
            print(f"Total return: {format_currency(performance['total_return'], 'EUR')}")
            print(f"Total return %: {format_percentage(performance['total_return_percentage'])}")
            print(f"Daily avg return: {format_percentage(performance['daily_avg_return'])}")
            print(f"Volatility: {performance['volatility']:.2f}%")
        else:
            print(f"{Fore.RED}Error: {performance['error']}{Style.RESET_ALL}")


def handle_database_command(args):
    """Handle database-related commands."""
    if args.stats:
        print(f"\n{Fore.CYAN}=== Database Statistics ==={Style.RESET_ALL}")
        stats = portfolio_service.get_database_stats()
        
        if "error" not in stats:
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print(f"{Fore.RED}Error: {stats['error']}{Style.RESET_ALL}")
    
    elif args.init:
        print(f"\n{Fore.CYAN}Initializing database...{Style.RESET_ALL}")
        success = init_database(create_tables=True)
        if success:
            print(f"{Fore.GREEN}✅ Database initialized successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to initialize database{Style.RESET_ALL}")
    
    else:
        print(f"{Fore.YELLOW}Use --stats to show database statistics or --init to initialize database{Style.RESET_ALL}")


if __name__ == "__main__":
    main()