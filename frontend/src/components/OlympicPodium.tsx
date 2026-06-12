"use client";

import { useMemo } from "react";
import { DashboardPodiumEntry } from "@/lib/api";
import { useT } from "@/lib/i18n";

/** Silver left, gold center (tallest), bronze right — heights are fixed by medal, not headcount. */
const PODIUM_SLOTS = [
  {
    rank: 2,
    medal: "🥈",
    heightClass: "h-20",
    platform: "from-slate-300 to-slate-100",
    edge: "border-slate-400/40",
  },
  {
    rank: 1,
    medal: "🥇",
    heightClass: "h-28",
    platform: "from-gold-500 to-gold-200",
    edge: "border-gold-600/40",
  },
  {
    rank: 3,
    medal: "🥉",
    heightClass: "h-14",
    platform: "from-amber-700 to-amber-400",
    edge: "border-amber-800/40",
  },
] as const;

export function OlympicPodium({ podium }: { podium: DashboardPodiumEntry[] }) {
  const t = useT();

  const byRank = useMemo(() => {
    const map: Record<number, DashboardPodiumEntry[]> = { 1: [], 2: [], 3: [] };
    for (const entry of podium) {
      if (entry.rank >= 1 && entry.rank <= 3) {
        map[entry.rank].push(entry);
      }
    }
    return map;
  }, [podium]);

  return (
    <div className="flex items-end justify-center gap-1.5 sm:gap-2">
      {PODIUM_SLOTS.map((slot) => {
        const entries = byRank[slot.rank];
        const points = entries[0]?.total_points;

        return (
          <div key={slot.rank} className="flex w-[31%] max-w-[7.5rem] flex-col items-center">
            <div className="mb-1.5 flex min-h-[3.5rem] w-full flex-col items-center justify-end gap-0.5 px-0.5 text-center">
              <span className="text-xl leading-none sm:text-2xl" aria-hidden>
                {slot.medal}
              </span>
              {entries.length > 0 ? (
                <div className="max-h-16 w-full space-y-0.5 overflow-y-auto">
                  {entries.map((entry) => (
                    <p
                      key={entry.user_id}
                      className={`truncate text-[10px] font-bold leading-tight sm:text-xs ${
                        entry.is_you ? "text-royal-600" : "text-night-900"
                      }`}
                      title={entry.username}
                    >
                      {entry.username}
                      {entry.is_you && (
                        <span className="font-semibold text-royal-500"> ({t("you")})</span>
                      )}
                    </p>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400">—</p>
              )}
            </div>

            <div
              className={`flex w-full ${slot.heightClass} flex-col items-center justify-end rounded-t-lg border-x border-t bg-gradient-to-t ${slot.platform} ${slot.edge} px-1 pb-1.5 shadow-[inset_0_2px_4px_rgba(255,255,255,0.35)]`}
            >
              {points != null ? (
                <span className="font-display text-sm font-extrabold text-night-900/85">
                  {points}
                  {entries.length > 1 && (
                    <span className="block text-[9px] font-semibold normal-case opacity-70">
                      {t("tiedPoints")}
                    </span>
                  )}
                </span>
              ) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
}
