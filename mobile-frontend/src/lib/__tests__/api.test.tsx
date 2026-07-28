import { renderHook, waitFor } from "@testing-library/react";
import type React from "react";
import { ApiProvider, useApi } from "../api";

global.fetch = jest.fn();

function wrapper({ children }: { children: React.ReactNode }) {
  return <ApiProvider>{children}</ApiProvider>;
}

describe("API Context", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.localStorage.clear();
  });

  it("provides all API methods", () => {
    const { result } = renderHook(() => useApi(), { wrapper });

    expect(result.current).toHaveProperty("get");
    expect(result.current).toHaveProperty("post");
    expect(result.current).toHaveProperty("postForm");
    expect(result.current).toHaveProperty("put");
    expect(result.current).toHaveProperty("del");
  });

  it("throws error when used outside provider", () => {
    expect(() => {
      renderHook(() => useApi());
    }).toThrow("useApi must be used within an ApiProvider");
  });

  it("persists the token to localStorage", async () => {
    const { result } = renderHook(() => useApi(), { wrapper });

    result.current.setToken("test-token");

    await waitFor(() => {
      expect(window.localStorage.getItem("quantumnest_auth_token")).toBe(
        "test-token",
      );
    });
  });

  it("attaches the bearer token to GET requests", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: { get: () => "application/json" },
      json: async () => ({ hello: "world" }),
    });

    const { result } = renderHook(() => useApi(), { wrapper });
    result.current.setToken("abc123");

    await waitFor(async () => {
      const data = await result.current.get("/users/me");
      expect(data).toEqual({ hello: "world" });
    });

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/users/me"),
      expect.objectContaining({
        method: "GET",
      }),
    );
  });
});
