"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/admin", label: "Overview", exact: true },
  { href: "/admin/matches", label: "Match Scores" },
  { href: "/admin/tournaments", label: "Tournaments" },
  { href: "/admin/stages", label: "Stages" },
  { href: "/admin/cup-groups", label: "Cup Groups" },
  { href: "/admin/teams", label: "Teams" },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
    else if (!loading && user && !(user.is_staff ?? false)) router.push("/dashboard");
  }, [loading, user, router]);

  if (loading || !user) return <div className="py-12 text-center text-gray-500">Loading...</div>;
  if (!(user.is_staff ?? false)) return null;

  return (
    <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
      <aside className="w-full shrink-0 lg:w-56">
        <div className="card sticky top-4 p-4">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
            Admin Panel
          </p>
          <nav className="flex flex-wrap gap-1 lg:flex-col">
            {NAV.map((item) => {
              const active = item.exact
                ? pathname === item.href
                : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                    active
                      ? "bg-pitch-50 text-pitch-700"
                      : "text-gray-600 hover:bg-gray-50 hover:text-pitch-600"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
