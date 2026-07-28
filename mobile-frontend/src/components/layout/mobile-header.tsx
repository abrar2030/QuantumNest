"use client";

import { Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Logo } from "./logo";
import { ThemeToggle } from "./theme-toggle";

export function MobileHeader({ title }: { title?: string }) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border/60 bg-background/90 px-4 backdrop-blur-xl">
      {title ? (
        <p className="font-display text-base font-semibold">{title}</p>
      ) : (
        <Logo iconOnly />
      )}
      <div className="ml-auto flex items-center gap-1">
        <Button variant="ghost" size="icon" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </Button>
        <ThemeToggle />
      </div>
    </header>
  );
}
