"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, Tournament, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface Stage {
  id: number;
  name: string;
  order: number;
  stage_type: string;
  tournament: number;
}

export default function AdminStagesPage() {
  const { token } = useAuth();
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [tournamentId, setTournamentId] = useState<number | "">("");
  const [stages, setStages] = useState<Stage[]>([]);
  const [form, setForm] = useState({ name: "", order: 1, stage_type: "group" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!token) return;
    api.adminGetTournaments(token).then((data) => {
      const list = unwrapList(data);
      setTournaments(list);
      if (list.length && !tournamentId) setTournamentId(list[0].id);
    });
  }, [token, tournamentId]);

  const loadStages = useCallback(() => {
    if (!token || !tournamentId) return;
    api.adminGetStages(token, tournamentId).then((data) => setStages(unwrapList(data)));
  }, [token, tournamentId]);

  useEffect(() => {
    loadStages();
  }, [loadStages]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token || !tournamentId) return;
    setError("");
    setSuccess("");
    try {
      await api.adminCreateStage(token, { tournament: tournamentId, ...form });
      setSuccess("Stage created.");
      setForm({ name: "", order: stages.length + 1, stage_type: "group" });
      loadStages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create stage.");
    }
  }

  async function handleDelete(id: number) {
    if (!token || !confirm("Delete this stage?")) return;
    try {
      await api.adminDeleteStage(token, id);
      setSuccess("Stage deleted.");
      loadStages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete stage.");
    }
  }

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">Stages</h1>
      <p className="mb-6 text-gray-600">Group stages and knockout rounds for each tournament.</p>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {success && <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">{success}</div>}

      <div className="mb-6">
        <label className="mb-1 block text-sm font-medium">Tournament</label>
        <select
          className="input max-w-md"
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

      <form onSubmit={handleSubmit} className="card mb-8 space-y-4">
        <h2 className="font-semibold">Add Stage</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium">Name</label>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Group Stage MD1"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Order</label>
            <input
              className="input"
              type="number"
              min={1}
              value={form.order}
              onChange={(e) => setForm({ ...form, order: Number(e.target.value) })}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Type</label>
            <select
              className="input"
              value={form.stage_type}
              onChange={(e) => setForm({ ...form, stage_type: e.target.value })}
            >
              <option value="group">Group Stage</option>
              <option value="knockout">Knockout</option>
            </select>
          </div>
        </div>
        <button type="submit" className="btn-primary">
          Create Stage
        </button>
      </form>

      <div className="card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="py-2 pr-4">Order</th>
              <th className="py-2 pr-4">Name</th>
              <th className="py-2 pr-4">Type</th>
              <th className="py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {stages.map((stage) => (
              <tr key={stage.id} className="border-b border-gray-100">
                <td className="py-2 pr-4">{stage.order}</td>
                <td className="py-2 pr-4 font-medium">{stage.name}</td>
                <td className="py-2 pr-4 capitalize">{stage.stage_type}</td>
                <td className="py-2">
                  <button type="button" className="text-red-600 hover:underline" onClick={() => handleDelete(stage.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
