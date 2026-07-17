#!/usr/bin/env python3
"""
build_timeline.py — Timeline Builder for Novelverse Forge
===========================================================
Normalizes relative time expressions from a novel into a unified,
sequenced timeline with epochs, events, and character fate lines.

Input:
    A JSON array of event objects (typically from extract_entities.py output
    filtered to type='event'), plus optional user-provided anchor dates.

    Each event should have at minimum:
      - name (str)
      - description (str)
      - temporal_markers (list[str]) — raw time phrases from the text

Output:
    Standardized timeline JSON:

    {
      "epochs": [
        {"id": "era_001", "name": "Age of Creation", "order": 0,
         "start_event": "evnt_001", "end_event": "evnt_005",
         "description": "..."}
      ],
      "events": [
        {
          "id": "evnt_001",
          "name": "The Great Sundering",
          "description": "...",
          "sequence_order": 3,
          "absolute_date": null,
          "relative_to": null,
          "relative_offset_years": null,
          "era": "era_001",
          "participants": ["char_001", "fact_002"],
          "location": "loc_003",
          "confidence": "high",
          "contradiction_flag": false
        }
      ],
      "character_fates": [
        {
          "character_id": "char_001",
          "character_name": "Yan Chen",
          "events": ["evnt_001", "evnt_003", "evnt_007"],
          "arc_summary": "From disciple to grandmaster"
        }
      ],
      "contradictions": [
        {
          "event_a": "evnt_002",
          "event_b": "evnt_004",
          "description": "Chapter 3 says 200 years apart, Chapter 7 says 150."
        }
      ]
    }

Dependencies:
    Python 3.9+ (stdlib only — no external packages required)

Usage:
    python build_timeline.py --input events.json > timeline.json
    python build_timeline.py --input events.json --anchors anchors.json --output timeline.json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ============================================================================
# Time Expression Patterns
# ============================================================================

# Chinese relative time patterns
# Format: (regex_pattern, multiplier_in_years)
CN_TIME_PATTERNS: list[tuple[re.Pattern, float]] = [
    (re.compile(r"(\d+)万年前"), 10_000),
    (re.compile(r"(\d+)千年前"), 1_000),
    (re.compile(r"(\d+)百年前"), 100),
    (re.compile(r"(\d+)年前"), 1),
    (re.compile(r"(\d+)月前"), 1 / 12),
    (re.compile(r"(\d+)天前"), 1 / 365),
    (re.compile(r"(\d+)万年后"), 10_000),
    (re.compile(r"(\d+)千年后"), 1_000),
    (re.compile(r"(\d+)百年后"), 100),
    (re.compile(r"(\d+)年后"), 1),
    (re.compile(r"(\d+)月后"), 1 / 12),
    (re.compile(r"(\d+)天后"), 1 / 365),
    (re.compile(r"(\d+)个纪元"), 1_000_000),  # "纪元" treated as ~1M years
    (re.compile(r"(\d+)万年"), 10_000),
    (re.compile(r"(\d+)千年"), 1_000),
    (re.compile(r"(\d+)载"), 1),  # literary "year"
    (re.compile(r"距今(\d+)年"), 1),
    (re.compile(r"(\d+)甲子"), 60),
    # Qualitative (mapped to approximate values)
    (re.compile(r"数年前"), 3),
    (re.compile(r"数年后"), 3),
    (re.compile(r"几年前"), 3),
    (re.compile(r"几年后"), 3),
    (re.compile(r"不久之前"), 1),
    (re.compile(r"不久之后"), 1),
    (re.compile(r"很久以前"), 100),
    (re.compile(r"遥远的未来"), 100),
]

# English relative time patterns
EN_TIME_PATTERNS: list[tuple[re.Pattern, float]] = [
    (re.compile(r"(\d+)\s*millennia?\s*ago", re.I), 1_000),
    (re.compile(r"(\d+)\s*centur(?:y|ies)\s*ago", re.I), 100),
    (re.compile(r"(\d+)\s*decades?\s*ago", re.I), 10),
    (re.compile(r"(\d+)\s*years?\s*ago", re.I), 1),
    (re.compile(r"(\d+)\s*months?\s*ago", re.I), 1 / 12),
    (re.compile(r"(\d+)\s*days?\s*ago", re.I), 1 / 365),
    (re.compile(r"(\d+)\s*millennia?\s*(?:later|from now|after)", re.I), 1_000),
    (re.compile(r"(\d+)\s*centur(?:y|ies)\s*(?:later|from now|after)", re.I), 100),
    (re.compile(r"(\d+)\s*decades?\s*(?:later|from now|after)", re.I), 10),
    (re.compile(r"(\d+)\s*years?\s*(?:later|from now|after)", re.I), 1),
    (re.compile(r"(\d+)\s*months?\s*(?:later|from now|after)", re.I), 1 / 12),
    (re.compile(r"(\d+)\s*days?\s*(?:later|from now|after)", re.I), 1 / 365),
    (re.compile(r"several\s*years?\s*ago", re.I), 3),
    (re.compile(r"several\s*years?\s*(?:later|from now)", re.I), 3),
    (re.compile(r"a\s*few\s*years?\s*ago", re.I), 3),
    (re.compile(r"a\s*few\s*years?\s*(?:later|from now)", re.I), 3),
    (re.compile(r"long\s*ago", re.I), 100),
    (re.compile(r"in\s*the\s*distant\s*future", re.I), 100),
    (re.compile(r"eon", re.I), 1_000_000),
]

# Era boundary keywords — presence of these suggests a new era
CN_ERA_KEYWORDS = [
    "纪元",
    "时代",
    "太古",
    "远古",
    "上古",
    "中古",
    "近古",
    "当世",
    "创世",
    "末法",
    "灵气复苏",
]
EN_ERA_KEYWORDS = [
    "age of",
    "era of",
    "eon",
    "epoch",
    "before the",
    "after the",
    "dawn of",
    "twilight of",
    "rising of",
    "fall of",
    "pre-",
    "post-",
    "first age",
    "second age",
    "third age",
    "golden age",
    "dark age",
]


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class TimelineEvent:
    """Internal representation of a timeline event during processing."""

    id: str
    name: str
    description: str = ""
    temporal_markers: list[str] = field(default_factory=list)
    sequence_order: int | None = None
    absolute_date: str | None = None
    relative_to: str | None = None
    relative_offset_years: float | None = None
    era: str | None = None
    participants: list[str] = field(default_factory=list)
    location: str | None = None
    confidence: str = "medium"
    contradiction_flag: bool = False
    chapter_ref: str = ""


@dataclass
class Era:
    """A named era/epoch in the timeline."""

    id: str
    name: str
    order: int
    start_event: str | None = None
    end_event: str | None = None
    description: str = ""
    approximate_span_years: float | None = None


# ============================================================================
# Time Expression Parser
# ============================================================================


def parse_time_expression(
    text: str, lang: str = "zh"
) -> list[dict[str, Any]]:
    """
    Parse all time expressions from a string.

    Returns a list of dicts with:
      - matched_text (str)
      - numeric_value (float)
      - unit_years (float)
      - total_years (float)
      - direction ("past" or "future")
    """
    patterns = CN_TIME_PATTERNS if lang == "zh" else EN_TIME_PATTERNS
    results: list[dict[str, Any]] = []

    for pattern, multiplier in patterns:
        for m in pattern.finditer(text):
            # Try to extract a numeric group
            numeric_val = 1.0
            try:
                numeric_val = float(m.group(1))
            except (IndexError, ValueError):
                pass

            total_years = numeric_val * multiplier

            # Determine direction
            direction = "past"
            if any(
                kw in m.group(0)
                for kw in ["后", "later", "from now", "after", "未来"]
            ):
                direction = "future"

            results.append(
                {
                    "matched_text": m.group(0).strip(),
                    "numeric_value": numeric_val,
                    "unit_years": multiplier,
                    "total_years": round(total_years, 2),
                    "direction": direction,
                    "position": m.start(),
                }
            )

    # Sort by position in text
    results.sort(key=lambda x: x["position"])
    return results


def detect_eras(text: str, lang: str) -> list[dict[str, Any]]:
    """Detect named eras from the full novel text."""
    eras = []
    keywords = CN_ERA_KEYWORDS if lang == "zh" else EN_ERA_KEYWORDS

    for kw in keywords:
        for m in re.finditer(re.escape(kw), text, re.IGNORECASE):
            # Extract surrounding context as era name
            start = max(0, m.start() - 20)
            end = min(len(text), m.end() + 30)
            context = text[start:end].strip()

            # Try to get a clean era name
            era_name = context
            # Trim to the nearest punctuation
            for sep in ["。", "，", ".", ",", "\n", "—", ";"]:
                if sep in era_name:
                    era_name = era_name.split(sep)[0]

            if len(era_name) >= 2:
                eras.append({"name": era_name.strip(), "position": m.start()})

    # Remove duplicates by name similarity
    seen_names = set()
    unique_eras = []
    for era in eras:
        clean = era["name"].strip().lower()
        if clean not in seen_names and len(clean) <= 60:
            seen_names.add(clean)
            unique_eras.append(era)

    # Sort by position
    unique_eras.sort(key=lambda x: x["position"])

    # Assign IDs and order
    for i, era in enumerate(unique_eras):
        era["id"] = f"era_{i + 1:03d}"
        era["order"] = i
        del era["position"]

    return unique_eras


# ============================================================================
# Main Timeline Builder
# ============================================================================


def build_timeline(
    events_input: list[dict[str, Any]],
    anchors: list[dict[str, Any]] | None = None,
    full_text: str = "",
    lang: str | None = None,
) -> dict[str, Any]:
    """
    Build a normalized timeline from extracted events and time expressions.

    Parameters
    ----------
    events_input : list[dict]
        Raw event objects. Each must have at minimum 'name' and 'description'.
        May optionally include 'temporal_markers', 'participants', 'location'.
    anchors : list[dict] or None
        User-provided anchor points with known absolute dates, e.g.:
        [{"event_name": "The Sundering", "absolute_year": 0}]
    full_text : str
        Original novel text for era detection and secondary time-parsing.
    lang : str or None
        Language hint. Auto-detected if None.

    Returns
    -------
    dict with keys: epochs, events, character_fates, contradictions
    """
    if lang is None:
        # Simple CJK detection
        cjk = sum(1 for ch in full_text if "一" <= ch <= "鿿")
        lang = "zh" if cjk > len(full_text) * 0.1 else "en"

    # ------------------------------------------------------------------
    # Step 1: Normalize events to internal representation
    # ------------------------------------------------------------------
    events: list[TimelineEvent] = []
    for i, raw in enumerate(events_input):
        evt = TimelineEvent(
            id=raw.get("id", f"evnt_{i + 1:03d}"),
            name=raw.get("name", f"Event {i + 1}"),
            description=raw.get("description", ""),
            temporal_markers=raw.get("temporal_markers", []),
            participants=raw.get("participants", []),
            location=raw.get("location"),
            confidence=raw.get("confidence", "medium"),
            chapter_ref=raw.get("chapter_ref", ""),
        )

        # Also scan the description for time expressions
        if evt.description and not evt.temporal_markers:
            parsed = parse_time_expression(evt.description, lang)
            evt.temporal_markers = [p["matched_text"] for p in parsed]

        events.append(evt)

    # ------------------------------------------------------------------
    # Step 2: Assign each event a numeric offset from its temporal markers
    # ------------------------------------------------------------------
    anchor_map: dict[str, float] = {}
    if anchors:
        for a in anchors:
            anchor_map[a["event_name"]] = a.get("absolute_year", 0)

    for evt in events:
        parsed_markers = []
        for marker in evt.temporal_markers:
            parsed = parse_time_expression(marker, lang)
            parsed_markers.extend(parsed)

        if not parsed_markers:
            # Also try parsing the name itself
            parsed = parse_time_expression(evt.name, lang)
            parsed_markers.extend(parsed)

        if parsed_markers:
            # Use the most specific (largest total_years) marker
            best = max(parsed_markers, key=lambda x: abs(x["total_years"]))
            evt.relative_offset_years = best["total_years"]
            if evt.relative_offset_years < 0.1:
                evt.relative_offset_years = 1.0  # Floor to 1 year

    # ------------------------------------------------------------------
    # Step 3: Detect eras from full text
    # ------------------------------------------------------------------
    detected_eras = detect_eras(full_text, lang) if full_text else []

    # If no eras detected, create a single default era
    if not detected_eras:
        detected_eras = [
            {
                "id": "era_001",
                "name": "Main Story Era" if lang == "en" else "主线时代",
                "order": 0,
            }
        ]

    # ------------------------------------------------------------------
    # Step 4: Sequence events by chapter order + relative markers
    # ------------------------------------------------------------------
    # Sort events: first by chapter appearance, then by relative offset
    def sort_key(evt: TimelineEvent) -> tuple[int, float]:
        chapter = 0
        if evt.chapter_ref:
            try:
                chapter = int(re.search(r"\d+", evt.chapter_ref).group())
            except (AttributeError, ValueError):
                pass
        offset = evt.relative_offset_years or 0
        return (chapter, offset)

    events.sort(key=sort_key)

    # Assign sequence orders
    for i, evt in enumerate(events):
        evt.sequence_order = i

    # ------------------------------------------------------------------
    # Step 5: Assign eras to events
    # ------------------------------------------------------------------
    if len(detected_eras) >= 2:
        # Distribute events across eras
        events_per_era = max(1, len(events) // len(detected_eras))
        for i, evt in enumerate(events):
            era_idx = min(i // events_per_era, len(detected_eras) - 1)
            evt.era = detected_eras[era_idx]["id"]

            # Link first/last events to eras
            if i == 0 or (i > 0 and events[i - 1].era != evt.era):
                detected_eras[era_idx]["start_event"] = evt.id
            detected_eras[era_idx]["end_event"] = evt.id
    else:
        for evt in events:
            evt.era = detected_eras[0]["id"]
        if events:
            detected_eras[0]["start_event"] = events[0].id
            detected_eras[0]["end_event"] = events[-1].id

    # ------------------------------------------------------------------
    # Step 6: Detect temporal contradictions
    # ------------------------------------------------------------------
    contradictions: list[dict[str, str]] = []

    # Check for events that appear "before" their predecessor but have
    # a larger sequence_order
    for i in range(1, len(events)):
        prev = events[i - 1]
        curr = events[i]

        if (
            prev.relative_offset_years
            and curr.relative_offset_years
            and prev.sequence_order
            and curr.sequence_order
        ):
            # If prev occurs "10 years later" and curr "3 years later",
            # but curr comes after prev in the text, flag it
            if prev.sequence_order < curr.sequence_order:
                # This is normal; contradiction check is on absolute meaning
                pass

        # Check for contradictory era assignments
        if prev.era and curr.era and prev.era != curr.era:
            # Ensure this boundary makes sense
            era_boundary_events.append((prev, curr))

    # Check for duplicate names with different temporal claims
    name_groups: dict[str, list[TimelineEvent]] = defaultdict(list)
    for evt in events:
        name_groups[evt.name.lower().strip()].append(evt)

    for name, group in name_groups.items():
        if len(group) >= 2:
            offsets = {e.relative_offset_years for e in group if e.relative_offset_years}
            if len(offsets) >= 2:
                contradictions.append(
                    {
                        "event_a": group[0].id,
                        "event_b": group[1].id,
                        "description": (
                            f"Event '{name}' appears with conflicting time references: "
                            f"{offsets}"
                        ),
                    }
                )
                for evt in group:
                    evt.contradiction_flag = True

    # ------------------------------------------------------------------
    # Step 7: Build character fate lines
    # ------------------------------------------------------------------
    character_events: dict[str, list[str]] = defaultdict(list)
    character_names: dict[str, str] = {}

    for evt in events:
        for participant_id in evt.participants:
            character_events[participant_id].append(evt.id)

    character_fates = []
    for char_id, evt_ids in character_events.items():
        character_fates.append(
            {
                "character_id": char_id,
                "character_name": character_names.get(char_id, char_id),
                "events": evt_ids,
                "arc_summary": f"Involved in {len(evt_ids)} major events",
            }
        )

    # ------------------------------------------------------------------
    # Step 8: Assemble output
    # ------------------------------------------------------------------
    # Convert eras
    output_eras = []
    for era in detected_eras:
        output_eras.append(
            {
                "id": era["id"],
                "name": era["name"],
                "order": era["order"],
                "start_event": era.get("start_event"),
                "end_event": era.get("end_event"),
                "description": era.get("description", ""),
                "approximate_span_years": era.get("approximate_span_years"),
            }
        )

    # Convert events
    output_events = []
    for evt in events:
        output_events.append(
            {
                "id": evt.id,
                "name": evt.name,
                "description": evt.description,
                "sequence_order": evt.sequence_order,
                "absolute_date": evt.absolute_date,
                "relative_to": evt.relative_to,
                "relative_offset_years": evt.relative_offset_years,
                "era": evt.era,
                "participants": evt.participants,
                "location": evt.location,
                "confidence": evt.confidence,
                "contradiction_flag": evt.contradiction_flag,
                "temporal_markers": evt.temporal_markers,
            }
        )

    return {
        "epochs": output_eras,
        "events": output_events,
        "character_fates": character_fates,
        "contradictions": contradictions,
    }


# ============================================================================
# CLI Entry Point
# ============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a normalized timeline from novel events.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Input JSON file with event objects.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file path. Writes to stdout if omitted.",
    )
    parser.add_argument(
        "--anchors",
        "-a",
        type=Path,
        help="Optional JSON file with known absolute dates as anchors.",
    )
    parser.add_argument(
        "--full-text",
        "-t",
        type=Path,
        help="Original novel text file for era detection.",
    )
    parser.add_argument(
        "--lang",
        choices=["zh", "en"],
        help="Language hint.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output.",
    )

    args = parser.parse_args()

    # Read input events
    events_input = json.loads(args.input.read_text(encoding="utf-8"))
    if isinstance(events_input, dict):
        # Could be the full entities output; extract events
        events_input = events_input.get("entities", events_input)
        events_input = [e for e in events_input if e.get("type") == "event"]

    if not events_input:
        print("[WARN] No event-type entities found in input.", file=sys.stderr)
        # Still produce valid output structure
        result = {
            "epochs": [],
            "events": [],
            "character_fates": [],
            "contradictions": [],
        }
    else:
        # Read anchors if provided
        anchors = None
        if args.anchors:
            anchors = json.loads(args.anchors.read_text(encoding="utf-8"))

        # Read full text if provided
        full_text = ""
        if args.full_text:
            full_text = args.full_text.read_text(encoding="utf-8")

        result = build_timeline(
            events_input,
            anchors=anchors,
            full_text=full_text,
            lang=args.lang,
        )

    # Write output
    indent = 2 if args.pretty else None
    json_output = json.dumps(result, ensure_ascii=False, indent=indent)

    if args.output:
        args.output.write_text(json_output, encoding="utf-8")
        print(
            f"[OK] Timeline with {len(result['events'])} events "
            f"and {len(result['epochs'])} epochs written to {args.output}",
            file=sys.stderr,
        )
    else:
        print(json_output)


if __name__ == "__main__":
    main()
