---
name: novelverse-forge
description: >-
  Transforms user-provided novel text and companion images into an immersive,
  highly interactive worldbuilding showcase webpage. Every design is uniquely
  generated from the novel's "visual genome" — no preset templates. Activated
  when the user mentions "novel worldbuilding", "story universe webpage",
  "fiction world showcase", "小说世界观", "故事宇宙展示", "novelverse",
  "worldbuilding site", "interactive story map", "character relationship graph",
  "fantasy world website", or uploads novel chapters/character art and asks for
  a visual world bible.
---

# Novelverse Forge v4 — Visual Genome Edition

## Overview

Novelverse Forge transforms raw novel drafts and companion artwork into a
polished, single-page interactive world bible. Given a novel excerpt and
optional character/location images, the skill extracts entities, builds a
normalized timeline, **extracts a unique visual genome from the text itself**,
and emits a fully self-contained HTML website with:

- A **hero landing** section with world summary and key art
- An interactive **character / faction / creature / location** gallery
- A draggable, zoomable **timeline** with event cards
- A text-based **relationship web** display
- Full-text **search** with autocomplete and result highlighting
- **Dark / light** mode toggle
- **Responsive** layout (mobile → ultrawide)
- A **design rationale footer** explaining every visual decision

**Core innovation (v4)**: No preset style templates. Every novel gets a
completely unique visual design generated from its own text — colors from
color words in the prose, fonts from the era and mood, textures from scene
descriptions, and motion from emotional atmosphere. The design literally
"grows from the text."

---

## Trigger Conditions

| Trigger Pattern | Examples |
|---|---|
| Explicit skill name | "use novelverse-forge", "run novelverse forge" |
| Worldbuilding request | "build a world bible site for my novel", "make an interactive story universe page" |
| Entity extraction request | "extract all characters from this chapter and visualize them" |
| Timeline request | "create a timeline of events from my novel", "map out the history of this world" |
| Relationship graph request | "show me a relationship map", "graph character connections" |
| Chinese-language equivalents | "帮我做小说世界观展示", "生成故事宇宙网页", "角色关系图" |
| Combined art + text upload | User attaches novel text + character/faction images |

---

## Workflow

### Phase 1 — Ingest & Validate

1. **Collect input** — Identify the novel text (pasted, uploaded `.txt`/`.md`,
   or extracted from an attached document) and any companion images.
2. **Assess completeness** — If any critical section is missing (no text
   provided, no entities detectable), ask the user targeted questions before
   proceeding.
3. **Confirm scope** — Ask whether the user wants the full world bible or a
   specific section (characters only, timeline only, relationship map only).

### Phase 2 — Extract Entities

Execute `scripts/extract_entities.py` (or replicate its logic manually if
Python is unavailable) to produce structured entity JSON.

Refer to `references/extraction_guide.md` for the full extraction schema.

**Output**: `entities[]`, `relationships[]`, `statistics{}`

### Phase 3 — Build Timeline

Execute `scripts/build_timeline.py` to normalize relative time expressions
into an absolute-sequence timeline.

**Output**: `epochs[]`, `events[]`, `character_fates[]`, `contradictions[]`

### Phase 4 — Extract Visual Genome 🆕

Execute `scripts/visual_genome.py` to analyze the novel text and extract
its unique "visual genes" — a complete design scheme generated from nothing
but the text itself.

Refer to `references/design_genome_guide.md` for the complete color lexicon,
texture library, mood→parameter mappings, and font selection algorithm.

**The extraction process:**

| Step | What It Does | Source of Truth |
|---|---|---|
| 4.1 | Scan text for color keywords → generate palette | Color lexicon (200+ words → hex) |
| 4.2 | Scan text for texture/material keywords → select texture type | Texture lexicon (80+ words) |
| 4.3 | Detect era from keywords + entity types → select fonts | Era→font mapping table |
| 4.4 | Detect emotional tone from mood keywords → adjust design params | Mood→parameter mapping table |
| 4.5 | Scan scene descriptions → influence background + decoration | Scene→texture mapping table |
| 4.6 | Detect atmosphere keywords → select motion/animation style | Emotion→motion mapping table |
| 4.7 | Compose final `design.json` with all parameters + rationale | — |

**Output**: Visual design scheme JSON with:
- `color` — 13 hex colors + warmth/saturation/brightness parameters
- `typography` — heading/body/decorative fonts, weights, spacing, scale ratio
- `space` — page padding, card padding, gaps, border radii
- `texture` — type (grain/grid/stars/neon/paper/etc.) + intensity
- `lighting` — type, shadow blur, shadow color
- `motion` — speed, type (pulse/wave/drift/static/rapid), parallax, glow pulse
- `mood` — emotional tone, visual density, era feel
- `generation_rationale` — WHY each color/font/texture was chosen

### Phase 5 — Preview Design 🆕

Execute `scripts/design_preview.py` to generate a visual preview card.

**The preview shows:**
1. Color palette swatches (5-7 color blocks)
2. Typography samples (heading / body / decorative text)
3. Texture effect preview (live CSS rendering)
4. Card component sample (how entity cards will look)
5. Motion effect indicator (dot animation showing the motion type)
6. Design rationale summary (why colors, fonts, textures were chosen)

**Interactive flow:**
1. User uploads novel → Skill analyzes text
2. Skill generates visual design scheme JSON
3. Skill outputs design preview card
4. User can say "确认" to proceed, or give adjustment feedback

### Phase 6 — User Fine-Tuning 🆕

Users can adjust the design using natural language before final generation.

**Supported adjustment commands:**

| User Says | What Changes |
|---|---|
| "色彩再冷一点" / "cooler" | Warmth -0.2, hue shift toward blue |
| "整体亮一些" / "brighter" | Brightness +0.15, lighten backgrounds |
| "字体换更现代的" / "more modern" | Switch to Inter / sans-serif fonts |
| "背景纹理再淡一些" | Texture intensity -0.15 |
| "去掉动效" / "no animation" | Motion type → static, speed → 0 |
| "把主色换成蓝色系" | Primary hue → blue range (~220°) |
| "更简洁一些" | Visual density -0.2, texture -0.15, motion -0.15 |
| "不够史诗，再厚重一点" | Mood → epic, saturation +0.1, weight +200 |
| "更古典" / "classic" | Switch to Playfair Display / serif fonts |

**Adjustment loop:**
1. User provides feedback
2. `visual_genome.py --adjustments` modifies the design JSON
3. `design_preview.py` regenerates the preview
4. Repeat until user is satisfied

### Phase 7 — Generate Final HTML (Multi-Page SPA)

Execute `scripts/generate_html.py` to produce the final website.

**Architecture: Multi-Page SPA with Hash Routing**

The generated page is NOT a single long-scroll document. Instead, it's a
7-page Single Page Application where each functional module lives on its
own page, accessible via the global navigation bar:

| Page | Route | Content |
|---|---|---|
| **总览** Overview | `#overview` | Hero section, world summary, stats, quick-nav circles |
| **时间线** Timeline | `#timeline` | Full-screen interactive timeline with era filters |
| **人物** Characters | `#characters` | Entity gallery grid with type filter tabs |
| **派别** Factions | `#factions` | Faction cards + power structure display |
| **生物** Beings | `#beings` | Creature/being cards with classification filters |
| **关系网** Relations | `#relations` | Full-screen relationship web with legend |
| **互动** Interactive | `#interactive` | Mysteries, whispers, and interactive elements |

**Navigation features:**
- Hash-based routing (`#characters`, `#timeline`, etc.) with browser back/forward
- Smooth page transitions: fade-out + slide-up (200ms out, 400ms in)
- Keyboard shortcuts: ← → to cycle pages, 1–7 to jump directly, Ctrl+K to search
- Hamburger menu on mobile (< 768px) with slide-in panel
- Transition progress bar in the nav during page switches
- Deep linking: open `index.html#relations` to land directly on relations page
- Cross-page search: find any entity from any page, results navigate to the correct page

**The v4 generator:**
1. Reads `assets/templates/page_template.html` as the 7-page layout skeleton
2. Reads the visual design scheme JSON from Phase 4
3. **Dynamically generates ALL CSS** from the design scheme (no theme files!)
4. **Conditionally builds pages** — only pages with content are included
   (e.g., if no creatures extracted, the beings page is omitted)
5. Injects entity data, timeline data, and relationship data as `WORLD_DATA`
6. Inlines all JavaScript modules: navigation (SPA router), interactions,
   timeline, search, and relation graph
7. Generates a "design rationale" footer explaining every visual decision
8. Writes a single self-contained `world_bible.html`

**CSS generation (all inline, no external CSS except Google Fonts):**
- Color CSS variables from design palette
- Typography CSS variables from font selections
- Spacing CSS variables from density parameters
- Texture CSS (SVG filters / gradients) from texture type
- Motion CSS keyframes from motion type and speed
- Component overrides (card glow, hero gradient, scrollbar, etc.)
- Hamburger menu and mobile overlay styles
- Full-screen page layouts for timeline and relations pages

### Phase 8 — Deliver & Iterate

1. Inform the user the file is ready and provide its path.
2. Offer to open it in the default browser.
3. Remind the user of keyboard shortcuts (← → to browse, Ctrl+K to search).
4. The design rationale section in the footer explains every visual decision.

---

## Behavior Rules

### Core Principles

1. **No fabrication** — Every entity MUST be grounded in the provided source
   text. Never invent characters, events, or relationships not present in the
   input.
2. **Transparent reasoning** — When inferring attributes (e.g., a character's
   personality trait from dialogue), cite the source passage. Every design
   decision MUST have a traceable rationale.
3. **Confidence labels** — Every extracted entity and relationship MUST carry a
   confidence label (`high` / `medium` / `low`).
4. **User sovereignty** — The user is the final authority on their world.
   Always allow corrections before final generation.
5. **Design uniqueness** — No two novels should ever receive identical visual
   designs. The visual genome engine guarantees uniqueness through
   content-derived parameters.
6. **Progressive disclosure** — SKILL.md stays under 500 lines. Detailed
   specs live in `references/`.
7. **Graceful degradation** — If Python is unavailable, perform extraction
   manually with the same logic.
8. **Encoding safety** — All text is UTF-8. Special characters are escaped.

### Privacy

- All processing is local. No novel text is sent to any external API.
- Generated HTML files are fully self-contained (no outbound requests except
  Google Fonts CDN for the specific fonts used).

---

## Resource Map

| Resource | Path | When to Load |
|---|---|---|
| Extraction spec | `references/extraction_guide.md` | Phase 2 |
| Design genome guide 🆕 | `references/design_genome_guide.md` | Phase 4 |
| HTML template spec | `references/html_template.md` | Phase 7 |
| Reference index | `references/index.md` | Any phase |
| Entity extractor | `scripts/extract_entities.py` | Phase 2 |
| Timeline builder | `scripts/build_timeline.py` | Phase 3 |
| Visual genome engine 🆕 | `scripts/visual_genome.py` | Phase 4 |
| Design preview generator 🆕 | `scripts/design_preview.py` | Phase 5 |
| HTML generator (v4) | `scripts/generate_html.py` | Phase 7 |
| Base CSS (layout only) | `assets/css/base.css` | Phase 7 |
| Timeline JS | `assets/js/timeline.js` | Phase 7 |
| Search JS | `assets/js/search.js` | Phase 7 |
| Interactions JS | `assets/js/interactions.js` | Phase 7 |
| Navigation JS | `assets/js/navigation.js` | Phase 7 |
| Page template (skeleton) | `assets/templates/page_template.html` | Phase 7 |

All paths relative to the skill root directory.

---

## Usage Examples

### Example 1 — Full World Bible from Chinese Xianxia Novel

**User:** "我写了一本修仙小说，这里是前三章的文本和几张角色设定图，帮我做一个完整的世界观展示页。"

**Skill actions (v4):**
1. Ingest 3 chapters + 5 character images.
2. Run `extract_entities.py` → 12 characters, 4 factions, 3 locations, 8 events.
3. Run `build_timeline.py` → Normalize time expressions.
4. **Run `visual_genome.py`** → Extract "朱红 + 墨色 + 暗金" from text,
   detect "仙侠·古代" era, choose Noto Serif SC, select "水墨" texture,
   detect "史诗感" mood → generate unique design scheme.
5. **Run `design_preview.py`** → Show color palette, font samples, texture.
6. User confirms → "确认，开始生成"
7. Run `generate_html.py` with design scheme → produce `world_bible.html`
   with dynamic ink-wash styling, serif fonts, vermillion-gold palette.
8. Deliver. Footer explains: "从文中反复出现的'朱红''墨色'提取了色彩基调..."

### Example 2 — Sci-Fi Space Opera

**User:** "I finished my space opera novel. Build me a world bible."

**Skill actions (v4):**
1. Ingest novel text.
2. Extract entities (characters, factions spanning galaxies, starship locations).
3. Build timeline across millennia.
4. **Visual genome**: Detects "星舰/太空/银河" → era=future,
   colors from "深蓝/银灰/星白" → cool blue-silver palette,
   texture="stars", mood="史诗感", fonts="Orbitron + Space Grotesk".
5. Preview shows star-field texture, tech fonts, cool palette.
6. User: "再冷一点，更像深空的感觉" → adjustments applied.
7. Generate final HTML with deep-space styling.

### Example 3 — Adjustment Flow

**User:** "色彩太暗了，整体亮一些，字体换更现代的。"

**Skill actions:**
1. `visual_genome.py --adjustments '{"brighter": true, "more_modern": true}'`
2. Design JSON updated: brightness +0.15, fonts → Inter
3. Preview regenerated with lighter background and sans-serif fonts
4. User: "好，就这样" → generate final HTML

---

## Quality Checklist

Before delivering the final HTML, verify:

- [ ] All entities are source-grounded with `source_evidence` populated.
- [ ] Confidence labels are present on every entity and relationship.
- [ ] Timeline contradictions are flagged and shown to the user.
- [ ] **Visual design was previewed and confirmed by the user** (or adjusted).
- [ ] **Design rationale is populated** — every color/font/texture has a "why".
- [ ] The generated HTML renders correctly at 320px, 768px, 1024px, and 1440px.
- [ ] All special characters in entity names are HTML-escaped.
- [ ] Images are base64-inlined (no broken external references).
- [ ] Search returns results across all entity types.
- [ ] Dark mode toggle works and persists (localStorage).
- [ ] The page has `<h1>`, semantic landmarks, and alt text on all images.
- [ ] **Design rationale footer is present** and explains design decisions.
- [ ] **No two generated pages use identical color schemes** (verify for multi-novel sessions).
- [ ] No console errors in a clean browser profile.
