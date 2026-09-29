# AGENTS.md — 论文写作Skills 系列项目

## 项目定位

抖音系列「论文写作Skills」：每期一个 skill，视频演示"给 AI 装一个 skill、一句话搞定一个科研环节"，skill 打包评论区自取。受众为研究生和科研新手。

七工位产线：**检索(0) → 筛选(1-3) → 精读(4-7) → 方向发现(8-11) → 综述撰写(12-14) → 正文撰写(15-17) → 投稿返修(18)**，共 19 期主系列 + 2 期加更。

## 目录约定

| 路径 | 内容 |
|---|---|
| `SUITE_INDEX.md` | **体系宪法**：工位流水线、期数表、合并映射、统一依赖图、溯源表。所有体系级改动先改这里 |
| `EPISODE_PLAN.md` | 视频期数规划：每期钩子/要点/串场/状态、制作约定、待办 |
| `stage1-search/` … `stage7-rebuttal/` | 按工位组织的 skill，每 skill 一个子目录（SKILL.md + test-prompts.json） |
| `bonus/` | 可选加更 skill（B1 头脑风暴、B2 博士蓝图），不发则不动 |

## 核心规则

1. **SUITE_INDEX 是宪法**：改依赖关系、改期数、加/删/合并 skill，一律先改 SUITE_INDEX 和 EPISODE_PLAN，再动 skill 正文，不反过来。
2. **依赖表唯一**：每个 skill 的 frontmatter `related_skills` 和底部"相关 skills"段必须与 SUITE_INDEX §5 依赖表一致（depends-on / contrasts-with / composes-with 三字段）。
3. **已做视频的 3 个 skill 正文不动**：`literature-search`（第0期已发布）、`critical-creative-paper-reading`（第4期待发）、`matrix-method-topic-selection`（第9期待发）。只允许补引用类字段。
4. **books/ 蒸馏归档不动**：`C:\Users\16112\.config\opencode\skill-library\books\` 是两本书的蒸馏审计档案（本项目的溯源依据），禁止修改、删除、移动。
5. **命名**：skill 目录用英文小写连字符（如 `research-quality-checklist`）；中文名只出现在正文标题和期数表。
6. **新 skill 进对应工位目录**，按现有 SKILL.md 结构写（R/I/A1/A2/E/B + 产线位置行 + 相关 skills 段）。

## 视频制作约定

- **制作流程以 `short-video-workflow/SKILL.md` 为准**（Rod 的抖音短视频工作流 v2.4）：Step 0 选题验证 → 0.5 爆款调研 → 1 主副类型识别 → 2 选配物料 → 3 制作计划 → 4 口播稿 → 5 封面 → 6 发布物料 → 7 数据复盘。每期开一个项目文件夹：`YYYY-MM-DD-分类标签-选题名/`，project.md 为总控台
- 本系列选题统一是"技能交付"主类型（短打型 60-120s）+ "Prompt交付"副类型（skill 压缩包）
- 每期发布物：口播稿 + 发布物料（标题×2、封面标题、标签、正文、置顶评论）+ slides + skill 压缩包
- 统一结构：痛点开场 → 装 skill 演示 → 方法拆解 → 效果展示 → 评论区自取 + 串场
- 串场话术见 SUITE_INDEX §6 指针表；品牌元素沿用第 0 期（猫头鹰头像 + 品牌栏），视觉规范见 `short-video-workflow/references/visual-style-guide.md`
- 工作流里调度的部分 skill（hot-content-research、cover-brand-bar、echart、rediantong 等）在本 agent 环境没有，制作时用本环境等价能力替代（frontend-slides、xhs-cover、生图能力等）
- 期号已按产线重排：已做待发的两个视频对应第 4、9 期（素材位置待 Rod 提供后核对期号表述）

## 验证

- 无构建/测试命令。一致性验证：grep 所有 `related_skills` 的 slug 与依赖表逐条核对；确保无 `{{}}` 占位符残留
- test-prompts.json 可选接 darwin-skill 跑测试（当前均标记"未运行"）
- Python 用 `C:/ProgramData/anaconda3/python.exe`

## 当前进度

- [x] 体系架构（SUITE_INDEX + EPISODE_PLAN）
- [x] 21+2 个 skill 全部理顺（3 合并、1 新蒸馏、拷贝+依赖重写）
- [ ] 第 1 期视频制作（优先：兑现第 0 期评论区"AI 批量筛论文"承诺）
- [ ] 第 4、9 期素材期号核对
- [ ] git 首次提交（Rod 拍板后执行）
