---
name: zotero-cite
description: 操作本地 Zotero 文库并生成带"活"Zotero 域代码的 docx 引用片段。当用户说"把文献存入 Zotero"、"生成 Zotero 引用"、"插入文献引用"、"把这篇论文加到 Zotero 并给我引用格式"、"zotero 引用片段"时触发。适用于：AI 检索文献后，将选中文献写入本地 Zotero 库，并输出可直接粘贴进 Word 的 docx 片段——其中的引用和参考文献是 Zotero Word 插件可识别、可刷新、可换样式的活域。
---

# zotero-cite

把选中文献写入本地 Zotero 库，并生成带活 Zotero 域代码的 docx 引用片段（粘贴进 Word 后可用 Zotero 插件刷新/换引用格式）。

## 🚀 小白 5 分钟上手（不读下文也能用）

**第 1 步：装 Zotero**（只需一次）
官网 zotero.org 下载安装，一路"下一步"即可（需 5.0+ 版本）。

**第 2 步：开开关**（只需一次）
打开 Zotero → 设置 → 高级 → 常规 → 勾选 **"允许此计算机上的其他应用程序与 Zotero 通讯"**。

**第 3 步：跑自检**（每次换电脑/报错时跑）
```powershell
python zotero_cite.py doctor
```
全绿 = 直接可用；红了 = 它告诉你差什么、怎么补，补完再跑一次。

**第 4 步：三个最常用的命令**（复制即用，把中文部分换掉）
```powershell
# 查库：先搜一下，确认库里有没有这篇（避免重复入库）
python zotero_cite.py search "电子口碑 eWOM"

# 存文献：把"文献.json"存进 Zotero（自动去重+打标签）
python zotero_cite.py add 文献.json --tag 我的文献

# 生成引用：把 KEY（search 结果第一列）变成可粘贴进 Word 的引用片段
python zotero_cite.py cite KEY --text "正文句子" -o 引用.docx
```

**第 5 步：贴进 Word**
打开生成的 docx → 全选复制 → 粘进你的论文 → 点 Word 菜单栏 "Zotero" → **Refresh**，引用自动变标准格式。

> 文献.json 长什么样？见下方「2. 入库（add）」的示例。让 AI 帮你把论文元数据写成这个文件即可。

**新手高频问题**
- 命令报"无法连接 localhost:23119" → 第 2 步的开关没开，或 Zotero 没启动
- 报"API key not found" → 缺 `~/.config/zotero-cite/api-key` 文件（找管理员/技术同学要）
- Word 里引用不刷新 → Word 的 Zotero 插件没装（打开 Word 看菜单栏有没有 "Zotero"）

---
## 🤖 Agent 接入指南（用户把 GitHub 链接丢给 AI 时，AI 按此接管）

拿到本 skill 后按顺序自动完成环境接管：

1. **读本文件**——命令用法见下方「用法」；环境要求见「前置条件」
2. **跑环境自检**：`python zotero_cite.py doctor`（加 `--json` 拿结构化结果供程序判断）
   - 全绿 → 直接进入第 4 步
   - 有 ❌ → 按输出里的 fix 指引引导用户逐项修复（装 Zotero / 开开关 / 配 key），修复一项重跑一次复查
3. **首次使用引导用户配置**（三选一，见下表）：
   - 申请 API key：zotero.org 登录 → 设置 → Keys → Create new private key（全选权限）→ 存到 key 文件
   - 用户 ID：不用手动配，脚本从 key 自动解析
   - zotero.exe 非默认路径：设 `ZOTERO_EXE`
4. **常用操作链路**：`search`（查库防重复）→ `add --check`（入库+自动验证）→ `cite`/`check`（引用与巡检）
5. **约定**：写操作（mkcol/move/delete/rmcol/数据修复）前先向用户确认；API key 内容绝不输出到对话/日志/代码

### 环境变量（可移植配置）

| 变量 | 用途 | 默认 |
|---|---|---|
| `ZOTERO_API_KEY_FILE` | API key 文件路径 | `~/.config/zotero-cite/api-key` |
| `ZOTERO_USER_ID` | Zotero 用户 ID | 自动从 key 解析（无需设置） |
| `ZOTERO_EXE` | zotero.exe 完整路径 | 自动探测默认安装位置 |

---

## 前置条件

### 1. Zotero 桌面端版本：5.0 及以上（实测 7 / 9 均可用）

- 本地 API（`localhost:23119`）与 Connector API（`/connector/saveItems`）自 **Zotero 5.0** 起提供；4.x 及更早版本没有，脚本无法工作
- **未运行时脚本会自动拉起**（默认路径找不到时需设环境变量 `ZOTERO_EXE` 指向 zotero.exe）并等待就绪
- 查版本：Zotero 菜单 → 帮助 → 关于 Zotero

### 2. Local API 开关（必须开启，agent 控制 Zotero 的钥匙）

Zotero 设置 → **高级** → **常规** → 勾选 **"允许此计算机上的其他应用程序与 Zotero 通讯"**（Allow other applications on this computer to communicate with Zotero）。

验证开关是否生效（两种方式任选）：
- 浏览器访问 `http://localhost:23119/connector/ping`，页面显示 `Zotero Connector Server is running` 即正常
- 或运行 `zotero_cite.py search "test" --limit 1`，能出结果即正常

### 3. Zotero 账号 + 同步（管理类操作需要）

`mkcol / move / delete / rmcol / 数据修复` 走 Web API（`api.zotero.org`），依赖：
- Zotero 已登录账号（Zotero 菜单 → 设置 → 同步，显示你的账号）
- **同步已开启**（设置 → 同步 → 开启"自动同步"，或至少手动点过同步）——Web API 的改动经云端同步回本地，未同步时本地看不到改动
- API key 存于 `~/.config/zotero-cite/api-key`（绝不输出到对话/日志/代码）

### 4. Word 的 Zotero 插件（仅引用片段功能需要）

- `cite` / `document` 生成的 docx 含 **Zotero 活域**（`ZOTERO_ITEM CSL_CITATION` + `ZOTERO_BIBL`），必须在 **Word 里安装 Zotero 插件**才能识别、刷新（Refresh）、切换引用样式
- Word 插件随 Zotero 桌面端自动安装（Word 菜单栏出现"Zotero"标签即已装好）；装不上时在 Zotero 设置 → 引用 → Word 处理器 里修复
- 只做 `add / search / check / collections` 等文献管理操作时**不需要** Word 插件

### 5. 浏览器 Zotero Connector 插件（可选，skill 不依赖）

- skill 的写入走的是 **Zotero 内置本地 Connector API**，与浏览器插件无关——浏览器插件**未安装也能正常工作**
- 浏览器插件只用于你**手动**从网页/数据库一键抓文献进库（如你自己之前收文献的场景），属于用户侧便利工具

### 6. Python

- `python`（仅标准库，无第三方依赖）

## 架构（重要）

- **读**：Local API `http://localhost:23119/api/users/0/...`（只读，GET，快）
- **新建条目**：Connector API `POST http://localhost:23119/connector/saveItems`（只能新建，不返回 key，需写入后按标题检索拿 key）
- **修改/移动/删除/建文件夹**：Web API `https://api.zotero.org/users/<你的用户ID>/...`，API key 存于 `~/.config/zotero-cite/api-key`（绝不输出到对话/日志/代码）
- 写入前必须先去重（按 DOI 或标题 search），Connector 重复写入会产生重复条目
- Connector 保存的条目会进入 Zotero 界面当前选中的文件夹，可用 `--collection` 或 `move` 纠正
- Web API 的改动经 Zotero 同步回本地，有秒级延迟

## 用法

脚本：`skills/zotero-cite/zotero_cite.py`

### 1. 检索库内条目（防重复 / 找 key）

```powershell
python zotero_cite.py search "关键词" --limit 10
```

可选过滤：`--fulltext`（含 PDF 全文，qmode=everything）、`--tag 标签名`、`--collection 文件夹名`。

输出：`KEY<TAB>年份<TAB>作者<TAB>标题`

### 2. 入库（add）

先把文献元数据写成 Zotero API 格式的 JSON 文件（UTF-8），再：

```powershell
python zotero_cite.py add item.json --tag ai-agent --collection "文件夹名" --check
```

`--collection` 可选，指定后条目自动归入该文件夹（走 Web API 补一次移动）。
`--check` 可选，入库后自动读回条目与源数据逐字段比对，输出验证结论。

**入库自带四道防线**：
1. **去重**：按 DOI 全文检索（`qmode=everything`——Zotero 本地搜索默认不索引 DOI 字段）+ 归一化标题精确匹配双保险；已存在条目返回 `duplicate: true`，绝不重复写入
2. **反转义**：所有文本字段入库前自动 `html.unescape`，杜绝 `&amp;` 类脏数据
3. **入库后验证**（`--check`）：读回 Zotero 条目，与源 item.json 逐字段比对（标题/期刊/DOI/年份/作者），不一致或字段缺失立即报警
4. **集合归属**：写文件夹 + 打标签后落库

item.json 示例（journalArticle）：

```json
{
  "itemType": "journalArticle",
  "title": "论文标题",
  "creators": [{"creatorType": "author", "firstName": "San", "lastName": "Zhang"}],
  "date": "2024",
  "publicationTitle": "期刊名",
  "volume": "12", "issue": "3", "pages": "1-20",
  "DOI": "10.xxxx/xxxxx",
  "abstractNote": "摘要……",
  "url": "https://...",
  "language": "zh-CN"
}
```

返回 `{"key": "XXXXXXXX", "duplicate": false, "check": {...}}`；若已存在则返回已有 key 且 `duplicate: true`（不会重复写入）。

### 2.5 验证已入库条目（check）

```powershell
python zotero_cite.py check KEY [--source item.json]
```

- 给 `--source`：与源 item.json 逐字段比对（含原文级检查，能抓 `&amp;` 实体残留）
- 不给：按条目 DOI 调 Crossref 权威元数据比对（标题/期刊/年份），能发现线上首发年份 vs 正式刊期年份的差异
- 输出逐字段 `✅/⚠️` 明细 + 结论；适合批量巡检（对文件夹内所有条目循环调用）

### 3. 生成引用片段（cite）

```powershell
python zotero_cite.py cite KEY1 [KEY2 ...] --text "正文句子" -o 输出.docx
```

- 多 key 会合并为一个引用域（多篇同时引用）
- 生成的 docx 含：`ZOTERO_ITEM CSL_CITATION` 活域 + `ZOTERO_BIBL` 参考文献活域
- 引用格式跟随 Zotero 当前默认样式（Local API `include=bib/citation` 的输出）
- `--text` 可省略，则片段只有引用本身

### 3.5 整篇文档生成（document）

从 JSON 规格文件生成整篇 docx：多段正文、段内任意位置插入引用、每处可独立设 `suppress_author`，末尾自动生成参考文献列表（按首次出现顺序）。

```powershell
python zotero_cite.py document 规格.json -o 输出.docx
```

规格 JSON 结构：

```json
{
  "title": "可选标题（渲染为加粗大字号）",
  "paragraphs": [
    [
      {"text": "……Gerlich"},
      {"keys": ["994CK9QP"], "suppress_author": true},
      {"text": "对666名受访者……"}
    ],
    [
      {"text": "综述证据表明……"},
      {"keys": ["48RZKM6M", "TRZLYCKL"]}
    ]
  ]
}
```

规则：
- 每段是 seg 列表；seg 只有 `text`（纯正文）、`keys`（引用，可多个 key 合并一个域）、或两者都有
- `suppress_author: true` 时该域只渲染年份——正文已写了作者名时用（防重复年份）
- 参考文献按全文中 key 首次出现顺序排列；`--collection` 不可用，归属由 key 决定

### 4. 文件夹与条目管理（Web API，需 key）

```powershell
zotero_cite.py collections                          # 列出所有文件夹（key/名称/父级）
zotero_cite.py mkcol "文件夹名" [--parent 父key]      # 新建文件夹
zotero_cite.py move 条目key 文件夹key [--remove 文件夹key2]  # 移入（可同时移出另一个）
zotero_cite.py delete 条目key                        # 删除条目（进回收站）
zotero_cite.py rmcol 文件夹key                       # 删除文件夹（不删里面的条目）
```

`move`/`delete` 属写操作：移动跨文件夹、删除条目或文件夹前，向用户确认目标和影响。

## 典型工作流（agent 侧）

1. **入库前核验**（要求：文献真实存在、信息准确）：组装 item.json 前，先对文献清单跑 `litsearch.py verify <清单.json>`——每篇与 Crossref 权威元数据比对，`❌ 不存在`/`⚠️ 有出入` 的条目先修正，全部 `✅` 才进入入库
2. 用户选定文献 → agent 组装 item.json → `add --check` 拿 key（自动去重 + 反转义 + 入库后逐字段验证）
3. 可选批量巡检：对文件夹内所有条目循环 `check KEY`（Crossref 模式），发现年份/实体差异及时修正
4. `cite KEY --text "正文"` 生成片段 docx 给用户；或写整篇规格 JSON → `document` 生成完整文档
5. 用户打开 docx，全选复制粘贴进自己的论文 Word；或直接以片段/文档为底稿继续写
6. 在 Word 里点 Zotero 插件 Refresh，引用即与库联动，可随意切换引用样式

## 测试

```powershell
python test_zotero_cite.py
```

覆盖纯函数（CSL 转换、引用域构造、suppress_author、参考文献 XML 组装、docx 打包），不依赖 Zotero 运行。改完代码跑一遍再宣布完成。

## ⚠️ 正文写作规范（防重复/防格式打架）

正文里**零手写引用标注**——引用标注全部由 Zotero 域生成。手写 `(Author, 2024)` 会与域渲染重复，且在用户切换样式后永远是错的。

- **纯标注**：句子不提及作者 → 句末直接插域
- **叙述性提及**："Gerlich（2025）发现……" → 作者名写进句子，该处域的 bundle 设 `suppress_author=True`（Zotero 原生 suppress-author），只渲染 `(2025)`

## 注意事项

- 生成片段中的显示文本（如 `(Author, 2026)`）是占位符，用户在 Word 中 Refresh 后由 Zotero 按当前样式重绘，这是正常现象
- 若 Zotero 未运行，本地命令会自动拉起 Zotero（最长等待 90 秒）；纯 Web API 操作（mkcol/move/delete/rmcol/check 数据修复）不依赖本地运行，但依赖账号登录 + 同步开启（见前置条件 3）
- 桌面上遗留的 `zotero-cite测试片段.docx` 是验证用文件，可删
- **环境自检速查**：① `localhost:23119/connector/ping` 通 → Local API 开关 OK；② 本地操作报 404 → Zotero 版本过低；③ Web API 报 403/401 → API key 失效或未登录；④ Word 里域不刷新 → 检查 Word 插件是否安装（前置条件 4）
