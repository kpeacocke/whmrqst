# Game Rules and Mechanics

## Campaign Time and Actions

- Campaign time is tracked in days and weeks.
- Each living hero may resolve one settlement action per day; party actions are separately logged.
- A day completes only after all living heroes have acted or taken an unavailable skip.

## Resources and Determinism

- The campaign tracks party gold, supplies, morale, hero health, conditions, and inventory.
- Each state-changing gameplay service runs transactionally and records a StepLog.
- A campaign seed and per-step sequence derive deterministic random outcomes; rolls and effects are persisted.
- Rules, content, and balance tables are editable and portable through content packs.

## Expedition Resolution

- Expeditions are off-screen simulations using party capability, objective, risk, and content definitions.
- Outcomes can include rewards, supplies consumed, loot, injury, death, conditions, and progression.

## Explicit Exclusions

No turn-based combat, enemy initiative, tactical actions, dungeon turns, or grid movement are implemented.
