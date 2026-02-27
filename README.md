# Nexus

A multi-tenant user management web application with Google OAuth 2.0, role-based access control (RBAC), and invitation-based onboarding.

---

## Overview

Nexus lets organizations manage their members through a clean, modern dashboard. An admin registers their organization, invites teammates via email, and controls who has what level of access — all backed by secure Google OAuth sign-in and short-lived JWTs.

### Key capabilities

- **Organization registration** — first user creates an org; all subsequent members join via invitation
- **Google OAuth 2.0** — no passwords; identity is delegated entirely to Google
- **RBAC** — three roles (Admin, Manager, Viewer) with a permission matrix enforced at both the API and UI layers
- **Invitation flow** — admin sends an invitation link; recipient signs in with Google; the backend enforces that the Google email matches the invited address
- **JWT dual-token auth** — short-lived access token (15 min, in-memory) + long-lived refresh token (7 days, httpOnly cookie)
- **Pluggable email** — ships with a console provider (logs invitation links to stdout); swap in SendGrid/Resend by implementing one interface

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async) |
| Auth | Google OAuth 2.0, PyJWT |
| Database | PostgreSQL (Neon in production) |
| Frontend | React 18, Vite, TypeScript |
| Styling | Tailwind CSS |
| Containerization | Docker, Docker Compose |
| CI | GitHub Actions |
| Deployment | Vercel (frontend), Render (backend), Neon (database) |

---

## Repository Structure

```
Nexus/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── config.py            # Pydantic settings (reads .env)
│   │   ├── db/                  # Async engine + session factory
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # CRUD layer (no business logic)
│   │   ├── services/            # Business logic + email provider
│   │   ├── auth/                # OAuth, JWT, RBAC, FastAPI deps
│   │   └── routes/              # FastAPI routers
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios client + typed endpoints
│   │   ├── context/             # Auth context (token storage)
│   │   ├── components/          # Shared UI components
│   │   ├── pages/               # Route-level page components
│   │   ├── hooks/               # Custom React hooks
│   │   └── types/               # TypeScript types
│   ├── Dockerfile               # Multi-stage: Node build → nginx
│   ├── nginx.conf               # SPA routing + security headers
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── docker/
│   ├── docker-compose.yml       # postgres + api + web
│   └── init-scripts/init.sql   # Schema DDL
│
├── tests/
│   ├── conftest.py
│   ├── unit/                    # Service + RBAC unit tests
│   └── integration/             # API endpoint tests
│
├── docs/
│   ├── overview.md
│   └── architecture.md
│
├── .github/workflows/ci.yml
├── .env.example
└── TODO.md
```

---

## Local Development

### Prerequisites

- Python 3.12+
- Node 20+
- Docker + Docker Compose
- A Google Cloud project with OAuth 2.0 credentials

### 1. Clone and configure environment

```bash
git clone https://github.com/<your-username>/Nexus.git
cd Nexus
cp .env.example .env
```

Edit `.env` with your values:

```env
# Google OAuth — create at https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT — generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your-secret-key

# Database (used locally via Docker)
DATABASE_URL=postgresql+asyncpg://nexus:nexus_password@localhost:5432/nexus
```

### 2. Run with Docker Compose (recommended)

```bash
docker compose -f docker/docker-compose.yml up --build
```

This starts three services:
- **postgres** on port `5432` (schema applied automatically via `init.sql`)
- **api** on port `8000` — FastAPI with auto-reload
- **web** on port `80` — React app served by nginx

Open `http://localhost` in your browser.

### 3. Run backend manually

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### 4. Run frontend manually

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:5173`.

---

## Authentication Flow

```
User                    Frontend               Backend              Google
 │                          │                     │                    │
 │  Click "Sign in"         │                     │                    │
 │─────────────────────────>│                     │                    │
 │                          │  GET /auth/google   │                    │
 │                          │────────────────────>│                    │
 │                          │  { auth_url }       │                    │
 │                          │<────────────────────│                    │
 │  Redirect to Google      │                     │                    │
 │<─────────────────────────│                     │                    │
 │                          │                     │                    │
 │  Sign in with Google     │                     │                    │
 │────────────────────────────────────────────────────────────────────>│
 │  Redirect: /auth/callback?code=...             │                    │
 │<────────────────────────────────────────────────────────────────────│
 │                          │  GET /auth/callback │                    │
 │                          │────────────────────>│  Exchange code     │
 │                          │                     │───────────────────>│
 │                          │                     │  { id_token, ... } │
 │                          │                     │<───────────────────│
 │                          │  { access_token }   │  Set refresh cookie│
 │                          │<────────────────────│                    │
```

---

## Role-Based Access Control

| Permission | Viewer | Manager | Admin |
|-----------|--------|---------|-------|
| View users | ✓ | ✓ | ✓ |
| Invite users | | ✓ | ✓ |
| Change user role | | | ✓ |
| Delete users | | | ✓ |

Permissions are enforced server-side via `require_role()` FastAPI dependencies. The frontend additionally hides/disables controls the current user cannot use.

---

## Invitation Flow

1. Admin fills in the Invite User modal (email + role).
2. Backend creates an `Invitation` record with a signed token and logs the link (console provider).
3. Recipient opens the link → lands on `AcceptInvitePage`.
4. Page triggers Google OAuth with the invitation token attached.
5. After Google sign-in, the backend verifies the Google email **matches** the invited email exactly. A mismatch returns `401`.
6. On match, the user account is activated with the assigned role.

---

## Email-to-Org Lookup

On the login page, users enter no organization identifier. Instead, the backend derives the organization from the authenticated Google email by querying which organizations have a matching member record. If exactly one match is found, the user is logged in; multiple matches would present an org selector (not yet implemented — v1.0 assumes one org per user).

---

## Email Provider

The `EmailProvider` abstract class (`backend/src/services/email/provider.py`) defines a single `send_invitation` method. The `ConsoleEmailProvider` implements it by printing the invitation link to stdout — useful for local development without any external service.

To swap in a real provider:

```python
# backend/src/services/email/sendgrid.py
class SendGridEmailProvider(EmailProvider):
    async def send_invitation(self, to_email: str, token: str, org_name: str) -> None:
        # call SendGrid API
        ...
```

Then update `SEND_INVITATION_VIA` in `config.py` or wire it via dependency injection.

---

## API Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | — | Liveness check |
| `GET` | `/health/db` | — | DB readiness check |
| `GET` | `/auth/google` | — | Get OAuth redirect URL |
| `GET` | `/auth/callback` | — | OAuth callback, issues tokens |
| `POST` | `/auth/refresh` | cookie | Rotate access token |
| `POST` | `/auth/logout` | bearer | Revoke refresh token |
| `POST` | `/auth/register` | — | Register org + first admin |
| `GET` | `/users` | bearer | List org members |
| `GET` | `/users/me` | bearer | Current user profile |
| `PATCH` | `/users/{id}/role` | bearer (admin) | Update user role |
| `DELETE` | `/users/{id}` | bearer (admin) | Remove user from org |
| `POST` | `/invitations` | bearer (manager+) | Create invitation |
| `GET` | `/invitations` | bearer | List pending invitations |
| `GET` | `/invitations/accept` | — | Accept invitation (post-OAuth) |

Full interactive docs: `http://localhost:8000/docs`

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

The test suite covers:
- Unit tests for all three services (organization, user, invitation) and the RBAC permission matrix
- Integration tests for the full auth flow, user management endpoints, and invitation acceptance with email-match enforcement

---

## Deployment

### Frontend → Vercel

```bash
# Install Vercel CLI
npm i -g vercel

cd frontend
vercel --prod
```

Set the environment variable in the Vercel dashboard:
```
VITE_API_URL=https://your-render-api.onrender.com
```

The `vercel.json` at the project root configures SPA routing so all paths fall back to `index.html`.

### Backend → Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Point it at the `backend/` directory
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example` in the Render dashboard

The `render.yaml` in the project root defines the service declaratively.

### Database → Neon

1. Create a project at [neon.tech](https://neon.tech)
2. Copy the connection string (use the `postgresql+asyncpg://...` format)
3. Run the schema: paste `docker/init-scripts/init.sql` into the Neon SQL editor
4. Set `DATABASE_URL` in both Render and your local `.env`

---

## Contributing

This project follows conventional commits:

```
feat(scope): short description
fix(scope): short description
docs: short description
test: short description
chore: short description
style(scope): short description
```

Where `scope` is one of: `db`, `auth`, `core`, `api`, `email`, `docker`, `web`, `ci`.
