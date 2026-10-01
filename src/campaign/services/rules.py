from typing import Any

from django.core.exceptions import ImproperlyConfigured

from campaign.models import GameRuleDef


def get_game_rules() -> dict[str, Any]:
    try:
        rule_def = GameRuleDef.objects.get(code="core")
    except GameRuleDef.DoesNotExist as error:
        raise ImproperlyConfigured(
            "Core game rules are missing; apply the campaign migrations."
        ) from error

    if not isinstance(rule_def.definition, dict):
        raise ImproperlyConfigured("Core game rules must be a JSON object.")
    return rule_def.definition
