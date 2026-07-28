"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { primaryNavItems } from "@/lib/nav-items";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";
import { Logo } from "./logo";

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { user } = useAuth();

  const items = primaryNavItems.filter(
    (item) => !item.adminOnly || user?.role === "admin",
  );

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center border-b border-sidebar-border px-5">
        <Logo />
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {items.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-primary/15 text-sidebar-primary"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-sidebar-border p-4">
        <div className="rounded-lg bg-gradient-to-br from-primary/15 to-accent/10 p-3.5">
          <p className="font-display text-sm font-semibold text-sidebar-foreground">
            Upgrade to Pro
          </p>
          <p className="mt-1 text-xs text-sidebar-foreground/60">
            Unlock deeper AI insight and smart-contract deployment.
          </p>
        </div>
      </div>
    </div>
  );
}
