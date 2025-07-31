# MCP Tools Setup Guide

## 1. GitHub Token Setup

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name like "Claude Desktop MCP"
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
   - `gist` (Create gists)
5. Generate token and copy it
6. Replace `YOUR_GITHUB_TOKEN_HERE` in the config

## 2. Slack Bot Setup

1. Go to: https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "DEGIRO Trading Bot" and select your workspace
4. Under "OAuth & Permissions":
   - Add Bot Token Scopes:
     - `chat:write` (Send messages)
     - `channels:read` (View channels)
     - `groups:read` (View private channels)
     - `im:read` (View direct messages)
     - `mpim:read` (View group direct messages)
5. Install to workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)
7. Get your Team ID from: https://app.slack.com/client/[TEAM_ID]/
8. Replace tokens in the config

## 3. Memory Server
- No configuration needed
- Automatically stores conversation context
- Persists between Claude sessions

## 4. Browser (Puppeteer) Server
- No configuration needed
- Will download Chromium on first use
- Useful for web scraping and testing

## 5. Time Server
- No configuration needed
- Provides time-based operations
- Market hours calculations

## Installation Commands

After updating the config file with your tokens, copy it:

```bash
# Backup current config (if exists)
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.backup.json 2>/dev/null

# Copy new config
cp /Users/mike10h/PROJECTS/DEGIRO-2025/complete_mcp_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Restart Claude Desktop
```

## Testing After Restart

After restarting Claude Desktop, I'll have access to:

### GitHub Tools:
- `mcp__github__create_issue` - Create GitHub issues
- `mcp__github__create_pull_request` - Create PRs
- `mcp__github__search_repositories` - Search repos
- `mcp__github__get_file_contents` - Read files from repos

### Memory Tools:
- `mcp__memory__store` - Store information
- `mcp__memory__retrieve` - Retrieve stored info
- `mcp__memory__list` - List stored items

### Browser Tools:
- `mcp__browser__navigate` - Go to URL
- `mcp__browser__screenshot` - Take screenshots
- `mcp__browser__click` - Click elements
- `mcp__browser__type` - Type text

### Time Tools:
- `mcp__time__get_current_time` - Get current time
- `mcp__time__add_time` - Add time intervals
- `mcp__time__time_until` - Calculate time until event

### Slack Tools:
- `mcp__slack__send_message` - Send Slack messages
- `mcp__slack__list_channels` - List available channels
- `mcp__slack__get_channel_history` - Read channel messages

## Use Cases for DEGIRO Project

1. **GitHub**: Track features, bugs, and project progress
2. **Memory**: Remember trading rules, decisions, and context
3. **Browser**: Monitor DEGIRO web interface, test our web UI
4. **Time**: Handle market hours, schedule trades
5. **Slack**: Send trading alerts, notifications, daily summaries