"use client";

import type { ThirdPlaceStandingRow } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { teamLabel } from "@/lib/localize";
import type { Locale } from "@/lib/messages";

type Props = {
  rows: ThirdPlaceStandingRow[];
  locale: Locale;
  slots: number;
};

export function ThirdPlaceRankingTable({ rows, locale, slots }: Props) {
  const t = useT();

  if (rows.length === 0) {
    return <p className="mt-2 text-xs text-gray-500">{t("thirdPlacePending")}</p>;
  }

  return (
    <div className="mt-3 overflow-x-auto">
      <table className="w-full min-w-[20rem] text-left text-xs">
        <thead>
          <tr className="border-b border-gray-200 text-[10px] font-bold uppercase tracking-wide text-gray-500">
            <th className="py-2 pe-2">#</th>
            <th className="py-2 pe-2">{t("group")}</th>
            <th className="py-2 pe-2">{t("team")}</th>
            <th className="px-1 py-2 text-center">Pts</th>
            <th className="px-1 py-2 text-center">GD</th>
            <th className="px-1 py-2 text-center">GF</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const inCutoff = row.rank_among_thirds <= slots;
            return (
              <tr
                key={`${row.group_id}-${row.team.id}`}
                className={`border-b border-gray-100 ${
                  row.qualifies ? "bg-pitch-50/70" : inCutoff ? "" : "opacity-70"
                }`}
              >
                <td className="py-2 pe-2 font-bold text-night-800">
                  {row.rank_among_thirds}
                  {row.qualifies && (
                    <span className="ms-1 text-[10px] text-pitch-600" title={t("qualifiesBestThird")}>
                      ✓
                    </span>
                  )}
                </td>
                <td className="py-2 pe-2 font-semibold text-royal-700">{row.group_name}</td>
                <td className="py-2 pe-2 font-semibold text-night-900">
                  {teamLabel(row.team, locale)}
                </td>
                <td className="px-1 py-2 text-center font-extrabold">{row.points}</td>
                <td className="px-1 py-2 text-center font-semibold">
                  {row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}
                </td>
                <td className="px-1 py-2 text-center">{row.goals_for}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
