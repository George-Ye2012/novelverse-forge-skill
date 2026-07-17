#!/usr/bin/env python3
"""
generate_html.py v4 — Dynamic Design Genome Generator for Novelverse Forge
===========================================================================
Completely rewritten: no preset themes. All CSS is dynamically generated from
a visual design scheme JSON (produced by visual_genome.py).

The generator:
1. Reads the layout skeleton from assets/templates/page_template.html
2. Reads the visual design scheme JSON
3. Dynamically generates ALL CSS from the design scheme
4. Injects entity data, timeline data, and relationship data
5. Inlines JS modules from assets/js/
6. Writes a single self-contained HTML file

Usage:
    python generate_html.py --input world_data.json --design design.json -o output.html
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"
CSS_DIR = SKILL_ROOT / "assets" / "css"
JS_DIR = SKILL_ROOT / "assets" / "js"

DEFAULT_TEMPLATE = TEMPLATE_DIR / "page_template.html"
BASE_CSS_FILE = CSS_DIR / "base.css"

JS_MODULES = [
    JS_DIR / "interactions.js",
    JS_DIR / "navigation.js",
    JS_DIR / "timeline.js",
    JS_DIR / "search.js",
]

# Entity display configuration
TYPE_ICONS = {"character": "👤", "faction": "🏛️", "location": "📍", "creature": "🐉", "event": "📜", "item": "⚔️"}
TYPE_LABELS = {"character": "Characters", "faction": "Factions", "location": "Locations",
               "creature": "Beings & Creatures", "event": "Events", "item": "Artifacts & Items"}

QUICK_NAV_ITEMS = [
    ("timeline", "⏳", "Chronicles"),
    ("characters", "👤", "Characters"),
    ("factions", "🏛️", "Factions"),
    ("beings", "🐉", "Beings"),
    ("relations", "🕸️", "Web of Ties"),
]

RELATION_META = {
    "romantic": ("💕", "Romantic", "#FF8C94"),
    "sibling": ("👥", "Sibling", "#FF6B6B"),
    "parent_child": ("👶", "Parent-Child", "#4ECDC4"),
    "master_apprentice": ("📚", "Master-Apprentice", "#FFD93D"),
    "enmity": ("⚔️", "Enmity", "#FF3333"),
    "ally": ("🤝", "Ally", "#6BCB77"),
    "allegiance": ("🏴", "Allegiance", "#4D96FF"),
    "blood_bond": ("🩸", "Blood Bond", "#9B59B6"),
    "creator_creation": ("🔧", "Creator-Creation", "#00CED1"),
    "possessor_possessed": ("🔑", "Possession", "#FFD700"),
    "mentor": ("🧭", "Mentor", "#E8A87C"),
}


# ============================================================================
# Helpers
# ============================================================================

def read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"[WARN] Missing: {path}", file=sys.stderr)
    return ""


def esc(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def conf_badge(level: str) -> str:
    colors = {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}
    c = colors.get(level, "#6b7280")
    return f'<span class="confidence-badge" style="background:{c}">&#8203;{level.upper()}</span>'


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, val))


# ============================================================================
# Dynamic CSS Generation from Design Scheme
# ============================================================================

def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def generate_dynamic_css(design: dict) -> str:
    """Generate ALL visual CSS from the design scheme JSON."""
    c = design["color"]
    t = design["typography"]
    s = design["space"]
    tx = design["texture"]
    l = design["lighting"]
    m = design["motion"]
    mood = design["mood"]

    css_parts = []

    # ------------------------------------------------------------------
    # 1. CSS Custom Properties (Design Tokens)
    # ------------------------------------------------------------------
    css_parts.append(f"""
/* =====================================================================
   DYNAMIC DESIGN TOKENS — Generated from Visual Genome
   Design: {design['design_name']}
   ID: {design['design_id']}
   ===================================================================== */

:root {{
  /* === Color System === */
  --nv-color-primary: {c['primary']};
  --nv-color-primary-hover: {adjust_hex(c['primary'], l_mult=1.15)};
  --nv-color-primary-text: {c['bg_start']};
  --nv-color-secondary: {c['secondary']};
  --nv-color-secondary-hover: {adjust_hex(c['secondary'], l_mult=1.15)};
  --nv-color-accent: {c['accent']};
  --nv-color-bg-start: {c['bg_start']};
  --nv-color-bg-end: {c['bg_end']};
  --nv-color-text-primary: {c['text_primary']};
  --nv-color-text-secondary: {c['text_secondary']};
  --nv-color-text-muted: {adjust_hex(c['text_secondary'], l_mult=1.3)};
  --nv-color-surface: {c['surface']};
  --nv-color-surface-hover: {adjust_hex(c['surface'], l_mult=1.1)};
  --nv-color-border: {c['surface_border']};
  --nv-color-border-glow: {c['glow']};
  --nv-color-glow: {c['glow']};
  --nv-color-shadow-glow: {c['glow']}33;
  --nv-color-warning: #ffa726;
  --nv-color-success: #66bb6a;
  --nv-color-danger: #ef5350;
  --nv-color-warmth: {c['warmth']};
  --nv-color-saturation: {c['saturation']};
  --nv-color-brightness: {c['brightness']};

  /* === Typography System === */
  --nv-font-heading: '{t['heading_font']}', {get_fallback(t['heading_font'])};
  --nv-font-body: '{t['body_font']}', {get_fallback(t['body_font'])};
  --nv-font-decorative: '{t.get('decorative_font', t['heading_font'])}', {get_fallback(t.get('decorative_font', t['heading_font']))};
  --nv-font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  --nv-font-size-xs: 0.75rem;
  --nv-font-size-sm: 0.875rem;
  --nv-font-size-base: 1rem;
  --nv-font-size-lg: {round(t['scale_ratio'] * 16)}px;
  --nv-font-size-xl: {round(t['scale_ratio']**2 * 16)}px;
  --nv-font-size-2xl: {round(t['scale_ratio']**3 * 16)}px;
  --nv-font-size-3xl: {round(t['scale_ratio']**4 * 16)}px;
  --nv-font-size-4xl: {round(t['scale_ratio']**5 * 16)}px;
  --nv-font-size-5xl: {round(t['scale_ratio']**6 * 16)}px;
  --nv-heading-weight: {t['heading_weight']};
  --nv-body-weight: {t['body_weight']};
  --nv-heading-letter-spacing: {t['heading_letter_spacing']}em;
  --nv-body-letter-spacing: {t['body_letter_spacing']}em;
  --nv-line-height-tight: {clamp(t['line_height'] - 0.45, 1.1, 1.5):.2f};
  --nv-line-height-snug: {clamp(t['line_height'] - 0.25, 1.2, 1.6):.2f};
  --nv-line-height-base: {t['line_height']:.2f};
  --nv-line-height-relaxed: {clamp(t['line_height'] + 0.15, 1.5, 2.0):.2f};
  --nv-letter-spacing-tight: -0.02em;
  --nv-letter-spacing-normal: 0;
  --nv-letter-spacing-wide: 0.02em;
  --nv-letter-spacing-wider: {t['heading_letter_spacing'] + 0.02:.3f}em;

  /* === Spacing System === */
  --nv-space-1: 4px;
  --nv-space-2: {s['gap_small']};
  --nv-space-3: 12px;
  --nv-space-4: {s['gap_medium']};
  --nv-space-5: 24px;
  --nv-space-6: {s['gap_large']};
  --nv-space-7: {s['gap_xl']};
  --nv-space-8: 64px;
  --nv-space-9: 96px;

  /* === Radius System === */
  --nv-radius-xs: {s['radius_small']};
  --nv-radius-sm: calc({s['radius_small']} + 4px);
  --nv-radius-md: {s['radius_medium']};
  --nv-radius-lg: {s['radius_card']};
  --nv-radius-xl: {s['radius_large']};
  --nv-radius-full: 9999px;

  /* === Shadows === */
  --nv-shadow-xs: 0 1px 2px {l['shadow_color']};
  --nv-shadow-sm: 0 2px 8px {l['shadow_color']};
  --nv-shadow-md: 0 8px {l['shadow_blur']} {l['shadow_color']};
  --nv-shadow-lg: 0 16px calc({l['shadow_blur']} * 1.5) {l['shadow_color']};
  --nv-shadow-xl: 0 24px calc({l['shadow_blur']} * 2) {l['shadow_color']};

  /* === Transitions === */
  --nv-ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --nv-ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --nv-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --nv-duration-fast: {0.1 + m['speed'] * 0.1:.2f}s;
  --nv-duration-base: {0.2 + m['speed'] * 0.15:.2f}s;
  --nv-duration-slow: {0.3 + m['speed'] * 0.25:.2f}s;
  --nv-duration-slower: {0.5 + m['speed'] * 0.3:.2f}s;

  /* === Layout === */
  --nv-max-width: 1280px;
  --nv-header-height: 72px;
  --nv-header-height-scrolled: 56px;
  --nv-page-padding: {s['page_padding']};
  --nv-card-padding: {s['card_padding']};

  /* === Z-index === */
  --nv-z-dropdown: 100;
  --nv-z-sticky: 200;
  --nv-z-overlay: 300;
  --nv-z-modal: 400;
  --nv-z-tooltip: 500;
  --nv-z-toast: 600;
}}

/* =====================================================================
   TEXTURE & BACKGROUND
   ===================================================================== */
{generate_texture_css(tx, c)}

/* =====================================================================
   MOTION & ANIMATION
   ===================================================================== */
{generate_motion_keyframes(m, c)}

/* =====================================================================
   THEME-AWARE OVERRIDES
   ===================================================================== */
body {{
  background: linear-gradient(135deg, var(--nv-color-bg-start), var(--nv-color-bg-end));
  background-attachment: fixed;
}}

h1, h2, h3, h4, .h1, .h2, .h3, .h4 {{
  font-family: var(--nv-font-heading);
  font-weight: var(--nv-heading-weight);
  letter-spacing: var(--nv-heading-letter-spacing);
}}

/* Hero title gradient */
.hero-section h1 {{
  background: linear-gradient(
    135deg,
    var(--nv-color-text-primary) 0%,
    var(--nv-color-primary) 50%,
    var(--nv-color-accent) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}

/* Section header accent bar */
.section-header h2::before {{
  background: var(--nv-color-primary);
}}

/* Entity card hover glow */
.entity-card:hover {{
  box-shadow: var(--nv-shadow-lg), 0 0 48px var(--nv-color-shadow-glow);
  border-color: var(--nv-color-border-glow);
}}

.entity-card::before {{
  background: radial-gradient(
    400px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    var(--nv-color-shadow-glow),
    transparent 60%
  );
}}

/* Glass card hover */
.glass-card:hover {{
  box-shadow: var(--nv-shadow-lg), 0 0 40px var(--nv-color-shadow-glow);
}}

/* Timeline track */
.timeline-track::before {{
  background: linear-gradient(
    90deg,
    var(--nv-color-border),
    var(--nv-color-primary),
    var(--nv-color-border)
  );
}}

/* Scrollbar */
::-webkit-scrollbar-thumb {{
  background: linear-gradient(180deg, var(--nv-color-primary), var(--nv-color-secondary));
}}

/* Button glow */
.btn-primary {{
  background: linear-gradient(135deg, var(--nv-color-primary), var(--nv-color-secondary));
  box-shadow: 0 4px 16px var(--nv-color-shadow-glow);
}}
.btn-primary:hover {{
  box-shadow: 0 8px 24px var(--nv-color-shadow-glow);
}}

/* Active nav/filter indicators */
.entity-type-nav button.active {{
  background: var(--nv-color-primary);
  color: var(--nv-color-primary-text);
  box-shadow: 0 2px 12px var(--nv-color-shadow-glow);
}}

.era-filter-btn:hover, .era-filter-btn.active {{
  background: var(--nv-color-primary);
  color: var(--nv-color-primary-text);
  border-color: var(--nv-color-primary);
}}

/* Design rationale footer */
.design-rationale-footer {{
  padding: var(--nv-space-7) var(--nv-space-5);
  border-top: 1px solid var(--nv-color-border);
  background: var(--nv-color-surface);
}}
.design-rationale-footer .rationale-inner {{
  max-width: var(--nv-max-width);
  margin: 0 auto;
}}
.design-rationale-footer h3 {{
  font-family: var(--nv-font-heading);
  font-weight: var(--nv-heading-weight);
  color: var(--nv-color-primary);
  margin-bottom: var(--nv-space-4);
  font-size: var(--nv-font-size-lg);
}}
.design-rationale-footer p {{
  color: var(--nv-color-text-secondary);
  font-size: var(--nv-font-size-sm);
  line-height: var(--nv-line-height-relaxed);
  margin-bottom: var(--nv-space-2);
}}
.design-rationale-footer .design-concept {{
  font-family: var(--nv-font-decorative);
  font-size: var(--nv-font-size-base);
  color: var(--nv-color-text-primary);
  margin-top: var(--nv-space-4);
  padding-top: var(--nv-space-4);
  border-top: 1px solid var(--nv-color-border);
  text-align: center;
}}
""")

    return "\n".join(css_parts)


def adjust_hex(hex_str: str, h_shift: float = 0, s_mult: float = 1.0, l_mult: float = 1.0) -> str:
    """Adjust a hex color's HSL values."""
    r, g, b = hex_to_rgb(hex_str)
    # Simple RGB-based adjustment
    nr = min(255, max(0, int(r * l_mult)))
    ng = min(255, max(0, int(g * l_mult)))
    nb = min(255, max(0, int(b * l_mult)))
    return f"#{nr:02X}{ng:02X}{nb:02X}"


def get_fallback(font_name: str) -> str:
    """Get system font fallback stack."""
    serif_fonts = ["Noto Serif SC", "Playfair Display", "Cinzel", "Lora",
                   "Cormorant Garamond", "EB Garamond", "Uncial Antiqua",
                   "Ma Shan Zheng"]
    mono_fonts = ["Share Tech Mono", "Special Elite"]
    if font_name in serif_fonts:
        return "Georgia, 'Times New Roman', serif"
    elif font_name in mono_fonts:
        return "'Courier New', monospace"
    else:
        return "system-ui, -apple-system, 'Segoe UI', sans-serif"


def round(val: float, decimals: int = 0) -> float:
    return float(f"{val:.{decimals}f}")


def generate_texture_css(texture: dict, color: dict) -> str:
    """Generate CSS for the background texture."""
    tx_type = texture["type"]
    intensity = texture["intensity"]

    if tx_type == "grain":
        opacity = intensity * 0.12
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='{opacity}'/%3E%3C/svg%3E");
  opacity: {intensity};
}}"""

    elif tx_type == "grid":
        opacity = intensity * 0.1
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    linear-gradient(rgba(255,255,255,{opacity}) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,{opacity}) 1px, transparent 1px);
  background-size: 40px 40px;
}}"""

    elif tx_type == "stars":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 25% 45%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1.5px 1.5px at 40% 10%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 55% 35%, rgba(255,255,255,0.4), transparent),
    radial-gradient(1px 1px at 70% 60%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1.5px 1.5px at 85% 25%, rgba(255,255,255,0.3), transparent),
    radial-gradient(2px 2px at 15% 75%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 60% 85%, rgba(255,255,255,0.4), transparent),
    radial-gradient(1px 1px at 90% 55%, rgba(255,255,255,0.5), transparent);
}}"""

    elif tx_type == "neon":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      {color['bg_start']} 2px,
      {color['bg_start']} 4px
    );
  opacity: 0.3;
}}"""

    elif tx_type == "paper":
        opacity = intensity * 0.06
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='{opacity}'/%3E%3C/svg%3E");
  opacity: {intensity};
}}"""

    elif tx_type == "ink_wash":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse at 30% 20%, {color['primary']}10 0%, transparent 50%),
    radial-gradient(ellipse at 70% 60%, {color['secondary']}08 0%, transparent 50%),
    radial-gradient(ellipse at 50% 80%, {color['accent']}06 0%, transparent 40%);
}}"""

    elif tx_type == "metal":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background: linear-gradient(
    135deg,
    {color['surface']} 0%,
    {color['bg_end']}25 25%,
    {color['surface']} 50%,
    {color['bg_start']}25 75%,
    {color['surface']} 100%
  );
  opacity: 0.5;
}}"""

    elif tx_type == "shadow":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse at 50% 0%, {color['bg_end']} 0%, transparent 60%),
    radial-gradient(ellipse at 80% 50%, {color['secondary']}08 0%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, {color['primary']}06 0%, transparent 40%);
}}"""

    elif tx_type == "crystal":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.06) 0%, transparent 50%),
    linear-gradient(225deg, {color['accent']}08 0%, transparent 50%);
}}"""

    elif tx_type == "wave":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 30px,
    {color['primary']}05 30px,
    {color['primary']}05 31px
  );
}}"""

    elif tx_type == "fire":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse at 50% 100%, {color['accent']}20 0%, transparent 60%),
    radial-gradient(ellipse at 30% 80%, {color['primary']}15 0%, transparent 40%);
}}"""

    elif tx_type == "mist":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse at 30% 40%, {color['surface']} 0%, transparent 50%),
    radial-gradient(ellipse at 70% 60%, {color['bg_end']} 0%, transparent 50%);
}}"""

    elif tx_type == "stone":
        return f"""
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.4' numOctaves='5' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E");
  opacity: {intensity};
}}"""

    else:  # smooth or unknown
        return "/* Smooth texture — no overlay needed */"


def generate_motion_keyframes(motion: dict, color: dict) -> str:
    """Generate CSS keyframes for motion effects."""
    mtype = motion["type"]
    speed = motion["speed"]
    parts = []

    if motion.get("has_glow_pulse"):
        duration = max(1.5, 5.0 - speed * 3.5)
        parts.append(f"""
@keyframes glow-pulse {{
  0%, 100% {{ box-shadow: 0 0 5px {color['glow']}44; }}
  50% {{ box-shadow: 0 0 25px {color['glow']}88; }}
}}
.glow-pulse-element {{
  animation: glow-pulse {duration:.1f}s ease-in-out infinite;
}}""")

    if motion.get("has_parallax"):
        duration = max(8, 25 - speed * 20)
        parts.append(f"""
@keyframes parallax-drift {{
  0% {{ transform: translateX(0) translateY(0); }}
  25% {{ transform: translateX(-10px) translateY(-5px); }}
  50% {{ transform: translateX(0) translateY(-10px); }}
  75% {{ transform: translateX(10px) translateY(-5px); }}
  100% {{ transform: translateX(0) translateY(0); }}
}}
.parallax-layer {{
  animation: parallax-drift {duration:.1f}s linear infinite;
}}""")

    if mtype == "wave":
        duration = max(4, 10 - speed * 7)
        parts.append(f"""
@keyframes wave-motion {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-6px); }}
}}
.wave-element {{
  animation: wave-motion {duration:.1f}s ease-in-out infinite;
}}""")

    if mtype == "pulse" and not motion.get("has_glow_pulse"):
        duration = max(1, 4 - speed * 3)
        parts.append(f"""
@keyframes subtle-pulse {{
  0%, 100% {{ opacity: 0.85; }}
  50% {{ opacity: 1; }}
}}
.pulse-element {{
  animation: subtle-pulse {duration:.1f}s ease-in-out infinite;
}}""")

    return "\n".join(parts)


# ============================================================================
# Google Fonts URL Generation
# ============================================================================

def generate_google_fonts_url(design: dict) -> str:
    """Generate Google Fonts import URL dynamically based on selected fonts."""
    t = design["typography"]
    fonts_needed = set()

    for font_key in ["heading_font", "body_font", "decorative_font"]:
        font = t.get(font_key, "")
        if font:
            fonts_needed.add(font)

    font_configs = {
        "Noto Serif SC": "Noto+Serif+SC:wght@400;700;900",
        "Noto Sans SC": "Noto+Sans+SC:wght@300;400;500;700",
        "Inter": "Inter:wght@300;400;500;600;700;800;900",
        "Orbitron": "Orbitron:wght@400;500;600;700;800;900",
        "Space Grotesk": "Space+Grotesk:wght@300;400;500;600;700",
        "Cinzel": "Cinzel:wght@400;500;600;700;800;900",
        "Playfair Display": "Playfair+Display:wght@400;500;600;700;800;900",
        "Lora": "Lora:wght@400;500;600;700",
        "Cormorant Garamond": "Cormorant+Garamond:wght@300;400;500;600;700",
        "EB Garamond": "EB+Garamond:wght@400;500;600;700;800",
        "Oswald": "Oswald:wght@200;300;400;500;600;700",
        "Lato": "Lato:wght@300;400;700;900",
        "Bangers": "Bangers",
        "Roboto Condensed": "Roboto+Condensed:wght@300;400;700",
        "Uncial Antiqua": "Uncial+Antiqua",
        "Share Tech Mono": "Share+Tech+Mono",
        "Special Elite": "Special+Elite",
        "Ma Shan Zheng": "Ma+Shan+Zheng",
        "Rajdhani": "Rajdhani:wght@300;400;500;600;700",
        "Exo 2": "Exo+2:wght@400;500;600;700;800;900",
        "Titillium Web": "Titillium+Web:wght@300;400;600;700;900",
        "UnifrakturMaguntia": "UnifrakturMaguntia",
    }

    families = []
    for font in sorted(fonts_needed):
        config = font_configs.get(font, font.replace(" ", "+"))
        families.append(f"family={config}")

    if not families:
        return ""

    return "https://fonts.googleapis.com/css2?" + "&".join(families) + "&display=swap"


# ============================================================================
# HTML Builders (same as v3, now using dynamic CSS variables)
# ============================================================================

def build_hero_stats(entities: list[dict]) -> str:
    by_type = {}
    for e in entities:
        by_type[e.get("type", "character")] = by_type.get(e.get("type", "character"), 0) + 1
    items = []
    for sid, label in [("character", "Characters"), ("faction", "Factions"),
                        ("location", "Locations"), ("creature", "Beings"), ("event", "Events")]:
        c = by_type.get(sid, 0)
        if c > 0:
            items.append(
                f'<div class="hero-stat"><div class="stat-number" data-count="{c}">0</div>'
                f'<div class="stat-label">{label}</div></div>'
            )
    if not items:
        items.append(
            f'<div class="hero-stat"><div class="stat-number" data-count="{len(entities)}">0</div>'
            f'<div class="stat-label">Total Entities</div></div>'
        )
    return "".join(items)


def build_quick_nav(available_pages: set) -> str:
    items = []
    for pid, icon, label in QUICK_NAV_ITEMS:
        if pid in available_pages:
            items.append(
                f'<div class="quick-nav-item" data-page="{pid}">'
                f'<span class="qni-icon">{icon}</span>{label}</div>'
            )
    return "".join(items)


def build_entity_cards(entities: list[dict], entity_types: list[str] | None = None) -> str:
    filtered = entities
    if entity_types:
        filtered = [e for e in entities if e.get("type") in entity_types]
    if not filtered:
        return ""

    grouped: dict[str, list[dict]] = {}
    for e in filtered:
        t = e.get("type", "character")
        grouped.setdefault(t, []).append(e)

    sections = []
    for etype, items in grouped.items():
        label = TYPE_LABELS.get(etype, etype.title())
        cards = []
        for ent in items:
            name = esc(ent.get("name", "Unknown"))
            cf = ent.get("confidence", "medium")
            badge = conf_badge(cf)
            attrs = ent.get("attributes", {})

            display_fields = {
                "character": ["affiliation", "rank", "abilities", "personality", "status"],
                "faction": ["type", "leader", "territory", "alignment", "philosophy"],
                "location": ["type", "climate", "significance", "parent_location"],
                "creature": ["species", "habitat", "danger_level", "abilities"],
                "event": ["date", "location", "significance", "outcome"],
                "item": ["type", "owner", "abilities", "significance"],
            }
            attr_rows = []
            for field in display_fields.get(etype, []):
                val = attrs.get(field, "")
                if val:
                    if isinstance(val, list):
                        val = ", ".join(str(v) for v in val)
                    attr_rows.append(
                        f'<span class="attr"><strong>{field}:</strong> {esc(str(val))}</span>'
                    )
            attr_html = ""
            if attr_rows:
                attr_html = '<div class="entity-attrs">' + "".join(attr_rows) + "</div>"

            evidence = ent.get("source_evidence", [])
            ev_html = ""
            if evidence:
                ev_html = (
                    f'<details class="evidence"><summary>📖 Source</summary>'
                    f'<blockquote>{esc(evidence[0][:180])}</blockquote></details>'
                )

            eid = esc(ent.get("id", ""))
            cards.append(
                f'<article class="entity-card reveal-target {etype} confidence-{cf}" '
                f'id="entity-{eid}" data-entity-id="{eid}">'
                f'<div class="card-header"><h3>{name}{badge}</h3>'
                f'<span class="entity-type-label">{etype}</span></div>'
                f'{attr_html}{ev_html}</article>'
            )

        sections.append(
            f'<section class="entity-group" id="group-{etype}">'
            f'<h3 class="group-title">{TYPE_ICONS.get(etype, "📄")} {label} '
            f'<span class="count">({len(items)})</span></h3>'
            f'<div class="entity-grid">{"".join(cards)}</div>'
            f'</section>'
        )
    return "".join(sections)


def build_timeline_page(timeline: dict) -> str:
    epochs = timeline.get("epochs", [])
    events = timeline.get("events", [])
    if not events:
        return ""

    era_btns = '<button class="era-filter-btn active" data-era="all">All Eras</button>\n'
    for era in epochs:
        era_btns += (
            f'<button class="era-filter-btn" data-era="{esc(era.get("id", ""))}">'
            f'{esc(era.get("name", ""))}</button>\n'
        )

    cards = ""
    for evt in events:
        eid = esc(evt.get("id", ""))
        ename = esc(evt.get("name", "Unnamed"))
        edesc = esc(evt.get("description", "")[:200])
        era_id = esc(evt.get("era", ""))
        offset = evt.get("relative_offset_years")
        is_main = "true" if evt.get("participants") and len(evt.get("participants", [])) > 0 else "false"
        conflict = "true" if evt.get("contradiction_flag") else "false"
        loc = esc(str(evt.get("location", "")))
        tlabel = f"≈{offset}y" if offset else f"Seq #{evt.get('sequence_order', 0)}"

        cards += (
            f'<div class="timeline-event-card reveal-target {"contradiction" if conflict != "false" else ""}" '
            f'data-era="{era_id}" data-main="{is_main}" data-conflict="{conflict}" '
            f'data-location="{loc}" data-year="{tlabel}" id="event-{eid}">'
            f'<div class="timeline-dot"></div>'
            f'<div class="event-content"><span class="event-time-label">{tlabel}</span>'
            f'<h4>{ename}</h4><p>{edesc}</p></div></div>'
        )

    return (
        f'<section id="page-timeline" class="page" data-page="timeline">'
        f'<div class="timeline-section">'
        f'<div class="section-header"><h2>⏳ Chronicles</h2>'
        f'<p class="section-description">The story\'s timeline — from first cause to final echo.</p></div>'
        f'<div class="timeline-controls">'
        f'<button id="timeline-zoom-in" class="btn btn-ghost" title="Zoom in">🔍+</button>'
        f'<button id="timeline-zoom-out" class="btn btn-ghost" title="Zoom out">🔍−</button>'
        f'<button id="timeline-reset" class="btn btn-ghost" title="Reset">↺ Reset</button>'
        f'<label><input type="checkbox" id="timeline-main-only"> Main only</label>'
        f'</div>'
        f'<div class="era-filter-bar">{era_btns}</div>'
        f'<div class="timeline-container" id="timeline-container">'
        f'<div class="timeline-track">{cards}</div></div></div></section>'
    )


def build_relations_page(entities: list[dict], relationships: list[dict]) -> str:
    """Build a pure-text relations page — each relationship rendered as a readable sentence."""
    if len(relationships) < 2:
        return ""

    name_map = {}
    for e in entities:
        name_map[e.get("id", "")] = e.get("name", "Unknown")

    # Relation type → natural-language template
    # Each template has {src} and {tgt} placeholders
    RELATION_PHRASES = {
        "romantic": ("{src} 与 {tgt} 彼此深爱", "{src} and {tgt} are lovers"),
        "sibling": ("{src} 是 {tgt} 的血亲手足", "{src} is the sibling of {tgt}"),
        "parent_child": ("{src} 是 {tgt} 的父母", "{src} is the parent of {tgt}"),
        "master_apprentice": ("{src} 是 {tgt} 的师父", "{src} is the master of {tgt}"),
        "enmity": ("{src} 与 {tgt} 互为仇敌", "{src} and {tgt} are sworn enemies"),
        "ally": ("{src} 是 {tgt} 的盟友", "{src} is the ally of {tgt}"),
        "allegiance": ("{src} 效忠于 {tgt}", "{src} serves {tgt}"),
        "blood_bond": ("{src} 与 {tgt} 血脉相连", "{src} and {tgt} share a blood bond"),
        "creator_creation": ("{src} 创造了 {tgt}", "{src} created {tgt}"),
        "possessor_possessed": ("{src} 持有 {tgt}", "{src} possesses {tgt}"),
        "mentor": ("{src} 是 {tgt} 的引路人", "{src} mentors {tgt}"),
    }

    # Detect language for bilingual output
    def _cn_ratio(s):
        cjk = sum(1 for ch in s if '一' <= ch <= '鿿')
        return cjk / max(len(s), 1)

    text_items = ""
    for rel in relationships:
        src_name = name_map.get(rel.get("source", ""), rel.get("source", "?"))
        tgt_name = name_map.get(rel.get("target", ""), rel.get("target", "?"))
        rel_type = rel.get("relation_type", "ally")
        meta = RELATION_META.get(rel_type, ("🔗", "related to", "#888"))
        icon, label, color = meta
        confidence = rel.get("confidence", "medium")

        # Build natural-language sentence
        phrases = RELATION_PHRASES.get(rel_type, ("{src} 与 {tgt} 相关联", "{src} is related to {tgt}"))
        cn_phrase, en_phrase = phrases if isinstance(phrases, tuple) else (phrases, phrases)

        # Pick CN or EN based on name content
        use_cn = _cn_ratio(src_name + tgt_name) > 0.3
        sentence = cn_phrase if use_cn else en_phrase
        sentence = sentence.replace("{src}", f"<strong>{esc(src_name)}</strong>")
        sentence = sentence.replace("{tgt}", f"<strong>{esc(tgt_name)}</strong>")

        # Evidence as a subtle footnote
        evidence = rel.get("evidence", "")
        ev_html = ""
        if evidence:
            ev_html = f'<span class="rel-footnote"> — {esc(str(evidence)[:180])}</span>'

        # Confidence indicator for low-confidence entries
        conf_marker = ""
        if confidence == "low":
            conf_marker = ' <sup class="rel-tentative">[推测]</sup>'

        text_items += (
            f'<p class="rel-sentence reveal-target confidence-{confidence}">'
            f'{icon} {sentence}{conf_marker}{ev_html}'
            f'</p>'
        )

    # Build a compact legend showing relationship types with counts
    type_counts = {}
    for rel in relationships:
        rt = rel.get("relation_type", "ally")
        type_counts[rt] = type_counts.get(rt, 0) + 1

    legend_items = ""
    for rt, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        meta = RELATION_META.get(rt, ("🔗", rt.replace("_", " ").title(), "#888"))
        legend_items += (
            f'<span class="legend-text-tag">'
            f'{meta[0]} {meta[1]} ({count})</span>'
        )

    return (
        f'<section id="page-relations" class="page" data-page="relations">'
        f'<div class="section">'
        f'<div class="section-header"><h2>🕸️ Web of Ties</h2>'
        f'<p class="section-description">{len(relationships)} threads connecting the souls of this world.</p></div>'
        f'<div class="rel-legend-text">{legend_items}</div>'
        f'<div class="rel-text-list">{text_items}</div>'
        f'</div></section>'
    )


def build_factions_page(entities: list[dict]) -> str:
    html = build_entity_cards(entities, entity_types=["faction"])
    if not html:
        return ""
    return (
        f'<section id="page-factions" class="page" data-page="factions">'
        f'<div class="section">'
        f'<div class="section-header"><h2>🏛️ Factions & Powers</h2>'
        f'<p class="section-description">The organizations, empires, and forces that shape history.</p></div>'
        f'{html}</div></section>'
    )


def build_beings_page(entities: list[dict]) -> str:
    html = build_entity_cards(entities, entity_types=["creature"])
    if not html:
        return ""
    return (
        f'<section id="page-beings" class="page" data-page="beings">'
        f'<div class="section">'
        f'<div class="section-header"><h2>🐉 Beings & Creatures</h2>'
        f'<p class="section-description">From mythic beasts to alien species — the lifeforms of this universe.</p></div>'
        f'{html}</div></section>'
    )


def build_interactive_page(entities: list[dict]) -> str:
    mysteries = [e for e in entities if e.get("confidence") == "low"]
    if len(mysteries) < 1:
        return ""

    mystery_cards = ""
    for m in mysteries[:6]:
        name = esc(m.get("name", "?"))
        desc = esc(str(m.get("attributes", {}).get("description",
                    m.get("attributes", {}).get("significance", "")))[:120]
                   or "A mystery yet to be unraveled.")
        evidence = m.get("source_evidence", [""])[0][:150] if m.get("source_evidence") else ""
        mystery_cards += (
            f'<div class="entity-card reveal-target confidence-low">'
            f'<div class="card-header"><h3>🔮 {name}</h3><span class="entity-type-label">mystery</span></div>'
            f'<p style="font-size:0.875rem;color:var(--nv-color-text-secondary)">{desc}</p>'
            f'{"".join([f"<blockquote style=\"margin-top:8px;font-size:0.8rem;opacity:0.7\">{esc(evidence)}</blockquote>"]) if evidence else ""}'
            f'</div>'
        )

    return (
        f'<section id="page-interactive" class="page" data-page="interactive">'
        f'<div class="section">'
        f'<div class="section-header"><h2>🔮 Mysteries & Whispers</h2>'
        f'<p class="section-description">Unanswered questions and threads of fate woven into this world.</p></div>'
        f'<div class="entity-grid">{"".join(mystery_cards) if mystery_cards else "<p class=\"empty-state\">No mysteries flagged — all entities have medium+ confidence.</p>"}</div>'
        f'</div></section>'
    )


def build_design_rationale_footer(design: dict) -> str:
    """Build the design rationale section for the page footer."""
    rationale = design.get("generation_rationale", {})
    return (
        f'<footer class="design-rationale-footer">'
        f'<div class="rationale-inner">'
        f'<h3>💡 设计理念 · Design Rationale</h3>'
        f'<p>🎨 {esc(rationale.get("color_from", ""))}</p>'
        f'<p>🔤 {esc(rationale.get("font_from", ""))}</p>'
        f'<p>🖼️ {esc(rationale.get("texture_from", ""))}</p>'
        f'<p class="design-concept">「{esc(rationale.get("design_concept", ""))}」</p>'
        f'<p style="margin-top:16px;font-size:0.7rem;opacity:0.5;text-align:center;">'
        f'Design: {esc(design.get("design_name", ""))} · '
        f'Generated by Novelverse Forge Visual Genome Engine · '
        f'<span style="font-family:monospace">{esc(design.get("design_id", "")[:8])}</span>'
        f'</p>'
        f'</div></footer>'
    )


# ============================================================================
# Main Generator
# ============================================================================

def generate_html(world_data: dict, design: dict,
                  images_dir: Path | None = None,
                  custom_template: Path | None = None) -> str:
    """Generate a complete HTML page with dynamic styling from design scheme."""
    metadata = world_data.get("metadata", {})
    entities = world_data.get("entities", [])
    relationships = world_data.get("relationships", [])
    timeline = world_data.get("timeline", {})

    title = esc(metadata.get("title", "World Bible"))
    title_short = esc(title[:30] + ("…" if len(title) > 30 else ""))
    author = esc(metadata.get("author", "Unknown"))
    genre = esc(metadata.get("genre", ""))
    summary = esc(metadata.get("summary", ""))

    # Load template and base CSS
    html = read_text(custom_template or DEFAULT_TEMPLATE)
    if not html:
        print("[ERROR] No template found.", file=sys.stderr)
        sys.exit(1)

    base_css = read_text(BASE_CSS_FILE)

    # Generate dynamic CSS from design scheme
    dynamic_css = generate_dynamic_css(design)

    # Load and concatenate JS modules
    js_parts = []
    for jsf in JS_MODULES:
        c = read_text(jsf)
        if c:
            js_parts.append(f"// === {jsf.name} ===\n{c}")
    inline_js = "\n\n".join(js_parts)

    # Build all page content
    entities_all = build_entity_cards(entities)
    factions_page = build_factions_page(entities)
    beings_page = build_beings_page(entities)
    timeline_page = build_timeline_page(timeline)
    relations_page = build_relations_page(entities, relationships)
    interactive_page = build_interactive_page(entities)

    # Determine available pages
    has_timeline = bool(timeline_page)
    has_characters = bool(entities_all)
    has_factions = bool(factions_page)
    has_beings = bool(beings_page)
    has_relations = bool(relations_page)
    has_interactive = bool(interactive_page)

    available_pages = {"overview"}
    if has_timeline:
        available_pages.add("timeline")
    if has_characters:
        available_pages.add("characters")
    if has_factions:
        available_pages.add("factions")
    if has_beings:
        available_pages.add("beings")
    if has_relations:
        available_pages.add("relations")
    if has_interactive:
        available_pages.add("interactive")

    # Build page content
    hero_stats = build_hero_stats(entities)
    quick_nav = build_quick_nav(available_pages)

    # Navigation conditional links
    nav_timeline = '<a href="#timeline" data-page="timeline">时间线</a>' if has_timeline else ""
    nav_relations = '<a href="#relations" data-page="relations">关系网</a>' if has_relations else ""
    nav_interactive = '<a href="#interactive" data-page="interactive">互动</a>' if has_interactive else ""

    # Slim WORLD_DATA for JS
    slim_entities = []
    for ent in entities:
        slim_entities.append({
            "id": ent.get("id", ""), "name": ent.get("name", ""),
            "type": ent.get("type", ""), "confidence": ent.get("confidence", "medium"),
            "attributes": ent.get("attributes", {}),
            "aliases": ent.get("aliases", []), "mention_count": ent.get("mention_count", 1),
            "first_mention": ent.get("first_mention"),
            "source_evidence": ent.get("source_evidence", []),
        })

    world_data_js = json.dumps({
        "metadata": metadata, "entities": slim_entities,
        "relationships": relationships, "timeline": timeline,
    }, ensure_ascii=False)

    image_assets_js = "{}"
    if images_dir and images_dir.exists():
        imgs = {}
        for f in images_dir.iterdir():
            if f.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
                imgs[f.name] = _b64_image(f)
        if imgs:
            image_assets_js = json.dumps(imgs, ensure_ascii=False)

    # Design rationale footer
    design_footer = build_design_rationale_footer(design)

    # Google Fonts URL
    google_fonts_url = generate_google_fonts_url(design)

    # --- Template substitution ---
    subs = {
        "PAGE_TITLE": title,
        "PAGE_TITLE_SHORT": title_short,
        "PAGE_AUTHOR": author,
        "PAGE_GENRE": genre,
        "PAGE_SUMMARY": summary,
        "STYLE_NAME": "dynamic",
        "DESIGN_NAME": design.get("design_name", "Custom Design"),
        "DESIGN_ID": design.get("design_id", ""),
        "GOOGLE_FONTS_URL": google_fonts_url,
        "BASE_CSS": base_css,
        "DYNAMIC_CSS": dynamic_css,
        "INLINE_JS": inline_js,
        "WORLD_DATA_JSON": world_data_js,
        "IMAGE_ASSETS_JSON": image_assets_js,
        # Hero
        "HERO_STATS": hero_stats,
        "QUICK_NAV": quick_nav,
        # Pages
        "ENTITIES_ALL": entities_all,
        "PAGE_FACTIONS": factions_page,
        "PAGE_BEINGS": beings_page,
        "PAGE_TIMELINE": timeline_page,
        "PAGE_RELATIONS": relations_page,
        "PAGE_INTERACTIVE": interactive_page,
        # Nav links
        "NAV_TIMELINE": nav_timeline,
        "NAV_FACTIONS": '<a href="#factions" data-page="factions">派别</a>' if has_factions else "",
        "NAV_BEINGS": '<a href="#beings" data-page="beings">生物</a>' if has_beings else "",
        "NAV_RELATIONS": nav_relations,
        "NAV_INTERACTIVE": nav_interactive,
        # Search HTML
        "SEARCH_HTML": "",
        # Design rationale footer
        "DESIGN_RATIONALE_FOOTER": design_footer,
        # Legacy template vars
        "THEME_CSS": "",  # No longer used — dynamic CSS replaces it
        "DARK_CSS": "",   # No longer used — dark mode is handled by base.css + dynamic overrides
        "ENTITIES_HTML": "",
        "TIMELINE_HTML": "",
        "GRAPH_HTML": "",
        "TIMELINE_SECTION": "",
        "GRAPH_SECTION": "",
        "TIMELINE_NAV": "",
        "GRAPH_NAV": "",
    }

    for key, value in subs.items():
        html = html.replace("{{" + key + "}}", value)

    return html


def _b64_image(path: Path) -> str:
    """Base64 encode an image file."""
    data = path.read_bytes()
    if not data:
        return ""
    ext = path.suffix.lower()
    mimes = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
    }
    mime = mimes.get(ext, "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate dynamic-design world bible HTML v4."
    )
    parser.add_argument("--input", "-i", type=Path, required=True,
                       help="WORLD_DATA JSON file")
    parser.add_argument("--design", "-d", type=Path, required=True,
                       help="Design scheme JSON file (from visual_genome.py)")
    parser.add_argument("--output", "-o", type=Path,
                       default=Path("world_bible.html"), help="Output HTML")
    parser.add_argument("--images-dir", type=Path,
                       help="Images to base64-inline")
    parser.add_argument("--template", "-t", type=Path,
                       help="Custom template")
    args = parser.parse_args()

    wd = json.loads(args.input.read_text(encoding="utf-8"))
    design = json.loads(args.design.read_text(encoding="utf-8"))

    out = generate_html(wd, design, images_dir=args.images_dir,
                        custom_template=args.template)
    args.output.write_text(out, encoding="utf-8")
    kb = len(out.encode("utf-8")) / 1024
    print(f"[OK] World bible v4 (Dynamic Genome) generated: "
          f"{args.output} ({kb:.1f} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
