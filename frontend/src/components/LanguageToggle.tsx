"use client";

import { useLocale, useT } from "@/lib/i18n";
import type { Locale } from "@/lib/messages";

export function LanguageToggle() {
  const { locale, setLocale } = useLocale();
  const t = useT();

  return (
    <label className="flex items-center gap-2 rounded-lg border border-pitch-200 bg-pitch-50 px-2 py-1.5 text-sm shadow-sm">
      <span className="text-base leading-none" aria-hidden>
        🌐
      </span>
      <span className="hidden font-medium text-gray-600 sm:inline">{t("language")}</span>
      <select
        className="cursor-pointer border-0 bg-transparent py-0 pl-0 pr-6 text-sm font-semibold text-pitch-800 focus:outline-none focus:ring-0"
        value={locale}
        onChange={(e) => setLocale(e.target.value as Locale)}
        aria-label={t("language")}
      >
        <option value="en">{t("english")}</option>
        <option value="ar">{t("arabic")}</option>
      </select>
    </label>
  );
}
