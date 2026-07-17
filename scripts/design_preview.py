#!/usr/bin/env python3
"""
design_preview.py — Design Preview Generator for Novelverse Forge
==================================================================
Generates a compact, visual preview of a design scheme so users can
review and approve the design before full HTML generation.

Input:
    Design scheme JSON (from visual_genome.py)

Output:
    A self-contained HTML preview card showing:
    - Color palette swatches
    - Typography samples (heading/body/decorative)
    - Texture effect preview
    - Card component sample
    - Motion effect preview (if applicable)
    - Design rationale summary

Usage:
    python design_preview.py --design design.json > preview.html
    python design_preview.py --design design.json --output preview.html
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ============================================================================
# CSS Generation from Design Scheme
# ============================================================================

def generate_preview_css(design: dict) -> str:
    """Generate CSS for the preview card from the design scheme."""
    c = design["color"]
    t = design["typography"]
    s = design["space"]
    tx = design["texture"]
    m = design["motion"]

    css = f"""
    :root {{
      --pv-primary: {c["primary"]};
      --pv-secondary: {c["secondary"]};
      --pv-accent: {c["accent"]};
      --pv-bg-start: {c["bg_start"]};
      --pv-bg-end: {c["bg_end"]};
      --pv-text-primary: {c["text_primary"]};
      --pv-text-secondary: {c["text_secondary"]};
      --pv-surface: {c["surface"]};
      --pv-surface-border: {c["surface_border"]};
      --pv-glow: {c["glow"]};
      --pv-heading-font: '{t["heading_font"]}', {get_fallback(t["heading_font"])};
      --pv-body-font: '{t["body_font"]}', {get_fallback(t["body_font"])};
      --pv-decorative-font: '{t.get("decorative_font", t["heading_font"])}', {get_fallback(t.get("decorative_font", t["heading_font"]))};
      --pv-heading-weight: {t["heading_weight"]};
      --pv-body-weight: {t["body_weight"]};
      --pv-heading-ls: {t["heading_letter_spacing"]}em;
      --pv-radius-card: {s["radius_card"]};
      --pv-radius-md: {s["radius_medium"]};
      --pv-gap: {s["gap_medium"]};
      --pv-padding: {s["card_padding"]};
      --pv-shadow-blur: {design["lighting"]["shadow_blur"]};
      --pv-shadow-color: {design["lighting"]["shadow_color"]};
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: var(--pv-body-font);
      font-weight: var(--pv-body-weight);
      background: linear-gradient(135deg, var(--pv-bg-start), var(--pv-bg-end));
      color: var(--pv-text-primary);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      line-height: {design["typography"]["line_height"]};
    }}

    .preview-card {{
      max-width: 800px;
      width: 100%;
      background: var(--pv-surface);
      border: 1px solid var(--pv-surface-border);
      border-radius: var(--pv-radius-card);
      padding: 40px;
      box-shadow: 0 4px var(--pv-shadow-blur) var(--pv-shadow-color);
    }}

    .preview-header {{
      text-align: center;
      margin-bottom: 32px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--pv-surface-border);
    }}

    .preview-header h1 {{
      font-family: var(--pv-heading-font);
      font-weight: var(--pv-heading-weight);
      font-size: {round(t["scale_ratio"]**3 * 16)}px;
      letter-spacing: var(--pv-heading-ls);
      color: var(--pv-primary);
      margin-bottom: 8px;
    }}

    .preview-header .design-name {{
      font-family: var(--pv-decorative-font);
      font-size: 14px;
      color: var(--pv-text-secondary);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    .section-title {{
      font-family: var(--pv-heading-font);
      font-weight: {t["heading_weight"]};
      font-size: 13px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--pv-text-secondary);
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--pv-surface-border);
    }}

    /* Palette swatches */
    .palette-row {{
      display: flex;
      gap: 12px;
      margin-bottom: 28px;
      flex-wrap: wrap;
    }}

    .swatch {{
      flex: 1;
      min-width: 80px;
      height: 64px;
      border-radius: 8px;
      position: relative;
      cursor: pointer;
      transition: transform 0.2s;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    .swatch:hover {{ transform: translateY(-4px) scale(1.05); }}
    .swatch .swatch-label {{
      position: absolute;
      bottom: -20px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 10px;
      font-family: monospace;
      color: var(--pv-text-secondary);
      white-space: nowrap;
    }}

    /* Typography samples */
    .type-samples {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-bottom: 28px;
    }}

    .type-sample-heading {{
      font-family: var(--pv-heading-font);
      font-weight: var(--pv-heading-weight);
      font-size: 24px;
      letter-spacing: var(--pv-heading-ls);
      color: var(--pv-primary);
    }}

    .type-sample-body {{
      font-family: var(--pv-body-font);
      font-weight: var(--pv-body-weight);
      font-size: 14px;
      color: var(--pv-text-primary);
      line-height: {design["typography"]["line_height"]};
    }}

    .type-sample-decorative {{
      font-family: var(--pv-decorative-font);
      font-size: 16px;
      color: var(--pv-text-secondary);
      letter-spacing: 0.05em;
    }}

    /* Texture preview */
    .texture-preview {{
      height: 80px;
      border-radius: var(--pv-radius-card);
      margin-bottom: 28px;
      position: relative;
      overflow: hidden;
      border: 1px solid var(--pv-surface-border);
      {generate_texture_css(tx)}
    }}

    .texture-preview .texture-label {{
      position: absolute;
      bottom: 8px;
      right: 12px;
      font-size: 11px;
      color: var(--pv-text-secondary);
      background: var(--pv-surface);
      padding: 2px 10px;
      border-radius: 4px;
    }}

    /* Component preview */
    .component-preview {{
      display: flex;
      gap: 16px;
      margin-bottom: 28px;
      flex-wrap: wrap;
    }}

    .sample-card {{
      flex: 1;
      min-width: 200px;
      background: var(--pv-surface);
      border: 1px solid var(--pv-surface-border);
      border-radius: var(--pv-radius-md);
      padding: var(--pv-padding);
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}

    .sample-card .card-title {{
      font-family: var(--pv-heading-font);
      font-weight: var(--pv-heading-weight);
      font-size: 16px;
      color: var(--pv-primary);
      margin-bottom: 8px;
    }}

    .sample-card .card-text {{
      font-size: 13px;
      color: var(--pv-text-secondary);
      line-height: 1.5;
    }}

    .sample-button {{
      display: inline-block;
      padding: 10px 24px;
      border-radius: 24px;
      background: var(--pv-primary);
      color: {c["bg_start"]};
      font-weight: 600;
      font-size: 13px;
      margin-top: 12px;
      cursor: pointer;
      border: none;
      transition: transform 0.2s, box-shadow 0.2s;
      box-shadow: 0 2px 12px {c["glow"]}44;
    }}
    .sample-button:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 20px {c["glow"]}66;
    }}

    /* Motion indicator */
    .motion-indicator {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 28px;
    }}

    .motion-dot {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--pv-accent);
      {generate_motion_css(m)}
    }}

    .motion-label {{
      font-size: 13px;
      color: var(--pv-text-secondary);
    }}

    /* Rationale */
    .rationale-section {{
      background: {c["bg_end"]};
      border-radius: var(--pv-radius-md);
      padding: 20px;
      margin-bottom: 16px;
    }}

    .rationale-section p {{
      font-size: 13px;
      color: var(--pv-text-secondary);
      line-height: 1.7;
      margin-bottom: 6px;
    }}

    .rationale-section .rationale-title {{
      font-family: var(--pv-heading-font);
      font-weight: var(--pv-heading-weight);
      font-size: 14px;
      color: var(--pv-primary);
      margin-bottom: 12px;
    }}

    .rationale-section .concept {{
      font-family: var(--pv-decorative-font);
      font-size: 15px;
      color: var(--pv-text-primary);
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--pv-surface-border);
      text-align: center;
    }}

    /* Mood tags */
    .mood-tags {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 28px;
    }}

    .mood-tag {{
      padding: 4px 14px;
      border-radius: 20px;
      background: var(--pv-surface);
      border: 1px solid var(--pv-surface-border);
      font-size: 12px;
      color: var(--pv-text-secondary);
    }}

    .mood-tag.active {{
      background: var(--pv-primary);
      color: {c["bg_start"]};
      border-color: var(--pv-primary);
      font-weight: 600;
    }}

    /* Responsive */
    @media (max-width: 600px) {{
      .preview-card {{ padding: 20px; }}
      .component-preview {{ flex-direction: column; }}
    }}

    /* Google Font import will be injected in <head> */
    """

    return css


def get_fallback(font_name: str) -> str:
    """Get system font fallback stack for a given font."""
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


def generate_texture_css(texture: dict) -> str:
    """Generate CSS for texture preview."""
    tx_type = texture["type"]
    intensity = texture["intensity"]

    if tx_type == "grain":
        opacity = intensity * 0.15
        return f"""
      background-color: var(--pv-bg-start);
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='{opacity}'/%3E%3C/svg%3E");
    """
    elif tx_type == "grid":
        opacity = intensity * 0.12
        return f"""
      background-color: var(--pv-bg-start);
      background-image:
        linear-gradient(rgba(255,255,255,{opacity}) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,{opacity}) 1px, transparent 1px);
      background-size: 30px 30px;
    """
    elif tx_type == "stars":
        return f"""
      background-color: var(--pv-bg-start);
      background-image:
        radial-gradient(1px 1px at 15% 25%, rgba(255,255,255,0.8), transparent),
        radial-gradient(1px 1px at 35% 65%, rgba(255,255,255,0.5), transparent),
        radial-gradient(1.5px 1.5px at 55% 15%, rgba(255,255,255,0.6), transparent),
        radial-gradient(1px 1px at 75% 55%, rgba(255,255,255,0.4), transparent),
        radial-gradient(1px 1px at 85% 35%, rgba(255,255,255,0.3), transparent);
    """
    elif tx_type == "neon":
        return f"""
      background-color: var(--pv-bg-start);
      background-image:
        linear-gradient(0deg, transparent 30%, var(--pv-glow)22 31%, transparent 32%),
        linear-gradient(0deg, transparent 60%, var(--pv-glow)11 61%, transparent 62%),
        linear-gradient(0deg, transparent 85%, var(--pv-glow)18 86%, transparent 87%);
      background-size: 100% 100%;
    """
    elif tx_type == "paper":
        opacity = intensity * 0.05
        return f"""
      background-color: var(--pv-bg-start);
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='{opacity}'/%3E%3C/svg%3E");
    """
    elif tx_type == "metal":
        return f"""
      background: linear-gradient(135deg,
        var(--pv-surface) 0%, var(--pv-bg-end) 30%, var(--pv-surface) 50%,
        var(--pv-bg-start) 70%, var(--pv-surface) 100%);
    """
    elif tx_type == "ink_wash":
        return f"""
      background-color: var(--pv-bg-start);
      background:
        radial-gradient(ellipse at 30% 20%, var(--pv-primary)08 0%, transparent 50%),
        radial-gradient(ellipse at 70% 60%, var(--pv-secondary)05 0%, transparent 50%),
        radial-gradient(ellipse at 50% 80%, var(--pv-accent)04 0%, transparent 40%);
    """
    elif tx_type == "shadow":
        return f"""
      background:
        radial-gradient(ellipse at 50% 0%, var(--pv-bg-start) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 50%, var(--pv-secondary)08 0%, transparent 50%),
        radial-gradient(ellipse at 20% 80%, var(--pv-primary)06 0%, transparent 40%);
      background-color: var(--pv-bg-end);
    """
    elif tx_type == "crystal":
        return f"""
      background:
        linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 50%),
        linear-gradient(225deg, var(--pv-accent)08 0%, transparent 50%);
      background-color: var(--pv-bg-start);
    """
    elif tx_type == "stone":
        return f"""
      background-color: var(--pv-bg-start);
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.4' numOctaves='5' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.12'/%3E%3C/svg%3E");
    """
    elif tx_type == "wave":
        return f"""
      background-color: var(--pv-bg-start);
      background:
        repeating-linear-gradient(0deg, transparent, transparent 20px, var(--pv-primary)08 20px, var(--pv-primary)08 21px);
    """
    elif tx_type == "fire":
        return f"""
      background:
        radial-gradient(ellipse at 50% 100%, var(--pv-accent)33 0%, transparent 60%),
        radial-gradient(ellipse at 30% 80%, var(--pv-primary)22 0%, transparent 40%);
      background-color: var(--pv-bg-start);
    """
    elif tx_type == "mist":
        return f"""
      background:
        radial-gradient(ellipse at 30% 40%, var(--pv-surface) 0%, transparent 40%),
        radial-gradient(ellipse at 70% 60%, var(--pv-bg-end) 0%, transparent 40%);
      background-color: var(--pv-bg-start);
    """
    else:  # smooth
        return f"""
      background: linear-gradient(180deg, var(--pv-bg-start), var(--pv-bg-end));
    """


def generate_motion_css(motion: dict) -> str:
    """Generate CSS animation for the motion indicator dot."""
    mtype = motion["type"]
    speed = motion["speed"]

    if mtype == "static" or speed < 0.05:
        return ""

    duration = max(0.5, 4.0 - speed * 3.5)  # Map speed 0→4s, 1→0.5s

    if mtype == "pulse":
        return f"animation: pv-pulse {duration}s ease-in-out infinite;"
    elif mtype == "wave":
        return f"animation: pv-wave {duration * 2}s ease-in-out infinite;"
    elif mtype == "drift":
        return f"animation: pv-drift {duration * 4}s linear infinite;"
    elif mtype == "rapid":
        return f"animation: pv-pulse {duration}s ease-in-out infinite;"
    else:
        return ""


def round(val: float, decimals: int = 0) -> float:
    return float(f"{val:.{decimals}f}")


# ============================================================================
# Google Font URL Generation
# ============================================================================

def generate_google_fonts_url(design: dict) -> str:
    """Generate Google Fonts import URL from the design's font selections."""
    t = design["typography"]
    fonts_needed = set()

    for font_key in ["heading_font", "body_font", "decorative_font"]:
        font = t.get(font_key, "")
        if font:
            fonts_needed.add(font)

    # Map fonts to their Google Fonts family names and weights
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
# Main Preview Generator
# ============================================================================

def generate_preview_html(design: dict) -> str:
    """Generate a complete HTML preview page for a design scheme."""
    c = design["color"]
    t = design["typography"]
    tx = design["texture"]
    m = design["motion"]
    mood = design["mood"]
    rationale = design["generation_rationale"]

    google_fonts_url = generate_google_fonts_url(design)
    css = generate_preview_css(design)

    # Animation keyframes
    keyframes = """
    @keyframes pv-pulse {
      0%, 100% { transform: scale(1); opacity: 0.8; box-shadow: 0 0 4px var(--pv-accent); }
      50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 16px var(--pv-accent); }
    }
    @keyframes pv-wave {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-8px); }
    }
    @keyframes pv-drift {
      0% { transform: translateX(0); }
      100% { transform: translateX(16px); }
    }
    """

    # Mood tags
    all_moods = ["史诗感", "压抑", "轻快", "诡谲", "浪漫", "冷峻", "温暖", "悲壮"]
    mood_tags_html = ""
    current_mood = mood["emotional_tone"]
    for mood_label in all_moods:
        cls = "active" if mood_label == current_mood else ""
        mood_tags_html += f'<span class="mood-tag {cls}">{mood_label}</span>'

    # Texture animation class
    motion_class = ""
    if m["type"] != "static" and m["speed"] > 0.05:
        motion_class = "motion-dot-animated"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Design Preview — {design["design_name"]}</title>
  {f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="{google_fonts_url}" rel="stylesheet">' if google_fonts_url else ''}
  <style>
    {css}
    {keyframes}
  </style>
</head>
<body>
  <div class="preview-card">

    <!-- Header -->
    <div class="preview-header">
      <h1>{design["design_name"]}</h1>
      <p class="design-name">Design Scheme Preview · Visual Genome v1</p>
    </div>

    <!-- Mood Tags -->
    <div class="section-title">🎭 情绪基调 Emotional Tone</div>
    <div class="mood-tags">
      {mood_tags_html}
    </div>

    <!-- Color Palette -->
    <div class="section-title">🎨 调色板 Color Palette</div>
    <div class="palette-row">
"""

    # Palette swatches
    palette = c["palette"]
    palette_roles = ["主色", "辅色", "强调", "背景1", "背景2"]
    for i, color_hex in enumerate(palette[:5]):
        role = palette_roles[i] if i < len(palette_roles) else ""
        html += f"""      <div class="swatch" style="background:{color_hex}" title="{role}: {color_hex}">
        <span class="swatch-label">{color_hex}</span>
      </div>
"""

    # Additional color info
    html += f"""
    </div>
    <div style="display:flex;gap:12px;font-size:11px;color:var(--pv-text-secondary);margin-bottom:28px;flex-wrap:wrap;">
      <span>主色 Primary: {c["primary"]}</span>
      <span>辅色 Secondary: {c["secondary"]}</span>
      <span>强调 Accent: {c["accent"]}</span>
      <span>发光 Glow: {c["glow"]}</span>
      <span>暖度 Warmth: {c["warmth"]:+.2f}</span>
      <span>饱和度 Sat: {c["saturation"]:.2f}</span>
      <span>明度 Bri: {c["brightness"]:.2f}</span>
    </div>

    <!-- Typography -->
    <div class="section-title">🔤 字体 Typography</div>
    <div class="type-samples">
      <div class="type-sample-heading">山川异域 · 风月同天</div>
      <div class="type-sample-body">世间万物皆有灵，一花一世界，一叶一菩提。The quick brown fox jumps over the lazy dog. 天地玄黄，宇宙洪荒。</div>
      <div class="type-sample-decorative">✦ {design["design_name"]} ✦ Design Genome System ✦</div>
    </div>
    <div style="font-size:11px;color:var(--pv-text-secondary);margin-bottom:28px;">
      <span>标题: {t["heading_font"]} w{t["heading_weight"]} · </span>
      <span>正文: {t["body_font"]} w{t["body_weight"]} · </span>
      <span>字距: {t["heading_letter_spacing"]}em · </span>
      <span>比例: {t["scale_ratio"]}</span>
    </div>

    <!-- Texture -->
    <div class="section-title">🖼️ 纹理 Texture — {tx["type"]} (强度 {tx["intensity"]:.2f})</div>
    <div class="texture-preview">
      <span class="texture-label">{tx["type"]} · {tx["description"]}</span>
    </div>

    <!-- Component Samples -->
    <div class="section-title">🧩 组件 Components</div>
    <div class="component-preview">
      <div class="sample-card">
        <div class="card-title">角色 / Character</div>
        <div class="card-text">这是一张角色卡片的示例，展示标题、描述文字和按钮的外观效果。</div>
        <button class="sample-button">查看详情 →</button>
      </div>
      <div class="sample-card">
        <div class="card-title">事件 / Event</div>
        <div class="card-text">事件卡片展示时间线中的关键节点。悬停时会微微上浮并发出柔和光晕。</div>
        <button class="sample-button">展开时间线 →</button>
      </div>
    </div>

    <!-- Motion -->
    <div class="section-title">✨ 动效 Motion — {m["type"]} (速度 {m["speed"]:.2f})</div>
    <div class="motion-indicator">
      <div class="motion-dot {motion_class}"></div>
      <span class="motion-label">
        类型: {m["type"]} ·
        视差: {'是' if m["has_parallax"] else '否'} ·
        光晕脉冲: {'是' if m["has_glow_pulse"] else '否'}
      </span>
    </div>

    <!-- Design Rationale -->
    <div class="section-title">💡 设计理念 Design Rationale</div>
    <div class="rationale-section">
      <div class="rationale-title">设计依据</div>
      <p>🎨 {rationale.get("color_from", "")}</p>
      <p>🔤 {rationale.get("font_from", "")}</p>
      <p>🖼️ {rationale.get("texture_from", "")}</p>
      <div class="concept">「{rationale.get("design_concept", "")}」</div>
    </div>

    <!-- Metadata -->
    <div style="text-align:center;font-size:10px;color:var(--pv-text-secondary);margin-top:24px;opacity:0.5;">
      design_id: {design["design_id"][:8]}... · generated by Novelverse Forge Visual Genome Engine
    </div>

  </div>
</body>
</html>"""

    return html


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate a design preview page from a visual design scheme."
    )
    parser.add_argument("--design", "-d", type=Path, required=True,
                       help="Design scheme JSON file (from visual_genome.py)")
    parser.add_argument("--output", "-o", type=Path,
                       help="Output preview HTML file (stdout if omitted)")
    args = parser.parse_args()

    design = json.loads(args.design.read_text(encoding="utf-8"))
    html = generate_preview_html(design)

    if args.output:
        args.output.write_text(html, encoding="utf-8")
        print(f"[OK] Design preview written to {args.output}", file=sys.stderr)
    else:
        print(html)


if __name__ == "__main__":
    main()
