from typing import Any

from django.db import transaction

from campaign.models import Expedition, ExpeditionDef, Hero, InventoryItem, ItemDef, Party, StepLog
from campaign.services.crafting import get_party_encumbrance_penalty
from campaign.services.rng import DeterministicRng, derive_step_seed


RISK_CONFIG = {
    "cautious": {
        "reward_pct": 0.75,
        "challenge_mod": -1,
        "injury_mod": -1,
        "morale_on_success": 0,
    },
    "standard": {
        "reward_pct": 1.0,
        "challenge_mod": 0,
        "injury_mod": 0,
        "morale_on_success": 1,
    },
    "reckless": {
        "reward_pct": 1.4,
        "challenge_mod": 2,
        "injury_mod": 1,
        "morale_on_success": 2,
    },
}


@transaction.atomic
def resolve_expedition(party: Party, expedition_def: ExpeditionDef, risk_level: str) -> dict[str, Any]:
    campaign = party.campaign
    living_heroes = _get_living_heroes(party)

    sequence = StepLog.objects.filter(campaign=campaign).count() + 1
    seed = derive_step_seed(campaign.seed, "expedition", "run", f"party:{party.pk}", sequence)
    rng = DeterministicRng(seed)
    config = RISK_CONFIG[risk_level]
    encumbrance_penalty = get_party_encumbrance_penalty(party)

    challenge_roll = rng.randint(2, 12)
    challenge_total = challenge_roll + int(expedition_def.difficulty) + int(config["challenge_mod"])
    party_power = sum(hero.level for hero in living_heroes) + len(living_heroes)
    success_margin = party_power - challenge_total
    is_success = success_margin >= 0

    reward_roll = rng.randint(int(expedition_def.base_reward_min), int(expedition_def.base_reward_max))
    base_reward = int(reward_roll * float(config["reward_pct"]))
    gold_delta = base_reward if is_success else max(0, base_reward // 3)

    supply_cost = _get_supply_cost(expedition_def, risk_level)
    dice_rolled = [
        {"die": "2d6", "result": challenge_roll, "context": "challenge-roll"},
        {"die": "d100", "result": reward_roll, "context": "reward-roll"},
    ]
    injuries, deaths, conditions_gained = _resolve_expedition_injuries(
        living_heroes=living_heroes,
        expedition_def=expedition_def,
        config=config,
        encumbrance_penalty=encumbrance_penalty,
        rng=rng,
        dice_rolled=dice_rolled,
    )

    party.gold += gold_delta
    party.supplies = max(0, party.supplies - supply_cost)
    morale_delta = int(config["morale_on_success"]) if is_success else -1
    party.morale += morale_delta
    party.save(update_fields=["gold", "supplies", "morale", "updated_at"])

    loot = []
    if is_success:
        loot = _resolve_expedition_loot(party, expedition_def, rng, dice_rolled)

    narrative = (
        f"{party.name} completed {expedition_def.name}: "
        f"{'success' if is_success else 'setback'} with {gold_delta} gold, "
        f"{len(injuries)} injuries, {len(deaths)} deaths, and {len(loot)} items looted."
    )

    effects = {
        "success": is_success,
        "success_margin": success_margin,
        "encumbrance_penalty": encumbrance_penalty,
        "party_gold_delta": gold_delta,
        "party_supplies_delta": -supply_cost,
        "party_morale_delta": morale_delta,
        "injuries": injuries,
        "deaths": deaths,
        "conditions_gained": conditions_gained,
        "loot": loot,
        "objective": expedition_def.code,
        "risk_level": risk_level,
    }

    step_log = StepLog.objects.create(
        campaign=campaign,
        party=party,
        step_type="expedition",
        action_type="run",
        rng_seed=seed,
        dice_rolled=dice_rolled,
        effects_applied=effects,
        narrative=narrative,
    )

    expedition = Expedition.objects.create(
        campaign=campaign,
        party=party,
        expedition_def=expedition_def,
        risk_level=risk_level,
        result={
            "step_log_id": int(step_log.pk),
            "success": is_success,
            "narrative": narrative,
            **effects,
        },
    )

    return {
        "expedition_id": int(expedition.pk),
        "step_log_id": int(step_log.pk),
        "narrative": narrative,
        **effects,
    }


def _get_living_heroes(party: Party) -> list[Hero]:
    heroes = list(Hero.objects.filter(party=party).order_by("id"))
    if not heroes:
        raise ValueError("Party must have at least one hero")

    living_heroes = [hero for hero in heroes if hero.alive]
    if not living_heroes:
        raise ValueError("Party has no living heroes")
    return living_heroes


def _get_supply_cost(expedition_def: ExpeditionDef, risk_level: str) -> int:
    supply_cost = max(1, int(expedition_def.base_supply_cost))
    if risk_level == "cautious":
        return max(1, supply_cost - 1)
    if risk_level == "reckless":
        return supply_cost + 1
    return supply_cost


def _resolve_expedition_injuries(
    living_heroes: list[Hero],
    expedition_def: ExpeditionDef,
    config: dict[str, float | int],
    encumbrance_penalty: dict[str, int],
    rng: DeterministicRng,
    dice_rolled: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    injuries: list[dict[str, Any]] = []
    deaths: list[dict[str, Any]] = []
    conditions_gained: list[dict[str, Any]] = []
    injury_target = max(
        2,
        int(expedition_def.base_injury_risk)
        + int(config["injury_mod"])
        + int(encumbrance_penalty["agility_penalty"]),
    )

    for hero in living_heroes:
        injury_roll = rng.d6()
        dice_rolled.append(
            {
                "die": "d6",
                "result": injury_roll,
                "target": injury_target,
                "hero": hero.name,
                "context": "injury-check",
            }
        )

        if injury_roll <= injury_target:
            injury_record, death_record, condition_record = _apply_expedition_injury(hero, rng, dice_rolled)
            injuries.append(injury_record)
            conditions_gained.append(condition_record)
            if death_record is not None:
                deaths.append(death_record)

        _apply_expedition_progression(hero)

    return injuries, deaths, conditions_gained


def _apply_expedition_injury(
    hero: Hero,
    rng: DeterministicRng,
    dice_rolled: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any] | None, dict[str, Any]]:
    damage = rng.randint(1, 3)
    hero.current_health = max(0, hero.current_health - damage)
    dice_rolled.append(
        {
            "die": "d3",
            "result": damage,
            "hero": hero.name,
            "context": "injury-damage",
        }
    )

    conditions = list(hero.conditions)
    death_record: dict[str, Any] | None = None
    if hero.current_health == 0:
        hero.alive = False
        if "dead" not in conditions:
            conditions.append("dead")
        death_record = {"hero": hero.name, "damage": damage}
        hero.conditions = conditions
        hero.save(update_fields=["current_health", "alive", "conditions", "updated_at"])
    else:
        if "injured" not in conditions:
            conditions.append("injured")
        hero.conditions = conditions
        hero.save(update_fields=["current_health", "conditions", "updated_at"])

    return (
        {"hero": hero.name, "damage": damage, "dead": hero.current_health == 0},
        death_record,
        {"hero": hero.name, "conditions": list(hero.conditions)},
    )


def _apply_expedition_progression(hero: Hero) -> None:
    stats = dict(hero.stats or {})
    stats["expedition_progress"] = int(stats.get("expedition_progress", 0)) + 1
    hero.stats = stats
    hero.save(update_fields=["stats", "updated_at"])


def _resolve_expedition_loot(
    party: Party,
    expedition_def: ExpeditionDef,
    rng: DeterministicRng,
    dice_rolled: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    definition = expedition_def.definition or {}
    loot_table = definition.get("loot_table", [])
    if not loot_table:
        return []

    options = [(entry["item_name"], int(entry.get("weight", 1))) for entry in loot_table]
    item_name = rng.weighted_choice(options)
    dice_rolled.append({"die": "weighted", "result": item_name, "context": "loot-roll"})

    item_def = ItemDef.objects.filter(name=item_name).first()
    if item_def is None:
        return []

    inventory_item, _ = InventoryItem.objects.get_or_create(
        party=party,
        hero=None,
        item_def=item_def,
        defaults={"quantity": 0},
    )
    inventory_item.quantity += 1
    inventory_item.save(update_fields=["quantity", "updated_at"])
    return [{"item_name": item_name, "quantity": 1}]
