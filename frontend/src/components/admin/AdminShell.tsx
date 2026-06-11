"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { isStaff } from "@/lib/staff";

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
    else if (!loading && user && !isStaff(user)) router.push("/dashboard");
  }, [loading, user, router]);

  if (loading || !user) return <div className="py-12 text-center text-gray-500">Loading...</div>;
  if (!isStaff(user)) return null;

  return <>{children}</>;
}
