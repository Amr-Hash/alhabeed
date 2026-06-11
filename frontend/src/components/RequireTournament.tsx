"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import { useTournament } from "@/lib/tournament";
import { EmptyState } from "@/components/EmptyState";

export function RequireTournament({ children }: { children: React.ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const { selectedTournament, loading: tournamentLoading, error } = useTournament();
  const router = useRouter();

  useEffect(() => {
    if (authLoading || tournamentLoading) return;
    if (user && !selectedTournament && !error) {
      router.replace("/");
    }
  }, [authLoading, tournamentLoading, user, selectedTournament, error, router]);

  if (authLoading || tournamentLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-gray-500">
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon="⚠️"
        title="Could not load tournaments"
        description={error}
        action={{ label: "Back to home", href: "/" }}
      />
    );
  }

  if (!selectedTournament) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-gray-500">
        Redirecting to tournament selection...
      </div>
    );
  }

  return <>{children}</>;
}
