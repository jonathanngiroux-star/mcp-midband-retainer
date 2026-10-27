# mcp-midband-retainer

MCP server for Mid-Band Success Retainer - account summaries, quarterly reviews, upgrade paths.

## Tools

### get_account_summary
Get account summary for mid-band retainer.

**Parameters:**
- `account_id` (string, required): Account ID

### get_quarterly_review
Get quarterly business review for an account.

**Parameters:**
- `account_id` (string, required): Account ID
- `quarter` (string, optional): Quarter (e.g., "Q4 2024"), returns latest if not specified

### get_upgrade_path
Get upgrade path eligibility and details to enterprise tier.

**Parameters:**
- `account_id` (string, required): Account ID

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Connecting to Claude Desktop

```json
{
  "mcpServers": {
    "midband-retainer": {
      "command": "python",
      "args": ["/path/to/mcp-midband-retainer/main.py"],
      "cwd": "/path/to/mcp-midband-retainer"
    }
  }
}
```

## License

MIT