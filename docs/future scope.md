## Future scope for Nexus

### Functional improvements

- **Stronger authentication and security**
  - Implement refresh-token rotation with reuse detection and session revocation.
  - Add a “Sessions & devices” page where users can see and revoke active sessions.
  - Introduce organization-level security settings (allowed email domains, SSO-only mode, optional 2FA/TOTP).
  - Add rate limiting and basic abuse protection on auth and invitation endpoints.
  - During registration, perform a pre-OAuth email availability check on the frontend (via a lightweight backend lookup) and surface a clear error if the address is already in use, instead of sending the user through the Google sign-in flow.
  - Add API keys / personal access tokens for future programmatic access.

- **Multi-tenant and organization features**
  - Optionally support users belonging to multiple organizations with a clean org switcher.
  - Expand organization settings (logo, display name, brand color, default role, soft delete).
  - Introduce per-organization quotas for users, invitations, and API usage to prepare for billing.

- **User lifecycle and governance**
  - Add soft delete and deactivation for users and organizations (keep history, block login).
  - Implement audit logs (user created, invited, role changed, deleted, login events) with an API and UI.
  - Support CSV/JSON export of users and invitations per organization with proper authorization checks.

- **Email and notifications**
  - Replace direct SMTP with an HTTP email provider such as Resend or SendGrid.
  - Add branded email templates per organization (HTML layout, subject, logo).
  - Add in-app notifications (toasts + notification center) for invitations, role changes, and system events.

- **Robustness and correctness**
  - Introduce Alembic migrations and a repeatable migration pipeline for Neon.
  - Standardize error responses and add global exception handlers for FastAPI.
  - Move slow work (email sending, audit logging) into background jobs or a small queue.
  - Add idempotency to invitation creation so repeated submits do not create duplicate invites.

- **APIs and integrations**
  - Add a small public REST API (with API keys) so organizations can sync users programmatically.
  - Expose webhooks for key events (user invited, created, role changed) with signing and retry logic.

### Cosmetic and UX improvements

- **Onboarding and flows**
  - Add a first-time admin onboarding checklist (add logo, invite teammates, configure roles).
  - Improve empty states with clear copy and CTAs instead of blank tables.
  - If multi-org is supported, provide a clear organization switcher with context about the current org.

- **Dashboard usability**
  - Enhance search and filters (by role, status, creation date) with saved filter presets.
  - Add column sorting and pagination or infinite scroll for large user lists.
  - Implement bulk actions (bulk invite from CSV, bulk role change, bulk deactivate).

- **Visual polish**
  - Add light/dark themes with a toggle and persisted preference.
  - Surface organization branding (logo, color) across the header, login/register, and email templates.
  - Add micro-interactions (loading skeletons, hover/active states, transitions, optimistic updates).

### Operational and infra improvements

- **Observability**
  - Add structured, correlated logging (request IDs, user IDs, org IDs) across backend and frontend.
  - Integrate error tracking (e.g. Sentry) in both FastAPI and React.
  - Expose basic metrics (latency, error rates, invitations sent, logins) via a `/metrics` endpoint.

- **Performance and scalability**
  - Introduce caching for common queries (e.g. current user, organization, role lookups).
  - Add and tune database indexes for frequent queries (by org_id, email, status).

- **Deployment and reliability**
  - Improve health/readiness checks (DB connectivity, migrations applied).
  - Harden CI to run linting, type-checking, unit tests, and integration tests on every PR.
  - Document and test disaster recovery steps (Neon backups, secret rotation).

