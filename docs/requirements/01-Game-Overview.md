# Game Overview

Quest Between is a single-player, browser-based campaign RPG. The player manages a party of one to four heroes between adventures; expeditions resolve through deterministic simulation and return persistent consequences to the campaign.

## Supported Play

- Create and manage campaigns, parties, and heroes.
- Simulate expeditions using party capability, risk, and editable expedition definitions.
- Resolve travel hazards, settlement actions, events, trade, crafting, training, injury, and recovery.
- Review the campaign chronicle, export campaign state, and import it later.

## Platform

- Django templates and PostgreSQL, deployable with Docker Compose.
- Desktop browser first, usable on a local network.
- Single-player only.

## Explicit Exclusions

- Dungeon maps, room exploration, grid movement, or tactical/turn-based combat.
- Quest trees, enemy encounters, platforming, multiplayer, or cloud-only services.

Game rules and campaign content belong in database definitions and content packs, not in template copy or UI-specific logic.
