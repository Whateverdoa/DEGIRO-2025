from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class ProductInfo:
    """Product/instrument information"""
    id: str
    name: str = ""
    symbol: str = ""
    isin: str = ""
    currency: str = ""
    exchange: str = ""
    product_type: str = ""
    
@dataclass
class Position:
    """Represents a single portfolio position"""
    id: str
    position_type: str  # 'PRODUCT' or 'CASH'
    size: float
    price: float
    value: float
    pl_base: Dict[str, float]  # Profit/Loss in base currency
    today_pl_base: Dict[str, float]
    break_even_price: float
    realized_product_pl: float
    realized_fx_pl: float
    currency: str = "EUR"
    product_info: Optional[ProductInfo] = None
    
    @property
    def is_active(self) -> bool:
        """Returns True if position has non-zero size"""
        return self.size != 0
    
    @property
    def total_pl(self) -> float:
        """Returns total P&L in EUR"""
        return sum(self.pl_base.values()) if self.pl_base else 0
    
    @property
    def today_pl(self) -> float:
        """Returns today's P&L in EUR"""
        return sum(self.today_pl_base.values()) if self.today_pl_base else 0

@dataclass
class PortfolioSummary:
    """Portfolio summary information"""
    total_cash: float
    degiro_cash: float
    flatex_cash: float
    total_deposits: float
    today_deposits: float
    total_fees: float
    cash_compensation: float
    free_space_eur: float
    free_space_usd: float

class DegiroPortfolioParser:
    """Parser for DEGIRO API portfolio responses"""
    
    def __init__(self, api_response: Dict[str, Any], api_client=None):
        self.response = api_response
        self.api_client = api_client
        self._product_cache = {}  # Cache for product info
    
    def get_product_ids(self) -> List[str]:
        """Extract all product IDs from active positions"""
        positions = self.get_all_positions()
        return [pos.id for pos in positions 
               if pos.position_type == 'PRODUCT' and pos.is_active]
    
    def fetch_product_info(self, product_ids: List[str]) -> Dict[str, ProductInfo]:
        """Fetch product information for given IDs"""
        if not self.api_client:
            print("Warning: No API client provided. Cannot fetch product info.")
            return {}
        
        if not product_ids:
            return {}
        
        try:
            # Try to get product info using get_products_info
            products_response = self.api_client.get_products_info(
                products_list=product_ids
            )
            
            product_info = {}
            
            # Parse the response structure
            if isinstance(products_response, dict) and 'data' in products_response:
                for product_id, product_data in products_response['data'].items():
                    product_info[product_id] = ProductInfo(
                        id=product_id,
                        name=product_data.get('name', ''),
                        symbol=product_data.get('symbol', ''),
                        isin=product_data.get('isin', ''),
                        currency=product_data.get('currency', ''),
                        exchange=product_data.get('exchangeId', ''),
                        product_type=product_data.get('productType', '')
                    )
            
            self._product_cache.update(product_info)
            return product_info
            
        except Exception as e:
            print(f"Error fetching product info: {e}")
            return {}
    
    def enrich_positions_with_product_info(self):
        """Fetch and attach product information to positions"""
        product_ids = self.get_product_ids()
        product_info = self.fetch_product_info(product_ids)
        
        positions = self.get_all_positions()
        for pos in positions:
            if pos.id in product_info:
                pos.product_info = product_info[pos.id]
    
    def parse_position_row(self, position_data: Dict[str, Any]) -> Position:
        """Parse a single position row into Position object"""
        position_id = position_data.get('id', '')
        
        # Extract values from the nested structure
        values = {item['name']: item.get('value') for item in position_data.get('value', [])}
        
        return Position(
            id=position_id,
            position_type=values.get('positionType', ''),
            size=values.get('size', 0),
            price=values.get('price', 0),
            value=values.get('value', 0),
            pl_base=values.get('plBase', {}),
            today_pl_base=values.get('todayPlBase', {}),
            break_even_price=values.get('breakEvenPrice', 0),
            realized_product_pl=values.get('realizedProductPl', 0),
            realized_fx_pl=values.get('realizedFxPl', 0)
        )
    
    def get_all_positions(self) -> List[Position]:
        """Extract all positions from portfolio data"""
        positions = []
        
        portfolio_data = self.response.get('portfolio', {})
        if isinstance(portfolio_data, dict) and 'value' in portfolio_data:
            for item in portfolio_data['value']:
                if item.get('name') == 'positionrow':
                    positions.append(self.parse_position_row(item))
        
        return positions
    
    def get_active_positions(self) -> List[Position]:
        """Get only positions with non-zero size"""
        return [pos for pos in self.get_all_positions() if pos.is_active]
    
    def get_product_positions(self) -> List[Position]:
        """Get only PRODUCT type positions (securities, not cash)"""
        return [pos for pos in self.get_all_positions() if pos.position_type == 'PRODUCT']
    
    def get_cash_positions(self) -> List[Position]:
        """Get only CASH type positions"""
        return [pos for pos in self.get_all_positions() if pos.position_type == 'CASH']
    
    def get_portfolio_summary(self) -> PortfolioSummary:
        """Extract total portfolio summary"""
        total_portfolio = self.response.get('totalPortfolio', {})
        
        # Parse the nested value structure
        values = {}
        if 'value' in total_portfolio:
            for item in total_portfolio['value']:
                values[item['name']] = item.get('value')
        
        free_space = values.get('freeSpaceNew', {})
        
        return PortfolioSummary(
            total_cash=values.get('totalCash', 0),
            degiro_cash=values.get('degiroCash', 0),
            flatex_cash=values.get('flatexCash', 0),
            total_deposits=values.get('totalDepositWithdrawal', 0),
            today_deposits=values.get('todayDepositWithdrawal', 0),
            total_fees=values.get('totalNonProductFees', 0),
            cash_compensation=values.get('cashFundCompensation', 0),
            free_space_eur=free_space.get('EUR', 0) if isinstance(free_space, dict) else 0,
            free_space_usd=free_space.get('USD', 0) if isinstance(free_space, dict) else 0
        )
    
    def get_total_portfolio_value(self) -> float:
        """Calculate total portfolio value (cash + securities)"""
        summary = self.get_portfolio_summary()
        active_positions = self.get_active_positions()
        
        securities_value = sum(pos.value for pos in active_positions if pos.position_type == 'PRODUCT')
        return summary.total_cash + securities_value
    
    def get_total_unrealized_pl(self) -> float:
        """Calculate total unrealized P&L"""
        active_positions = self.get_active_positions()
        return sum(pos.total_pl for pos in active_positions if pos.position_type == 'PRODUCT')
    
    def get_total_realized_pl(self) -> float:
        """Calculate total realized P&L"""
        all_positions = self.get_all_positions()
        return sum(pos.realized_product_pl + pos.realized_fx_pl for pos in all_positions)
    
    def print_portfolio_summary(self):
        """Print a formatted portfolio summary"""
        summary = self.get_portfolio_summary()
        active_positions = self.get_active_positions()
        product_positions = [p for p in active_positions if p.position_type == 'PRODUCT']
        
        print("=== PORTFOLIO SUMMARY ===")
        print(f"Total Cash: €{summary.total_cash:,.2f}")
        print(f"Active Securities: {len(product_positions)}")
        print(f"Total Securities Value: €{sum(p.value for p in product_positions):,.2f}")
        print(f"Total Portfolio Value: €{self.get_total_portfolio_value():,.2f}")
        print(f"Total Unrealized P&L: €{self.get_total_unrealized_pl():,.2f}")
        print(f"Total Realized P&L: €{self.get_total_realized_pl():,.2f}")
        print(f"Available Trading Space: €{summary.free_space_eur:,.2f}")
        
        print("\n=== ACTIVE POSITIONS ===")
        for pos in product_positions:
            if pos.product_info:
                product_name = f"{pos.product_info.name} ({pos.product_info.symbol})"
                if pos.product_info.isin:
                    product_name += f" [ISIN: {pos.product_info.isin}]"
            else:
                product_name = f"Product ID: {pos.id}"
            
            print(f"{product_name}: {pos.size} @ €{pos.price} = €{pos.value} (P&L: €{pos.total_pl:,.2f})")

# Example usage function
def analyze_degiro_portfolio(api_response: Dict[str, Any], api_client=None):
    """Main function to analyze DEGIRO portfolio data"""
    parser = DegiroPortfolioParser(api_response, api_client)
    
    # Enrich positions with product information if API client is available
    if api_client:
        print("Fetching product information...")
        parser.enrich_positions_with_product_info()
    
    # Print summary
    parser.print_portfolio_summary()
    
    # Get specific data
    active_positions = parser.get_active_positions()
    summary = parser.get_portfolio_summary()
    
    return {
        'parser': parser,
        'active_positions': active_positions,
        'summary': summary,
        'total_value': parser.get_total_portfolio_value(),
        'unrealized_pl': parser.get_total_unrealized_pl(),
        'realized_pl': parser.get_total_realized_pl()
    }

# For integration with your existing code:
def parse_degiro_update_response(update_response, api_client=None):
    """
    Parse the response from api.get_update() call
    
    Args:
        update_response: The response from your DEGIRO API get_update call
        api_client: The connected DEGIRO API client for fetching product info
    
    Returns:
        Parsed portfolio data with product information
    """
    return analyze_degiro_portfolio(update_response, api_client)