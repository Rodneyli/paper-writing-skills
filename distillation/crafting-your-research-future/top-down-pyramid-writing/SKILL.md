---
name: top-down-pyramid-writing
description: |
  用户需要组织学术论文结构、撰写引言和摘要、或论文被评审批评"逻辑混乱""结构不清"时调用。
  用户会说"论文引言写不好""不知道怎么组织论文结构""论文读起来逻辑混乱""被评审说结构不清"
  "摘要怎么写""怎么让审稿人快速理解我的贡献""论文论证不清晰"。
  不适用于：理论数学论文、短报告/海报/幻灯片、已经完成实验需要反向整理材料的场景。
  与 logic-argument-5steps (v04，写作方法论) 的区别：本 skill 是"怎么写"（直接生成结构），
  v05 10-30-test 是"怎么检"（写作后检验可读性）。
source_book: 《学术研究：你的成功之道》(Crafting Your Research Future) 凌晓峰, 杨强
source_chapter: 第6章 6.1节 逻辑论证五大步骤 + 6.4节 自上而下金字塔式写作 + 6.5节 层次结构与标题
tags: [论文写作, 学术写作, 金字塔结构, 论文结构, 逻辑论证]
related_skills: []
---

# 自上而下金字塔写作法

## R — 原文 (Reading)

> 自上而下细化的写作方法，又称金字塔式写作……要求作者按照从宽泛到具体的流程展示研究工作。论文应该有一个中心主题：(1)研究问题很重要；(2)现有方法存在不足；(3)我们提出了新方法；(4)我们证明新方法更优；(5)讨论优缺点。在写论文时需要在不同细节层次上多次强调这个中心论点：标题(10字)→摘要(200字故事)→引言(摘要每句扩展为3～20句)→正文各节→结论。引言中的每个论点都可以对应到相同顺序下摘要中的每个论点，不同之处在于引言中的论点更加细化和具体。
>
> — 凌晓峰, 杨强，《学术研究：你的成功之道》第6章

---

## I — 方法论骨架 (Interpretation)

自上而下金字塔写作法是将论文组织成一座"金字塔"：塔尖是最凝练的概括（标题+摘要），塔身是逐层展开的论证（引言→正文各节→结论），每一层都是对上一层相同论点的细化而非引入新论点。

金字塔的核心是五步逻辑论证链，这个论证链在论文的每一个层级中都完整出现，只是详略不同：

1. **重要性锚定** — 论文开篇必须建立"这个研究问题值得被解决"的认知，通过引用前人论述、展示应用场景、提供数字证据来建立紧迫感
2. **建立缺口 (Gap)** — 明确指出现有方法的局限，不是泛泛说"还不够好"，而是具体说"A方法在X场景下失效""B方法需要Y假设不成立时"
3. **宣告贡献 (Contribution)** — 用主动语态（"We propose..."）明确陈述你提出的新方法/理论/设计
4. **比较性证明** — 通过理论推导 + 实验对比 + 显著性检验，证明你的方法在特定维度上优于现有方法
5. **诚实讨论局限** — 在结论中冷静分析方法的适用范围和弱点，这不是减分项，而是建立学术可信度

创建金字塔的操作顺序是**先写塔尖再建塔身**：
- 先写出五句话草稿（用自然语言，每句对应一个论证步骤）
- 压缩为 200 字摘要（五个句子各压缩为一句）
- 将摘要每句扩展 3-20 句 → 引言（15-30句）
- 引言的"现有工作不足"扩展为一节 → Related Work
- 引言的"我们提出了Z"扩展为多节 → Method
- 引言的"证明Z更好"扩展为多节 → Experiments
- 结论 = 摘要的再次重述 + 局限讨论 + 未来工作

每一节开始用一个段落概述本节内容（这一小段本身也是该节的金字塔塔尖），然后逐小节展开。节/小节/次小节的层次深度不超过 3-4 层。

使用特定的引导词帮助读者在金字塔中导航：
- 高层概述："Generally speaking""at a high level""the intuition is"
- 进入细节："More specifically""For example""We provide details as follows"

---

## A1 — 书中的应用 (Past Application)

### 案例: 搜索引擎论文写作示例（书中 6.4 节附录）

书中以一篇关于"集成分层浏览的搜索引擎"的论文为例，展示了摘要→引言的金字塔细化过程。

**摘要（200字故事，塔尖）**：

| 论证步骤 | 摘要中的表述 | 长度 |
|---------|------------|------|
| 1. 问题重要 | `General web search engines play an important role in people's life.` | 1句 |
| 2. 现有不足 | `However, most of them return a flat list of webpages based only on keywords search.` | 1句 |
| 3. 我们提出Z | `We report our attempt towards building an integrated web search engine with a topic hierarchy. We implement a hierarchical classification system and embed it in our search engine. We also design a novel user interface...` | 3句 |
| 4. 证明Z更优 | `the results, including a user study, have shown that it is better than the flat search engine` | 1句 |
| 5. 讨论局限 | `Though the coverage of our current search engine is still small, ...it has a great potential as the next-generation search engine.` | 1句 |

**引言（对摘要的逐句展开，塔身第一层）**：

| 摘要原文 | 引言展开 |
|---------|---------|
| `General web search engines...play an important role` | `General web search engines...play an important role in helping people to find information they want. According to (SEMPO 2009), more than 14 billion searches are conducted globally in each month.` — 加了数据支撑（14亿次/月）和引用 |
| `most of them return a flat list...based only on keywords` | `As queries are usually related to topics, simple keyword queries are often insufficient to express such topics...Many keywords (such as china, chip) are also ambiguous without a topic.` — 加了具体例子（china/chip歧义） |
| `It would be ideal if hierarchical browsing and keyword search can be seamlessly combined` | `It would be ideal if hierarchical browsing and keyword search can be seamlessly combined, to narrow down the scope of search, and to remove ambiguity. The original Yahoo! Search Engine is a topic directory with hierarchy for easy browsing.` — 加了历史背景（Yahoo!）和更细化的收益说明 |
| [引入搜索引擎背景] | `However, ...` [继续展开搜索技术发展背景] |

**关键观察**：
- 摘要和引言共享完全相同的论证顺序（五步逻辑链）
- 引言没有引入任何摘要中没有的新"论点类型"，只是将每个论点"掰开揉碎"
- 引言用数据、例子、引用让每个论点更具体、更有说服力
- 作者在撰写时先写了摘要（塔尖），然后才将摘要逐句扩展为引言（塔身第一层）

---

## A2 — 触发场景 (Future Trigger) ★

### 用户会在什么情境下需要这个 skill?

1. **被评审批评论文结构混乱** — 用户收到了"逻辑不清晰""不知道贡献在哪""读起来费劲"的评审意见，需要从结构层面重建论文
2. **引言写不出、写不好** — 用户面对空白引言页面发呆，不知道第一句写什么，或者写了一大段但读起来像文献堆砌没有主线
3. **摘要和引言"各说各话"** — 用户写完了全文发现摘要强调的点在引言里没展开，或者引言讨论的内容摘要里根本没提
4. **从零开始规划论文结构** — 用户有了实验结果和数据，但不知道如何组织成一篇有逻辑的论文

### 语言信号（用户的话里出现这些就应激活）

- "怎么组织论文结构"
- "论文引言怎么写/写不好"
- "论文读起来逻辑混乱"
- "被评审说结构不清/逻辑不清"
- "摘要和引言怎么对应"
- "论文论证不清晰/不充分"
- "不知道怎么展开/不知道怎么往下写"
- "审稿人说读不懂我的贡献"

### 与相邻 skill 的区分

- 与 `10-30-test`（v05 质量检测）的区别：本 skill 是**写作方法论**——告诉你怎么写出一篇结构清晰的论文；v05 是**质量检测法**——写完后检验论文是否通过 10/30 分钟可读性测试。用盖房类比：本 skill 是施工图设计，v05 是竣工验收。
- 与 `logic-argument-5steps`（如果单独拆分）的区别：本 skill 包含五步逻辑论证链并将其嵌入金字塔结构中，如果用户只需要论证框架而不需要结构组织方法，可以单独使用五步法。

---

## E — 可执行步骤 (Execution)

当 skill 被激活后，agent 应按以下步骤执行：

1. **先写五步论证草稿**
   - 用自然语言（中文即可）写出五句话，分别回答：
     (1) 这个研究问题为什么重要？（有谁说过、有什么应用场景、有什么数据支撑）
     (2) 现有方法 A, B 有什么具体不足？（不能泛泛说"还不够好"，要指名道姓说具体缺陷）
     (3) 我提出了什么新方法 Z？（用主动语态，强调第一次提出）
     (4) 我如何证明 Z 比 A, B 更好？（理论证明？实验对比？显著性检验？用户研究？）
     (5) Z 有什么局限和不足？（诚实讨论，这也是未来工作方向）
   - 完成标准：五句话写在一张纸上/一个文本框里，读起来像一个完整的故事论证
   - 判停条件：如果用户连五句话都无法写出 → 说明研究本身还不够清晰，应先回到研究设计阶段，不急于写论文

2. **压缩为 200 字摘要（塔尖）**
   - 将五步草稿的每句话压缩为约 40 字，连成一段完整的摘要
   - 摘要必须能独立阅读：不包含引用标记 [1]，不包含技术术语缩写，不包含图表编号
   - 使用积极但不浮夸的语调（"shows great potential"而非"revolutionizes the field"）
   - 完成标准：摘要是 5-8 句话组成的连贯段落，任何同行读完都能复述你的核心贡献

3. **扩展为引言（塔身第一层）**
   - 将摘要的每个句子按顺序扩展为 3～20 句，构成引言段落
   - 扩展方式：加引用支撑 → 加数据/例子 → 加背景说明 → 加推理桥梁
   - 保证引言与摘要的论点顺序完全一致（如果摘要逻辑顺序调整了，引言必须同步调整）
   - 引言末尾加一段"论文结构导航"（"The rest of this paper is organized as follows..."）
   - 完成标准：引言 1-4 页，不包含技术细节，任何章节都可追溯到摘要中对应的句子

4. **规划正文分节（塔身各层）**
   - 引言中"现有工作不足"的段落 → 扩展为一节 Related Work
   - 引言中"我们提出了 Z"的段落 → 扩展为 Method / Proposed Approach（可能分多个小节）
   - 引言中"证明 Z 更好"的段落 → 扩展为 Experiments / Evaluation
   - 每一节开始用一个段落概述本节内容，然后逐小节展开
   - 层次深度控制在 3-4 层（如 3.1 → 3.1.1 → 3.1.1.1，不要再往下）
   - 完成标准：大纲完成，每节的中心句已写好，可以直接开始"填空"写作

5. **金字塔导航检查**
   - 逐层检查：标题包含核心贡献关键词吗？摘要独立讲述了完整故事吗？引言每段都能找到摘要对应句吗？正文每节都能追溯到引言对应段吗？
   - 检查引导词使用：高层次描述前有 "Generally speaking" 等提示词吗？进入细节时有 "More specifically" 等过渡吗？每节开头有概述段落吗？
   - 递交给用户审阅，指出哪些层级可能过于简略或过于冗长

---

## B — 边界 (Boundary) ★

### 不要在以下情况使用此 skill

- **理论数学论文** — 数学论文可能需要"定义→引理→定理→证明"的线性叙述顺序，不一定适合"先讲重要性再展开"的金字塔结构。如果用户写的是纯数学论文，应建议其参考数学领域的写作惯例
- **短报告/海报/幻灯片** — 两页的 workshop paper、学术海报、答辩幻灯片等空间有限的格式，金字塔可以在两个层级内完成（标题→正文），不需要本节中三层以上的细化
- **已有大量实验材料，需要自下而上整理** — 如果用户已经做完了全部实验、有了大量图表和数据，但还没形成清晰的论证主线，可能需要先用自下而上方法从材料中提炼故事线，然后再用金字塔法组织

### 作者在书中警告的失败模式

- **"先写正文再补引言"** — 作者明确反对这种写法。如果先写细节再补高层概述，会导致摘要/引言和正文脱节，论证链断裂。正确的顺序永远是塔尖→塔身
- **层级太深** — 作者警告不要出现 3.1.2.1.1 这种深度。超过 3-4 层说明顶层分类有问题，应该把内容拆分成并列的节，而不是在一个节里无限嵌套
- **每节开头没有概述段落** — 如果 3.1 节直接从 3.1.1 开始而没有先写一段介绍 3.1 节的文字，读者会迷失在结构中
- **摘要包含技术术语/引用** — 摘要应该是完全自包含的高层故事，不能出现"[1]"、技术缩写（除非全称已解释）、图表编号
- **谦虚陷阱** — 作者特别针对亚洲研究者指出：不要以为"评审者自己会看出来这篇论文很棒"。必须主动、清晰地宣告贡献，使用主动语态（"We propose..."），但要避免夸大（"completely solved AI"）

### 作者的盲点 / 时代局限

- **2012 年的论文结构惯例** — 书中描述的是 10 页会议论文的写作方法。在 2026 年，许多机器学习论文采用"Introduction → Related Work → Method → Experiments → Conclusion"的标准模板，作者的金字塔方法仍然适用，但论文篇幅和附录文化已变化（如 NeurIPS 允许无限附录）
- **AI 辅助写作工具未涉及** — 书中未讨论 ChatGPT/Claude 等 LLM 辅助写作，这些工具可以大幅加速"摘要→引言扩展"和"段落填空"的过程，但也可能引入论证链不连贯的问题
- **过度强调摘要独立性** — 在 arXiv/开放获取时代，许多读者直接搜索全文 PDF，摘要的"独立可读性"不如 2012 年重要，但作为金字塔塔尖的核心功能（为整篇论文定调）仍然有效

### 容易混淆的邻近方法论

- **倒金字塔（新闻写作）** — 新闻写作的倒金字塔是把最重要信息放最前面然后递减重要性，而学术金字塔是"每一层都完整讲述同一个故事，只是详略不同"。学术论文不能用"重要性递减"的方式组织
- **IMRaD 结构（Introduction-Methods-Results-Discussion）** — 这是论文的章节命名惯例，金字塔写作法是更底层的**内容组织原则**。一篇 IMRaD 结构的论文可以写得完全不符合金字塔原则（如 Introduction 和 Results 讲的不是同一个论证链）
- **自下而上写作法** — 博士论文组织方法之一（书中第 7 章），适合已发表多篇相关论文、需要从中提炼统一主线的场景。期刊/会议论文不应使用自下而上法

---

## 相关 skills

- depends-on: `logic-argument-5steps`（五步逻辑论证，本 skill 的核心组件）
- contrasts-with: `10-30-test`（写作后的质量检测，非写作方法），`bottom-up-thesis`（博士论文自下而上组织法）
- composes-with: `greys-criteria`（选题时用格雷准则评估问题，写作时用金字塔法展示结果）

---

## 审计信息

- **验证通过**: V1 ✓ / V2 ✓ / V3 ✓
- **测试通过率**: —（待测试）
- **蒸馏时间**: 2026-07-06
