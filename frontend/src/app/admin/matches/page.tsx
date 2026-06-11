"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { api, Match, Team, Tournament, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface Stage {
  id: number;
  name: string;
  order: number;
  stage_type: string;
  tournament: number;
}

interface ScoreDraft {
  home_score: string;
  away_score: string;
  status: string;
  winner_team: string;
}

function toDraft(match: Match): ScoreDraft {
  return {
    home_score: match.home_score !== null ? String(match.home_score) : "",
    away_score: match.away_score !== null ? String(match.away_score) : "",
    status: match.status,
    winner_team: match.winner_team ? String(match.winner_team.id) : "",
  };
}

export default function AdminMatchesPage() {
  const { token } = useAuth();
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [stages, setStages] = useState<Stage[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [drafts, setDrafts] = useState<Record<number, ScoreDraft>>({});
  const [tournamentId, setTournamentId] = useState<number | "">("");
  const [statusFilter, setStatusFilter] = useState("");
  const [matchdayFilter, setMatchdayFilter] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [savingId, setSavingId] = useState<number | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    stage: "",
    cup_group: "",
    matchday: "",
    home_team: "",
    away_team: "",
    kickoff_time: "",
    status: "scheduled",
  });

  useEffect(() => {
    if (!token) return;
    Promise.all([
      api.adminGetTournaments(token),
      api.adminGetTeams(token),
    ]).then(([tData, teamData]) => {
      const tList = unwrapList(tData);
      setTournaments(tList);
      setTeams(unwrapList(teamData));
      if (tList.length && !tournamentId) setTournamentId(tList[0].id);
    });
  }, [token, tournamentId]);

  useEffect(() => {
    if (!token || !tournamentId) return;
    api.adminGetStages(token, tournamentId).then((data) => setStages(unwrapList(data)));
  }, [token, tournamentId]);

  const loadMatches = useCallback(() => {
    if (!token || !tournamentId) return;
    const params: { tournament: number; status?: string; matchday?: number } = {
      tournament: tournamentId,
    };
    if (statusFilter) params.status = statusFilter;
    if (matchdayFilter) params.matchday = Number(matchdayFilter);
    api.adminGetMatches(token, params).then((data) => {
      const list = unwrapList(data);
      setMatches(list);
      const nextDrafts: Record<number, ScoreDraft> = {};
      for (const m of list) nextDrafts[m.id] = toDraft(m);
      setDrafts(nextDrafts);
    });
  }, [token, tournamentId, statusFilter, matchdayFilter]);

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  const matchdays = useMemo(() => {
    const days = new Set<number>();
    for (const m of matches) if (m.matchday) days.add(m.matchday);
    return Array.from(days).sort((a, b) => a - b);
  }, [matches]);

  function updateDraft(id: number, patch: Partial<ScoreDraft>) {
    setDrafts((prev) => ({ ...prev, [id]: { ...prev[id], ...patch } }));
  }

  async function saveMatch(match: Match) {
    if (!token) return;
    const draft = drafts[match.id];
    if (!draft) return;
    setSavingId(match.id);
    setError("");
    setSuccess("");
    try {
      const homeScore = draft.home_score === "" ? null : Number(draft.home_score);
      const awayScore = draft.away_score === "" ? null : Number(draft.away_score);
      const winnerTeam = draft.winner_team ? Number(draft.winner_team) : null;

      await api.adminUpdateMatch(token, match.id, {
        status: draft.status,
        home_score: homeScore,
        away_score: awayScore,
        winner_team: winnerTeam,
      });
      setSuccess(`Saved ${match.home_team.code} vs ${match.away_team.code}`);
      loadMatches();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save match.");
    } finally {
      setSavingId(null);
    }
  }

  async function recalculate(matchId: number) {
    if (!token) return;
    try {
      const res = await api.adminRecalculateMatch(token, matchId);
      setSuccess(res.detail);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Recalculate failed.");
    }
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!token || !tournamentId) return;
    setError("");
    setSuccess("");
    try {
      await api.adminCreateMatch(token, {
        tournament: tournamentId,
        stage: Number(createForm.stage),
        home_team: Number(createForm.home_team),
        away_team: Number(createForm.away_team),
        kickoff_time: new Date(createForm.kickoff_time).toISOString(),
        cup_group: createForm.cup_group ? Number(createForm.cup_group) : null,
        matchday: createForm.matchday ? Number(createForm.matchday) : null,
        status: createForm.status,
      });
      setSuccess("Match created.");
      setShowCreate(false);
      loadMatches();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create match.");
    }
  }

  async function handleDelete(id: number) {
    if (!token || !confirm("Delete this match?")) return;
    try {
      await api.adminDeleteMatch(token, id);
      setSuccess("Match deleted.");
      loadMatches();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete match.");
    }
  }

  const needsWinner = (match: Match, draft: ScoreDraft) => {
    if (!match.is_knockout) return false;
    const h = draft.home_score === "" ? null : Number(draft.home_score);
    const a = draft.away_score === "" ? null : Number(draft.away_score);
    return h !== null && a !== null && h === a;
  };

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">Match Scores</h1>
      <p className="mb-6 text-gray-600">
        Enter results and set status to <strong>finished</strong> to award prediction points automatically.
      </p>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {success && <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">{success}</div>}

      <div className="mb-6 flex flex-wrap gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Tournament</label>
          <select
            className="input min-w-[200px]"
            value={tournamentId}
            onChange={(e) => setTournamentId(Number(e.target.value))}
          >
            {tournaments.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} ({t.year})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Status</label>
          <select className="input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All</option>
            <option value="scheduled">Scheduled</option>
            <option value="live">Live</option>
            <option value="finished">Finished</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Matchday</label>
          <select className="input" value={matchdayFilter} onChange={(e) => setMatchdayFilter(e.target.value)}>
            <option value="">All</option>
            {matchdays.map((d) => (
              <option key={d} value={d}>
                MD{d}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-end">
          <button type="button" className="btn-secondary" onClick={() => setShowCreate((v) => !v)}>
            {showCreate ? "Hide form" : "+ Add match"}
          </button>
        </div>
      </div>

      {showCreate && (
        <form onSubmit={handleCreate} className="card mb-8 space-y-4">
          <h2 className="font-semibold">Create Match</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <label className="mb-1 block text-sm font-medium">Stage</label>
              <select
                className="input"
                value={createForm.stage}
                onChange={(e) => setCreateForm({ ...createForm, stage: e.target.value })}
                required
              >
                <option value="">Select stage</option>
                {stages.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Home team</label>
              <select
                className="input"
                value={createForm.home_team}
                onChange={(e) => setCreateForm({ ...createForm, home_team: e.target.value })}
                required
              >
                <option value="">Select team</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.code} — {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Away team</label>
              <select
                className="input"
                value={createForm.away_team}
                onChange={(e) => setCreateForm({ ...createForm, away_team: e.target.value })}
                required
              >
                <option value="">Select team</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.code} — {t.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Kickoff</label>
              <input
                className="input"
                type="datetime-local"
                value={createForm.kickoff_time}
                onChange={(e) => setCreateForm({ ...createForm, kickoff_time: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Matchday</label>
              <input
                className="input"
                type="number"
                min={1}
                value={createForm.matchday}
                onChange={(e) => setCreateForm({ ...createForm, matchday: e.target.value })}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Status</label>
              <select
                className="input"
                value={createForm.status}
                onChange={(e) => setCreateForm({ ...createForm, status: e.target.value })}
              >
                <option value="scheduled">Scheduled</option>
                <option value="live">Live</option>
                <option value="finished">Finished</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn-primary">
            Create Match
          </button>
        </form>
      )}

      <div className="card overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="py-2 pr-3">Fixture</th>
              <th className="py-2 pr-3">Stage / MD</th>
              <th className="py-2 pr-3">Kickoff</th>
              <th className="py-2 pr-3">Score</th>
              <th className="py-2 pr-3">Status</th>
              <th className="py-2 pr-3">Winner</th>
              <th className="py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {matches.map((match) => {
              const draft = drafts[match.id] || toDraft(match);
              const showWinner = needsWinner(match, draft);
              return (
                <tr key={match.id} className="border-b border-gray-100 align-middle">
                  <td className="py-3 pr-3">
                    <span className="font-medium">{match.home_team.code}</span>
                    <span className="mx-1 text-gray-400">vs</span>
                    <span className="font-medium">{match.away_team.code}</span>
                    {match.cup_group_name && (
                      <span className="ml-2 text-xs text-gray-400">Grp {match.cup_group_name}</span>
                    )}
                  </td>
                  <td className="py-3 pr-3 text-gray-600">
                    {match.stage_name}
                    {match.matchday ? ` · MD${match.matchday}` : ""}
                  </td>
                  <td className="py-3 pr-3 whitespace-nowrap text-gray-500">
                    {new Date(match.kickoff_time).toLocaleString()}
                  </td>
                  <td className="py-3 pr-3">
                    <div className="flex items-center gap-1">
                      <input
                        className="input w-14 text-center"
                        type="number"
                        min={0}
                        value={draft.home_score}
                        onChange={(e) => updateDraft(match.id, { home_score: e.target.value })}
                      />
                      <span className="text-gray-400">-</span>
                      <input
                        className="input w-14 text-center"
                        type="number"
                        min={0}
                        value={draft.away_score}
                        onChange={(e) => updateDraft(match.id, { away_score: e.target.value })}
                      />
                    </div>
                  </td>
                  <td className="py-3 pr-3">
                    <select
                      className="input min-w-[110px]"
                      value={draft.status}
                      onChange={(e) => updateDraft(match.id, { status: e.target.value })}
                    >
                      <option value="scheduled">Scheduled</option>
                      <option value="live">Live</option>
                      <option value="finished">Finished</option>
                    </select>
                  </td>
                  <td className="py-3 pr-3">
                    {showWinner ? (
                      <select
                        className="input min-w-[120px]"
                        value={draft.winner_team}
                        onChange={(e) => updateDraft(match.id, { winner_team: e.target.value })}
                      >
                        <option value="">Pick winner</option>
                        <option value={match.home_team.id}>{match.home_team.name}</option>
                        <option value={match.away_team.id}>{match.away_team.name}</option>
                      </select>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="py-3">
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        className="btn-primary text-xs"
                        disabled={savingId === match.id}
                        onClick={() => saveMatch(match)}
                      >
                        {savingId === match.id ? "Saving…" : "Save"}
                      </button>
                      {match.status === "finished" && (
                        <button
                          type="button"
                          className="btn-secondary text-xs"
                          onClick={() => recalculate(match.id)}
                        >
                          Recalc
                        </button>
                      )}
                      <button
                        type="button"
                        className="text-xs text-red-600 hover:underline"
                        onClick={() => handleDelete(match.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {matches.length === 0 && (
          <p className="py-8 text-center text-gray-500">No matches for this filter.</p>
        )}
      </div>
    </div>
  );
}
