# zotero-cite

把文献写进本地 Zotero 库，并生成 Word 可直接用的"活"引用片段（换样式全自动刷新）。

> 本 skill 为 AI Agent 设计：SKILL.md 是给 agent 的指令，`zotero_cite.py` 是执行脚本（纯 Python 标准库，零第三方依赖）。

## 它能干什么

| 命令 | 功能 |
|---|---|
| `doctor` | 环境自检：Zotero 装没装、开关开没开、账号通不通，缺什么告诉你怎么补（小白先用这个） |
| `search` | 查库里有没有某篇文献（防重复入库） |
| `add` | 写入文献：自动去重、自动反转义脏数据、`--check` 入库后逐字段回读验证 |
| `check` | 巡检已入库条目：与源数据或 Crossref 权威元数据比对（抓年份/实体残留等差异） |
| `cite` / `document` | 生成带 Zotero 活域的 docx 引用片段/整篇文档（Word 里 Refresh 即换样式） |
| `mkcol / move / delete / rmcol` | 文件夹与条目管理（写操作需用户确认） |

## 快速开始（小白版）

1. **装 Zotero 5.0+**：zotero.org 下载，一路下一步
2. **开一个开关**：Zotero → 设置 → 高级 → 常规 → 勾选 **"允许此计算机上的其他应用程序与 Zotero 通讯"**
3. **跑自检**：
   ```powershell
   python zotero_cite.py doctor
   ```
   全绿即用；红了按提示补（配 API key 的指引也在里面）

## 快速开始（Agent 版）

拿到本 skill 后：读 SKILL.md → 跑 `doctor --json` 检查环境 → 按 fix 指引引导用户修复 → 全绿后进入正常使用链路（search → add --check → cite）。

## 环境变量（可选配置）

| 变量 | 用途 | 默认 |
|---|---|---|
| `ZOTERO_API_KEY_FILE` | API key 文件路径 | `~/.config/zotero-cite/api-key` |
| `ZOTERO_USER_ID` | Zotero 用户 ID | 自动从 key 解析 |
| `ZOTERO_EXE` | zotero.exe 路径 | 自动探测默认安装位置 |

API key 获取：zotero.org 登录 → 设置 → Keys → Create new private key（全选权限）→ 存到 key 文件。

## 文件结构

```
zotero-cite/
├── SKILL.md           # skill 指令（agent 必读，含小白上手 + 完整用法 + 依赖说明）
├── zotero_cite.py     # 主脚本（仅标准库）
├── test_zotero_cite.py# 回归测试（python test_zotero_cite.py）
└── README.md          # 本文件
```

## 安全约定

- API key 只存本地文件，**绝不**出现在代码、日志、对话里
- 写操作（删除条目/文件夹/移动）执行前必须向用户确认
- 元数据入库前经 Crossref 权威核验，杜绝编造 DOI 和错误信息

## 依赖环境

- Zotero 5.0+ 桌面端（本地 API + Connector API 自 5.0 提供；实测 7 / 9 可用）
- Python 3.6+（仅标准库）
- Word 插件（仅 `cite`/`document` 生成活域引用时需要）
- 浏览器插件**不需要**（skill 走 Zotero 内置本地 API）
