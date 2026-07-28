"use client";

import type { ReactNode } from "react";
import { ProtectedRoute } from "@/components/auth/route-guards";
import { MobileHeader } from "./mobile-header";
import { BottomNav } from "./bottom-nav";

export function AppShell({
  children,
  title,
  requireAdmin = false,
}: {
  children: ReactNode;
  title?: string;
  requireAdmin?: boolean;
}) {
  return (
    <ProtectedRoute requireAdmin={requireAdmin}>
      <div className="flex min-h-screen flex-col bg-background">
        <MobileHeader title={title} />
        <main className="flex-1 px-4 pb-24 pt-4">
          <div className="mx-auto w-full max-w-lg space-y-5">{children}</div>
        </main>
        <BottomNav />
      </div>
    </ProtectedRoute>
  );
}
