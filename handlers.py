#!/usr/bin/env python3
"""Real business logic for mcp-midband-retainer handlers."""

import json
import os
import statistics
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

def _state_dir() -> Path:
    override = os.environ.get("MCP_MIDBAND_RETAINER_STATE_DIR")
    path = Path(override) if override else Path(__file__).resolve().parent / "state"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _state_path() -> Path:
    return _state_dir() / "midband_state.json"


def _default_state() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "accounts": {
            "acct-001": {
                "id": "acct-001",
                "name": "Acme Trading Corp",
                "tier": "midband",
                "monthly_price_usd": 120.0,
                "services": ["mcp-agent-sla", "mcp-frcompliance", "mcp-regression-watch"],
                "owner": "sm-001",
                "owner_name": "L. Moreau",
                "start_date": "2025-06-01T00:00:00Z",
                "health_score": 87,
                "monthly_volume_usd": 2500000,
                "agent_count": 3,
                "active_services": 3,
                "last_invoice": "2025-12-01T00:00:00Z",
                "next_invoice": "2026-01-01T00:00:00Z",
                "renewal_date": "2026-06-01T00:00:00Z",
                "price_locked": True,
                "invoice_history": [
                    {"date": "2025-12-01", "amount_usd": 120.0},
                    {"date": "2025-11-01", "amount_usd": 120.0},
                    {"date": "2025-10-01", "amount_usd": 120.0},
                ],
            },
            "acct-002": {
                "id": "acct-002",
                "name": "Beta DeFi Labs",
                "tier": "midband",
                "monthly_price_usd": 120.0,
                "services": ["mcp-oncall-retainer", "mcp-onchain-proof"],
                "owner": "sm-002",
                "owner_name": "S. Haddad",
                "start_date": "2025-08-15T00:00:00Z",
                "health_score": 92,
                "monthly_volume_usd": 1800000,
                "agent_count": 2,
                "active_services": 2,
                "last_invoice": "2025-12-01T00:00:00Z",
                "next_invoice": "2026-01-01T00:00:00Z",
                "renewal_date": "2026-08-15T00:00:00Z",
                "price_locked": True,
                "invoice_history": [
                    {"date": "2025-12-01", "amount_usd": 120.0},
                    {"date": "2025-11-01", "amount_usd": 120.0},
                ],
            },
        },
        "quarterly_reviews": {
            "acct-001": [
                {
                    "quarter": "Q4 2025",
                    "meeting_date": "2025-10-15T10:00:00Z",
                    "attendees": ["sm-001", "acme-stakeholder"],
                    "sla_compliance_rate": 98.5,
                    "incident_counts": {"sev1": 0, "sev2": 1, "sev3": 2},
                    "sla_credits_usd": 45.0,
                    "artifact_accesses": {"sla": 8, "regression": 3, "run_logs": 2, "compliance": 5, "onchain": 4},
                    "usage_vs_plan": {"agents": "3/5", "services": "3/5", "volume_pct": 50},
                    "health_score": 87,
                    "prior_health_score": 85,
                    "action_items": [
                        {"item": "Add Solana support to agent-sla", "owner": "product", "due": "2026-01-15", "status": "in_progress"},
                        {"item": "Optimize gas costs on Polygon", "owner": "engineering", "due": "2025-12-01", "status": "done"},
                    ],
                    "next_quarter_calendar": [
                        {"date": "2026-01-15", "event": "Q1 kickoff", "type": "meeting"},
                        {"date": "2026-02-01", "event": "SLA review", "type": "review"},
                        {"date": "2026-03-01", "event": "Annual pricing lock-in", "type": "milestone"},
                    ],
                },
                {
                    "quarter": "Q3 2025",
                    "meeting_date": "2025-07-15T10:00:00Z",
                    "attendees": ["sm-001", "acme-stakeholder"],
                    "sla_compliance_rate": 99.1,
                    "incident_counts": {"sev1": 0, "sev2": 0, "sev3": 1},
                    "sla_credits_usd": 0.0,
                    "artifact_accesses": {"sla": 6, "regression": 2, "run_logs": 1, "compliance": 4, "onchain": 3},
                    "usage_vs_plan": {"agents": "3/5", "services": "3/5", "volume_pct": 48},
                    "health_score": 85,
                    "prior_health_score": 82,
                    "action_items": [
                        {"item": "Configure FR/EN compliance cadence", "owner": "compliance", "due": "2025-09-01", "status": "done"},
                    ],
                    "next_quarter_calendar": [
                        {"date": "2025-10-15", "event": "Q4 review", "type": "meeting"},
                    ],
                },
            ],
            "acct-002": [
                {
                    "quarter": "Q4 2025",
                    "meeting_date": "2025-11-01T10:00:00Z",
                    "attendees": ["sm-002", "beta-stakeholder"],
                    "sla_compliance_rate": 99.7,
                    "incident_counts": {"sev1": 0, "sev2": 0, "sev3": 1},
                    "sla_credits_usd": 0.0,
                    "artifact_accesses": {"sla": 0, "regression": 0, "run_logs": 0, "compliance": 2, "onchain": 6},
                    "usage_vs_plan": {"agents": "2/5", "services": "2/5", "volume_pct": 36},
                    "health_score": 92,
                    "prior_health_score": 90,
                    "action_items": [
                        {"item": "Enable on-chain attestations for liability pool", "owner": "engineering", "due": "2026-01-15", "status": "in_progress"},
                    ],
                    "next_quarter_calendar": [
                        {"date": "2026-02-01", "event": "Q1 review", "type": "meeting"},
                    ],
                },
            ],
        },
        "artifact_access_log": {
            "acct-001": [
                {"artifact": "sla_artifact_pack", "type": "sla", "last_accessed": "2025-12-20T14:30:00Z", "access_count": 8, "included": True},
                {"artifact": "regression_comparison_report", "type": "regression", "last_accessed": "2025-12-18T09:15:00Z", "access_count": 3, "included": True},
                {"artifact": "raw_run_logs", "type": "run_logs", "last_accessed": "2025-12-15T11:00:00Z", "access_count": 2, "included": True},
                {"artifact": "compliance_deliverable", "type": "compliance", "last_accessed": "2025-12-10T16:45:00Z", "access_count": 5, "included": True},
                {"artifact": "onchain_attestation", "type": "onchain", "last_accessed": "2025-12-08T12:00:00Z", "access_count": 4, "included": True},
            ],
            "acct-002": [
                {"artifact": "compliance_deliverable", "type": "compliance", "last_accessed": "2025-12-18T10:00:00Z", "access_count": 2, "included": True},
                {"artifact": "onchain_attestation", "type": "onchain", "last_accessed": "2025-12-20T15:30:00Z", "access_count": 6, "included": True},
            ],
        },
    }


def load_state() -> dict[str, Any]:
    path = _state_path()
    if not path.exists():
        state = _default_state()
        save_state(state)
        return state
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        state = _default_state()
    base = _default_state()
    base.update(state)
    for key, default in _default_state().items():
        if key not in base:
            base[key] = default
    return state


def save_state(state: dict[str, Any]) -> None:
    path = _state_path()
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".midband-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_ts(value: str) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _tenure_months(start_date_str: str) -> int:
    start = _parse_ts(start_date_str)
    now = _now()
    return (now.year - start.year) * 12 + now.month - start.month + (1 if now.day >= start.day else 0)


def _annual_price(monthly: float) -> float:
    return round(monthly * 10 * (1 - 0.17), 2)


# --------------------------------------------------------------------------
# Handlers
# --------------------------------------------------------------------------

def _handler_get_account_summary(arguments: dict) -> dict[str, Any]:
    account_id = str(arguments.get("account_id", "acct-001")).strip()
    state = load_state()
    account = state.get("accounts", {}).get(account_id)
    if not account:
        return {
            "status": "error",
            "error": f"account not found: {account_id}",
            "valid_accounts": list(state.get("accounts", {}).keys()),
        }

    tenure = _tenure_months(account["start_date"])
    annual = _annual_price(account["monthly_price_usd"])

    # Health score from incident/SLA/artifact signals
    reviews = state.get("quarterly_reviews", {}).get(account_id, [])
    latest_review = reviews[0] if reviews else {}
    health = latest_review.get("health_score", account.get("health_score", 0))

    ip_exit = {
        "leaves_with_customer": [
            "SLA artifact pack (incidents, credits, post-mortems)",
            "Regression comparison reports",
            "Raw run logs (customer-owned per two-column IP rule)",
            "Compliance deliverables (KYC packs, legal annexes)",
            "On-chain attestation records",
        ],
        "stays_with_provider": [
            "Platform monitoring infrastructure",
            "Shared baseline data",
            "Aggregated pool statistics",
        ],
    }

    return {
        "account": {
            "id": account["id"],
            "name": account["name"],
            "tier": account["tier"],
            "monthly_price_usd": account["monthly_price_usd"],
            "price_anchor": "$120/mo (dominant V3 anchor)",
            "services_subscribed": account["services"],
            "account_owner": {"id": account["owner"], "name": account["owner_name"]},
            "tenure_months": tenure,
            "health_score": health,
            "spend_to_date_usd": round(sum(inv["amount_usd"] for inv in account.get("invoice_history", [])), 2),
            "next_invoice_date": account.get("next_invoice"),
            "renewal_date": account.get("renewal_date"),
            "annual_option": {
                "monthly_usd": account["monthly_price_usd"],
                "annual_usd": annual,
                "discount_pct": 17.0,
                "formula": "10 x monthly x (1 - 0.17)",
            },
            "price_lock_status": "active" if account.get("price_locked") else "not_locked",
            "two_column_ip_exit_rights": ip_exit,
        }
    }


def _handler_get_quarterly_review(arguments: dict) -> dict[str, Any]:
    account_id = str(arguments.get("account_id", "acct-001")).strip()
    quarter = arguments.get("quarter")
    state = load_state()
    reviews = state.get("quarterly_reviews", {}).get(account_id, [])
    if not reviews:
        return {"status": "error", "error": f"no reviews found for account: {account_id}"}
    if quarter:
        reviews = [r for r in reviews if r["quarter"] == quarter]
    reviews.sort(key=lambda r: r["meeting_date"], reverse=True)
    if not reviews:
        return {"status": "error", "error": f"no review for quarter: {quarter}"}
    return {"account_id": account_id, "reviews": reviews}


def _handler_get_upgrade_path(arguments: dict) -> dict[str, Any]:
    account_id = str(arguments.get("account_id", "acct-001")).strip()
    state = load_state()
    account = state.get("accounts", {}).get(account_id)
    if not account:
        return {"status": "error", "error": f"account not found: {account_id}", "valid_accounts": list(state.get("accounts", {}).keys())}

    target = "enterprise"
    reqs = {
        "min_monthly_volume_usd": 5000000,
        "min_agent_count": 5,
        "min_health_score": 85,
        "min_tenure_months": 6,
        "min_active_services": 3,
    }
    tenure = _tenure_months(account["start_date"])
    checks = {
        "volume": {"required": reqs["min_monthly_volume_usd"], "actual": account["monthly_volume_usd"], "pass": account["monthly_volume_usd"] >= reqs["min_monthly_volume_usd"]},
        "agents": {"required": reqs["min_agent_count"], "actual": account["agent_count"], "pass": account["agent_count"] >= reqs["min_agent_count"]},
        "health": {"required": reqs["min_health_score"], "actual": account["health_score"], "pass": account["health_score"] >= reqs["min_health_score"]},
        "tenure": {"required": reqs["min_tenure_months"], "actual": tenure, "pass": tenure >= reqs["min_tenure_months"]},
        "services": {"required": reqs["min_active_services"], "actual": account["active_services"], "pass": account["active_services"] >= reqs["min_active_services"]},
    }
    gaps = []
    for key, check in checks.items():
        if not check["pass"]:
            gaps.append(f"{key}: {check['actual']} < {check['required']}")
    eligible = all(c["pass"] for c in checks.values())

    current_monthly = account["monthly_price_usd"]
    enterprise_monthly = 300.0  # 150% increase per V3 pricing
    benefits = [
        "99.9% uptime SLA",
        "15-min recovery guarantee",
        "Dedicated success engineer",
        "Custom adversarial testing",
        "Priority feature requests",
        "Volume pricing discounts",
    ]

    return {
        "account_id": account_id,
        "current_tier": account["tier"],
        "target_tier": target,
        "eligible": eligible,
        "gaps": gaps,
        "requirements": reqs,
        "checks": checks,
        "benefits": benefits,
        "price_increase_pct": 150,
        "current_monthly_usd": current_monthly,
        "target_monthly_usd": enterprise_monthly,
        "migration_timeline_days": 30,
        "recommended_path": "Eligible - proceed with migration" if eligible else "Address gaps first: " + "; ".join(gaps),
    }


def _handler_get_artifact_access(arguments: dict) -> dict[str, Any]:
    account_id = str(arguments.get("account_id", "acct-001")).strip()
    artifact_type = str(arguments.get("artifact_type", "all")).strip()
    state = load_state()
    logs = state.get("artifact_access_log", {}).get(account_id, [])
    if artifact_type != "all":
        logs = [l for l in logs if l["type"] == artifact_type]

    # Artifact pack definitions
    pack_defs = {
        "sla": {"name": "SLA Artifact Pack", "included": True, "description": "Incidents, credits, post-mortems, adversarial test runs"},
        "regression": {"name": "Regression Comparison Reports", "included": True, "description": "Per-case side-by-side, diff summary, regression list"},
        "run_logs": {"name": "Raw Run Logs", "included": True, "description": "Full agent execution traces (customer-owned on exit)"},
        "compliance": {"name": "Compliance Deliverables", "included": True, "description": "KYC packs, legal annexes, AMF interpretations"},
        "onchain": {"name": "On-Chain Attestations", "included": True, "description": "Proof-of-service attestations with chain linkage"},
    }

    artifacts = []
    for log in logs:
        defn = pack_defs.get(log["type"], {})
        artifacts.append({
            "type": log["type"],
            "name": defn.get("name", log["type"]),
            "description": defn.get("description", ""),
            "included_in_retainer": defn.get("included", True),
            "last_accessed": log["last_accessed"],
            "access_count": log["access_count"],
        })

    # Add any pack types the account doesn't have yet
    for key, defn in pack_defs.items():
        if not any(a["type"] == key for a in artifacts):
            artifacts.append({
                "type": key,
                "name": defn["name"],
                "description": defn["description"],
                "included_in_retainer": defn["included"],
                "last_accessed": None,
                "access_count": 0,
            })

    ip_rule = {
        "customer_owned_on_exit": [
            "SLA artifact pack",
            "Regression comparison reports",
            "Raw run logs",
            "Compliance deliverables",
            "On-chain attestation records",
        ],
        "provider_retained": [
            "Platform monitoring infrastructure",
            "Shared baseline data",
            "Aggregated pool statistics",
        ],
    }

    return {
        "account_id": account_id,
        "filter": artifact_type,
        "artifacts": artifacts,
        "ip_exit_rule": ip_rule,
    }


HANDLERS = {
    "get_account_summary": _handler_get_account_summary,
    "get_quarterly_review": _handler_get_quarterly_review,
    "get_upgrade_path": _handler_get_upgrade_path,
    "get_artifact_access": _handler_get_artifact_access,
}