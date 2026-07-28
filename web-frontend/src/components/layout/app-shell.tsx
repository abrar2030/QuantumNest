"use client";

import { useState, type ReactNode } from "react";
import { Bell, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ProtectedRoute } from "@/components/auth/route-guards";
import { SidebarNav } from "./sidebar-nav";
import { ThemeToggle } from "./theme-toggle";
import { UserMenu } from "./user-menu";

export function AppShell({
  children,
  requireAdmin = false,
}: {
  children: ReactNode;
  requireAdmin?: boolean;
}) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <ProtectedRoute requireAdmin={requireAdmin}>
      <div className="min-h-screen bg-background">
        <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 border-r border-sidebar-border bg-sidebar lg:block">
          <SidebarNav />
        </aside>

        <div className="flex min-h-screen flex-col lg:pl-64">
          <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border/60 bg-background/80 px-4 backdrop-blur-xl sm:px-6">
            <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="lg:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-64 border-sidebar-border bg-sidebar p-0"
              >
                <SidebarNav onNavigate={() => setMobileNavOpen(false)} />
              </SheetContent>
            </Sheet>

            <div className="ml-auto flex items-center gap-2">
              <Button variant="ghost" size="icon" aria-label="Notifications">
                <Bell className="h-4 w-4" />
              </Button>
              <ThemeToggle />
              <UserMenu />
            </div>
          </header>

          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <div className="mx-auto w-full max-w-7xl space-y-6">{children}</div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
