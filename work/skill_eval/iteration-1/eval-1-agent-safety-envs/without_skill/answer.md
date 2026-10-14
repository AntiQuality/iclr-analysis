# ICLR 2026 / 2027 Agent Safety 论文用的是哪些环境

## 结论

- **2026 年，agent safety 的环境主要是“看得见的交互界面”。** Web 浏览器、computer-use（桌面 GUI）和手机 GUI 合计约占 22%，多智能体或社会模拟约占 22%。领域场景也不少，主要是金融、医疗和客服 SOP。
- **2027 年，重心转到了智能体自身的工具链和运行时。** 只按主环境算，工具调用、MCP、Agent Skills 生态，以及 OpenClaw / Claude Code / Codex 这类生产级 harness，合计从 13.5% 升到 26.8%，成为最大的一类。代码、终端和网络攻防从 6.8% 升到 10.2%。memory 和 self-evolving agent 从 2% 升到 8.4%。Web 和 GUI 的占比则从 22% 降到 11%。
- **使用最多的现成环境是 AgentDojo，远远领先其他环境。** 2027 年有 61 篇（7.3%）的摘要提到它。其后是 SWE-bench（20 篇）、InjecAgent（11 篇）、AgentHarm（9 篇）和 τ-bench（8 篇）。Terminal-Bench、AppWorld、OSWorld、WebArena 等都在个位数。大量论文是**自己造一个新的 benchmark 或 sandbox**，所以环境非常分散，没有形成统一标准。
- 规模上，这类论文在当年投稿中的占比从 2026 年的 0.75%（148 / 19,813）升到 2027 年的 1.93%（831 / 43,013）。

> 两点说明：
> 1. 数据集只有标题、关键词和摘要，没有论文全文。下面的“环境”是根据摘要里写明的环境或 benchmark 判断的。正文实验部分用到、但摘要没提的环境不会被统计到，所以具名 benchmark 的数字是**下限**。
> 2. 环境标签是用规则（正则词表）打的，不是逐篇人工标注。我人工抽查了 90 篇，主环境标签大约 85% 合理，适合看整体分布，不适合直接引用某一篇的标签。

---

## 1. 统计对象

数据来自 `safety/labels.csv`。论文的安全标签由数据集作者用 LLM 生成，没有人工逐篇复核。纳入范围如下：

| 范围 | 2026 | 2027 | 说明 |
|---|---:|---:|---|
| `subfield` 或 `subfield_2` = `AGENT_SAFE` | 128 | 774 | 主口径。taxonomy 的定义是“prompt injection 以外的自主智能体安全”，包括风险动作、computer-use / web / coding agent 安全、多智能体风险和 agent safety benchmark |
| 另加：`subfield = PI` 且 `target_system` 为 agent 或 multiagent | 20 | 57 | 面向智能体的 prompt injection / 工具劫持。很多人会把它算进 agent safety，所以一起统计 |
| **合计** | **148** | **831** | 下文百分比默认用这个口径 |

只用 `AGENT_SAFE` 口径时，结论基本不变。数字见 `work/primary_env_by_year_agentsafe.csv`。

2026 年论文的状态：接收 36 篇（3 篇 oral），拒稿 65 篇，撤稿 35 篇，desk reject 12 篇。2027 年的论文还在审稿中。

---

## 2. 环境分布：每篇只计一个主环境

一篇论文可能同时提到多种环境。这一节给每篇只分配一个**主环境**：优先取最具体的那类，例如具身 > 手机 > Skills/MCP/harness > GUI > Web > 网络攻防 > 代码 > 垂直领域 > 多智能体 > memory > 泛化工具调用。

### 2.1 大类

| 环境大类 | 2026 篇数 | 2026 占比 | 2027 篇数 | 2027 占比 | 变化 |
|---|---:|---:|---:|---:|---|
| 工具 / MCP / Agent Skills / 生产级 harness | 20 | 13.5% | 223 | **26.8%** | ↑↑ |
| 多智能体系统 / 社会模拟 / 博弈 | 32 | 21.6% | 130 | 15.6% | ↓ |
| 垂直领域场景（个人助理、客服 SOP、金融、医疗、检索等） | 28 | 18.9% | 125 | 15.0% | ↓ |
| Web / 桌面 GUI / 手机 GUI | 33 | **22.3%** | 91 | 11.0% | ↓↓ |
| 代码 / 终端 / 网络攻防 | 10 | 6.8% | 85 | 10.2% | ↑ |
| Memory / self-evolving agent | 3 | 2.0% | 70 | 8.4% | ↑↑ |
| 具身 / 机器人 / 自动驾驶 | 8 | 5.4% | 31 | 3.7% | ↓ |
| 摘要未写明具体环境 | 14 | 9.5% | 76 | 9.1% | – |

### 2.2 细类

| 主环境 | 2026 | % | 2027 | % | 代表论文（标题） |
|---|---:|---:|---:|---:|---|
| 多智能体系统 / A2A / 社会模拟 | 27 | 18.2 | 103 | 12.4 | Goal-Aware … Misinformation in MAS (ARGUS), A2A-BFT, Shutdown Sabotage Propensities in MAS |
| 泛化工具调用（未指明具体领域） | 8 | 5.4 | 102 | 12.3 | STAC, CAST (trajectory triage), TAPER |
| Memory / self-evolving | 3 | 2.0 | 70 | 8.4 | Your Agent May Misevolve, InjecMEM, A-MemGuard, SEABench |
| 代码 / SWE / 终端 | 6 | 4.1 | 60 | 7.2 | XOXO, AutoApproveBench, Audit Horizons |
| 个人助理 / 工作区（邮件、日历、银行、旅行等，AgentDojo 类） | 8 | 5.4 | 58 | 7.0 | A Two-Neuron Edit to Mitigate Prompt Injections |
| **Agent Skills 生态（SKILL.md、技能市场）** | **0** | 0.0 | **50** | **6.0** | SkillDOS, Under the Hood of SKILL.md |
| **生产级 harness（OpenClaw、Claude Code、Codex、OpenCode、Moltbook）** | 6 | 4.1 | 49 | 5.9 | CONTRA, TrustFork (Trust the Brand…), RedCodeAgent |
| Computer-use / 桌面 GUI / OS | 10 | 6.8 | 37 | 4.5 | VPI-Bench, RedTeamCUA, Just Do It!?, ClickShield |
| Web / 浏览器 | 18 | **12.2** | 34 | 4.1 | ST-WebAgentBench, How Dark Patterns Manipulate Web Agents |
| 具身 / 机器人 / 驾驶 | 8 | 5.4 | 31 | 3.7 | SafeAgentBench, BEAT, TutelaBench, PUARobot |
| 博弈 / 经济模拟（拍卖、谈判、游戏） | 5 | 3.4 | 27 | 3.2 | Opponent Shaping, Four Bridges |
| 网络攻防（CTF、CVE、渗透测试） | 4 | 2.7 | 25 | 3.0 | CyberGym (oral), PACEbench, CyberPersistBench |
| MCP / 插件 / 工具服务器 | 6 | 4.1 | 22 | 2.6 | MCP-SafetyBench, Log-To-Leak, TruncDoS |
| 客服 / 企业 SOP（τ-bench 类） | 1 | 0.7 | 21 | 2.5 | SOPBench, Policy-Verified Self-Training |
| 手机 / Android | 5 | 3.4 | 20 | 2.4 | ScreenLocate |
| 金融 / 交易 / 加密 | 8 | 5.4 | 19 | 2.3 | CAIA, Benchmarking Financial Agent Safety |
| 搜索 / deep research / RAG | 5 | 3.4 | 12 | 1.4 | （SafeSearch 因同时提到 web 而被归入 Web 类） |
| 医疗 / 临床 | 5 | 3.4 | 9 | 1.1 | MedicalPressureBench |
| 科研 / 化学 / 生物实验 | 1 | 0.7 | 3 | 0.4 | PropensityBench |
| 语音 | 0 | 0.0 | 3 | 0.4 | |
| 摘要未写明 | 14 | 9.5 | 76 | 9.1 | |

> 2026 年只有 148 篇，每个细类只有个位数到二十几篇，所以 2026 年各类占比的误差大约是 ±3–4 个百分点。细类之间小于这个幅度的差异不要过度解读。

---

## 3. 环境分布：同一篇可计入多类

这一节允许一篇论文同时计入多种环境，反映的是“这类环境被提到的频率”。

| 环境（被提及） | 2026 | 2027 |
|---|---:|---:|
| 工具调用 / API | 31.8% | 34.3% |
| 多智能体 | 28.4% | 21.5% |
| Memory / self-evolving | 7.4% | **19.3%** |
| 代码 / 终端 | 10.1% | 14.0% |
| 个人助理 / 工作区 | 12.8% | 12.3% |
| Computer-use GUI | 10.1% | 7.1% |
| 生产级 harness（OpenClaw / Claude Code / Codex 等） | 4.1% | 6.9% |
| Web 浏览器 | **15.5%** | 6.1% |
| Agent Skills | 0.0% | 6.0% |
| 博弈 / 经济模拟 | 4.7% | 5.5% |

---

## 4. 具名 benchmark 和环境的使用频率

下表统计在**摘要**中被点名的环境。正文中实际用到的会更多，所以这些数字是下限。

| Benchmark / 环境 | 类型 | 2026（n=148） | 2027（n=831） |
|---|---|---:|---:|
| **AgentDojo** | 工具调用 + 个人助理（邮件、银行、旅行、Slack），用于 prompt injection | 10（6.8%） | **61（7.3%）** |
| SWE-bench | 代码仓库 | 2 | 20 |
| InjecAgent | 工具调用 prompt injection | 4 | 11 |
| AgentHarm | 有害工具任务 | 2 | 9 |
| τ-bench / τ²-bench | 客服 / 航空 / 零售政策 | 1 | 8 |
| Terminal-Bench | 终端 | 0 | 7 |
| AppWorld | 多 App 个人助理 | 0 | 6 |
| R-Judge / Agent-SafetyBench | 轨迹安全判定 / 综合 agent 安全 | 0 | 6 / 6 |
| ASB（Agent Security Bench） | 综合攻击 / 防御 | 2 | 4 |
| OSWorld / WebArena / VisualWebArena | 桌面 / Web | 1 / 1 / 0 | 4 / 4 / 2 |
| ALFWorld / ScienceWorld | 文本世界 | 0 | 4 / 4 |
| SHADE-Arena / CUA-SHADE-Arena | 隐蔽破坏（AI control） | 2 | 2 |
| WASP、ToolEmu、OpenAgentSafety、CVE-Bench、BaxBench、RedCode、CyberGym 等 | | 各 1–2 | 各 1–2 |

从这些数字可以看出：

- **AgentDojo 基本是 agent 安全领域事实上的通用标准。** 它主要服务于 prompt injection 攻防，即使不看 PI 论文，在 `AGENT_SAFE` 子集里也有 43 篇提到。
- 除 AgentDojo 外，**没有第二个环境的使用率超过 3%**。2026 年约 40% 的论文、2027 年约 26% 的论文在摘要里说自己“提出或构建了新的 benchmark / environment / sandbox”。

---

## 5. 环境的实现方式

只有少数论文在摘要里写明了实现方式，下表的数字是下限：

| 实现方式 | 2026 | 2027 |
|---|---:|---:|
| 真实可执行 sandbox（Docker、VM、真实网站或系统、live service） | 17.6% | 14.6% |
| LLM 模拟或仿真环境（如 ToolEmu 式模拟工具） | 6.1% | 2.8% |
| 静态轨迹判定（给定轨迹，判断是否安全，如 R-Judge） | 4.1% | 2.9% |

2027 年出现的一个新现象是：越来越多的论文**直接在真实的 agent 产品或 harness 里做实验**，例如 OpenClaw、Claude Code、Codex CLI、OpenCode、Moltbook 智能体社交网络，以及 ClawHub 技能市场。这类论文从 2026 年的 6 篇增加到 2027 年的约 57 篇（按多标签计）。

---

## 6. 2026 → 2027 的趋势

1. **攻击面从“环境内容”转向“智能体自身的扩展机制”。** 2026 年的典型设定是网页、UI 或工具返回值被投毒，通过 Web/GUI 注入。2027 年新增了大量供应链式的设定，包括 Agent Skills（SKILL.md、技能市场，从 0 篇增加到约 50 篇）、MCP 服务器、memory 和 self-evolving 经验库，攻击对象变成了智能体的持久状态。
2. **Web 和 GUI 环境的占比明显下降**（主环境口径从 22% 降到 11%）。绝对数量仍在增加（33 → 91 篇），但增速远低于工具链类。
3. **代码和终端环境在上升**（6.8% → 10.2%），对应的是 coding agent 自动审批、审计 horizon、reward hacking（如 ImpossibleBench）、harness 代码漏洞等问题。
4. **多智能体环境仍是第二大类，但占比在下降**（21.6% → 15.6%）。研究对象从 MoA、辩论式 MAS，扩展到 A2A 协议、智能体社交网络和长期运行的智能体社会，例如 AgentWorld。
5. **领域场景更分散。** 医疗、金融这类 2026 年常见的“高风险领域包装”占比下降。客服和企业 SOP（τ-bench 类）略有上升。
6. **贡献类型从“建 benchmark”转向“做防御”。** eval 类论文从 48% 降到 32%，defense 类从 20% 升到 30%。这和“环境越来越依赖现成的 AgentDojo、SWE-bench 等，新建 benchmark 的比例下降（40% → 26%）”是一致的。

---

## 7. 局限

- **只看了摘要。** 实验部分使用、但摘要没写的环境不会被统计，具名 benchmark 的数字都是下限。约 9% 的论文摘要完全没有写明环境。
- **分类是规则匹配。** 我人工抽查了 90 篇（两轮随机样本），主环境大约 85% 合理。常见误判有三种：泛泛提到 “finance/healthcare” 等领域作为动机的论文被归入领域类；理论或机制类论文被关键词误拉到 coding 或 memory；Web 与 GUI、MCP 与泛化工具调用之间存在边界模糊。还有个别明显错误，例如手机 GUI 的 GhostEI-Bench 被误归入具身类。
- **样本来源本身有噪声。** `AGENT_SAFE` 和 `PI` 标签由 LLM 生成，没有人工复核。2027 年的投稿是 2026-10-07 的快照，尚无审稿结果。另外，数据集 README 指出 2027 年有 42% 的摘要带有明显的模板化措辞，相关关键词的频率可能因此偏高。
- **年份比较请看占比，不要看篇数。** 2027 年总投稿量是 2026 年的 2.17 倍。

逐篇标签在 `work/env_tags.csv`，可按 `primary_env` 或 `env` 筛选后回到 OpenReview 核对原文。
