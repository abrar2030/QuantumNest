"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Bell,
  Loader2,
  Lock,
  Moon,
  ShieldQuestion,
  Sun,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { getSettings, updateSettings } from "@/lib/settings";
import { ApiError, useApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface SettingsState {
  notifications: { email: boolean; push: boolean; sms: boolean };
  security: { twoFactor: boolean; biometrics: boolean };
  privacy: { dataSharing: boolean; analytics: boolean };
}

function ToggleRow({
  label,
  description,
  checked,
  onCheckedChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between py-3">
      <div className="pr-4">
        <Label className="text-sm font-medium">{label}</Label>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}

function SettingsContent() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();
  const { del } = useApi();
  const router = useRouter();

  const [settings, setSettings] = useState<SettingsState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    getSettings()
      .then((s) =>
        setSettings({
          notifications: s.notifications || {
            email: true,
            push: true,
            sms: false,
          },
          security: s.security || { twoFactor: false, biometrics: false },
          privacy: s.privacy || { dataSharing: true, analytics: true },
        }),
      )
      .finally(() => setIsLoading(false));
  }, []);

  async function patch(partial: Partial<SettingsState>) {
    if (!settings) return;
    const next = { ...settings, ...partial };
    setSettings(next);
    try {
      await updateSettings(next);
    } catch {
      toast.error("Could not save your preference.");
    }
  }

  async function handleDeleteAccount() {
    if (!user) return;
    setIsDeleting(true);
    try {
      await del(`/users/${user.id}`);
      toast.success("Your account has been deleted.");
      logout();
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not delete account.",
      );
      setIsDeleting(false);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your preferences and account."
      />

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          {theme === "dark" ? (
            <Moon className="h-4 w-4 text-primary" />
          ) : (
            <Sun className="h-4 w-4 text-primary" />
          )}
          <CardTitle className="font-display">Appearance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-sm font-medium">Dark mode</Label>
              <p className="text-xs text-muted-foreground">
                Switch between light and dark themes.
              </p>
            </div>
            <Switch
              checked={theme === "dark"}
              onCheckedChange={(checked) =>
                setTheme(checked ? "dark" : "light")
              }
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <Bell className="h-4 w-4 text-primary" />
          <CardTitle className="font-display">Notifications</CardTitle>
        </CardHeader>
        <CardContent className="divide-y divide-border/60">
          {isLoading || !settings ? (
            <Skeleton className="h-32 w-full" />
          ) : (
            <>
              <ToggleRow
                label="Email notifications"
                description="Portfolio alerts, statements, and AI insight summaries."
                checked={settings.notifications.email}
                onCheckedChange={(v) =>
                  patch({
                    notifications: { ...settings.notifications, email: v },
                  })
                }
              />
              <ToggleRow
                label="Push notifications"
                description="Real-time price and recommendation alerts."
                checked={settings.notifications.push}
                onCheckedChange={(v) =>
                  patch({
                    notifications: { ...settings.notifications, push: v },
                  })
                }
              />
              <ToggleRow
                label="SMS notifications"
                description="Critical account and security alerts by text."
                checked={settings.notifications.sms}
                onCheckedChange={(v) =>
                  patch({
                    notifications: { ...settings.notifications, sms: v },
                  })
                }
              />
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <Lock className="h-4 w-4 text-primary" />
          <CardTitle className="font-display">Security</CardTitle>
        </CardHeader>
        <CardContent className="divide-y divide-border/60">
          {isLoading || !settings ? (
            <Skeleton className="h-20 w-full" />
          ) : (
            <>
              <ToggleRow
                label="Two-factor authentication"
                description="Add an extra layer of security at sign-in."
                checked={settings.security.twoFactor}
                onCheckedChange={(v) =>
                  patch({ security: { ...settings.security, twoFactor: v } })
                }
              />
              <ToggleRow
                label="Biometric unlock"
                description="Use Face ID or fingerprint on supported devices."
                checked={settings.security.biometrics}
                onCheckedChange={(v) =>
                  patch({ security: { ...settings.security, biometrics: v } })
                }
              />
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <ShieldQuestion className="h-4 w-4 text-primary" />
          <CardTitle className="font-display">Privacy</CardTitle>
        </CardHeader>
        <CardContent className="divide-y divide-border/60">
          {isLoading || !settings ? (
            <Skeleton className="h-20 w-full" />
          ) : (
            <>
              <ToggleRow
                label="Data sharing"
                description="Share anonymized data to improve AI recommendations."
                checked={settings.privacy.dataSharing}
                onCheckedChange={(v) =>
                  patch({ privacy: { ...settings.privacy, dataSharing: v } })
                }
              />
              <ToggleRow
                label="Analytics"
                description="Help us improve QuantumNest with usage analytics."
                checked={settings.privacy.analytics}
                onCheckedChange={(v) =>
                  patch({ privacy: { ...settings.privacy, analytics: v } })
                }
              />
            </>
          )}
        </CardContent>
      </Card>

      <Card className="border-destructive/30">
        <CardHeader className="flex flex-row items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <CardTitle className="font-display text-destructive">
            Danger zone
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium">Delete account</p>
              <p className="text-xs text-muted-foreground">
                Permanently delete your account and all associated data.
              </p>
            </div>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  variant="outline"
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" /> Delete account
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete your account?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will permanently delete your account, portfolios, and
                    transaction history. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    disabled={isDeleting}
                    onClick={handleDeleteAccount}
                  >
                    {isDeleting && <Loader2 className="h-4 w-4 animate-spin" />}
                    Delete permanently
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
          <Separator className="my-4" />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/dashboard")}
          >
            Back to dashboard
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <AppShell>
      <SettingsContent />
    </AppShell>
  );
}
