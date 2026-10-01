from typing import Any

from campaign.models import Campaign, Hero, Party, StepLog
from campaign.services.rng import derive_step_seed


def log_campaign_mutation(
    campaign: Campaign,
    action_type: str,
    effects: dict[str, Any],
    narrative: str,
    party: Party | None = None,
    hero: Hero | None = None,
) -> StepLog:
    sequence = StepLog.objects.filter(campaign=campaign).count() + 1
    actor_key = "campaign"
    if party is not None:
        actor_key = f"party:{party.pk}"
    if hero is not None:
        actor_key = f"hero:{hero.pk}"
    seed = derive_step_seed(campaign.seed, "campaign", action_type, actor_key, sequence)
    return StepLog.objects.create(
        campaign=campaign,
        party=party,
        hero=hero,
        step_type="campaign",
        action_type=action_type,
        rng_seed=seed,
        dice_rolled=[],
        effects_applied=effects,
        narrative=narrative,
    )
