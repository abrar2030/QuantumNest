"use client";

import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

type QueryParams = Record<string, string | number | boolean | undefined | null>;

interface ApiContextType {
  apiUrl: string;
  token: string | null;
  setToken: (token: string | null) => void;
  get: <T>(endpoint: string, params?: QueryParams) => Promise<T>;
  post: <T>(
    endpoint: string,
    data?: unknown,
    params?: QueryParams,
  ) => Promise<T>;
  postForm: <T>(endpoint: string, form: URLSearchParams) => Promise<T>;
  put: <T>(
    endpoint: string,
    data?: unknown,
    params?: QueryParams,
  ) => Promise<T>;
  del: <T>(endpoint: string, params?: QueryParams) => Promise<T>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

const TOKEN_KEY = "quantumnest_auth_token";

function buildQuery(params?: QueryParams): string {
  if (!params) return "";
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.append(key, String(value));
    }
  });
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function ApiProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  // Mirrors `token`, but updates synchronously (unlike React state) so that
  // a request fired immediately after setToken() — before the next render —
  // still picks up the new value instead of a stale, closed-over one.
  const tokenRef = useRef<string | null>(null);
  const [hydrated, setHydrated] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = window.localStorage.getItem(TOKEN_KEY);
      if (saved) {
        tokenRef.current = saved;
        setTokenState(saved);
      }
    }
    setHydrated(true);
  }, []);

  const setToken = useCallback((newToken: string | null) => {
    tokenRef.current = newToken;
    setTokenState(newToken);
    if (typeof window !== "undefined") {
      if (newToken) {
        window.localStorage.setItem(TOKEN_KEY, newToken);
      } else {
        window.localStorage.removeItem(TOKEN_KEY);
      }
    }
  }, []);

  const handleResponse = useCallback(async (response: Response) => {
    if (!response.ok) {
      let detail: unknown;
      try {
        detail = await response.json();
      } catch {
        detail = null;
      }
      const message =
        (detail && typeof detail === "object" && "detail" in detail
          ? String((detail as { detail: unknown }).detail)
          : null) || `Request failed with status ${response.status}`;

      if (response.status === 401 && typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("quantumnest:unauthorized"));
      }

      throw new ApiError(message, response.status, detail);
    }

    if (response.status === 204) {
      return undefined as unknown;
    }

    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    return response.text();
  }, []);

  const authHeaders = useCallback((extra?: HeadersInit): HeadersInit => {
    const headers: Record<string, string> = {};
    if (tokenRef.current) headers.Authorization = `Bearer ${tokenRef.current}`;
    return { ...headers, ...(extra as Record<string, string>) };
  }, []);

  const get = useCallback(
    async <T,>(endpoint: string, params?: QueryParams): Promise<T> => {
      const response = await fetch(
        `${apiUrl}${endpoint}${buildQuery(params)}`,
        {
          method: "GET",
          headers: authHeaders(),
        },
      );
      return handleResponse(response) as Promise<T>;
    },
    [apiUrl, authHeaders, handleResponse],
  );

  const post = useCallback(
    async <T,>(
      endpoint: string,
      data?: unknown,
      params?: QueryParams,
    ): Promise<T> => {
      const response = await fetch(
        `${apiUrl}${endpoint}${buildQuery(params)}`,
        {
          method: "POST",
          headers: authHeaders({ "Content-Type": "application/json" }),
          body: data !== undefined ? JSON.stringify(data) : undefined,
        },
      );
      return handleResponse(response) as Promise<T>;
    },
    [apiUrl, authHeaders, handleResponse],
  );

  const postForm = useCallback(
    async <T,>(endpoint: string, form: URLSearchParams): Promise<T> => {
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: "POST",
        headers: authHeaders({
          "Content-Type": "application/x-www-form-urlencoded",
        }),
        body: form.toString(),
      });
      return handleResponse(response) as Promise<T>;
    },
    [apiUrl, authHeaders, handleResponse],
  );

  const put = useCallback(
    async <T,>(
      endpoint: string,
      data?: unknown,
      params?: QueryParams,
    ): Promise<T> => {
      const response = await fetch(
        `${apiUrl}${endpoint}${buildQuery(params)}`,
        {
          method: "PUT",
          headers: authHeaders({ "Content-Type": "application/json" }),
          body: data !== undefined ? JSON.stringify(data) : undefined,
        },
      );
      return handleResponse(response) as Promise<T>;
    },
    [apiUrl, authHeaders, handleResponse],
  );

  const del = useCallback(
    async <T,>(endpoint: string, params?: QueryParams): Promise<T> => {
      const response = await fetch(
        `${apiUrl}${endpoint}${buildQuery(params)}`,
        {
          method: "DELETE",
          headers: authHeaders(),
        },
      );
      return handleResponse(response) as Promise<T>;
    },
    [apiUrl, authHeaders, handleResponse],
  );

  const value: ApiContextType = {
    apiUrl,
    token: hydrated ? token : null,
    setToken,
    get,
    post,
    postForm,
    put,
    del,
  };

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
}

export function useApi() {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error("useApi must be used within an ApiProvider");
  }
  return context;
}
