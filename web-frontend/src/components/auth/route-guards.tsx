"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { Loader2 } from "lucide-react";

function FullScreenLoader({ label }: { label: string }) {
  return (
    <div className="flex min-h-[60vh] w-full flex-col items-center justify-center gap-3 text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <p className="text-sm">{label}</p>
    </div>
  );
}

/** Wraps pages that require an authenticated session. */
export function ProtectedRoute({
  children,
  requireAdmin = false,
}: {
  children: React.ReactNode;
  requireAdmin?: boolean;
}) {
  const { isAuthenticated, isInitializing, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isInitializing) return;
    if (!isAuthenticated) {
      router.replace("/auth/login");
      return;
    }
    if (requireAdmin && user && user.role !== "admin") {
      router.replace("/dashboard");
    }
  }, [isInitializing, isAuthenticated, requireAdmin, user, router]);

  if (isInitializing) {
    return <FullScreenLoader label="Loading your session..." />;
  }

  if (!isAuthenticated) {
    return <FullScreenLoader label="Redirecting to sign in..." />;
  }

  if (requireAdmin && user && user.role !== "admin") {
    return <FullScreenLoader label="Redirecting..." />;
  }

  return <>{children}</>;
}

/** Wraps pages (login/register) that signed-in users shouldn't see. */
export function GuestRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isInitializing } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isInitializing && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isInitializing, isAuthenticated, router]);

  if (!isInitializing && isAuthenticated) {
    return <FullScreenLoader label="Redirecting to your dashboard..." />;
  }

  return <>{children}</>;
}
