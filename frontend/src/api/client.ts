import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

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

// 

// THE FIX: Enhanced Interceptor with Circuit Breaker
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 1. Check if the error is 401 and we haven't tried to retry yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      // If we are already on the login page, don't try to refresh (prevents loops)
      if (window.location.pathname === "/login") {
        return Promise.reject(error);
      }

      originalRequest._retry = true; 

      try {
        // We use the base axios instance here to avoid the interceptor adding 
        // a dead/expired Bearer token to the refresh call itself
        const { data } = await axios.post<{ access_token: string }>(
          `${BASE_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        const newToken = data.access_token;
        setAccessToken(newToken);

        // Update the header for the retry
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }

        return apiClient(originalRequest);
      } catch (refreshError) {
        // IF REFRESH FAILS: The Refresh Token is dead. Wipe everything.
        clearAccessToken();
        
        // Force a hard redirect to break the React state loop
        if (window.location.pathname !== "/login") {
          window.location.replace("/login"); 
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
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