# Copilot Instructions

## Project intent
This project is a browser-based single-player campaign game built with Django and PostgreSQL.

The game focuses on:
- party management
- expedition simulation
- travel hazards
- settlement events
- shopping
- healing
- training
- progression

The game does **not** include:
- dungeon maps
- grid movement
- tactical combat
- room-by-room exploration

## Coding expectations
- Use Australian English in comments, documentation, and user-facing text.
- Prefer clear, maintainable code over clever shortcuts.
- Keep game content data-driven.
- Do not hardcode hazards, events, items, or skill content inside service logic unless explicitly asked.
- Write deterministic logic for simulation systems.
- Avoid hidden randomness; log rolls and seeds.
- Use Django best practices with a clean separation between models, services, views, and templates.
- Use database transactions for all state-changing game actions.
- Avoid putting business logic into model save methods or templates.

## Testing expectations
- Add unit tests for simulation and state mutation logic.
- Add integration tests for end-to-end campaign flow.
- Test deterministic RNG behaviour.
- Test failure and rollback cases for transactional actions.

## Architecture expectations
- Use Django as a monolith.
- Use PostgreSQL as the database.
- Prefer Django templates and HTMX for the first UI implementation.
- Keep the StepLog or equivalent event log central to all state mutation.

## Content expectations
- Treat all hazards, events, shops, skills, and items as editable content.
- Design schemas so future JSON import/export is straightforward.
- Keep content models expressive enough for future expansion.

## Guardrails
- Do not introduce tactical combat systems.
- Do not add multiplayer unless explicitly requested.
- Do not replace PostgreSQL with MongoDB or SQLite.
- Do not introduce unnecessary frontend complexity early.
