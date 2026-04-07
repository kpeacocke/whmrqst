from typing import Any

from campaign.models import Hero, HeroSkill, Party, SettlementLocationDef, SkillDef
from campaign.services.rng import DeterministicRng


ARCHETYPE_LOCATION_GATES = {
    "wizards_guild": "mage",
    "elf_quarter": "ranger",
    "dwarf_guildmasters": "warrior",
}


def resolve_location_access(
    settlement_size: str,
    rng: DeterministicRng,
) -> tuple[SettlementLocationDef | None, list[dict[str, Any]]]:
    """Roll to find an accessible special location for the given settlement size.

    Village: only village_available or always_available locations are accessible.
    Town/City: always_available are guaranteed; others use a 2d6 roll vs find_target.

    Returns (selected_location_or_None, dice_rolled).
    """
    dice_rolled: list[dict[str, Any]] = []

    if settlement_size == "village":
        accessible = list(
            SettlementLocationDef.objects.filter(village_available=True) |
            SettlementLocationDef.objects.filter(always_available=True)
        )
    else:
        always = list(SettlementLocationDef.objects.filter(always_available=True))
        find_target_field = f"{settlement_size}_find_target"
        candidates = SettlementLocationDef.objects.filter(
            **{f"{find_target_field}__isnull": False}
        )
        found = list(always)
        for location in candidates:
            target = getattr(location, find_target_field)
            d6a = rng.d6()
            d6b = rng.d6()
            roll_total = d6a + d6b
            dice_rolled.append({
                "die": "2d6",
                "result": roll_total,
                "min_needed": target,
                "location": location.code,
                "context": "location-find",
            })
            if roll_total >= target:
                found.append(location)
        accessible = found

    if not accessible:
        return None, dice_rolled

    idx = rng.randint(0, len(accessible) - 1)
    return accessible[idx], dice_rolled


def apply_location_effects(
    hero: Hero,
    party: Party,
    location: SettlementLocationDef,
    rng: DeterministicRng,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply the effects of visiting a location. Returns an effects dict."""
    code = location.code
    effects = {
        "location_code": code,
        "hero_health_delta": 0,
        "party_gold_delta": 0,
        "party_morale_delta": 0,
        "hero_level_delta": 0,
        "skill_learned": None,
        "rejected": None,
        "narrative": "",
    }
    dice_rolled: list[dict[str, Any]] = []

    # Archetype gates — return early without any mutation if hero doesn't qualify.
    required_archetype = ARCHETYPE_LOCATION_GATES.get(code)
    if required_archetype and hero.archetype != required_archetype:
        effects["rejected"] = "wrong_archetype"
        effects["narrative"] = (
            f"{hero.name} is not permitted entry to the {location.name}."
        )
        return effects, dice_rolled

    if code == "alehouse":
        cost = min(5, party.gold)
        if cost > 0:
            party.gold -= cost
            effects["party_gold_delta"] -= cost
        party.morale += 1
        effects["party_morale_delta"] += 1
        effects["narrative"] = (
            f"{hero.name} spends a restful evening at the {location.name}. Morale improves."
        )
        party.save(update_fields=["gold", "morale", "updated_at"])

    elif code == "temple":
        if party.gold >= 50:
            party.gold -= 50
            effects["party_gold_delta"] -= 50
            hero.temple_reroll_charges += 1
            effects["narrative"] = (
                f"{hero.name} donates to the temple and receives a divine blessing."
            )
            party.save(update_fields=["gold", "updated_at"])
            hero.save(update_fields=["temple_reroll_charges", "updated_at"])
        else:
            effects["rejected"] = "insufficient_gold"
            effects["narrative"] = (
                f"{hero.name} cannot afford the 50 gold donation at the {location.name}."
            )

    elif code == "gambling_house":
        wager = max(10, min(100, party.gold // 4))
        if party.gold < wager:
            effects["rejected"] = "insufficient_gold"
            effects["narrative"] = f"Not enough gold to wager at the {location.name}."
        else:
            roll = rng.d6()
            dice_rolled.append({"die": "d6", "result": roll, "context": "gambling-roll"})
            if roll <= 3:
                party.gold -= wager
                effects["party_gold_delta"] -= wager
                effects["narrative"] = (
                    f"{hero.name} loses the wager of {wager} gold at the {location.name}."
                )
            elif roll == 4:
                effects["narrative"] = (
                    f"{hero.name} breaks even at the {location.name}."
                )
            else:
                winnings = wager
                party.gold += winnings
                effects["party_gold_delta"] += winnings
                effects["narrative"] = (
                    f"{hero.name} wins {winnings} gold at the {location.name}."
                )
            party.save(update_fields=["gold", "updated_at"])

    elif code == "alchemist":
        effects["narrative"] = (
            f"{hero.name} visits the Alchemist's Laboratory but has nothing to transmute."
        )

    elif code in ("wizards_guild", "elf_quarter", "dwarf_guildmasters"):
        skill = _grant_next_archetype_skill(hero, location)
        if skill:
            effects["skill_learned"] = skill.skill_def.name
            effects["narrative"] = (
                f"{hero.name} learns {skill.skill_def.name} at the {location.name}."
            )
        else:
            effects["narrative"] = (
                f"{hero.name} has already learned all available skills from the {location.name}."
            )

    else:
        effects["narrative"] = f"{hero.name} explores the {location.name}."

    effects["dice_rolled"] = dice_rolled
    return effects, dice_rolled


def _grant_next_archetype_skill(
    hero: Hero,
    location: SettlementLocationDef,
) -> HeroSkill | None:
    """Grant the next unlearned archetype skill to the hero. Returns the new HeroSkill or None."""
    already_learned = set(HeroSkill.objects.filter(hero=hero).values_list("skill_def_id", flat=True))
    available = SkillDef.objects.filter(
        archetype=hero.archetype,
    ).exclude(id__in=already_learned).order_by("name").first()

    if not available:
        return None

    return HeroSkill.objects.create(
        hero=hero,
        skill_def=available,
        source=f"location:{location.code}",
    )
