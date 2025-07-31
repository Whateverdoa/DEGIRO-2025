"""Database configuration and session management."""

import os
from typing import Generator, Optional
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from core.config import settings
from core.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self, database_url: Optional[str] = None) -> bool:
        """Initialize database connection."""
        try:
            # Use provided URL or fall back to settings
            db_url = database_url or settings.database_url
            
            # For development, use SQLite if PostgreSQL not available
            if settings.is_development and db_url.startswith("postgresql://"):
                sqlite_path = "data/degiro_trading.db"
                os.makedirs("data", exist_ok=True)
                db_url = f"sqlite:///{sqlite_path}"
                logger.info(f"Development mode: Using SQLite database at {sqlite_path}")
            
            # Create engine with connection pooling
            if db_url.startswith("sqlite"):
                # SQLite specific settings
                self.engine = create_engine(
                    db_url,
                    echo=settings.debug,
                    connect_args={"check_same_thread": False}
                )
            else:
                # PostgreSQL settings
                self.engine = create_engine(
                    db_url,
                    echo=settings.debug,
                    poolclass=QueuePool,
                    pool_size=settings.database_pool_size,
                    max_overflow=settings.database_max_overflow,
                    pool_pre_ping=True,
                    pool_recycle=3600  # Recycle connections every hour
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connection
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self._initialized = True
            logger.info(f"Database initialized successfully: {db_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self._initialized = False
            return False
    
    def create_tables(self) -> bool:
        """Create all tables if they don't exist."""
        try:
            if not self._initialized:
                raise RuntimeError("Database not initialized")
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def drop_tables(self) -> bool:
        """Drop all tables (use with caution)."""
        try:
            if not self._initialized:
                raise RuntimeError("Database not initialized")
            
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            return False
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_factory(self) -> sessionmaker:
        """Get session factory for dependency injection."""
        if not self._initialized:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal
    
    def health_check(self) -> bool:
        """Check database connection health."""
        try:
            if not self._initialized:
                return False
            
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get database connection statistics."""
        if not self._initialized or not self.engine:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        return {
            "status": "connected",
            "engine_name": self.engine.name,
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "is_healthy": self.health_check()
        }


# Global database manager
db_manager = DatabaseManager()


def init_database(create_tables: bool = True) -> bool:
    """Initialize database with optional table creation."""
    success = db_manager.initialize()
    
    if success and create_tables:
        success = db_manager.create_tables()
    
    return success


def get_db_session():
    """Dependency function for FastAPI/other frameworks."""
    with db_manager.get_session() as session:
        yield session


# For backward compatibility
def get_db():
    """Get database session (legacy function)."""
    return db_manager.get_session()