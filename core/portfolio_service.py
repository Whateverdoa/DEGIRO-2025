"""Portfolio monitoring service for DEGIRO trading agent."""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from core.logging_config import get_logger
from core.models import Portfolio, Position, Product, ProductType
from core.degiro_api import degiro_api
from core.config import config_manager
from core.database import init_database
from core.data_persistence import data_persistence
import pandas as pd


logger = get_logger("portfolio_service")


class PortfolioService:
    """Service for fetching and analyzing portfolio data."""
    
    def __init__(self):
        self.api = degiro_api
        self._portfolio_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 60  # Cache for 60 seconds
        self._database_initialized = False
        
    def get_portfolio(self, force_refresh: bool = False) -> Optional[Portfolio]:
        """
        Get current portfolio with positions and values.
        
        Args:
            force_refresh: Force API call even if cache is valid
            
        Returns:
            Portfolio object or None if error
        """
        try:
            # Check cache
            if not force_refresh and self._is_cache_valid():
                logger.debug("Returning cached portfolio data")
                return self._portfolio_cache
            
            # Ensure connected
            if not self.api.is_connected:
                logger.warning("Not connected to DEGIRO")
                if not self.api.connect():
                    logger.error("Failed to connect to DEGIRO")
                    return None
            
            # Get raw portfolio data from API
            logger.info("Fetching portfolio from DEGIRO...")
            raw_data = self._fetch_portfolio_data()
            
            if not raw_data:
                logger.error("Failed to fetch portfolio data")
                return None
            
            # Convert to Portfolio model
            portfolio = self._process_portfolio_data(raw_data)
            
            # Update cache
            self._portfolio_cache = portfolio
            self._cache_timestamp = datetime.now()
            
            # Save to database
            self._save_portfolio_to_database(portfolio)
            
            logger.info(f"Portfolio updated: {len(portfolio.positions)} positions, "
                       f"total value: {portfolio.total_value:.2f} {portfolio.currency}")
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if portfolio cache is still valid."""
        if not self._portfolio_cache or not self._cache_timestamp:
            return False
        
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self._cache_ttl
    
    def _fetch_portfolio_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch raw portfolio data from DEGIRO API.
        
        Returns:
            Raw portfolio data or None if error
        """
        try:
            # Get portfolio data from DEGIRO API
            logger.info("Fetching real portfolio data from DEGIRO API")
            portfolio_data = self.api.get_portfolio()
            
            if not portfolio_data:
                logger.warning("No portfolio data returned from API")
                return None
            
            # The DEGIRO API wrapper already returns processed data
            # We need to adapt it to match our expected format
            return {
                "positions": portfolio_data.get("positions", []),
                "totalPortfolio": {
                    "totalValue": portfolio_data.get("total_value", 0),
                    "totalCash": portfolio_data.get("cash", 0),
                    "degiroCash": portfolio_data.get("cash", 0),
                    "flatexCash": 0,
                    "totalDepositWithdrawal": 0,  # Not available in current API response
                    "reportOverallGainloss": 0,  # Will need to calculate this
                    "reportTodayGainloss": 0,  # Not available in current API response
                    "reportCreationTime": portfolio_data.get("timestamp", datetime.now().isoformat()),
                    "reportPortfolioValue": portfolio_data.get("total_value", 0),
                    "reportCash": portfolio_data.get("cash", 0),
                    "reportNetliq": portfolio_data.get("total_value", 0),
                    "reportFreeRemainingFunds": portfolio_data.get("cash", 0),
                    "reportMarginCallStatus": "NO_MARGIN_CALL",
                    "currency": "EUR"  # DEGIRO base currency
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching portfolio data: {e}")
            return None
    
    def _process_portfolio_data(self, raw_data: Dict[str, Any]) -> Portfolio:
        """
        Process raw portfolio data into Portfolio model.
        
        Args:
            raw_data: Raw data from DEGIRO API
            
        Returns:
            Portfolio object
        """
        positions = []
        total_portfolio = raw_data.get("totalPortfolio", {})
        
        # Process positions
        for pos_data in raw_data.get("positions", []):
            # The position data structure from our API wrapper
            product_info = pos_data.get("product_info", {})
            
            # Create Product if we have product info
            if product_info:
                product = Product(
                    id=str(pos_data.get("product_id", "")),
                    symbol=product_info.get("symbol", ""),
                    name=product_info.get("name", ""),
                    isin=product_info.get("isin"),
                    product_type=self._map_product_type(product_info.get("productType", "")),
                    currency=product_info.get("currency", "EUR"),
                    exchange_id=product_info.get("exchangeId"),
                    close_price=product_info.get("closePrice", pos_data.get("price", 0))
                )
            else:
                # Create minimal product with just ID
                product = Product(
                    id=str(pos_data.get("product_id", "")),
                    symbol=f"ID:{pos_data.get('product_id', 'UNKNOWN')}",
                    name="Unknown Product",
                    product_type=ProductType.STOCK,
                    currency="EUR"
                )
            
            # Extract position data
            size = float(pos_data.get("size", 0))
            current_price = float(pos_data.get("price", 0))
            value = float(pos_data.get("value", 0))
            
            # Calculate average price from value if not provided
            average_price = (value / size) if size > 0 and value > 0 else current_price
            
            # Calculate unrealized P&L
            unrealized_pnl = (current_price - average_price) * size if size > 0 else 0
            
            # Create Position
            position = Position(
                product_id=product.id,
                product=product,
                size=size,
                average_price=average_price,
                current_price=current_price,
                value=value,
                unrealized_pnl=unrealized_pnl,
                currency=product.currency
            )
            
            positions.append(position)
        
        # Create Portfolio
        total_value = float(total_portfolio.get("totalValue", 0))
        cash_balance = float(total_portfolio.get("totalCash", 0))
        total_deposit = float(total_portfolio.get("totalDepositWithdrawal", 0))
        total_pnl = float(total_portfolio.get("reportOverallGainloss", 0))
        
        portfolio = Portfolio(
            positions=positions,
            total_value=total_value,
            cash_balance=cash_balance,
            total_invested=total_deposit,
            total_pnl=total_pnl,
            total_pnl_percentage=(total_pnl / total_deposit * 100) if total_deposit > 0 else 0,
            currency="EUR"  # DEGIRO base currency
        )
        
        return portfolio
    
    def _map_product_type(self, degiro_type: str) -> ProductType:
        """Map DEGIRO product type to our ProductType enum."""
        mapping = {
            "STOCK": ProductType.STOCK,
            "ETF": ProductType.ETF,
            "BOND": ProductType.BOND,
            "OPTION": ProductType.OPTION,
            "FUTURE": ProductType.FUTURE,
            "CFD": ProductType.CFD,
            "WARRANT": ProductType.OPTION,
            "STRUCTURED_PRODUCT": ProductType.OPTION,
            "INVESTMENT_FUND": ProductType.ETF
        }
        return mapping.get(degiro_type.upper(), ProductType.STOCK)
    
    def get_portfolio_analytics(self, portfolio: Optional[Portfolio] = None) -> Dict[str, Any]:
        """
        Get detailed portfolio analytics.
        
        Args:
            portfolio: Portfolio to analyze (fetches if not provided)
            
        Returns:
            Dictionary with analytics data
        """
        if not portfolio:
            portfolio = self.get_portfolio()
            
        if not portfolio:
            return {}
        
        analytics = {
            "summary": {
                "total_value": portfolio.total_value,
                "cash_balance": portfolio.cash_balance,
                "invested_value": portfolio.total_value - portfolio.cash_balance,
                "total_pnl": portfolio.total_pnl,
                "total_pnl_percentage": portfolio.total_pnl_percentage,
                "number_of_positions": len(portfolio.positions),
                "currency": portfolio.currency
            },
            "positions_by_type": {},
            "positions_by_currency": {},
            "top_gainers": [],
            "top_losers": [],
            "concentration": [],
            "risk_metrics": {}
        }
        
        # Analyze positions
        if portfolio.positions:
            # Group by product type
            type_groups = {}
            currency_groups = {}
            
            for position in portfolio.positions:
                # By type
                ptype = position.product.product_type if position.product else "UNKNOWN"
                if ptype not in type_groups:
                    type_groups[ptype] = {"count": 0, "value": 0, "pnl": 0}
                type_groups[ptype]["count"] += 1
                type_groups[ptype]["value"] += position.value or 0
                type_groups[ptype]["pnl"] += position.unrealized_pnl or 0
                
                # By currency
                currency = position.currency
                if currency not in currency_groups:
                    currency_groups[currency] = {"count": 0, "value": 0, "pnl": 0}
                currency_groups[currency]["count"] += 1
                currency_groups[currency]["value"] += position.value or 0
                currency_groups[currency]["pnl"] += position.unrealized_pnl or 0
            
            analytics["positions_by_type"] = type_groups
            analytics["positions_by_currency"] = currency_groups
            
            # Sort positions by P&L
            sorted_positions = sorted(
                portfolio.positions, 
                key=lambda p: p.unrealized_pnl or 0, 
                reverse=True
            )
            
            # Top gainers
            analytics["top_gainers"] = [
                {
                    "symbol": p.product.symbol if p.product else p.product_id,
                    "name": p.product.name if p.product else "Unknown",
                    "pnl": p.unrealized_pnl or 0,
                    "pnl_percentage": p.pnl_percentage or 0,
                    "value": p.value or 0
                }
                for p in sorted_positions[:5] if (p.unrealized_pnl or 0) > 0
            ]
            
            # Top losers
            analytics["top_losers"] = [
                {
                    "symbol": p.product.symbol if p.product else p.product_id,
                    "name": p.product.name if p.product else "Unknown",
                    "pnl": p.unrealized_pnl or 0,
                    "pnl_percentage": p.pnl_percentage or 0,
                    "value": p.value or 0
                }
                for p in sorted_positions[-5:] if (p.unrealized_pnl or 0) < 0
            ]
            
            # Concentration (top 5 positions by value)
            sorted_by_value = sorted(
                portfolio.positions,
                key=lambda p: p.value or 0,
                reverse=True
            )
            
            analytics["concentration"] = [
                {
                    "symbol": p.product.symbol if p.product else p.product_id,
                    "name": p.product.name if p.product else "Unknown",
                    "value": p.value or 0,
                    "percentage": ((p.value or 0) / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
                }
                for p in sorted_by_value[:5]
            ]
            
        return analytics
    
    def export_portfolio(self, portfolio: Optional[Portfolio] = None, format: str = "json") -> str:
        """
        Export portfolio data in various formats.
        
        Args:
            portfolio: Portfolio to export (fetches if not provided)
            format: Export format (json, csv, html)
            
        Returns:
            Exported data as string
        """
        if not portfolio:
            portfolio = self.get_portfolio()
            
        if not portfolio:
            return ""
        
        if format == "json":
            return portfolio.model_dump_json(indent=2)
        
        elif format == "csv":
            # Convert to DataFrame
            positions_data = []
            for position in portfolio.positions:
                positions_data.append({
                    "Symbol": position.product.symbol if position.product else position.product_id,
                    "Name": position.product.name if position.product else "Unknown",
                    "Type": position.product.product_type if position.product else "Unknown",
                    "Quantity": position.size,
                    "Avg Price": position.average_price,
                    "Current Price": position.current_price,
                    "Value": position.value,
                    "P&L": position.unrealized_pnl,
                    "P&L %": position.pnl_percentage,
                    "Currency": position.currency
                })
            
            df = pd.DataFrame(positions_data)
            return df.to_csv(index=False)
        
        elif format == "html":
            # Create HTML report
            analytics = self.get_portfolio_analytics(portfolio)
            
            html = f"""
            <html>
            <head>
                <title>Portfolio Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .positive {{ color: green; }}
                    .negative {{ color: red; }}
                    .summary {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>Portfolio Report</h1>
                <div class="summary">
                    <h2>Summary</h2>
                    <p>Total Value: {portfolio.currency} {portfolio.total_value:,.2f}</p>
                    <p>Cash Balance: {portfolio.currency} {portfolio.cash_balance:,.2f}</p>
                    <p>Total P&L: <span class="{'positive' if portfolio.total_pnl >= 0 else 'negative'}">{portfolio.currency} {portfolio.total_pnl:,.2f} ({portfolio.total_pnl_percentage:.2f}%)</span></p>
                    <p>Number of Positions: {len(portfolio.positions)}</p>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <h2>Positions</h2>
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Quantity</th>
                        <th>Avg Price</th>
                        <th>Current Price</th>
                        <th>Value</th>
                        <th>P&L</th>
                        <th>P&L %</th>
                    </tr>
            """
            
            for position in portfolio.positions:
                pnl_class = 'positive' if (position.unrealized_pnl or 0) >= 0 else 'negative'
                html += f"""
                    <tr>
                        <td>{position.product.symbol if position.product else position.product_id}</td>
                        <td>{position.product.name if position.product else 'Unknown'}</td>
                        <td>{position.product.product_type if position.product else 'Unknown'}</td>
                        <td>{position.size}</td>
                        <td>{position.average_price:.2f}</td>
                        <td>{position.current_price or 0:.2f}</td>
                        <td>{position.value or 0:,.2f}</td>
                        <td class="{pnl_class}">{position.unrealized_pnl or 0:,.2f}</td>
                        <td class="{pnl_class}">{position.pnl_percentage or 0:.2f}%</td>
                    </tr>
                """
            
            html += """
                </table>
            </body>
            </html>
            """
            
            return html
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _ensure_database_initialized(self):
        """Ensure database is initialized for data persistence."""
        if not self._database_initialized:
            try:
                success = init_database(create_tables=True)
                if success:
                    self._database_initialized = True
                    logger.info("Database initialized successfully for portfolio persistence")
                else:
                    logger.warning("Failed to initialize database - data will not be persisted")
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
    
    def _save_portfolio_to_database(self, portfolio: Portfolio):
        """Save portfolio snapshot to database."""
        try:
            self._ensure_database_initialized()
            
            if self._database_initialized:
                success = data_persistence.save_portfolio_snapshot(portfolio)
                if success:
                    logger.debug("Portfolio snapshot saved to database")
                else:
                    logger.warning("Failed to save portfolio snapshot to database")
            
        except Exception as e:
            logger.error(f"Error saving portfolio to database: {e}")
    
    def get_portfolio_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get portfolio history from database."""
        try:
            self._ensure_database_initialized()
            
            if self._database_initialized:
                return data_persistence.get_portfolio_history(days)
            else:
                logger.warning("Database not available - cannot retrieve portfolio history")
                return []
                
        except Exception as e:
            logger.error(f"Error getting portfolio history: {e}")
            return []
    
    def get_portfolio_performance(self, days: int = 30) -> Dict[str, Any]:
        """Get portfolio performance metrics from database."""
        try:
            self._ensure_database_initialized()
            
            if self._database_initialized:
                return data_persistence.get_portfolio_performance(days)
            else:
                logger.warning("Database not available - cannot calculate performance metrics")
                return {"error": "Database not available"}
                
        except Exception as e:
            logger.error(f"Error getting portfolio performance: {e}")
            return {"error": str(e)}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring."""
        try:
            self._ensure_database_initialized()
            
            if self._database_initialized:
                return data_persistence.get_database_stats()
            else:
                return {"error": "Database not initialized"}
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}


# Global portfolio service instance
portfolio_service = PortfolioService()