"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, Match, Prediction, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function MatchResultsPage() {
  const { id } = useParams<{ id: string }>();
  const { user, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [match, setMatch] = useState<Match | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!token || !id) return;
    Promise.all([
      api.getMatches(token).then((data) => {
        const list = unwrapList(data);
        setMatch(list.find((m) => m.id === Number(id)) || null);
      }),
      api.getPredictions(token).then((data) => {
        setPredictions(unwrapList(data).filter((p) => p.match === Number(id)));
      }),
    ]);
  }, [token, id]);

  if (authLoading || !user) return <div>Loading...</div>;
  if (!match) return <div>Match not found</div>;

  return (
    <div className="mx-auto max-w-2xl">
      <Link href={`/matches/${id}`} className="mb-4 inline-block text-sm text-pitch-600 hover:underline">
        ← Back to match
      </Link>
      <h1 className="mb-6 text-3xl font-bold">Match Results</h1>

      <div className="card mb-6">
        <p className="mb-2 text-sm text-gray-500">{match.stage_name}</p>
        <div className="flex items-center justify-between">
          <p className="font-semibold">{match.home_team.name}</p>
          <p className="text-3xl font-bold">
            {match.home_score} - {match.away_score}
          </p>
          <p className="font-semibold">{match.away_team.name}</p>
        </div>
        <p className="mt-2 text-center text-sm capitalize text-gray-500">Status: {match.status}</p>
        {match.winner_team && (
          <p className="mt-1 text-center text-sm text-pitch-600">
            Winner: {match.winner_team.name}
          </p>
        )}
      </div>

      <h2 className="mb-4 text-xl font-semibold">Your Predictions</h2>
      {predictions.length === 0 ? (
        <p className="text-gray-500">No predictions for this match.</p>
      ) : (
        predictions.map((p) => (
          <div key={p.id} className="card mb-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">
                  Predicted: {p.predicted_home_score}-{p.predicted_away_score}
                </p>
                {p.predicted_winner_team && (
                  <p className="text-sm text-gray-500">
                    Advanced: {p.predicted_winner_team.name}
                  </p>
                )}
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-pitch-600">{p.points_awarded}</p>
                <p className="text-xs text-gray-500">points</p>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
