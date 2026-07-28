"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  Cpu,
  Database,
  HardDrive,
  Megaphone,
  ScrollText,
  Send,
  ServerCog,
  ShieldCheck,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { StatCard } from "@/components/finance/stat-card";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { ApiError, useApi } from "@/lib/api";
import { formatCompactNumber, formatDateWithTime } from "@/lib/utils";
import type {
  AdminDashboard,
  AdminUserRow,
  AdminUsersResponse,
  SystemLog,
  SystemPerformance,
} from "@/lib/types";

const roles = ["admin", "portfolio_manager", "analyst", "user", "api_user"];

function OverviewTab() {
  const { get } = useApi();
  const [data, setData] = useState<AdminDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setData(await get<AdminDashboard>("/admin/dashboard"));
    } catch {
      setError("We couldn't load the admin dashboard.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total users"
          value={formatCompactNumber(data.user_stats.total_users)}
          hint={`${data.user_stats.active_users} active`}
          icon={Users}
        />
        <StatCard
          label="Total portfolios"
          value={formatCompactNumber(data.portfolio_stats.total_portfolios)}
          hint={`${data.portfolio_stats.average_assets_per_portfolio.toFixed(1)} avg. assets`}
          icon={Database}
        />
        <StatCard
          label="Transactions today"
          value={formatCompactNumber(data.transaction_stats.transactions_today)}
          hint={`${data.transaction_stats.total_transactions} all-time`}
          icon={Activity}
        />
        <StatCard
          label="API uptime"
          value={`${data.system_health.api_uptime}%`}
          hint={`${data.system_health.error_rate}% error rate`}
          icon={ServerCog}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="font-display">User tiers</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(data.user_stats.user_tiers).map(([tier, count]) => (
              <div
                key={tier}
                className="flex items-center justify-between text-sm"
              >
                <span className="capitalize text-muted-foreground">{tier}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <AlertCircle className="h-4 w-4 text-warning" />
            <CardTitle className="font-display">Active alerts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.alerts.length === 0 ? (
              <p className="text-sm text-muted-foreground">No active alerts.</p>
            ) : (
              data.alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between rounded-lg border border-border/60 p-3 text-sm"
                >
                  <span>{alert.message}</span>
                  <Badge variant="outline" className="capitalize">
                    {alert.type}
                  </Badge>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function UsersTab() {
  const { get } = useApi();
  const [users, setUsers] = useState<AdminUserRow[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const res = await get<AdminUsersResponse>("/admin/users", { limit: 100 });
      setUsers(res.data);
      setTotal(res.total);
    } catch {
      setError("We couldn't load the user list.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-4">
      {error ? (
        <ErrorState message={error} onRetry={load} />
      ) : isLoading ? (
        <Skeleton className="h-96 w-full" />
      ) : (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="font-display">All users</CardTitle>
            <span className="text-xs text-muted-foreground">{total} total</span>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Tier</TableHead>
                    <TableHead>Joined</TableHead>
                    <TableHead>Active</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user) => (
                    <UserRow
                      key={user.id}
                      user={user}
                      isUpdating={updatingId === user.id}
                      onUpdating={setUpdatingId}
                      onLocalUpdate={(patch) =>
                        setUsers((prev) =>
                          prev.map((u) =>
                            u.id === user.id ? { ...u, ...patch } : u,
                          ),
                        )
                      }
                    />
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function UserRow({
  user,
  isUpdating,
  onUpdating,
  onLocalUpdate,
}: {
  user: AdminUserRow;
  isUpdating: boolean;
  onUpdating: (id: number | null) => void;
  onLocalUpdate: (patch: Partial<AdminUserRow>) => void;
}) {
  const { put } = useApi();

  async function handleRoleChange(role: string) {
    onUpdating(user.id);
    try {
      await put(`/admin/users/${user.id}/role`, undefined, { role });
      onLocalUpdate({ role });
      toast.success(`${user.email}'s role is now ${role}.`);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not update role.",
      );
    } finally {
      onUpdating(null);
    }
  }

  async function handleStatusToggle(checked: boolean) {
    onUpdating(user.id);
    try {
      await put(`/admin/users/${user.id}/status`, undefined, {
        is_active: checked,
      });
      onLocalUpdate({ is_active: checked });
      toast.success(`${user.email} is now ${checked ? "active" : "inactive"}.`);
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not update user status.",
      );
    } finally {
      onUpdating(null);
    }
  }

  return (
    <TableRow>
      <TableCell>
        <p className="font-medium">{user.username || user.email}</p>
        <p className="text-xs text-muted-foreground">{user.email}</p>
      </TableCell>
      <TableCell>
        <Select
          value={user.role}
          onValueChange={handleRoleChange}
          disabled={isUpdating}
        >
          <SelectTrigger className="h-8 w-40 text-xs capitalize">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {roles.map((role) => (
              <SelectItem
                key={role}
                value={role}
                className="text-xs capitalize"
              >
                {role.replace(/_/g, " ")}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TableCell>
      <TableCell className="capitalize text-muted-foreground">
        {user.tier}
      </TableCell>
      <TableCell className="text-xs text-muted-foreground">
        {user.created_at ? formatDateWithTime(user.created_at) : "—"}
      </TableCell>
      <TableCell>
        <Switch
          checked={user.is_active}
          disabled={isUpdating}
          onCheckedChange={handleStatusToggle}
        />
      </TableCell>
    </TableRow>
  );
}

function LogsTab() {
  const { get } = useApi();
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [level, setLevel] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load(selectedLevel?: string) {
    setIsLoading(true);
    setError(null);
    try {
      setLogs(
        await get<SystemLog[]>("/admin/system/logs", {
          limit: 50,
          log_level:
            selectedLevel && selectedLevel !== "all"
              ? selectedLevel
              : undefined,
        }),
      );
    } catch {
      setError("We couldn't load system logs.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const levelStyle: Record<string, string> = {
    ERROR: "bg-destructive/10 text-destructive hover:bg-destructive/10",
    WARNING: "bg-warning/10 text-warning hover:bg-warning/10",
    INFO: "bg-primary/10 text-primary hover:bg-primary/10",
    DEBUG: "bg-muted text-muted-foreground",
  };

  return (
    <div className="space-y-4">
      <Select
        value={level}
        onValueChange={(v) => {
          setLevel(v);
          load(v);
        }}
      >
        <SelectTrigger className="w-44">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All levels</SelectItem>
          <SelectItem value="INFO">Info</SelectItem>
          <SelectItem value="WARNING">Warning</SelectItem>
          <SelectItem value="ERROR">Error</SelectItem>
          <SelectItem value="DEBUG">Debug</SelectItem>
        </SelectContent>
      </Select>

      <Card>
        <CardContent className="p-0">
          {error ? (
            <div className="p-6">
              <ErrorState message={error} onRetry={() => load(level)} />
            </div>
          ) : isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-8 w-full" />
              ))}
            </div>
          ) : logs.length === 0 ? (
            <div className="p-6">
              <EmptyState icon={ScrollText} title="No logs found" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Level</TableHead>
                    <TableHead>Component</TableHead>
                    <TableHead>Message</TableHead>
                    <TableHead>Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>
                        <Badge className={levelStyle[log.log_level] || ""}>
                          {log.log_level}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {log.component}
                      </TableCell>
                      <TableCell className="max-w-md truncate">
                        {log.message}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {formatDateWithTime(log.timestamp)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function PerformanceTab() {
  const { get } = useApi();
  const [data, setData] = useState<SystemPerformance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setData(await get<SystemPerformance>("/admin/system/performance"));
    } catch {
      setError("We couldn't load system performance metrics.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading) return <Skeleton className="h-72 w-full" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <ResourceGauge icon={Cpu} label="CPU usage" value={data.cpu_usage} />
        <ResourceGauge
          icon={ServerCog}
          label="Memory usage"
          value={data.memory_usage}
        />
        <ResourceGauge
          icon={HardDrive}
          label="Disk usage"
          value={data.disk_usage}
        />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="font-display">Database</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Row label="Active connections" value={data.database.connections} />
            <Row
              label="Avg. query time"
              value={`${data.database.query_time_avg}ms`}
            />
            <Row
              label="Active transactions"
              value={data.database.active_transactions}
            />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="font-display">API</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Row
              label="Requests / minute"
              value={data.api.requests_per_minute}
            />
            <Row
              label="Avg. response time"
              value={`${data.api.average_response_time}ms`}
            />
            <Row label="Error rate" value={`${data.api.error_rate}%`} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function ResourceGauge({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Cpu;
  label: string;
  value: number;
}) {
  return (
    <Card>
      <CardContent className="p-5">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Icon className="h-4 w-4" />
          <span className="text-sm">{label}</span>
        </div>
        <p className="mt-2 font-display text-2xl font-semibold">
          {value.toFixed(1)}%
        </p>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={`h-full ${value > 80 ? "bg-destructive" : value > 60 ? "bg-warning" : "bg-primary"}`}
            style={{ width: `${Math.min(value, 100)}%` }}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function AnnouncementsTab() {
  const { post } = useApi();
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit() {
    if (!title || !message) {
      toast.error("Add a title and message before publishing.");
      return;
    }
    setIsSubmitting(true);
    try {
      await post("/admin/announcements", {
        title,
        message,
        target_users: "all",
        expiry_days: 7,
      });
      toast.success("Announcement published.");
      setTitle("");
      setMessage("");
    } catch (err) {
      toast.error(
        err instanceof ApiError
          ? err.message
          : "Could not publish the announcement.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="max-w-xl">
      <CardHeader className="flex flex-row items-center gap-2">
        <Megaphone className="h-4 w-4 text-primary" />
        <CardTitle className="font-display">Publish an announcement</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium">Title</label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Scheduled maintenance"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-sm font-medium">Message</label>
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={4}
            placeholder="We'll be performing scheduled maintenance..."
          />
        </div>
        <Button onClick={submit} disabled={isSubmitting}>
          <Send className="h-4 w-4" /> Publish to all users
        </Button>
      </CardContent>
    </Card>
  );
}

function AdminContent() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Admin console"
        description="Platform health, user management, and operational controls."
        actions={
          <Badge className="bg-primary/15 text-primary hover:bg-primary/15">
            <ShieldCheck className="mr-1 h-3.5 w-3.5" /> Administrator
          </Badge>
        }
      />
      <Tabs defaultValue="overview">
        <TabsList className="flex-wrap">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="announcements">Announcements</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="mt-6">
          <OverviewTab />
        </TabsContent>
        <TabsContent value="users" className="mt-6">
          <UsersTab />
        </TabsContent>
        <TabsContent value="logs" className="mt-6">
          <LogsTab />
        </TabsContent>
        <TabsContent value="performance" className="mt-6">
          <PerformanceTab />
        </TabsContent>
        <TabsContent value="announcements" className="mt-6">
          <AnnouncementsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function AdminPage() {
  return (
    <AppShell requireAdmin>
      <AdminContent />
    </AppShell>
  );
}
