"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { isStaff, isStaffAllowedPath } from "@/lib/staff";

export function StaffGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (loading || !isStaff(user)) return;
    if (!isStaffAllowedPath(pathname)) {
      router.replace("/admin");
    }
  }, [loading, user, pathname, router]);

  return <>{children}</>;
}
