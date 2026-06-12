from tournaments.models import Tournament

ENGINE_RULE_METADATA = {
    Tournament.StandingRules.FIFA_WORLD_CUP: {
        "label_en": "FIFA World Cup",
        "label_ar": "كأس العالم (فيفا)",
        "qualifiers_per_group": 2,
        # 12 groups × top 2 (24) + best 8 third-placed teams = 32 in the round of 32
        "best_third_place_qualifiers": 8,
        "steps_en": [
            "Points",
            "Goal difference (all group matches)",
            "Goals scored (all group matches)",
            "Head-to-head points among tied teams",
            "Head-to-head goal difference among tied teams",
            "Head-to-head goals scored among tied teams",
        ],
        "steps_ar": [
            "النقاط",
            "فارق الأهداف (كل مباريات المجموعة)",
            "الأهداف المسجلة (كل مباريات المجموعة)",
            "نقاط المواجهات المباشرة بين المتعادلين",
            "فارق الأهداف في المواجهات المباشرة بين المتعادلين",
            "الأهداف المسجلة في المواجهات المباشرة بين المتعادلين",
        ],
        "third_place_steps_en": [
            "Points (all group matches)",
            "Goal difference (all group matches)",
            "Goals scored (all group matches)",
        ],
        "third_place_steps_ar": [
            "النقاط (كل مباريات المجموعة)",
            "فارق الأهداف (كل مباريات المجموعة)",
            "الأهداف المسجلة (كل مباريات المجموعة)",
        ],
    },
    Tournament.StandingRules.UEFA_CHAMPIONS_LEAGUE: {
        "label_en": "UEFA Champions League",
        "label_ar": "دوري أبطال أوروبا",
        "qualifiers_per_group": 2,
        "steps_en": [
            "Points",
            "Head-to-head points among tied teams",
            "Head-to-head goal difference among tied teams",
            "Head-to-head goals scored among tied teams",
            "Goal difference (all group matches)",
            "Goals scored (all group matches)",
            "Away goals scored (all group matches)",
            "Wins (all group matches)",
        ],
        "steps_ar": [
            "النقاط",
            "نقاط المواجهات المباشرة بين المتعادلين",
            "فارق الأهداف في المواجهات المباشرة بين المتعادلين",
            "الأهداف المسجلة في المواجهات المباشرة بين المتعادلين",
            "فارق الأهداف (كل مباريات المجموعة)",
            "الأهداف المسجلة (كل مباريات المجموعة)",
            "الأهداف المسجلة خارج الأرض (كل مباريات المجموعة)",
            "الانتصارات (كل مباريات المجموعة)",
        ],
    },
    Tournament.StandingRules.SIMPLE: {
        "label_en": "Simple",
        "label_ar": "بسيط",
        "qualifiers_per_group": 2,
        "steps_en": [
            "Points",
            "Goal difference",
            "Goals scored",
        ],
        "steps_ar": [
            "النقاط",
            "فارق الأهداف",
            "الأهداف المسجلة",
        ],
    },
}


# Backwards-compatible alias
RULE_METADATA = ENGINE_RULE_METADATA


def get_rule_metadata(rules_key: str) -> dict:
    return ENGINE_RULE_METADATA.get(
        rules_key, ENGINE_RULE_METADATA[Tournament.StandingRules.SIMPLE]
    )
