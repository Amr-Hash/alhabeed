"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, Match, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { MatchCard } from "@/components/MatchCard";

export default function MatchesPage() {
  const { user, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [matches, setMatches] = useState<Match[]>([]);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!token) return;
    api.getMatches(token).then((data) => setMatches(unwrapList(data)));
  }, [token]);

  if (authLoading || !user) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Matches</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {matches.map((m) => (
          <MatchCard key={m.id} match={m} showPredictLink showResultLink />
        ))}
      </div>
    </div>
  );
}
