import type { ReactNode } from "react";
import { PublicNavbar } from "./public-navbar";
import { Footer } from "./footer";

export function PublicShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <PublicNavbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </div>
  );
}
