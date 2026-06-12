"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, Team, unwrapList } from "@/lib/api";
import { adminLabel } from "@/lib/adminDisplay";
import { useAuth } from "@/lib/auth";
import { useLocale, useT } from "@/lib/i18n";

const CONTINENT_OPTIONS = [
  "africa",
  "asia",
  "europe",
  "north_america",
  "south_america",
  "oceania",
] as const;

const emptyForm = {
  name: "",
  name_ar: "",
  code: "",
  flag_url: "",
  team_type: "national",
  country_code: "",
  continent: "",
  division: "",
};

export default function AdminTeamsPage() {
  const { token } = useAuth();
  const { locale } = useLocale();
  const t = useT();
  const [teams, setTeams] = useState<Team[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  const load = useCallback(() => {
    if (!token) return;
    setError("");
    api
      .adminGetTeams(token)
      .then((data) => setTeams(unwrapList(data)))
      .catch((err) =>
        setError(err instanceof Error ? err.message : t("failedLoadTeams"))
      );
  }, [token, t]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError("");
    setSuccess("");
    try {
      const payload = {
        ...form,
        division: form.team_type === "club" ? form.division : "",
      };
      if (editingId) {
        await api.adminUpdateTeam(token, editingId, payload);
        setSuccess(t("teamUpdated"));
        setEditingId(null);
      } else {
        await api.adminCreateTeam(token, payload);
        setSuccess(t("teamCreated"));
      }
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedSaveTeam"));
    }
  }

  function startEdit(team: Team) {
    setEditingId(team.id);
    setForm({
      name: team.name,
      name_ar: team.name_ar || "",
      code: team.code,
      flag_url: team.flag_url || "",
      team_type: team.team_type || "national",
      country_code: team.country_code || "",
      continent: team.continent || "",
      division: team.division || "",
    });
  }

  async function handleDelete(id: number) {
    if (!token || !confirm(t("adminDeleteConfirmTeam"))) return;
    try {
      await api.adminDeleteTeam(token, id);
      setSuccess(t("teamDeleted"));
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("failedSaveTeam"));
    }
  }

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">{t("adminTeams")}</h1>
      <p className="mb-6 text-gray-600">{t("adminTeamsDesc")}</p>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {success && <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">{success}</div>}

      <form onSubmit={handleSubmit} className="card mb-8 space-y-4">
        <h2 className="font-semibold">
          {editingId ? t("adminEditTeam") : t("adminAddTeam")}
        </h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminTeamType")}</label>
            <select
              className="input"
              value={form.team_type}
              onChange={(e) => setForm({ ...form, team_type: e.target.value })}
            >
              <option value="national">{t("adminTeamTypeNational")}</option>
              <option value="club">{t("adminTeamTypeClub")}</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("fieldName")}</label>
            <input
              className="input"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("nameAr")}</label>
            <input
              className="input"
              dir="rtl"
              value={form.name_ar}
              onChange={(e) => setForm({ ...form, name_ar: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Code (3 letters)</label>
            <input
              className="input uppercase"
              maxLength={3}
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminTeamCountry")}</label>
            <input
              className="input"
              value={form.country_code}
              onChange={(e) => setForm({ ...form, country_code: e.target.value.toLowerCase() })}
              placeholder="eg, mx, gb-eng"
              required={form.team_type === "club"}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminTeamContinent")}</label>
            <select
              className="input"
              value={form.continent}
              onChange={(e) => setForm({ ...form, continent: e.target.value })}
              required={form.team_type === "national"}
            >
              <option value="">{t("adminSelect")}</option>
              {CONTINENT_OPTIONS.map((c) => (
                <option key={c} value={c}>
                  {c.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </div>
          {form.team_type === "club" && (
            <div>
              <label className="mb-1 block text-sm font-medium">{t("adminTeamDivision")}</label>
              <input
                className="input"
                value={form.division}
                onChange={(e) => setForm({ ...form, division: e.target.value })}
                placeholder="Premier League"
              />
            </div>
          )}
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminFlag")}</label>
            <input
              className="input"
              type="url"
              value={form.flag_url}
              onChange={(e) => setForm({ ...form, flag_url: e.target.value })}
              placeholder="https://flagcdn.com/w80/eg.png"
            />
          </div>
        </div>
        <div className="flex gap-2">
          <button type="submit" className="btn-primary">
            {editingId ? t("update") : t("create")}
          </button>
          {editingId && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setEditingId(null);
                setForm(emptyForm);
              }}
            >
              {t("cancel")}
            </button>
          )}
        </div>
      </form>

      <div className="card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b text-gray-500">
              <th className="py-2 pr-4">{t("adminFlag")}</th>
              <th className="py-2 pr-4">{t("fieldName")}</th>
              <th className="py-2 pr-4">{t("adminTeamType")}</th>
              <th className="py-2 pr-4">{t("adminTeamContinent")}</th>
              <th className="py-2 pr-4">Code</th>
              <th className="py-2">{t("adminActions")}</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((team) => (
              <tr key={team.id} className="border-b border-gray-100">
                <td className="py-2 pr-4">
                  {team.flag_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={team.flag_url} alt="" className="h-5 w-7 object-cover" />
                  ) : (
                    "—"
                  )}
                </td>
                <td className="py-2 pr-4 font-medium">{adminLabel(team, locale)}</td>
                <td className="py-2 pr-4">
                  {team.team_type === "club" ? t("adminTeamTypeClub") : t("adminTeamTypeNational")}
                </td>
                <td className="py-2 pr-4">{team.continent?.replace(/_/g, " ") || "—"}</td>
                <td className="py-2 pr-4">{team.code}</td>
                <td className="py-2">
                  <div className="flex gap-2">
                    <button
                      type="button"
                      className="text-pitch-600 hover:underline"
                      onClick={() => startEdit(team)}
                    >
                      {t("adminEdit")}
                    </button>
                    <button
                      type="button"
                      className="text-red-600 hover:underline"
                      onClick={() => handleDelete(team.id)}
                    >
                      {t("adminDelete")}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
