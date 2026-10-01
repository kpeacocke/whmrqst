# Character System

## Hero Creation

Each hero belongs to the campaign party and uses one of the supported archetypes: Warrior, Ranger, Mage, or Priest. A party has one to four heroes.

## Persistent State

- Name and archetype.
- Level, health, stats, conditions, and alive/dead status.
- Days unavailable and settlement-specific persistent effects.
- Skills acquired through progression and stored as hero-skill records.
- Items owned by the hero, distinct from shared party inventory.

## Progression and Recovery

- Training costs party gold and consumes the hero's daily action.
- Level advancement improves health and can grant an unlearned archetype skill.
- Expeditions add progression and may cause health loss, conditions, or death.
- Rest and healing recover health; unavailable heroes consume their daily action while recovering.

## Design Boundary

Archetype skills are campaign content. This system does not define combat attributes, initiative, enemy turns, tactical abilities, or dungeon status rules.
