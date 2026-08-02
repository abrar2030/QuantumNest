import type { Metadata, Viewport } from "next";
import "@fontsource-variable/inter";
import "@fontsource-variable/space-grotesk";
import "@fontsource-variable/jetbrains-mono";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: {
    default: "QuantumNest Capital | AI-Powered Investment Platform",
    template: "%s | QuantumNest Capital",
  },
  description:
    "QuantumNest Capital is a futuristic fintech platform combining AI-driven analytics, portfolio optimization, and blockchain-tokenized assets for the modern investor.",
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#080a12",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      {/* suppressHydrationWarning here guards against browser extensions
          (ad blockers, converters, password managers, etc.) injecting
          attributes into <body> before React hydrates — that's an
          extension-caused mismatch, not an app bug, and is safe to ignore. */}
      <body className="font-sans" suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
