"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Logo } from "./logo";
import { ThemeToggle } from "./theme-toggle";
import { useAuth } from "@/lib/auth-context";

export function PublicNavbar() {
  const { isAuthenticated } = useAuth();

  return (
    <header className="sticky top-0 z-50 flex h-14 items-center gap-2 border-b border-border/60 bg-background/90 px-4 backdrop-blur-xl">
      <Logo />
      <div className="ml-auto flex items-center gap-2">
        <ThemeToggle />
        {isAuthenticated ? (
          <Button size="sm" asChild>
            <Link href="/dashboard">Dashboard</Link>
          </Button>
        ) : (
          <Button size="sm" asChild>
            <Link href="/auth/login">Sign in</Link>
          </Button>
        )}
      </div>
    </header>
  );
}
