"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Suspense, useState } from "react";
import { CheckCircle2, Loader2, ShieldAlert } from "lucide-react";
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

const schema = z
  .object({
    password: z
      .string()
      .min(8, "Use at least 8 characters")
      .regex(/[A-Z]/, "Include an uppercase letter")
      .regex(/[0-9]/, "Include a number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof schema>;

function ResetPasswordForm() {
  const { post } = useApi();
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { password: "", confirmPassword: "" },
  });

  async function onSubmit(values: FormValues) {
    if (!token) return;
    setIsSubmitting(true);
    try {
      await post("/users/password-reset/confirm", undefined, {
        token,
        new_password: values.password,
      });
      setDone(true);
      toast.success("Password updated. You can now sign in.");
      setTimeout(() => router.push("/auth/login"), 1800);
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

  if (!token) {
    return (
      <div className="space-y-4 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <ShieldAlert className="h-6 w-6" />
        </div>
        <p className="text-sm text-muted-foreground">
          This reset link is missing or invalid. Please request a new one.
        </p>
        <Button className="w-full" asChild>
          <Link href="/auth/forgot-password">Request a new link</Link>
        </Button>
      </div>
    );
  }

  if (done) {
    return (
      <div className="space-y-4 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-success/10 text-success">
          <CheckCircle2 className="h-6 w-6" />
        </div>
        <p className="text-sm text-muted-foreground">
          Your password has been updated. Redirecting you to sign in...
        </p>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>New password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="••••••••"
                  autoComplete="new-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm new password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="••••••••"
                  autoComplete="new-password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
          Update password
        </Button>
      </form>
    </Form>
  );
}

export default function ResetPasswordPage() {
  return (
    <GuestRoute>
      <AuthShell
        title="Set a new password"
        description="Choose a strong password you haven't used before."
      >
        <Suspense
          fallback={
            <Loader2 className="mx-auto h-5 w-5 animate-spin text-primary" />
          }
        >
          <ResetPasswordForm />
        </Suspense>
      </AuthShell>
    </GuestRoute>
  );
}
