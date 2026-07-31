---
name: literature-search-starter
description: 免费学术文献检索基础能力（零基础分享版）。当用户说"查文献""找论文""搜一下某个主题的研究""检索相关资料"，或其他学术 skill（论文写作、选题、综述）需要文献检索能力时触发。开箱即用、内置 doctor 环境自检；检测到用户是新手时 agent 主动引导配置（用户只需注册账号+粘贴 Key，其余全由 agent 完成）。输出统一 JSON（标题/作者/年份/期刊/DOI/摘要/引用量/开放获取PDF）。
---

# 文献检索基础能力 · 零基础分享版（literature-search-starter）

## 首次使用

**Agent 注意：检测到下述信号时，主动进入"引导配置流程"，不要让用户自己碰终端**：
- 用户说"帮我配置""怎么开始用""第一次用"
- 首次调用本 skill 且 doctor 显示未配置任何 Key
- 用户明显是小白（问"什么是 API Key""终端是什么"）

### Agent 引导配置流程

全程由 agent 执行命令、解读结果，**一次只引导一步**，等用户完成再进行下一步。用户只需要做两件事：在网页上注册/申请、把 Key 粘贴给 agent。

1. **跑自检**：agent 执行 `python scripts/litsearch.py doctor`，把结果翻译成人话告诉用户（哪几个源能用、缺什么）
2. **缺 Python 才处理**：若命令找不到 Python，帮用户安装或给出其平台的确切步骤，装完重跑 doctor
3. **引导申请 OpenAlex Key**（推荐）：告诉用户"打开 https://openalex.org/settings/api ，邮箱注册后点生成 Key，复制发给我"。等用户粘贴
4. **引导申请 AMiner Key**（推荐）：告诉用户"打开 https://open.aminer.cn/open/board?tab=control ，注册后在个人设置创建 API Token，复制发给我"。等用户粘贴
5. **引导申请 S2 Key**（可选）：告诉用户"打开 https://www.semanticscholar.org/product/api#api-key-form ，填邮箱和用途提交，Key 会发到邮箱，收到后发给我"。用户嫌麻烦可跳过
6. **写入配置**：agent 把用户粘贴的 Key 写入 `scripts/.env`（从 `.env.example` 复制模板）。**不要把 Key 值打印回对话或写进其他文件**
6. **复检**：再跑一次 `doctor`，全部 `[OK]` 后恭喜用户，并用他的研究主题演示一次 `search`

规则：
- 用户只粘贴 Key 时，agent 默认执行第 6 步（写入配置），不用重复询问
- 用户明确说"不想申请"，直接进入匿名模式使用，不再纠缠
- 任何时候不要把用户的 Key 提交 git、发到 issue/PR、或写进日志

## 定位

这是一个**底座型 skill**：为论文写作、选题、综述类 skill 提供文献检索能力，也可单独使用。

设计原则：**拿到就能用**。不装任何第三方依赖（纯 Python 标准库）；所有数据源免费，匿名调用目前可用，配上免费 Key（申请合计约 2 分钟）则长期稳定。

## 环境要求

- Python 3.6+（任意发行版，无需 pip install 任何东西）

## 用法

### 环境自检

```bash
python scripts/litsearch.py doctor
```

检查 Python 版本、四个数据源连通性、Key 配置状态，并打印下一步引导。

### 搜索文献

```bash
python scripts/litsearch.py search "<关键词>" [--source all|openalex|crossref|arxiv|s2] [--limit 10] [--year-from 2020] [--year-to 2026] [--sort relevance|cited]
```

示例：

```bash
python scripts/litsearch.py search "job crafting" --limit 8 --year-from 2021 --sort cited
```

### 按 DOI 获取单篇元数据

```bash
python scripts/litsearch.py fetch "10.5465/amj.2022.0426"
```

### 输出格式

统一 JSON 到 stdout，每条记录字段：

| 字段 | 说明 |
|---|---|
| `title` / `authors` / `year` / `venue` | 基础元数据 |
| `doi` | 无 DOI 时为 null（如 arXiv 预印本） |
| `url` | 落地页链接 |
| `pdf_url` | 开放获取 PDF，无则 null |
| `abstract` | 摘要，源站未提供则为 null |
| `citations` | 引用量（arXiv 不提供，为 null） |
| `source` | openalex / crossref / arxiv / semantic_scholar |

多源合并时按 DOI/标题自动去重。某个源失败不会阻塞其他源，错误信息收在输出的 `errors` 字段里。

## 数据源

| 源 | 覆盖 | Key | 说明 |
|---|---|---|---|
| **OpenAlex** | 2.5 亿+ 文献，全学科 | 免费 Key（官方已要求，1 分钟申请） | 主力源，含摘要/引用量/OA链接 |
| **AMiner** | 中英文文献/学者/专利/机构 | 免费 Key（需申请，约 2 分钟） | 中文文献覆盖好，含摘要/作者；须配 Key |
| **Crossref** | 1.6 亿+ DOI 记录 | 不需要 | 元数据权威，多数无摘要 |
| **arXiv** | 物理/CS/数学等预印本 | 不需要 | 全文免费 |
| **Semantic Scholar** | 2 亿+，含 TLDR | **强烈建议配 Key** | 无 Key 时共享池常年 429，基本不可用 |

`--source all`（默认）= OpenAlex + Crossref + arXiv；当检测到 Semantic Scholar Key 时自动加入 S2；当检测到 AMiner Key 时自动加入 AMiner。

## 配置指南（可选增强）

在 `scripts/` 目录下创建 `.env` 文件（可参考 `scripts/.env.example`）：

```bash
# 推荐。OpenAlex 免费 Key，申请约 1 分钟：
# https://openalex.org/settings/api
# 免费额度 $1/天（约数万次请求，日常用不完）。匿名调用目前仍放行，但官方已明确要求 Key，随时可能收紧
OPENALEX_API_KEY=

# 推荐。AMiner 免费 Key，申请约 2 分钟：
# https://open.aminer.cn/open/board?tab=control
# 生成 Token 后写入。覆盖中英文文献、学者、机构、专利
AMINER_API_KEY=

# 可选。填你的邮箱，进入 OpenAlex/Crossref "礼貌池"，速率更稳定
LITSEARCH_MAILTO=you@example.com

# 可选但推荐。Semantic Scholar 免费 Key，申请约 1 分钟：
# https://www.semanticscholar.org/product/api#api-key-form
SEMANTIC_SCHOLAR_API_KEY=
```

至少配一个 Key（OpenAlex 或 AMiner）即可用；两项都配效果最佳。脚本会自动读取系统环境变量里已有的同名 Key，无需重复配置。

### 速率参考

| 源 | 速率 |
|---|---|
| OpenAlex（免费 Key） | $1/天免费额度（约数万次请求） |
| AMiner（免费 Key） | 免费，数百次/天可用 |
| Crossref | 免 Key，约 50 次/秒（礼貌池） |
| arXiv | 免 Key，建议间隔 3 秒 |
| S2（有 Key） | 1 次/秒 |

脚本已对 429 做自动退避重试（最多 2 次）。

## 给其他 skill 的集成方式

在依赖文献检索的 skill 的 SKILL.md 中加入：

> 需要检索文献时，调用 literature-search skill 的脚本：
> `python <skills目录>/literature-search/scripts/litsearch.py search "<query>" --limit 10`
> 返回统一 JSON 结构，逐条使用，禁止编造 DOI 和链接。

## 注意事项

1. **禁止编造**：DOI、链接、摘要一律以脚本返回为准；字段为 null 就说明源站没提供，不要自己补。
2. **中文文献**：配置 AMINER_API_KEY 后 AMiner 源可覆盖中英文文献，但核心期刊收录通常滞后 1-2 个季度；要查最新中文文献见下方补充方案。
3. **`--sort cited` 的行为**：先按相关性取 3×limit 候选，再本地按引用量重排（直接让 API 按引用量排会严重稀释相关性）。
4. **初次调用某源失败**：先单独 `--source <源>` 小 limit 试水，打印原始返回排查。

## 中文文献补充方案（可选）

AMiner 对中国核心期刊的收录滞后（如《南开管理评论》2026 年论文可能到 2025 年都没进库）。需要检索**最新中文文献**时，可搭配社区方案 [cookjohn/cnki-skills](https://github.com/cookjohn/cnki-skills)（通过 Chrome 操作知网，支持期刊/年份/CSSCI 过滤的检索）：

- **适用场景**：查 CNKI 最新收录的核心期刊论文（AMiner 覆盖不到的）
- **前提条件**：Chrome 已登录知网且账号有机构/个人下载权限
- **常用命令**：`cnki-advanced-search <期刊名> <关键词> <年份范围>`
- **注意**：依赖浏览器操作和登录态，非开箱即用；作为 AMiner 的补充而非替代

其他备选：[ExquisiteCore/CNKI-search](https://github.com/ExquisiteCore/cnki-search)（Go CLI 直连知网接口，更轻量）、[lechan775/cnki-vip-reader](https://github.com/lechan775/cnki-vip-reader)（知网+维普双库自动检索）。

## 参考链接

- AMiner 开放平台文档：https://www.aminer.cn/open/docs
- AMiner Open Academic Skills 完整指南（飞书）：https://zhipu-ai.feishu.cn/wiki/TlLvwTEOZiZCyVkfxptc516SnBb
