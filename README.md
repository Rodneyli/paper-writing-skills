# paper-writing-skills · 论文写作 Skills 系列

面向 AI Agent（opencode / Claude Code / OpenClaw 等支持 SKILL.md 格式的工具）的学术论文写作 Skill 集合。

## 系列路线图

| 期数 | Skill | 定位 | 状态 |
|---|---|---|---|
| **#0** | **literature-search-starter** | 文献检索底座：五源联搜，中英文覆盖 | ✅ 已发布 |
| #1 | 论文精读 | 待规划 | 🔜 |
| #2 | 文献综述 | 待规划 | 🔜 |
| #3 | 选题 | 待规划 | 🔜 |

> 系列从文献检索起步——后续的精读、综述、选题，都建立在"先搜到论文"这个底座之上。

## #0 基石：literature-search-starter

免费学术文献检索基础能力。装好就能用，零基础也有引导。

**核心能力**：
- 一条命令同时检索 **5 个免费学术数据源**，自动合并去重
- 数据源：**OpenAlex**（主力）· **AMiner**（中文文献）· **Crossref** · **arXiv** · **Semantic Scholar**
- 纯 Python 标准库实现，**零第三方依赖**
- 两个免费 Key 可选配置（各约 1 分钟申请；**OpenAlex 不申请也能用**）
- 内置 `doctor` 环境自检：一键检查 Python、各数据源连通性、Key 配置状态
- 零基础引导：新手对 agent 说一句"帮我配置"即可，agent 全程代操作

**中文文献说明**：AMiner 覆盖中英文文献（部分期刊收录可能存在滞后）；要查最新中文文献，可搭配 [cookjohn/cnki-skills](https://github.com/cookjohn/cnki-skills) 走知网检索。

## 安装

将 `literature-search-starter` 整个文件夹复制到你的 skills 目录：

| 工具 | 目录 |
|---|---|
| opencode | `~/.config/opencode/skills/` |
| Claude Code | `~/.claude/skills/` |

## 配置

- 零基础用户：直接对你的 agent 说"帮我配置 literature-search"，agent 会引导你完成
- 动手党：详见 `literature-search-starter/SETUP.md`（约 5 分钟）

## 参考链接

- AMiner 开放平台文档：https://www.aminer.cn/open/docs
- AMiner Open Academic Skills 完整指南（飞书）：https://zhipu-ai.feishu.cn/wiki/TlLvwTEOZiZCyVkfxptc516SnBb
