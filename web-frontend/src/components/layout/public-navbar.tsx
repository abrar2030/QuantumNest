"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Logo } from "./logo";
import { ThemeToggle } from "./theme-toggle";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const links = [
  { name: "Platform", href: "/#platform" },
  { name: "Intelligence", href: "/#intelligence" },
  { name: "Security", href: "/#security" },
];

export function PublicNavbar() {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="container flex h-16 items-center justify-between">
        <Logo />

        <nav className="hidden items-center gap-8 md:flex">
          {pathname === "/" &&
            links.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.name}
              </a>
            ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <ThemeToggle />
          {isAuthenticated ? (
            <Button asChild>
              <Link href="/dashboard">Go to dashboard</Link>
            </Button>
          ) : (
            <>
              <Button variant="ghost" asChild>
                <Link href="/auth/login">Sign in</Link>
              </Button>
              <Button asChild>
                <Link href="/auth/register">Get started</Link>
              </Button>
            </>
          )}
        </div>

        <div className="flex items-center gap-1 md:hidden">
          <ThemeToggle />
          <Button
            variant="ghost"
            size="icon"
            aria-label="Toggle menu"
            onClick={() => setOpen((v) => !v)}
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      <div
        className={cn(
          "overflow-hidden border-b border-border/60 bg-background transition-[max-height] duration-300 md:hidden",
          open ? "max-h-72" : "max-h-0 border-b-0",
        )}
      >
        <div className="container flex flex-col gap-1 py-3">
          {pathname === "/" &&
            links.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={() => setOpen(false)}
                className="rounded-md px-2 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
              >
                {link.name}
              </a>
            ))}
          <div className="mt-2 flex flex-col gap-2 border-t border-border/60 pt-3">
            {isAuthenticated ? (
              <Button asChild>
                <Link href="/dashboard">Go to dashboard</Link>
              </Button>
            ) : (
              <>
                <Button variant="outline" asChild>
                  <Link href="/auth/login">Sign in</Link>
                </Button>
                <Button asChild>
                  <Link href="/auth/register">Get started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
