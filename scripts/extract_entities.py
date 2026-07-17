#!/usr/bin/env python3
"""
extract_entities.py — Named Entity Extractor for Novelverse Forge
=================================================================
Extracts characters, factions, locations, creatures, events, and items from
novel text using a hybrid approach: spaCy for general NER + regex patterns
for genre-specific entities + heuristic rules for relationship detection.

Input:
    Novel text as a UTF-8 string (piped via stdin, or passed as --input FILE).

Output:
    Structured JSON to stdout with the following top-level schema:

    {
      "entities": [
        {
          "id": "char_001",
          "name": "Yan Chen",
          "aliases": ["Old Ghost", "The Sword Shadow"],
          "type": "character",
          "attributes": { ... type-specific fields ... },
          "mentions": [
            {"chapter": 1, "paragraph": 3, "context": "..."}
          ],
          "confidence": "high",
          "source_evidence": ["Chapter 1, para 3: 'Yan Chen drew his blade...'"]
        }
      ],
      "relationships": [
        {
          "source": "char_001",
          "target": "char_002",
          "relation_type": "enmity",
          "evidence": "...",
          "confidence": "medium"
        }
      ],
      "statistics": {
        "total_entities": 42,
        "by_type": {"character": 15, "faction": 4, ...},
        "low_confidence_count": 3
      }
    }

Dependencies:
    - Python 3.9+
    - spaCy with a Chinese or English model (auto-detected)
    - (optional) jieba for Chinese word segmentation fallback

Usage:
    python extract_entities.py --input novel_ch1.txt --lang zh > entities.json
    python extract_entities.py --input story.txt --output entities.json
    cat chapter*.txt | python extract_entities.py > entities.json
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Try importing NLP libraries; degrade gracefully if unavailable.
# ---------------------------------------------------------------------------
try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print(
        "[WARN] spaCy not installed. Falling back to regex-only extraction. "
        "Install with: pip install spacy",
        file=sys.stderr,
    )

try:
    import jieba

    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False


# ============================================================================
# Configuration & Constants
# ============================================================================

# Character title/suffix patterns (Chinese xianxia/wuxia)
CN_HONORIFICS = [
    "尊者",
    "真人",
    "仙子",
    "魔尊",
    "剑仙",
    "天尊",
    "大帝",
    "老祖",
    "圣主",
    "神王",
    "仙帝",
    "魔帝",
    "妖皇",
    "宫主",
    "掌门",
    "长老",
    "师兄",
    "师姐",
    "师弟",
    "师妹",
    "师父",
    "徒弟",
]

# English fantasy title patterns
EN_HONORIFICS = [
    "Lord",
    "Lady",
    "Sir",
    "Dame",
    "King",
    "Queen",
    "Prince",
    "Princess",
    "Emperor",
    "Empress",
    "Duke",
    "Duchess",
    "Baron",
    "Count",
    "Archmage",
    "Grandmaster",
    "Elder",
    "Master",
    "Apprentice",
]

# Faction/group indicator keywords
FACTION_INDICATORS_CN = [
    "宗",
    "派",
    "门",
    "阁",
    "殿",
    "宫",
    "盟",
    "会",
    "族",
    "国",
    "教",
    "帮",
    "谷",
    "山",
    "楼",
    "寺",
    "学院",
    "世家",
]

FACTION_INDICATORS_EN = [
    "clan",
    "guild",
    "order",
    "faction",
    "kingdom",
    "empire",
    "tribe",
    "cult",
    "academy",
    "house",
    "alliance",
    "legion",
    "covenant",
    "dynasty",
    "syndicate",
    "council",
    "brotherhood",
    "sisterhood",
]

# Location indicator keywords
LOCATION_INDICATORS_CN = [
    "城",
    "镇",
    "村",
    "山",
    "海",
    "谷",
    "林",
    "域",
    "界",
    "境",
    "大陆",
    "岛",
    "沙漠",
    "平原",
    "洞府",
    "秘境",
]

LOCATION_INDICATORS_EN = [
    "city",
    "town",
    "village",
    "mountain",
    "sea",
    "forest",
    "valley",
    "kingdom",
    "realm",
    "continent",
    "island",
    "desert",
    "plain",
    "dungeon",
    "tower",
]

# Relationship cue phrases → relation types
RELATION_CUES_CN = {
    "兄弟": "sibling",
    "姐妹": "sibling",
    "兄妹": "sibling",
    "父子": "parent_child",
    "母女": "parent_child",
    "师徒": "master_apprentice",
    "道侣": "romantic",
    "恋人": "romantic",
    "夫妻": "romantic",
    "仇人": "enmity",
    "死敌": "enmity",
    "宿敌": "enmity",
    "盟友": "ally",
    "同盟": "ally",
    "效忠": "allegiance",
    "臣服": "allegiance",
    "下属": "allegiance",
    "血亲": "blood_bond",
    "族人": "blood_bond",
}

RELATION_CUES_EN = {
    "brother": "sibling",
    "sister": "sibling",
    "father": "parent_child",
    "mother": "parent_child",
    "son of": "parent_child",
    "daughter of": "parent_child",
    "master": "master_apprentice",
    "apprentice": "master_apprentice",
    "disciple": "master_apprentice",
    "lover": "romantic",
    "wife": "romantic",
    "husband": "romantic",
    "enemy": "enmity",
    "nemesis": "enmity",
    "rival": "enmity",
    "ally": "ally",
    "allied": "ally",
    "sworn to": "allegiance",
    "serves": "allegiance",
    "blood": "blood_bond",
    "clan": "blood_bond",
}

# Entity type icon mapping (for frontend use)
ENTITY_TYPE_ICONS = {
    "character": "👤",
    "faction": "🏛️",
    "location": "📍",
    "creature": "🐉",
    "event": "📜",
    "item": "⚔️",
}


# ============================================================================
# Helper Functions
# ============================================================================


def detect_language(text: str) -> str:
    """Heuristic language detection based on CJK character ratio."""
    cjk_count = sum(1 for ch in text if "一" <= ch <= "鿿")
    total_chars = len(re.sub(r"\s", "", text))
    if total_chars == 0:
        return "en"
    return "zh" if (cjk_count / max(total_chars, 1)) > 0.15 else "en"


def chunk_text(text: str, chunk_size: int = 2000) -> list[dict]:
    """
    Split text into chapter/paragraph chunks for mention tracking.
    Attempts to detect chapter boundaries via common patterns.
    """
    chapters: list[dict] = []

    # Try splitting by chapter markers
    chapter_pattern = re.compile(
        r"(?:^|\n)\s*(?:第[一二三四五六七八九十百千万\d]+[章节回]|Chapter\s+\d+|[Cc][Hh]\b.*\d)",
        re.MULTILINE,
    )
    splits = chapter_pattern.split(text)
    markers = chapter_pattern.findall(text)

    if len(markers) >= 1 and len(splits) >= 2:
        chapter_num = 0
        for i, block in enumerate(splits):
            if i < len(markers):
                chapter_num = i + 1
            paragraphs = [p.strip() for p in block.split("\n\n") if p.strip()]
            for para_idx, para in enumerate(paragraphs):
                chapters.append(
                    {"chapter": chapter_num, "paragraph": para_idx + 1, "text": para}
                )
    else:
        # Fallback: treat the whole text as one chapter
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for para_idx, para in enumerate(paragraphs):
            chapters.append({"chapter": 1, "paragraph": para_idx + 1, "text": para})

    return chapters


def generate_id(entity_type: str, counter: int) -> str:
    """Generate a stable entity ID like 'char_001'."""
    prefix_map = {
        "character": "char",
        "faction": "fact",
        "location": "loc",
        "creature": "crea",
        "event": "evnt",
        "item": "item",
    }
    prefix = prefix_map.get(entity_type, "unk")
    return f"{prefix}_{counter:03d}"


def extract_capitalized_names(text: str) -> list[str]:
    """Extract capitalized proper name sequences (English)."""
    pattern = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b")
    matches = pattern.findall(text)
    # Filter out sentence-start words
    return [m for m in matches if m not in {"The", "A", "An", "It", "He", "She", "They"}]


def extract_cn_names(text: str) -> list[tuple[str, int]]:
    """
    Extract potential Chinese names (2-4 characters) with position.
    Uses jieba if available, otherwise a character-gram approach.
    """
    candidates: list[tuple[str, int]] = []

    if JIEBA_AVAILABLE:
        words = list(jieba.tokenize(text))
        for word, start, end in words:
            w = word.strip()
            if 2 <= len(w) <= 4 and all("一" <= ch <= "鿿" for ch in w):
                # Check if followed by an honorific
                candidates.append((w, start))
    else:
        # Fallback: find sequences of 2-4 CJK characters near honorifics
        for honorific in CN_HONORIFICS:
            for m in re.finditer(
                rf"([一-鿿]{{2,4}}){re.escape(honorific)}", text
            ):
                candidates.append((m.group(1), m.start()))

    return candidates


def classify_entity(
    name: str, context: str, lang: str
) -> tuple[str, float]:
    """
    Classify an entity name into a type based on context keywords.
    Returns (type, confidence_score).
    """
    scores: dict[str, float] = defaultdict(float)

    # Check faction indicators
    faction_indicators = (
        FACTION_INDICATORS_CN if lang == "zh" else FACTION_INDICATORS_EN
    )
    for ind in faction_indicators:
        if ind in name:
            scores["faction"] += 3.0
        if ind in context:
            scores["faction"] += 1.0

    # Check location indicators
    loc_indicators = LOCATION_INDICATORS_CN if lang == "zh" else LOCATION_INDICATORS_EN
    for ind in loc_indicators:
        if ind in name:
            scores["location"] += 3.0
        if ind in context:
            scores["location"] += 1.0

    # Check for creature/bestial keywords
    creature_keywords = ["兽", "妖", "魔", "怪", "灵", "dragon", "beast", "demon",
                         "spirit", "monster", "creature", "wyrm", "leviathan"]
    for kw in creature_keywords:
        if kw in name:
            scores["creature"] += 2.0

    # Check for event keywords
    event_keywords = ["大战", "之役", "之变", "大会", "劫", "war", "battle",
                      "conference", "cataclysm", "reckoning", "festival", "ceremony"]
    for kw in event_keywords:
        if kw in name:
            scores["event"] += 2.0

    # Default: character
    scores["character"] += 1.0

    best_type = max(scores, key=lambda k: scores[k])
    best_score = scores[best_type]
    total = sum(scores.values()) or 1
    confidence = min(best_score / total, 1.0)

    return best_type, confidence


def find_relationships(
    entities: list[dict], chunks: list[dict], lang: str
) -> list[dict]:
    """Scan text for relationship cue phrases between known entities."""
    relationships: list[dict] = []
    cues = RELATION_CUES_CN if lang == "zh" else RELATION_CUES_EN
    entity_names = {e["name"] for e in entities}
    entity_names.update({a for e in entities for a in e.get("aliases", [])})

    # Build name → entity id lookup
    name_to_id: dict[str, str] = {}
    for e in entities:
        name_to_id[e["name"]] = e["id"]
        for alias in e.get("aliases", []):
            name_to_id[alias] = e["id"]

    for chunk in chunks:
        text = chunk["text"]
        # For each pair of entities in the same chunk
        found_names = [n for n in entity_names if n in text]
        if len(found_names) < 2:
            continue

        for cue_phrase, rel_type in cues.items():
            if cue_phrase not in text:
                continue
            for i, name_a in enumerate(found_names):
                for name_b in found_names[i + 1 :]:
                    if name_a in name_to_id and name_b in name_to_id:
                        relationships.append(
                            {
                                "source": name_to_id[name_a],
                                "target": name_to_id[name_b],
                                "relation_type": rel_type,
                                "evidence": f"Chapter {chunk['chapter']}, "
                                f"para {chunk['paragraph']}: "
                                f"'{cue_phrase}' links '{name_a}' and '{name_b}'",
                                "confidence": "medium",
                            }
                        )

    # Deduplicate
    seen = set()
    unique_rels = []
    for r in relationships:
        key = tuple(sorted([r["source"], r["target"]])) + (r["relation_type"],)
        if key not in seen:
            seen.add(key)
            unique_rels.append(r)

    return unique_rels


# ============================================================================
# Main Extraction Pipeline
# ============================================================================


def extract_entities(
    text: str,
    lang: str | None = None,
    min_confidence: float = 0.3,
) -> dict[str, Any]:
    """
    Main extraction pipeline. Extracts entities and relationships from
    the provided novel text.
    """
    if lang is None:
        lang = detect_language(text)

    chunks = chunk_text(text)
    full_text_lower = text.lower()

    entities: list[dict] = []
    entity_counters: dict[str, int] = defaultdict(int)
    seen_names: set[str] = set()

    # ------------------------------------------------------------------
    # Step 1: Extract candidate names
    # ------------------------------------------------------------------
    candidates: list[tuple[str, str, int]] = []  # (name, context, para_idx)

    if lang == "zh":
        cn_names = extract_cn_names(text)
        for name, pos in cn_names:
            # Grab surrounding context (±50 chars)
            ctx_start = max(0, pos - 50)
            ctx_end = min(len(text), pos + len(name) + 50)
            context = text[ctx_start:ctx_end]
            candidates.append((name, context, pos))
    else:
        en_names = extract_capitalized_names(text)
        for name in en_names:
            pos = text.find(name)
            ctx_start = max(0, pos - 50)
            ctx_end = min(len(text), pos + len(name) + 50)
            context = text[ctx_start:ctx_end]
            candidates.append((name, context, pos))

    # ------------------------------------------------------------------
    # Step 2: Classify and build entity records
    # ------------------------------------------------------------------
    for name, context, pos in candidates:
        if name in seen_names:
            continue
        if len(name) < 2:
            continue

        entity_type, type_confidence = classify_entity(name, context, lang)
        if type_confidence < min_confidence:
            continue

        seen_names.add(name)
        entity_counters[entity_type] += 1
        entity_id = generate_id(entity_type, entity_counters[entity_type])

        # Collect all mentions of this entity
        mentions = []
        for chunk in chunks:
            if name in chunk["text"]:
                mentions.append(
                    {
                        "chapter": chunk["chapter"],
                        "paragraph": chunk["paragraph"],
                        "context": chunk["text"][:200],
                    }
                )

        entities.append(
            {
                "id": entity_id,
                "name": name,
                "aliases": [],
                "type": entity_type,
                "attributes": _default_attributes(entity_type),
                "mentions": mentions[:20],  # Cap at 20 mentions
                "first_mention": mentions[0] if mentions else None,
                "mention_count": len(mentions),
                "confidence": _confidence_label(type_confidence),
                "source_evidence": [
                    f"Chapter {m['chapter']}, para {m['paragraph']}: "
                    f"'{m['context'][:120]}...'"
                    for m in mentions[:5]
                ],
            }
        )

    # ------------------------------------------------------------------
    # Step 3: spaCy NER augmentation (if available)
    # ------------------------------------------------------------------
    if SPACY_AVAILABLE:
        try:
            model_name = "zh_core_web_sm" if lang == "zh" else "en_core_web_sm"
            nlp = spacy.load(model_name)
            doc = nlp(text[:100000])  # Process first 100k chars for performance

            for ent in doc.ents:
                if ent.label_ in ("PERSON", "GPE", "ORG", "FAC", "LOC"):
                    name = ent.text.strip()
                    if name in seen_names or len(name) < 2:
                        continue

                    type_map = {
                        "PERSON": "character",
                        "ORG": "faction",
                        "GPE": "location",
                        "LOC": "location",
                        "FAC": "location",
                    }
                    entity_type = type_map.get(ent.label_, "character")
                    seen_names.add(name)
                    entity_counters[entity_type] += 1
                    entity_id = generate_id(
                        entity_type, entity_counters[entity_type]
                    )

                    entities.append(
                        {
                            "id": entity_id,
                            "name": name,
                            "aliases": [],
                            "type": entity_type,
                            "attributes": _default_attributes(entity_type),
                            "mentions": [],
                            "first_mention": None,
                            "mention_count": 1,
                            "confidence": "medium",
                            "source_evidence": [
                                f"spaCy NER: {ent.label_} at char {ent.start_char}"
                            ],
                        }
                    )
        except Exception as e:
            print(f"[WARN] spaCy processing failed: {e}", file=sys.stderr)

    # ------------------------------------------------------------------
    # Step 4: Extract relationships
    # ------------------------------------------------------------------
    relationships = find_relationships(entities, chunks, lang)

    # ------------------------------------------------------------------
    # Step 5: Compute statistics
    # ------------------------------------------------------------------
    by_type = Counter(e["type"] for e in entities)
    low_conf_count = sum(1 for e in entities if e["confidence"] == "low")
    statistics = {
        "total_entities": len(entities),
        "by_type": dict(by_type),
        "total_relationships": len(relationships),
        "low_confidence_count": low_conf_count,
        "language": lang,
    }

    return {
        "entities": entities,
        "relationships": relationships,
        "statistics": statistics,
    }


def _default_attributes(entity_type: str) -> dict:
    """Return the default attribute schema for each entity type."""
    schemas = {
        "character": {
            "full_name": "",
            "aliases": [],
            "age": None,
            "gender": "",
            "appearance": "",
            "personality": "",
            "abilities": [],
            "affiliation": "",
            "rank": "",
            "status": "alive",  # alive / deceased / unknown
            "first_appearance": "",
        },
        "faction": {
            "full_name": "",
            "aliases": [],
            "type": "",  # sect, kingdom, guild, clan, etc.
            "leader": "",
            "members_count": None,
            "territory": "",
            "philosophy": "",
            "alignment": "",  # good, evil, neutral, chaotic, lawful
            "status": "active",
        },
        "location": {
            "full_name": "",
            "aliases": [],
            "type": "",  # city, realm, dungeon, etc.
            "parent_location": "",
            "climate": "",
            "population": None,
            "description": "",
            "significance": "",
        },
        "creature": {
            "full_name": "",
            "aliases": [],
            "species": "",
            "habitat": "",
            "abilities": [],
            "danger_level": "",  # low, medium, high, legendary
            "description": "",
        },
        "event": {
            "full_name": "",
            "aliases": [],
            "date": "",
            "location": "",
            "participants": [],
            "outcome": "",
            "significance": "",
            "era": "",
        },
        "item": {
            "full_name": "",
            "aliases": [],
            "type": "",  # weapon, artifact, tool, etc.
            "owner": "",
            "abilities": [],
            "description": "",
            "significance": "",
        },
    }
    return schemas.get(entity_type, {})


def _confidence_label(score: float) -> str:
    """Map a numeric confidence score to a label."""
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    return "low"


# ============================================================================
# CLI Entry Point
# ============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract named entities from novel text for worldbuilding.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input text file path. Reads from stdin if omitted.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file path. Writes to stdout if omitted.",
    )
    parser.add_argument(
        "--lang",
        choices=["zh", "en", "auto"],
        default="auto",
        help="Language hint (default: auto-detect).",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.3,
        help="Minimum confidence threshold for entity inclusion (0.0–1.0).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output.",
    )

    args = parser.parse_args()

    # Read input
    if args.input:
        text = args.input.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("[ERROR] No input text provided.", file=sys.stderr)
        sys.exit(1)

    # Determine language
    lang = None if args.lang == "auto" else args.lang

    # Run extraction
    result = extract_entities(text, lang=lang, min_confidence=args.min_confidence)

    # Write output
    indent = 2 if args.pretty else None
    json_output = json.dumps(result, ensure_ascii=False, indent=indent)

    if args.output:
        args.output.write_text(json_output, encoding="utf-8")
        print(f"[OK] Wrote {result['statistics']['total_entities']} entities "
              f"to {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
