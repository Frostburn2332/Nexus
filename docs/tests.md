# Nexus -- Test Cases

> Comprehensive test scenarios covering all backend functionality.

---

## 1. RBAC & Permissions

### 1.1 Role Hierarchy

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | Viewer has minimum role Viewer | `has_minimum_role(VIEWER, VIEWER)` | `True` |
| 2 | Viewer does not have minimum role Manager | `has_minimum_role(VIEWER, MANAGER)` | `False` |
| 3 | Viewer does not have minimum role Admin | `has_minimum_role(VIEWER, ADMIN)` | `False` |
| 4 | Manager has minimum role Viewer | `has_minimum_role(MANAGER, VIEWER)` | `True` |
| 5 | Manager has minimum role Manager | `has_minimum_role(MANAGER, MANAGER)` | `True` |
| 6 | Manager does not have minimum role Admin | `has_minimum_role(MANAGER, ADMIN)` | `False` |
| 7 | Admin has minimum role for all | `has_minimum_role(ADMIN, ADMIN)` | `True` |

### 1.2 Permission Checks

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | Viewer can read users | `has_permission(VIEWER, "users:read")` | `True` |
| 2 | Viewer cannot invite | `has_permission(VIEWER, "users:invite")` | `False` |
| 3 | Viewer cannot delete | `has_permission(VIEWER, "users:delete")` | `False` |
| 4 | Manager can invite | `has_permission(MANAGER, "users:invite")` | `True` |
| 5 | Manager can update roles | `has_permission(MANAGER, "users:update_role")` | `True` |
| 6 | Manager cannot delete | `has_permission(MANAGER, "users:delete")` | `False` |
| 7 | Admin can delete | `has_permission(ADMIN, "users:delete")` | `True` |
| 8 | Admin can do everything | All permissions for ADMIN | All `True` |

---

## 2. JWT Token Management

### 2.1 Token Creation & Verification

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Create access token | `create_access_token(user_id, org_id)` | Valid JWT string with `type: "access"` |
| 2 | Create refresh token | `create_refresh_token(user_id, org_id)` | Valid JWT string with `type: "refresh"` |
| 3 | Verify valid access token | `verify_access_token(token)` | Returns payload with `sub`, `org`, `type`, `exp` |
| 4 | Verify valid refresh token | `verify_refresh_token(token)` | Returns payload with `sub`, `org`, `type`, `exp` |
| 5 | Access token contains correct user ID | Decode token, check `sub` | Matches input `user_id` |
| 6 | Access token contains correct org ID | Decode token, check `org` | Matches input `org_id` |

### 2.2 Token Rejection

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Reject expired access token | Create token with past expiry | `InvalidTokenError` |
| 2 | Reject tampered token | Modify payload of valid token | `InvalidTokenError` |
| 3 | Reject refresh token as access | `verify_access_token(refresh_token)` | `InvalidTokenError("Not an access token")` |
| 4 | Reject access token as refresh | `verify_refresh_token(access_token)` | `InvalidTokenError("Not a refresh token")` |
| 5 | Reject token with wrong secret | Decode with different secret key | `InvalidTokenError` |

---

## 3. Organization Service

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Register new organization | `register("Acme", "admin@acme.com", "Admin")` | Returns `(Organization, User)` with user as ADMIN, ACTIVE |
| 2 | Organization has correct name | Check returned org | `org.name == "Acme"` |
| 3 | Founding user is admin | Check returned user | `user.role == ADMIN` |
| 4 | Founding user is active | Check returned user | `user.status == ACTIVE` |
| 5 | Founding user email matches | Check returned user | `user.email == "admin@acme.com"` |
| 6 | Get org by ID | `get_by_id(org.id)` | Returns the organization |
| 7 | Get org by invalid ID | `get_by_id(random_uuid)` | Returns `None` |

---

## 4. User Service

### 4.1 CRUD Operations

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Get user by ID | `get_by_id(valid_id)` | Returns user |
| 2 | Get user by invalid ID | `get_by_id(random_uuid)` | `404 Not Found` |
| 3 | Get user by email | `get_by_email("user@acme.com")` | Returns user or `None` |
| 4 | List users by organization | `list_by_organization(org_id)` | Returns list of users in that org only |
| 5 | List returns empty for new org | `list_by_organization(empty_org_id)` | Returns `[]` |

### 4.2 Role Updates

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Update role successfully | Manager updates Viewer to Manager | Role updated, returns user |
| 2 | Cannot change own role | Admin tries to change own role | `400 Bad Request` |
| 3 | Cannot change role cross-org | Admin in Org A tries to update user in Org B | `403 Forbidden` |
| 4 | Update to valid role | Change Viewer to Admin | Role is `ADMIN` |

### 4.3 User Deletion

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Delete user successfully | Admin deletes a Viewer | User removed from DB |
| 2 | Cannot delete yourself | Admin tries to delete self | `400 Bad Request` |
| 3 | Cannot delete cross-org | Admin in Org A tries to delete user in Org B | `403 Forbidden` |
| 4 | Deleted user not found | `get_by_id(deleted_id)` | `404 Not Found` |

### 4.4 User Activation

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Activate pending user | `activate_user(pending_user)` | `status == ACTIVE` |
| 2 | Update profile on activation | `activate_user(user, name="New", picture="url")` | Name and picture updated |

---

## 5. Invitation Service

### 5.1 Create Invitation

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Create invitation successfully | Valid email, name, role | Returns invitation with token, status PENDING |
| 2 | Invitation token is unique | Create two invitations | Different tokens |
| 3 | Invitation has 7-day expiry | Check `expires_at` | ~7 days from now |
| 4 | Invitation link printed to console | Create invitation | Console output contains link with token |
| 5 | Reject duplicate email in org | Invite email that already has a user | `409 Conflict` |
| 6 | Reject duplicate pending invitation | Invite same email twice | `409 Conflict` |

### 5.2 Accept Invitation

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Accept with matching email | OAuth email == invitation email | User created, ACTIVE, correct role |
| 2 | Email match is case-insensitive | `User@Acme.com` vs `user@acme.com` | Accepted successfully |
| 3 | Reject mismatched email | OAuth email != invitation email | `401 Unauthorized` |
| 4 | Reject expired invitation | Accept after expiry date | `400 Bad Request`, status set to EXPIRED |
| 5 | Reject already accepted invitation | Accept same token twice | `400 Bad Request` |
| 6 | Reject invalid token | `accept_invitation("bad-token", ...)` | `404 Not Found` |
| 7 | Accepted user has correct org | Check created user | `organization_id` matches invitation |
| 8 | Accepted user has assigned role | Invited as Manager, accept | `user.role == MANAGER` |
| 9 | Invitation status updated | After acceptance | `status == ACCEPTED` |
| 10 | Profile picture stored | Accept with picture URL | `user.profile_picture` is set |

### 5.3 List Invitations

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | List pending invitations | `list_pending(org_id)` | Returns only PENDING invitations |
| 2 | Accepted invitations excluded | After acceptance | Not in pending list |
| 3 | Expired invitations excluded | After expiry | Not in pending list |
| 4 | Empty list for org with no invitations | `list_pending(new_org_id)` | Returns `[]` |

---

## 6. API Endpoints

### 6.1 Health

| # | Test | Endpoint | Expected |
|---|------|----------|----------|
| 1 | Basic health check | `GET /health` | `200`, `{"status": "healthy"}` |
| 2 | Database health check | `GET /health/db` | `200`, `{"status": "healthy", "database": "connected"}` |

### 6.2 Auth Routes

| # | Test | Endpoint | Expected |
|---|------|----------|----------|
| 1 | Get Google auth URL for registration | `GET /auth/google?flow=register&org_name=Acme` | `200`, returns `auth_url` |
| 2 | Get Google auth URL for login | `GET /auth/google?flow=login` | `200`, returns `auth_url` |
| 3 | Get Google auth URL for invitation | `GET /auth/google?flow=invite&invitation_token=...` | `200`, returns `auth_url` |
| 4 | Reject invalid flow | `GET /auth/google?flow=invalid` | `422 Validation Error` |
| 5 | Reject register without org name | `GET /auth/google?flow=register` (no org_name) | `400 Bad Request` |
| 6 | Refresh with valid cookie | `POST /auth/refresh` with refresh token cookie | `200`, new access token |
| 7 | Refresh without cookie | `POST /auth/refresh` (no cookie) | `401 Unauthorized` |
| 8 | Refresh with expired token | `POST /auth/refresh` with expired token | `401 Unauthorized` |
| 9 | Logout clears cookie | `POST /auth/logout` | `200`, refresh token cookie deleted |

### 6.3 User Routes

| # | Test | Endpoint | Expected |
|---|------|----------|----------|
| 1 | List users (authenticated) | `GET /users` with valid token | `200`, list of users in org |
| 2 | List users (unauthenticated) | `GET /users` without token | `401/403` |
| 3 | Get current user | `GET /users/me` with valid token | `200`, current user data |
| 4 | Update role as Manager | `PATCH /users/{id}/role` as Manager | `200`, role updated |
| 5 | Update role as Viewer | `PATCH /users/{id}/role` as Viewer | `403 Forbidden` |
| 6 | Delete user as Admin | `DELETE /users/{id}` as Admin | `204 No Content` |
| 7 | Delete user as Manager | `DELETE /users/{id}` as Manager | `403 Forbidden` |
| 8 | Delete user as Viewer | `DELETE /users/{id}` as Viewer | `403 Forbidden` |

### 6.4 Invitation Routes

| # | Test | Endpoint | Expected |
|---|------|----------|----------|
| 1 | Create invitation as Manager | `POST /invitations` as Manager | `201`, invitation with token |
| 2 | Create invitation as Viewer | `POST /invitations` as Viewer | `403 Forbidden` |
| 3 | Create invitation as Admin | `POST /invitations` as Admin | `201`, invitation with token |
| 4 | List pending as Manager | `GET /invitations` as Manager | `200`, list of pending |
| 5 | List pending as Viewer | `GET /invitations` as Viewer | `403 Forbidden` |
| 6 | Create with invalid email | `POST /invitations` with bad email | `422 Validation Error` |
| 7 | Create with missing fields | `POST /invitations` with empty body | `422 Validation Error` |

---

## 7. Multi-Tenancy Isolation

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Users only see their org's users | User in Org A calls `GET /users` | Only Org A users returned |
| 2 | Cannot update role cross-org | Admin in Org A patches user in Org B | `403 Forbidden` |
| 3 | Cannot delete cross-org | Admin in Org A deletes user in Org B | `403 Forbidden` |
| 4 | Invitations scoped to org | Manager in Org A calls `GET /invitations` | Only Org A invitations |
| 5 | Invitation creates user in correct org | Accept invitation for Org B | User's `organization_id == Org B` |

---

## 8. Edge Cases

| # | Test | Action | Expected |
|---|------|--------|----------|
| 1 | Register with existing email | Register org with email already in another org | `409 Conflict` |
| 2 | Login with unregistered email | Login with email not in any org | `404 Not Found` |
| 3 | Invite existing active user | Invite email already active in org | `409 Conflict` |
| 4 | Re-invite after accepted | Invite email whose invitation was already accepted | `409 Conflict` (user exists) |
| 5 | Token in Authorization header format | `Bearer <token>` format enforced | Missing Bearer prefix returns `401/403` |
| 6 | Empty organization name on register | `flow=register`, `org_name=""` | `400 Bad Request` |
| 7 | Concurrent invitations to same email | Two simultaneous invite requests | One succeeds, one gets `409` |
