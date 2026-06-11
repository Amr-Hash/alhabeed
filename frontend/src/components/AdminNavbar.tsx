"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { APP_NAME } from "@/lib/brand";
import { useAuth } from "@/lib/auth";

const LINKS = [
  { href: "/admin", label: "Overview", exact: true },
  { href: "/admin/matches", label: "Scores" },
  { href: "/admin/tournaments", label: "Tournaments" },
  { href: "/admin/stages", label: "Stages" },
  { href: "/admin/cup-groups", label: "Groups" },
  { href: "/admin/teams", label: "Teams" },
];

export function AdminNavbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  return (
    <nav className="border-b border-amber-200 bg-amber-50">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/admin" className="flex items-center gap-2 text-xl font-bold text-amber-900">
          <span>⚙️</span>
          <span>{APP_NAME}</span>
          <span className="rounded-full bg-amber-200 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-amber-900">
            Admin
          </span>
        </Link>
        <div className="flex flex-wrap items-center gap-2">
          {LINKS.map((item) => {
            const active = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                  active
                    ? "bg-white text-amber-900 shadow-sm"
                    : "text-amber-800 hover:bg-amber-100"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
          <span className="ml-2 text-sm text-amber-700">{user?.username}</span>
          <button onClick={logout} className="btn-secondary border-amber-300 bg-white text-sm">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
