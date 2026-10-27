#!/usr/bin/env python3
"""MCP server for midband-retainer - Mid-Band Success Retainer"""

import json
import os
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("mcp-midband-retainer")

ACCOUNTS = {
    "acc-001": {
        "id": "acc-001",
        "name": "Acme Trading Corp",
        "tier": "midband",
        "monthly_volume_usd": 2500000,
        "agent_count": 3,
        "agents": ["agent-001", "agent-002", "agent-003"],
        "success_manager": "sm-001",
        "health_score": 87,
        "last_qbr": "2024-10-15T10:00:00",
        "next_qbr_due": "2025-01-15T10:00:00",
        "upgrade_eligible": True,
        "contract_renewal": "2025-06-01"
    },
    "acc-002": {
        "id": "acc-002",
        "name": "Beta DeFi Labs",
        "tier": "midband",
        "monthly_volume_usd": 1800000,
        "agent_count": 2,
        "agents": ["agent-004", "agent-005"],
        "success_manager": "sm-002",
        "health_score": 92,
        "last_qbr": "2024-11-01T10:00:00",
        "next_qbr_due": "2025-02-01T10:00:00",
        "upgrade_eligible": False,
        "contract_renewal": "2025-08-15"
    }
}

QUARTERLY_REVIEWS = {
    "qbr-001": {
        "id": "qbr-001",
        "account_id": "acc-001",
        "quarter": "Q4 2024",
        "date": "2024-10-15T10:00:00",
        "attendees": ["sm-001", "acc-001-stakeholder"],
        "metrics": {"uptime": 99.7, "volume_usd": 2500000, "incidents": 2, "sla_credits": 30},
        "action_items": [
            {"item": "Optimize gas costs on Polygon", "owner": "engineering", "due": "2024-12-01", "status": "done"},
            {"item": "Add Solana support", "owner": "product", "due": "2025-03-01", "status": "in_progress"}
        ],
        "health_score": 87,
        "satisfaction": 4.5
    }
}

UPGRADE_PATHS = {
    "midband_to_enterprise": {
        "from_tier": "midband",
        "to_tier": "enterprise",
        "requirements": {
            "min_monthly_volume_usd": 5000000,
            "min_agent_count": 5,
            "min_health_score": 85,
            "min_tenure_months": 6
        },
        "benefits": [
            "99.9% uptime SLA",
            "15-min recovery guarantee",
            "Dedicated success engineer",
            "Custom adversarial testing",
            "Priority feature requests",
            "Volume pricing discounts"
        ],
        "price_increase_pct": 150,
        "migration_timeline_days": 30
    }
}

app = Server("mcp-midband-retainer")

TOOLS = [
    Tool(
        name="get_account_summary",
        description="Get account summary for mid-band retainer",
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Account ID"}
            },
            "required": ["account_id"]
        }
    ),
    Tool(
        name="get_quarterly_review",
        description="Get quarterly business review for an account",
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Account ID"},
                "quarter": {"type": "string", "description": "Quarter (e.g., Q4 2024), optional - returns latest if not specified"}
            },
            "required": ["account_id"]
        }
    ),
    Tool(
        name="get_upgrade_path",
        description="Get upgrade path eligibility and details",
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Account ID"}
            },
            "required": ["account_id"]
        }
    )
]

@app.list_tools()
async def list_tools():
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_account_summary":
        account_id = arguments.get("account_id")
        
        account = ACCOUNTS.get(account_id)
        if not account:
            return [TextContent(type="text", text=json.dumps({"error": f"Account not found: {account_id}"}))]
        
        result = {"status": "ok", "tool": "get_account_summary", "account": account}
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "get_quarterly_review":
        account_id = arguments.get("account_id")
        quarter = arguments.get("quarter")
        
        reviews = [r for r in QUARTERLY_REVIEWS.values() if r["account_id"] == account_id]
        if not reviews:
            return [TextContent(type="text", text=json.dumps({"error": f"No reviews found for account: {account_id}"}))]
        
        if quarter:
            reviews = [r for r in reviews if r["quarter"] == quarter]
        
        reviews.sort(key=lambda x: x["date"], reverse=True)
        
        result = {"status": "ok", "tool": "get_quarterly_review", "account_id": account_id, "reviews": reviews}
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "get_upgrade_path":
        account_id = arguments.get("account_id")
        
        account = ACCOUNTS.get(account_id)
        if not account:
            return [TextContent(type="text", text=json.dumps({"error": f"Account not found: {account_id}"}))]
        
        upgrade_path = UPGRADE_PATHS.get("midband_to_enterprise")
        if not upgrade_path:
            return [TextContent(type="text", text=json.dumps({"error": "No upgrade path defined"}))]
        
        # Check eligibility
        req = upgrade_path["requirements"]
        eligible = (
            account["monthly_volume_usd"] >= req["min_monthly_volume_usd"] and
            account["agent_count"] >= req["min_agent_count"] and
            account["health_score"] >= req["min_health_score"]
        )
        
        gaps = []
        if account["monthly_volume_usd"] < req["min_monthly_volume_usd"]:
            gaps.append(f"Volume: ${account['monthly_volume_usd']:,} < ${req['min_monthly_volume_usd']:,}")
        if account["agent_count"] < req["min_agent_count"]:
            gaps.append(f"Agents: {account['agent_count']} < {req['min_agent_count']}")
        if account["health_score"] < req["min_health_score"]:
            gaps.append(f"Health score: {account['health_score']} < {req['min_health_score']}")
        
        result = {
            "status": "ok",
            "tool": "get_upgrade_path",
            "account_id": account_id,
            "current_tier": account["tier"],
            "target_tier": "enterprise",
            "eligible": eligible,
            "gaps": gaps,
            "requirements": req,
            "benefits": upgrade_path["benefits"],
            "price_increase_pct": upgrade_path["price_increase_pct"],
            "migration_timeline_days": upgrade_path["migration_timeline_days"]
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def serve():
        reader, writer = await stdio_server()
        await app.run(reader, writer)
    
    asyncio.run(serve())