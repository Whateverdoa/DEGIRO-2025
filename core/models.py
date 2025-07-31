"""Data models for DEGIRO trading agent."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func


# SQLAlchemy Base
Base = declarative_base()


# Enums
class OrderType(str, Enum):
    """Order types."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(str, Enum):
    """Order side (buy/sell)."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class TransactionType(str, Enum):
    """Transaction types."""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    FEE = "FEE"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class ProductType(str, Enum):
    """Product types."""
    STOCK = "STOCK"
    ETF = "ETF"
    BOND = "BOND"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    FOREX = "FOREX"
    CFD = "CFD"
    CRYPTO = "CRYPTO"


# Pydantic Models (for API responses and validation)
class Product(BaseModel):
    """Product/Security information."""
    id: str
    symbol: str
    name: str
    isin: Optional[str] = None
    product_type: ProductType
    currency: str
    exchange_id: Optional[str] = None
    close_price: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    last_update: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class Position(BaseModel):
    """Portfolio position."""
    product_id: str
    product: Optional[Product] = None
    size: float
    average_price: float
    current_price: Optional[float] = None
    value: Optional[float] = None
    realized_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None
    currency: str
    last_update: datetime = Field(default_factory=datetime.now)
    
    @field_validator('pnl_percentage')
    @classmethod
    def calculate_pnl_percentage(cls, v, values):
        if v is None and 'unrealized_pnl' in values and 'average_price' in values and 'size' in values:
            cost = values['average_price'] * values['size']
            if cost != 0:
                return (values['unrealized_pnl'] / cost) * 100
        return v


class Portfolio(BaseModel):
    """Portfolio summary."""
    positions: List[Position]
    total_value: float
    cash_balance: float
    total_invested: float
    total_pnl: float
    total_pnl_percentage: float
    currency: str
    last_update: datetime = Field(default_factory=datetime.now)
    
    @field_validator('total_pnl_percentage')
    @classmethod
    def calculate_total_pnl_percentage(cls, v, values):
        if v is None and 'total_pnl' in values and 'total_invested' in values:
            if values['total_invested'] != 0:
                return (values['total_pnl'] / values['total_invested']) * 100
        return v


class Order(BaseModel):
    """Order information."""
    id: Optional[str] = None
    product_id: str
    order_type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None  # For limit orders
    stop_price: Optional[float] = None  # For stop orders
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    executed_price: Optional[float] = None
    executed_quantity: Optional[float] = None
    fees: Optional[float] = None
    notes: Optional[str] = None
    
    class Config:
        use_enum_values = True


class Transaction(BaseModel):
    """Transaction record."""
    id: str
    product_id: str
    product: Optional[Product] = None
    transaction_type: TransactionType
    quantity: float
    price: float
    total_amount: float
    fees: Optional[float] = None
    currency: str
    executed_at: datetime
    order_id: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        use_enum_values = True


# SQLAlchemy Models (for database storage)
class DBProduct(Base):
    """Database model for products."""
    __tablename__ = 'products'
    
    id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    isin = Column(String, index=True)
    product_type = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    exchange_id = Column(String)
    last_close_price = Column(Float)
    last_update = Column(DateTime, default=func.now(), onupdate=func.now())
    metadata_json = Column(JSON)
    
    # Relationships
    positions = relationship("DBPosition", back_populates="product")
    transactions = relationship("DBTransaction", back_populates="product")


class DBPosition(Base):
    """Database model for positions."""
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False)
    size = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    product = relationship("DBProduct", back_populates="positions")


class DBOrder(Base):
    """Database model for orders."""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    degiro_order_id = Column(String, unique=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False)
    order_type = Column(String, nullable=False)
    side = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float)
    stop_price = Column(Float)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    executed_at = Column(DateTime)
    executed_price = Column(Float)
    executed_quantity = Column(Float)
    fees = Column(Float)
    notes = Column(String)
    metadata_json = Column(JSON)


class DBTransaction(Base):
    """Database model for transactions."""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    degiro_transaction_id = Column(String, unique=True)
    product_id = Column(String, ForeignKey('products.id'), nullable=False)
    transaction_type = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float)
    currency = Column(String, nullable=False)
    executed_at = Column(DateTime, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    notes = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    product = relationship("DBProduct", back_populates="transactions")


class DBPortfolioSnapshot(Base):
    """Database model for portfolio snapshots."""
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)
    total_invested = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    total_pnl_percentage = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    positions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())


# Model conversion utilities
def product_to_db(product: Product) -> DBProduct:
    """Convert Pydantic Product to SQLAlchemy model."""
    return DBProduct(
        id=product.id,
        symbol=product.symbol,
        name=product.name,
        isin=product.isin,
        product_type=product.product_type.value if isinstance(product.product_type, Enum) else product.product_type,
        currency=product.currency,
        exchange_id=product.exchange_id,
        last_close_price=product.close_price,
        metadata_json={
            "bid_price": product.bid_price,
            "ask_price": product.ask_price
        }
    )


def db_to_product(db_product: DBProduct) -> Product:
    """Convert SQLAlchemy model to Pydantic Product."""
    metadata = db_product.metadata_json or {}
    return Product(
        id=db_product.id,
        symbol=db_product.symbol,
        name=db_product.name,
        isin=db_product.isin,
        product_type=db_product.product_type,
        currency=db_product.currency,
        exchange_id=db_product.exchange_id,
        close_price=db_product.last_close_price,
        bid_price=metadata.get("bid_price"),
        ask_price=metadata.get("ask_price"),
        last_update=db_product.last_update
    )