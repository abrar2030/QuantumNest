"use client";

import { useRouter } from "next/navigation";
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { ApiError, useApi } from "@/lib/api";
import type { RegisterInput, User } from "@/lib/types";

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  isSubmitting: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterInput) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { token, setToken, get, post, postForm } = useApi();
  const [user, setUser] = useState<User | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const clearError = useCallback(() => setError(null), []);

  const refreshUser = useCallback(async () => {
    try {
      const me = await get<User>("/users/me");
      setUser(me);
    } catch {
      setUser(null);
      setToken(null);
    }
  }, [get, setToken]);

  // On first mount, resolve the current session (if a token was persisted).
  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      // token starts as null until localStorage hydration completes; give it a tick
      await new Promise((resolve) => setTimeout(resolve, 0));
      if (cancelled) return;
      if (!token) {
        setIsInitializing(false);
        return;
      }
      try {
        const me = await get<User>("/users/me");
        if (!cancelled) setUser(me);
      } catch {
        if (!cancelled) setToken(null);
      } finally {
        if (!cancelled) setIsInitializing(false);
      }
    }
    bootstrap();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // Handle 401s raised anywhere in the app by clearing the session.
  useEffect(() => {
    function handleUnauthorized() {
      setUser(null);
      setToken(null);
    }
    window.addEventListener("quantumnest:unauthorized", handleUnauthorized);
    return () =>
      window.removeEventListener(
        "quantumnest:unauthorized",
        handleUnauthorized,
      );
  }, [setToken]);

  const login = useCallback(
    async (email: string, password: string) => {
      setIsSubmitting(true);
      setError(null);
      try {
        const form = new URLSearchParams();
        form.append("username", email);
        form.append("password", password);
        const tokenResponse = await postForm<TokenResponse>("/token", form);
        setToken(tokenResponse.access_token);
        const me = await get<User>("/users/me");
        setUser(me);
        router.push("/dashboard");
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Unable to sign in. Please try again.";
        setError(message);
        throw err;
      } finally {
        setIsSubmitting(false);
      }
    },
    [postForm, get, setToken, router],
  );

  const register = useCallback(
    async (data: RegisterInput) => {
      setIsSubmitting(true);
      setError(null);
      try {
        await post<User>("/users/", {
          email: data.email,
          username: data.username || undefined,
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          password: data.password,
        });
        await login(data.email, data.password);
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Unable to create your account. Please try again.";
        setError(message);
        throw err;
      } finally {
        setIsSubmitting(false);
      }
    },
    [post, login],
  );

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    router.push("/");
  }, [setToken, router]);

  const value: AuthContextType = {
    user,
    isAuthenticated: Boolean(user),
    isInitializing,
    isSubmitting,
    error,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
