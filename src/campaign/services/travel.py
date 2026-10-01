from typing import Any, cast

from django.db import transaction

from campaign.models import Campaign, HazardDef, Hero, Party, StepLog
from campaign.services.crafting import get_party_encumbrance_penalty
from campaign.services.rng import DeterministicRng, derive_step_seed
from campaign.services.rules import get_game_rules

WHQ_SOURCE = "whq_roleplay_book"


@transaction.atomic
def resolve_travel_hazards(
    party: Party, settlement_size: str, settlement_name: str | None = None
) -> dict[str, Any]:
    party = Party.objects.select_for_update().get(pk=party.pk)
    campaign = Campaign.objects.select_for_update().get(pk=party.campaign.pk)
    hazards = list(HazardDef.objects.filter(definition__source=WHQ_SOURCE))
    if not hazards:
        hazards = list(HazardDef.objects.filter(settlement_size=settlement_size))
    if not hazards:
        raise ValueError("No hazards are configured for travel resolution")

    hazards_by_roll: dict[str, HazardDef] = {}
    for hazard in hazards:
        definition = cast(dict[str, Any], hazard.definition or {})
        table_roll = str(definition.get("table_roll", "")).strip()
        if table_roll:
            hazards_by_roll[table_roll] = hazard

    encumbrance_penalty = get_party_encumbrance_penalty(party)
    travel_rules = get_game_rules().get("travel", {})
    hazard_counts = travel_rules.get("hazards_by_settlement", {})
    if settlement_size not in hazard_counts:
        raise ValueError(f"No travel hazard count configured for {settlement_size}")
    pending_hazards = int(hazard_counts[settlement_size]) + int(
        encumbrance_penalty["movement_penalty"]
    )
    resolved: list[dict[str, Any]] = []
    safety_counter = 0
    maximum_hazards = int(travel_rules.get("maximum_hazards_per_trip", 100))

    while pending_hazards > 0 and safety_counter < maximum_hazards:
        safety_counter += 1
        sequence = StepLog.objects.filter(campaign=campaign).count() + 1
        seed = derive_step_seed(
            campaign.seed, "travel", "hazard", f"party:{party.pk}", sequence
        )
        rng = DeterministicRng(seed)

        tens = rng.d6()
        units = rng.d6()
        table_roll = f"{tens}{units}"
        chosen_hazard = hazards_by_roll.get(table_roll)
        if chosen_hazard is None:
            chosen_hazard = rng.choice(hazards)

        dice_rolled: list[dict[str, Any]] = [
            {"die": "d6", "result": tens, "context": "hazard-roll-tens"},
            {"die": "d6", "result": units, "context": "hazard-roll-units"},
            {"die": "d66", "result": table_roll, "context": "hazard-roll"},
        ]
        effects = _apply_hazard_effects(party, chosen_hazard, rng)

        pending_hazards -= 1
        extra_hazards = int(effects.get("extra_hazards", 0))
        pending_hazards += extra_hazards
        pending_hazards = max(0, pending_hazards)

        log = StepLog.objects.create(
            campaign=campaign,
            party=party,
            step_type="travel",
            action_type="hazard",
            rng_seed=seed,
            dice_rolled=dice_rolled,
            effects_applied=effects,
            narrative=str(
                cast(dict[str, Any], chosen_hazard.definition or {}).get(
                    "narrative", chosen_hazard.name
                )
            ),
        )
        resolved.append(
            {
                "hazard": chosen_hazard.name,
                "table_roll": table_roll,
                "effects": effects,
                "log_id": int(log.pk),
            }
        )

    destination_name = (settlement_name or settlement_size.title()).strip()[:120]
    party.current_settlement_size = settlement_size
    party.current_location_name = destination_name
    party.save(
        update_fields=[
            "current_settlement_size",
            "current_location_name",
            "updated_at",
        ]
    )
    sequence = StepLog.objects.filter(campaign=campaign).count() + 1
    arrival_seed = derive_step_seed(
        campaign.seed, "travel", "arrival", f"party:{party.pk}", sequence
    )
    StepLog.objects.create(
        campaign=campaign,
        party=party,
        step_type="travel",
        action_type="arrival",
        rng_seed=arrival_seed,
        dice_rolled=[],
        effects_applied={
            "settlement_size": settlement_size,
            "location_name": destination_name,
        },
        narrative=f"The party arrives at {destination_name}.",
    )

    return {
        "settlement_size": settlement_size,
        "settlement_name": destination_name,
        "encumbrance_penalty": encumbrance_penalty,
        "resolved_hazards": resolved,
        "party_gold": party.gold,
        "party_supplies": party.supplies,
        "party_morale": party.morale,
    }


def _apply_hazard_effects(
    party: Party, hazard: HazardDef, rng: DeterministicRng
) -> dict[str, Any]:
    definition = cast(dict[str, Any], hazard.definition or {})
    effects = cast(list[dict[str, Any]], definition.get("effects", []))

    applied: dict[str, Any] = {
        "gold_delta": 0,
        "supplies_delta": 0,
        "morale_delta": 0,
        "injuries": [],
        "extra_hazards": 0,
    }

    for effect in effects:
        effect_type = effect.get("type")
        min_value = int(effect.get("min", 0))
        max_value = int(effect.get("max", min_value))
        value = (
            rng.randint(min_value, max_value) if max_value >= min_value else min_value
        )

        if effect_type == "gold_loss":
            party.gold = max(0, party.gold - value)
            applied["gold_delta"] -= value
        elif effect_type == "supplies_loss":
            party.supplies = max(0, party.supplies - value)
            applied["supplies_delta"] -= value
        elif effect_type == "morale_change":
            party.morale += value
            applied["morale_delta"] += value
        elif effect_type == "injury_random_hero":
            hero = Hero.objects.filter(party=party).order_by("id").first()
            if hero:
                hero.current_health = max(0, hero.current_health - value)
                hero.save(update_fields=["current_health", "updated_at"])
                applied["injuries"].append({"hero": hero.name, "damage": value})
        elif effect_type == "extra_hazards":
            applied["extra_hazards"] += value

    party.save(update_fields=["gold", "supplies", "morale", "updated_at"])
    return applied
