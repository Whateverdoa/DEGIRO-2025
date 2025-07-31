# DEGIRO Trading Agent

A Python-based trading agent for DEGIRO that monitors portfolios, executes conditional trades with human oversight, and provides comprehensive risk management.

## Project Status

Phase 1.1 (Project Setup) ✅ COMPLETE
- Python virtual environment configured
- Project structure established
- Core dependencies installed
- Logging framework implemented
- Configuration management system created

## Quick Start

1. **Set up environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure the application**:
   ```bash
   cp .env.example .env
   # Edit .env with your DEGIRO credentials and preferences
   ```

3. **Run tests** (when implemented):
   ```bash
   pytest
   ```

## Project Structure

```
DEGIRO-2025/
├── core/              # Core functionality
├── strategies/        # Trading strategies
├── notifications/     # Alert and notification system
├── ui/               # Web dashboard
├── tests/            # Test suite
├── config/           # Configuration files
├── logs/             # Application logs
├── data/             # Data storage
└── todo/             # Development roadmap
```

## Security

- Never commit `.env` file or credentials
- Sensitive data is encrypted using Fernet encryption
- Configuration files with `.key` extension are gitignored

## Development

See `todo/degiro_trading_agent_todo.md` for the complete development roadmap.