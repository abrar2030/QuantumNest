"use client";

import Link from "next/link";
import { CompassIcon, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PublicShell } from "@/components/layout/public-shell";

export default function NotFound() {
  return (
    <PublicShell>
      <div className="container flex min-h-[70vh] flex-col items-center justify-center py-20 text-center">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
          <CompassIcon className="h-8 w-8" />
        </div>
        <p className="font-display text-6xl font-bold text-primary">404</p>
        <h1 className="mt-4 font-display text-2xl font-semibold">
          This page has drifted off the chart
        </h1>
        <p className="mt-2 max-w-md text-sm text-muted-foreground">
          The page you&apos;re looking for doesn&apos;t exist or may have been
          moved. Let&apos;s get you back on track.
        </p>
        <Button className="mt-8" asChild>
          <Link href="/">
            <Home className="h-4 w-4" /> Back to homepage
          </Link>
        </Button>
      </div>
    </PublicShell>
  );
}
