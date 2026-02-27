import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from "axios";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

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

// On 401, attempt a silent token refresh once then retry
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const { data } = await axios.post<{ access_token: string }>(
          `${BASE_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );
        setAccessToken(data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch {
        clearAccessToken();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// In-memory token store (never written to localStorage)
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

// --- Auth ---
export const authApi = {
  getGoogleAuthUrl: (flow: "register" | "login" | "invite", params?: { org_name?: string; invitation_token?: string }) =>
    apiClient.get<{ auth_url: string }>("/auth/google", { params: { flow, ...params } }),

  refresh: () =>
    apiClient.post<{ access_token: string }>("/auth/refresh"),

  logout: () =>
    apiClient.post<{ message: string }>("/auth/logout"),
};

// --- Users ---
export const usersApi = {
  getMe: () =>
    apiClient.get<import("../types").User>("/users/me"),

  list: () =>
    apiClient.get<import("../types").User[]>("/users"),

  updateRole: (userId: string, role: import("../types").UserRole) =>
    apiClient.patch<import("../types").User>(`/users/${userId}/role`, { role }),

  deleteUser: (userId: string) =>
    apiClient.delete(`/users/${userId}`),
};

// --- Invitations ---
export const invitationsApi = {
  create: (data: import("../types").CreateInvitationRequest) =>
    apiClient.post<import("../types").Invitation>("/invitations", data),

  list: () =>
    apiClient.get<import("../types").Invitation[]>("/invitations"),
};

// --- Health ---
export const healthApi = {
  check: () =>
    apiClient.get<{ status: string }>("/health"),
};

export default apiClient;
