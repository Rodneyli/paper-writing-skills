# AGENTS.md — paper-writing-skills

论文写作 Skills 全集的本地主仓库（归档 + 分发 + git 管理）。上游工作仓库在 Coze 云盘（见 README「上游与血统」）。

## 目录约定

- `skills/<期数-名称>/`：一个 skill 一个目录，入口固定为 `SKILL.md`（frontmatter 含 `name` / `description` / `source_book`）；附带的 `test-prompts.json`、`scripts/`、`assets/` 随目录走。
- `episodes/<期数-名称>/`：视频制作物料（口播稿、封面、图卡、发布物料），与 `skills/` 同期数对应，但**不参与 skill 运行**。
- `distillation/`：两本书的蒸馏产物，只读参考，不要当 skill 源改。
- `books/`：两本书的电子版本体，只读，不改动。
- `定稿skill包/`：对外分发的 zip，更新 skill 后如需重新打包再覆盖。
- `project-docs/`：Coze 项目级文档快照，只读参考。

## 工作规则

1. **所有文本文件一律 UTF-8**。历史上有 GBK 文件（旧 literature-search 系列），归拢时已转码；新写入禁止 GBK。
2. **Coze 云盘是正式工作区，本仓库是快照**：改 skill 源文件优先改 Coze 并同步到这里；如直接在本仓库改，记得回传 Coze。
3. 只增不删：不删 `episodes/`、`books/`、`distillation/` 内容；清理必须先问 Rod。
4. 版本状态以 README 的 Skill 总览表为准，更新 skill 时同步改表。
5. `skills/00-文献检索Skill/SKILL.md` 是**合并版**（本地五源未发布版 + 全集元数据），与 Coze 上的第0期发布版不同，不要互相覆盖。

## 构建 / 校验

- 无构建步骤。校验方式：检查每个 skill 目录存在 `SKILL.md` 且 frontmatter 的 `name:` 唯一。
- git 提交前检查是否含密钥（`.env`、`API_KEY` 等）；`scripts/.env.example` 是模板可以提交。
