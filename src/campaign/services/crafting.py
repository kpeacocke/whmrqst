from django.db import transaction
from django.db.models import F, Sum

from campaign.models import CraftingRecipeDef, Hero, InventoryItem, ItemDef, Party, StepLog
from campaign.services.rng import derive_step_seed


ENCUMBRANCE_BASE_CAPACITY = 10


def get_hero_carry_capacity(hero: Hero) -> int:
    """Return the maximum total item weight a hero can carry."""
    return ENCUMBRANCE_BASE_CAPACITY + (hero.level * 2)


def get_hero_carry_weight(hero: Hero) -> int:
    """Return the current total weight of items assigned to this hero."""
    result = (
        InventoryItem.objects.filter(hero=hero)
        .aggregate(total=Sum(F("item_def__weight") * F("quantity")))["total"]
    )
    return result or 0


@transaction.atomic
def resolve_crafting(
    party: Party,
    recipe_def: CraftingRecipeDef,
    hero: Hero | None = None,
) -> dict:
    """
    Attempt to craft the output item defined by recipe_def.

    Ingredients are consumed from party-level inventory (hero=None).
    Output is placed in party-level inventory (hero=None).
    All state changes are logged to StepLog.
    Returns a dict with "status" of "success" or "rejected".
    """
    campaign = party.campaign
    definition = recipe_def.definition or {}
    ingredients = definition.get("ingredients", [])
    output_item_name = definition.get("output_item_name", "")
    output_quantity = int(definition.get("output_quantity", 1))

    sequence = campaign.step_logs.count() + 1
    actor_key = f"party:{party.id}"
    seed = derive_step_seed(campaign.seed, "crafting", "craft", actor_key, sequence)

    # Validate all ingredients are available before consuming any.
    for ingredient in ingredients:
        item_name = ingredient["item_name"]
        required_qty = int(ingredient.get("quantity", 1))
        inv_row = InventoryItem.objects.filter(
            party=party, hero=None, item_def__name=item_name
        ).first()
        if not inv_row or inv_row.quantity < required_qty:
            effects = {
                "status": "rejected",
                "reason": "insufficient_ingredients",
                "missing_item": item_name,
                "required": required_qty,
                "available": inv_row.quantity if inv_row else 0,
            }
            StepLog.objects.create(
                campaign=campaign,
                party=party,
                hero=hero,
                step_type="crafting",
                action_type="crafting_rejected",
                rng_seed=seed,
                dice_rolled=[],
                effects_applied=effects,
                narrative=f"Crafting {recipe_def.name} failed: insufficient {item_name}.",
            )
            return effects

    # Consume ingredients.
    items_consumed = []
    for ingredient in ingredients:
        item_name = ingredient["item_name"]
        required_qty = int(ingredient.get("quantity", 1))
        inv_row = InventoryItem.objects.select_for_update().get(
            party=party, hero=None, item_def__name=item_name
        )
        inv_row.quantity -= required_qty
        if inv_row.quantity == 0:
            inv_row.delete()
        else:
            inv_row.save(update_fields=["quantity", "updated_at"])
        items_consumed.append({"item_name": item_name, "quantity": required_qty})

    # Grant output item to party inventory.
    output_item = ItemDef.objects.get(name=output_item_name)
    output_row, _ = InventoryItem.objects.select_for_update().get_or_create(
        party=party,
        hero=None,
        item_def=output_item,
        defaults={"quantity": 0},
    )
    output_row.quantity += output_quantity
    output_row.save(update_fields=["quantity", "updated_at"])

    effects = {
        "status": "success",
        "recipe": recipe_def.code,
        "items_consumed": items_consumed,
        "output_item_name": output_item_name,
        "output_quantity": output_quantity,
    }

    StepLog.objects.create(
        campaign=campaign,
        party=party,
        hero=hero,
        step_type="crafting",
        action_type="craft",
        rng_seed=seed,
        dice_rolled=[],
        effects_applied=effects,
        narrative=f"{party.name} crafted {output_quantity}x {output_item_name} using {recipe_def.name}.",
    )

    return effects
