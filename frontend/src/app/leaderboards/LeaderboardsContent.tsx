"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, Group, LeaderboardEntry, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LeaderboardsContent() {
  const { user, token, loading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [groups, setGroups] = useState<Group[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<number | "global">(
    searchParams.get("group") ? Number(searchParams.get("group")) : "global"
  );
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!token) return;
    api.getGroups(token).then((data) => setGroups(unwrapList(data)));
  }, [token]);

  useEffect(() => {
    if (!token) return;
    if (selectedGroup === "global") {
      api.getGlobalLeaderboard(token).then(setLeaderboard);
    } else {
      api.getGroupLeaderboard(token, selectedGroup).then(setLeaderboard);
    }
  }, [token, selectedGroup]);

  if (authLoading || !user) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Leaderboards</h1>
      <div className="mb-6">
        <select
          className="input max-w-xs"
          value={selectedGroup}
          onChange={(e) =>
            setSelectedGroup(e.target.value === "global" ? "global" : Number(e.target.value))
          }
        >
          <option value="global">Global Leaderboard</option>
          {groups.map((g) => (
            <option key={g.id} value={g.id}>{g.name}</option>
          ))}
        </select>
      </div>

      <div className="card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="pb-3 pr-4">Rank</th>
              <th className="pb-3 pr-4">Username</th>
              <th className="pb-3 pr-4">Points</th>
              <th className="pb-3 pr-4">Exact</th>
              <th className="pb-3">Outcomes</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry) => (
              <tr key={`${entry.user_id}-${entry.rank}`} className="border-b last:border-0">
                <td className="py-3 pr-4">
                  {entry.rank === 1 ? "🥇" : entry.rank === 2 ? "🥈" : entry.rank === 3 ? "🥉" : entry.rank}
                </td>
                <td className="py-3 pr-4 font-medium">{entry.username}</td>
                <td className="py-3 pr-4 font-bold text-pitch-600">{entry.total_points}</td>
                <td className="py-3 pr-4">{entry.exact_predictions}</td>
                <td className="py-3">{entry.correct_outcomes}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {leaderboard.length === 0 && (
          <p className="py-8 text-center text-gray-500">No rankings yet.</p>
        )}
      </div>
    </div>
  );
}
