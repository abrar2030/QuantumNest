import {
  Blocks,
  LayoutDashboard,
  LineChart,
  Shield,
  Sparkles,
  Wallet,
} from "lucide-react";

export interface NavItem {
  name: string;
  href: string;
  icon: typeof LayoutDashboard;
  adminOnly?: boolean;
}

export const primaryNavItems: NavItem[] = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Portfolios", href: "/portfolio", icon: Wallet },
  { name: "Market", href: "/market-analysis", icon: LineChart },
  { name: "AI Insights", href: "/recommendations", icon: Sparkles },
  { name: "Blockchain", href: "/blockchain-explorer", icon: Blocks },
  { name: "Admin", href: "/admin", icon: Shield, adminOnly: true },
];
