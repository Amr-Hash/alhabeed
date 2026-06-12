"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { api, StandingRuleSet, unwrapList } from "@/lib/api";
import { adminLabel } from "@/lib/adminDisplay";
import { useAuth } from "@/lib/auth";
import { useLocale, useT } from "@/lib/i18n";
import type { MessageKey } from "@/lib/messages";

const COMPETITION_TYPE_KEYS: Record<string, MessageKey> = {
  world_cup: "adminRuleTypeWorldCup",
  champions_league: "adminRuleTypeChampionsLeague",
  other: "adminRuleTypeOther",
};

const ENGINE_KEYS: Record<string, MessageKey> = {
  fifa_world_cup: "adminStandingRulesFifa",
  uefa_champions_league: "adminStandingRulesUefa",
  simple: "adminStandingRulesSimple",
};

const emptyForm = {
  slug: "",
  name: "",
  name_ar: "",
  competition_type: "world_cup",
  version: "",
  engine: "fifa_world_cup",
  qualifiers_per_group: 2,
  best_third_place_qualifiers: 0,
  is_active: true,
};

function suggestedSlug(competitionType: string, version: string) {
  const base = `${competitionType}-${version || "v1"}`
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return base;
}

export default function AdminStandingRulesPage() {
  const { token } = useAuth();
  const { locale } = useLocale();
  const t = useT();
  const [items, setItems] = useState<StandingRuleSet[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = useCallback(() => {
    if (!token) return;
    api
      .adminGetStandingRuleSets(token)
      .then((data) => setItems(unwrapList(data)))
      .catch((err) =>
        setError(err instanceof Error ? err.message : t("adminStandingRulesLoadFailed"))
      );
  }, [token, t]);

  useEffect(() => {
    load();
  }, [load]);

  const grouped = useMemo(() => {
    const map = new Map<string, StandingRuleSet[]>();
    for (const item of items) {
      const list = map.get(item.competition_type) ?? [];
      list.push(item);
      map.set(item.competition_type, list);
    }
    return map;
  }, [items]);

  function startEdit(item: StandingRuleSet) {
    setEditingId(item.id);
    setForm({
      slug: item.slug,
      name: item.name,
      name_ar: item.name_ar || "",
      competition_type: item.competition_type,
      version: item.version,
      engine: item.engine,
      qualifiers_per_group: item.qualifiers_per_group,
      best_third_place_qualifiers: item.best_third_place_qualifiers,
      is_active: item.is_active,
    });
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError("");
    setSuccess("");
    const slug = form.slug.trim() || suggestedSlug(form.competition_type, form.version);
    const payload = { ...form, slug };
    try {
      if (editingId) {
        await api.adminUpdateStandingRuleSet(token, editingId, payload);
        setSuccess(t("adminStandingRuleUpdated"));
      } else {
        await api.adminCreateStandingRuleSet(token, payload);
        setSuccess(t("adminStandingRuleCreated"));
      }
      setEditingId(null);
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("adminStandingRuleSaveFailed"));
    }
  }

  async function toggleActive(item: StandingRuleSet) {
    if (!token) return;
    try {
      await api.adminUpdateStandingRuleSet(token, item.id, { is_active: !item.is_active });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("adminStandingRuleSaveFailed"));
    }
  }

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold">{t("adminStandingRuleSets")}</h1>
      <p className="mb-6 text-gray-600">{t("adminStandingRuleSetsDesc")}</p>

      {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      {success && (
        <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700">{success}</div>
      )}

      <form onSubmit={handleSubmit} className="card mb-8 space-y-4">
        <h2 className="font-semibold">
          {editingId ? t("adminEditStandingRule") : t("adminAddStandingRule")}
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminRuleCompetitionType")}</label>
            <select
              className="input"
              value={form.competition_type}
              onChange={(e) =>
                setForm({
                  ...form,
                  competition_type: e.target.value,
                  slug: suggestedSlug(e.target.value, form.version),
                })
              }
            >
              <option value="world_cup">{t("adminRuleTypeWorldCup")}</option>
              <option value="champions_league">{t("adminRuleTypeChampionsLeague")}</option>
              <option value="other">{t("adminRuleTypeOther")}</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminRuleVersion")}</label>
            <input
              className="input"
              value={form.version}
              onChange={(e) =>
                setForm({
                  ...form,
                  version: e.target.value,
                  slug: suggestedSlug(form.competition_type, e.target.value),
                })
              }
              placeholder="2026"
              required
            />
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
            <label className="mb-1 block text-sm font-medium">{t("adminRuleSlug")}</label>
            <input
              className="input"
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
              placeholder={suggestedSlug(form.competition_type, form.version)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminRuleEngine")}</label>
            <select
              className="input"
              value={form.engine}
              onChange={(e) => setForm({ ...form, engine: e.target.value })}
            >
              <option value="fifa_world_cup">{t("adminStandingRulesFifa")}</option>
              <option value="uefa_champions_league">{t("adminStandingRulesUefa")}</option>
              <option value="simple">{t("adminStandingRulesSimple")}</option>
            </select>
            <p className="mt-1 text-xs text-gray-500">{t("adminRuleEngineHint")}</p>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t("adminQualifiersPerGroup")}</label>
            <input
              className="input"
              type="number"
              min={1}
              max={4}
              value={form.qualifiers_per_group}
              onChange={(e) =>
                setForm({ ...form, qualifiers_per_group: Number(e.target.value) })
              }
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              {t("adminBestThirdPlaceQualifiers")}
            </label>
            <input
              className="input"
              type="number"
              min={0}
              max={16}
              value={form.best_third_place_qualifiers}
              onChange={(e) =>
                setForm({ ...form, best_third_place_qualifiers: Number(e.target.value) })
              }
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
          />
          {t("adminRuleSetActive")}
        </label>
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

      {Array.from(grouped.entries()).map(([type, rules]) => (
        <section key={type} className="mb-8">
          <h2 className="mb-3 text-lg font-semibold">
            {t(COMPETITION_TYPE_KEYS[type] ?? "adminRuleTypeOther")}
          </h2>
          <div className="space-y-3">
            {rules.map((item) => (
              <div key={item.id} className="card flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold">
                    {adminLabel({ name: item.name, name_ar: item.name_ar }, locale)}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {t("adminRuleVersion")}: {item.version} · {t(ENGINE_KEYS[item.engine])} ·{" "}
                    {t("adminQualifiersPerGroup")}: {item.qualifiers_per_group}
                    {item.best_third_place_qualifiers > 0
                      ? ` · ${t("adminBestThirdPlaceQualifiers")}: ${item.best_third_place_qualifiers}`
                      : ""}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">
                    {item.slug} · {t("adminTournamentsUsing", { count: item.tournament_count ?? 0 })}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      item.is_active
                        ? "bg-green-100 text-green-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {item.is_active ? t("adminActive") : t("adminInactive")}
                  </span>
                  <button
                    type="button"
                    className="btn-secondary text-sm"
                    onClick={() => toggleActive(item)}
                  >
                    {item.is_active ? t("adminDeactivate") : t("adminActivate")}
                  </button>
                  <button
                    type="button"
                    className="btn-secondary text-sm"
                    onClick={() => startEdit(item)}
                  >
                    {t("adminEditDetails")}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}

      {items.length === 0 && (
        <div className="card py-12 text-center text-gray-500">{t("adminNoStandingRulesYet")}</div>
      )}
    </div>
  );
}
