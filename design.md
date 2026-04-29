# Quest Between — Design Document

## 1. Overview

Quest Between is a Django and PostgreSQL web application that models the campaign layer of a party-based fantasy adventure game. The player controls the whole party and interacts with the world through expedition planning, simulated outcomes, travel hazards, settlement actions, training, and random events.

The design intentionally excludes tactical dungeon play. The system must instead provide strong state management, deterministic randomness, and rich event-driven gameplay.

## 2. Architectural Approach

### 2.1 Application style
- Django monolith
- PostgreSQL as primary system of record
- Django templates with HTMX for first UI implementation
- Docker Compose deployment

### 2.2 Design principles
- Keep gameplay logic in a dedicated service layer
- Treat every game action as a transaction
- Record every mutation in an event log
- Keep content and rules configurable where practical

## 3. High-Level Components

### 3.1 Web layer
Responsible for:
- routing
- forms and validation
- rendering templates
- presenting game state

### 3.2 Domain services
Responsible for:
- expedition simulation
- travel hazard resolution
- settlement day processing
- event application
- inventory changes
- progression and training

### 3.3 Persistence layer
Responsible for:
- campaign state
- hero state
- inventories
- content definitions
- event logs

## 4. Core Data Model

### 4.1 Campaign
Represents a single persistent game world.

Suggested fields:
- id
- name
- created_at
- updated_at
- base_rng_seed
- settings_json
- current_state

### 4.2 Party
Represents the active party inside a campaign.

Suggested fields:
- campaign
- name
- current_location_type
- current_location_name
- leader_hero
- week_counter
- day_counter
- gold_shared_optional

### 4.3 Hero
Represents a persistent character.

Suggested fields:
- party
- name
- archetype
- battle_level
- current_wounds
- starting_wounds
- gold
- core_stats_json or explicit columns
- luck
- status
- alive

### 4.4 InventoryItem
Represents an owned item.

Suggested fields:
- owner_type
- owner_id
- item_def
- quantity
- charges
- condition_state

### 4.5 Content Models
These define data-driven game content.

Suggested models:
- HeroArchetypeDef
- HazardDef
- SettlementEventDef
- CatastrophicEventDef
- ItemDef
- ShopDef
- SkillDef
- ExpeditionTableDef
- ContentPack

### 4.6 StepLog
Represents an immutable record of each applied action.

Suggested fields:
- campaign
- step_type
- actor_type
- actor_id
- timestamp
- rng_seed
- rolls_json
- effects_json
- summary_text
- before_hash_optional
- after_hash_optional

## 5. State Mutation Strategy

### 5.1 Rule
Every state-changing action must:
1. load the relevant current state
2. calculate its outcome deterministically
3. apply the mutation inside a database transaction
4. create a StepLog entry in the same transaction

### 5.2 Why
This gives:
- consistency
- auditability
- replay
- easier debugging
- safer balance iteration

## 6. Randomness Design

### 6.1 Deterministic RNG
Randomness must be derived from a stored campaign seed and a predictable per-step derivation.

Suggested formula inputs:
- campaign base seed
- step type
- actor identity
- step counter or generated step id

### 6.2 Required outputs to store
- dice rolled
- modifiers
- selected table result
- any rerolls

## 7. Core System Designs

### 7.1 Expedition Simulation System

#### Purpose
Replace dungeon crawling with an off-screen simulation that still produces meaningful campaign consequences.

#### Inputs
- current party state
- hero archetypes and levels
- current wounds and conditions
- gear and consumables
- risk profile
- objective type
- duration profile if used

#### Outputs
- gold delta
- item rewards
- condition changes
- injury changes
- death state changes
- progression gains
- narrative summary
- detailed combat or expedition ledger for debug display

#### Design notes
Use weighted probability systems driven by party power score versus risk tier. Keep the implementation explainable and testable.

### 7.2 Travel System

#### Flow
1. Player selects destination tier
2. System assigns baseline hazard count
3. For each hazard:
   - derive RNG seed
   - roll table
   - apply effects
   - append log
4. If hazard adds time, increase pending hazard count
5. On completion, transition party to settlement state

#### Requirements
- Hazards affect the whole party
- Hazards can be original content but data-driven
- Hazard effects must support inventory, wounds, delay, economy, and route flags

### 7.3 Settlement Loop

#### Time model
- Days are the main action unit
- Weeks are used for special triggers and upkeep

#### Daily flow
For each hero:
1. choose action
2. resolve action
3. resolve settlement event
4. persist and log

#### Weekly flow
- increment week counter after each 7-day block
- apply upkeep
- after week 2, resolve one catastrophic event per week

### 7.4 Shop System

#### Requirements
- Settlement tier influences availability roll size
- Item definition includes stock threshold and price
- Purchase flow must verify affordability and availability
- Selling must update item ownership and gold values atomically

### 7.5 Progression System

#### Requirements
- Battle level advancement based on progression accumulation
- Training consumes time and gold
- Level-up changes may include:
  - wounds
  - stats
  - luck
  - skill acquisition

#### Skill acquisition
- Skill pools are archetype-specific
- Duplicate rolls reroll
- Skill content stored in database

## 8. Content System Design

### 8.1 Data-driven content
Game content must live in database models and be editable via Django admin.

### 8.2 Import and export
Later support JSON import and export for content packs.

### 8.3 Benefits
- easier balancing
- cleaner code
- less hardcoding
- easier future modding

## 9. UI Design Direction

### 9.1 Initial UI style
- server-rendered pages
- HTMX for partial updates
- event cards and logs instead of complex client-side apps

### 9.2 Primary screens
- campaign list and create
- campaign dashboard
- party management
- hero detail
- expedition setup
- expedition result
- travel hazard screen
- settlement hub
- event resolution
- admin content editing

### 9.3 UX principles
- make consequences obvious
- avoid burying the player in raw numbers
- always show what changed
- make repeated loops efficient

## 10. Testing Strategy

### 10.1 Unit tests
Write unit tests for:
- RNG derivation
- expedition outcome calculations
- hazard resolution
- event application
- shop availability
- training and skill assignment

### 10.2 Integration tests
Write integration tests for:
- complete expedition to settlement loop
- atomic transaction behaviour
- state persistence after step logging

## 11. Deployment Design

### 11.1 Containers
- web: Django + gunicorn
- db: PostgreSQL
- optional reverse proxy later

### 11.2 Storage
- persistent Postgres volume
- optional media or export volume

### 11.3 Environment
Use environment variables for:
- Django secret key
- database credentials
- debug mode
- allowed hosts

## 12. Suggested App Structure

Possible Django apps:
- `campaigns`
- `heroes`
- `content`
- `simulation`
- `economy`
- `events`
- `ui`

Keep actual business rules in service modules within these apps rather than burying them in models.

## 13. Implementation Order

### Stage 1
- Project setup
- Postgres integration
- Core models
- Admin

### Stage 2
- StepLog
- RNG utilities
- Expedition simulation service

### Stage 3
- Travel hazards
- Settlement day loop
- Event systems

### Stage 4
- Shops, inventory, progression, training

### Stage 5
- Template polish and UX improvements

## 14. Risks and Mitigations

### Risk: content explosion
Mitigation: start with a limited content pack and ensure definitions are reusable.

### Risk: tangled business rules
Mitigation: use a clear service layer and extensive tests.

### Risk: hardcoded tables
Mitigation: enforce content-driven definitions and keep logic generic.

### Risk: poor debuggability
Mitigation: log every step with RNG and applied effects.
