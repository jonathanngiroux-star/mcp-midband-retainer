#!/usr/bin/env python3
"""Tool definitions for mcp-midband-retainer."""

from mcp.types import Tool

TOOLS = [
    Tool(
        name="get_account_summary",
        description=(
            "Return a real computed summary of the mid-band account: tier, monthly price (the "
            "$120 anchor), services subscribed, account owner, tenure months computed from the "
            "start date, health score computed from actual incident/SLA/artifact signals, spend "
            "to date, next invoice date, renewal date, annual option price (10x monthly less "
            "~17% discount) computed in Python, price-lock status, and the two-column IP "
            "exit-rights summary."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "default": "acct-001",
                    "description": "Account identifier.",
                },
            },
            "required": ["account_id"],
        },
    ),
    Tool(
        name="get_quarterly_review",
        description=(
            "Return the real quarterly review: quarter, meeting date, attendees, SLA compliance "
            "rate, incident counts and severity mix, SLA credits issued in the quarter (USD), "
            "artifact access activity, usage vs plan, health score trend vs prior quarter, action "
            "items with owner and due date, and the published next-quarter calendar."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "default": "acct-001",
                    "description": "Account identifier.",
                },
                "quarter": {
                    "type": "string",
                    "description": "Quarter (e.g., Q4 2024); returns latest if not specified.",
                },
            },
            "required": ["account_id"],
        },
    ),
    Tool(
        name="get_upgrade_path",
        description=(
            "Compute upgrade eligibility for real: checks each requirement (min monthly volume, "
            "min agent count, min health score, min tenure months, min active services) against "
            "the account's actual data, returns per-requirement pass/fail, the specific gaps, "
            "the target tier's benefits and price, the price delta, the migration timeline "
            "estimate, and a recommended path."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "default": "acct-001",
                    "description": "Account identifier.",
                },
            },
            "required": ["account_id"],
        },
    ),
    Tool(
        name="get_artifact_access",
        description=(
            "Return the real priority artifact access state: the artifact pack the account is "
            "entitled to (SLA artifact pack, regression comparison reports, raw run logs, "
            "compliance deliverables, on-chain attestations), which are included in the retainer "
            "vs available as paid add-on, per-artifact access history (last accessed, access count), "
            "and the two-column IP rule stating which artifacts are customer-owned on exit."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "default": "acct-001",
                    "description": "Account identifier.",
                },
                "artifact_type": {
                    "type": "string",
                    "enum": ["all", "sla", "regression", "run_logs", "compliance", "onchain"],
                    "default": "all",
                    "description": "Filter by artifact type.",
                },
            },
            "required": ["account_id"],
        },
    ),
]