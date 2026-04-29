# Quest Between — Planning Document for GitHub Copilot Planning Agent

## 1. Project Overview

### Name
**Quest Between** (working title)

### Goal
Build a **single-player browser-based campaign game** using **Django + PostgreSQL**, where the player manages a party of heroes between adventures.

This game is inspired by the campaign layer of classic fantasy dungeon-crawl campaign systems, but:
- **NO dungeon crawling or tactical combat**
- **All expeditions are simulated**
- **The gameplay is entirely: travel, events, settlements, training, and decisions**

## 2. Core Game Loop

1. Create and manage a party (1–4 heroes)
2. Configure an expedition (risk + objective)
3. Run an **expedition simulation**
4. Travel to a settlement and resolve hazards
5. Stay in settlement:
   - Perform daily actions per hero
   - Resolve random events
   - Handle shopping, healing, and training
6. Leave settlement and repeat the loop

## 3. Core Constraints (Critical)

These are **non-negotiable rules**:

- No dungeon maps
- No tactical combat system
- No grid, rooms, or turn-based battles
- All combat is abstracted into simulation
- Game outcomes must be deterministic per RNG seed
- Every action must produce a logged event

## 4. Technical Stack

- Backend: **Django**
- Database: **PostgreSQL**
- UI: **Django templates + HTMX** initially
- Deployment: **Docker Compose**, suitable for NAS hosting

## 5. Domain Model (High Level)

### Core Entities
- Campaign
- Party
- Hero
- InventoryItem
- ContentPack
- HazardDef
- SettlementEventDef
- CatastrophicEventDef
- ItemDef
- ShopDef
- SkillDef
- StepLog

## 6. System Architecture

### Pattern
- Django monolith with a clear **service layer**
- Each game action runs inside an **atomic transaction**
- All state changes recorded in **StepLog**

### Key Principle
> The database is the source of truth, and every mutation is logged as a step.

## 7. Core Systems

### 7.1 Expedition Simulation

#### Input
- Party composition
- Hero stats
- Equipment and consumables
- Risk level (Cautious / Standard / Reckless)
- Objective type
- Optional duration / expedition profile

#### Output
- Gold earned
- Loot found
- Injuries and conditions
- Consumables used
- Deaths
- Progression gains

#### Requirements
- Deterministic from seed
- Produces both:
  - a summary narrative
  - structured result data

### 7.2 Travel System

#### Rules
Player selects destination:
- Village (2 hazards)
- Town (4 hazards)
- City (6 hazards)

#### Behaviour
- Hazards apply to the entire party
- Hazards can:
  - cause loss or injury
  - add travel time and trigger extra hazards
  - force early arrival or other route changes

### 7.3 Settlement System

#### Structure
- Time is tracked in **days and weeks**
- Each hero performs **1 action per day**

#### Actions
- Buy items
- Sell items
- Train
- Visit special location
- Rest
- Heal or recover

### 7.4 Events

#### Settlement Events
- Triggered after each hero action
- Affect an individual hero

#### Catastrophic Events
- Triggered weekly after week 2
- Affect the entire party
- May:
  - force departure
  - alter the economy
  - cause major consequences

### 7.5 Shops and Economy

#### Availability
- Based on settlement size:
  - Village → 1D6
  - Town → 2D6
  - City → 3D6

#### Behaviour
- Roll must meet or exceed item stock value
- Supports buy and sell flows
- Economy should remain data-driven and tunable

### 7.6 Training and Progression

- Heroes have battle levels
- Training costs gold and time
- On level-up:
  - stats improve
  - skills may be gained
- Skills:
  - rolled from archetype-specific tables
  - duplicates must reroll

## 8. Data-Driven Content System

All content must be configurable via database first, and later exportable or importable as JSON:

- Hazards
- Settlement events
- Catastrophic events
- Shops
- Items
- Skills
- Expedition tables

### Requirement
> No hardcoded content in the logic layer.

## 9. Event Logging System (Critical)

### StepLog Model
Each action must record:
- Step type
- Actor (hero or party)
- RNG seed used
- Dice rolled
- Effects applied
- Timestamp

### Purpose
- Debugging
- Replay
- Deterministic behaviour
- Auditing state mutations

## 10. RNG System

- Seed derived from:
  - campaign seed
  - step id
  - action type
  - actor identity where needed

### Requirement
> The same inputs must always produce the same outputs.

## 11. UI Requirements

### Screens
- Campaign dashboard
- Party management
- Expedition setup
- Expedition report
- Travel hazard resolution
- Settlement hub
- Event resolution
- Hero sheet
- Content administration via Django admin

### UX Principles
- Event-driven presentation using cards and logs
- Consequences shown clearly
- Minimal clicks per action
- State changes must be visible and understandable

## 12. Non-Functional Requirements

- Atomic database transactions for all actions
- Autosave after every step
- Fast response time, typically less than 2 seconds per simulation
- Works offline on local network
- Simple single-user authentication initially
- Testable core logic

## 13. MVP Scope

### Include
- 4 hero archetypes
- Expedition simulation
- Travel hazards
- Settlement system
- Events system
- Training system
- Shops and inventory

### Exclude
- Multiplayer
- Tactical combat
- Animation-heavy UI
- External integrations

## 14. Implementation Phases

### Phase 1 – Foundation
- Django project setup
- App structure
- PostgreSQL integration
- Core models
- Django admin setup

### Phase 2 – Core Engine
- StepLog system
- RNG system
- Expedition simulation service

### Phase 3 – Travel and Settlement
- Hazard system
- Settlement loop
- Event system

### Phase 4 – Economy and Progression
- Shops
- Inventory
- Training
- Skills

### Phase 5 – UI
- Core templates
- Navigation
- Event cards
- Dashboard screens

## 15. Definition of Done

The first playable slice is complete when the player can:
- Create a party
- Run an expedition
- Travel with hazards
- Stay in settlement with events
- Train and shop
- Repeat the loop indefinitely

## 16. Instructions for Copilot Agent

- Do not introduce dungeon systems
- Do not add real-time or tactical combat
- Keep logic deterministic
- Prefer clarity over cleverness
- Use Django best practices: models, services, transactions
- Keep content data-driven
- Write tests for simulation and state mutation logic
