import Link from "next/link";
import { Match } from "@/lib/api";

interface Props {
  match: Match;
  showPredictLink?: boolean;
  showResultLink?: boolean;
}

export function MatchCard({ match, showPredictLink, showResultLink }: Props) {
  const kickoff = new Date(match.kickoff_time).toLocaleString();
  const isFinished = match.status === "finished";

  return (
    <div className="card">
      <div className="mb-2 flex items-center justify-between text-xs text-gray-500">
        <span>{match.stage_name}</span>
        {match.is_locked && !isFinished && (
          <span className="rounded bg-red-100 px-2 py-0.5 text-red-700">Locked</span>
        )}
      </div>
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 text-center">
          {match.home_team.flag_url && (
            <img src={match.home_team.flag_url} alt="" className="mx-auto mb-1 h-8 w-12 object-cover" />
          )}
          <p className="font-semibold">{match.home_team.name}</p>
        </div>
        <div className="text-center">
          {isFinished ? (
            <p className="text-2xl font-bold">
              {match.home_score} - {match.away_score}
            </p>
          ) : (
            <p className="text-lg text-gray-400">vs</p>
          )}
          <p className="text-xs text-gray-500">{kickoff}</p>
        </div>
        <div className="flex-1 text-center">
          {match.away_team.flag_url && (
            <img src={match.away_team.flag_url} alt="" className="mx-auto mb-1 h-8 w-12 object-cover" />
          )}
          <p className="font-semibold">{match.away_team.name}</p>
        </div>
      </div>
      <div className="mt-3 flex justify-center gap-2">
        {showPredictLink && !match.is_locked && !isFinished && (
          <Link href={`/matches/${match.id}`} className="btn-primary text-sm">
            Predict
          </Link>
        )}
        {showResultLink && isFinished && (
          <Link href={`/matches/${match.id}/results`} className="btn-secondary text-sm">
            View Results
          </Link>
        )}
        <Link href={`/matches/${match.id}`} className="btn-secondary text-sm">
          Details
        </Link>
      </div>
    </div>
  );
}
