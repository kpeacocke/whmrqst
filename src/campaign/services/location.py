from typing import Any

from campaign.models import Hero, HeroSkill, Party, SettlementLocationDef, SkillDef
from campaign.services.rng import DeterministicRng


ARCHETYPE_LOCATION_GATES = {
    "wizards_guild": "mage",
    "elf_quarter": "ranger",
    "dwarf_guildmasters": "warrior",
}

SKILL_GRANTING_LOCATIONS = {"wizards_guild", "elf_quarter", "dwarf_guildmasters"}
VALID_SETTLEMENT_SIZES = {"village", "town", "city"}


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

    if settlement_size not in VALID_SETTLEMENT_SIZES:
        raise ValueError(f"Unsupported settlement size: {settlement_size}")

    if settlement_size == "village":
        accessible = _get_village_locations()
    else:
        accessible = _get_larger_settlement_locations(settlement_size, rng, dice_rolled)

    if not accessible:
        return None, dice_rolled

    idx = rng.randint(0, len(accessible) - 1)
    return accessible[idx], dice_rolled


def _get_village_locations() -> list[SettlementLocationDef]:
    return list(
        (
            SettlementLocationDef.objects.filter(village_available=True)
            | SettlementLocationDef.objects.filter(always_available=True)
        ).distinct()
    )


def _get_larger_settlement_locations(
    settlement_size: str,
    rng: DeterministicRng,
    dice_rolled: list[dict[str, Any]],
) -> list[SettlementLocationDef]:
    always = list(SettlementLocationDef.objects.filter(always_available=True))
    find_target_field = f"{settlement_size}_find_target"
    candidates = SettlementLocationDef.objects.filter(**{f"{find_target_field}__isnull": False})
    found = always.copy()
    found_ids = {location.pk for location in found}

    for location in candidates:
        if location.pk in found_ids:
            continue
        if _location_is_found(location, find_target_field, rng, dice_rolled):
            found.append(location)
            found_ids.add(location.pk)

    return found


def _location_is_found(
    location: SettlementLocationDef,
    find_target_field: str,
    rng: DeterministicRng,
    dice_rolled: list[dict[str, Any]],
) -> bool:
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
    return roll_total >= target


def apply_location_effects(
    hero: Hero,
    party: Party,
    location: SettlementLocationDef,
    rng: DeterministicRng,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply the effects of visiting a location. Returns an effects dict."""
    code = location.code
    effects = _initialise_location_effects(code)
    dice_rolled: list[dict[str, Any]] = []

    # Archetype gates — return early without any mutation if hero doesn't qualify.
    required_archetype = ARCHETYPE_LOCATION_GATES.get(code)
    if required_archetype and hero.archetype != required_archetype:
        _reject_wrong_archetype(hero, location, effects)
        return effects, dice_rolled

    handler = LOCATION_EFFECT_HANDLERS.get(code)
    if handler is not None:
        handler(hero, party, location, rng, effects, dice_rolled)
    elif code in SKILL_GRANTING_LOCATIONS:
        _apply_skill_location_effects(hero, location, effects)
    else:
        effects["narrative"] = f"{hero.name} explores the {location.name}."

    effects["dice_rolled"] = dice_rolled
    return effects, dice_rolled


def _initialise_location_effects(code: str) -> dict[str, Any]:
    return {
        "location_code": code,
        "hero_health_delta": 0,
        "party_gold_delta": 0,
        "party_morale_delta": 0,
        "hero_level_delta": 0,
        "skill_learned": None,
        "rejected": None,
        "narrative": "",
    }


def _reject_wrong_archetype(
    hero: Hero,
    location: SettlementLocationDef,
    effects: dict[str, Any],
) -> None:
    effects["rejected"] = "wrong_archetype"
    effects["narrative"] = f"{hero.name} is not permitted entry to the {location.name}."


def _apply_alehouse_effects(
    hero: Hero,
    party: Party,
    location: SettlementLocationDef,
    rng: DeterministicRng,
    effects: dict[str, Any],
    dice_rolled: list[dict[str, Any]],
) -> None:
    del rng, dice_rolled
    cost = min(5, party.gold)
    if cost > 0:
        party.gold -= cost
        effects["party_gold_delta"] -= cost
    party.morale += 1
    effects["party_morale_delta"] += 1
    effects["narrative"] = f"{hero.name} spends a restful evening at the {location.name}. Morale improves."
    party.save(update_fields=["gold", "morale", "updated_at"])


def _apply_temple_effects(
    hero: Hero,
    party: Party,
    location: SettlementLocationDef,
    rng: DeterministicRng,
    effects: dict[str, Any],
    dice_rolled: list[dict[str, Any]],
) -> None:
    del rng, dice_rolled
    if party.gold < 50:
        effects["rejected"] = "insufficient_gold"
        effects["narrative"] = f"{hero.name} cannot afford the 50 gold donation at the {location.name}."
        return

    party.gold -= 50
    effects["party_gold_delta"] -= 50
    hero.temple_reroll_charges += 1
    effects["narrative"] = f"{hero.name} donates to the temple and receives a divine blessing."
    party.save(update_fields=["gold", "updated_at"])
    hero.save(update_fields=["temple_reroll_charges", "updated_at"])


def _apply_gambling_house_effects(
    hero: Hero,
    party: Party,
    location: SettlementLocationDef,
    rng: DeterministicRng,
    effects: dict[str, Any],
    dice_rolled: list[dict[str, Any]],
) -> None:
    wager = max(10, min(100, party.gold // 4))
    if party.gold < wager:
        effects["rejected"] = "insufficient_gold"
        effects["narrative"] = f"Not enough gold to wager at the {location.name}."
        return

    roll = rng.d6()
    dice_rolled.append({"die": "d6", "result": roll, "context": "gambling-roll"})
    if roll <= 3:
        party.gold -= wager
        effects["party_gold_delta"] -= wager
        effects["narrative"] = f"{hero.name} loses the wager of {wager} gold at the {location.name}."
    elif roll == 4:
        effects["narrative"] = f"{hero.name} breaks even at the {location.name}."
    else:
        winnings = wager
        party.gold += winnings
        effects["party_gold_delta"] += winnings
        effects["narrative"] = f"{hero.name} wins {winnings} gold at the {location.name}."
    party.save(update_fields=["gold", "updated_at"])


def _apply_alchemist_effects(
    hero: Hero,
    party: Party,
    location: SettlementLocationDef,
    rng: DeterministicRng,
    effects: dict[str, Any],
    dice_rolled: list[dict[str, Any]],
) -> None:
    del party, rng, dice_rolled
    effects["narrative"] = f"{hero.name} visits the Alchemist's Laboratory but has nothing to transmute."


def _apply_skill_location_effects(
    hero: Hero,
    location: SettlementLocationDef,
    effects: dict[str, Any],
) -> None:
    skill = _grant_next_archetype_skill(hero, location)
    if skill is None:
        effects["narrative"] = (
            f"{hero.name} has already learned all available skills from the {location.name}."
        )
        return

    effects["skill_learned"] = skill.skill_def.name
    effects["narrative"] = f"{hero.name} learns {skill.skill_def.name} at the {location.name}."


LOCATION_EFFECT_HANDLERS = {
    "alehouse": _apply_alehouse_effects,
    "temple": _apply_temple_effects,
    "gambling_house": _apply_gambling_house_effects,
    "alchemist": _apply_alchemist_effects,
}


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
