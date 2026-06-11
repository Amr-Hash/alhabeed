"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  api,
  Group,
  GroupMatchPredictions,
  GroupMember,
  GroupPredictionsResponse,
  unwrapList,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTournament } from "@/lib/tournament";
import { RequireTournament } from "@/components/RequireTournament";
import { EmptyState } from "@/components/EmptyState";
import { useLocale, useT } from "@/lib/i18n";
import { matchContextLabel, teamLabel, tournamentLabel } from "@/lib/localize";

type Tab = "members" | "predictions";

function formatPrediction(
  pred: GroupMatchPredictions["predictions"][0],
  locale: "en" | "ar",
  t: ReturnType<typeof useT>
) {
  if (pred.predicted_home_score === null || pred.predicted_away_score === null) {
    return t("noPrediction");
  }
  const score = `${pred.predicted_home_score}-${pred.predicted_away_score}`;
  if (pred.predicted_winner_team) {
    return `${score} (${teamLabel(pred.predicted_winner_team, locale)} ${t("advances")})`;
  }
  return score;
}

function GroupDetailContent() {
  const { id } = useParams<{ id: string }>();
  const { user, token, loading: authLoading } = useAuth();
  const { selectedTournament } = useTournament();
  const { locale } = useLocale();
  const t = useT();
  const router = useRouter();
  const groupId = Number(id);

  const [group, setGroup] = useState<Group | null>(null);
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [predictionsData, setPredictionsData] = useState<GroupPredictionsResponse | null>(null);
  const [tab, setTab] = useState<Tab>("members");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) router.push("/login");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!token || !groupId) return;
    setLoading(true);
    setError("");
    Promise.all([
      api.getGroups(token).then((data) => {
        const found = unwrapList(data).find((g) => g.id === groupId) || null;
        setGroup(found);
        if (!found) setError(t("groupNotFound"));
      }),
      api.getGroupMembers(token, groupId).then(setMembers).catch(() => {
        setError(t("groupAccessDenied"));
      }),
    ])
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [token, groupId, t]);

  useEffect(() => {
    if (!token || !groupId || !selectedTournament) return;
    api
      .getGroupPredictions(token, groupId, selectedTournament.id)
      .then(setPredictionsData)
      .catch(() => setPredictionsData(null));
  }, [token, groupId, selectedTournament]);

  if (authLoading || !user) return <div>{t("loading")}</div>;

  return (
    <RequireTournament>
      <div>
        <Link href="/groups" className="mb-4 inline-flex text-sm text-pitch-600 hover:underline">
          ← {t("backToGroups")}
        </Link>

        {loading ? (
          <p className="text-gray-500">{t("loading")}</p>
        ) : error ? (
          <div className="rounded-lg bg-red-50 p-4 text-red-700">{error}</div>
        ) : group ? (
          <>
            <h1 className="mb-1 text-3xl font-bold">{group.name}</h1>
            {group.description && <p className="mb-2 text-gray-600">{group.description}</p>}
            <p className="mb-6 text-sm text-gray-500">
              {t("groupMembersCount", { count: members.length })}
              {group.is_admin && (
                <span className="ml-2 rounded bg-gold-400/20 px-2 py-0.5 text-xs font-medium text-gold-600">
                  {t("groupAdmin")}
                </span>
              )}
            </p>

            <div className="mb-6 flex gap-2 border-b">
              <button
                type="button"
                className={`border-b-2 px-4 py-2 text-sm font-medium ${
                  tab === "members"
                    ? "border-pitch-600 text-pitch-700"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => setTab("members")}
              >
                {t("groupMembersTab")}
              </button>
              <button
                type="button"
                className={`border-b-2 px-4 py-2 text-sm font-medium ${
                  tab === "predictions"
                    ? "border-pitch-600 text-pitch-700"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => setTab("predictions")}
              >
                {t("groupPredictionsTab")}
              </button>
            </div>

            {tab === "members" && (
              <div className="card overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b text-gray-500">
                      <th className="pb-3 pr-4">{t("username")}</th>
                      <th className="pb-3 pr-4">{t("role")}</th>
                      <th className="pb-3">{t("joined")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {members.map((member) => (
                      <tr key={member.id} className="border-b last:border-0">
                        <td className="py-3 pr-4 font-medium">{member.username}</td>
                        <td className="py-3 pr-4 capitalize">
                          {member.role === "admin" ? t("groupAdmin") : t("groupMember")}
                        </td>
                        <td className="py-3 text-gray-500">
                          {new Date(member.joined_at).toLocaleDateString(
                            locale === "ar" ? "ar-EG" : undefined
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {tab === "predictions" && selectedTournament && (
              <>
                <p className="mb-4 text-sm text-gray-600">
                  {t("groupPredictionsFor", {
                    name: tournamentLabel(selectedTournament, locale),
                    year: selectedTournament.year,
                  })}
                </p>
                {!predictionsData || predictionsData.matches.length === 0 ? (
                  <EmptyState
                    icon="🎯"
                    title={t("noGroupPredictionsYet")}
                    description={t("noGroupPredictionsDesc")}
                    action={{ label: t("makePredictions"), href: "/matches" }}
                  />
                ) : (
                  <div className="space-y-4">
                    {predictionsData.matches.map(({ match, predictions }) => {
                      const hasAnyPrediction = predictions.some(
                        (p) => p.predicted_home_score !== null
                      );
                      if (!hasAnyPrediction) return null;
                      return (
                        <div key={match.id} className="card overflow-x-auto">
                          <div className="mb-3 border-b pb-3">
                            <p className="text-xs text-gray-500">
                              {matchContextLabel(match, locale, t("group"))}
                              {match.matchday ? ` · ${t("matchday", { day: match.matchday })}` : ""}
                            </p>
                            <p className="font-semibold">
                              {teamLabel(match.home_team, locale)} vs{" "}
                              {teamLabel(match.away_team, locale)}
                              {match.status === "finished" &&
                                match.home_score !== null &&
                                match.away_score !== null && (
                                  <span className="ml-2 text-pitch-700">
                                    ({match.home_score}-{match.away_score})
                                  </span>
                                )}
                            </p>
                          </div>
                          <table className="w-full text-left text-sm">
                            <thead>
                              <tr className="border-b text-gray-500">
                                <th className="pb-2 pr-4">{t("player")}</th>
                                <th className="pb-2 pr-4">{t("yourPrediction")}</th>
                                <th className="pb-2">{t("points")}</th>
                              </tr>
                            </thead>
                            <tbody>
                              {predictions.map((pred) => (
                                <tr key={pred.user_id} className="border-b last:border-0">
                                  <td className="py-2 pr-4 font-medium">{pred.username}</td>
                                  <td className="py-2 pr-4">
                                    {formatPrediction(pred, locale, t)}
                                  </td>
                                  <td className="py-2 font-medium text-pitch-600">
                                    {match.status === "finished" ? pred.points_awarded : "—"}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            )}
          </>
        ) : null}
      </div>
    </RequireTournament>
  );
}

export default function GroupDetailPage() {
  return <GroupDetailContent />;
}
