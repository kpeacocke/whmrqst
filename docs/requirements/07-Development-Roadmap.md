# Development Roadmap

## MVP: Campaign Loop

- [x] Django/PostgreSQL application, campaign persistence, admin, and Docker Compose.
- [x] Campaign and party creation, one-to-four hero roster, authentication, ownership checks, import/export, and a hero sheet.
- [x] Deterministic expedition simulation with risk profiles and StepLog outcomes.
- [x] Travel hazards with persisted destination, settlement actions, daily party completion, and weekly events.
- [x] Database-driven rules, hazards, event definitions, locations, items, shops, skills, and recipes; safe first-run content bootstrap.
- [x] Trade, inventory weight, crafting, training, injury, recovery, and progression.
- [x] Server-rendered campaign UI and campaign-cycle integration coverage.
- [x] CI checks for migration drift, Django tests, pytest, Ruff, and Mypy.

## Release Hardening

- [x] Add PostgreSQL-backed CI integration coverage in addition to SQLite service tests.
- [x] Verify PostgreSQL row locking prevents concurrent shop double-spend.
- [x] Cover concurrent shop, expedition, travel, crafting, and settlement mutations plus rollback failures for gameplay services on PostgreSQL.
- [x] Exercise backup and restore against an isolated PostgreSQL database; document host-operated backup/restore.
- [x] Smoke-check campaign and hero-sheet rendering at desktop/mobile widths; verify static assets load and no horizontal overflow occurs.
- [ ] Conduct manual usability testing and incorporate player feedback.

## Explicitly Out of Scope

- Dungeon maps, grid movement, tactical combat, quests, multiplayer, and cloud-only features.

The MVP acceptance gate is a new campaign completing expedition → travel → settlement → trade/crafting → export/import, with every result persisted and logged deterministically.
