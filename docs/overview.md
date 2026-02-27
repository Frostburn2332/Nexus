# Nexus -- Project Overview

## Vision

Nexus is a multi-tenant user management platform that enables organizations to onboard, manage, and control access for their team members through a secure, invitation-based workflow powered by Google OAuth 2.0.

## Core Requirements

### 1. Multi-Tenancy

- The application supports multiple organizations, each fully isolated.
- Each user belongs to exactly one organization.
- Users are uniquely identified by their email + organization combination.
- There is no cross-organization visibility or data leakage.

### 2. Organization Registration (First-Time Setup)

- A new user lands on the registration page.
- They enter an organization name.
- They complete Google OAuth login.
- They become the **Admin** of that newly created organization.
- The organization is tied to this founding user's email.

### 3. Authentication

- Google OAuth 2.0 via Google Identity Services.
- Login flow: user clicks "Sign in with Google" -> OAuth completes -> backend issues JWT tokens.
- JWT dual-token pattern:
  - **Access token**: short-lived (~15 minutes), sent in Authorization header.
  - **Refresh token**: longer-lived (~7 days), stored in httpOnly cookie.
- Support for logout and session invalidation.
- Store user profile data: email, name, profile picture URL.

### 4. User Management

**List Users:**
- Display all users in the organization.
- Show active users (completed OAuth login) and pending invitations (haven't logged in yet).

**Invite User:**
- Admins and Managers can send invitations.
- Specify the invitee's email, name, and initial role.
- An invitation link is generated.
- When the invitee clicks the link and completes Google OAuth:
  - The OAuth email **must** match the invitation email.
  - On match: account is activated with the pre-assigned role.
  - On mismatch: `401 Unauthorized` is returned. The invitation stays pending.

**Delete User:**
- Admin-only operation.
- Removes the user from the organization.

**Role Assignment:**
- Admins and Managers can assign or modify user roles.
- Three predefined roles (see Access Control below).

### 5. Access Control (RBAC)

| Permission | Viewer | Manager | Admin |
|-----------|--------|---------|-------|
| View user list | Yes | Yes | Yes |
| Invite users | No | Yes | Yes |
| Assign/modify roles | No | Yes | Yes |
| Delete users | No | No | Yes |

- Permissions are enforced both on the backend (FastAPI dependencies) and frontend (conditional rendering).

## UI Pages

### Registration Page
- Organization name input field.
- "Sign up with Google" button.
- Clean, centered design.

### Login Page
- "Sign in with Google" button.
- No organization input needed -- the organization is auto-detected from the user's email.

### Dashboard / User List
- Organization name displayed prominently.
- User table or card grid showing:
  - Profile picture (if activated).
  - Name.
  - Email.
  - Role (color-coded badge).
  - Status (Active / Pending).
  - Action buttons (Edit role, Delete -- Admin only).
- "Invite User" button visible to Managers and Admins.
- Search and filter functionality (by name/email, by role, by status).

### Invite User Modal
- Form fields: email, name, role dropdown.
- Input validation for required fields.
- Generates and displays the invitation link.
- Success/error toast notifications.

### Accept Invitation Page
- Landing page from the invitation link.
- Triggers Google OAuth flow.
- Handles email mismatch error gracefully.

## Deliverables

1. **GitHub Repository** with clean commit history and clear project structure.
2. **README.md** with project overview, tech stack, setup instructions, and architecture explanation.
3. **Live Demo** with deployed application and working OAuth flows.
4. **`.env.example`** files with all required environment variables documented.
