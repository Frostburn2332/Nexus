from src.models import UserRole
from src.auth.rbac import has_permission, has_minimum_role


class TestRoleHierarchy:
    def test_viewer_has_viewer_role(self):
        assert has_minimum_role(UserRole.VIEWER, UserRole.VIEWER) is True

    def test_viewer_lacks_manager_role(self):
        assert has_minimum_role(UserRole.VIEWER, UserRole.MANAGER) is False

    def test_viewer_lacks_admin_role(self):
        assert has_minimum_role(UserRole.VIEWER, UserRole.ADMIN) is False

    def test_manager_has_viewer_role(self):
        assert has_minimum_role(UserRole.MANAGER, UserRole.VIEWER) is True

    def test_manager_has_manager_role(self):
        assert has_minimum_role(UserRole.MANAGER, UserRole.MANAGER) is True

    def test_manager_lacks_admin_role(self):
        assert has_minimum_role(UserRole.MANAGER, UserRole.ADMIN) is False

    def test_admin_has_all_roles(self):
        assert has_minimum_role(UserRole.ADMIN, UserRole.VIEWER) is True
        assert has_minimum_role(UserRole.ADMIN, UserRole.MANAGER) is True
        assert has_minimum_role(UserRole.ADMIN, UserRole.ADMIN) is True


class TestPermissions:
    def test_viewer_can_read_users(self):
        assert has_permission(UserRole.VIEWER, "users:read") is True

    def test_viewer_cannot_invite(self):
        assert has_permission(UserRole.VIEWER, "users:invite") is False

    def test_viewer_cannot_delete(self):
        assert has_permission(UserRole.VIEWER, "users:delete") is False

    def test_viewer_cannot_update_roles(self):
        assert has_permission(UserRole.VIEWER, "users:update_role") is False

    def test_manager_can_invite(self):
        assert has_permission(UserRole.MANAGER, "users:invite") is True

    def test_manager_can_update_roles(self):
        assert has_permission(UserRole.MANAGER, "users:update_role") is True

    def test_manager_cannot_delete(self):
        assert has_permission(UserRole.MANAGER, "users:delete") is False

    def test_manager_can_read_invitations(self):
        assert has_permission(UserRole.MANAGER, "invitations:read") is True

    def test_manager_can_create_invitations(self):
        assert has_permission(UserRole.MANAGER, "invitations:create") is True

    def test_admin_can_delete(self):
        assert has_permission(UserRole.ADMIN, "users:delete") is True

    def test_admin_has_all_permissions(self):
        all_permissions = [
            "users:read", "users:invite", "users:update_role",
            "users:delete", "invitations:read", "invitations:create",
        ]
        for perm in all_permissions:
            assert has_permission(UserRole.ADMIN, perm) is True
