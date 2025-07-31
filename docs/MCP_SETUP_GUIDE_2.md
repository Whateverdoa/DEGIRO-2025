# MCP (Model Context Protocol) Setup Guide for Claude Code

This guide explains how to set up and configure MCP servers in Claude Code CLI.

## Overview

MCP servers enable Claude to access external tools and data sources. There are two different approaches depending on which Claude interface you're using:

- **Claude Desktop**: Uses configuration files
- **Claude Code CLI**: Uses `claude mcp` commands

## Setting Up GitHub MCP Server

### Prerequisites

1. **GitHub Personal Access Token**
   - Go to https://github.com/settings/tokens/new
   - Create a new token (classic)
   - Required scopes:
     - `repo` (Full control of private repositories)
     - `read:org` (Read org and team membership)
     - `read:user` (Read user profile data)
   - Copy the token (you won't see it again!)

### For Claude Code CLI

1. **Check current MCP servers**:
   ```bash
   claude mcp list
   ```

2. **Add GitHub MCP server**:
   ```bash
   claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here -- npx -y @modelcontextprotocol/server-github
   ```

3. **Verify installation**:
   ```bash
   claude mcp list
   ```

4. **Restart Claude Code session** to load the new tools

### For Claude Desktop (Alternative Method)

1. **Create configuration directory**:
   ```bash
   mkdir -p ~/Library/Application\ Support/Claude
   ```

2. **Create/edit configuration file**:
   ```bash
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Add configuration**:
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** completely

## Managing MCP Servers in Claude Code

### Basic Commands

- **List all servers**: `claude mcp list`
- **Get server details**: `claude mcp get github`
- **Remove a server**: `claude mcp remove github`

### Adding Other MCP Servers

#### Filesystem Server
```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/directory
```

#### PostgreSQL Server
```bash
claude mcp add postgres -e POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/db -- npx -y @modelcontextprotocol/server-postgres
```

#### Custom Server with Environment Variables
```bash
claude mcp add myserver -e API_KEY=your_key -e BASE_URL=https://api.example.com -- /path/to/server
```

### Server Scopes

Use the `-s` flag to specify scope:
- `claude mcp add -s user` - Available across all projects
- `claude mcp add -s project` - Only for current project
- `claude mcp add -s local` - Default, local to current directory

## Troubleshooting

### Common Issues

1. **Token not working**:
   - Verify token has correct scopes
   - Check token hasn't expired
   - Regenerate token if needed

2. **Server not loading**:
   - Restart Claude Code session
   - Check `claude mcp list` shows the server
   - Verify npm package exists

3. **Permission errors**:
   - Ensure token has required GitHub permissions
   - Check environment variable is set correctly

### Security Best Practices

1. **Token Security**:
   - Never commit tokens to repositories
   - Use environment variables when possible
   - Regenerate tokens periodically
   - Revoke unused tokens

2. **MCP Server Security**:
   - Only install trusted MCP servers
   - Review third-party servers before installation
   - Use appropriate scopes for filesystem access

## Verification

After setup, you should see GitHub-related tools in Claude Code:
- Tools starting with `mcp__github__*`
- Ability to interact with GitHub repositories
- Access to GitHub API functionality

## Example Usage

Once configured, you can ask Claude to:
- "List my GitHub repositories"
- "Create a new issue in my repo"
- "Show recent commits"
- "Create a pull request"

## Additional Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Available MCP Servers](https://github.com/modelcontextprotocol)

---

*Last updated: May 30, 2025*