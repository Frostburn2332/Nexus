# Nexus -- Architecture


## Architecture Overview

```
┌─────────────────┐     ┌─────────────────────────────────────────┐
│                 │     │              Backend (FastAPI)           │
│   React SPA     │────>│                                         │
│   (Vite + TS)   │<────│  Routes ─> Services ─> Repositories     │
│                 │     │    │                        │            │
│   Tailwind CSS  │     │    │                        ▼            │
│                 │     │  Auth Dependencies     PostgreSQL        │
└─────────────────┘     │  (OAuth, JWT, RBAC)                     │
                        └─────────────────────────────────────────┘
```

The application follows a **layered architecture**:

1. **Routes** -- HTTP request/response handling, input validation, auth guards.
2. **Services** -- Business logic, orchestration, domain rules.
3. **Repositories** -- Data access, SQL queries, no business logic.
4. **Models** -- SQLAlchemy table definitions and enums.

Each layer only depends on the layer directly below it. Routes never touch the database directly; repositories never enforce business rules.

## Database Schema

### organizations

| Column | Type | Constraints |
|--------|------|------------|
| `id` | UUID | PK, default gen_random_uuid() |
| `name` | VARCHAR(255) | NOT NULL |
| `created_at` | TIMESTAMP | NOT NULL, default now() |
| `updated_at` | TIMESTAMP | NOT NULL, default now() |

### users

| Column | Type | Constraints |
|--------|------|------------|
| `id` | UUID | PK, default gen_random_uuid() |
| `organization_id` | UUID | FK -> organizations.id, NOT NULL |
| `email` | VARCHAR(255) | NOT NULL |
| `name` | VARCHAR(255) | NOT NULL |
| `profile_picture` | TEXT | NULLABLE |
| `role` | ENUM('admin', 'manager', 'viewer') | NOT NULL, default 'viewer' |
| `status` | ENUM('active', 'pending') | NOT NULL, default 'pending' |
| `created_at` | TIMESTAMP | NOT NULL, default now() |
| `updated_at` | TIMESTAMP | NOT NULL, default now() |

**Constraints:**
- UNIQUE(`email`, `organization_id`) -- a user can only exist once per org.
- INDEX on `email` -- fast lookup for login (email-to-org resolution).
- INDEX on `organization_id` -- fast listing of all users in an org.

### invitations

| Column | Type | Constraints |
|--------|------|------------|
| `id` | UUID | PK, default gen_random_uuid() |
| `organization_id` | UUID | FK -> organizations.id, NOT NULL |
| `email` | VARCHAR(255) | NOT NULL |
| `name` | VARCHAR(255) | NOT NULL |
| `role` | ENUM('admin', 'manager', 'viewer') | NOT NULL |
| `token` | VARCHAR(255) | UNIQUE, NOT NULL |
| `invited_by` | UUID | FK -> users.id, NOT NULL |
| `status` | ENUM('pending', 'accepted', 'expired') | NOT NULL, default 'pending' |
| `created_at` | TIMESTAMP | NOT NULL, default now() |
| `expires_at` | TIMESTAMP | NOT NULL |

**Constraints:**
- UNIQUE(`token`) -- each invitation link is unique.
- INDEX on `token` -- fast lookup when accepting invitations.
- INDEX on (`organization_id`, `email`) -- prevent duplicate invitations.

## Authentication Flow

### Registration (New Organization)

```
User                    Frontend              Backend              Google
 │                         │                     │                    │
 │  Enter org name         │                     │                    │
 │  Click "Sign up"        │                     │                    │
 │────────────────────────>│                     │                    │
 │                         │  GET /auth/google   │                    │
 │                         │  ?flow=register     │                    │
 │                         │  &org_name=...      │                    │
 │                         │────────────────────>│                    │
 │                         │  redirect URL       │                    │
 │                         │<────────────────────│                    │
 │                         │                     │   OAuth consent    │
 │<────────────────────────│─────────────────────│───────────────────>│
 │  Google login           │                     │                    │
 │────────────────────────>│                     │                    │
 │                         │                     │  GET /auth/callback│
 │                         │                     │  ?code=...         │
 │                         │                     │<───────────────────│
 │                         │                     │  exchange code     │
 │                         │                     │───────────────────>│
 │                         │                     │  user info         │
 │                         │                     │<───────────────────│
 │                         │                     │                    │
 │                         │                     │  Create org        │
 │                         │                     │  Create admin user │
 │                         │                     │  Issue JWT tokens  │
 │                         │  tokens + user data │                    │
 │                         │<────────────────────│                    │
 │  Redirect to dashboard  │                     │                    │
 │<────────────────────────│                     │                    │
```

### Login (Existing User)

```
User                    Frontend              Backend              Google
 │                         │                     │                    │
 │  Click "Sign in"        │                     │                    │
 │────────────────────────>│                     │                    │
 │                         │  GET /auth/google   │                    │
 │                         │  ?flow=login        │                    │
 │                         │────────────────────>│                    │
 │                         │  redirect URL       │                    │
 │                         │<────────────────────│                    │
 │                         │                     │   OAuth consent    │
 │<────────────────────────│─────────────────────│───────────────────>│
 │  Google login           │                     │                    │
 │────────────────────────>│                     │                    │
 │                         │                     │  GET /auth/callback│
 │                         │                     │<───────────────────│
 │                         │                     │  exchange + info   │
 │                         │                     │<──────────────────>│
 │                         │                     │                    │
 │                         │                     │  Lookup user by    │
 │                         │                     │  email -> get org  │
 │                         │                     │  Issue JWT tokens  │
 │                         │  tokens + user data │                    │
 │                         │<────────────────────│                    │
 │  Redirect to dashboard  │                     │                    │
 │<────────────────────────│                     │                    │
```

### Invitation Acceptance

```
Invitee                 Frontend              Backend              Google
 │                         │                     │                    │
 │  Click invitation link  │                     │                    │
 │────────────────────────>│                     │                    │
 │                         │  GET /invitations   │                    │
 │                         │  /accept?token=...  │                    │
 │                         │────────────────────>│                    │
 │                         │  redirect to Google │                    │
 │                         │<────────────────────│                    │
 │  Google login           │                     │                    │
 │────────────────────────>│                     │                    │
 │                         │                     │  GET /auth/callback│
 │                         │                     │<───────────────────│
 │                         │                     │  exchange + info   │
 │                         │                     │<──────────────────>│
 │                         │                     │                    │
 │                         │                     │  Validate:         │
 │                         │                     │  OAuth email ==    │
 │                         │                     │  invitation email? │
 │                         │                     │                    │
 │                         │                     │  YES: activate     │
 │                         │                     │  user, issue JWT   │
 │                         │                     │                    │
 │                         │                     │  NO: 401           │
 │                         │  tokens OR error    │                    │
 │                         │<────────────────────│                    │
 │  Dashboard OR error     │                     │                    │
 │<────────────────────────│                     │                    │
```

## API Contract

### Auth Routes

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/auth/google` | Initiate Google OAuth (query: `flow`, `org_name`, `invitation_token`) | Public |
| GET | `/auth/callback` | Google OAuth callback | Public |
| POST | `/auth/refresh` | Refresh access token | Refresh token |
| POST | `/auth/logout` | Invalidate session | Authenticated |

### User Routes

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users` | List all users in the organization | Viewer+ |
| GET | `/users/me` | Get current user profile | Authenticated |
| PATCH | `/users/{id}/role` | Update a user's role | Manager+ |
| DELETE | `/users/{id}` | Delete a user from the organization | Admin |

### Invitation Routes

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/invitations` | Create a new invitation | Manager+ |
| GET | `/invitations` | List pending invitations for the org | Manager+ |
| GET | `/invitations/accept` | Accept invitation (redirects to OAuth) | Public |

### Health Routes

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Basic health check | Public |
| GET | `/health/db` | Database connectivity check | Public |

## Email-to-Organization Resolution

A critical design decision: **users don't specify their organization at login**. The system resolves it automatically:

1. User authenticates via Google -> backend gets their email.
2. Query `users` table: `SELECT organization_id FROM users WHERE email = ?`
3. If a matching active user is found -> log them in, scoped to that org.
4. If not found -> the user needs to either register a new org or accept a pending invitation.

This works because of the UNIQUE constraint on `(email, organization_id)`. A user can only belong to one organization, so their email unambiguously identifies their tenant.

## Email Provider Pattern

```
EmailProvider (abstract)
├── ConsoleEmailProvider   # Logs to stdout (development)
└── SendGridEmailProvider  # Real delivery (production, added later)
```

The `InvitationService` depends on the abstract `EmailProvider` interface. Swapping providers is a configuration change, not a code change.
