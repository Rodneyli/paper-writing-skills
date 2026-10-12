# literature-search-starter 零基础配置指南

> **更省事的方式**：直接对你的 AI agent 说"帮我配置 literature-search"，它会自动完成本指南里的所有检查和写入操作，你只需按它提示注册账号、粘贴 Key。本文件是留给喜欢自己动手的人的自助版。

这份指南面向**从未配置过任何学术 API** 的用户。跟着做完，你的 AI agent 就拥有文献检索能力。

全程约 5 分钟。只有第 0–3 步是必需的，其余是可选增强。

---

## 第 0 步：确认你有 Python

打开终端（Windows 按 `Win+R` 输入 `powershell` 回车；Mac 打开"终端"），输入：

```bash
python --version
```

- 显示 `Python 3.x.x` → 跳到第 1 步
- 提示"不是命令"/"command not found" → 试试 `python3 --version` 或 `py --version`；都不行就去 [python.org](https://www.python.org/downloads/) 下载安装（Windows 安装时**务必勾选 "Add Python to PATH"**）。也可以直接让你的 AI agent 帮你装。

> 本 skill 不需要 pip 安装任何第三方包，Python 自带库就够。

## 第 1 步：放置 skill

把 `literature-search-starter` 整个文件夹复制到你的 agent 的 skills 目录：

| 工具 | 目录 |
|---|---|
| opencode | `~/.config/opencode/skills/` |
| Claude Code | `~/.claude/skills/` |

## 第 2 步：运行自检

```bash
python <skills目录>/literature-search-starter/scripts/litsearch.py doctor
```

你会看到类似输出：

```
=== literature-search 环境自检 ===
[INFO] Python 3.12.7
[OK]   OpenAlex 数据源（匿名模式）
[WARN] 未配置 OPENALEX_API_KEY。匿名目前可用但官方已要求 Key...
[OK]   Crossref 数据源
[OK]   arXiv 数据源
[WARN] 未配置 SEMANTIC_SCHOLAR_API_KEY，S2 源默认关闭...
```

结果解读：

| 标记 | 含义 |
|---|---|
| `[OK]` | 该数据源可用 |
| `[WARN]` | 不影响使用，但建议配置（见第 4、5 步） |
| `[FAIL]` | 该数据源连不上（多为网络/代理问题，见 FAQ） |

## 第 3 步：第一次搜索

```bash
python <skills目录>/literature-search-starter/scripts/litsearch.py search "你的研究主题" --limit 5
```

看到 JSON 格式的论文列表（标题、作者、期刊、摘要、引用量、PDF 链接）就说明**已经可以用了**。

到这里为止没有配置任何 Key。以下步骤是可选增强，建议有空时完成。

---

## 第 4 步（推荐）：配置 OpenAlex Key

OpenAlex 是主力数据源。官方已要求使用 Key（免费），匿名访问随时可能关闭。

1. 打开 https://openalex.org/settings/api （没有账号就用邮箱注册一个，约 30 秒）
2. 点击生成 API Key，复制那串字符
3. 先记下，第 6 步统一写入配置

免费额度为每天 $1（约数万次请求），日常使用绰绰有余。

## 第 5 步（可选）：配置 Semantic Scholar Key

S2 的摘要有 TLDR 精编版，质量高；但不配也不影响其他三个源。

1. 打开 https://www.semanticscholar.org/product/api#api-key-form
2. 填邮箱和用途（写 "personal academic research" 即可）
3. 提交后 Key 会发到邮箱，查收并复制

## 第 6 步：写入配置文件

1. 把 `scripts/.env.example` 复制一份，改名为 `scripts/.env`
2. 用记事本打开，把 Key 填到等号后面（不要加引号、不要留空格）：

```bash
OPENALEX_API_KEY=粘贴你的key
SEMANTIC_SCHOLAR_API_KEY=粘贴你的key
LITSEARCH_MAILTO=你的邮箱
```

> `LITSEARCH_MAILTO` 可留空，填了能进 OpenAlex/Crossref 的"礼貌池"，速率更稳定。
>
> ⚠️ `.env` 是你的私密文件，不要提交到 git、不要发给别人。

## 第 7 步：再跑一次自检

```bash
python <skills目录>/literature-search-starter/scripts/litsearch.py doctor
```

全部 `[OK]`、没有 `[WARN]`，配置完成。

---

## FAQ

**Q: 某个源 [FAIL] 了怎么办？**
A: 大概率是网络问题（公司防火墙/代理）。单独再试一次；如果只有个别源失败，其他源照常可用，脚本会自动跳过失败源，不影响搜索。

**Q: 搜索很慢？**
A: Crossref 偶尔慢（5-10 秒）属正常。可以 `--source openalex` 只用最快的源。

**Q: 能查中文文献吗？**
A: 这几个库对中文期刊收录不全。知网/万方没有免费 API，中文文献请让 agent 配合 Web 搜索。

**Q: Key 会不会泄露？**
A: Key 只存在你本机的 `.env` 或环境变量里，脚本只读取、不打印、不上传。
