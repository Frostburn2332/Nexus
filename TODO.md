# Nexus -- Implementation Tracker

## Phase 0: Foundation & Planning
- [x] Initial commit (LICENSE, .gitignore)
- [x] README with project overview, tech stack, and setup guide
- [x] Project overview document (`docs/overview.md`)
- [x] Architecture document (`docs/architecture.md`)
- [x] Implementation tracker (`TODO.md`)

## Phase 1: Project Configuration
- [x] Initialize backend project (`pyproject.toml`, `requirements.txt`, package skeleton)
- [x] Initialize frontend project (Vite + React + TypeScript + Tailwind CSS)
- [x] Add environment configuration (`.env.example`)

## Phase 2: Database Layer
- [x] PostgreSQL schema and init scripts (`docker/init-scripts/init.sql`)
- [x] SQLAlchemy models (Organization, User, Invitation)
- [x] Database connection and session factory
- [x] Repository layer (CRUD for organizations, users, invitations)

## Phase 3: Authentication Core
- [x] Google OAuth 2.0 client
- [x] JWT token management (create, verify, refresh)
- [x] RBAC permission system (roles, permission matrix)
- [x] Auth dependencies (`get_current_user`, `require_role`)

## Phase 4: Business Logic
- [x] Organization service (create, lookup)
- [x] User service (CRUD, role assignment, email-org validation)
- [x] Invitation service (create, validate token, accept, email match enforcement)

## Phase 5: Email Service
- [ ] Abstract email provider interface
- [ ] Console email provider (logs invitation links to stdout)

## Phase 6: API Layer
- [x] FastAPI app setup with CORS and lifespan events
- [x] Health check routes
- [x] Auth routes (register, login, callback, logout, refresh)
- [x] User management routes (list, update role, delete)
- [x] Invitation routes (create, accept, list)

## Phase 7: Docker & CI
- [ ] Backend Dockerfile
- [ ] Docker Compose (API + PostgreSQL)
- [ ] GitHub Actions CI pipeline (lint, test, build)

## Phase 8: Tests
- [ ] Test configuration and fixtures
- [ ] Unit tests (services, RBAC)
- [ ] Integration tests (API endpoints, auth flow, invitation flow)

## Phase 9: Frontend -- Core
- [ ] TypeScript types and API client (Axios)
- [ ] Auth context and protected routes
- [ ] Layout and navigation
- [ ] Registration page

## Phase 10: Frontend -- Pages
- [ ] Login page
- [ ] Dashboard and user list
- [ ] Invite user modal
- [ ] Role management and user actions

## Phase 11: Frontend -- Polish
- [ ] Search, filter, and toast notifications
- [ ] Responsive design and UI polish
- [ ] Accept invitation page

## Phase 12: Deployment & Documentation
- [ ] Frontend Docker containerization
- [ ] Comprehensive README (final update)
- [ ] Deployment configuration (Vercel, Render, Neon)
- [ ] Finalize v1.0
