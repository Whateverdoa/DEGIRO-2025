# DEGIRO Trading Agent - Technical Manual

**Version**: 1.0  
**Date**: 2025-06-02  
**Author**: Jamie Rodriguez (API Integration Specialist)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [API Integration](#api-integration)
6. [Portfolio Management](#portfolio-management)
7. [Error Handling](#error-handling)
8. [Monitoring & Alerting](#monitoring--alerting)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [Security Considerations](#security-considerations)
13. [Performance Optimization](#performance-optimization)
14. [Maintenance](#maintenance)
15. [API Reference](#api-reference)

---

## System Overview

The DEGIRO Trading Agent is a Python-based automated trading system that integrates with DEGIRO's investment platform. It provides portfolio monitoring, trading capabilities, and risk management features while maintaining human-like behavior patterns to avoid detection.

### Key Features

- **Real-time Portfolio Monitoring**: Live tracking of positions, P&L, and portfolio analytics
- **Automated Trading**: Rule-based trading with risk management
- **Human Behavior Simulation**: Realistic interaction patterns to avoid detection
- **Comprehensive Monitoring**: Real-time API health monitoring and alerting
- **Secure Authentication**: Encrypted credential storage with 2FA support
- **Data Export**: Portfolio reports in JSON, CSV, and HTML formats

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    DEGIRO Trading Agent                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend: CLI Dashboard + Web Reports                     │
│  Backend: Python 3.13 + FastAPI                          │
│  Database: PostgreSQL + SQLAlchemy                        │
│  API Client: degiro-connector v3.0.29                     │
│  Security: Cryptography + TOTP                            │
│  Monitoring: Custom API Monitor + Prometheus              │
│  Testing: pytest + Mock                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Core Components

```mermaid
graph TB
    A[Portfolio Dashboard] --> B[Portfolio Service]
    B --> C[DEGIRO API Wrapper]
    C --> D[degiro-connector]
    C --> E[API Monitor]
    C --> F[Session Manager]
    B --> G[Data Models]
    G --> H[Database]
    E --> I[Alert System]
    C --> J[Security Module]
    J --> K[Credential Store]
```

### Directory Structure

```
DEGIRO-2025/
├── core/                      # Core business logic
│   ├── __init__.py
│   ├── api_monitor.py         # API health monitoring
│   ├── config.py              # Configuration management
│   ├── degiro_api.py          # DEGIRO API wrapper
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── human_behavior.py      # Human behavior simulation
│   ├── logging_config.py      # Logging configuration
│   ├── models.py              # Data models (Pydantic + SQLAlchemy)
│   ├── portfolio_service.py   # Portfolio management
│   ├── security.py            # Security and encryption
│   └── session_manager.py     # Session management
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_degiro_integration.py
├── docs/                      # Documentation
│   ├── DEGIRO_API_DOCUMENTATION.md
│   └── TECHNICAL_MANUAL.md
├── config/                    # Configuration files
│   └── app_config.json
├── data/                      # Data storage
│   └── exports/               # Exported reports
├── logs/                      # Log files
├── portfolio_dashboard.py     # Main CLI application
├── requirements.txt           # Python dependencies
└── INTEGRATION_STATUS.md      # Project status
```

---

## Installation & Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 12+ (optional, for advanced features)
- Git
- Virtual environment tool (venv/conda)

### 1. Clone Repository

```bash
git clone <repository-url>
cd DEGIRO-2025
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file:

```bash
# DEGIRO Credentials (encrypted)
DEGIRO_USERNAME_ENC="<encrypted_username>"
DEGIRO_PASSWORD_ENC="<encrypted_password>"
DEGIRO_TOTP_SECRET_ENC="<encrypted_totp_secret>"
CREDENTIAL_KEY="<encryption_key>"

# API Configuration
DEGIRO_API_RATE_LIMIT=60
MARKET_DATA_RATE_LIMIT=120
MAX_POSITION_SIZE=10000

# Database (optional)
DATABASE_URL="postgresql://user:pass@localhost/degiro_trading"

# Logging
LOG_LEVEL="INFO"
LOG_FILE="logs/trading.log"

# Environment
ENVIRONMENT="development"  # development/staging/production
```

### 5. Initialize Configuration

```bash
python -c "
from core.security import degiro_credentials
degiro_credentials.setup_credentials(interactive=True)
"
```

---

## Configuration

### Application Configuration

The system uses a layered configuration approach:

1. **Default Values** (in `core/config.py`)
2. **Environment Variables** (`.env` file)
3. **Configuration File** (`config/app_config.json`)
4. **Runtime Overrides** (command-line arguments)

### Core Settings

```python
# core/config.py
class Settings:
    # DEGIRO API
    degiro_api_rate_limit: int = 60
    degiro_session_timeout: int = 30  # minutes
    
    # Trading
    max_position_size: float = 10000.0
    default_currency: str = "EUR"
    
    # Monitoring
    monitor_check_interval: int = 10  # seconds
    alert_cooldown: int = 300  # seconds
    
    # Human Behavior
    human_behavior_enabled: bool = True
    min_delay: float = 1.0
    max_delay: float = 5.0
```

### Security Configuration

```python
# Credential encryption settings
ENCRYPTION_ALGORITHM = "Fernet"
KEY_DERIVATION = "PBKDF2HMAC"
ITERATIONS = 100000

# TOTP settings
TOTP_WINDOW = 1  # Allow 1 window tolerance
TOTP_PERIOD = 30  # 30-second periods
```

---

## API Integration

### DEGIRO API Wrapper

The `DeGiroAPIWrapper` class provides a high-level interface to the DEGIRO API with enhanced features:

```python
from core.degiro_api import degiro_api

# Connection
if degiro_api.connect():
    print("Connected successfully")
    
    # Get portfolio
    portfolio = degiro_api.get_portfolio()
    
    # Search products
    results = degiro_api.search_products("AAPL", limit=10)
    
    # Get product info
    product_info = degiro_api.get_product_info("1234567")
    
    # Disconnect
    degiro_api.disconnect()
```

### Key Methods

#### Connection Management

```python
# Connect to DEGIRO
success = degiro_api.connect()

# Check connection status
is_connected = degiro_api.is_connected

# Force reconnection
degiro_api.ensure_connected()

# Disconnect
degiro_api.disconnect()

# Health check
health = degiro_api.health_check()
```

#### Portfolio Operations

```python
# Get current portfolio
portfolio_data = degiro_api.get_portfolio()

# Expected response structure:
{
    "positions": [
        {
            "product_id": "1234567",
            "size": 10,
            "price": 150.50,
            "value": 1505.00,
            "product_info": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "isin": "US0378331005"
            }
        }
    ],
    "total_value": 10000.00,
    "cash": 5000.00,
    "timestamp": "2025-06-02T15:30:00"
}
```

#### Product Search

```python
# Search for products
results = degiro_api.search_products(
    search_text="Apple",
    limit=10
)

# Response structure:
[
    {
        "id": "1234567",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "isin": "US0378331005",
        "product_type": 1,
        "currency": "USD",
        "exchange_id": "NASDAQ"
    }
]
```

#### Transaction History

```python
from datetime import datetime, timedelta

# Get transactions for last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

transactions = degiro_api.get_transactions(start_date, end_date)
```

### Rate Limiting

The API wrapper includes built-in rate limiting:

```python
# Default: 60 calls per minute
rate_limiter = RateLimiter(max_calls=60, time_window=60)

# Rate limiting is applied automatically via decorator
@rate_limited
def api_method(self):
    # This method will be rate limited
    pass
```

### Retry Mechanism

Automatic retry with exponential backoff:

```python
@with_retry(max_retries=3, delay=1.0)
def api_method(self):
    # This method will retry on failure
    # Delay doubles each retry: 1s, 2s, 4s
    pass
```

---

## Portfolio Management

### Portfolio Service

The `PortfolioService` class provides high-level portfolio management:

```python
from core.portfolio_service import portfolio_service

# Get portfolio with caching
portfolio = portfolio_service.get_portfolio()

# Force refresh (bypass cache)
portfolio = portfolio_service.get_portfolio(force_refresh=True)

# Get analytics
analytics = portfolio_service.get_portfolio_analytics(portfolio)

# Export portfolio
json_export = portfolio_service.export_portfolio(portfolio, format="json")
csv_export = portfolio_service.export_portfolio(portfolio, format="csv")
html_report = portfolio_service.export_portfolio(portfolio, format="html")
```

### Data Models

The system uses Pydantic models for data validation and serialization:

```python
from core.models import Portfolio, Position, Product

# Portfolio model
portfolio = Portfolio(
    positions=[...],
    total_value=10000.00,
    cash_balance=5000.00,
    total_invested=9500.00,
    total_pnl=500.00,
    total_pnl_percentage=5.26,
    currency="EUR"
)

# Position model
position = Position(
    product_id="1234567",
    product=product,
    size=10,
    average_price=140.00,
    current_price=150.00,
    value=1500.00,
    unrealized_pnl=100.00,
    currency="USD"
)
```

### Portfolio Analytics

```python
analytics = portfolio_service.get_portfolio_analytics(portfolio)

# Analytics structure:
{
    "summary": {
        "total_value": 10000.00,
        "cash_balance": 5000.00,
        "number_of_positions": 5,
        "total_pnl_percentage": 5.26
    },
    "positions_by_type": {
        "STOCK": {"count": 3, "value": 7500.00},
        "ETF": {"count": 2, "value": 2500.00}
    },
    "top_gainers": [...],
    "top_losers": [...],
    "concentration": [...]
}
```

---

## Error Handling

### Exception Hierarchy

```python
DEGIROError                    # Base exception
├── AuthenticationError        # Login/credentials failed
├── SessionExpiredError        # Session timeout
├── RateLimitError            # API rate limit exceeded
├── InvalidRequestError       # Bad request parameters
├── ProductNotFoundError      # Product not found
├── InsufficientFundsError    # Not enough funds
├── OrderValidationError      # Order validation failed
├── MarketClosedError         # Market is closed
├── APITimeoutError           # Request timeout
├── ConnectionError           # Network/connection issues
└── DataParsingError          # Response parsing failed
```

### Error Handling Patterns

```python
from core.exceptions import (
    AuthenticationError,
    SessionExpiredError,
    RateLimitError
)

try:
    portfolio = degiro_api.get_portfolio()
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e.message}")
    # Re-authenticate
    degiro_api.connect()
except SessionExpiredError as e:
    logger.warning(f"Session expired: {e.message}")
    # Automatic reconnection handled by wrapper
except RateLimitError as e:
    logger.warning(f"Rate limit hit: {e.message}")
    if e.retry_after:
        time.sleep(e.retry_after)
except DEGIROError as e:
    logger.error(f"DEGIRO API error: {e.message}")
    if e.details:
        logger.debug(f"Error details: {e.details}")
```

### Automatic Error Recovery

The system includes automatic recovery mechanisms:

1. **Session Recovery**: Automatic reconnection on session expiry
2. **Rate Limit Handling**: Automatic backoff and retry
3. **Connection Recovery**: Retry with exponential backoff
4. **Circuit Breaker**: Prevent cascading failures

```python
# Session manager handles automatic reconnection
session_manager.add_reconnect_callback(on_reconnect)
session_manager.add_disconnect_callback(on_disconnect)

def on_reconnect():
    logger.info("Session reconnected successfully")

def on_disconnect():
    logger.warning("Session disconnected")
```

---

## Monitoring & Alerting

### API Monitor

Real-time monitoring of API performance and health:

```python
from core.api_monitor import api_monitor

# Start monitoring
api_monitor.start_monitoring()

# Record custom metrics
api_monitor.record_request(
    endpoint="get_portfolio",
    response_time=250.0,  # milliseconds
    success=True
)

# Get statistics
stats = api_monitor.get_statistics(window_minutes=60)

# Export metrics
api_monitor.export_metrics("metrics.json", format="json")
```

### Built-in Alerts

The system includes predefined alerts:

1. **High Error Rate**: >10% error rate in 5-minute window
2. **Rate Limit Exceeded**: >5 rate limit hits in 5 minutes
3. **Slow Response**: Average response time >5 seconds
4. **Session Instability**: >3 reconnections in 5 minutes

### Custom Alerts

```python
from core.api_monitor import Alert

# Define custom alert
custom_alert = Alert(
    name="custom_metric_alert",
    condition=lambda metrics: custom_condition(metrics),
    message="Custom alert fired: {custom_value}",
    severity="warning",
    cooldown=300  # 5 minutes
)

# Add to monitor
api_monitor.add_alert(custom_alert)
```

### Alert Callbacks

```python
# Set up alert callbacks
alert_callbacks = {
    "critical": send_sms_alert,
    "error": send_email_alert,
    "warning": log_alert,
    "info": log_alert
}

api_monitor = APIMonitor(alert_callbacks=alert_callbacks)
```

---

## Testing

### Test Suite Structure

```
tests/
├── test_degiro_integration.py    # Main integration tests
├── test_portfolio_service.py     # Portfolio service tests
├── test_api_monitor.py           # Monitoring tests
├── test_security.py             # Security tests
└── test_models.py               # Data model tests
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_degiro_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov-report=html

# Run integration tests only
python -m pytest tests/ -m integration -v

# Run without slow tests
python -m pytest tests/ -m "not slow" -v
```

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end API testing
3. **Mock Tests**: Testing with simulated responses
4. **Performance Tests**: Load and stress testing

### Example Test

```python
def test_portfolio_retrieval():
    """Test portfolio data retrieval and processing."""
    # Setup mock data
    mock_data = {
        "positions": [
            {
                "product_id": "123",
                "size": 10,
                "price": 150.0,
                "value": 1500.0
            }
        ],
        "total_value": 10000.0,
        "cash": 8500.0
    }
    
    # Mock API response
    with patch.object(degiro_api, 'get_portfolio', return_value=mock_data):
        portfolio = portfolio_service.get_portfolio()
        
        assert portfolio is not None
        assert len(portfolio.positions) == 1
        assert portfolio.total_value == 10000.0
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    integration: Integration tests requiring API access
    slow: Slow tests that may timeout
    unit: Fast unit tests
addopts = 
    -v
    --tb=short
    --strict-markers
```

---

## Deployment

### Development Environment

```bash
# Set environment
export ENVIRONMENT=development

# Run with development settings
python portfolio_dashboard.py --debug
```

### Staging Environment

```bash
# Set environment
export ENVIRONMENT=staging

# Use staging credentials
export DEGIRO_USERNAME_ENC="<staging_encrypted_username>"

# Run with monitoring
python portfolio_dashboard.py --monitor
```

### Production Environment

```bash
# Set environment
export ENVIRONMENT=production

# Production configuration
export LOG_LEVEL=WARNING
export DEGIRO_API_RATE_LIMIT=30  # Conservative rate limiting

# Run as service
python -m gunicorn portfolio_dashboard:app --workers 1 --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "portfolio_dashboard.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  degiro-agent:
    build: .
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@db:5432/degiro
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: degiro
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: degiro-trading-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: degiro-trading-agent
  template:
    metadata:
      labels:
        app: degiro-trading-agent
    spec:
      containers:
      - name: trading-agent
        image: degiro-trading-agent:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: degiro-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Symptoms**: `AuthenticationError` on connection attempts

**Causes**:
- Invalid credentials
- Expired TOTP token
- Account locked

**Solutions**:
```bash
# Verify credentials
python -c "
from core.security import degiro_credentials
creds = degiro_credentials.get_credentials()
print('Username:', creds['username'][:3] + '***')
print('TOTP Secret:', 'Set' if creds.get('totp_secret') else 'Missing')
"

# Re-setup credentials
python -c "
from core.security import degiro_credentials
degiro_credentials.setup_credentials(interactive=True)
"
```

#### 2. Rate Limiting

**Symptoms**: `RateLimitError` exceptions

**Causes**:
- Too many API calls
- Insufficient delays between requests

**Solutions**:
```python
# Reduce rate limit
settings.degiro_api_rate_limit = 30  # Reduce from 60

# Add manual delays
import time
time.sleep(2)  # 2-second delay between calls
```

#### 3. Session Timeouts

**Symptoms**: `SessionExpiredError` after period of inactivity

**Causes**:
- Sessions expire after 30 minutes
- Network connectivity issues

**Solutions**:
```python
# Enable automatic session management
from core.session_manager import session_manager
session_manager.start()

# Manual reconnection
if not degiro_api.is_connected:
    degiro_api.connect()
```

#### 4. Data Parsing Errors

**Symptoms**: `DataParsingError` when processing API responses

**Causes**:
- API response format changes
- Network corruption

**Solutions**:
```python
# Enable debug logging
import logging
logging.getLogger("degiro_api").setLevel(logging.DEBUG)

# Validate response format
def validate_response(response):
    required_fields = ['positions', 'total_value', 'cash']
    for field in required_fields:
        if field not in response:
            raise DataParsingError(f"Missing field: {field}")
```

### Debugging Tools

#### 1. Enable Debug Logging

```python
# In code
import logging
logging.basicConfig(level=logging.DEBUG)

# Via environment
export LOG_LEVEL=DEBUG
```

#### 2. API Response Inspection

```python
# Log raw responses
degiro_api.api.set_debug_mode(True)

# Capture responses
responses = []
def capture_response(response):
    responses.append(response)

degiro_api.add_response_callback(capture_response)
```

#### 3. Connection Health Check

```python
# Comprehensive health check
health = degiro_api.health_check()
print(f"Connected: {health['connected']}")
print(f"Session Duration: {health['session_duration']}")
print(f"Last Activity: {health['last_activity']}")
print(f"Rate Limit Status: {health['rate_limit_status']}")
```

#### 4. Monitor Metrics

```python
# Get detailed metrics
stats = api_monitor.get_statistics(window_minutes=60)
print(f"Total Requests: {stats['metrics'].get('request_count', 0)}")
print(f"Error Count: {stats['metrics'].get('error_count', 0)}")
print(f"Average Response Time: {stats['metrics'].get('response_time', {}).get('avg', 0)}ms")
```

### Log Analysis

#### Key Log Patterns

```bash
# Authentication issues
grep "Authentication failed" logs/trading.log

# Rate limiting
grep "Rate limit" logs/trading.log

# Connection problems
grep "Failed to connect" logs/trading.log

# API errors
grep "ERROR.*degiro_api" logs/trading.log
```

#### Log Rotation

```python
# Configure log rotation
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'logs/trading.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

---

## Security Considerations

### Credential Security

1. **Encryption**: All credentials encrypted with Fernet
2. **Key Management**: Encryption keys stored separately
3. **Environment Variables**: No hardcoded credentials
4. **Access Control**: Restricted file permissions

```bash
# Set secure file permissions
chmod 600 .env
chmod 700 data/
```

### Network Security

1. **HTTPS Only**: All API calls use HTTPS
2. **Certificate Validation**: SSL certificates verified
3. **Timeout Settings**: Prevent hanging connections

```python
# Security settings
VERIFY_SSL = True
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
```

### API Security

1. **Rate Limiting**: Prevent API abuse
2. **Request Signing**: Secure API requests
3. **Session Management**: Automatic session cleanup

### Audit Logging

```python
# Security audit logging
security_logger = logging.getLogger("security")
security_logger.info(f"User {username} authenticated successfully")
security_logger.warning(f"Failed login attempt for {username}")
```

### Best Practices

1. **Rotate Credentials**: Change passwords regularly
2. **Monitor Access**: Track API usage patterns
3. **Update Dependencies**: Keep libraries current
4. **Secure Storage**: Encrypt sensitive data at rest

---

## Performance Optimization

### API Performance

1. **Connection Pooling**: Reuse HTTP connections
2. **Request Batching**: Combine multiple requests
3. **Caching**: Cache frequently accessed data
4. **Compression**: Enable response compression

```python
# Optimize API client
api_client = APIClient(
    pool_connections=10,
    pool_maxsize=20,
    enable_compression=True
)
```

### Data Processing

1. **Lazy Loading**: Load data on demand
2. **Pagination**: Process large datasets in chunks
3. **Parallel Processing**: Use threading for I/O operations

```python
# Parallel data processing
from concurrent.futures import ThreadPoolExecutor

def process_portfolio_parallel(positions):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_position, pos) 
            for pos in positions
        ]
        results = [f.result() for f in futures]
    return results
```

### Memory Management

1. **Data Models**: Use efficient data structures
2. **Garbage Collection**: Explicit cleanup
3. **Memory Profiling**: Monitor memory usage

```python
# Memory profiling
import tracemalloc

tracemalloc.start()
# ... code execution ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

### Database Optimization

1. **Connection Pooling**: Efficient database connections
2. **Query Optimization**: Optimize SQL queries
3. **Indexing**: Add appropriate database indexes

```python
# Database connection pool
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

---

## Maintenance

### Regular Maintenance Tasks

#### Daily
- [ ] Check system logs for errors
- [ ] Verify API connection health
- [ ] Review monitoring alerts
- [ ] Validate portfolio data accuracy

#### Weekly
- [ ] Update market data
- [ ] Review performance metrics
- [ ] Check disk space usage
- [ ] Backup configuration files

#### Monthly
- [ ] Update dependencies
- [ ] Review security logs
- [ ] Performance optimization review
- [ ] Documentation updates

### Backup Procedures

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r config/ "$BACKUP_DIR/"

# Backup data
cp -r data/ "$BACKUP_DIR/"

# Backup logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# Create archive
tar -czf "backups/backup_$DATE.tar.gz" "$BACKUP_DIR/"
rm -rf "$BACKUP_DIR"

echo "Backup completed: backup_$DATE.tar.gz"
```

### Update Procedures

#### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade degiro-connector

# Update all packages (caution in production)
pip install --upgrade -r requirements.txt
```

#### Code Updates

```bash
# Pull latest changes
git pull origin main

# Run tests
python -m pytest tests/ -v

# Restart services
systemctl restart degiro-trading-agent
```

### Health Monitoring

```python
# System health check script
def health_check():
    checks = {
        "api_connection": test_api_connection(),
        "database_connection": test_database_connection(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage(),
        "log_errors": check_recent_errors()
    }
    
    for check, status in checks.items():
        print(f"{check}: {'✅' if status else '❌'}")
    
    return all(checks.values())

if __name__ == "__main__":
    if health_check():
        print("System healthy")
        exit(0)
    else:
        print("System issues detected")
        exit(1)
```

---

## API Reference

### Core Classes

#### DeGiroAPIWrapper

```python
class DeGiroAPIWrapper:
    """Main API wrapper for DEGIRO integration."""
    
    def __init__(self):
        """Initialize API wrapper."""
        
    def connect(self) -> bool:
        """Connect to DEGIRO API."""
        
    def disconnect(self):
        """Disconnect from DEGIRO API."""
        
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio positions."""
        
    def search_products(self, search_text: str, limit: int = 10) -> List[Dict]:
        """Search for products by text."""
        
    def get_transactions(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get transaction history."""
        
    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """Get detailed product information."""
        
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on API connection."""
```

#### PortfolioService

```python
class PortfolioService:
    """Service for fetching and analyzing portfolio data."""
    
    def get_portfolio(self, force_refresh: bool = False) -> Optional[Portfolio]:
        """Get current portfolio with positions and values."""
        
    def get_portfolio_analytics(self, portfolio: Optional[Portfolio] = None) -> Dict[str, Any]:
        """Get detailed portfolio analytics."""
        
    def export_portfolio(self, portfolio: Optional[Portfolio] = None, format: str = "json") -> str:
        """Export portfolio data in various formats."""
```

#### APIMonitor

```python
class APIMonitor:
    """Monitor API performance and health."""
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        
    def record_request(self, endpoint: str, response_time: float, success: bool, error: Optional[Exception] = None):
        """Record API request metrics."""
        
    def get_statistics(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Get monitoring statistics."""
        
    def add_alert(self, alert: Alert):
        """Add a monitoring alert."""
```

### Data Models

#### Portfolio

```python
@dataclass
class Portfolio:
    positions: List[Position]
    total_value: float
    cash_balance: float
    total_invested: float
    total_pnl: float
    total_pnl_percentage: float
    currency: str
    last_update: datetime = Field(default_factory=datetime.now)
```

#### Position

```python
@dataclass
class Position:
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
```

### Configuration API

```python
# Get configuration
from core.config import settings

# API settings
rate_limit = settings.degiro_api_rate_limit
session_timeout = settings.degiro_session_timeout

# Update settings
settings.degiro_api_rate_limit = 30
```

### Error Handling API

```python
from core.exceptions import handle_degiro_error, DEGIROError

try:
    # API operation
    result = api_operation()
except Exception as e:
    # Convert to custom exception
    custom_error = handle_degiro_error(e)
    raise custom_error
```

---

## Appendices

### Appendix A: Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment (dev/staging/prod) | development | No |
| `DEGIRO_USERNAME_ENC` | Encrypted DEGIRO username | - | Yes |
| `DEGIRO_PASSWORD_ENC` | Encrypted DEGIRO password | - | Yes |
| `DEGIRO_TOTP_SECRET_ENC` | Encrypted TOTP secret | - | Yes |
| `CREDENTIAL_KEY` | Encryption key | - | Yes |
| `DEGIRO_API_RATE_LIMIT` | API rate limit (calls/minute) | 60 | No |
| `DATABASE_URL` | Database connection string | - | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Appendix B: File Permissions

```bash
# Recommended file permissions
chmod 600 .env                    # Environment variables
chmod 600 config/app_config.json  # Configuration
chmod 700 data/                   # Data directory
chmod 755 logs/                   # Log directory
chmod 644 *.py                    # Python files
chmod 755 portfolio_dashboard.py  # Executable script
```

### Appendix C: Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `degiro-connector` | 3.0.29 | DEGIRO API client |
| `pydantic` | 2.5.2+ | Data validation |
| `sqlalchemy` | 2.0.23+ | Database ORM |
| `cryptography` | 41.0.7+ | Encryption |
| `requests` | 2.31.0+ | HTTP client |
| `pandas` | 2.1.4+ | Data analysis |
| `pytest` | 7.4.3+ | Testing |

### Appendix D: API Endpoints

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/portfolio` | GET | Get portfolio data | 1/min |
| `/products/search` | GET | Search products | 10/min |
| `/products/{id}` | GET | Get product info | 30/min |
| `/transactions` | GET | Get transactions | 5/min |
| `/orders` | GET | Get orders | 10/min |

---

**Document Information**
- **Version**: 1.0
- **Last Updated**: 2025-06-02
- **Reviewed By**: Jamie Rodriguez
- **Next Review**: 2025-07-02

---

*This manual is maintained as part of the DEGIRO Trading Agent project. For updates and support, contact the development team.*