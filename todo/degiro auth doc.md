# DEGIRO API Authentication: Complete Technical Guide with Critical Warnings

## Critical Warning: Account Termination Risk

DEGIRO's updated terms of service (October 2024) explicitly state: *"The Client is not allowed to use Automated Tools on DEGIRO's investment platform. If DEGIRO detects Automated Tools or activities pointing to their use, the queries, activities or accounts involved could be blocked by DEGIRO."*

Despite this prohibition, here's the comprehensive technical information you requested:

## 1. How to obtain DEGIRO username and password for API access

### Username and Password Requirements
- **Username**: Your standard DEGIRO login (alphanumeric)
- **Password**: 
  - Web platform: alphanumeric password
  - Mobile app: numeric-only password
- **Storage**: Never hardcode credentials; use secure storage methods

### Secure Credential Management
```python
# Example using environment variables with encryption
from cryptography.fernet import Fernet
import os

def get_degiro_credentials():
    encryption_key = os.environ['CREDENTIAL_KEY']
    fernet = Fernet(encryption_key)
    
    username = fernet.decrypt(os.environ['DEGIRO_USER_ENC'].encode()).decode()
    password = fernet.decrypt(os.environ['DEGIRO_PWD_ENC'].encode()).decode()
    
    return username, password
```

## 2. Extracting the TOTP secret from DEGIRO's 2FA setup

### The extraction process requires capturing the QR code during initial 2FA setup:

**Step 1: Enable 2FA in DEGIRO**
- Navigate to: Profile Icon → Personal Settings → Security → Enable

**Step 2: Capture the QR Code**
- When the QR code appears, save it as an image before scanning with your authenticator app

**Step 3: Extract the Secret**
The QR code contains a standard TOTP URI format:
```
otpauth://totp/DEGIRO:YOUR_USERNAME?algorithm=SHA1&issuer=DEGIRO&secret=YOUR_TOTP_SECRET&digits=6&period=30
```

### Extraction Methods:

**Python Method (Recommended):**
```python
from pyzbar import pyzbar
from PIL import Image
import re

def extract_totp_secret(qr_image_path):
    # Read QR code
    image = Image.open(qr_image_path)
    qr_codes = pyzbar.decode(image)
    
    for qr_code in qr_codes:
        qr_data = qr_code.data.decode('utf-8')
        # Extract secret using regex
        match = re.search(r'secret=([A-Z2-7]+)', qr_data)
        if match:
            return match.group(1)
    return None

# Usage
secret = extract_totp_secret('degiro_qr.png')
print(f"TOTP Secret: {secret}")
```

**Command Line Method:**
```bash
# Install zbar-tools
sudo apt-get install zbar-tools  # Ubuntu/Debian
brew install zbar                 # macOS

# Extract from QR image
zbarimg degiro_qr.png | grep -oP 'secret=\K[A-Z2-7]+'
```

## 3. Where to find the 2FA secret in DEGIRO settings

**Important**: DEGIRO does **not** display the TOTP secret after initial setup. You can only obtain it during the initial 2FA activation process by extracting it from the QR code. There's no way to view the secret later through the interface.

## 4. Step-by-step 2FA setup and secret extraction

### Complete Setup Process:

1. **Login to DEGIRO** (web browser only)
2. **Navigate to Security Settings**
   - Click profile icon (bottom-left)
   - Select "Personal Settings"
   - Click "Security" tab
   - Click "Enable" under Two-Factor Authentication

3. **Prepare for Secret Extraction**
   - Have screen capture software ready
   - Or use browser developer tools to save the QR image

4. **During QR Code Display**
   - Right-click the QR code → Save image as...
   - Or take a screenshot immediately

5. **Extract the Secret**
   ```python
   import pyotp
   from urllib.parse import urlparse, parse_qs
   
   # After extracting the otpauth URL
   otpauth_url = "otpauth://totp/DEGIRO:username?secret=ABCDEF123456..."
   parsed = urlparse(otpauth_url)
   params = parse_qs(parsed.query)
   totp_secret = params['secret'][0]
   
   # Verify it works
   totp = pyotp.TOTP(totp_secret)
   current_code = totp.now()
   print(f"Current OTP: {current_code}")
   ```

6. **Complete Setup**
   - Scan QR with authenticator app
   - Enter the 6-digit code to confirm
   - Save backup codes provided

## 5. Security best practices for storing credentials

### Tier 1: Enterprise Key Management (Recommended)
```python
# Azure Key Vault example
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net", credential=credential)

# Store secrets
client.set_secret("degiro-username", username)
client.set_secret("degiro-password", password)
client.set_secret("degiro-totp", totp_secret)

# Retrieve secrets
username = client.get_secret("degiro-username").value
```

### Tier 2: Local Encrypted Storage
```python
import keyring
from cryptography.fernet import Fernet

class SecureCredentialStore:
    def __init__(self, service_name="degiro_automation"):
        self.service = service_name
        self.key = self._get_or_create_key()
        
    def _get_or_create_key(self):
        key = keyring.get_password(self.service, "encryption_key")
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password(self.service, "encryption_key", key)
        return key.encode()
    
    def store_credential(self, name, value):
        f = Fernet(self.key)
        encrypted = f.encrypt(value.encode()).decode()
        keyring.set_password(self.service, name, encrypted)
    
    def get_credential(self, name):
        f = Fernet(self.key)
        encrypted = keyring.get_password(self.service, name)
        return f.decrypt(encrypted.encode()).decode()
```

### Critical Security Considerations:
- **Never store TOTP secrets alongside passwords** - this defeats 2FA
- Implement credential rotation every 30-90 days
- Use separate storage systems for passwords and TOTP secrets
- Enable audit logging for all credential access
- Implement rate limiting to prevent brute force attacks

## 6. Risks and warnings about unofficial DEGIRO APIs

### **HIGH RISK - Account Termination**
- DEGIRO actively monitors for automation patterns
- Detected automation results in permanent account closure
- No appeal process for automation violations
- Possible complications accessing funds after termination

### Technical Risks:
- **API Instability**: Unofficial APIs break when DEGIRO updates
- **No Support**: Zero official support or documentation
- **Data Integrity**: No guarantees on order execution
- **Security Exposure**: Credentials handled by third-party code

### Detection Methods DEGIRO Uses:
- Unusual login frequency patterns
- Rapid API call sequences
- Non-browser user agents
- Consistent timing patterns
- High-frequency data requests

## 7. Alternative authentication methods

**Currently Not Available**:
- ❌ No OAuth2 implementation
- ❌ No official API keys
- ❌ No developer portal
- ❌ No webhook support
- ❌ No official third-party integrations

**Only Method (Prohibited)**:
Username/password authentication via reverse-engineered APIs

## 8. Common issues and solutions

### Issue 1: Session Timeout (30 minutes)
```python
from degiro_connector.trading.api import API
from degiro_connector.core.exceptions import TimeoutError

def safe_api_call(api, operation):
    try:
        return operation()
    except TimeoutError:
        print("Session expired, reconnecting...")
        api.connect()
        return operation()

# Usage
result = safe_api_call(trading_api, lambda: trading_api.get_portfolio())
```

### Issue 2: Rate Limiting (HTTP 429)
```python
import time
from functools import wraps

def rate_limit(min_interval=1.0):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(min_interval=2.0)
def create_order(api, order_details):
    return api.create_order(order_details)
```

### Issue 3: TOTP Generation
```python
import pyotp

class DEGIROAuthenticator:
    def __init__(self, totp_secret):
        self.totp = pyotp.TOTP(totp_secret)
    
    def get_current_code(self):
        return self.totp.now()
    
    def verify_code(self, code):
        return self.totp.verify(code, valid_window=1)
```

## Working Implementation Example

```python
from degiro_connector.trading.api import API
from degiro_connector.trading.models.credentials import Credentials
import logging

# WARNING: This violates DEGIRO's terms of service
def setup_degiro_connection(username, password, totp_secret, int_account=None):
    credentials = Credentials(
        username=username,
        password=password,
        totp_secret_key=totp_secret,
        int_account=int_account
    )
    
    api = API(credentials=credentials)
    
    try:
        api.connect()
        config = api.get_config()
        
        # Store session info for reuse
        session_id = config.get('sessionId')
        client_id = config.get('clientId')
        
        return api, session_id, client_id
        
    except Exception as e:
        logging.error(f"Connection failed: {e}")
        raise
```

## Safer Alternatives

Given the significant risks, consider these alternatives:

### 1. **API-Friendly Brokers**
- **Interactive Brokers**: Official TWS API with full automation support
- **Saxo Bank**: REST API with proper documentation
- **Alpaca**: Commission-free with extensive API support

### 2. **Semi-Automated Approaches**
- Use portfolio tracking software with DEGIRO integration
- Set up bank auto-transfers for regular investing
- Use alert systems for manual execution

### 3. **Hybrid Strategy**
- Keep long-term investments with DEGIRO (manual)
- Use API-enabled brokers for automated strategies

## Conclusion

While it's technically possible to extract DEGIRO credentials and TOTP secrets for automation, **doing so violates DEGIRO's terms of service and risks permanent account closure**. The technical implementation involves extracting TOTP secrets from QR codes during 2FA setup and using unofficial Python/JavaScript libraries.

For users requiring API access, the safest approach is to switch to brokers that officially support automation. If you choose to proceed despite the risks, implement robust security practices, careful rate limiting, and be prepared for potential account termination without recourse.