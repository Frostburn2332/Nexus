from src.models.user import UserRole

ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.VIEWER: 0,
    UserRole.MANAGER: 1,
    UserRole.ADMIN: 2,
}

ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.VIEWER: {"users:read"},
    UserRole.MANAGER: {"users:read", "users:invite", "users:update_role", "invitations:read", "invitations:create"},
    UserRole.ADMIN: {"users:read", "users:invite", "users:update_role", "users:delete", "invitations:read", "invitations:create"},
}


def has_permission(role: UserRole, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def has_minimum_role(user_role: UserRole, required_role: UserRole) -> bool:
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]
