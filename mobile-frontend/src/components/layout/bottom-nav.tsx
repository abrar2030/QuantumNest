"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Blocks,
  LayoutDashboard,
  LineChart,
  LogOut,
  MoreHorizontal,
  Settings,
  Shield,
  Sparkles,
  UserRound,
  Wallet,
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { useAuth } from "@/lib/auth-context";
import { cn, displayName, getInitials } from "@/lib/utils";

const tabs = [
  { name: "Home", href: "/dashboard", icon: LayoutDashboard },
  { name: "Portfolio", href: "/portfolio", icon: Wallet },
  { name: "Market", href: "/market-analysis", icon: LineChart },
  { name: "AI", href: "/recommendations", icon: Sparkles },
];

const moreLinks = [
  { name: "Blockchain Explorer", href: "/blockchain-explorer", icon: Blocks },
  { name: "Profile", href: "/profile", icon: UserRound },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function BottomNav() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [moreOpen, setMoreOpen] = useState(false);

  const isMoreActive = [...moreLinks.map((l) => l.href), "/admin"].some(
    (href) => pathname === href || pathname.startsWith(`${href}/`),
  );

  return (
    <>
      <nav className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background/95 backdrop-blur-xl pb-[env(safe-area-inset-bottom)]">
        <div className="grid grid-cols-5">
          {tabs.map((tab) => {
            const isActive =
              pathname === tab.href || pathname.startsWith(`${tab.href}/`);
            const Icon = tab.icon;
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
                {tab.name}
              </Link>
            );
          })}
          <button
            onClick={() => setMoreOpen(true)}
            className={cn(
              "flex flex-col items-center gap-1 py-2.5 text-[11px] font-medium transition-colors",
              isMoreActive ? "text-primary" : "text-muted-foreground",
            )}
          >
            <MoreHorizontal className="h-5 w-5" />
            More
          </button>
        </div>
      </nav>

      <Sheet open={moreOpen} onOpenChange={setMoreOpen}>
        <SheetContent
          side="bottom"
          className="rounded-t-2xl pb-[calc(env(safe-area-inset-bottom)+1.5rem)]"
        >
          <SheetHeader className="text-left">
            <SheetTitle className="sr-only">More</SheetTitle>
            {user && (
              <div className="flex items-center gap-3 pb-2">
                <Avatar className="h-11 w-11">
                  <AvatarFallback className="bg-primary/15 font-semibold text-primary">
                    {getInitials(displayName(user) || user.email)}
                  </AvatarFallback>
                </Avatar>
                <div className="min-w-0">
                  <p className="truncate font-display text-sm font-semibold">
                    {displayName(user) || user.email}
                  </p>
                  <div className="mt-1 flex gap-1.5">
                    <Badge variant="secondary" className="capitalize">
                      {user.tier}
                    </Badge>
                    {user.role === "admin" && (
                      <Badge className="bg-primary/15 text-primary hover:bg-primary/15">
                        Admin
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            )}
          </SheetHeader>

          <div className="mt-2 space-y-1">
            {moreLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMoreOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium hover:bg-muted"
              >
                <link.icon className="h-4 w-4 text-muted-foreground" />
                {link.name}
              </Link>
            ))}
            {user?.role === "admin" && (
              <Link
                href="/admin"
                onClick={() => setMoreOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium hover:bg-muted"
              >
                <Shield className="h-4 w-4 text-muted-foreground" />
                Admin console
              </Link>
            )}
            <button
              onClick={() => {
                setMoreOpen(false);
                logout();
              }}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm font-medium text-destructive hover:bg-destructive/10"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
