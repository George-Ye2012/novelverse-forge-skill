# Design Genome Guide — Visual Gene Extraction Reference

Complete reference for extracting "visual genes" from novel text and
generating a unique visual design scheme. Used by `scripts/visual_genome.py`
in **Phase 3 — Visual Genome Extraction**.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Color Lexicon](#color-lexicon)
3. [Texture Lexicon](#texture-lexicon)
4. [Mood → Design Parameter Mapping](#mood--design-parameter-mapping)
5. [Era → Typography Mapping](#era--typography-mapping)
6. [Scene → Texture Mapping](#scene--texture-mapping)
7. [Emotion → Motion Mapping](#emotion--motion-mapping)
8. [Font Selection Algorithm](#font-selection-algorithm)
9. [Color Generation Algorithm](#color-generation-algorithm)
10. [Design Name Generation](#design-name-generation)

---

## Core Philosophy

**Old model**: Analyze novel → match preset style → apply template
**New model**: Analyze novel → extract visual genes → generate unique design → build page

Every design decision MUST be traceable back to a specific passage, keyword,
or pattern in the source text. No two novels should ever receive identical
visual schemes. The design should feel like it "grew organically" from the
text itself.

---

## Color Lexicon

### Chinese Color Words → Hex Mapping

| Chinese Color Word | Hex Value | Hue Family | Warmth |
|---|---|---|---|
| 血红 / 赤红 | `#8B0000` | Red | Warm (+0.9) |
| 暗红 / 深红 | `#4A0A0A` | Dark Red | Warm (+0.7) |
| 绯红 / 朱红 | `#CC3333` | Vermillion | Warm (+0.8) |
| 嫣红 / 桃红 | `#E87080` | Rose | Warm (+0.7) |
| 玫瑰红 | `#C04060` | Rose Red | Warm (+0.6) |
| 墨色 / 漆黑 | `#1A1A1A` | Black | Neutral (0.0) |
| 暗金 / 古铜 | `#C9A050` | Gold | Warm (+0.8) |
| 鎏金 / 灿金 | `#D4A830` | Bright Gold | Warm (+0.9) |
| 淡金 / 沙金 | `#D4C090` | Pale Gold | Warm (+0.5) |
| 青金 / 宝蓝 | `#1A3A6A` | Sapphire | Cold (-0.7) |
| 天蓝 / 蔚蓝 | `#4080C0` | Sky Blue | Cold (-0.5) |
| 海蓝 / 深蓝 | `#0A2A5A` | Deep Blue | Cold (-0.8) |
| 翠绿 / 碧色 | `#2A6B5A` | Jade Green | Cold (-0.4) |
| 墨绿 / 苍翠 | `#1A3A2A` | Forest Green | Cold (-0.5) |
| 嫩绿 / 新绿 | `#80C060` | Spring Green | Warm (+0.3) |
| 苍白 / 月白 | `#E8E0D8` | Moon White | Neutral (0.0) |
| 灰白 / 素白 | `#D0D0D0` | Ash White | Neutral (-0.2) |
| 雪白 / 霜白 | `#F0F0F8` | Snow White | Cold (-0.3) |
| 乳白 / 象牙白 | `#F5F0E0` | Ivory | Warm (+0.3) |
| 紫罗兰 / 绛紫 | `#4A1A5A` | Violet | Cold (-0.6) |
| 品红 / 洋红 | `#AA006A` | Magenta | Warm (+0.4) |
| 淡紫 / 薰衣草 | `#A080C0` | Lavender | Cold (-0.3) |
| 青蓝 / 天青 | `#0088BB` | Cyan Blue | Cold (-0.6) |
| 暗紫 / 幽紫 | `#2A0A3A` | Deep Purple | Cold (-0.8) |
| 琥珀 / 金棕 | `#C97030` | Amber | Warm (+0.7) |
| 锈红 / 赭石 | `#8A4A2A` | Rust | Warm (+0.6) |
| 苍青 / 霜色 | `#6A8A9A` | Steel Blue | Cold (-0.7) |
| 烟灰 / 雾色 | `#8A8A8A` | Smoke | Neutral (-0.1) |
| 桃粉 / 樱色 | `#EEB0B0` | Cherry Pink | Warm (+0.6) |
| 薄荷 / 青碧 | `#80C0A0` | Mint | Cold (-0.3) |
| 橘黄 / 暖橙 | `#E08040` | Orange | Warm (+0.8) |
| 明黄 / 亮黄 | `#E8C040` | Yellow | Warm (+0.7) |
| 靛蓝 / 靛青 | `#2A4070` | Indigo | Cold (-0.7) |
| 银灰 / 铁灰 | `#708090` | Slate | Neutral (-0.3) |
| 炭灰 / 石墨 | `#3A3A3A` | Charcoal | Neutral (-0.1) |
| 沙色 / 沙漠色 | `#D4B896` | Sand | Warm (+0.4) |
| 砖红 / 土红 | `#A05030` | Brick | Warm (+0.6) |
| 巧克力 / 可可 | `#604030` | Brown | Warm (+0.5) |
| 米色 / 杏色 | `#F0E0C8` | Beige | Warm (+0.3) |
| 藏蓝 / 海军蓝 | `#1A2A4A` | Navy | Cold (-0.8) |
| 钴蓝 | `#2040A0` | Cobalt | Cold (-0.7) |
| 湖蓝 / 水蓝 | `#40A0C0` | Lake Blue | Cold (-0.4) |
| 荧光绿 | `#40FF40` | Neon Green | Cold (-0.2) |
| 荧光粉 | `#FF40A0` | Neon Pink | Warm (+0.3) |
| 霓虹橙 | `#FF6020` | Neon Orange | Warm (+0.6) |

### English Color Words → Hex Mapping

| English Color Word | Hex Value | Hue Family | Warmth |
|---|---|---|---|
| blood red / crimson | `#8B0000` | Red | Warm (+0.9) |
| scarlet / vermillion | `#CC3333` | Red-Orange | Warm (+0.8) |
| gold / golden | `#D4A830` | Gold | Warm (+0.9) |
| silver / argent | `#C0C0C0` | Silver | Neutral (-0.2) |
| bronze / copper | `#CD7F32` | Bronze | Warm (+0.6) |
| emerald | `#2A6B5A` | Green | Cold (-0.4) |
| sapphire | `#1A3A6A` | Blue | Cold (-0.7) |
| ruby | `#8B0000` | Red | Warm (+0.9) |
| amethyst | `#6A3A8A` | Purple | Cold (-0.5) |
| obsidian / onyx | `#1A1A1A` | Black | Neutral (0.0) |
| ivory | `#F5F0E0` | Off-white | Warm (+0.3) |
| ebony | `#2A1A0A` | Dark Brown | Warm (+0.3) |
| pearl | `#F0F0F0` | White | Neutral (0.0) |
| coral | `#E87060` | Coral | Warm (+0.7) |
| teal | `#208080` | Teal | Cold (-0.5) |
| magenta | `#AA006A` | Magenta | Warm (+0.4) |
| cyan | `#00AAAA` | Cyan | Cold (-0.6) |
| neon blue | `#4060FF` | Electric Blue | Cold (-0.5) |
| neon pink | `#FF40A0` | Hot Pink | Warm (+0.3) |
| holographic | `#80C0FF` | Iridescent Blue | Cold (-0.4) |
| chrome | `#C0C8D0` | Metallic Gray | Neutral (-0.2) |
| brass | `#B5A642` | Brass | Warm (+0.6) |

---

## Texture Lexicon

### Chinese Texture Words → Texture Type

| Texture Word | Texture Type | CSS Generation Method |
|---|---|---|
| 光滑 / 琉璃 / 镜面 / 冰面 | `smooth` | Pure color + glossy gradient overlay |
| 粗糙 / 沙砾 / 风化 / 磨砂 | `grain` | SVG feTurbulence noise filter |
| 纸张 / 羊皮 / 布帛 / 绢帛 / 宣纸 | `paper` | Subtle noise + paper texture pattern |
| 金属 / 钢铁 / 黄铜 / 铁锈 / 合金 | `metal` | Multi-directional linear-gradient |
| 水墨 / 晕染 / 墨迹 / 泼墨 | `ink_wash` | Blurred radial-gradient layers |
| 霓虹 / 荧光 / 光带 / 全息 / 激光 | `neon` | Glow box-shadow + light streaks |
| 网格 / 电路 / 矩阵 / 数据 / 代码 | `grid` | CSS repeating-linear-gradient |
| 星云 / 星尘 / 深空 / 星河 / 宇宙 | `stars` | CSS radial-gradient dots + twinkle |
| 暗影 / 幽暗 / 迷雾 / 雾霭 / 阴霾 | `shadow` | Multi-layer radial-gradient |
| 波纹 / 水纹 / 流动 / 涟漪 / 潮汐 | `wave` | SVG wave path or CSS wave animation |
| 石纹 / 岩石 / 大理石 / 花岗岩 | `stone` | SVG feTurbulence + color matrix |
| 织物 / 丝绸 / 锦缎 / 天鹅绒 | `fabric` | Fine repeating pattern |
| 木质 / 木纹 / 竹纹 | `wood` | Linear-gradient wood grain |
| 晶体 / 水晶 / 冰晶 / 钻石 | `crystal` | Sharp gradient facets + inner glow |
| 火焰 / 熔岩 / 余烬 | `fire` | Animated radial-gradient + warm glow |
| 雾气 / 烟 / 蒸汽 | `mist` | Blurred gradient shapes + low opacity |
| 皮革 / 皮质 | `leather` | Dark gradient + subtle grain |
| 陶瓷 / 瓷器 | `ceramic` | Smooth gradient + sharp highlight |

### English Texture Words → Texture Type

| Texture Word | Texture Type |
|---|---|
| smooth / glass / polished / mirror | `smooth` |
| rough / grainy / gritty / sand | `grain` |
| paper / parchment / vellum | `paper` |
| metal / steel / iron / brass / chrome / alloy | `metal` |
| ink / watercolor / wash / brush | `ink_wash` |
| neon / glow / hologram / laser | `neon` |
| grid / circuit / matrix / wireframe / digital | `grid` |
| nebula / stardust / void / cosmic / galaxy | `stars` |
| shadow / dark / misty / fog / gloom | `shadow` |
| wave / ripple / water / flowing / tide | `wave` |
| stone / rock / marble / granite | `stone` |
| fabric / silk / velvet / cloth | `fabric` |
| wood / timber / bamboo | `wood` |
| crystal / ice / diamond / frost | `crystal` |
| fire / lava / ember / flame | `fire` |

---

## Mood → Design Parameter Mapping

| Emotional Tone | Saturation | Brightness | Contrast | Motion Speed | Border Radius | Visual Density |
|---|---|---|---|---|---|---|
| **史诗感** (Epic) | 0.60 | 0.50 | High (0.85) | 0.50 | Small (4-8px) | 0.45 |
| **压抑** (Oppressive) | 0.30 | 0.30 | Low (0.30) | 0.20 | Medium (8-12px) | 0.70 |
| **轻快** (Light) | 0.80 | 0.80 | Medium (0.55) | 0.80 | Large (16-24px) | 0.30 |
| **诡谲** (Uncanny) | 0.40 | 0.40 | Medium (0.50) | 0.30 | Medium (8-16px) | 0.55 |
| **浪漫** (Romantic) | 0.70 | 0.70 | Low (0.35) | 0.60 | Large (16-24px) | 0.40 |
| **冷峻** (Stoic) | 0.20 | 0.50 | High (0.80) | 0.10 | Small (2-6px) | 0.25 |
| **温暖** (Warm) | 0.70 | 0.70 | Medium (0.50) | 0.50 | Medium (8-16px) | 0.40 |
| **悲壮** (Tragic) | 0.50 | 0.30 | High (0.80) | 0.20 | Small (4-8px) | 0.50 |
| **神秘** (Mysterious) | 0.50 | 0.40 | Medium (0.55) | 0.25 | Medium (8-12px) | 0.50 |
| **紧张** (Tense) | 0.40 | 0.45 | High (0.75) | 0.70 | Small (4-6px) | 0.35 |
| **宁静** (Serene) | 0.50 | 0.75 | Low (0.35) | 0.15 | Medium (8-16px) | 0.20 |
| **狂野** (Wild) | 0.85 | 0.60 | High (0.80) | 0.85 | Irregular | 0.65 |
| **怀旧** (Nostalgic) | 0.45 | 0.60 | Low (0.35) | 0.30 | Medium (8-12px) | 0.45 |

---

## Era → Typography Mapping

| Era Keywords (CN) | Era Keywords (EN) | Recommended Font | Category |
|---|---|---|---|
| 古代 / 帝国 / 王朝 / 宫廷 / 江湖 / 战国 / 三国 | ancient, empire, dynasty, kingdom, medieval, feudal | Noto Serif SC / Playfair Display | Serif |
| 现代 / 都市 / 当代 / 现实 / 日常 | modern, urban, contemporary, realistic, everyday | Inter / Noto Sans SC | Sans-serif |
| 未来 / 科幻 / 赛博 / 星舰 / 太空 / 银河 | future, sci-fi, cyber, starship, space, galaxy | Orbitron / Space Grotesk | Tech Sans-serif |
| 奇幻 / 魔法 / 传说 / 神话 / 龙 / 精灵 | fantasy, magic, myth, legend, dragon, elf | Cinzel / Uncial Antiqua | Decorative Serif |
| 蒸汽 / 维多利亚 / 齿轮 / 工业革命 | steam, victorian, gear, industrial revolution | Playfair Display / Lora | Vintage Serif |
| 仙侠 / 水墨 / 道 / 禅 / 修真 / 修仙 | cultivation, tao, zen, ink, immortal | 思源宋体 / 霞鹜文楷 | Calligraphic |
| 废土 / 末日 / 荒漠 / 核后 | wasteland, apocalypse, post-apocalyptic, desert | Bangers / Roboto Condensed | Rough Sans-serif |
| 侦探 / 黑色 / 悬疑 / 推理 / noir | detective, noir, mystery, suspense, crime | Oswald / Lato | Compact Sans-serif |
| 海盗 / 航海 / 大航海 / 海洋 | pirate, nautical, age of sail, ocean | Pirata One / IM Fell English | Historical |
| 西部 / 牛仔 / 荒野 | western, cowboy, frontier, wild west | Rye / Abril Fatface | Western |
| 文艺复兴 / 巴洛克 | renaissance, baroque, enlightenment | Cormorant Garamond / EB Garamond | Old-style Serif |
| 昭和 / 大正 / 和风 | japanese, samurai, taisho, showa | Noto Serif JP / Zen Kaku Gothic | Japanese |

---

## Scene → Texture Mapping

| Scene Keywords (CN) | Scene Keywords (EN) | Primary Texture | Secondary Texture |
|---|---|---|---|
| 城堡 / 地牢 / 古堡 / 要塞 | castle, dungeon, fortress, citadel | `stone` | `shadow` |
| 未来城市 / 赛博 / 霓虹街 | future city, cyberpunk, neon street | `grid` | `neon` |
| 森林 / 山林 / 雨林 / 丛林 | forest, jungle, woods, rainforest | `paper` | `grain` |
| 星舰 / 太空站 / 飞船 | starship, space station, spacecraft | `stars` | `metal` |
| 废土 / 荒漠 / 废墟 | wasteland, desert, ruins | `grain` | `stone` |
| 宫廷 / 殿堂 / 皇宫 | palace, court, throne room | `fabric` | `metal` |
| 江湖 / 山水 / 竹林 | rivers and lakes, mountains, bamboo | `ink_wash` | `paper` |
| 深海 / 海底 / 水下 | deep sea, underwater, ocean abyss | `wave` | `shadow` |
| 寺院 / 道观 / 庙宇 | temple, monastery, shrine | `wood` | `paper` |
| 实验室 / 研究所 | laboratory, research facility | `smooth` | `grid` |
| 战场 / 前线 | battlefield, warzone, front line | `fire` | `grain` |
| 云端 / 天空城 | cloud, sky city, floating island | `mist` | `crystal` |
| 地下 / 洞穴 / 矿坑 | underground, cave, mine | `stone` | `shadow` |
| 学院 / 图书馆 / 书院 | academy, library, archive | `paper` | `wood` |
| 蒸汽工厂 / 车间 | steam factory, workshop | `metal` | `mist` |
| 冰原 / 雪域 / 极地 | tundra, snowfield, arctic | `crystal` | `smooth` |
| 火山 / 岩浆 | volcano, lava, magma | `fire` | `stone` |

---

## Emotion → Motion Mapping

| Emotion / Atmosphere | Motion Type | Speed | Has Parallax | Has Glow Pulse | Description |
|---|---|---|---|---|---|
| 涌动 / 流动 / 潮汐 | `wave` | 0.4 | true | false | Slow, undulating background motion |
| 闪烁 / 幽光 / 星火 | `pulse` | 0.5 | false | true | Subtle brightness oscillation |
| 飘渺 / 漂浮 / 云烟 | `drift` | 0.2 | true | false | Slow horizontal drift of background elements |
| 静止 / 永恒 / 凝固 | `static` | 0.0 | false | false | No motion — frozen, timeless feel |
| 紧张 / 急速 / 追逐 | `rapid` | 0.8 | true | true | Fast transitions, energetic feel |
| 呼吸 / 生命 / 脉动 | `pulse` | 0.3 | false | true | Slow, organic breathing rhythm |
| 坠落 / 崩塌 / 毁灭 | `fall` | 0.6 | true | false | Downward particle motion |
| 旋转 / 轮回 / 螺旋 | `spin` | 0.3 | true | false | Very slow rotation of decorative elements |

---

## Font Selection Algorithm

```
Input: novel_text, era_keywords[], mood_tone, proper_nouns[]
Output: heading_font, body_font, decorative_font

Step 1 — Detect era from keywords
  - Scan text for era keywords from the Era → Typography table
  - Score each era category by keyword frequency (weighted by proximity to key passages)
  - Select the highest-scoring era category

Step 2 — Get base fonts for that era
  - heading_font = era's recommended heading font
  - body_font = era's recommended body font or system font fallback
  - decorative_font = optional; only set if era has one

Step 3 — Adjust weights and spacing from mood
  mood = detect_dominant_mood(text)
  - Epic / Tragic → heading_weight: 800-900, heading_letter_spacing: 0.02-0.05em
  - Light / Warm → heading_weight: 400-600, heading_letter_spacing: 0-0.01em
  - Oppressive / Stoic → heading_weight: 700-800, heading_letter_spacing: -0.01-0.01em
  - Uncanny / Mysterious → heading_weight: 500-700, heading_letter_spacing: 0.01-0.03em
  - Romantic → heading_weight: 300-500, heading_letter_spacing: 0-0.02em
  - Tense → heading_weight: 600-800, heading_letter_spacing: -0.02-0em

Step 4 — Determine scale_ratio from visual density
  - High density → smaller ratio (1.125-1.2) — tighter hierarchy
  - Low density → larger ratio (1.25-1.333) — more dramatic scale jumps

Step 5 — Validate
  - Ensure all fonts are available on Google Fonts
  - Provide system font fallback stack
  - For Chinese text, always include a Chinese-capable font
```

---

## Color Generation Algorithm

```
Input: novel_text, mood_tone, color_keywords_found[]
Output: full color palette (13 colors + 3 parameters)

Step 1 — Extract color keywords from text
  - Scan for all words matching the Color Lexicon (CN + EN)
  - For each match, record: {word, hex, warmth, position, context_sentence}
  - Count frequency of each color word
  - Build a warmth-weighted frequency map

Step 2 — Generate base palette (5 colors)
  - Take top 3 most frequent color keywords → direct hex mapping
  - Fill remaining slots with:
    - A complementary color (hue +180°, adjusted by warmth preference)
    - A neutral anchor (near-black or near-white based on mood brightness)

Step 3 — Adjust by mood
  mood_params = MOOD_PARAMETER_MAP[mood_tone]
  For each color in palette:
    - Adjust saturation by mood_params.saturation factor
    - Adjust brightness by mood_params.brightness factor
    - Shift hue toward warm (red/orange) or cool (blue/cyan) based on mood warmth

Step 4 — Assign roles
  primary = palette[0] (most frequent)
  secondary = palette[1] (second most frequent, or complementary to primary)
  accent = palette[2] (highest contrast relative to background)
  bg_start, bg_end = derive background gradient from palette (dark or light based on mood)
  text_primary = derive from bg: if bg is dark → light text; if bg is light → dark text
  text_secondary = text_primary at 60-70% opacity
  surface = bg shifted slightly lighter/darker
  surface_border = surface with alpha for glass effect
  glow = accent or secondary with glow intensity

Step 5 — Set color parameters
  warmth = average_warmth of all palette colors
  saturation = mood-adjusted average saturation
  brightness = mood-adjusted average brightness

Step 6 — Validate contrast
  - Ensure text_primary vs bg contrast ≥ 4.5:1 (WCAG AA)
  - Ensure text_primary vs surface contrast ≥ 3:1
  - Adjust if necessary by lightening/darkening
```

---

## Design Name Generation

Design names follow the pattern: `「意象A·意象B纪元」` or `「ConceptA · ConceptB Era」`

**Rules:**
1. Extract the two strongest visual意象 (imagery keywords) from the text
2. First意象 represents the dominant visual element (color/texture dominant)
3. Second意象 represents the era or atmosphere
4. Combine with `·` separator

**意象 word pool (auto-expanded from text analysis):**
- Color-based: 暗金, 深红, 霜白, 碧空, 墨色, 朱砂, 青冥, 银灰, 紫电, 金曦
- Texture-based: 深渊, 星尘, 霓虹, 水墨, 冰晶, 锈铁, 琉璃, 丝绸, 雾霭, 雷霆
- Era-based: 纪元, 王朝, 时代, 世纪, 年代, 轮回, 序章, 终章

**Examples:**
- From "血色残阳" + 帝国 → 「暗金·残阳纪元」
- From "星舰" + 深空 → 「星尘·深空回响」
- From "水墨" + 仙侠 → 「墨韵·青云志」
- From "霓虹" + 赛博 → 「霓虹深渊·数据纪元」

---

## Texture CSS Generation Reference

### `grain` — SVG Noise Filter
```css
background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E");
```

### `grid` — CSS Linear Gradient
```css
background-image:
  linear-gradient(rgba(PRIMARY, 0.08) 1px, transparent 1px),
  linear-gradient(90deg, rgba(PRIMARY, 0.08) 1px, transparent 1px);
background-size: 40px 40px;
```

### `stars` — CSS Radial Gradient Dots
```css
background-image:
  radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.6), transparent),
  radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.4), transparent),
  radial-gradient(1.5px 1.5px at 60% 20%, rgba(255,255,255,0.5), transparent),
  radial-gradient(1px 1px at 80% 50%, rgba(255,255,255,0.3), transparent);
```

### `neon` — Glow Effect
```css
box-shadow:
  0 0 5px GLOW_COLOR,
  0 0 15px GLOW_COLOR,
  0 0 30px GLOW_COLOR,
  0 0 60px GLOW_COLOR;
```

### `paper` — Subtle Paper Texture
```css
background-color: BG_COLOR;
background-image:
  url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
```

### `metal` — Metallic Gradient
```css
background: linear-gradient(
  135deg,
  METAL_LIGHT 0%,
  METAL_MID 25%,
  METAL_DARK 50%,
  METAL_MID 75%,
  METAL_LIGHT 100%
);
```

### `ink_wash` — Ink Wash Effect
```css
background:
  radial-gradient(ellipse at 30% 20%, rgba(PRIMARY, 0.08) 0%, transparent 50%),
  radial-gradient(ellipse at 70% 60%, rgba(SECONDARY, 0.05) 0%, transparent 50%),
  radial-gradient(ellipse at 50% 80%, rgba(ACCENT, 0.04) 0%, transparent 40%);
```

### `shadow` — Multi-Layer Shadow
```css
background:
  radial-gradient(ellipse at 50% 0%, BG_START 0%, transparent 60%),
  radial-gradient(ellipse at 80% 50%, rgba(SECONDARY, 0.05) 0%, transparent 50%),
  radial-gradient(ellipse at 20% 80%, rgba(PRIMARY, 0.03) 0%, transparent 40%);
```

### `crystal` — Crystal / Ice Effect
```css
background:
  linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%),
  linear-gradient(225deg, rgba(ACCENT, 0.08) 0%, transparent 50%),
  BG_COLOR;
```

---

## Motion CSS Generation Reference

### `wave` — Undulating Background
```css
@keyframes wave-motion {
  0%, 100% { transform: translateY(0) scaleY(1); }
  50% { transform: translateY(-10px) scaleY(1.02); }
}
.animated-bg { animation: wave-motion 8s ease-in-out infinite; }
```

### `pulse` — Breathing Glow
```css
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 5px GLOW_COLOR; opacity: 0.8; }
  50% { box-shadow: 0 0 25px GLOW_COLOR; opacity: 1; }
}
.glow-element { animation: glow-pulse 4s ease-in-out infinite; }
```

### `drift` — Slow Parallax Drift
```css
@keyframes drift-slow {
  0% { transform: translateX(0); }
  100% { transform: translateX(-30px); }
}
.drift-layer { animation: drift-slow 20s linear infinite; }
```

### `rapid` — Fast Energy
```css
@keyframes rapid-pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}
.rapid-element { animation: rapid-pulse 1.5s ease-in-out infinite; }
```

### `static` — Frozen / Timeless
```css
/* No animation — pure static rendering */
```

---

## Validation Rules

1. **Uniqueness**: Every design_id must be unique (UUID v4). No two generations should produce identical palettes.
2. **Contrast**: WCAG AA compliance for all text/background pairs (≥4.5:1 for normal text, ≥3:1 for large text).
3. **Font availability**: All recommended fonts must be available on Google Fonts.
4. **Color harmony**: All palette colors must be within acceptable color harmony ranges (no clashing hues without intentional contrast).
5. **Cultural sensitivity**: Avoid color combinations that carry unwanted cultural connotations.
6. **Design rationale**: Every design parameter must have a traceable source in the text (recorded in `generation_rationale`).
