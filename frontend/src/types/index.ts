export type UserRole = "admin" | "manager" | "viewer";
export type UserStatus = "active" | "pending";
export type InvitationStatus = "pending" | "accepted" | "expired";

export interface Organization {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  organization_id: string;
  email: string;
  name: string;
  profile_picture: string | null;
  role: UserRole;
  status: UserStatus;
  created_at?: string;
  updated_at?: string;
  organization_name?: string;
}

export interface Invitation {
  id: string;
  organization_id: string;
  email: string;
  name: string;
  role: UserRole;
  token: string;
  status: InvitationStatus;
  created_at?: string;
  expires_at?: string;
}

export interface AuthTokens {
  access_token: string;
}

export interface CreateInvitationRequest {
  email: string;
  name: string;
  role: UserRole;
}

export interface UpdateRoleRequest {
  role: UserRole;
}

export interface ApiError {
  detail: string;
}
