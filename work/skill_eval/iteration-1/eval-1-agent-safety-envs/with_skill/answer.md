# ICLR 2026 与 2027 的 agent safety 工作用的是哪些环境？

## 结论

两年里，agent safety 论文用得最多的环境都是**工具调用 / API 类环境**（以 AgentDojo、InjecAgent、τ-bench 这类工具套件为代表）和**多智能体环境**。

2027 年的分布有明显变化：
- **变多的**：工具调用环境（23.7% → 37.5%）、代码/终端 agent（11.9% → 19.0%）、agent 记忆或 RAG（4.0% → 12.5%）、MCP 与 Agent Skills（3.4% → 8.5%）。
- **变少的**：Web 浏览 agent（16.9% → 8.0%）、纯对话式的 prompt injection 研究（16.9% → 8.0%），多智能体环境也略有下降（24.9% → 19.5%）。

可以概括为：研究的重心从"网页和 GUI 上的 agent"转向了"带工具、带记忆、可装 skill 的 coding agent 运行环境"（agent harness）。

## 环境类别分布

一篇论文可以同时属于多个类别，所以每列加起来会超过 100%。

| 环境类别 | 2026 篇数 (%) | 2027 篇数 (%) ± 95% CI | 变化 |
|---|---|---|---|
| 工具调用 / API（tool_api） | 42 (23.7%) | 75 (37.5% ± 6) | ↑ 1.6× |
| 多智能体（multi_agent） | 44 (24.9%) | 39 (19.5% ± 5) | ↓ 0.8× |
| 代码 / 终端 / 仓库 / 网络安全靶场（coding_terminal） | 21 (11.9%) | 38 (19.0% ± 5) | ↑ 1.6× |
| 记忆 / RAG（memory_rag） | 7 (4.0%) | 25 (12.5% ± 4) | ↑ 3.2× |
| MCP / Agent Skills（mcp_skills） | 6 (3.4%) | 17 (8.5% ± 3) | ↑ 2.5× |
| Web 浏览（web） | 30 (16.9%) | 16 (8.0% ± 3) | ↓ 0.5× |
| 仅对话、无工具（chat_only） | 30 (16.9%) | 16 (8.0% ± 3) | ↓ 0.5× |
| GUI / 桌面 / 手机（os_desktop_mobile） | 15 (8.5%) | 12 (6.0% ± 3) | ↓ 0.7× |
| 具身 / 机器人 / 驾驶 / 游戏（embodied） | 7 (4.0%) | 8 (4.0% ± 2) | 持平 |
| 邮件 / 办公 / 企业流程（email_office） | 2 (1.1%) | 7 (3.5% ± 2) | ↑（基数小） |
| 摘要未说明环境（none_stated） | 8 (4.5%) | 13 (6.5% ± 3) | — |

- 2026 年读了全部 177 篇；2027 年从 891 篇中随机抽了 200 篇来读。
- 置信区间只针对 2027 的抽样，已做有限总体校正。
- email_office 在 2026 年少于 10 篇，比较时请直接看两年的篇数，不要看倍数。

## 摘要中点名的具体环境 / benchmark

下面用词表在**全部 1068 篇**里统计，所以比抽样更稳。

| 名称 | 2026（n=177） | 2027（n=891） |
|---|---|---|
| AgentDojo | 10 (5.6%) | 64 (7.2%) |
| Agent Skills / SKILL.md | 0 | 42 (4.7%) |
| Claude Code / Cursor / Codex CLI | 3 (1.7%) | 21 (2.4%) |
| SWE-bench | 2 (1.1%) | 20 (2.2%) |
| MCP | 6 (3.4%) | 17 (1.9%) |
| InjecAgent | 4 (2.3%) | 11 (1.2%) |
| τ-bench | 1 (0.6%) | 9 (1.0%) |
| AgentHarm | 2 (1.1%) | 9 (1.0%) |
| Terminal-Bench | 0 | 7 (0.8%) |
| R-Judge | 0 | 6 (0.7%) |
| WebArena / OSWorld | 各 1 | 各 4 |

在读过的样本里，**2027 年新出现**的名字有：OpenClaw、Codex、OpenCode、Hermes、AgentDyn、Agent-SafetyBench、AppWorld、LangGraph/LangChain、Terminal-Bench 2.x。其中大量是真实 agent harness，而不是专门搭的模拟环境。

另外，约三分之二的摘要至少写出了一个环境、框架或 benchmark 的名字（2026 年 66.7%，2027 年 65.5%），但这其中包括论文自己新建的 benchmark。名称非常分散：在读过的样本里，除 AgentDojo（约 6–7%）外，没有哪个名字的占比超过 3.5%。大多数论文用的是自建 benchmark。

## 主要观察

1. **工具调用环境仍是主力，AgentDojo 是事实标准。** 2027 年 37.5% 的论文在工具 / API 环境里做实验，AgentDojo 在全部论文中的占比从 5.6% 升到 7.2%。不过这个上升有一部分来自写作风格（见方法说明）：只看风格正常的 2027 摘要，工具环境占 28.4%，比 2026 年只高约 5 个百分点。
2. **攻击面从"网页内容"移到了"agent 自身的组件"。** 记忆 / RAG（4.0% → 12.5%）和 MCP / Skills（3.4% → 8.5%）的上升，在排除套话风格摘要后依然成立（分别为 11.8% 和 9.8%）。"Agent Skills"在 2026 年是 0 篇，2027 年有 42 篇。研究对象变成了 skill 投毒、记忆注入、MCP 中间人等供应链式攻击。
3. **Coding agent 和真实 harness 成为新的主战场。** 代码 / 终端类环境从 11.9% 升到 19.0%。2027 年大量论文直接在 Claude Code、Codex CLI、OpenClaw、OpenCode 上做实验，研究监控绕过、轨迹篡改、权限最小化等问题，而不是在模拟器里。
4. **Web / GUI agent 的相对份额减半，纯对话式 prompt injection 也在退潮。** Web 从 16.9% 降到 8.0%，GUI 从 8.5% 降到 6.0%。纯对话式（无工具）的 prompt injection / 指令层级研究从 16.9% 降到 8.0%；只看真正以 agent 为对象的论文时，这一项本来就只有 2–4%。由于 2027 年总量涨了 5 倍，这些方向的绝对篇数并没有减少，只是占比被稀释了。

## 代表论文

- MCP / Skills
  - Opaque Skills, Cautious Agents?（2027）：在 Claude Code、Codex CLI、Gemini CLI、OpenCode 上测试恶意 Skill。https://openreview.net/forum?id=uAeJBSQOH8
  - MMSkillRisk（2027）：多模态 Skill 中的图像注入。https://openreview.net/forum?id=5iWb2yVfnC
  - MCP-SafetyBench（2026，poster）：基于真实 MCP server。https://openreview.net/forum?id=7XYjeL46co
- 记忆
  - MemSecBench（2027）：记忆投毒的全生命周期。https://openreview.net/forum?id=bpOmYif9u7
  - MemGhost（2027）：通过邮件向 OpenClaw / Claude Code SDK 注入记忆。https://openreview.net/forum?id=u94T9UWCzY
- Coding agent / harness
  - Red-Teaming Auto Mode（2027）：针对 Claude Code Auto Mode 和 Codex Guardian。https://openreview.net/forum?id=Xvoqy4F84S
  - ClashBench（2027）：资源冲突导致的破坏性抢占。https://openreview.net/forum?id=AqeZ1dd6BR
- 工具环境：ATTRACK（2027），在 AgentDojo 上做 taint tracking 防御。https://openreview.net/forum?id=0QXPPsbddF
- 2026 年典型的 Web / GUI 环境
  - ST-WebAgentBench（poster）：https://openreview.net/forum?id=MuCDzH0ctf
  - RedTeamCUA（oral）：混合 Web-OS 沙箱。https://openreview.net/forum?id=yWwrgcBoK3
  - GhostEI-Bench（poster）：Android 模拟器。https://openreview.net/forum?id=2zi9z2geAO

## 方法说明

- **论文范围**：2026–27 年安全标签中，相关度 ≥ 1、且主或次子领域为 `AGENT_SAFE` 或 `PI`（prompt injection）的论文。2026 年 177 篇（每万篇投稿约 89 篇），2027 年 891 篇（每万篇约 207 篇）。其中 2027 年的提交量和占比都明显上升。
  - PI 子领域里有少量不涉及 agent 的 prompt injection / 指令层级论文，它们被标为 chat_only。
  - 另一种范围是按 `target_system` 为 agent / multiagent 来选，两者大部分重叠。只看这部分论文时，结论方向一致，只是 chat_only 降到 2–4%。
- **"环境"的含义**：本文指 agent 运行的场景类型（web、OS、代码、工具、MCP 等），同时记录具体的 benchmark 或模拟器名称。
- **测量方法**：
  1. 先用词表做预跑。词表只覆盖约 60% 的论文，而且以"tool-use agent"这类泛称为主，所以接着逐篇阅读摘要并按 codebook 标注。
  2. 2026 年读了全部 177 篇；2027 年随机抽了 200 篇（seed 0）。所有阅读都由我一个人完成，没有使用子 agent。
  3. 用词表命中结果对阅读标注做了交叉核对：web 类无冲突；其他类别词表多出来的几篇，都是"提到但并非实验环境"的情况。
  4. 具体 benchmark 名称的占比用词表在全部 1068 篇上统计。
- **注意事项**：
  - 统计的是**摘要中提到的环境**，会低估论文正文里实际用到的环境。
  - 2027 年有 42% 的摘要使用一种新的套话写作风格。在 2027 样本中，这类摘要有 98 篇，其中工具环境占比高达 46.9%；其余 102 篇风格正常的摘要只有 28.4%。因此"工具环境大幅上升"的幅度应当打折扣。记忆、MCP / Skills、代码类上升以及 Web 下降，在排除套话风格摘要后依然成立。
  - 安全标签和本文的环境标注都由语言模型从摘要生成，适合看整体分布。引用单篇论文作为例子前，请先核对原文。
