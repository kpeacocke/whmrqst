# Quest Between — Requirements Document

## 1. Purpose

Build a **single-player browser game** hosted on a NAS via Docker, where the player controls an entire party of heroes and the core gameplay is the **between-adventure campaign layer**: travel, hazards, settlements, shopping, healing, training, and random events.

Dungeon exploration and tactical combat are not part of the product. Expeditions are resolved through simulation and produce outcomes that feed back into the campaign loop.

## 2. Product Summary

### 2.1 One-line description
A campaign management RPG where the player makes strategic and narrative decisions between adventures while expedition outcomes are simulated from party capability and risk.

### 2.2 Platform
- Desktop web browser first
- Mobile-friendly later
- Self-hosted with Docker containers on a NAS

### 2.3 Player model
- Single player
- Player controls the whole party
- Initial party size: 1–4 heroes

## 3. Scope

### 3.1 In scope
- Party creation and management
- Hero persistence and progression
- Expedition simulation
- Travel hazards and time tracking
- Settlement phase with daily hero actions
- Shops, economy, healing, and training
- Hero and party events
- Campaign persistence, export, and import
- Admin-editable game content

### 3.2 Out of scope
- Dungeon maps
- Tactical combat
- Room-by-room exploration
- Real-time action systems
- Multiplayer in initial releases

## 4. Core Design Principles

1. **Between-adventure gameplay is the game**
2. **Persistent consequences matter**
3. **Events and randomness create emergent stories**
4. **All results must be understandable and reviewable**
5. **Game content must be data-driven, not hardcoded**

## 5. Core Gameplay Loop

1. Assemble or modify party
2. Choose expedition profile
3. Simulate expedition
4. Travel to settlement and resolve hazards
5. Spend time in settlement using daily hero actions
6. Resolve settlement and weekly catastrophic events
7. Depart for next expedition

## 6. Functional Requirements

### FR-01 Campaign Management
- Create, load, rename, export, import, and delete campaigns
- Persist campaign state automatically after every resolved step

### FR-02 Party Management
- Allow party size from 1 to 4 heroes
- Support multiple hero archetypes
- Allow the player to view and manage party-wide state
- Support party leader assignment for future modifiers

### FR-03 Hero State
Each hero must persist:
- Name
- Archetype
- Battle level
- Core stats
- Current wounds
- Starting wounds baseline
- Gold
- Inventory
- Skills
- Conditions and injuries
- Alive / dead state

### FR-04 Expedition Simulation
The game must support an expedition simulation system that consumes:
- Party composition
- Hero stats and conditions
- Equipment and consumables
- Expedition risk profile
- Expedition objective

The simulation must produce:
- Gold
- Loot
- Injuries
- Conditions
- Resource consumption
- Deaths where applicable
- Progression gains
- Narrative summary and structured ledger

### FR-05 Travel System
- Player chooses destination type: village, town, or city
- Destination determines number of hazard rolls
- Hazards apply to the party as a whole
- Hazards may damage the party, alter inventory, add delay, or force route changes
- Travel system must support extra hazards caused by added travel time

### FR-06 Settlement System
- Track time in days and weeks
- Each hero can take exactly one main action per day
- Supported actions:
  - buy
  - sell
  - train
  - rest
  - heal
  - visit special location

### FR-07 Events System
- Settlement events trigger after each hero action
- Weekly catastrophic events trigger after week 2 and every week thereafter
- Events can alter hero state, party state, economy, or travel
- Events must be implemented using content definitions rather than hardcoded branching logic

### FR-08 Economy and Shops
- Shops must be settlement-size aware
- Item availability must be resolved probabilistically based on settlement tier
- Buying and selling must affect inventory and gold atomically
- The economy must be tunable through content and settings

### FR-09 Training and Progression
- Heroes progress through battle levels
- Training consumes time and gold
- Progression may modify stats, wounds, luck, and skills
- Skills are drawn from archetype-specific pools
- Duplicate skill results must reroll

### FR-10 Logging and Replay
- Every state-changing action must be logged
- Logs must record random rolls and applied effects
- The game must support deterministic replay for debugging and balancing

### FR-11 Content Administration
- Admin must be able to add and edit:
  - hero archetypes
  - hazards
  - events
  - items
  - shops
  - skills
  - expedition tables
- Admin interface should be available via Django admin initially

## 7. Non-Functional Requirements

### NFR-01 Reliability
- All state-changing actions must execute inside atomic database transactions
- No partial application of an event is acceptable

### NFR-02 Performance
- Normal expedition simulations should complete in under 2 seconds
- Common UI actions should remain responsive on NAS-class hardware

### NFR-03 Portability
- Full application must run under Docker Compose
- No dependency on cloud-only services

### NFR-04 Security
- Support single-user authentication initially
- Use Django authentication and standard security defaults

### NFR-05 Maintainability
- Business logic should live in service modules, not templates or model save hooks
- Content should be data-driven
- Core simulation logic must be testable independently

## 8. Acceptance Criteria

The MVP is acceptable when a player can:
1. Create a campaign
2. Create or recruit a party
3. Run an expedition simulation
4. Travel to a destination and resolve hazards
5. Spend time in settlement using daily actions
6. Trigger and resolve random events
7. Train heroes and manage inventory
8. Save, reload, export, and continue the campaign

## 9. Release Priorities

### MVP
- 4 hero archetypes
- Core expedition simulation
- Travel hazards
- Settlement loop
- Events system
- Shops and progression

### Later
- More archetypes
- Richer special locations
- More event chains
- Modding tools beyond Django admin
- LAN multi-user support
