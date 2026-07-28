"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState } from "react";
import { Loader2, ShieldCheck, UserRound } from "lucide-react";
import { toast } from "sonner";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { ApiError, useApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { displayName, formatDate, getInitials } from "@/lib/utils";
import type { User } from "@/lib/types";

const profileSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  username: z.string().min(2, "Username must be at least 2 characters"),
  email: z.string().email("Enter a valid email address"),
});

const passwordSchema = z
  .object({
    newPassword: z
      .string()
      .min(8, "Use at least 8 characters")
      .regex(/[A-Z]/, "Include an uppercase letter")
      .regex(/[0-9]/, "Include a number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type ProfileFormValues = z.infer<typeof profileSchema>;
type PasswordFormValues = z.infer<typeof passwordSchema>;

function ProfileContent() {
  const { user, refreshUser } = useAuth();
  const { put } = useApi();
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [isSavingPassword, setIsSavingPassword] = useState(false);

  const profileForm = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    values: {
      firstName: user?.first_name || "",
      lastName: user?.last_name || "",
      username: user?.username || "",
      email: user?.email || "",
    },
  });

  const passwordForm = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { newPassword: "", confirmPassword: "" },
  });

  async function onSaveProfile(values: ProfileFormValues) {
    if (!user) return;
    setIsSavingProfile(true);
    try {
      await put<User>(`/users/${user.id}`, {
        first_name: values.firstName,
        last_name: values.lastName,
        username: values.username,
        email: values.email,
      });
      await refreshUser();
      toast.success("Profile updated.");
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not update profile.",
      );
    } finally {
      setIsSavingProfile(false);
    }
  }

  async function onSavePassword(values: PasswordFormValues) {
    if (!user) return;
    setIsSavingPassword(true);
    try {
      await put<User>(`/users/${user.id}`, { password: values.newPassword });
      toast.success("Password updated.");
      passwordForm.reset();
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not update password.",
      );
    } finally {
      setIsSavingPassword(false);
    }
  }

  if (!user) return null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Profile"
        description="Manage your personal information."
      />

      <Card>
        <CardContent className="flex flex-wrap items-center gap-4 p-6">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="bg-primary/15 text-lg font-semibold text-primary">
              {getInitials(displayName(user) || user.email)}
            </AvatarFallback>
          </Avatar>
          <div>
            <p className="font-display text-lg font-semibold">
              {displayName(user) || user.email}
            </p>
            <p className="text-sm text-muted-foreground">{user.email}</p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              <Badge variant="secondary" className="capitalize">
                {user.tier} tier
              </Badge>
              <Badge variant="outline" className="capitalize">
                {user.role.replace(/_/g, " ")}
              </Badge>
              {user.role === "admin" && (
                <Badge className="bg-primary/15 text-primary hover:bg-primary/15">
                  <ShieldCheck className="mr-1 h-3 w-3" /> Admin
                </Badge>
              )}
            </div>
          </div>
          <p className="ml-auto text-xs text-muted-foreground">
            Member since {formatDate(user.created_at)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <UserRound className="h-4 w-4 text-primary" />
          <CardTitle className="font-display">Personal information</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...profileForm}>
            <form
              onSubmit={profileForm.handleSubmit(onSaveProfile)}
              className="space-y-4"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={profileForm.control}
                  name="firstName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First name</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={profileForm.control}
                  name="lastName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last name</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={profileForm.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Username</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={profileForm.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input type="email" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <Button type="submit" disabled={isSavingProfile}>
                {isSavingProfile && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
                Save changes
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-display">Change password</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...passwordForm}>
            <form
              onSubmit={passwordForm.handleSubmit(onSavePassword)}
              className="space-y-4"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={passwordForm.control}
                  name="newPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>New password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          autoComplete="new-password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={passwordForm.control}
                  name="confirmPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirm new password</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          autoComplete="new-password"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <Button
                type="submit"
                variant="outline"
                disabled={isSavingPassword}
              >
                {isSavingPassword && (
                  <Loader2 className="h-4 w-4 animate-spin" />
                )}
                Update password
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <AppShell>
      <ProfileContent />
    </AppShell>
  );
}
