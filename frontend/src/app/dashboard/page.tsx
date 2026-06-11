"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, Dashboard } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { MatchCard } from "@/components/MatchCard";

export default function DashboardPage() {
  const { user, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!token) return;
    api.getDashboard(token)
      .then(setDashboard)
      .catch((e) => setError(e.message));
  }, [token]);

  if (authLoading || !user) return <div className="text-center">Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;
  if (!dashboard) return <div className="text-center">Loading dashboard...</div>;

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Dashboard</h1>
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <div className="card bg-pitch-50">
          <p className="text-sm text-gray-600">Total Points</p>
          <p className="text-3xl font-bold text-pitch-700">{dashboard.total_points}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Global Rank</p>
          <p className="text-3xl font-bold">{dashboard.current_rank ?? "—"}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600">Your Groups</p>
          <p className="text-3xl font-bold">{dashboard.groups.length}</p>
        </div>
      </div>

      {dashboard.pending_predictions.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-4 text-xl font-semibold">Pending Predictions</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {dashboard.pending_predictions.map((m) => (
              <MatchCard key={m.id} match={m} showPredictLink />
            ))}
          </div>
        </section>
      )}

      <section className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Upcoming Matches</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {dashboard.upcoming_matches.map((m) => (
            <MatchCard key={m.id} match={m} showPredictLink />
          ))}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Recent Results</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {dashboard.recent_results.map((m) => (
            <MatchCard key={m.id} match={m} showResultLink />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Your Groups</h2>
          <Link href="/groups" className="btn-primary text-sm">
            Manage Groups
          </Link>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {dashboard.groups.map((g) => (
            <div key={g.id} className="card">
              <h3 className="font-semibold">{g.name}</h3>
              <p className="mt-1 text-sm text-gray-500">Code: {g.invite_code}</p>
              <Link
                href={`/leaderboards?group=${g.id}`}
                className="mt-3 inline-block text-sm text-pitch-600 hover:underline"
              >
                View Leaderboard →
              </Link>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
