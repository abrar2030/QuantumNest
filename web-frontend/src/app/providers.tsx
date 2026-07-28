"use client";

import type { ReactNode } from "react";
import { ThemeProvider } from "next-themes";
import { ApiProvider } from "@/lib/api";
import { AuthProvider } from "@/lib/auth-context";
import { BlockchainProvider } from "@/lib/blockchain";
import { Toaster } from "@/components/ui/sonner";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <ApiProvider>
        <AuthProvider>
          <BlockchainProvider>
            {children}
            <Toaster position="top-right" richColors closeButton />
          </BlockchainProvider>
        </AuthProvider>
      </ApiProvider>
    </ThemeProvider>
  );
}
