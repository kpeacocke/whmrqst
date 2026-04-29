# Copilot implementation brief

Implement the initial UI and interaction system for this project according to the existing `planning.md`, `requirements.md`, `design.md`, and `.github/copilot-instructions.md`.

## Objective

Build the first production-ready UI foundation for a **text-first, premium-looking browser game** in **Django + PostgreSQL**, using **Django templates + HTMX + CSS + minimal JavaScript**.

This is **not** a graphical game. It is a **text-based campaign game** with a luxurious, dark, elegant interface.

The UI must feel:
- premium
- restrained
- dark fantasy
- text-led
- highly readable
- beautiful without using illustrations

Do not use React, Vue, or other frontend SPA frameworks for this phase.

---

## Critical constraints

These are mandatory:

- No dungeon maps
- No tactical combat UI
- No image-heavy layout
- No bright arcade styling
- No cartoonish animations
- No Bootstrap-looking admin-panel UI
- No hardcoded game content in templates or business logic
- All content and state should remain compatible with a data-driven backend

This game should feel like:
- a luxury fantasy ledger
- an elegant strategy interface
- a beautifully typeset RPG chronicle

It should **not** feel like:
- a terminal app
- a default Django admin skin
- a generic bootstrap dashboard
- a mobile gacha game
- a JRPG combat UI

---

## Tech requirements

Use:
- Django templates
- HTMX
- plain CSS or a well-structured CSS system
- minimal JavaScript only where needed for timing / transitions

Do not introduce a heavy frontend build pipeline unless absolutely required.

---

## UI direction

Create a reusable UI system with these qualities:

### Visual style
- Dark mode by default
- Rich charcoal / near-black backgrounds
- Off-white / warm parchment text
- Muted metallic gold accents
- Restrained crimson for negative states
- Muted green or sage for positive states
- Excellent typography and spacing
- Strong hierarchy for titles, narrative text, hero data, and impacts

### Layout philosophy
Use a three-column layout where appropriate:

- Left: party / hero state
- Centre: current narrative event / main interaction
- Right: chronicle / recent log / contextual information

Everything should feel structured through cards and panels, not images.

### Core screens to implement first
Implement templates and styling for:

1. Campaign / dashboard shell
2. Party panel
3. Main event card
4. Choice list / action list
5. Chronicle / timeline panel
6. Generic settlement screen shell
7. Generic expedition report shell
8. Hero detail card or hero sheet panel

These should be reusable partials/components in Django template terms.

---

## Motion and feedback system

Implement a restrained “luxury feedback system” for event outcomes.

### Impact categories
Create a reusable impact model in the UI layer for:

- positive
- neutral
- cost
- negative
- catastrophic

### Behaviour
- Positive: soft fade + slight rise
- Neutral: simple fade
- Cost: soft reveal with muted gold styling
- Negative: short, sharp horizontal tremor
- Catastrophic: one stronger jolt, then stillness

### Important rules
- Motion must communicate consequence, not decoration
- No bouncy animation
- No excessive shaking
- No flashy glow spam
- No neon colours
- Keep animation short, elegant, and expensive-feeling

### Pacing
Do not dump all effects instantly.
Support the UI pattern:
1. show narrative
2. small delay
3. reveal impacts one by one
4. then show available choices

Implement this in a simple, maintainable way.

---

## Design tokens / theme system

Create a reusable theme system for:
- colours
- spacing
- border radius
- shadows
- typography scale
- panel/card styles
- impact styles

Use CSS custom properties if appropriate.

At minimum, define tokens for:
- background
- surface
- elevated surface
- primary text
- secondary text
- accent gold
- positive
- warning/cost
- negative
- catastrophic

The visual result must be cohesive and premium.

---

## Accessibility and readability

Even though this is a dark fantasy interface, it must remain highly readable.

Requirements:
- excellent contrast
- readable font sizes
- generous spacing
- clear focus states
- keyboard-usable interactions
- semantic HTML

---

## Deliverables

Implement the following in the codebase:

### Templates / partials
- base layout
- dashboard layout
- party panel partial
- event card partial
- impact pill partial
- choice/action partial
- chronicle panel partial
- settlement shell
- expedition report shell

### Styling
- global theme stylesheet
- reusable card/panel system
- reusable impact styles
- animation styles for impacts and content reveal
- typography and layout system

### Minimal behaviour
- simple progressive reveal system for event narrative, impacts, and choices
- HTMX-friendly partial swaps
- hooks/classes that can later connect to backend event data

---

## Implementation quality requirements

- Keep templates clean and modular
- Keep styling consistent and reusable
- Avoid one-off inline styles
- Avoid duplicated markup patterns
- Prefer reusable partials/includes
- Use clear naming
- Write code that is easy to extend for later game systems

---

## Do not do these things

- Do not invent gameplay systems outside the planning/design docs
- Do not add dungeon visuals or combat widgets
- Do not add placeholder fantasy artwork
- Do not make it look like a generic admin system
- Do not over-engineer the frontend
- Do not hardcode narrative content as the long-term solution

---

## What to optimise for

Optimise for:
- atmosphere
- clarity
- elegance
- maintainability
- text-first immersion

The result should make a player think:
“this looks beautiful, serious, and dangerous,”
even though it is primarily text and structured data.

---

## Suggested implementation order

1. Create base theme tokens and layout system
2. Build reusable panel/card components in template form
3. Build event card and impact system
4. Build chronicle panel
5. Build party panel and hero cards
6. Add progressive reveal and impact animations
7. Build settlement and expedition report shells
8. Refine polish, spacing, and consistency

---

## Final instruction

Favour restraint over spectacle.

If unsure between two options, choose the one that is:
- simpler
- darker
- cleaner
- more typographically elegant
- less flashy
