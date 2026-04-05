from django.db import transaction

from campaign.models import HazardDef, InventoryItem, ItemDef, Party, StepLog
from campaign.services.rng import DeterministicRng, derive_step_seed


STOCK_DICE_BY_SETTLEMENT = {
    HazardDef.SettlementSize.VILLAGE: 1,
    HazardDef.SettlementSize.TOWN: 2,
    HazardDef.SettlementSize.CITY: 3,
}


@transaction.atomic
def process_shop_transaction(
    party: Party,
    settlement_size: str,
    transaction_type: str,
    item_def: ItemDef,
    quantity: int,
) -> dict:
    locked_party = Party.objects.select_for_update().get(id=party.id)
    campaign = locked_party.campaign
    sequence = campaign.step_logs.count() + 1
    actor_key = f"party:{locked_party.id}"
    seed = derive_step_seed(campaign.seed, "economy", transaction_type, actor_key, sequence)
    rng = DeterministicRng(seed)

    if transaction_type == "buy":
        return _buy_item(locked_party, settlement_size, item_def, quantity, rng, seed)
    if transaction_type == "sell":
        return _sell_item(locked_party, settlement_size, item_def, quantity, rng, seed)
    raise ValueError(f"Unsupported transaction type: {transaction_type}")


def _buy_item(
    party: Party,
    settlement_size: str,
    item_def: ItemDef,
    quantity: int,
    rng: DeterministicRng,
    seed: str,
) -> dict:
    stock_dice_count = STOCK_DICE_BY_SETTLEMENT.get(settlement_size, 1)
    stock_rolls = [rng.d6() for _ in range(stock_dice_count)]
    stock_total = sum(stock_rolls)
    available_stock = max(0, stock_total - max(1, item_def.stock_value) + 1)

    effective_unit_price = item_def.base_price * max(1, party.hardship_price_multiplier)
    total_price = effective_unit_price * quantity

    if available_stock < quantity:
        effects = {
            "status": "rejected",
            "reason": "insufficient_stock",
            "requested_quantity": quantity,
            "available_stock": available_stock,
            "unit_price": effective_unit_price,
            "total_price": total_price,
        }
        _log_economy_step(
            party,
            action_type="buy_rejected",
            seed=seed,
            dice_rolled=[{"die": "d6", "result": roll, "context": "stock-roll"} for roll in stock_rolls],
            effects_applied=effects,
            narrative=f"Stock check failed for {item_def.name}.",
        )
        return effects

    if party.gold < total_price:
        effects = {
            "status": "rejected",
            "reason": "insufficient_gold",
            "requested_quantity": quantity,
            "available_stock": available_stock,
            "unit_price": effective_unit_price,
            "total_price": total_price,
        }
        _log_economy_step(
            party,
            action_type="buy_rejected",
            seed=seed,
            dice_rolled=[{"die": "d6", "result": roll, "context": "stock-roll"} for roll in stock_rolls],
            effects_applied=effects,
            narrative=f"Purchase failed due to low gold: {item_def.name}.",
        )
        return effects

    inventory_row, _ = InventoryItem.objects.select_for_update().get_or_create(
        party=party,
        hero=None,
        item_def=item_def,
        defaults={"quantity": 0},
    )
    inventory_row.quantity += quantity
    inventory_row.save(update_fields=["quantity", "updated_at"])

    party.gold -= total_price
    party.save(update_fields=["gold", "updated_at"])

    effects = {
        "status": "success",
        "transaction_type": "buy",
        "item_name": item_def.name,
        "quantity_delta": quantity,
        "party_gold_delta": -total_price,
        "requested_quantity": quantity,
        "available_stock": available_stock,
        "unit_price": effective_unit_price,
        "total_price": total_price,
    }
    _log_economy_step(
        party,
        action_type="buy",
        seed=seed,
        dice_rolled=[{"die": "d6", "result": roll, "context": "stock-roll"} for roll in stock_rolls],
        effects_applied=effects,
        narrative=f"Purchased {quantity}x {item_def.name} in a {settlement_size}.",
    )
    return effects


def _sell_item(
    party: Party,
    settlement_size: str,
    item_def: ItemDef,
    quantity: int,
    rng: DeterministicRng,
    seed: str,
) -> dict:
    del rng  # Sell operations have no availability roll in this phase.
    del settlement_size

    inventory_row = (
        InventoryItem.objects.select_for_update()
        .filter(party=party, hero=None, item_def=item_def)
        .first()
    )

    if not inventory_row or inventory_row.quantity < quantity:
        effects = {
            "status": "rejected",
            "reason": "insufficient_inventory",
            "requested_quantity": quantity,
            "available_quantity": 0 if not inventory_row else inventory_row.quantity,
            "unit_price": max(1, item_def.base_price // 2),
        }
        _log_economy_step(
            party,
            action_type="sell_rejected",
            seed=seed,
            dice_rolled=[],
            effects_applied=effects,
            narrative=f"Attempted to sell unavailable quantity of {item_def.name}.",
        )
        return effects

    unit_price = max(1, item_def.base_price // 2)
    total_sale = unit_price * quantity

    inventory_row.quantity -= quantity
    if inventory_row.quantity == 0:
        inventory_row.delete()
    else:
        inventory_row.save(update_fields=["quantity", "updated_at"])

    party.gold += total_sale
    party.save(update_fields=["gold", "updated_at"])

    effects = {
        "status": "success",
        "transaction_type": "sell",
        "item_name": item_def.name,
        "quantity_delta": -quantity,
        "party_gold_delta": total_sale,
        "unit_price": unit_price,
        "total_price": total_sale,
    }
    _log_economy_step(
        party,
        action_type="sell",
        seed=seed,
        dice_rolled=[],
        effects_applied=effects,
        narrative=f"Sold {quantity}x {item_def.name}.",
    )
    return effects


def _log_economy_step(
    party: Party,
    action_type: str,
    seed: str,
    dice_rolled: list,
    effects_applied: dict,
    narrative: str,
) -> StepLog:
    return StepLog.objects.create(
        campaign=party.campaign,
        party=party,
        step_type="economy",
        action_type=action_type,
        rng_seed=seed,
        dice_rolled=dice_rolled,
        effects_applied=effects_applied,
        narrative=narrative,
    )
