"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Tournament } from "@/lib/api";
import { useTournament } from "@/lib/tournament";
import { EmptyState } from "@/components/EmptyState";

export function TournamentPicker() {
  const router = useRouter();
  const {
    tournaments,
    selectedTournament,
    setSelectedTournamentId,
    loading,
    error,
  } = useTournament();

  if (loading) {
    return (
      <div className="flex min-h-[30vh] items-center justify-center text-gray-500">
        Loading tournaments...
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon="⚠️"
        title="Could not load tournaments"
        description={error}
        action={{ label: "Try again", href: "/" }}
      />
    );
  }

  const active = tournaments.filter((t) => t.is_active !== false);

  if (active.length === 0) {
    return (
      <EmptyState
        icon="🏆"
        title="No active tournaments"
        description="Check back soon — an admin can add and activate competitions from the admin panel."
      />
    );
  }

  return (
    <div className="w-full max-w-4xl">
      <h2 className="mb-2 text-center text-2xl font-bold text-pitch-900">
        Choose a tournament
      </h2>
      <p className="mb-8 text-center text-gray-600">
        Pick a competition to view matches, make predictions, and climb the leaderboard.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        {active.map((t) => (
          <TournamentCard
            key={t.id}
            tournament={t}
            selected={selectedTournament?.id === t.id}
            onSelect={() => {
              setSelectedTournamentId(t.id);
              router.push("/dashboard");
            }}
          />
        ))}
      </div>
      {selectedTournament && (
        <p className="mt-6 text-center text-sm text-gray-500">
          Currently selected:{" "}
          <strong>
            {selectedTournament.name} ({selectedTournament.year})
          </strong>
          .{" "}
          <Link href="/dashboard" className="text-pitch-600 hover:underline">
            Open dashboard →
          </Link>
        </p>
      )}
    </div>
  );
}

function TournamentCard({
  tournament,
  selected,
  onSelect,
}: {
  tournament: Tournament;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`card w-full text-left transition hover:border-pitch-300 hover:shadow-md ${
        selected ? "border-pitch-400 ring-2 ring-pitch-200" : ""
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-pitch-900">{tournament.name}</h3>
          <p className="text-sm text-gray-500">{tournament.year}</p>
        </div>
        <span className="text-2xl">🏆</span>
      </div>
      <p className="mt-3 text-sm text-gray-600">
        {tournament.match_count ?? 0} matches
        {tournament.stage_count ? ` · ${tournament.stage_count} stages` : ""}
      </p>
      <p className="mt-4 text-sm font-medium text-pitch-600">
        {selected ? "Selected — enter →" : "Select tournament →"}
      </p>
    </button>
  );
}
