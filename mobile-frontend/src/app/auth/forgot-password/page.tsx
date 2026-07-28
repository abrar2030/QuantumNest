"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState } from "react";
import { ArrowLeft, KeyRound, Loader2, MailCheck } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { AuthShell } from "@/components/layout/auth-shell";
import { GuestRoute } from "@/components/auth/route-guards";
import { ApiError, useApi } from "@/lib/api";

const schema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Enter a valid email address"),
});

type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const { post } = useApi();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [devResetLink, setDevResetLink] = useState<string | null>(null);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  });

  async function onSubmit(values: FormValues) {
    setIsSubmitting(true);
    try {
      const response = await post<{ message: string; reset_token?: string }>(
        "/users/password-reset/request",
        undefined,
        { email: values.email },
      );
      setSent(true);
      if (response.reset_token) {
        setDevResetLink(`/auth/reset-password?token=${response.reset_token}`);
      }
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Something went wrong. Please try again.";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <GuestRoute>
      <AuthShell
        title="Reset your password"
        description="We'll send you instructions to get back into your account."
      >
        {sent ? (
          <div className="space-y-5 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-success/10 text-success">
              <MailCheck className="h-6 w-6" />
            </div>
            <div>
              <p className="font-display text-sm font-semibold">
                Check your inbox
              </p>
              <p className="mt-1 text-sm text-muted-foreground">
                If an account exists for that address, we&apos;ve sent a link to
                reset your password. The link expires in 15 minutes.
              </p>
            </div>
            {devResetLink && (
              <div className="rounded-lg border border-dashed border-primary/40 bg-primary/5 p-3 text-left">
                <p className="text-xs font-medium text-primary">
                  Development preview
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  No email service is configured in this environment, so
                  here&apos;s a direct link instead:
                </p>
                <Link
                  href={devResetLink}
                  className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                >
                  <KeyRound className="h-3 w-3" /> Continue to reset password
                </Link>
              </div>
            )}
            <Button variant="outline" className="w-full" asChild>
              <Link href="/auth/login">
                <ArrowLeft className="h-4 w-4" /> Back to sign in
              </Link>
            </Button>
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="you@example.com"
                        autoComplete="email"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                Send reset link
              </Button>
              <Button variant="ghost" className="w-full" asChild>
                <Link href="/auth/login">
                  <ArrowLeft className="h-4 w-4" /> Back to sign in
                </Link>
              </Button>
            </form>
          </Form>
        )}
      </AuthShell>
    </GuestRoute>
  );
}
