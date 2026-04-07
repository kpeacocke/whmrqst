from django.db import transaction

from campaign.models import HazardDef, Hero, Party, StepLog
from campaign.services.crafting import get_party_encumbrance_penalty
from campaign.services.rng import DeterministicRng, derive_step_seed

WHQ_SOURCE = "whq_roleplay_book"


HAZARDS_BY_SETTLEMENT = {
    HazardDef.SettlementSize.VILLAGE: 2,
    HazardDef.SettlementSize.TOWN: 4,
    HazardDef.SettlementSize.CITY: 6,
}


@transaction.atomic
def resolve_travel_hazards(party: Party, settlement_size: str) -> dict:
    campaign = party.campaign
    hazards = list(HazardDef.objects.filter(definition__source=WHQ_SOURCE))
    if not hazards:
        hazards = list(HazardDef.objects.filter(settlement_size=settlement_size))
    if not hazards:
        raise ValueError("No hazards are configured for travel resolution")

    hazards_by_roll = {
        str(hazard.definition.get("table_roll", "")): hazard
        for hazard in hazards
        if hazard.definition.get("table_roll")
    }

    encumbrance_penalty = get_party_encumbrance_penalty(party)
    pending_hazards = HAZARDS_BY_SETTLEMENT[settlement_size] + int(encumbrance_penalty["movement_penalty"])
    resolved = []
    safety_counter = 0

    while pending_hazards > 0 and safety_counter < 100:
        safety_counter += 1
        sequence = campaign.step_logs.count() + 1
        seed = derive_step_seed(campaign.seed, "travel", "hazard", f"party:{party.id}", sequence)
        rng = DeterministicRng(seed)

        tens = rng.d6()
        units = rng.d6()
        table_roll = f"{tens}{units}"
        chosen_hazard = hazards_by_roll.get(table_roll)
        if chosen_hazard is None:
            chosen_hazard = rng.choice(hazards)

        dice_rolled = [
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
            narrative=chosen_hazard.definition.get("narrative", chosen_hazard.name),
        )
        resolved.append({
            "hazard": chosen_hazard.name,
            "table_roll": table_roll,
            "effects": effects,
            "log_id": log.id,
        })

    return {
        "settlement_size": settlement_size,
        "encumbrance_penalty": encumbrance_penalty,
        "resolved_hazards": resolved,
        "party_gold": party.gold,
        "party_supplies": party.supplies,
        "party_morale": party.morale,
    }


def _apply_hazard_effects(party: Party, hazard: HazardDef, rng: DeterministicRng) -> dict:
    definition = hazard.definition or {}
    effects = definition.get("effects", [])

    applied = {
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
        value = rng.randint(min_value, max_value) if max_value >= min_value else min_value

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
