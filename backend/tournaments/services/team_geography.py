"""Geography metadata for national teams (FIFA confederations)."""

from __future__ import annotations

from tournaments.models import Continent, Team

# FIFA team code → (country_code for flags, continent)
WC2026_TEAM_GEOGRAPHY: dict[str, tuple[str, str]] = {
    "MEX": ("mx", Continent.NORTH_AMERICA),
    "RSA": ("za", Continent.AFRICA),
    "KOR": ("kr", Continent.ASIA),
    "CZE": ("cz", Continent.EUROPE),
    "CAN": ("ca", Continent.NORTH_AMERICA),
    "BIH": ("ba", Continent.EUROPE),
    "QAT": ("qa", Continent.ASIA),
    "SUI": ("ch", Continent.EUROPE),
    "BRA": ("br", Continent.SOUTH_AMERICA),
    "MAR": ("ma", Continent.AFRICA),
    "HAI": ("ht", Continent.NORTH_AMERICA),
    "SCO": ("gb-sct", Continent.EUROPE),
    "USA": ("us", Continent.NORTH_AMERICA),
    "PAR": ("py", Continent.SOUTH_AMERICA),
    "AUS": ("au", Continent.OCEANIA),
    "TUR": ("tr", Continent.EUROPE),
    "GER": ("de", Continent.EUROPE),
    "CUW": ("cw", Continent.NORTH_AMERICA),
    "CIV": ("ci", Continent.AFRICA),
    "ECU": ("ec", Continent.SOUTH_AMERICA),
    "NED": ("nl", Continent.EUROPE),
    "JPN": ("jp", Continent.ASIA),
    "SWE": ("se", Continent.EUROPE),
    "TUN": ("tn", Continent.AFRICA),
    "BEL": ("be", Continent.EUROPE),
    "EGY": ("eg", Continent.AFRICA),
    "IRN": ("ir", Continent.ASIA),
    "NZL": ("nz", Continent.OCEANIA),
    "ESP": ("es", Continent.EUROPE),
    "CPV": ("cv", Continent.AFRICA),
    "KSA": ("sa", Continent.ASIA),
    "URU": ("uy", Continent.SOUTH_AMERICA),
    "FRA": ("fr", Continent.EUROPE),
    "SEN": ("sn", Continent.AFRICA),
    "NOR": ("no", Continent.EUROPE),
    "IRQ": ("iq", Continent.ASIA),
    "ARG": ("ar", Continent.SOUTH_AMERICA),
    "ALG": ("dz", Continent.AFRICA),
    "AUT": ("at", Continent.EUROPE),
    "JOR": ("jo", Continent.ASIA),
    "POR": ("pt", Continent.EUROPE),
    "COD": ("cd", Continent.AFRICA),
    "UZB": ("uz", Continent.ASIA),
    "COL": ("co", Continent.SOUTH_AMERICA),
    "ENG": ("gb-eng", Continent.EUROPE),
    "CRO": ("hr", Continent.EUROPE),
    "GHA": ("gh", Continent.AFRICA),
    "PAN": ("pa", Continent.NORTH_AMERICA),
}


def geography_for_team_code(code: str, flag_iso: str | None = None) -> dict[str, str]:
    """Defaults for seeding national teams."""
    upper = code.upper()
    if upper in WC2026_TEAM_GEOGRAPHY:
        country_code, continent = WC2026_TEAM_GEOGRAPHY[upper]
        return {
            "team_type": Team.TeamType.NATIONAL,
            "country_code": country_code,
            "continent": continent,
        }
    return {
        "team_type": Team.TeamType.NATIONAL,
        "country_code": (flag_iso or code[:2]).lower(),
        "continent": "",
    }
