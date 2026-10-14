# ICLR 2027 vs 2026：RLVR / GRPO 类 LLM 强化学习后训练论文的 base model 变化

## 结论

**Qwen 的主导地位更强了，而且主力从 Qwen2.5 换到了 Qwen3 / Qwen3.5。** 在摘要里写出了开源模型名的 RLVR/GRPO 论文中，用到 Qwen 的比例从 2026 年的 83% 升到 2027 年的 92%；只用 Qwen、不用其他家族的从 51% 升到 72%。

- **在涨的：** Qwen3、Qwen3.5/3.6（2027 年新出现）、Qwen3-VL、OLMo-3 和 Gemma-4（这两个都是新出现），以及 3–4B 的小模型和 MoE 模型。
- **在跌的：** Llama（占比 26% → 9%）、DeepSeek-R1-Distill-Qwen/Llama、Qwen2.5-Math、Mistral，以及 70B 以上的大模型。
- 2026 年摘要里常见的"受 DeepSeek-R1 / OpenAI o1 启发"这类开头，到 2027 年几乎没有了。

## 主要数据

口径：每个百分比 = 当年在摘要中写出至少一个开源模型名的论文里，提到该家族或版本的论文所占比例。这类论文 2026 年 210 篇，2027 年 727 篇。一篇论文可以同时属于多个家族，所以各行加起来超过 100%。

| 模型家族（开源权重） | 2026 n | 2026 % | 2027 n | 2027 % | 变化 |
|---|---|---|---|---|---|
| **Qwen**（全部，含 QwQ、R1-Distill-Qwen） | 175 | 83.3% | 666 | 91.6% | ↑ 1.10× |
| **Llama** | 55 | 26.2% | 64 | 8.8% | ↓ 0.34× |
| DeepSeek-R1-Distill（Qwen/Llama） | 15 | 7.1% | 15 | 2.1% | ↓ 0.30× |
| DeepSeek 其他（Math/Coder/V3/V4 等） | 11 | 5.2% | 17 | 2.3% | ↓ 0.44× |
| **OLMo** | 3 | 1.4% | 31 | 4.3% | ↑ 3.1× |
| Gemma | 6 | 2.9% | 22 | 3.0% | 持平（但 Gemma-4 是新出现的） |
| Mistral / Ministral | 7 | 3.3% | 8 | 1.1% | ↓ |
| Nemotron | 5 | 2.4% | 9 | 1.2% | ↓ |
| Kimi / Moonlight | 5 | 2.4% | 18 | 2.5% | 持平（主要被当作对比对象，见下） |
| GLM | 5 | 2.4% | 12 | 1.7% | ≈（同上） |
| InternLM / InternVL | 3 | 1.4% | 10 | 1.4% | 持平 |
| GPT-OSS | 2 | 1.0% | 8 | 1.1% | 数量太少 |
| SmolLM | 1 | 0.5% | 7 | 1.0% | 数量太少 |

**各家族内部的版本更替**（口径同上）

| 版本 | 2026 % (n) | 2027 % (n) |
|---|---|---|
| Qwen2.5（全部） | 44.3% (93) | 24.8% (180) |
| └ Qwen2.5-Math | 7.1% (15) | 2.6% (19) |
| └ Qwen2.5-VL | 8.1% (17) | 5.2% (38) |
| Qwen3（不含 3.5 及以上） | 24.8% (52) | 50.1% (364) |
| └ 摘要中明确写 Qwen3-xB-**Base** | 3.3% (7) | 5.9% (43) |
| Qwen3-VL | 0 | 9.4% (68) |
| Qwen3.5 / 3.6 / 3.7–3.8 | 0 | 14.0% / 2.5% / 1.1%（102 / 18 / 8 篇） |
| R1-Distill-Qwen | 5.7% (12) | 1.7% (12) |
| Llama-3.1 / Llama-3.2 | 7.6% / 4.3% | 3.0% / 2.3% |
| Llama-4 | 0 | 0 |
| OLMo-3 | 0 | 3.3% (24) |
| Gemma-4 | 0 | 1.7% (12) |

只看用到 Qwen 的论文、并取每篇提到的最新一代时：2026 年 Qwen2.5 占 47%、Qwen3 占 30%；2027 年 Qwen2.5 占 20%、Qwen3 占 53%、Qwen3.5–3.8 占 19%。

**模型规模**（摘要中跟在开源模型名后面的参数量；一篇论文可以落入多个区间）：≤2B 13% → 20%，3–4B 16% → 28%，7–9B 39% → 41%（基本不变），27–40B 10% → 11%，≥70B 4.8% → 1.2%。MoE 写法（如 30B-A3B、35B-A3B）从 2.9% 升到 7.2%。

## 观察

1. **Qwen 几乎成了默认选项，跨家族验证变少了。** 同时报告两个及以上家族的论文从 36% 降到 21%。2026 年常见"Qwen2.5 + Llama-3.1-8B"这样的双家族设置，2027 年大多只报告 Qwen3 系列的几个规模，例如 Qwen3-1.7B/4B/8B。
2. **Qwen 内部是代际更替，旧代没有完全退出。** Qwen3 的占比翻了一倍（25% → 50%），Qwen3.5 发布后很快进入 14% 的论文。Qwen2.5 仍有约四分之一，大多作为第二组设置或用于与旧基线对比。专门的数学模型 Qwen2.5-Math 和 R1-Distill 蒸馏模型都在退场。研究者更多从通用 base 或 instruct 模型出发，摘要中明确写"Qwen3-xB-Base"的比例也上升了。
3. **Llama 明显在退。** 占比从 26% 降到 9%，降幅约三分之二。2027 年仍在用的基本还是 Llama-3.1-8B 和 Llama-3.2-1B/3B 这些老型号，Llama-4 一次都没有出现。
4. **"完全开放"的模型在涨，以 OLMo-3 为代表。** OLMo 从 3 篇增加到 31 篇。从摘要看，它多用于分析类研究：研究者利用 AI2 公开的 SFT → DPO → RLVR 中间 checkpoint 和 RL-Zero 模型，分析 RLVR 到底改变了什么。Gemma-4、GPT-OSS-20B/120B、Nemotron-3-Nano 等新的西方开源模型也开始被用作 RL 起点，但每个家族都不到 3%。
5. **Kimi、GLM、DeepSeek-V4 在 2027 年主要是对比对象，不是训练起点。** 逐条阅读上下文发现，它们大多以"超过 Kimi-K2.6/K3、GLM-5.x"的形式出现。真正拿来做 RL 训练的只有少数，例如 Moonlight-16B-A3B 和 GLM-4.5-Air。闭源模型方面，GPT-4o/GPT-5 系列在摘要中的出现率从 6.4% 降到 2.0%，o 系列从 4.1% 降到接近 0。DeepSeek-R1 作为"动机或范例"被提到的比例从 5.1% 降到 0.1%，这个开篇套路已经过时。

## 代表论文

- 2026 · Qwen2.5-Math：Scaf-GRPO — https://openreview.net/forum?id=bOwVr0yr7r （accept_poster）
- 2026 · R1-Distill-Qwen-1.5B：The Markovian Thinker — https://openreview.net/forum?id=3As6AQ9ELI （accept_poster）
- 2026 · Llama-3.1-8B + Qwen2.5-7B 双家族：Language Models That Think, Chat Better — https://openreview.net/forum?id=trBEiQFkxw
- 2027 · Qwen3.5-4B + GRPO：ContextForge — https://openreview.net/forum?id=GUTgBE6Ma0
- 2027 · OLMo-3 的 RLVR 中间 checkpoint：Questioning Instrumental Convergence in RLVR — https://openreview.net/forum?id=iKvECCrAgT
- 2027 · Gemma-4-12B + Qwen3.5-4B：Teaching LLMs to Generate Challenging MILP Instances — https://openreview.net/forum?id=7inOLMkafz
- 2027 · gpt-oss-120b 上的持续 RLVR：MagicBeanStalk — https://openreview.net/forum?id=udNCKUC7ux
- 2027 · Qwen3-VL 视频推理 RL：Learning to Reason Efficiently in Videos — https://openreview.net/forum?id=59ZHoBtdUU

## 方法说明

- **研究对象。** 2026 年和 2027 年的投稿，满足以下任一条件：（a）标题、关键词、TL;DR 或摘要中出现 RLVR、verifiable reward、GRPO、DAPO、GSPO、RLOO、R1-Zero 等词；（b）属于 9 个 LLM-RL 主题簇之一（RLVR、GRPO variants、agentic RL credit assignment、multimodal reasoning with RL、SFT-to-RL 等），且文中提到 RL、policy optimization 或 reward。在此基础上，剔除生成、视觉、具身和非 LLM 的 RL 主题中不涉及 LLM/VLM 的论文（主要是图像扩散模型上的 Flow-GRPO 类工作）。最终 2026 年 970 篇、2027 年 2,172 篇（每万篇投稿分别为 490 和 505 篇），包含 withdrawn 和 desk-rejected。2025 年没有符合条件的论文（RLVR 一词在 ICLR 2025 投稿中尚未出现），所以只比较 2026 和 2027 两年。抽查 40 个标题，约 85% 切题，噪声主要是只顺带提到 GRPO 的论文。这类论文通常不写 LLM 模型名，所以对上面按"写出模型名的论文"计算的比例影响很小。
- **测量方式。** 用词典正则匹配模型名，分家族和版本两层；排除了 Qwen-Image（扩散模型）和 Qwen-Max 这类闭源 API。另外人工阅读了约 200 条匹配上下文，用来判断提到的模型是训练对象还是对比对象：Qwen、Llama、OLMo、Gemma 约九成是被训练或被分析的模型；Kimi、GLM、DeepSeek-V4 多为对比对象。
- **为什么用"写出模型名的论文"做分母。** 写出至少一个开源模型名的摘要占比从 21.6% 升到 33.5%。这一上升大部分来自 2027 年的模板化写作风格：剔除这类摘要后，2027 年的比例是 26.0%。如果直接用全部论文做分母，几乎所有家族都会显得"在涨"。
- **稳健性检查。** 剔除 2027 年模板化风格的摘要后，结论不变：Qwen 83% → 91%，Llama 26% → 9%，Qwen2.5 44% → 23%，Qwen3 25% → 50%，OLMo 1.0% → 4.6%。改用"2026 年接收论文 vs 2027 年 active 论文"比较，结论也一致。
- **注意事项。**
  - 这里统计的是"摘要中写出的模型"，并不等于实际实验用的全部模型。约 67% 的论文摘要没有写模型名，其中不少只写了"7B model"这类参数量。这些论文的情况未知，不应理解为"没用"。
  - 小家族（GPT-OSS、SmolLM、MiMo 等）在 2026 年都不到 10 篇，只能看计数，不宜算倍数。
  - 2027 年还没有审稿结果，无法判断哪种 base 更受审稿人青睐。
  - 本次没有使用并行子代理逐篇阅读：家族名属于词典能可靠匹配的"命名实体"，只做了上下文抽查。
