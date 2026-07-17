# Novelverse Forge v4 — Reference Index

Navigation hub for all reference documentation. Load individual files as needed
during the appropriate workflow phase.

---

## Document Map

| Document | Path | Phase | Purpose |
|---|---|---|---|
| **Extraction Guide** | [extraction_guide.md](extraction_guide.md) | Phase 2 | Complete schema for entity extraction — field lists, relation type enums, confidence rubric, common pitfalls. |
| **Design Genome Guide** 🆕 | [design_genome_guide.md](design_genome_guide.md) | Phase 4 | Visual gene extraction reference — 200+ color word→hex mappings, texture lexicon, mood→parameter tables, era→font mappings, scene→texture mappings, emotion→motion mappings, font selection algorithm, color generation algorithm. |
| **Style Mapping** (deprecated) | [style_mapping.md](style_mapping.md) | — | Deprecated in v4. Preserved for reference. Superseded by design_genome_guide.md. |
| **HTML Template Spec** | [html_template.md](html_template.md) | Phase 7 | Page structure requirements, dynamic CSS generation spec, template substitution variables, design rationale footer spec, Google Fonts dynamic loading, responsive breakpoints, accessibility requirements. |

---

## Quick Lookup by Question

| If you need to know… | Go to… |
|---|---|
| What fields should I extract for a character? | [extraction_guide.md](extraction_guide.md) § Character Fields |
| How do I label a master-apprentice relationship? | [extraction_guide.md](extraction_guide.md) § Relation Types |
| What confidence level should this entity have? | [extraction_guide.md](extraction_guide.md) § Confidence Rubric |
| How are colors extracted from the novel text? | [design_genome_guide.md](design_genome_guide.md) § Color Lexicon + § Color Generation Algorithm |
| How are fonts selected based on the story's era? | [design_genome_guide.md](design_genome_guide.md) § Era → Typography Mapping + § Font Selection Algorithm |
| How is the texture chosen? | [design_genome_guide.md](design_genome_guide.md) § Texture Lexicon + § Scene → Texture Mapping |
| How does mood affect the design? | [design_genome_guide.md](design_genome_guide.md) § Mood → Design Parameter Mapping |
| How are animation styles chosen? | [design_genome_guide.md](design_genome_guide.md) § Emotion → Motion Mapping |
| What CSS variables does the template define? | [html_template.md](html_template.md) § Dynamic CSS Generation |
| How is the Google Fonts URL generated? | [html_template.md](html_template.md) § Google Fonts Dynamic Loading |
| What are the responsive breakpoints? | [html_template.md](html_template.md) § Responsive Breakpoints |
| How does the design rationale footer work? | [html_template.md](html_template.md) § Design Rationale Footer |
| What replaced the old preset themes? | [style_mapping.md](style_mapping.md) § Migration Notes |

---

## Resource Dependency Graph (v4)

```
                    ┌──────────────────┐
                    │    SKILL.md       │
                    │ (Core Workflow)   │
                    └──────┬───────────┘
                           │ loads on demand
            ┌──────────────┼──────────────────┐
            ▼              ▼                  ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │ extraction_  │ │ design_genome│ │ html_template│
   │ guide.md     │ │ _guide.md 🆕 │ │ .md          │
   │ (Phase 2)    │ │ (Phase 4)    │ │ (Phase 7)    │
   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
          │                │                │
          ▼                ▼                ▼
   extract_entities  visual_genome.py🆕  generate_html.py (v4)
   .py               design_preview.py🆕 page_template.html
                build_timeline.py         base.css (layout only)
                                          *.js
```

**Key changes from v3:**
- `style_mapping.md` → deprecated, replaced by `design_genome_guide.md`
- `assets/css/themes/*.css` → **deleted** (6 theme files)
- `assets/css/dark.css` → **deleted** (dark mode in base.css)
- `scripts/visual_genome.py` → **new** (visual gene extraction)
- `scripts/design_preview.py` → **new** (design preview)
- `scripts/generate_html.py` → **rewritten** (dynamic CSS generation)

---

## Conventions

- **File paths**: All cross-references use forward slashes and are relative
  to the skill root (`novelverse-forge/`).
- **Section anchors**: Use `§` notation for intra-document references
  (e.g., "see § Character Fields").
- **JSON schemas**: Documented inline using TypeScript-style notation for
  readability. Actual validation is done in the Python scripts.
- **Confidence labels**: Always one of `high`, `medium`, or `low`. Defined in
  detail in the extraction guide.
- **v4 markers**: Files marked with 🆕 are new in v4. Files marked as
  "deprecated" are preserved for reference but no longer used.
