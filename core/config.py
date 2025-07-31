import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json


# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation and type checking."""
    
    # Application
    app_name: str = "degiro-trading-agent"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False)
    
    # DEGIRO Credentials
    degiro_username: Optional[str] = Field(default=None, env="DEGIRO_USERNAME")
    degiro_password: Optional[str] = Field(default=None, env="DEGIRO_PASSWORD")
    degiro_totp_secret: Optional[str] = Field(default=None, env="DEGIRO_TOTP_SECRET")
    degiro_int_account: Optional[str] = Field(default=None, env="DEGIRO_INT_ACCOUNT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_dir: str = Field(default="logs")
    
    # Database
    database_url: str = Field(
        default="postgresql://localhost:5432/degiro_trading",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # API Rate Limiting
    degiro_api_rate_limit: int = Field(default=60, env="DEGIRO_API_RATE_LIMIT")
    market_data_rate_limit: int = Field(default=120, env="MARKET_DATA_RATE_LIMIT")
    
    # Trading Configuration
    max_daily_trades: int = Field(default=10, env="MAX_DAILY_TRADES")
    max_position_size: float = Field(default=10000.0, env="MAX_POSITION_SIZE")
    default_stop_loss_percent: float = Field(default=5.0, env="DEFAULT_STOP_LOSS_PERCENT")
    default_take_profit_percent: float = Field(default=10.0, env="DEFAULT_TAKE_PROFIT_PERCENT")
    
    # Notifications
    notification_email: Optional[str] = Field(default=None, env="NOTIFICATION_EMAIL")
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # SMS (Twilio)
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_from_number: Optional[str] = Field(default=None, env="TWILIO_FROM_NUMBER")
    sms_to_number: Optional[str] = Field(default=None, env="SMS_TO_NUMBER")
    
    # Risk Management
    max_portfolio_risk_percent: float = Field(default=20.0, env="MAX_PORTFOLIO_RISK_PERCENT")
    max_single_position_percent: float = Field(default=10.0, env="MAX_SINGLE_POSITION_PERCENT")
    enable_emergency_stop: bool = Field(default=True, env="ENABLE_EMERGENCY_STOP")
    
    # Market Data
    market_data_provider: str = Field(default="yfinance", env="MARKET_DATA_PROVIDER")
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    
    # Web Dashboard
    web_host: str = Field(default="0.0.0.0", env="WEB_HOST")
    web_port: int = Field(default=8000, env="WEB_PORT")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    enable_web_interface: bool = Field(default=True, env="ENABLE_WEB_INTERFACE")
    
    # Backup
    enable_backups: bool = Field(default=True, env="ENABLE_BACKUPS")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    backup_path: str = Field(default="./data/backups", env="BACKUP_PATH")
    
    # Encryption key for sensitive data
    _encryption_key: Optional[bytes] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @field_validator("market_data_provider")
    @classmethod
    def validate_market_data_provider(cls, v):
        allowed = ["yfinance", "alpha_vantage"]
        if v not in allowed:
            raise ValueError(f"Market data provider must be one of {allowed}")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    def get_encryption_key(self) -> bytes:
        """Get or generate encryption key for sensitive data."""
        if self._encryption_key is None:
            key_file = Path("config/.encryption.key")
            key_file.parent.mkdir(exist_ok=True)
            
            if key_file.exists():
                with open(key_file, "rb") as f:
                    self._encryption_key = f.read()
            else:
                self._encryption_key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(self._encryption_key)
                os.chmod(key_file, 0o600)  # Restrict access to owner only
        
        return self._encryption_key
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value."""
        f = Fernet(self.get_encryption_key())
        return f.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value."""
        f = Fernet(self.get_encryption_key())
        return f.decrypt(encrypted_value.encode()).decode()
    
    def get_safe_dict(self) -> Dict[str, Any]:
        """Get configuration as dict with sensitive values masked."""
        config_dict = self.dict()
        sensitive_keys = [
            "degiro_password", "degiro_totp_secret", "smtp_password",
            "twilio_auth_token", "alpha_vantage_api_key", "secret_key"
        ]
        
        for key in sensitive_keys:
            if key in config_dict and config_dict[key]:
                config_dict[key] = "***MASKED***"
        
        return config_dict


# Global settings instance
settings = Settings()


class ConfigManager:
    """Manage application configuration with hot-reloading support."""
    
    def __init__(self):
        self.settings = settings
        self.config_file = Path("config/app_config.json")
        self.config_file.parent.mkdir(exist_ok=True)
        self._load_dynamic_config()
    
    def _load_dynamic_config(self):
        """Load dynamic configuration that can be changed at runtime."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.dynamic_config = json.load(f)
        else:
            self.dynamic_config = {
                "trading_enabled": True,
                "rules_enabled": True,
                "emergency_stop_active": False,
                "allowed_symbols": [],
                "blocked_symbols": [],
                "active_strategies": []
            }
            self.save_dynamic_config()
    
    def save_dynamic_config(self):
        """Save dynamic configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(self.dynamic_config, f, indent=2)
    
    def update_dynamic_config(self, key: str, value: Any):
        """Update a dynamic configuration value."""
        self.dynamic_config[key] = value
        self.save_dynamic_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value, checking dynamic config first."""
        if key in self.dynamic_config:
            return self.dynamic_config[key]
        return getattr(self.settings, key, default)
    
    def reload(self):
        """Reload configuration from files."""
        load_dotenv(override=True)
        self.settings = Settings()
        self._load_dynamic_config()


# Global config manager instance
config_manager = ConfigManager()