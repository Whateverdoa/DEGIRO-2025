"""Security module for handling credentials and sensitive data."""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
import pyotp
from core.logging_config import get_logger
from core.config import settings


logger = get_logger("security")


class CredentialManager:
    """Manage encrypted storage and retrieval of sensitive credentials."""
    
    def __init__(self, credentials_file: str = "config/credentials.json"):
        self.credentials_file = Path(credentials_file)
        self.credentials_file.parent.mkdir(exist_ok=True)
        self._fernet = None
        self._master_key = None
        
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key."""
        if self._master_key:
            return self._master_key
            
        key_file = Path("config/.master.key")
        key_file.parent.mkdir(exist_ok=True)
        
        if key_file.exists():
            # Load existing key
            with open(key_file, "rb") as f:
                self._master_key = f.read()
                logger.debug("Loaded existing master key")
        else:
            # Generate new key
            self._master_key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self._master_key)
            # Restrict access to owner only
            os.chmod(key_file, 0o600)
            logger.info("Generated new master encryption key")
            
        return self._master_key
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption/decryption."""
        if not self._fernet:
            self._fernet = Fernet(self._get_or_create_master_key())
        return self._fernet
    
    def store_credential(self, key: str, value: str, force: bool = False) -> bool:
        """
        Store an encrypted credential.
        
        Args:
            key: Credential identifier
            value: Credential value to encrypt
            force: Whether to overwrite existing credential
            
        Returns:
            True if stored successfully
        """
        try:
            # Load existing credentials
            credentials = self._load_credentials()
            
            # Check if already exists
            if key in credentials and not force:
                logger.warning(f"Credential '{key}' already exists. Use force=True to overwrite.")
                return False
            
            # Encrypt and store
            encrypted_value = self._get_fernet().encrypt(value.encode()).decode()
            credentials[key] = {
                "encrypted_value": encrypted_value,
                "updated_at": str(datetime.now())
            }
            
            # Save credentials
            self._save_credentials(credentials)
            logger.info(f"Stored credential '{key}' successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credential '{key}': {e}")
            return False
    
    def retrieve_credential(self, key: str) -> Optional[str]:
        """
        Retrieve and decrypt a credential.
        
        Args:
            key: Credential identifier
            
        Returns:
            Decrypted credential value or None
        """
        try:
            credentials = self._load_credentials()
            
            if key not in credentials:
                logger.warning(f"Credential '{key}' not found")
                return None
                
            encrypted_value = credentials[key]["encrypted_value"]
            decrypted_value = self._get_fernet().decrypt(encrypted_value.encode()).decode()
            
            logger.debug(f"Retrieved credential '{key}'")
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve credential '{key}': {e}")
            return None
    
    def delete_credential(self, key: str) -> bool:
        """Delete a stored credential."""
        try:
            credentials = self._load_credentials()
            
            if key not in credentials:
                logger.warning(f"Credential '{key}' not found")
                return False
                
            del credentials[key]
            self._save_credentials(credentials)
            
            logger.info(f"Deleted credential '{key}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete credential '{key}': {e}")
            return False
    
    def list_credentials(self) -> list:
        """List all stored credential keys (not values)."""
        credentials = self._load_credentials()
        return list(credentials.keys())
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from encrypted file."""
        if not self.credentials_file.exists():
            return {}
            
        try:
            with open(self.credentials_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials file: {e}")
            return {}
    
    def _save_credentials(self, credentials: Dict[str, Any]):
        """Save credentials to encrypted file."""
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)
        # Restrict access to owner only
        os.chmod(self.credentials_file, 0o600)


class DeGiroCredentials:
    """Handle DEGIRO-specific credentials."""
    
    def __init__(self):
        self.credential_manager = CredentialManager()
        self._totp = None
        
    def setup_credentials(self, interactive: bool = True):
        """
        Set up DEGIRO credentials from environment or interactive input.
        
        Args:
            interactive: Whether to prompt for missing credentials
        """
        # Try to get from environment first
        username = settings.degiro_username
        password = settings.degiro_password
        totp_secret = settings.degiro_totp_secret
        
        # Store credentials if available
        if username:
            self.credential_manager.store_credential("degiro_username", username, force=True)
        elif interactive:
            username = input("Enter DEGIRO username: ")
            self.credential_manager.store_credential("degiro_username", username)
            
        if password:
            self.credential_manager.store_credential("degiro_password", password, force=True)
        elif interactive:
            password = getpass.getpass("Enter DEGIRO password: ")
            self.credential_manager.store_credential("degiro_password", password)
            
        if totp_secret:
            # Validate TOTP secret format
            if self._validate_totp_secret(totp_secret):
                self.credential_manager.store_credential("degiro_totp_secret", totp_secret, force=True)
            else:
                logger.error("Invalid TOTP secret format")
        elif interactive:
            totp_secret = input("Enter DEGIRO TOTP secret (press Enter if not using 2FA): ")
            if totp_secret:
                if self._validate_totp_secret(totp_secret):
                    self.credential_manager.store_credential("degiro_totp_secret", totp_secret)
                else:
                    logger.error("Invalid TOTP secret format")
    
    def get_credentials(self) -> Dict[str, Optional[str]]:
        """Get DEGIRO credentials."""
        return {
            "username": self.credential_manager.retrieve_credential("degiro_username"),
            "password": self.credential_manager.retrieve_credential("degiro_password"),
            "totp_secret": self.credential_manager.retrieve_credential("degiro_totp_secret"),
            "int_account": os.getenv("DEGIRO_INT_ACCOUNT")
        }
    
    def validate_credentials(self) -> bool:
        """Check if required credentials are available."""
        creds = self.get_credentials()
        
        if not creds["username"] or not creds["password"]:
            logger.error("Missing required DEGIRO credentials")
            return False
            
        # Validate TOTP secret if provided
        if creds["totp_secret"] and not self._validate_totp_secret(creds["totp_secret"]):
            logger.error("Invalid TOTP secret")
            return False
            
        return True
    
    def _validate_totp_secret(self, secret: str) -> bool:
        """Validate TOTP secret format."""
        try:
            # Remove spaces and convert to uppercase
            secret = secret.replace(" ", "").upper()
            # Check if it's valid base32
            pyotp.TOTP(secret).now()
            return True
        except Exception as e:
            logger.error(f"Invalid TOTP secret: {e}")
            return False
    
    def get_current_totp_code(self) -> Optional[str]:
        """Get current TOTP code if 2FA is enabled."""
        creds = self.get_credentials()
        totp_secret = creds.get("totp_secret")
        
        if not totp_secret:
            return None
            
        try:
            if not self._totp:
                self._totp = pyotp.TOTP(totp_secret)
            return self._totp.now()
        except Exception as e:
            logger.error(f"Failed to generate TOTP code: {e}")
            return None
    
    def verify_totp_code(self, code: str) -> bool:
        """Verify a TOTP code."""
        creds = self.get_credentials()
        totp_secret = creds.get("totp_secret")
        
        if not totp_secret:
            return False
            
        try:
            if not self._totp:
                self._totp = pyotp.TOTP(totp_secret)
            return self._totp.verify(code, valid_window=1)
        except Exception as e:
            logger.error(f"Failed to verify TOTP code: {e}")
            return False


# Global credential manager instance
credential_manager = CredentialManager()
degiro_credentials = DeGiroCredentials()