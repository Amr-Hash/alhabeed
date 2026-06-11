"use client";

import { useParams } from "next/navigation";
import { TournamentHub } from "@/components/admin/TournamentHub";

export default function AdminTournamentDetailPage() {
  const params = useParams();
  const id = Number(params.id);

  if (!id || Number.isNaN(id)) {
    return <div className="py-12 text-center text-gray-500">Invalid tournament.</div>;
  }

  return <TournamentHub tournamentId={id} />;
}
