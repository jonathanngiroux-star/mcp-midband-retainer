# mcp-midband-retainer

MCP server for the **Mid-Band Success Retainer** - the productized invisible tier: a $120/mo
named-relationship retainer with quarterly service reviews, upgrade-path orchestration, priority
artifact access, and price-lock in the billing token. $120/mo is the dominant anchor of the V3
run (133 price mentions, ~2x the next band). Annual ~10x with ~17% discount.

## Tools

### `get_account_summary`
Real computed summary of the mid-band account.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `account_id` | string | `acct-001` | Account identifier |

Returns tier, monthly price ($120 anchor), services, owner, tenure months, health score, spend,
next invoice, renewal date, annual option (10x less 17% discount), price-lock status, and the
two-column IP exit-rights summary.

### `get_quarterly_review`
Real quarterly business review.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `account_id` | string | `acct-001` | Account identifier |
| `quarter` | string | latest | Quarter (e.g., Q4 2024) |

Returns quarter, meeting date, attendees, SLA compliance rate, incident counts by severity, SLA
credits (USD), artifact access activity, usage vs plan, health score trend, action items, and
published next-quarter calendar.

### `get_upgrade_path`
Real upgrade eligibility computation.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `account_id` | string | `acct-001` | Account identifier |

Checks each requirement (min volume, min agents, min health, min tenure, min services) against
actual data, returns per-requirement pass/fail, gaps, target tier benefits and price, price
delta, migration timeline, and recommended path.

### `get_artifact_access`
Priority artifact access state.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `account_id` | string | `acct-001` | Account identifier |
| `artifact_type` | string enum | `all` | Filter by type: all/sla/regression/run_logs/compliance/onchain |

Returns artifact pack entitlements (what's included vs paid add-on), access history, and the
two-column IP rule for customer-owned artifacts on exit.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

State in `./state/midband_state.json`. Override with `MCP_MIDBAND_RETAINER_STATE_DIR`.

## Connecting to an MCP client

```json
{
  "mcpServers": {
    "midband-retainer": {
      "command": "python3",
      "args": ["/tmp/v3-services/mcp-midband-retainer/main.py"]
    }
  }
}
```

## License

MIT