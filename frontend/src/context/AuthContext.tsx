import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { authApi, clearAccessToken, setAccessToken, usersApi } from "../api/client";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  loginWithGoogle: (flow: "register" | "login" | "invite", params?: { org_name?: string; invitation_token?: string }) => Promise<void>;
  logout: () => Promise<void>;
  setTokenAndFetchUser: (token: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCurrentUser = useCallback(async () => {
    try {
      const { data } = await usersApi.getMe();
      setUser(data);
    } catch {
      setUser(null);
    }
  }, []);

  // On mount, try a silent refresh to restore session from the httpOnly cookie
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const { data } = await authApi.refresh();
        setAccessToken(data.access_token);
        await fetchCurrentUser();
      } catch {
        // No valid session - stay logged out
      } finally {
        setIsLoading(false);
      }
    };
    restoreSession();
  }, [fetchCurrentUser]);

  const loginWithGoogle = useCallback(
    async (
      flow: "register" | "login" | "invite",
      params?: { org_name?: string; invitation_token?: string }
    ) => {
      const { data } = await authApi.getGoogleAuthUrl(flow, params);
      window.location.href = data.auth_url;
    },
    []
  );

  const setTokenAndFetchUser = useCallback(
    async (token: string) => {
      setAccessToken(token);
      await fetchCurrentUser();
    },
    [fetchCurrentUser]
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      clearAccessToken();
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        loginWithGoogle,
        logout,
        setTokenAndFetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
