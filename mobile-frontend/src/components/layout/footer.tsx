import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-border/60 px-4 py-8 text-center">
      <div className="flex justify-center gap-4 text-xs text-muted-foreground">
        <Link href="/privacy" className="hover:text-foreground">
          Privacy
        </Link>
        <Link href="/terms" className="hover:text-foreground">
          Terms
        </Link>
      </div>
      <p className="mt-3 text-xs text-muted-foreground">
        © {new Date().getFullYear()} QuantumNest Capital
      </p>
    </footer>
  );
}
