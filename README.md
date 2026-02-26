# Nexus

A multi-tenant user management web application with Google OAuth 2.0 authentication, role-based access control (RBAC), and invitation-based user onboarding.

## Overview

Nexus allows organizations to manage their users through a secure, role-gated platform. An organization admin registers their company, invites team members via email, and controls access through three distinct roles: **Admin**, **Manager**, and **Viewer**.

### Key Features

- **Multi-tenancy** -- Each organization is isolated. Users belong to exactly one organization, identified by their email + organization combination.
- **Google OAuth 2.0** -- Secure authentication using Google Identity Services. No passwords to manage.
- **Invitation-based onboarding** -- Admins and Managers invite users by email. Invited users complete Google OAuth to activate their account. The OAuth email **must** match the invitation email (401 on mismatch).
- **Role-based access control** -- Three roles with escalating permissions:
  - **Viewer** -- Read-only access to the user list.
  - **Manager** -- Can invite users and assign/modify roles.
  - **Admin** -- Full CRUD access including user deletion.
- **JWT dual-token authentication** -- Short-lived access tokens (~15 min) with refresh token rotation for session continuity.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy |
| **Authentication** | Google OAuth 2.0, JWT (PyJWT) |
| **Database** | PostgreSQL (Neon in production) |
| **Frontend** | React, Vite, TypeScript |
| **Styling** | Tailwind CSS |
| **Containerization** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions |
| **Deployment** | Vercel (frontend), Render (backend), Neon (database) |

## Project Structure

```
Nexus/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── config.py            # Environment configuration
│   │   ├── db/                  # Database connection and session
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # Data access layer (CRUD)
│   │   ├── services/            # Business logic
│   │   ├── auth/                # OAuth, JWT, RBAC, dependencies
│   │   └── routes/              # API endpoints
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios client and API calls
│   │   ├── context/             # Auth state management
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Route-level page components
│   │   └── types/               # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
│
├── docker/
│   ├── docker-compose.yml
│   └── init-scripts/
│
├── tests/
│   ├── unit/
│   └── integration/
│
└── docs/
```

## Problem Breakdown

The project was built incrementally, bottom-up:

1. **Foundation** -- Documentation, architecture decisions, and project scaffolding before any code.
2. **Database layer** -- PostgreSQL schema, SQLAlchemy models, and repository pattern for data access.
3. **Authentication core** -- Google OAuth client, JWT token management, RBAC permission system, and FastAPI auth dependencies.
4. **Business logic** -- Service layer for organizations, users, and invitations -- decoupled from the HTTP layer.
5. **Email service** -- Abstract provider pattern. Console-logged invitation links initially, swappable for a real provider (SendGrid, Resend) later.
6. **API layer** -- FastAPI routes wiring services together with auth guards.
7. **Infrastructure** -- Docker Compose for local development, GitHub Actions CI pipeline.
8. **Testing** -- Unit tests for services and RBAC logic, integration tests for API endpoints.
9. **Frontend** -- React app with auth context, protected routes, and all functional pages.
10. **Deployment** -- Containerized frontend, Vercel/Render/Neon deployment configuration.

Each phase was committed atomically so the repository tells a clear, linear story of how the application was constructed.

## Email-to-Organization Lookup

When a user logs in, the backend determines their organization without requiring them to specify it:

1. User authenticates via Google OAuth and the backend receives their email.
2. The backend queries the `users` table for that email to find the associated `organization_id`.
3. If found, the user is logged in and scoped to that organization.
4. If not found, the user is prompted to either register a new organization or accept a pending invitation.

This means the **login page has no organization input field** -- the email alone resolves the tenant.

For invitations, when an invited user clicks the invitation link and completes OAuth:
- The backend verifies the OAuth email matches the invitation email exactly.
- On match: the user account is activated with the pre-assigned role.
- On mismatch: a `401 Unauthorized` is returned, and the invitation remains pending.

## Email Service Setup

Nexus uses an abstract email provider pattern, making it easy to swap implementations:

- **Development** -- `ConsoleEmailProvider` logs invitation links directly to the backend console. No external service needed.
- **Production** -- Swap in a real provider (e.g., SendGrid, Resend) by implementing the `EmailProvider` interface and updating the environment configuration.

To configure a production email provider:

1. Set the `EMAIL_PROVIDER` environment variable (e.g., `sendgrid`).
2. Add the provider's API key to your environment (e.g., `SENDGRID_API_KEY`).
3. The invitation service automatically uses the configured provider.

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker and Docker Compose
- Google Cloud Console project with OAuth 2.0 credentials

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Nexus.git
   cd Nexus
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Fill in your Google OAuth client ID/secret, database URL, and JWT secret.

3. **Start the database:**
   ```bash
   docker compose -f docker/docker-compose.yml up -d postgres
   ```

4. **Run the backend:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn src.main:app --reload
   ```

5. **Run the frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Open the app:**
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs

## License

MIT
