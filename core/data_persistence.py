"""Data persistence layer for portfolio and trading data."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
import logging

from core.database import db_manager
from core.models import (
    Portfolio, Position, Product, Transaction,
    DBProduct, DBPosition, DBOrder, DBTransaction, DBPortfolioSnapshot,
    product_to_db, db_to_product
)

logger = logging.getLogger(__name__)


class DataPersistence:
    """Handles data persistence for portfolio and trading data."""
    
    def save_portfolio_snapshot(self, portfolio: Portfolio) -> bool:
        """Save a portfolio snapshot to the database."""
        try:
            with db_manager.get_session() as session:
                # Create portfolio snapshot
                snapshot = DBPortfolioSnapshot(
                    snapshot_date=datetime.now(),
                    total_value=portfolio.total_value,
                    cash_balance=portfolio.cash_balance,
                    total_invested=portfolio.total_invested,
                    total_pnl=portfolio.total_pnl,
                    total_pnl_percentage=portfolio.total_pnl_percentage,
                    currency=portfolio.currency,
                    positions_json=[
                        {
                            "product_id": pos.product_id,
                            "size": pos.size,
                            "average_price": pos.average_price,
                            "current_price": pos.current_price,
                            "value": pos.value,
                            "unrealized_pnl": pos.unrealized_pnl,
                            "currency": pos.currency
                        }
                        for pos in portfolio.positions
                    ]
                )
                
                session.add(snapshot)
                
                # Update or create products
                for position in portfolio.positions:
                    if position.product:
                        self._upsert_product(session, position.product)
                
                logger.info(f"Portfolio snapshot saved with {len(portfolio.positions)} positions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save portfolio snapshot: {e}")
            return False
    
    def save_positions(self, positions: List[Position]) -> bool:
        """Save current positions to the database."""
        try:
            with db_manager.get_session() as session:
                # Mark all existing positions as inactive
                session.query(DBPosition).update({"is_active": False})
                
                # Add current positions
                for position in positions:
                    # Ensure product exists
                    if position.product:
                        self._upsert_product(session, position.product)
                    
                    # Create or update position
                    db_position = DBPosition(
                        product_id=position.product_id,
                        size=position.size,
                        average_price=position.average_price,
                        currency=position.currency,
                        is_active=True
                    )
                    session.add(db_position)
                
                logger.info(f"Saved {len(positions)} positions to database")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save positions: {e}")
            return False
    
    def save_transactions(self, transactions: List[Dict[str, Any]]) -> bool:
        """Save transaction data to the database."""
        try:
            with db_manager.get_session() as session:
                for tx_data in transactions:
                    # Check if transaction already exists
                    existing = session.query(DBTransaction).filter_by(
                        degiro_transaction_id=tx_data.get("id")
                    ).first()
                    
                    if existing:
                        continue  # Skip duplicate transactions
                    
                    # Create new transaction
                    db_transaction = DBTransaction(
                        degiro_transaction_id=tx_data.get("id"),
                        product_id=str(tx_data.get("product_id", "")),
                        transaction_type=tx_data.get("transaction_type", "UNKNOWN"),
                        quantity=float(tx_data.get("quantity", 0)),
                        price=float(tx_data.get("price", 0)),
                        total_amount=float(tx_data.get("total_amount", 0)),
                        fees=tx_data.get("fees"),
                        currency=tx_data.get("currency", "EUR"),
                        executed_at=tx_data.get("date", datetime.now()),
                        notes=tx_data.get("notes")
                    )
                    session.add(db_transaction)
                
                logger.info(f"Saved {len(transactions)} transactions to database")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save transactions: {e}")
            return False
    
    def get_portfolio_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get portfolio history for the specified number of days."""
        try:
            with db_manager.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                snapshots = session.query(DBPortfolioSnapshot).filter(
                    DBPortfolioSnapshot.snapshot_date >= cutoff_date
                ).order_by(desc(DBPortfolioSnapshot.snapshot_date)).all()
                
                return [
                    {
                        "date": snapshot.snapshot_date.isoformat(),
                        "total_value": snapshot.total_value,
                        "cash_balance": snapshot.cash_balance,
                        "total_pnl": snapshot.total_pnl,
                        "total_pnl_percentage": snapshot.total_pnl_percentage,
                        "currency": snapshot.currency,
                        "positions_count": len(snapshot.positions_json)
                    }
                    for snapshot in snapshots
                ]
                
        except Exception as e:
            logger.error(f"Failed to get portfolio history: {e}")
            return []
    
    def get_position_history(self, product_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get position history for a specific product."""
        try:
            with db_manager.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                positions = session.query(DBPosition).filter(
                    and_(
                        DBPosition.product_id == product_id,
                        DBPosition.created_at >= cutoff_date
                    )
                ).order_by(desc(DBPosition.created_at)).all()
                
                return [
                    {
                        "date": pos.created_at.isoformat(),
                        "size": pos.size,
                        "average_price": pos.average_price,
                        "currency": pos.currency,
                        "is_active": pos.is_active
                    }
                    for pos in positions
                ]
                
        except Exception as e:
            logger.error(f"Failed to get position history for {product_id}: {e}")
            return []
    
    def get_transactions(self, 
                        product_id: Optional[str] = None,
                        days: int = 30,
                        transaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get transactions with optional filtering."""
        try:
            with db_manager.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days)
                
                query = session.query(DBTransaction).filter(
                    DBTransaction.executed_at >= cutoff_date
                )
                
                if product_id:
                    query = query.filter(DBTransaction.product_id == product_id)
                
                if transaction_type:
                    query = query.filter(DBTransaction.transaction_type == transaction_type)
                
                transactions = query.order_by(desc(DBTransaction.executed_at)).all()
                
                return [
                    {
                        "id": tx.degiro_transaction_id,
                        "product_id": tx.product_id,
                        "transaction_type": tx.transaction_type,
                        "quantity": tx.quantity,
                        "price": tx.price,
                        "total_amount": tx.total_amount,
                        "fees": tx.fees,
                        "currency": tx.currency,
                        "executed_at": tx.executed_at.isoformat(),
                        "notes": tx.notes
                    }
                    for tx in transactions
                ]
                
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []
    
    def get_portfolio_performance(self, days: int = 30) -> Dict[str, Any]:
        """Calculate portfolio performance metrics."""
        try:
            history = self.get_portfolio_history(days)
            
            if len(history) < 2:
                return {"error": "Insufficient data for performance calculation"}
            
            # Sort by date (oldest first)
            history.sort(key=lambda x: x["date"])
            
            start_value = history[0]["total_value"]
            end_value = history[-1]["total_value"]
            
            total_return = end_value - start_value
            total_return_pct = (total_return / start_value * 100) if start_value > 0 else 0
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(history)):
                prev_value = history[i-1]["total_value"]
                curr_value = history[i]["total_value"]
                daily_return = (curr_value - prev_value) / prev_value if prev_value > 0 else 0
                daily_returns.append(daily_return)
            
            # Calculate volatility (standard deviation of daily returns)
            import statistics
            volatility = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
            
            return {
                "period_days": days,
                "start_value": start_value,
                "end_value": end_value,
                "total_return": total_return,
                "total_return_percentage": total_return_pct,
                "volatility": volatility * 100,  # Convert to percentage
                "data_points": len(history),
                "daily_avg_return": sum(daily_returns) / len(daily_returns) * 100 if daily_returns else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio performance: {e}")
            return {"error": str(e)}
    
    def cleanup_old_data(self, retention_days: int = 90) -> bool:
        """Clean up old data beyond retention period."""
        try:
            with db_manager.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=retention_days)
                
                # Delete old portfolio snapshots
                deleted_snapshots = session.query(DBPortfolioSnapshot).filter(
                    DBPortfolioSnapshot.snapshot_date < cutoff_date
                ).delete()
                
                # Delete old inactive positions
                deleted_positions = session.query(DBPosition).filter(
                    and_(
                        DBPosition.updated_at < cutoff_date,
                        DBPosition.is_active == False
                    )
                ).delete()
                
                logger.info(f"Cleaned up {deleted_snapshots} old snapshots and {deleted_positions} old positions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return False
    
    def _upsert_product(self, session: Session, product: Product):
        """Insert or update product information."""
        try:
            existing = session.query(DBProduct).filter_by(id=product.id).first()
            
            if existing:
                # Update existing product
                existing.symbol = product.symbol
                existing.name = product.name
                existing.isin = product.isin
                existing.product_type = product.product_type.value if hasattr(product.product_type, 'value') else str(product.product_type)
                existing.currency = product.currency
                existing.exchange_id = product.exchange_id
                existing.last_close_price = product.close_price
                existing.last_update = datetime.now()
                existing.metadata_json = {
                    "bid_price": product.bid_price,
                    "ask_price": product.ask_price
                }
            else:
                # Create new product
                db_product = product_to_db(product)
                session.add(db_product)
                
        except Exception as e:
            logger.error(f"Failed to upsert product {product.id}: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with db_manager.get_session() as session:
                return {
                    "products_count": session.query(DBProduct).count(),
                    "active_positions_count": session.query(DBPosition).filter_by(is_active=True).count(),
                    "total_positions_count": session.query(DBPosition).count(),
                    "transactions_count": session.query(DBTransaction).count(),
                    "portfolio_snapshots_count": session.query(DBPortfolioSnapshot).count(),
                    "orders_count": session.query(DBOrder).count()
                }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}


# Global persistence instance
data_persistence = DataPersistence()