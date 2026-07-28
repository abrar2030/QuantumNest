import Link from "next/link";
import { Logo } from "./logo";

const columns = [
  {
    title: "Platform",
    links: [
      { name: "Dashboard", href: "/dashboard" },
      { name: "Portfolios", href: "/portfolio" },
      { name: "Market analysis", href: "/market-analysis" },
      { name: "AI insights", href: "/recommendations" },
    ],
  },
  {
    title: "Company",
    links: [
      { name: "Blockchain explorer", href: "/blockchain-explorer" },
      { name: "Sign in", href: "/auth/login" },
      { name: "Create account", href: "/auth/register" },
    ],
  },
  {
    title: "Legal",
    links: [
      { name: "Privacy policy", href: "/privacy" },
      { name: "Terms of service", href: "/terms" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-surface/40">
      <div className="container grid gap-10 py-14 md:grid-cols-[1.5fr_1fr_1fr_1fr]">
        <div>
          <Logo />
          <p className="mt-4 max-w-xs text-sm text-muted-foreground">
            AI-powered portfolio intelligence and tokenized-asset infrastructure
            for the modern investor.
          </p>
        </div>
        {columns.map((col) => (
          <div key={col.title}>
            <h4 className="font-display text-sm font-semibold">{col.title}</h4>
            <ul className="mt-4 space-y-2.5">
              {col.links.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-border/60 py-6">
        <div className="container flex flex-col items-center justify-between gap-3 text-xs text-muted-foreground sm:flex-row">
          <p>
            © {new Date().getFullYear()} QuantumNest Capital. All rights
            reserved.
          </p>
          <p>Built with AI, blockchain, and a healthy respect for risk.</p>
        </div>
      </div>
    </footer>
  );
}
