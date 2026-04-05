from django.db import transaction

from campaign.models import Expedition, ExpeditionDef, Hero, Party, StepLog
from campaign.services.rng import DeterministicRng, derive_step_seed


RISK_CONFIG = {
    Expedition.RiskLevel.CAUTIOUS: {
        "reward_pct": 0.75,
        "challenge_mod": -1,
        "injury_mod": -1,
        "morale_on_success": 0,
    },
    Expedition.RiskLevel.STANDARD: {
        "reward_pct": 1.0,
        "challenge_mod": 0,
        "injury_mod": 0,
        "morale_on_success": 1,
    },
    Expedition.RiskLevel.RECKLESS: {
        "reward_pct": 1.4,
        "challenge_mod": 2,
        "injury_mod": 1,
        "morale_on_success": 2,
    },
}


@transaction.atomic
def resolve_expedition(party: Party, expedition_def: ExpeditionDef, risk_level: str) -> dict:
    campaign = party.campaign
    heroes = list(Hero.objects.filter(party=party).order_by("id"))
    if not heroes:
        raise ValueError("Party must have at least one hero")

    sequence = campaign.step_logs.count() + 1
    seed = derive_step_seed(campaign.seed, "expedition", "run", f"party:{party.id}", sequence)
    rng = DeterministicRng(seed)
    config = RISK_CONFIG[risk_level]

    challenge_roll = rng.randint(2, 12)
    challenge_total = challenge_roll + int(expedition_def.difficulty) + int(config["challenge_mod"])
    party_power = sum(hero.level for hero in heroes) + len(heroes)
    success_margin = party_power - challenge_total
    is_success = success_margin >= 0

    reward_roll = rng.randint(int(expedition_def.base_reward_min), int(expedition_def.base_reward_max))
    base_reward = int(reward_roll * float(config["reward_pct"]))
    gold_delta = base_reward if is_success else max(0, base_reward // 3)

    supply_cost = max(1, int(expedition_def.base_supply_cost))
    if risk_level == Expedition.RiskLevel.CAUTIOUS:
        supply_cost = max(1, supply_cost - 1)
    elif risk_level == Expedition.RiskLevel.RECKLESS:
        supply_cost += 1

    injuries = []
    dice_rolled = [
        {"die": "2d6", "result": challenge_roll, "context": "challenge-roll"},
        {"die": "d100", "result": reward_roll, "context": "reward-roll"},
    ]

    for hero in heroes:
        injury_target = max(2, int(expedition_def.base_injury_risk) + int(config["injury_mod"]))
        injury_roll = rng.d6()
        dice_rolled.append({
            "die": "d6",
            "result": injury_roll,
            "target": injury_target,
            "hero": hero.name,
            "context": "injury-check",
        })
        if injury_roll <= injury_target:
            damage = rng.randint(1, 3)
            hero.current_health = max(1, hero.current_health - damage)
            hero.save(update_fields=["current_health", "updated_at"])
            injuries.append({"hero": hero.name, "damage": damage})
            dice_rolled.append({
                "die": "d3",
                "result": damage,
                "hero": hero.name,
                "context": "injury-damage",
            })

    party.gold += gold_delta
    party.supplies = max(0, party.supplies - supply_cost)
    morale_delta = int(config["morale_on_success"]) if is_success else -1
    party.morale += morale_delta
    party.save(update_fields=["gold", "supplies", "morale", "updated_at"])

    narrative = (
        f"{party.name} completed {expedition_def.name}: "
        f"{'success' if is_success else 'setback'} with {gold_delta} gold and {len(injuries)} injuries."
    )

    effects = {
        "success": is_success,
        "success_margin": success_margin,
        "party_gold_delta": gold_delta,
        "party_supplies_delta": -supply_cost,
        "party_morale_delta": morale_delta,
        "injuries": injuries,
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
            "step_log_id": step_log.id,
            "success": is_success,
            "narrative": narrative,
            **effects,
        },
    )

    return {
        "expedition_id": expedition.id,
        "step_log_id": step_log.id,
        "narrative": narrative,
        **effects,
    }
