"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Building2, MessageSquare, Brain, FileText,
  Target, BookOpen, Search, AlertTriangle, User, LogOut,
} from "lucide-react";
import { useAuthStore } from "@/stores/authStore";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/experiences", label: "Experiences", icon: MessageSquare },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/interviews", label: "Mock Interviews", icon: Brain },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/weaknesses", label: "Weaknesses", icon: AlertTriangle },
  { href: "/recommendations", label: "Recommendations", icon: BookOpen },
  { href: "/readiness", label: "Readiness", icon: Target },
  { href: "/search", label: "Search", icon: Search },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-background flex flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Brain className="h-6 w-6 text-primary" />
          <span className="font-bold text-lg">PlaceIntel</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
            {user?.full_name?.charAt(0)?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name || "User"}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email || ""}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link
            href="/profile"
            className="flex-1 flex items-center justify-center gap-1 rounded-md border px-2 py-1.5 text-xs hover:bg-accent"
          >
            <User className="h-3 w-3" /> Profile
          </Link>
          <button
            onClick={() => { logout(); window.location.href = "/login"; }}
            className="flex-1 flex items-center justify-center gap-1 rounded-md border px-2 py-1.5 text-xs text-destructive hover:bg-destructive/10"
          >
            <LogOut className="h-3 w-3" /> Logout
          </button>
        </div>
      </div>
    </aside>
  );
}
