"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { api, Tournament, unwrapList } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTournament } from "@/lib/tournament";
import { EmptyState } from "@/components/EmptyState";
import { useLocale, useT } from "@/lib/i18n";
import { showTournamentYearSeparately, tournamentLabel, tournamentTitle } from "@/lib/localize";

export function TournamentPicker() {
  const router = useRouter();
  const { token } = useAuth();
  const { locale } = useLocale();
  const t = useT();
  const {
    tournaments: subscribedTournaments,
    selectedTournament,
    setSelectedTournamentId,
    reloadTournaments,
    loading: subscribedLoading,
    error: subscribedError,
  } = useTournament();
  const [available, setAvailable] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [subscribingId, setSubscribingId] = useState<number | null>(null);

  const loadAvailable = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAvailableTournaments(token);
      setAvailable(unwrapList(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : t("couldNotLoadTournaments"));
    } finally {
      setLoading(false);
    }
  }, [token, t]);

  useEffect(() => {
    loadAvailable();
  }, [loadAvailable]);

  const isLoading = subscribedLoading || loading;
  const displayError = subscribedError || error;

  if (isLoading) {
    return (
      <div className="flex min-h-[30vh] items-center justify-center text-gray-500">
        {t("loadingTournaments")}
      </div>
    );
  }

  if (displayError) {
    return (
      <EmptyState
        icon="⚠️"
        title={t("couldNotLoadTournaments")}
        description={displayError}
        action={{ label: t("tryAgain"), href: "/" }}
      />
    );
  }

  const active = available.filter((tournament) => tournament.is_active !== false);

  if (active.length === 0) {
    return (
      <EmptyState
        icon="🏆"
        title={t("noActiveTournaments")}
        description={t("noActiveTournamentsDesc")}
      />
    );
  }

  async function handleSelect(tournament: Tournament) {
    if (!token) return;
    setSubscribingId(tournament.id);
    try {
      if (!tournament.is_subscribed) {
        await api.subscribeTournament(token, tournament.id);
      }
      await reloadTournaments();
      setSelectedTournamentId(tournament.id);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("subscribeTournamentFailed"));
      setSubscribingId(null);
    }
  }

  return (
    <div className="w-full max-w-4xl">
      <h2 className="mb-2 text-center text-2xl font-bold text-pitch-900">
        {subscribedTournaments.length === 0 ? t("subscribeTournamentTitle") : t("chooseTournament")}
      </h2>
      <p className="mb-8 text-center text-gray-600">
        {subscribedTournaments.length === 0
          ? t("subscribeTournamentDesc")
          : t("chooseTournamentDesc")}
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {active.map((tournament) => (
          <TournamentCard
            key={tournament.id}
            tournament={tournament}
            selected={selectedTournament?.id === tournament.id || Boolean(tournament.is_subscribed)}
            subscribing={subscribingId === tournament.id}
            onSelect={() => handleSelect(tournament)}
          />
        ))}
      </div>
      {selectedTournament && subscribedTournaments.length > 0 && (
        <p className="mt-6 text-center text-sm text-gray-500">
          {t("currentlySelected")}{" "}
          <strong>{tournamentTitle(selectedTournament, locale)}</strong>.{" "}
          <Link href="/dashboard" className="text-pitch-600 hover:underline">
            {t("openDashboard")}
          </Link>
        </p>
      )}
    </div>
  );
}

function TournamentCard({
  tournament,
  selected,
  subscribing,
  onSelect,
}: {
  tournament: Tournament;
  selected: boolean;
  subscribing: boolean;
  onSelect: () => void;
}) {
  const { locale } = useLocale();
  const t = useT();

  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={subscribing}
      className={`card card-hover w-full border-t-4 border-t-pitch-500 text-left ${
        selected ? "ring-2 ring-royal-400 ring-offset-2" : ""
      } ${subscribing ? "opacity-70" : ""}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-pitch-900">
            {tournamentLabel(tournament, locale)}
          </h3>
          {showTournamentYearSeparately(tournament, locale) ? (
            <p className="text-sm text-gray-500">{tournament.year}</p>
          ) : null}
        </div>
        <span className="text-2xl" aria-hidden>
          🏆
        </span>
      </div>
      <p className="mt-3 text-sm text-gray-600">
        {t("matchesCount", { count: tournament.match_count ?? 0 })}
        {tournament.stage_count
          ? ` · ${t("stagesCount", { count: tournament.stage_count })}`
          : ""}
      </p>
      <p className="mt-4 text-sm font-medium text-pitch-600">
        {subscribing
          ? t("loading")
          : tournament.is_subscribed
            ? t("selectedEnter")
            : t("subscribeTournament")}
      </p>
    </button>
  );
}
