from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


def can_execute(role: Role) -> bool:
    return role in {Role.ADMIN, Role.OPERATOR}
