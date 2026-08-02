import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { ApiProvider, useApi } from "@/lib/api";

/**
 * Regression test for a race condition where, immediately after login,
 * GET /users/me was fired with a stale (missing) Authorization header
 * because it used the `get` function captured before the token state
 * update had committed. See auth-context.tsx `login()`:
 *
 *   setToken(tokenResponse.access_token);
 *   const me = await get<User>("/users/me"); // used to send no token here
 *
 * This reproduces just the header-timing part of that sequence directly
 * against ApiProvider, without needing the full AuthProvider/router stack.
 */
describe("ApiProvider token race condition", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    window.localStorage.clear();
    jest.clearAllMocks();
  });

  it("sends the new token on a request made immediately after setToken(), not the stale one", async () => {
    const capturedAuthHeaders: Array<string | null> = [];

    global.fetch = jest.fn(async (_url, init) => {
      const headers = init?.headers as Record<string, string>;
      capturedAuthHeaders.push(headers?.Authorization ?? null);
      return {
        ok: true,
        status: 200,
        headers: { get: () => "application/json" },
        json: async () => ({ id: 1, email: "test@example.com" }),
      } as unknown as Response;
    });

    const wrapper = ({ children }: { children: ReactNode }) => (
      <ApiProvider>{children}</ApiProvider>
    );
    const { result } = renderHook(() => useApi(), { wrapper });

    // Mirrors what login() does: set the token, then immediately (same
    // tick, before any re-render) fire an authenticated request.
    await act(async () => {
      result.current.setToken("brand-new-token");
      await result.current.get("/users/me");
    });

    expect(capturedAuthHeaders).toEqual(["Bearer brand-new-token"]);
  });
});
