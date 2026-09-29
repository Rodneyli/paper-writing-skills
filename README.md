# paper-writing-skills 论文写作 Skills 全集

「和Lee一起学AI」论文写作 Skills 系列的**本地主仓库**：22 个 skill 源文件 + 两本蒸馏原书 + 全部视频制作物料 + 蒸馏中间产物。

覆盖论文写作全流程：**选题 → 检索 → 精读 → 笔记 → 写作 → 修改 → 投稿**。

## 目录结构

```
paper-writing-skills/
├── README.md            ← 本文件
├── AGENTS.md            ← 项目约定（agent 必读）
├── skills/              ← 22 个 skill 源文件（按节目期数命名）
│   ├── 00-文献检索Skill/        （五源联搜版 = 未发布新版 + starter 发布定稿）
│   ├── 01 ~ 18/                 （主系列 18 期）
│   └── B0-zotero / B1-头脑风暴 / B2-博士蓝图  （番外 3 个）
├── episodes/            ← 22 期视频制作物料（口播稿、封面、图卡、发布物料，约 240MB）
├── distillation/        ← 两本书的蒸馏产物
│   ├── crafting-your-research-future/   成功之道：BOOK_OVERVIEW + INDEX + 9 个蒸馏 skill
│   └── writing-a-literature-review/     文献综述写作：SOURCES.md（章节→skill 映射）
├── books/               ← 两本书的电子版本体
├── 定稿skill包/          ← 第1~5期已定稿的 5 个独立 zip（对外分发用）
└── project-docs/        ← Coze 项目级文档（EPISODE_PLAN / SUITE_INDEX / 封面基准模板等）
```

## Skill 总览

| 期数 | 目录 | skill name | 蒸馏自 | 状态 |
|---|---|---|---|---|
| 00 | 00-文献检索Skill | literature-search | 自研 | ✅ 五源联搜已更新（待发布） |
| 01 | 01-预读分类详读 | preread-classify-deepread | 文献综述写作·第4章 | ✅ 定稿打包 |
| 02 | 02-研究质量评估清单 | research-quality-checklist | 文献综述写作·第1/6/7章 | ✅ 定稿打包 |
| 03 | 03-证据思维 | evidence-thinking | 文献综述写作·第1/6章 | 📄 已并入第2期 |
| 04 | 04-批判性创造性阅读 | critical-creative-paper-reading | 成功之道·第3章 | ✅ 定稿打包 |
| 05 | 05-九列笔记法 | spreadsheet-note-system | 文献综述写作·第4/8章 | ✅ 定稿打包 |
| 06 | 06-文献深度分析十二准则 | deep-article-analysis | 文献综述写作·第5章 | 📄 源已就绪 |
| 07 | 07-论断vs证据 | claim-vs-evidence | 文献综述写作·第5章 | ✅ 定稿打包 |
| 08 | 08-选题精炼十四步 | topic-refinement | 文献综述写作 | 📄 源已就绪 |
| 09 | 09-棋盘法选题 | matrix-method-topic-selection | 成功之道 | 🔶 已制作 |
| 10 | 10-格雷准则选题筛选 | grays-criteria-problem-evaluation | 成功之道·第4章 | 🔶 已制作 |
| 11 | 11-课题聚焦反游击战 | research-focus-anti-guerrilla | 成功之道 | 📄 源已就绪 |
| 12 | 12-笔记到主题大纲 | notes-to-outline-synthesis | 文献综述写作·第9章 | 📄 源已就绪 |
| 13 | 13-注释化vs综合叙述 | annotative-vs-synthetic-writing | 文献综述写作·第11章 | 📄 源已就绪 |
| 14 | 14-空白点与未来方向 | blank-spots-and-future-directions | 文献综述写作·第10章 | 📄 源已就绪 |
| 15 | 15-金字塔写作法 | top-down-pyramid-writing | 成功之道·第6章 | 📄 源已就绪 |
| 16 | 16-1030可读性检测 | ten-thirty-readability-test | 成功之道·第6章 | 📄 源已就绪 |
| 17 | 17-终稿自检 | final-self-edit-checklist | 文献综述写作·第12章+附录A | 📄 源已就绪 |
| 18 | 18-回复审稿人 | response-to-reviewers | 成功之道·第5/6章 | 📄 源已就绪 |
| B0 | B0-文献管理-zotero | zotero-cite | 自研（含 zotero_cite.py） | ✅ 已发布 |
| B1 | B1-学术头脑风暴 | academic-brainstorming-ideation | 成功之道 | 📄 源已就绪 |
| B2 | B2-博士论文蓝图 | thesis-blueprint-planning | 成功之道 | 📄 源已就绪 |

**两本蒸馏原书**：
- 《学术研究：你的成功之道》（Crafting Your Research Future），凌晓峰、杨强 → `books\` + `distillation\crafting-your-research-future\`
- 《文献综述写作》（Writing a Literature Review），加尔万 → `books\` + `distillation\writing-a-literature-review\SOURCES.md`

## 上游与血统

- **真正的工作主仓库**在 Coze 云盘：`C:\Users\16112\Coze\Drive\自媒体运营达人\所有对话\主对话\projects\论文写作Skills系列\`。本仓库是 2026-09-29 从「论文写作Skills全集-20260929.zip」+ Coze 主仓库 + 本地未发布新版**归拢合并**而成的只读快照。
- 归拢时的比对结论：zip 与 Coze 的 21 个公共 skill **逐字节一致**；差异仅两处——
  1. `00-文献检索Skill`：本仓库收的是**本地未发布五源版**（+AMiner 中文源 + 中文文献补充方案），并补回了 zip 版的 `related_skills` / 产线位置元数据；
  2. `B0-文献管理-zotero`：收的是 zip 版（9/29 较新），与 `C:\Users\16112\zotero-cite` 独立仓库（7/30 较旧）有差异，以 zip 为准。
- **修改 skill 源文件的正式入口仍是 Coze 主仓库**；本仓库用于归档、分发和 git 版本管理。同步回 Coze 前请先 diff。

## 安装

把整个 `skills\<目录>` 复制到对应工具的 skills 目录即可（每个 skill 自带 SKILL.md 说明触发条件与用法）：

| 工具 | 目录 |
|---|---|
| opencode | `~/.config/opencode/skills/` |
| Claude Code | `~/.claude/skills/` |
