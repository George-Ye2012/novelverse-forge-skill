#!/usr/bin/env python3
"""
visual_genome.py — Visual Genome Extraction Engine for Novelverse Forge
========================================================================
Extracts "visual genes" from novel text and generates a complete, unique
visual design scheme. No preset templates — every design is derived from
the text itself.

Input:
    Novel full text + entity extraction results (entities, relationships, timeline)

Output:
    Visual design scheme JSON with color, typography, space, texture, lighting,
    motion, mood, and generation rationale.

Dependencies:
    Python 3.9+ (stdlib only — no external packages required)

Usage:
    python visual_genome.py --text novel.txt --entities entities.json > design.json
    python visual_genome.py --text novel.txt --entities entities.json --output design.json
"""

import argparse
import json
import math
import re
import sys
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


# ============================================================================
# Color Lexicon — word → (hex, hue_angle, warmth)
# ============================================================================

COLOR_LEXICON_CN: dict[str, tuple[str, float, float]] = {
    # Reds (hue ~0°, warm)
    "血红": ("#8B0000", 0, 0.9), "赤红": ("#8B0000", 0, 0.9),
    "暗红": ("#4A0A0A", 0, 0.7), "深红": ("#4A0A0A", 0, 0.7),
    "绯红": ("#CC3333", 5, 0.8), "朱红": ("#CC3333", 5, 0.8),
    "嫣红": ("#E87080", 350, 0.7), "桃红": ("#E87080", 350, 0.7),
    "玫瑰红": ("#C04060", 345, 0.6), "品红": ("#AA006A", 330, 0.4),
    "洋红": ("#AA006A", 330, 0.4),
    # Golds / Yellows (hue ~40-50°, warm)
    "暗金": ("#C9A050", 42, 0.8), "古铜": ("#C9A050", 42, 0.8),
    "鎏金": ("#D4A830", 45, 0.9), "灿金": ("#D4A830", 45, 0.9),
    "淡金": ("#D4C090", 43, 0.5), "沙金": ("#D4C090", 43, 0.5),
    "琥珀": ("#C97030", 35, 0.7), "金棕": ("#C97030", 35, 0.7),
    "明黄": ("#E8C040", 50, 0.7), "亮黄": ("#E8C040", 50, 0.7),
    "橘黄": ("#E08040", 30, 0.8), "暖橙": ("#E08040", 30, 0.8),
    # Blacks / Darks (neutral)
    "墨色": ("#1A1A1A", 0, 0.0), "漆黑": ("#1A1A1A", 0, 0.0),
    "炭灰": ("#3A3A3A", 0, -0.1), "石墨": ("#3A3A3A", 0, -0.1),
    # Blues (hue ~210-240°, cold)
    "青金": ("#1A3A6A", 220, -0.7), "宝蓝": ("#1A3A6A", 220, -0.7),
    "天蓝": ("#4080C0", 210, -0.5), "蔚蓝": ("#4080C0", 210, -0.5),
    "海蓝": ("#0A2A5A", 215, -0.8), "深蓝": ("#0A2A5A", 215, -0.8),
    "青蓝": ("#0088BB", 200, -0.6), "天青": ("#0088BB", 200, -0.6),
    "靛蓝": ("#2A4070", 230, -0.7), "靛青": ("#2A4070", 230, -0.7),
    "藏蓝": ("#1A2A4A", 225, -0.8), "海军蓝": ("#1A2A4A", 225, -0.8),
    "钴蓝": ("#2040A0", 225, -0.7), "湖蓝": ("#40A0C0", 195, -0.4),
    "水蓝": ("#40A0C0", 195, -0.4),
    # Greens (hue ~120-160°, cold)
    "翠绿": ("#2A6B5A", 160, -0.4), "碧色": ("#2A6B5A", 160, -0.4),
    "墨绿": ("#1A3A2A", 140, -0.5), "苍翠": ("#1A3A2A", 140, -0.5),
    "嫩绿": ("#80C060", 100, 0.3), "新绿": ("#80C060", 100, 0.3),
    "薄荷": ("#80C0A0", 150, -0.3), "青碧": ("#80C0A0", 150, -0.3),
    # Purples (hue ~270-300°, cold)
    "紫罗兰": ("#4A1A5A", 280, -0.6), "绛紫": ("#4A1A5A", 280, -0.6),
    "暗紫": ("#2A0A3A", 275, -0.8), "幽紫": ("#2A0A3A", 275, -0.8),
    "淡紫": ("#A080C0", 270, -0.3), "薰衣草": ("#A080C0", 270, -0.3),
    # Whites / Lights (neutral to warm)
    "苍白": ("#E8E0D8", 40, 0.0), "月白": ("#E8E0D8", 40, 0.0),
    "灰白": ("#D0D0D0", 0, -0.2), "素白": ("#D0D0D0", 0, -0.2),
    "雪白": ("#F0F0F8", 240, -0.3), "霜白": ("#F0F0F8", 240, -0.3),
    "乳白": ("#F5F0E0", 45, 0.3), "象牙白": ("#F5F0E0", 45, 0.3),
    # Browns / Earth (warm)
    "锈红": ("#8A4A2A", 20, 0.6), "赭石": ("#8A4A2A", 20, 0.6),
    "砖红": ("#A05030", 15, 0.6), "土红": ("#A05030", 15, 0.6),
    "沙色": ("#D4B896", 35, 0.4), "沙漠色": ("#D4B896", 35, 0.4),
    "巧克力": ("#604030", 20, 0.5), "可可": ("#604030", 20, 0.5),
    "米色": ("#F0E0C8", 40, 0.3), "杏色": ("#F0E0C8", 40, 0.3),
    # Cool neutrals
    "苍青": ("#6A8A9A", 200, -0.7), "霜色": ("#6A8A9A", 200, -0.7),
    "银灰": ("#708090", 210, -0.3), "铁灰": ("#708090", 210, -0.3),
    # Pinks
    "桃粉": ("#EEB0B0", 5, 0.6), "樱色": ("#EEB0B0", 5, 0.6),
    "荧光粉": ("#FF40A0", 330, 0.3),
    # Neons
    "荧光绿": ("#40FF40", 120, -0.2), "霓虹橙": ("#FF6020", 20, 0.6),
    # Misc
    "烟灰": ("#8A8A8A", 0, -0.1), "雾色": ("#8A8A8A", 0, -0.1),
}

COLOR_LEXICON_EN: dict[str, tuple[str, float, float]] = {
    "blood red": ("#8B0000", 0, 0.9), "crimson": ("#8B0000", 0, 0.9),
    "scarlet": ("#CC3333", 5, 0.8), "vermillion": ("#CC3333", 5, 0.8),
    "gold": ("#D4A830", 45, 0.9), "golden": ("#D4A830", 45, 0.9),
    "silver": ("#C0C0C0", 0, -0.2), "argent": ("#C0C0C0", 0, -0.2),
    "bronze": ("#CD7F32", 35, 0.6), "copper": ("#CD7F32", 35, 0.6),
    "emerald": ("#2A6B5A", 160, -0.4), "sapphire": ("#1A3A6A", 220, -0.7),
    "ruby": ("#8B0000", 0, 0.9), "amethyst": ("#6A3A8A", 280, -0.5),
    "obsidian": ("#1A1A1A", 0, 0.0), "onyx": ("#1A1A1A", 0, 0.0),
    "ivory": ("#F5F0E0", 45, 0.3), "ebony": ("#2A1A0A", 30, 0.3),
    "pearl": ("#F0F0F0", 0, 0.0), "coral": ("#E87060", 10, 0.7),
    "teal": ("#208080", 180, -0.5), "magenta": ("#AA006A", 330, 0.4),
    "cyan": ("#00AAAA", 180, -0.6), "neon blue": ("#4060FF", 230, -0.5),
    "neon pink": ("#FF40A0", 330, 0.3), "holographic": ("#80C0FF", 210, -0.4),
    "chrome": ("#C0C8D0", 210, -0.2), "brass": ("#B5A642", 50, 0.6),
    "violet": ("#4A1A5A", 280, -0.6), "indigo": ("#2A4070", 230, -0.7),
    "maroon": ("#4A0A0A", 0, 0.7), "navy": ("#1A2A4A", 225, -0.8),
    "olive": ("#4A5A2A", 80, -0.2), "jade": ("#2A6B5A", 160, -0.4),
    "cobalt": ("#2040A0", 225, -0.7), "rust": ("#8A4A2A", 20, 0.6),
    "amber": ("#C97030", 35, 0.7), "charcoal": ("#3A3A3A", 0, -0.1),
    "slate": ("#708090", 210, -0.3), "sand": ("#D4B896", 35, 0.4),
    "mint": ("#80C0A0", 150, -0.3), "lavender": ("#A080C0", 270, -0.3),
    "rose": ("#C04060", 345, 0.6), "cherry": ("#CC3333", 5, 0.8),
    "midnight": ("#0A1A2A", 220, -0.9), "azure": ("#4080C0", 210, -0.5),
    "cerulean": ("#2080C0", 205, -0.6), "turquoise": ("#30A0A0", 180, -0.4),
    "carmine": ("#8B0000", 0, 0.9), "burgundy": ("#4A0A1A", 350, 0.5),
    "sepia": ("#604020", 30, 0.4), "mahogany": ("#4A1A0A", 20, 0.5),
    "alabaster": ("#F0F0E8", 50, 0.1), "porcelain": ("#F8F8F0", 50, 0.1),
    "cream": ("#F8F0E0", 45, 0.3), "champagne": ("#F0E0C0", 45, 0.3),
    "wine": ("#4A0A20", 345, 0.5), "plum": ("#3A1A3A", 300, -0.3),
    "lilac": ("#B0A0C0", 270, -0.2), "periwinkle": ("#8090C0", 230, -0.4),
    "crimson": ("#8B0000", 0, 0.9),
}


# ============================================================================
# Texture Lexicon — word → texture_type
# ============================================================================

TEXTURE_LEXICON_CN: dict[str, str] = {
    "光滑": "smooth", "琉璃": "smooth", "镜面": "smooth", "冰面": "smooth",
    "抛光": "smooth", "瓷器": "smooth", "陶瓷": "smooth",
    "粗糙": "grain", "沙砾": "grain", "风化": "grain", "磨砂": "grain",
    "沙尘": "grain", "粉末": "grain",
    "纸张": "paper", "羊皮": "paper", "布帛": "paper", "绢帛": "paper",
    "宣纸": "paper", "信纸": "paper", "书页": "paper",
    "金属": "metal", "钢铁": "metal", "黄铜": "metal", "铁锈": "metal",
    "合金": "metal", "青铜": "metal", "白银": "metal", "铝": "metal",
    "水墨": "ink_wash", "晕染": "ink_wash", "墨迹": "ink_wash",
    "泼墨": "ink_wash", "墨韵": "ink_wash", "毛笔": "ink_wash",
    "霓虹": "neon", "荧光": "neon", "光带": "neon", "全息": "neon",
    "激光": "neon", "灯管": "neon", "光污染": "neon",
    "网格": "grid", "电路": "grid", "矩阵": "grid", "数据": "grid",
    "代码": "grid", "扫描线": "grid", "像素": "grid",
    "星云": "stars", "星尘": "stars", "深空": "stars", "星河": "stars",
    "宇宙": "stars", "星空": "stars", "星辰": "stars",
    "暗影": "shadow", "幽暗": "shadow", "迷雾": "shadow", "雾霭": "shadow",
    "阴霾": "shadow", "黑雾": "shadow",
    "波纹": "wave", "水纹": "wave", "流动": "wave", "涟漪": "wave",
    "潮汐": "wave", "水波": "wave",
    "石纹": "stone", "岩石": "stone", "大理石": "stone", "花岗岩": "stone",
    "石壁": "stone", "石板": "stone",
    "织物": "fabric", "丝绸": "fabric", "锦缎": "fabric", "天鹅绒": "fabric",
    "布纹": "fabric", "绸缎": "fabric",
    "木质": "wood", "木纹": "wood", "竹纹": "wood",
    "晶体": "crystal", "水晶": "crystal", "冰晶": "crystal", "钻石": "crystal",
    "冰霜": "crystal", "玻璃": "crystal",
    "火焰": "fire", "熔岩": "fire", "余烬": "fire", "烈焰": "fire",
    "雾气": "mist", "烟": "mist", "蒸汽": "mist",
    "皮革": "leather", "皮质": "leather",
}

TEXTURE_LEXICON_EN: dict[str, str] = {
    "smooth": "smooth", "glass": "smooth", "polished": "smooth", "mirror": "smooth",
    "rough": "grain", "grainy": "grain", "gritty": "grain", "sand": "grain",
    "paper": "paper", "parchment": "paper", "vellum": "paper",
    "metal": "metal", "steel": "metal", "iron": "metal", "brass": "metal",
    "chrome": "metal", "alloy": "metal",
    "ink": "ink_wash", "watercolor": "ink_wash", "wash": "ink_wash", "brush": "ink_wash",
    "neon": "neon", "glow": "neon", "hologram": "neon", "laser": "neon",
    "grid": "grid", "circuit": "grid", "matrix": "grid", "wireframe": "grid",
    "digital": "grid",
    "nebula": "stars", "stardust": "stars", "void": "stars", "cosmic": "stars",
    "galaxy": "stars", "space": "stars",
    "shadow": "shadow", "dark": "shadow", "misty": "shadow", "fog": "shadow",
    "gloom": "shadow",
    "wave": "wave", "ripple": "wave", "water": "wave", "flowing": "wave",
    "tide": "wave",
    "stone": "stone", "rock": "stone", "marble": "stone", "granite": "stone",
    "fabric": "fabric", "silk": "fabric", "velvet": "fabric", "cloth": "fabric",
    "wood": "wood", "timber": "wood", "bamboo": "wood",
    "crystal": "crystal", "ice": "crystal", "diamond": "crystal", "frost": "crystal",
    "fire": "fire", "lava": "fire", "ember": "fire", "flame": "fire",
}


# ============================================================================
# Era Keywords → Font Family
# ============================================================================

ERA_FONT_MAP: dict[str, dict[str, Any]] = {
    "ancient_cn": {
        "keywords_cn": ["古代", "帝国", "王朝", "宫廷", "江湖", "战国", "三国",
                       "唐朝", "宋朝", "明朝", "清朝", "秦", "汉", "唐", "宋", "明"],
        "keywords_en": ["ancient", "empire", "dynasty", "kingdom", "medieval", "feudal"],
        "heading": "Noto Serif SC",
        "body": "Noto Sans SC",
        "decorative": "Ma Shan Zheng",
        "category": "serif",
    },
    "modern": {
        "keywords_cn": ["现代", "都市", "当代", "现实", "日常", "城市"],
        "keywords_en": ["modern", "urban", "contemporary", "realistic", "everyday"],
        "heading": "Inter",
        "body": "Inter",
        "decorative": "",
        "category": "sans-serif",
    },
    "future": {
        "keywords_cn": ["未来", "科幻", "赛博", "星舰", "太空", "银河", "星际",
                       "宇宙飞船", "空间站", "机器人"],
        "keywords_en": ["future", "sci-fi", "cyber", "starship", "space", "galaxy",
                       "interstellar", "spaceship", "robot"],
        "heading": "Orbitron",
        "body": "Space Grotesk",
        "decorative": "Share Tech Mono",
        "category": "tech-sans",
    },
    "fantasy": {
        "keywords_cn": ["奇幻", "魔法", "传说", "神话", "龙", "精灵", "矮人",
                       "兽人", "法师", "巫师", "剑与魔法"],
        "keywords_en": ["fantasy", "magic", "myth", "legend", "dragon", "elf",
                       "dwarf", "orc", "wizard", "sword and sorcery"],
        "heading": "Cinzel",
        "body": "Lora",
        "decorative": "Uncial Antiqua",
        "category": "decorative-serif",
    },
    "xianxia": {
        "keywords_cn": ["仙侠", "修仙", "修真", "水墨", "道", "禅", "灵气",
                       "金丹", "元婴", "渡劫", "飞升", "宗门"],
        "keywords_en": ["cultivation", "tao", "zen", "ink", "immortal", "xianxia"],
        "heading": "Noto Serif SC",
        "body": "Noto Sans SC",
        "decorative": "Ma Shan Zheng",
        "category": "calligraphic",
    },
    "steampunk": {
        "keywords_cn": ["蒸汽", "维多利亚", "齿轮", "工业革命", "发条", "飞艇"],
        "keywords_en": ["steam", "victorian", "gear", "industrial revolution",
                       "clockwork", "airship"],
        "heading": "Playfair Display",
        "body": "Lora",
        "decorative": "Special Elite",
        "category": "vintage-serif",
    },
    "wasteland": {
        "keywords_cn": ["废土", "末日", "荒漠", "核后", "辐射", "废墟"],
        "keywords_en": ["wasteland", "apocalypse", "post-apocalyptic", "desert",
                       "nuclear", "ruins"],
        "heading": "Bangers",
        "body": "Roboto Condensed",
        "decorative": "",
        "category": "rough-sans",
    },
    "noir": {
        "keywords_cn": ["侦探", "黑色", "悬疑", "推理", "犯罪", "谋杀"],
        "keywords_en": ["detective", "noir", "mystery", "suspense", "crime", "murder"],
        "heading": "Oswald",
        "body": "Lato",
        "decorative": "",
        "category": "compact-sans",
    },
    "renaissance": {
        "keywords_cn": ["文艺复兴", "巴洛克", "启蒙", "古典"],
        "keywords_en": ["renaissance", "baroque", "enlightenment", "classical"],
        "heading": "Playfair Display",
        "body": "Cormorant Garamond",
        "decorative": "EB Garamond",
        "category": "oldstyle-serif",
    },
}


# ============================================================================
# Mood → Design Parameters
# ============================================================================

MOOD_PARAMS: dict[str, dict[str, float]] = {
    "史诗感": {"saturation": 0.60, "brightness": 0.50, "contrast": 0.85,
              "motion_speed": 0.50, "radius_base": 0.35, "visual_density": 0.45,
              "heading_weight": 800, "letter_spacing": 0.03, "scale_ratio": 1.25},
    "压抑":   {"saturation": 0.30, "brightness": 0.30, "contrast": 0.30,
              "motion_speed": 0.20, "radius_base": 0.55, "visual_density": 0.70,
              "heading_weight": 700, "letter_spacing": -0.01, "scale_ratio": 1.15},
    "轻快":   {"saturation": 0.80, "brightness": 0.80, "contrast": 0.55,
              "motion_speed": 0.80, "radius_base": 0.85, "visual_density": 0.30,
              "heading_weight": 500, "letter_spacing": 0.01, "scale_ratio": 1.30},
    "诡谲":   {"saturation": 0.40, "brightness": 0.40, "contrast": 0.50,
              "motion_speed": 0.30, "radius_base": 0.55, "visual_density": 0.55,
              "heading_weight": 600, "letter_spacing": 0.02, "scale_ratio": 1.20},
    "浪漫":   {"saturation": 0.70, "brightness": 0.70, "contrast": 0.35,
              "motion_speed": 0.60, "radius_base": 0.85, "visual_density": 0.40,
              "heading_weight": 400, "letter_spacing": 0.01, "scale_ratio": 1.30},
    "冷峻":   {"saturation": 0.20, "brightness": 0.50, "contrast": 0.80,
              "motion_speed": 0.10, "radius_base": 0.20, "visual_density": 0.25,
              "heading_weight": 700, "letter_spacing": 0.01, "scale_ratio": 1.20},
    "温暖":   {"saturation": 0.70, "brightness": 0.70, "contrast": 0.50,
              "motion_speed": 0.50, "radius_base": 0.55, "visual_density": 0.40,
              "heading_weight": 500, "letter_spacing": 0.00, "scale_ratio": 1.25},
    "悲壮":   {"saturation": 0.50, "brightness": 0.30, "contrast": 0.80,
              "motion_speed": 0.20, "radius_base": 0.35, "visual_density": 0.50,
              "heading_weight": 900, "letter_spacing": 0.04, "scale_ratio": 1.25},
    "神秘":   {"saturation": 0.50, "brightness": 0.40, "contrast": 0.55,
              "motion_speed": 0.25, "radius_base": 0.55, "visual_density": 0.50,
              "heading_weight": 600, "letter_spacing": 0.02, "scale_ratio": 1.20},
    "紧张":   {"saturation": 0.40, "brightness": 0.45, "contrast": 0.75,
              "motion_speed": 0.70, "radius_base": 0.25, "visual_density": 0.35,
              "heading_weight": 700, "letter_spacing": -0.01, "scale_ratio": 1.15},
    "宁静":   {"saturation": 0.50, "brightness": 0.75, "contrast": 0.35,
              "motion_speed": 0.15, "radius_base": 0.55, "visual_density": 0.20,
              "heading_weight": 400, "letter_spacing": 0.02, "scale_ratio": 1.30},
    "狂野":   {"saturation": 0.85, "brightness": 0.60, "contrast": 0.80,
              "motion_speed": 0.85, "radius_base": 0.50, "visual_density": 0.65,
              "heading_weight": 800, "letter_spacing": 0.02, "scale_ratio": 1.33},
    "怀旧":   {"saturation": 0.45, "brightness": 0.60, "contrast": 0.35,
              "motion_speed": 0.30, "radius_base": 0.55, "visual_density": 0.45,
              "heading_weight": 500, "letter_spacing": 0.01, "scale_ratio": 1.20},
}

# English mood aliases → Chinese mood keys
MOOD_ALIASES_EN: dict[str, str] = {
    "epic": "史诗感", "grand": "史诗感", "majestic": "史诗感",
    "oppressive": "压抑", "dark": "压抑", "gloomy": "压抑", "depressing": "压抑",
    "light": "轻快", "cheerful": "轻快", "uplifting": "轻快", "bright": "轻快",
    "uncanny": "诡谲", "eerie": "诡谲", "strange": "诡谲", "weird": "诡谲",
    "romantic": "浪漫", "loving": "浪漫", "passionate": "浪漫",
    "stoic": "冷峻", "cold": "冷峻", "detached": "冷峻", "clinical": "冷峻",
    "warm": "温暖", "cozy": "温暖", "heartwarming": "温暖",
    "tragic": "悲壮", "sad": "悲壮", "sorrowful": "悲壮", "heroic tragedy": "悲壮",
    "mysterious": "神秘", "enigmatic": "神秘", "puzzling": "神秘",
    "tense": "紧张", "suspenseful": "紧张", "anxious": "紧张", "thrilling": "紧张",
    "serene": "宁静", "peaceful": "宁静", "calm": "宁静", "tranquil": "宁静",
    "wild": "狂野", "chaotic": "狂野", "frenzied": "狂野",
    "nostalgic": "怀旧", "wistful": "怀旧", "melancholic": "怀旧",
}


# ============================================================================
# Scene → Texture Mapping
# ============================================================================

SCENE_TEXTURE_MAP: dict[str, tuple[str, str]] = {
    "castle": ("stone", "shadow"), "dungeon": ("stone", "shadow"),
    "fortress": ("stone", "shadow"), "citadel": ("stone", "shadow"),
    "城堡": ("stone", "shadow"), "地牢": ("stone", "shadow"),
    "古堡": ("stone", "shadow"), "要塞": ("stone", "shadow"),
    "future_city": ("grid", "neon"), "cyberpunk": ("grid", "neon"),
    "neon_street": ("grid", "neon"),
    "未来城市": ("grid", "neon"), "赛博": ("grid", "neon"),
    "霓虹街": ("grid", "neon"),
    "forest": ("paper", "grain"), "jungle": ("paper", "grain"),
    "woods": ("paper", "grain"), "rainforest": ("paper", "grain"),
    "森林": ("paper", "grain"), "山林": ("paper", "grain"),
    "雨林": ("paper", "grain"), "丛林": ("paper", "grain"),
    "starship": ("stars", "metal"), "space_station": ("stars", "metal"),
    "spacecraft": ("stars", "metal"),
    "星舰": ("stars", "metal"), "太空站": ("stars", "metal"),
    "飞船": ("stars", "metal"),
    "wasteland": ("grain", "stone"), "desert": ("grain", "stone"),
    "ruins": ("grain", "stone"),
    "废土": ("grain", "stone"), "荒漠": ("grain", "stone"),
    "废墟": ("grain", "stone"),
    "palace": ("fabric", "metal"), "court": ("fabric", "metal"),
    "throne_room": ("fabric", "metal"),
    "宫廷": ("fabric", "metal"), "殿堂": ("fabric", "metal"),
    "皇宫": ("fabric", "metal"),
    "rivers_and_lakes": ("ink_wash", "paper"),
    "mountains": ("ink_wash", "paper"), "bamboo": ("ink_wash", "paper"),
    "江湖": ("ink_wash", "paper"), "山水": ("ink_wash", "paper"),
    "竹林": ("ink_wash", "paper"),
    "deep_sea": ("wave", "shadow"), "underwater": ("wave", "shadow"),
    "ocean_abyss": ("wave", "shadow"),
    "深海": ("wave", "shadow"), "海底": ("wave", "shadow"),
    "水下": ("wave", "shadow"),
    "temple": ("wood", "paper"), "monastery": ("wood", "paper"),
    "shrine": ("wood", "paper"),
    "寺院": ("wood", "paper"), "道观": ("wood", "paper"),
    "庙宇": ("wood", "paper"),
    "laboratory": ("smooth", "grid"), "research": ("smooth", "grid"),
    "实验室": ("smooth", "grid"), "研究所": ("smooth", "grid"),
    "battlefield": ("fire", "grain"), "warzone": ("fire", "grain"),
    "战场": ("fire", "grain"), "前线": ("fire", "grain"),
    "cloud": ("mist", "crystal"), "sky_city": ("mist", "crystal"),
    "云端": ("mist", "crystal"), "天空城": ("mist", "crystal"),
    "underground": ("stone", "shadow"), "cave": ("stone", "shadow"),
    "地下": ("stone", "shadow"), "洞穴": ("stone", "shadow"),
    "academy": ("paper", "wood"), "library": ("paper", "wood"),
    "学院": ("paper", "wood"), "图书馆": ("paper", "wood"),
    "tundra": ("crystal", "smooth"), "snowfield": ("crystal", "smooth"),
    "arctic": ("crystal", "smooth"),
    "冰原": ("crystal", "smooth"), "雪域": ("crystal", "smooth"),
    "极地": ("crystal", "smooth"),
    "volcano": ("fire", "stone"), "lava": ("fire", "stone"),
    "火山": ("fire", "stone"), "岩浆": ("fire", "stone"),
}


# ============================================================================
# Emotion → Motion Mapping
# ============================================================================

EMOTION_MOTION_MAP: dict[str, dict[str, Any]] = {
    "涌动": {"type": "wave", "speed": 0.4, "has_parallax": True, "has_glow_pulse": False},
    "流动": {"type": "wave", "speed": 0.4, "has_parallax": True, "has_glow_pulse": False},
    "潮汐": {"type": "wave", "speed": 0.4, "has_parallax": True, "has_glow_pulse": False},
    "flowing": {"type": "wave", "speed": 0.4, "has_parallax": True, "has_glow_pulse": False},
    "tide": {"type": "wave", "speed": 0.4, "has_parallax": True, "has_glow_pulse": False},
    "闪烁": {"type": "pulse", "speed": 0.5, "has_parallax": False, "has_glow_pulse": True},
    "幽光": {"type": "pulse", "speed": 0.5, "has_parallax": False, "has_glow_pulse": True},
    "星火": {"type": "pulse", "speed": 0.5, "has_parallax": False, "has_glow_pulse": True},
    "flicker": {"type": "pulse", "speed": 0.5, "has_parallax": False, "has_glow_pulse": True},
    "glow": {"type": "pulse", "speed": 0.5, "has_parallax": False, "has_glow_pulse": True},
    "飘渺": {"type": "drift", "speed": 0.2, "has_parallax": True, "has_glow_pulse": False},
    "漂浮": {"type": "drift", "speed": 0.2, "has_parallax": True, "has_glow_pulse": False},
    "云烟": {"type": "drift", "speed": 0.2, "has_parallax": True, "has_glow_pulse": False},
    "drift": {"type": "drift", "speed": 0.2, "has_parallax": True, "has_glow_pulse": False},
    "ethereal": {"type": "drift", "speed": 0.2, "has_parallax": True, "has_glow_pulse": False},
    "静止": {"type": "static", "speed": 0.0, "has_parallax": False, "has_glow_pulse": False},
    "永恒": {"type": "static", "speed": 0.0, "has_parallax": False, "has_glow_pulse": False},
    "凝固": {"type": "static", "speed": 0.0, "has_parallax": False, "has_glow_pulse": False},
    "still": {"type": "static", "speed": 0.0, "has_parallax": False, "has_glow_pulse": False},
    "timeless": {"type": "static", "speed": 0.0, "has_parallax": False, "has_glow_pulse": False},
    "紧张": {"type": "rapid", "speed": 0.8, "has_parallax": True, "has_glow_pulse": True},
    "急速": {"type": "rapid", "speed": 0.8, "has_parallax": True, "has_glow_pulse": True},
    "rapid": {"type": "rapid", "speed": 0.8, "has_parallax": True, "has_glow_pulse": True},
    "呼吸": {"type": "pulse", "speed": 0.3, "has_parallax": False, "has_glow_pulse": True},
    "脉动": {"type": "pulse", "speed": 0.3, "has_parallax": False, "has_glow_pulse": True},
    "breathing": {"type": "pulse", "speed": 0.3, "has_parallax": False, "has_glow_pulse": True},
}


# ============================================================================
# Mood Detection Keywords
# ============================================================================

MOOD_KEYWORDS_CN: dict[str, str] = {
    # 史诗感 keywords
    "史诗": "史诗感", "宏伟": "史诗感", "壮丽": "史诗感", "浩瀚": "史诗感",
    "传奇": "史诗感", "伟大": "史诗感", "宏大": "史诗感",
    # 压抑 keywords
    "压抑": "压抑", "绝望": "压抑", "窒息": "压抑", "灰暗": "压抑",
    "沉重": "压抑", "阴郁": "压抑", "痛苦": "压抑", "煎熬": "压抑",
    # 轻快 keywords
    "轻快": "轻快", "欢快": "轻快", "明朗": "轻快", "轻松": "轻快",
    "愉悦": "轻快", "活泼": "轻快", "阳光": "轻快",
    # 诡谲 keywords
    "诡异": "诡谲", "怪诞": "诡谲", "离奇": "诡谲", "诡秘": "诡谲",
    "不可名状": "诡谲", "怪奇": "诡谲",
    # 浪漫 keywords
    "浪漫": "浪漫", "温柔": "浪漫", "深情": "浪漫", "缠绵": "浪漫",
    "甜蜜": "浪漫", "心动": "浪漫",
    # 冷峻 keywords
    "冷峻": "冷峻", "冷漠": "冷峻", "冰冷": "冷峻", "理性": "冷峻",
    "冷静": "冷峻", "严酷": "冷峻", "残酷": "冷峻",
    # 温暖 keywords
    "温暖": "温暖", "温馨": "温暖", "柔和": "温暖", "治愈": "温暖",
    # 悲壮 keywords
    "悲壮": "悲壮", "牺牲": "悲壮", "壮烈": "悲壮", "慷慨": "悲壮",
    "悲凉": "悲壮", "苍凉": "悲壮",
    # 神秘 keywords
    "神秘": "神秘", "奥秘": "神秘", "未知": "神秘", "深邃": "神秘",
    # 紧张 keywords
    "紧张": "紧张", "紧迫": "紧张", "危机": "紧张", "惊险": "紧张",
    # 宁静 keywords
    "宁静": "宁静", "平静": "宁静", "安详": "宁静", "静谧": "宁静",
    # 狂野 keywords
    "狂野": "狂野", "狂暴": "狂野", "狂热": "狂野", "疯狂": "狂野",
    # 怀旧 keywords
    "怀旧": "怀旧", "回忆": "怀旧", "追忆": "怀旧", "往事": "怀旧",
}

MOOD_KEYWORDS_EN: dict[str, str] = {
    "epic": "史诗感", "grand": "史诗感", "majestic": "史诗感", "vast": "史诗感",
    "oppressive": "压抑", "despair": "压抑", "suffocating": "压抑", "gloomy": "压抑",
    "light": "轻快", "cheerful": "轻快", "bright": "轻快", "playful": "轻快",
    "uncanny": "诡谲", "eerie": "诡谲", "strange": "诡谲", "weird": "诡谲",
    "romantic": "浪漫", "tender": "浪漫", "loving": "浪漫", "passionate": "浪漫",
    "stoic": "冷峻", "cold": "冷峻", "detached": "冷峻", "clinical": "冷峻",
    "warm": "温暖", "cozy": "温暖", "gentle": "温暖",
    "tragic": "悲壮", "sorrowful": "悲壮", "heroic": "悲壮",
    "mysterious": "神秘", "enigmatic": "神秘", "unknown": "神秘",
    "tense": "紧张", "suspenseful": "紧张", "thrilling": "紧张",
    "serene": "宁静", "peaceful": "宁静", "calm": "宁静", "tranquil": "宁静",
    "wild": "狂野", "chaotic": "狂野", "frenzied": "狂野", "crazy": "狂野",
    "nostalgic": "怀旧", "wistful": "怀旧", "memory": "怀旧",
}


# ============================================================================
# Helper Functions
# ============================================================================

def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0,min(255,r)):02X}{max(0,min(255,g)):02X}{max(0,min(255,b)):02X}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    rn, gn, bn = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(rn, gn, bn), min(rn, gn, bn)
    l = (mx + mn) / 2
    if mx == mn:
        return (0, 0, l)
    d = mx - mn
    s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == rn:
        h = ((gn - bn) / d) % 6
    elif mx == gn:
        h = (bn - rn) / d + 2
    else:
        h = (rn - gn) / d + 4
    return (h * 60, s, l)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    h = h % 360
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    if h < 60: rn, gn, bn = c, x, 0
    elif h < 120: rn, gn, bn = x, c, 0
    elif h < 180: rn, gn, bn = 0, c, x
    elif h < 240: rn, gn, bn = 0, x, c
    elif h < 300: rn, gn, bn = x, 0, c
    else: rn, gn, bn = c, 0, x
    return (int((rn + m) * 255), int((gn + m) * 255), int((bn + m) * 255))


def adjust_hsl(hex_str: str, h_shift: float = 0, s_mult: float = 1.0,
               l_mult: float = 1.0) -> str:
    r, g, b = hex_to_rgb(hex_str)
    h, s, l = rgb_to_hsl(r, g, b)
    h = (h + h_shift) % 360
    s = clamp(s * s_mult)
    l = clamp(l * l_mult)
    nr, ng, nb = hsl_to_rgb(h, s, l)
    return rgb_to_hex(nr, ng, nb)


def detect_language(text: str) -> str:
    cjk_count = sum(1 for ch in text if "一" <= ch <= "鿿")
    total_chars = len(re.sub(r"\s", "", text))
    if total_chars == 0:
        return "en"
    return "zh" if (cjk_count / max(total_chars, 1)) > 0.15 else "en"


# ============================================================================
# Step 1: Extract Color Keywords
# ============================================================================

def extract_color_keywords(text: str, lang: str) -> list[dict]:
    """Scan text for color keywords from the lexicon and return matches."""
    results: list[dict] = []

    # Merge CN and EN lexicons for searching
    all_lexicon: dict[str, tuple[str, float, float]] = {}
    all_lexicon.update(COLOR_LEXICON_CN)
    all_lexicon.update(COLOR_LEXICON_EN)

    # Also search with partial matches for compound words
    for word, (hex_val, hue, warmth) in all_lexicon.items():
        # Exact match
        count = len(re.findall(re.escape(word), text, re.IGNORECASE))
        if count > 0:
            # Find first occurrence context
            pos = text.lower().find(word.lower())
            ctx_start = max(0, pos - 40)
            ctx_end = min(len(text), pos + len(word) + 40)
            context = text[ctx_start:ctx_end].strip()

            results.append({
                "word": word,
                "hex": hex_val,
                "hue": hue,
                "warmth": warmth,
                "count": count,
                "context": context[:120],
            })

    # Sort by frequency (descending)
    results.sort(key=lambda x: -x["count"])
    return results


# ============================================================================
# Step 2: Generate Color Palette
# ============================================================================

def generate_palette(color_hits: list[dict], mood_key: str) -> dict:
    """Generate a complete color palette from extracted color keywords and mood."""
    mood = MOOD_PARAMS.get(mood_key, MOOD_PARAMS["史诗感"])

    palette_hexes: list[str] = []
    total_warmth = 0.0

    if color_hits:
        # Take up to 5 most frequent, deduplicated by similar hue
        seen_hues: set[int] = set()
        for hit in color_hits:
            hue_bucket = int(hit["hue"] / 30) * 30  # bucket by 30° increments
            if hue_bucket not in seen_hues and len(palette_hexes) < 5:
                seen_hues.add(hue_bucket)
                palette_hexes.append(hit["hex"])
                total_warmth += hit["warmth"]
    else:
        # Default: generate from mood
        default_colors = {
            "史诗感": ["#C9A050", "#4A0A0A", "#1A2A4A", "#E8E0D8", "#8A4A2A"],
            "压抑": ["#1A1A1A", "#2A0A3A", "#4A0A0A", "#3A3A3A", "#1A3A2A"],
            "轻快": ["#E8C040", "#80C0A0", "#F0E0C8", "#EEB0B0", "#40A0C0"],
            "诡谲": ["#2A0A3A", "#1A3A2A", "#4A1A5A", "#8A4A2A", "#1A1A1A"],
            "浪漫": ["#C04060", "#EEB0B0", "#F0E0C8", "#A080C0", "#D4A830"],
            "冷峻": ["#1A2A4A", "#708090", "#6A8A9A", "#F0F0F8", "#3A3A3A"],
            "温暖": ["#E08040", "#D4A830", "#F0E0C8", "#C97030", "#A05030"],
            "悲壮": ["#4A0A0A", "#C9A050", "#1A1A1A", "#8A4A2A", "#2A0A3A"],
            "神秘": ["#2A0A3A", "#1A3A6A", "#4A1A5A", "#C9A050", "#1A1A1A"],
            "紧张": ["#8B0000", "#1A2A4A", "#3A3A3A", "#E08040", "#AA006A"],
            "宁静": ["#4080C0", "#F0E0C8", "#80C0A0", "#A080C0", "#E8E0D8"],
            "狂野": ["#8B0000", "#E08040", "#AA006A", "#FF40A0", "#1A1A1A"],
            "怀旧": ["#D4B896", "#604030", "#F0E0C8", "#C97030", "#8A4A2A"],
        }
        palette_hexes = default_colors.get(mood_key, default_colors["史诗感"])
        for hex_val in palette_hexes:
            for word, (h, hue, warmth) in COLOR_LEXICON_CN.items():
                if h == hex_val:
                    total_warmth += warmth
                    break

    avg_warmth = total_warmth / max(len(palette_hexes), 1)

    # Adjust palette colors by mood parameters
    adjusted = []
    for hex_val in palette_hexes:
        r, g, b = hex_to_rgb(hex_val)
        h, s, l = rgb_to_hsl(r, g, b)

        # Apply mood adjustments
        s = clamp(s * (0.5 + mood["saturation"]))
        l = clamp(l * (0.4 + mood["brightness"]))

        nr, ng, nb = hsl_to_rgb(h, s, l)
        adjusted.append(rgb_to_hex(nr, ng, nb))

    # Assign roles
    primary = adjusted[0]
    secondary = adjusted[1] if len(adjusted) > 1 else adjust_hsl(primary, 180, 1.0, 1.0)
    accent = adjusted[2] if len(adjusted) > 2 else adjust_hsl(primary, 60, 1.5, 1.0)

    # Generate background from palette
    bg_is_dark = mood["brightness"] < 0.55
    if bg_is_dark:
        bg_r, bg_g, bg_b = hex_to_rgb(adjusted[-1])
        bg_h, bg_s, bg_l = rgb_to_hsl(bg_r, bg_g, bg_b)
        bg_start = rgb_to_hex(*hsl_to_rgb(bg_h, clamp(bg_s * 0.8), 0.04))
        bg_end = rgb_to_hex(*hsl_to_rgb(bg_h, clamp(bg_s * 0.6), 0.10))
        text_primary = "#E8E8F0"
        text_secondary = "#A0A0B8"
        surface = rgb_to_hex(*hsl_to_rgb(bg_h, bg_s * 0.3, 0.10))
    else:
        bg_start = adjusted[-1] if len(adjusted) > 4 else "#F5F0E8"
        bg_end = adjust_hsl(bg_start, 0, 0.8, 1.1)
        text_primary = "#1A1A1A"
        text_secondary = "#5A5A5A"
        surface = adjust_hsl(bg_start, 0, 0.3, 1.05)

    surface_border = adjust_hsl(surface, 0, 0.5, 0.9)
    glow = adjust_hsl(accent, 0, 1.2, 0.8)

    return {
        "palette": adjusted[:5],
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "bg_start": bg_start,
        "bg_end": bg_end,
        "text_primary": text_primary,
        "text_secondary": text_secondary,
        "surface": surface,
        "surface_border": surface_border,
        "glow": glow,
        "warmth": round(clamp(avg_warmth, -1, 1), 2),
        "saturation": round(mood["saturation"], 2),
        "brightness": round(mood["brightness"], 2),
    }


# ============================================================================
# Step 3: Select Typography
# ============================================================================

def select_typography(text: str, lang: str, mood_key: str,
                       entities: list[dict]) -> dict:
    """Select fonts based on era detection, mood, and entity types."""
    mood = MOOD_PARAMS.get(mood_key, MOOD_PARAMS["史诗感"])

    # Score each era category by keyword frequency
    era_scores: dict[str, float] = defaultdict(float)
    text_lower = text.lower()

    for era_key, era_data in ERA_FONT_MAP.items():
        for kw in era_data.get("keywords_cn", []):
            era_scores[era_key] += text.count(kw) * 5.0
        for kw in era_data.get("keywords_en", []):
            era_scores[era_key] += text_lower.count(kw.lower()) * 3.0

    # Also scan entity types for era hints
    for entity in entities:
        etype = entity.get("type", "")
        attrs = entity.get("attributes", {})
        if etype == "faction":
            faction_type = attrs.get("type", "")
            if faction_type in ["sect", "clan"]:
                era_scores["xianxia"] += 2.0
            elif faction_type in ["kingdom", "empire"]:
                era_scores["ancient_cn" if lang == "zh" else "fantasy"] += 2.0

    # Pick the highest-scoring era, default to modern
    best_era = max(era_scores, key=lambda k: era_scores[k]) if any(era_scores.values()) else "modern"
    if era_scores.get(best_era, 0) < 1.0:
        best_era = "modern"

    era_data = ERA_FONT_MAP[best_era]
    heading_font = era_data["heading"]
    body_font = era_data["body"]
    decorative_font = era_data.get("decorative", "")

    # Adjust weights from mood
    heading_weight = int(mood["heading_weight"] * 100) * 100
    heading_weight = max(300, min(900, heading_weight))
    body_weight = 400 if mood["brightness"] > 0.6 else 500

    heading_ls = mood["letter_spacing"]
    body_ls = 0.005

    line_height = 1.6 + (mood["visual_density"] - 0.5) * 0.4
    scale_ratio = mood["scale_ratio"]

    return {
        "heading_font": heading_font,
        "body_font": body_font,
        "decorative_font": decorative_font,
        "heading_weight": heading_weight,
        "body_weight": body_weight,
        "heading_letter_spacing": round(heading_ls, 3),
        "body_letter_spacing": round(body_ls, 3),
        "line_height": round(line_height, 2),
        "scale_ratio": round(scale_ratio, 3),
        "era_detected": best_era,
    }


# ============================================================================
# Step 4: Select Texture
# ============================================================================

def select_texture(text: str, lang: str) -> dict:
    """Select texture type based on scene descriptions and texture keywords."""
    texture_scores: dict[str, float] = defaultdict(float)
    text_lower = text.lower()

    # Score from texture lexicon
    all_texture_lexicon: dict[str, str] = {}
    all_texture_lexicon.update(TEXTURE_LEXICON_CN)
    all_texture_lexicon.update(TEXTURE_LEXICON_EN)

    for word, texture_type in all_texture_lexicon.items():
        count = len(re.findall(re.escape(word), text, re.IGNORECASE))
        if count > 0:
            texture_scores[texture_type] += count * 3.0

    # Score from scene descriptions
    for scene_key, (t1, t2) in SCENE_TEXTURE_MAP.items():
        if scene_key in text_lower:
            texture_scores[t1] += 2.0
            texture_scores[t2] += 1.0

    # Sort and pick top
    sorted_textures = sorted(texture_scores.items(), key=lambda x: -x[1])

    if sorted_textures:
        primary_texture = sorted_textures[0][0]
        # Pick secondary if it's different and significant
        secondary = sorted_textures[1] if len(sorted_textures) > 1 else ("smooth", 0)
        if secondary[1] < sorted_textures[0][1] * 0.3:
            texture_type = primary_texture
            intensity = 0.3
        else:
            texture_type = primary_texture
            intensity = clamp(sorted_textures[0][1] / 15, 0.15, 0.8)
    else:
        texture_type = "smooth"
        intensity = 0.0

    # Texture descriptions for CSS generation
    descriptions = {
        "smooth": "Pure color with subtle gradient sheen",
        "grain": "Fine noise grain via SVG feTurbulence filter",
        "paper": "Subtle paper fiber texture with micro-imperfections",
        "metal": "Multi-angle metallic sheen gradients",
        "ink_wash": "Blurred radial gradients mimicking ink bleed",
        "neon": "Glowing light streaks and bloom effects",
        "grid": "Subtle geometric grid overlay",
        "stars": "Scattered luminous dots on dark field",
        "shadow": "Multi-layer radial darkening gradients",
        "wave": "Undulating gradient patterns",
        "stone": "Mottled surface with subtle cracks",
        "fabric": "Fine repeating weave pattern",
        "wood": "Linear streaked grain pattern",
        "crystal": "Sharp faceted gradient highlights",
        "fire": "Animated warm glow with upward motion",
        "mist": "Soft blurred gradient layers",
        "leather": "Dark gradient with subtle surface grain",
    }

    return {
        "type": texture_type,
        "intensity": round(intensity, 2),
        "description": descriptions.get(texture_type, "Smooth gradient"),
    }


# ============================================================================
# Step 5: Select Lighting
# ============================================================================

def select_lighting(mood_key: str, bg_is_dark: bool) -> dict:
    """Select lighting style based on mood and background brightness."""
    lighting_map = {
        "史诗感": ("dramatic", "30px", "rgba(0,0,0,0.5)"),
        "压抑": ("gloomy", "40px", "rgba(0,0,0,0.7)"),
        "轻快": ("soft", "10px", "rgba(0,0,0,0.1)"),
        "诡谲": ("dramatic", "25px", "rgba(0,0,0,0.4)"),
        "浪漫": ("soft", "15px", "rgba(0,0,0,0.15)"),
        "冷峻": ("natural", "20px", "rgba(0,0,0,0.3)"),
        "温暖": ("soft", "12px", "rgba(0,0,0,0.12)"),
        "悲壮": ("dramatic", "35px", "rgba(0,0,0,0.6)"),
        "神秘": ("dramatic", "25px", "rgba(0,0,0,0.5)"),
        "紧张": ("harsh", "20px", "rgba(0,0,0,0.45)"),
        "宁静": ("natural", "8px", "rgba(0,0,0,0.08)"),
        "狂野": ("harsh", "22px", "rgba(0,0,0,0.4)"),
        "怀旧": ("soft", "15px", "rgba(0,0,0,0.2)"),
    }
    ltype, blur, color = lighting_map.get(mood_key, ("soft", "20px", "rgba(0,0,0,0.3)"))

    return {
        "type": ltype,
        "shadow_blur": blur,
        "shadow_color": color,
    }


# ============================================================================
# Step 6: Select Motion
# ============================================================================

def select_motion(text: str, mood_key: str) -> dict:
    """Select motion/animation style from atmosphere keywords and mood."""
    mood = MOOD_PARAMS.get(mood_key, MOOD_PARAMS["史诗感"])

    # Scan for emotion→motion keywords
    motion_scores: dict[str, dict] = defaultdict(lambda: {"count": 0, "data": {}})
    for word, motion_data in EMOTION_MOTION_MAP.items():
        count = len(re.findall(re.escape(word), text, re.IGNORECASE))
        if count > 0:
            mt = motion_data["type"]
            motion_scores[mt]["count"] += count
            motion_scores[mt]["data"] = motion_data

    if motion_scores:
        best = max(motion_scores, key=lambda k: motion_scores[k]["count"])
        motion_data = motion_scores[best]["data"]
        motion_type = motion_data["type"]
        base_speed = motion_data["speed"]
        has_parallax = motion_data["has_parallax"]
        has_glow_pulse = motion_data["has_glow_pulse"]
    else:
        # Default from mood
        mood_speed = mood["motion_speed"]
        if mood_speed < 0.15:
            motion_type = "static"
        elif mood_speed < 0.4:
            motion_type = "drift"
        elif mood_speed < 0.6:
            motion_type = "pulse"
        elif mood_speed < 0.75:
            motion_type = "wave"
        else:
            motion_type = "rapid"
        base_speed = mood_speed
        has_parallax = mood_speed > 0.15
        has_glow_pulse = 0.3 <= mood_speed <= 0.7

    return {
        "speed": round(base_speed, 2),
        "type": motion_type,
        "has_parallax": has_parallax,
        "has_glow_pulse": has_glow_pulse,
    }


# ============================================================================
# Step 7: Detect Dominant Mood
# ============================================================================

def detect_mood(text: str, lang: str) -> str:
    """Detect the dominant emotional tone of the text."""
    mood_counts: dict[str, int] = defaultdict(int)

    # Score CN mood keywords
    for word, mood_key in MOOD_KEYWORDS_CN.items():
        mood_counts[mood_key] += text.count(word) * 5

    # Score EN mood keywords
    text_lower = text.lower()
    for word, mood_key in MOOD_KEYWORDS_EN.items():
        mood_counts[mood_key] += text_lower.count(word) * 5

    # Also check entity attributes for mood signals
    # (dark, death, war → 悲壮 or 压抑)

    if not any(mood_counts.values()):
        return "史诗感"  # Default

    best_mood = max(mood_counts, key=lambda k: mood_counts[k])
    return best_mood


# ============================================================================
# Step 8: Generate Design Name
# ============================================================================

def generate_design_name(text: str, color_hits: list[dict],
                          mood_key: str, era_key: str) -> str:
    """Generate a unique design name from text analysis."""
    # Extract意象 keywords from color hits
   意象_a = ""
   意象_b = ""

    if color_hits:
        意象_a = color_hits[0]["word"]

    #意象_b from mood/era
   意象_map = {
        "史诗感": "纪元", "压抑": "深渊", "轻快": "晨曦",
        "诡谲": "迷雾", "浪漫": "花语", "冷峻": "霜华",
        "温暖": "暖阳", "悲壮": "残响", "神秘": "秘境",
        "紧张": "急弦", "宁静": "静水", "狂野": "烈焰",
        "怀旧": "旧梦",
    }
    意象_b = 意象_map.get(mood_key, "回响")

    lang = detect_language(text)
    if lang == "zh":
        return f"「{意象_a}·{意象_b}」"
    else:
        return f"{意象_a} · {意象_b}"


# ============================================================================
# Step 9: Build Generation Rationale
# ============================================================================

def build_rationale(color_hits: list[dict], typography: dict,
                     texture: dict, mood_key: str, text: str) -> dict:
    """Build the generation rationale explaining design decisions."""
    # Color rationale
    if color_hits:
        top_colors = [h["word"] for h in color_hits[:3]]
        color_from = f"从文中反复出现的「{'」「'.join(top_colors)}」等色彩意象中提取了主色调"
    else:
        color_from = f"根据文本的整体{mood_key}基调生成了匹配的调色板"

    # Font rationale
    era = typography.get("era_detected", "modern")
    era_names = {
        "ancient_cn": "古典东方", "modern": "现代都市", "future": "未来科幻",
        "fantasy": "奇幻世界", "xianxia": "仙侠修真", "steampunk": "蒸汽工业",
        "wasteland": "废土末日", "noir": "黑色悬疑", "renaissance": "文艺复兴",
    }
    font_from = f"从文中的{era_names.get(era, era)}气质，选择了{'衬线' if 'serif' in typography.get('heading_font','').lower() or 'Serif' in typography.get('heading_font','') else '无衬线'}字体「{typography['heading_font']}」"

    # Texture rationale
    texture_from = f"从文中场景分布提取了「{texture['type']}」纹理质感"

    # Find a key image sentence for the design concept
    concept = f"以{mood_key}为基调，构建与文本气质共鸣的视觉体验"

    return {
        "color_from": color_from,
        "font_from": font_from,
        "texture_from": texture_from,
        "design_concept": concept,
    }


# ============================================================================
# Space parameter generation
# ============================================================================

def generate_space_params(mood_key: str, visual_density: float) -> dict:
    """Generate spacing parameters based on mood density."""
    # Higher density → tighter spacing
    base = 1.0 - visual_density * 0.5  # 0.5 to 1.0

    page_padding = f"{int(48 + base * 64)}px"
    card_padding = f"{int(16 + base * 16)}px"
    gap_small = f"{int(4 + base * 8)}px"
    gap_medium = f"{int(8 + base * 16)}px"
    gap_large = f"{int(16 + base * 24)}px"
    gap_xl = f"{int(32 + base * 32)}px"

    radius_base = MOOD_PARAMS.get(mood_key, MOOD_PARAMS["史诗感"])["radius_base"]
    radius_small = f"{int(2 + radius_base * 6)}px"
    radius_medium = f"{int(6 + radius_base * 16)}px"
    radius_large = f"{int(12 + radius_base * 24)}px"
    radius_card = f"{int(8 + radius_base * 20)}px"

    return {
        "page_padding": page_padding,
        "card_padding": card_padding,
        "gap_small": gap_small,
        "gap_medium": gap_medium,
        "gap_large": gap_large,
        "gap_xl": gap_xl,
        "radius_small": radius_small,
        "radius_medium": radius_medium,
        "radius_large": radius_large,
        "radius_card": radius_card,
    }


# ============================================================================
# Main: Extract Visual Genome
# ============================================================================

def extract_visual_genome(text: str, entities: list[dict] | None = None,
                           relationships: list[dict] | None = None,
                           timeline: dict | None = None,
                           user_adjustments: dict | None = None) -> dict:
    """
    Main visual genome extraction pipeline.

    Args:
        text: Full novel text
        entities: Extracted entities (optional, for context)
        relationships: Extracted relationships (optional)
        timeline: Timeline data (optional)
        user_adjustments: User-specified adjustments to the design scheme

    Returns:
        Complete visual design scheme JSON
    """
    if entities is None:
        entities = []

    lang = detect_language(text)

    # Step 1: Extract color keywords
    color_hits = extract_color_keywords(text, lang)

    # Step 2: Detect mood
    mood_key = detect_mood(text, lang)

    # Step 3: Generate color palette
    color = generate_palette(color_hits, mood_key)

    # Step 4: Select typography
    typography = select_typography(text, lang, mood_key, entities)

    # Step 5: Select texture
    texture = select_texture(text, lang)

    # Step 6: Select lighting
    lighting = select_lighting(mood_key, color["brightness"] < 0.55)

    # Step 7: Select motion
    motion = select_motion(text, mood_key)

    # Step 8: Generate space params
    mood = MOOD_PARAMS.get(mood_key, MOOD_PARAMS["史诗感"])
    space = generate_space_params(mood_key, mood["visual_density"])

    # Step 9: Generate design name
    design_name = generate_design_name(text, color_hits, mood_key,
                                        typography.get("era_detected", "modern"))

    # Step 10: Build rationale
    rationale = build_rationale(color_hits, typography, texture, mood_key, text)

    # Step 11: Build mood object
    mood_obj = {
        "emotional_tone": mood_key,
        "visual_density": round(mood["visual_density"], 2),
        "era_feel": _get_era_feel(typography.get("era_detected", "modern")),
    }

    # Assemble final design
    design = {
        "design_id": str(uuid.uuid4()),
        "design_name": design_name,

        "color": color,
        "typography": typography,
        "space": space,
        "texture": texture,
        "lighting": lighting,
        "motion": motion,
        "mood": mood_obj,

        "generation_rationale": rationale,

        "metadata": {
            "source_color_keywords": [h["word"] for h in color_hits[:10]],
            "detected_mood": mood_key,
            "detected_era": typography.get("era_detected", "modern"),
            "detected_language": lang,
            "color_hit_count": len(color_hits),
        },
    }

    # Apply user adjustments if provided
    if user_adjustments:
        design = apply_adjustments(design, user_adjustments)

    return design


def _get_era_feel(era_key: str) -> str:
    mapping = {
        "ancient_cn": "古代", "modern": "现代", "future": "未来",
        "fantasy": "奇幻", "xianxia": "古代", "steampunk": "近代",
        "wasteland": "未来", "noir": "现代", "renaissance": "古代",
    }
    return mapping.get(era_key, "永恒")


# ============================================================================
# User Adjustment Engine
# ============================================================================

def apply_adjustments(design: dict, adjustments: dict) -> dict:
    """Apply user-specified adjustments to a design scheme."""
    d = design  # Work on a reference (caller should deepcopy if needed)

    # --- Color adjustments ---
    if "cooler" in adjustments or "色彩再冷一点" in str(adjustments):
        d["color"]["warmth"] = clamp(d["color"]["warmth"] - 0.2, -1, 1)
        for key in ["primary", "secondary", "accent", "bg_start", "bg_end", "glow"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], h_shift=15, s_mult=0.9, l_mult=1.0)

    if "warmer" in adjustments or "暖一点" in str(adjustments):
        d["color"]["warmth"] = clamp(d["color"]["warmth"] + 0.2, -1, 1)
        for key in ["primary", "secondary", "accent", "bg_start", "bg_end", "glow"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], h_shift=-15, s_mult=1.1, l_mult=1.0)

    if "brighter" in adjustments or "亮一些" in str(adjustments) or "整体亮一些" in str(adjustments):
        d["color"]["brightness"] = clamp(d["color"]["brightness"] + 0.15)
        for key in ["bg_start", "bg_end", "surface"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], 0, 1.0, 1.3)
        if d["color"]["brightness"] > 0.6:
            d["color"]["text_primary"] = "#1A1A1A"
            d["color"]["text_secondary"] = "#5A5A5A"

    if "darker" in adjustments or "暗一些" in str(adjustments):
        d["color"]["brightness"] = clamp(d["color"]["brightness"] - 0.15)
        for key in ["bg_start", "bg_end", "surface"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], 0, 1.0, 0.7)
        if d["color"]["brightness"] < 0.5:
            d["color"]["text_primary"] = "#E8E8F0"
            d["color"]["text_secondary"] = "#A0A0B8"

    if "more saturated" in adjustments or "更鲜艳" in str(adjustments):
        d["color"]["saturation"] = clamp(d["color"]["saturation"] + 0.15)
        for key in ["primary", "secondary", "accent", "glow"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], 0, 1.3, 1.0)

    if "less saturated" in adjustments or "淡一些" in str(adjustments) or "灰度" in str(adjustments):
        d["color"]["saturation"] = clamp(d["color"]["saturation"] - 0.15)
        for key in ["primary", "secondary", "accent", "glow"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], 0, 0.7, 1.0)

    # --- Blue shift ---
    if "蓝色系" in str(adjustments) or "偏蓝" in str(adjustments) or "blue" in str(adjustments).lower():
        for key in ["primary", "secondary", "accent", "glow"]:
            if key in d["color"]:
                d["color"][key] = adjust_hsl(d["color"][key], h_shift=220, s_mult=1.0, l_mult=1.0)
                # Push toward blue by shifting hue toward ~220°

    # --- Font adjustments ---
    if "字体换更现代的" in str(adjustments) or "more modern font" in str(adjustments).lower():
        d["typography"]["heading_font"] = "Inter"
        d["typography"]["body_font"] = "Inter"
        d["typography"]["decorative_font"] = ""

    if "更古典" in str(adjustments) or "古典" in str(adjustments) or "classic" in str(adjustments).lower():
        d["typography"]["heading_font"] = "Playfair Display"
        d["typography"]["body_font"] = "Lora"
        d["typography"]["decorative_font"] = "Cormorant Garamond"

    # --- Texture adjustments ---
    if "背景纹理再淡一些" in str(adjustments) or "texture lighter" in str(adjustments).lower():
        d["texture"]["intensity"] = clamp(d["texture"]["intensity"] - 0.15)

    if "纹理更明显" in str(adjustments) or "texture stronger" in str(adjustments).lower():
        d["texture"]["intensity"] = clamp(d["texture"]["intensity"] + 0.15)

    # --- Motion adjustments ---
    if "去掉动效" in str(adjustments) or "no animation" in str(adjustments).lower():
        d["motion"]["speed"] = 0.0
        d["motion"]["type"] = "static"
        d["motion"]["has_parallax"] = False
        d["motion"]["has_glow_pulse"] = False

    if "动效更慢" in str(adjustments) or "slower" in str(adjustments).lower():
        d["motion"]["speed"] = clamp(d["motion"]["speed"] - 0.15)

    if "动效更快" in str(adjustments) or "faster" in str(adjustments).lower():
        d["motion"]["speed"] = clamp(d["motion"]["speed"] + 0.15)

    # --- Simplicity / density ---
    if "更简洁" in str(adjustments) or "更简洁一些" in str(adjustments) or "少点装饰" in str(adjustments):
        d["mood"]["visual_density"] = clamp(d["mood"]["visual_density"] - 0.2)
        d["texture"]["intensity"] = clamp(d["texture"]["intensity"] - 0.15)
        d["motion"]["speed"] = clamp(d["motion"]["speed"] - 0.15)
        d["motion"]["type"] = "static" if d["motion"]["speed"] < 0.1 else d["motion"]["type"]

    if "更厚重" in str(adjustments) or "更史诗" in str(adjustments) or "不够史诗" in str(adjustments):
        d["mood"]["emotional_tone"] = "史诗感"
        d["color"]["saturation"] = clamp(d["color"]["saturation"] + 0.1)
        d["typography"]["heading_weight"] = min(900, d["typography"]["heading_weight"] + 200)
        d["typography"]["heading_letter_spacing"] = round(d["typography"]["heading_letter_spacing"] + 0.01, 3)

    # --- Specific color replacement ---
    for adjust_key in adjustments:
        if "主色" in adjust_key and "换成" in adjust_key:
            # Simple: just set primary to something — handled by the blue-shift
            # or other specific color adjustments above
            pass

    return d


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Extract visual genome from novel text for unique design generation."
    )
    parser.add_argument("--text", "-t", type=Path, required=True,
                       help="Novel text file")
    parser.add_argument("--entities", "-e", type=Path,
                       help="Entities JSON file (from extract_entities.py)")
    parser.add_argument("--output", "-o", type=Path,
                       help="Output design JSON file (stdout if omitted)")
    parser.add_argument("--adjustments", "-a", type=Path,
                       help="JSON file with user adjustment parameters")
    parser.add_argument("--pretty", action="store_true",
                       help="Pretty-print output JSON")
    args = parser.parse_args()

    # Read inputs
    text = args.text.read_text(encoding="utf-8")
    entities = []
    relationships = []
    timeline = None

    if args.entities and args.entities.exists():
        edata = json.loads(args.entities.read_text(encoding="utf-8"))
        entities = edata.get("entities", [])
        relationships = edata.get("relationships", [])
        timeline = edata.get("timeline", None)

    adjustments = None
    if args.adjustments and args.adjustments.exists():
        adjustments = json.loads(args.adjustments.read_text(encoding="utf-8"))

    # Extract visual genome
    design = extract_visual_genome(text, entities, relationships, timeline, adjustments)

    # Output
    indent = 2 if args.pretty else None
    json_output = json.dumps(design, ensure_ascii=False, indent=indent)

    if args.output:
        args.output.write_text(json_output, encoding="utf-8")
        print(f"[OK] Visual design scheme '{design['design_name']}' "
              f"written to {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
