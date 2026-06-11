import type { User } from "./api";

export function isStaff(user: User | null | undefined): boolean {
  return Boolean(user?.is_staff);
}

export function staffHomePath(user: User | null | undefined): string {
  return isStaff(user) ? "/admin" : "/dashboard";
}

export function isStaffAllowedPath(pathname: string): boolean {
  return pathname === "/login" || pathname.startsWith("/admin");
}
