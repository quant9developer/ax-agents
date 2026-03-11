from __future__ import annotations

from datetime import datetime, timezone


def audit_entry(user_id: str, action: str, resource: str, result: str, ip_address: str) -> dict[str, str]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "result": result,
        "ip_address": ip_address,
    }
