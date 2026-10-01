# Inventory, Trade, and Crafting

## Inventory Model

Items are database-defined and stored as quantities owned either by the party or an individual hero. Item definitions include category, price, stock threshold, weight, and extensible JSON properties.

## Trade and Carrying Capacity

- Shop definitions are tier-specific and editable through Django admin/content packs.
- Buying checks availability and funds; selling checks owned quantity. Both are atomic and logged.
- Carry weight influences travel and expedition penalties.
- Crafting recipes consume defined ingredients and grant defined outputs atomically.

## Content Portability

Item, shop, and recipe definitions can be included in JSON content packs. Inventory does not implement weapon damage, equipment slots, quest-item locks, or tactical effects.
