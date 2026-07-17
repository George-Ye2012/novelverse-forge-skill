# Style Mapping Reference (DEPRECATED in v4)

> **⚠️ This document is deprecated as of Novelverse Forge v4.**
>
> In v3, this file contained preset style templates (wuxia, gothic, cyberpunk,
> space, lovecraft, steampunk) with fixed color palettes, font recommendations,
> and design elements. The skill selected from these 6 templates based on
> keyword matching.
>
> **v4 replaces this entirely** with the Visual Genome Engine — every novel
> gets a unique design generated from its own text, not selected from a fixed
> list.
>
> **See instead:**
> - [`design_genome_guide.md`](design_genome_guide.md) — Complete reference for
>   the visual gene extraction system (color lexicon, texture library, mood
>   mappings, era→font mappings, scene→texture mappings, etc.)
> - [`scripts/visual_genome.py`](../scripts/visual_genome.py) — The visual
>   genome extraction engine
> - [`SKILL.md`](../SKILL.md) § Phase 4 — Visual genome extraction workflow

---

## Why the Change?

### Problem with Preset Templates
Even 12 styles are essentially "skin-swapping" — picking from a fixed list
means every novel falls into one of a few visual paradigms. Two completely
different cyberpunk novels would get nearly identical designs.

### Solution: Visual Genome
The visual genome engine extracts design parameters **directly from the
novel's text**:
- Colors come from color words IN the prose (not a preset palette)
- Fonts come from the era and mood OF the specific story
- Textures come from scene descriptions IN the text
- Motion comes from emotional atmosphere OF the narrative

**Result**: Every novel gets a design that is truly its own — no two novels
will ever get the same color scheme, font combination, or texture treatment.

### Preserved Design Knowledge
The design knowledge from the old 6 themes has been generalized into the
design genome guide's mapping tables:
- Color palettes → Color Lexicon (200+ words → hex values)
- Font recommendations → Era→Font Mapping (8+ era categories)
- Texture choices → Texture Lexicon + Scene→Texture Mapping
- Animation styles → Emotion→Motion Mapping

---

## Migration Notes

| v3 Concept | v4 Equivalent |
|---|---|
| `style_mapping.md` § Wuxia | `design_genome_guide.md` § Color Lexicon + Era→Font (xianxia) + Scene→Texture (rivers_and_lakes) |
| `style_mapping.md` § Gothic | `design_genome_guide.md` § Color Lexicon + Era→Font (fantasy) + Scene→Texture (castle) |
| `style_mapping.md` § Cyberpunk | `design_genome_guide.md` § Color Lexicon + Era→Font (future) + Scene→Texture (future_city) |
| `style_mapping.md` § Space | `design_genome_guide.md` § Color Lexicon + Era→Font (future) + Scene→Texture (starship) |
| `style_mapping.md` § Lovecraft | `design_genome_guide.md` § Color Lexicon + Mood→Params (uncanny) + Texture Lexicon (shadow) |
| `style_mapping.md` § Steampunk | `design_genome_guide.md` § Color Lexicon + Era→Font (steampunk) + Scene→Texture (factory) |
| `style_mapping.md` § Mixed-Style Fusion | Obsolete — the genome engine natively blends influences |
| `style_mapping.md` § Style Inference Algorithm | Replaced by `visual_genome.py` → `detect_mood()` + `select_typography()` + `generate_palette()` |

### Deleted Files (v4)
- `assets/css/themes/wuxia.css`
- `assets/css/themes/gothic.css`
- `assets/css/themes/cyberpunk.css`
- `assets/css/themes/space.css`
- `assets/css/themes/lovecraft.css`
- `assets/css/themes/steampunk.css`
- `assets/css/dark.css`

### New Files (v4)
- `scripts/visual_genome.py` — Visual genome extraction engine
- `scripts/design_preview.py` — Design preview card generator
- `references/design_genome_guide.md` — Complete design gene reference
