# Entity Extraction Guide

Detailed specification for extracting structured world data from novel text.

---

## Table of Contents

1. [Entity Type Taxonomy](#entity-type-taxonomy)
2. [Character Fields](#character-fields)
3. [Faction Fields](#faction-fields)
4. [Location Fields](#location-fields)
5. [Creature Fields](#creature-fields)
6. [Event Fields](#event-fields)
7. [Item Fields](#item-fields)
8. [Relation Type Enumeration](#relation-type-enumeration)
9. [Confidence Rubric](#confidence-rubric)
10. [Timeline Extraction](#timeline-extraction)
11. [Common Pitfalls](#common-pitfalls)

---

## Entity Type Taxonomy

Every extracted entity MUST be assigned exactly one of the following types:

| Type | Code | Icon | Definition |
|---|---|---|---|
| `character` | char | 👤 | A sentient being with agency in the story. Includes humans, humanoids, gods, spirits with personality. |
| `faction` | fact | 🏛️ | An organized group of characters (sect, kingdom, guild, clan, tribe, cult, alliance). |
| `location` | loc | 📍 | A named place of narrative significance (city, realm, dungeon, mountain, planet). |
| `creature` | crea | 🐉 | A non-sentient or bestial entity (monster, beast, dragon, spirit beast). If sentient and a named character, classify as `character` instead. |
| `event` | evnt | 📜 | A significant historical or plot event (war, ceremony, discovery, catastrophe). |
| `item` | item | ⚔️ | A named object of significance (artifact, weapon, relic, treasure). |

**Edge cases:**

- A dragon with a name, personality, and dialogue → `character`
- A generic dragon species description → `creature`
- "The Dark Forest" as a place → `location`
- "The Dark Forest" as a faction of forest-dwellers → `faction`
- A sword that talks and has agency → `character` (or `item` with `sentient: true`; note the ambiguity)

---

## Character Fields

```typescript
interface CharacterEntity {
  id: string;                    // e.g. "char_001"
  name: string;                  // Primary name used in text
  aliases: string[];             // Titles, nicknames, pseudonyms
  type: "character";
  attributes: {
    full_name: string;           // Full formal name if different
    aliases: string[];           // Duplicated at top level for search
    age: number | null;          // Approximate or exact
    gender: string;              // "male" | "female" | "non-binary" | "unknown" | ""
    species: string;             // "human" | "elf" | "dragon" | "cultivator" | etc.
    appearance: string;          // Physical description from text
    personality: string;         // Personality traits from text
    abilities: string[];         // Powers, skills, techniques
    affiliation: string;         // Primary faction ID or name
    rank: string;                // Position within affiliation
    status: "alive" | "deceased" | "unknown";  // At story start
    first_appearance: string;    // Chapter/paragraph reference
    narrative_role: string;      // "protagonist" | "antagonist" | "supporting" | "cameo"
  };
}
```

### Extraction Heuristics

| Field | How to Extract |
|---|---|
| `age` | Look for explicit statements ("twenty years old", "三百岁"). If only implied by context (e.g., "young disciple"), leave null and note in `source_evidence`. |
| `personality` | Derive from character actions and dialogue tags. Quote the text: "他面无表情地说" → reserved/cold. |
| `abilities` | Extract named techniques, spells, or skills. In xianxia: 功法, 武技, 神通 names. |
| `rank` | Cultivation realms (筑基, 金丹, 元婴), military ranks, or social titles. |
| `status` | Default to "alive" unless death is explicitly stated. If a character is "presumed dead" or "vanished", use "unknown" with a note. |

---

## Faction Fields

```typescript
interface FactionEntity {
  id: string;
  name: string;
  aliases: string[];
  type: "faction";
  attributes: {
    full_name: string;
    aliases: string[];
    type: string;          // "sect" | "kingdom" | "guild" | "clan" | "cult" | "empire" | "academy" | "tribe" | "alliance" | "family"
    leader: string;        // Character ID or name of leader
    members_count: number | null;
    territory: string;     // Location ID or name of home base
    philosophy: string;    // Mission, creed, or governing principle
    alignment: string;     // "good" | "evil" | "neutral" | "lawful" | "chaotic"
    status: "active" | "destroyed" | "declining" | "rising" | "unknown";
    symbol: string;        // Description of emblem, flag, or sigil
  };
}
```

### Alignment Mapping

Map textual cues to standard alignment:

| Text Cues | Alignment |
|---|---|
| "正义", "正道", "righteous", "holy", "protect the weak" | `good` |
| "邪", "魔道", "evil", "dark", "corrupt" | `evil` |
| "中立", "neutral", "balanced", "mercenary" | `neutral` |
| "秩序", "rules", "code", "lawful" | `lawful` |
| "混乱", "chaos", "freedom", "rebellious" | `chaotic` |

---

## Location Fields

```typescript
interface LocationEntity {
  id: string;
  name: string;
  aliases: string[];
  type: "location";
  attributes: {
    full_name: string;
    aliases: string[];
    type: string;          // "city" | "realm" | "continent" | "dungeon" | "mountain" | "sea" | "forest" | "planet" | "dimension" | "academy" | "temple"
    parent_location: string; // Containing location ID/name
    climate: string;
    population: number | null;
    description: string;    // Physical description
    significance: string;   // Why this place matters
    controlled_by: string;  // Faction ID that controls it
  };
}
```

---

## Creature Fields

```typescript
interface CreatureEntity {
  id: string;
  name: string;
  aliases: string[];
  type: "creature";
  attributes: {
    full_name: string;
    aliases: string[];
    species: string;
    habitat: string;        // Location ID or biome description
    abilities: string[];
    danger_level: "low" | "medium" | "high" | "legendary";
    description: string;    // Physical and behavioral description
    is_sentient: boolean;   // True if the species is intelligent
  };
}
```

---

## Event Fields

```typescript
interface EventEntity {
  id: string;
  name: string;
  aliases: string[];
  type: "event";
  attributes: {
    full_name: string;
    aliases: string[];
    date: string;           // Raw temporal expression from text
    location: string;       // Location ID where it occurred
    participants: string[]; // Character/Faction IDs involved
    outcome: string;        // What resulted from this event
    significance: string;   // Why this event matters
    era: string;            // Which era it belongs to
    predecessor: string;    // Event ID that directly preceded it
    successor: string;      // Event ID that directly followed it
  };
}
```

---

## Item Fields

```typescript
interface ItemEntity {
  id: string;
  name: string;
  aliases: string[];
  type: "item";
  attributes: {
    full_name: string;
    aliases: string[];
    type: string;           // "weapon" | "artifact" | "tool" | "treasure" | "consumable" | "vehicle" | "document"
    owner: string;          // Character ID of current owner
    abilities: string[];
    description: string;
    origin: string;         // How/where it was created
    significance: string;
  };
}
```

---

## Relation Type Enumeration

Standardized relationship types for the `relationships` array:

| Type | Code | Description | Example Cues (CN / EN) |
|---|---|---|---|
| `sibling` | sib | Blood siblings | 兄弟, 姐妹 / brother, sister |
| `parent_child` | pc | Parent-offspring | 父子, 母女 / father of, son of |
| `master_apprentice` | ma | Teacher-student bond | 师徒 / master, disciple, apprentice |
| `romantic` | rom | Romantic or marital bond | 道侣, 夫妻 / lover, wife, husband |
| `enmity` | enm | Hatred, rivalry, sworn enemies | 仇人, 死敌 / enemy, nemesis, rival |
| `ally` | aly | Alliance or friendship | 盟友, 好友 / ally, friend, comrade |
| `allegiance` | alg | One-sided loyalty or service | 效忠, 下属 / sworn to, serves, vassal |
| `blood_bond` | bb | Clan, tribe, or magical blood link | 血亲, 族人 / blood of, clan of |
| `mentor` | men | One-directional guidance (≠ formal master) | 引路人 / mentor, guide |
| `creator_creation` | cc | Artificial being or created object | 创造, 炼制 / created, forged, built |
| `possessor_possessed` | pp | Ownership of an item | 持有 / wields, owns, carries |

**Directionality note**: Some relations are symmetric (`sibling`, `ally`, `romantic`, `enmity`),
others are directional (`parent_child`, `master_apprentice`, `allegiance`). For directional
relations, `source` is the "senior" or "dominant" end, `target` is the "junior" or
"subordinate" end.

---

## Confidence Rubric

Every entity and relationship MUST carry a confidence label:

| Label | Criteria | Visual Treatment |
|---|---|---|
| **high** | Name explicitly stated 3+ times; type confirmed by context; attributes directly described in text. | Solid border, full opacity. |
| **medium** | Name stated 1–2 times; type inferred from context clues; attributes partially implied. | Normal border, 90% opacity. |
| **low** | Name mentioned once in passing; type guessed; attributes inferred or absent. Attempt to extract anyway — even tentative data is useful, and the user can correct it later. | Dashed border, "tentative" badge, 80% opacity. |

### Confidence Scoring Heuristics

```
HIGH confidence when:
  - Entity has 3+ separate mentions across different paragraphs/chapters
  - Entity type is stated explicitly in the text
  - At least 3 attributes are directly extractable from text

MEDIUM confidence when:
  - Entity has 1-2 mentions
  - Entity type is strongly implied by context
  - 1-2 attributes directly extractable

LOW confidence when:
  - Single passing mention
  - Entity type is a best-guess based on naming patterns
  - No attributes directly extractable (all blank or inferred)
```

---

## Timeline Extraction

### Relative Time Resolution Algorithm

When the text contains relative time expressions, resolve them as follows:

1. **Identify anchor events** — Events with explicit temporal markers (e.g.,
   "Year 734 of the Empire", "2024-03-15").

2. **Chain relative events** — For events referenced relative to an anchor
   ("three years after the war"), compute the offset from the anchor.

3. **Resolve conflicts** — If two passages give different intervals for the
   same pair of events (Chapter 3: "200 years ago" vs Chapter 7: "150 years
   ago"), flag both values in the `contradictions` array and use the
   **earliest narrative mention** as the primary value (the author may have
   revised their timeline).

4. **Qualitative expressions** — Map fuzzy expressions to approximate values:

| Expression (CN) | Expression (EN) | Approx. Years |
|---|---|---|
| 不久 / 片刻 | soon / a moment | 0.01 |
| 几年 / 数年 | a few years | 3 |
| 多年 / 许久 | many years | 30 |
| 数百年 | centuries | 300 |
| 千年 / 万载 | millennia / eons | 1000 |
| 太古 / 远古 | ancient times / primordial | 10,000 |
| 创世之初 | dawn of creation | 1,000,000 |

### Character Fate Lines

For each character, collect all events they participate in and sort by
sequence order. This forms their "fate line" — a thread through the timeline
showing the character's journey.

---

## Common Pitfalls

### 1. Over-Extracting Generic Nouns

**Problem**: Treating every named object as an entity.
**Fix**: Require narrative significance. "A bronze sword" is not an item entity;
"The Sword of Seven Sorrows, passed down through twelve generations" is.

### 2. Confusing Epithets with Aliases

**Problem**: "The boy" is a narrative reference, not a character alias.
**Fix**: Only add descriptive epithets as aliases if they are used as a
substitute for the character's name by other characters ("The Sword Shadow"
is an alias; "the young cultivator" is not).

### 3. Duplicate Entities from Name Variants

**Problem**: "Yan Chen" and "Old Ghost Yan" extracted as two separate characters.
**Fix**: After extraction, run an alias-matching pass. If one entity's name is
a substring of another's alias (or vice versa), flag for merge.

### 4. Missing Implicit Relationships

**Problem**: Two characters are described as "growing up together" but no
explicit "兄弟" / "brother" cue exists.
**Fix**: In Phase 2 Step 4 (relationship extraction), also scan for co-occurrence
patterns: characters who appear in the same paragraphs across multiple chapters
likely have a significant relationship. Flag these as `confidence: low` for
user confirmation.

### 5. Timeline Over-Confidence

**Problem**: Treating sequence order (appearance in text) as chronological order.
**Fix**: Always distinguish between narrative order and chronological order.
A flashback event appearing in Chapter 10 may chronologically be the first
event. Use the `relative_offset_years` field to encode the actual temporal
position, not the chapter number.

### 6. Mixed-Language Text Confusion

**Problem**: A Chinese novel that uses English names for certain factions
(e.g., "The Order", "Nova Empire").
**Fix**: Run both CN and EN extraction patterns on every text. Use the
`detect_language()` heuristic per-paragraph, not per-document.
