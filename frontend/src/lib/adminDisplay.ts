import { localizedName, type NamedEntity } from "./localize";
import type { Locale } from "./messages";

/** Single localized label for admin lists (falls back to English when Arabic is missing). */
export function adminLabel(
  entity: NamedEntity | null | undefined,
  locale: Locale
): string {
  return localizedName(entity, locale);
}

export function teamOptionLabel(
  team: NamedEntity & { code: string },
  locale: Locale
): string {
  return `${team.code} — ${adminLabel(team, locale)}`;
}
