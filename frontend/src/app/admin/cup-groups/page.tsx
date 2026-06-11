"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, CupGroup, Team, Tournament, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function AdminCupGroupsPage() {
  const { token } = useAuth();
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [tournamentId, setTournamentId] = useState<number | "">("");
  const [groups, setGroups] = useState<CupGroup[]>([]);
  const [name, setName] = useState("");
  const [selectedTeamIds, setSelectedTeamIds] = useState<number[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

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

  const loadGroups = useCallback(() => {
    if (!token || !tournamentId) return;
    api.adminGetCupGroups(token, tournamentId).then((data) => setGroups(unwrapList(data)));
  }, [token, tournamentId]);

  useEffect(() => {
    loadGroups();
  }, [loadGroups]);

  function toggleTeam(id: number) {
    setSelectedTeamIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  function startEdit(group: CupGroup) {
    setEditingId(group.id);
    setName(group.name);
    setSelectedTeamIds(group.group_teams.map((gt) => gt.team.id));
  }

  function resetForm() {
    setEditingId(null);
    setName("");
    setSelectedTeamIds([]);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || !tournamentId) return;
    setError("");
    setSuccess("");
    try {
      const payload = { tournament: tournamentId, name: name.toUpperCase(), team_ids: selectedTeamIds };
      if (editingId) {
        await api.adminUpdateCupGroup(token, editingId, payload);
        setSuccess("Group updated.");
      } else {
        await api.adminCreateCupGroup(token, payload);
        setSuccess("Group created.");
      }
      resetForm();
      loadGroups();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save group.");
    }
  }

  async function handleDelete(id: number) {
    if (!token || !confirm("Delete this cup group?")) return;
    try {
      await api.adminDeleteCupGroup(token, id);
      setSuccess("Group deleted.");
      loadGroups();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete group.");
    }
  }

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">Cup Groups</h1>
      <p className="mb-6 text-gray-600">Create tournament groups and assign teams.</p>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {success && <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">{success}</div>}

      <div className="mb-6">
        <label className="mb-1 block text-sm font-medium">Tournament</label>
        <select
          className="input max-w-md"
          value={tournamentId}
          onChange={(e) => {
            setTournamentId(Number(e.target.value));
            resetForm();
          }}
        >
          {tournaments.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name} ({t.year})
            </option>
          ))}
        </select>
      </div>

      <form onSubmit={handleSubmit} className="card mb-8 space-y-4">
        <h2 className="font-semibold">{editingId ? "Edit Group" : "Add Group"}</h2>
        <div>
          <label className="mb-1 block text-sm font-medium">Group letter</label>
          <input
            className="input max-w-xs uppercase"
            maxLength={1}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="A"
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium">Teams</label>
          <div className="grid max-h-48 grid-cols-2 gap-2 overflow-y-auto sm:grid-cols-3">
            {teams.map((team) => (
              <label key={team.id} className="flex items-center gap-2 rounded border px-2 py-1 text-sm">
                <input
                  type="checkbox"
                  checked={selectedTeamIds.includes(team.id)}
                  onChange={() => toggleTeam(team.id)}
                />
                {team.code} — {team.name}
              </label>
            ))}
          </div>
        </div>
        <div className="flex gap-2">
          <button type="submit" className="btn-primary">
            {editingId ? "Update" : "Create"}
          </button>
          {editingId && (
            <button type="button" className="btn-secondary" onClick={resetForm}>
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <div key={group.id} className="card">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-lg font-semibold">Group {group.name}</h3>
              <div className="flex gap-2 text-sm">
                <button type="button" className="text-pitch-600 hover:underline" onClick={() => startEdit(group)}>
                  Edit
                </button>
                <button type="button" className="text-red-600 hover:underline" onClick={() => handleDelete(group.id)}>
                  Delete
                </button>
              </div>
            </div>
            <ul className="space-y-1 text-sm text-gray-600">
              {group.group_teams.map((gt) => (
                <li key={gt.team.id}>
                  {gt.team.code} — {gt.team.name}
                </li>
              ))}
              {group.group_teams.length === 0 && <li className="text-gray-400">No teams assigned</li>}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
