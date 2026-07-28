"use client";

import Link from "next/link";
import { LayoutGrid, LogOut, Settings, Shield, UserRound } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/lib/auth-context";
import { displayName, getInitials } from "@/lib/utils";

export function UserMenu() {
  const { user, logout } = useAuth();

  if (!user) return null;

  const name = displayName(user) || user.email;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex items-center gap-2 rounded-full border border-border bg-card px-1.5 py-1 pr-3 transition-colors hover:border-primary/40">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="bg-primary/15 text-xs font-semibold text-primary">
              {getInitials(name)}
            </AvatarFallback>
          </Avatar>
          <span className="hidden max-w-[120px] truncate text-sm font-medium sm:inline">
            {name}
          </span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col gap-1">
            <p className="truncate text-sm font-semibold">{name}</p>
            <p className="truncate text-xs text-muted-foreground">
              {user.email}
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
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link href="/dashboard" className="cursor-pointer">
            <LayoutGrid className="mr-2 h-4 w-4" /> Dashboard
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/profile" className="cursor-pointer">
            <UserRound className="mr-2 h-4 w-4" /> Profile
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/settings" className="cursor-pointer">
            <Settings className="mr-2 h-4 w-4" /> Settings
          </Link>
        </DropdownMenuItem>
        {user.role === "admin" && (
          <DropdownMenuItem asChild>
            <Link href="/admin" className="cursor-pointer">
              <Shield className="mr-2 h-4 w-4" /> Admin console
            </Link>
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={logout}
          className="cursor-pointer text-destructive focus:text-destructive"
        >
          <LogOut className="mr-2 h-4 w-4" /> Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
