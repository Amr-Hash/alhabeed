"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AdminCupGroupsRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/admin");
  }, [router]);
  return (
    <div className="py-12 text-center text-gray-500">
      Redirecting…{" "}
      <Link href="/admin" className="text-amber-700 hover:underline">
        Go to tournaments
      </Link>
    </div>
  );
}
