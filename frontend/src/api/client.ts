import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

// In production: set VITE_API_URL=/api in Vercel dashboard.
// Vercel proxies /api/* to the Render backend (same-origin, so httpOnly cookies work).
// In local dev: VITE_API_URL=http://localhost:8000 (direct connection, no proxy needed).
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// In-memory token store
let _accessToken: string | null = null;


export function getAccessToken(): string | null {
  return _accessToken;
}

export function setAccessToken(token: string): void {
  _accessToken = token;
}

export function clearAccessToken(): void {
  _accessToken = null;
}

const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach access token from memory on every request
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401: attempt a silent token refresh then retry the original request once.
// If the failing request IS the refresh endpoint itself, bail immediately to
// prevent an infinite loop (the refresh cookie is simply absent or expired).
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Never try to refresh when the refresh endpoint itself failed.
    const isRefreshCall =
      typeof originalRequest.url === "string" &&
      originalRequest.url.includes("/auth/refresh");
    if (isRefreshCall) {
      clearAccessToken();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      // Use the raw axios instance (not apiClient) so this call bypasses the
      // interceptor and does not add a stale Bearer token to the refresh request.
      const { data } = await axios.post<{ access_token: string }>(
        `${BASE_URL}/auth/refresh`,
        {},
        { withCredentials: true }
      );

      setAccessToken(data.access_token);

      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      }

      return apiClient(originalRequest);
    } catch (refreshError) {
      clearAccessToken();

      // Only hard-redirect to /login from protected pages, not public ones.
      const publicPaths = ["/login", "/register", "/invite/accept", "/auth/callback"];
      const isPublicPage = publicPaths.some((p) =>
        window.location.pathname.startsWith(p)
      );
      if (!isPublicPage) {
        window.location.replace("/login");
      }
      return Promise.reject(refreshError);
    }
  }
);

// --- Auth API ---
export const authApi = {
  getGoogleAuthUrl: (flow: "register" | "login" | "invite", params?: { org_name?: string; invitation_token?: string }) =>
    apiClient.get<{ auth_url: string }>("/auth/google", { params: { flow, ...params } }),

  refresh: () =>
    apiClient.post<{ access_token: string }>("/auth/refresh"),

  logout: () => {
    clearAccessToken();
    return apiClient.post<{ message: string }>("/auth/logout");
  }
};

// --- Users API ---
export const usersApi = {
  getMe: () => apiClient.get<import("../types").User>("/users/me"),
  list: () => apiClient.get<import("../types").User[]>("/users"),
  updateRole: (userId: string, role: import("../types").UserRole) =>
    apiClient.patch<import("../types").User>(`/users/${userId}/role`, { role }),
  deleteUser: (userId: string) => apiClient.delete(`/users/${userId}`),
};

// --- Organizations API ---
export const organizationsApi = {
  deleteMyOrg: (confirmation: string) =>
    apiClient.delete("/organizations/me", { data: { confirmation } }),
};

// --- Invitations API ---
export const invitationsApi = {
  create: (data: import("../types").CreateInvitationRequest) =>
    apiClient.post<import("../types").Invitation>("/invitations", data),
  list: () => apiClient.get<import("../types").Invitation[]>("/invitations"),
};

// --- Health API ---
export const healthApi = {
  check: () => apiClient.get<{ status: string }>("/health"),
};

export default apiClient;
