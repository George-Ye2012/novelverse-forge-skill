# Novelverse Forge v4 — Visual Genome Edition

> 将小说文本转化为沉浸式互动世界观展示网页。每部小说获得从自身文本中「生长出来」的独一无二的视觉设计——没有预设模板。

---

**Novelverse Forge** 是一个 AI 驱动的世界构建工具。你提供小说原文，它自动提取人物、派别、地点、事件和关系网，然后——最关键的一步——**从文本中提取「视觉基因」**：扫描文中每一个颜色词、每一处场景描写、每一缕情绪氛围，将它们编译成一套只属于这部小说的配色方案、字体系统、纹理质感和动画节奏。最终输出一个 7 页 SPA 风格的独立网页，像一个为你的故事定制的数字博物馆。

它不是「选一个模板套上去」——它是「从文字里长出来的设计」。

---

## 概述

Novelverse Forge 接收用户提供的小说文本和可选的配图，自动完成：

1. **实体提取** — 人物、派别、地点、生物、事件、物品
2. **关系发现** — 11 种关系类型（师徒、血亲、仇敌、恋人…）
3. **时间线构建** — 相对时间表达归一化为有序时间轴
4. **视觉基因提取** — 从文本中提取色彩、字体、纹理、动效，生成独一无二的设计方案
5. **设计预览** — 生成可视化预览卡片，支持自然语言微调
6. **网页生成** — 输出一个 7 页 SPA 风格的独立 HTML 文件

### 核心理念

```
旧模式: 分析小说 → 匹配预设风格（6选1） → 套用模板
新模式: 分析小说 → 提取视觉基因 → 生成专属设计 → 构建页面
```

每一部小说生成的网页视觉都完全不同——色彩从文中的颜色词提取，字体从时代背景推断，纹理从场景描写联想，动效从情绪氛围推导。**设计从文本中「长出来」。**

## 快速开始

### 触发方式

在 Claude Code 对话中，直接粘贴小说文本，然后说：

```
帮我做小说世界观展示
```

或使用明确的触发短语：
- `build a world bible site for my novel`
- `create an interactive story universe page`
- `extract all characters and visualize them`
- `帮我做小说世界观展示` / `生成故事宇宙网页`

### 工作流程

```
用户上传小说文本
    ↓
Phase 1: 确认范围（完整世界观 / 仅人物 / 仅时间线）
    ↓
Phase 2: 实体提取 (extract_entities.py)
    ↓
Phase 3: 时间线构建 (build_timeline.py)
    ↓
Phase 4: 视觉基因提取 (visual_genome.py)  ← v4 核心创新
    ↓
Phase 5: 设计预览 (design_preview.py)
    ↓  用户反馈 → 微调参数 → 重新预览（支持自然语言指令）
    ↓
Phase 6: 生成 HTML (generate_html.py)
    ↓
输出: world_bible.html（单文件，离线可用）
```

### 微调指令示例

| 你想说什么 | 效果 |
|---|---|
| 「色彩再冷一点」 | 暖度 -0.2，色相偏蓝 |
| 「整体亮一些」 | 明度 +0.15，背景提亮 |
| 「字体换更现代的」 | 切换为 Inter / 无衬线字体 |
| 「背景纹理再淡一些」 | 纹理强度 -0.15 |
| 「去掉动效」 | 动效类型 → 静态，速度 → 0 |
| 「更简洁一些」 | 视觉密度 -0.2，纹理和动效减弱 |
| 「不够史诗，再厚重一点」 | 情绪 → 史诗感，字重 +200 |

## 输出页面结构

生成的 HTML 是一个 **7 页 SPA（单页应用）**，而非长滚动文档：

| 页面 | 路由 | 内容 |
|---|---|---|
| 🏠 总览 | `#overview` | 英雄区 + 世界观摘要 + 统计数字 + 快速入口 |
| ⏳ 时间线 | `#timeline` | 全屏交互式时间轴 + 时代筛选 |
| 👤 人物 | `#characters` | 图鉴网格 + 类型筛选 + 点击查看完整详情 |
| 🏛️ 派别 | `#factions` | 势力卡片 + 阵营分布 |
| 🐉 生物 | `#beings` | 生物/种族图鉴 |
| 🕸️ 关系网 | `#relations` | 纯文字自然语句关系表达 |
| 🔮 互动 | `#interactive` | 暗影之谜 + 低置信度实体 |

### 交互功能

- **← →** 键翻页，**1-7** 数字键直达
- **Ctrl+K** 全局搜索（跨页跳转结果）
- 点击任意实体卡片 → 弹出完整详情模态窗口
- 移动端汉堡菜单（< 768px）
- 明/暗主题切换（自动记忆）
- 浏览器前进/后退完整支持

## 目录结构

```
novelverse-forge/
├── SKILL.md                          # 技能定义与工作流程
├── README.md                         # 本文件
│
├── scripts/                          # Python 脚本
│   ├── extract_entities.py           # 实体提取器 (Phase 2)
│   ├── build_timeline.py             # 时间线构建器 (Phase 3)
│   ├── visual_genome.py              # 视觉基因引擎 (Phase 4) 🆕
│   ├── design_preview.py             # 设计预览生成器 (Phase 5) 🆕
│   └── generate_html.py              # HTML 生成器 (Phase 7)
│
├── assets/
│   ├── css/
│   │   └── base.css                  # 布局骨架（无主题色，全由变量控制）
│   ├── js/
│   │   ├── interactions.js           # 交互动效 + 详情弹窗
│   │   ├── navigation.js             # SPA 路由 + 汉堡菜单
│   │   ├── timeline.js               # 时间线交互
│   │   ├── search.js                 # 全局搜索
│   │   └── relation_graph.js         # D3.js 力导向图
│   └── templates/
│       └── page_template.html        # 7 页 SPA HTML 骨架
│
├── references/                       # 参考文档
│   ├── index.md                      # 索引与导航
│   ├── extraction_guide.md           # 实体提取规范
│   ├── design_genome_guide.md        # 视觉基因参考指南 🆕
│   ├── html_template.md              # HTML 生成规范
│   └── style_mapping.md              # 旧版风格对照表（已废弃）
│
└── output/                           # 输出目录
    ├── world_bible.html              # 生成的世界观网页
    ├── world_data.json               # 结构化世界数据
    └── design.json                   # 设计方案 JSON
```

## 视觉基因引擎

v4 的核心创新：不再从 6 个预设主题中选择，而是从小说文本中提取独一无二的视觉基因。

### 色彩提取

扫描文本中 200+ 个中英文色彩词（「血红」「暗金」「霓虹」「墨绿」…），统计频率，生成 5 色调色板，根据情绪基调调整饱和度与明度。

### 字体选择

检测时代关键词 → 匹配最佳字体：

| 时代 | 推荐字体 |
|---|---|
| 古代/帝国/江湖 | Noto Serif SC / Playfair Display |
| 现代/都市 | Inter / Noto Sans SC |
| 未来/赛博/星舰 | Orbitron / Space Grotesk |
| 仙侠/水墨/修真 | 思源宋体 / 霞鹄文楷 |
| 奇幻/魔法/传说 | Cinzel / Uncial Antiqua |

### 纹理生成

从场景词汇（城堡→石纹，星舰→星空，霓虹街→霓虹光晕…）选择纹理类型，通过 CSS（SVG filter、gradient、radial-gradient）动态渲染。

### 情绪→参数映射

| 情绪 | 饱和度 | 明度 | 动效速度 |
|---|---|---|---|
| 史诗感 | 0.60 | 0.50 | 0.50 |
| 压抑 | 0.30 | 0.30 | 0.20 |
| 诡谲 | 0.40 | 0.40 | 0.30 |
| 浪漫 | 0.70 | 0.70 | 0.60 |
| 冷峻 | 0.20 | 0.50 | 0.10 |

## 技术架构

### 设计理念

- **零外部依赖**：生成的 HTML 完全自包含，离线可用（仅 Google Fonts CDN 可选）
- **渐进增强**：Python 不可用时，可手动复制提取逻辑
- **用户主权**：所有实体可修正，设计可微调，最终确认后才生成
- **透明设计**：页脚展示每一个设计决策的文本依据

### CSS 架构

三层结构：

```
base.css         → 布局骨架、组件结构、重置样式（无颜色）
  ↓ 变量引用
dynamic CSS      → 所有视觉属性：颜色、字体、间距、纹理、动效
  ↓ 从设计 JSON 动态生成
inline styles    → SPA 过渡动画、导航指示器、响应式覆盖
```

### JS 模块

- `navigation.js` — SPA 路由器、汉堡菜单、键盘快捷键、进度条
- `interactions.js` — 滚动揭示、计数器动画、卡片光晕、吐司通知、**实体详情弹窗**
- `timeline.js` — 时间线缩放、拖拽平移、时代筛选
- `search.js` — 全屏搜索浮层、跨页结果跳转、Ctrl+K 快捷键
- `relation_graph.js` — D3.js 力导向关系图（可选）

## API 参考

### visual_genome.py

```bash
python scripts/visual_genome.py \
  --text novel.txt \
  --entities entities.json \
  --output design.json \
  --pretty
```

### design_preview.py

```bash
python scripts/design_preview.py \
  --design design.json \
  --output preview.html
```

### generate_html.py

```bash
python scripts/generate_html.py \
  --input world_data.json \
  --design design.json \
  --output world_bible.html \
  --images-dir ./character_art/
```

## 设计基因参考指南

详见 [`references/design_genome_guide.md`](references/design_genome_guide.md)，包含：

- **色彩词库**：200+ 中文色彩词 → 色值映射
- **质感词库**：80+ 质感词 → 纹理类型映射
- **情绪→参数映射**：13 种情绪基调的设计参数
- **场景→纹理映射**：18 类场景的纹理推荐
- **色彩生成算法**：从提取到调色板的完整流程
- **字体选择算法**：时代检测 + 情绪调整

## 许可与隐私

- 所有处理在本地完成，小说文本不会发送到任何外部 API
- 生成的 HTML 文件完全自包含，不发出外部网络请求（除 Google Fonts CDN 可选）
- 用户保留对其创作内容的所有权利
