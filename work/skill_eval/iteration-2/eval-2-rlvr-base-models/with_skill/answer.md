# ICLR 2027 vs 2026：RLVR / GRPO 类 LLM 强化学习后训练论文用的 base model 怎么变了

## 结论

**Qwen 的统治地位更强了，而且整体从 Qwen2.5 换代到了 Qwen3 / Qwen3.5 / Qwen3-VL。** 只看摘要里点名了开源基座的论文：2026 年有 85% 提到 Qwen，2027 年升到 94%；"只用 Qwen、不提任何别的家族"的论文从 55% 涨到 77%。

- **在跌的**：Llama（29% → 10%）、DeepSeek-R1-Distill 系列（10% → 2.5%）、Qwen2.5 一代（Qwen2.5 文本 48% → 25%，其中 Qwen2.5-Math 10% → 3%，Qwen2.5-VL 12% → 6%）、Mistral（4% → 1%）。
- **在涨的**：Qwen3（27% → 44%），以及 2026 年还没有的 Qwen3.5/3.6（16%）和 Qwen3-VL（9%）。小家族里只有 OLMo（主要是 OLMo-3）的上涨比较可信，从 2% 到 4.5%，但 2026 年总共只有 3 篇。
- **基本持平的**：Gemma（2.8% → 2.8%，2027 年多是 Gemma 3/4），以及 gpt-oss、Nemotron、SmolLM、MiMo 这些长尾家族。它们每个都在 1–2% 左右，篇数太少，看不出趋势。

另外，用 DeepSeek-R1、OpenAI o1 当开篇引子的写法明显少了。这只是叙事上的变化，不代表这些模型被当作基座训练过。

## 主表：各模型家族在"点名了开源基座的论文"中的占比

分母是摘要里至少点名一个开源基座家族的论文：2026 年 177 篇，2027 年 642 篇。一篇论文可以同时属于多个家族。括号里是 95% Wilson 区间。

| 模型家族 | 2026 n | 2026 % | 2027 n | 2027 % | 变化 |
|---|---:|---:|---:|---:|---|
| **Qwen（任意版本）** | 151 | 85.3 (79–90) | 601 | 93.6 (91–95) | ↑ 1.10× |
| · Qwen2 / 2.5 文本（含 Math/Coder） | 84 | 47.5 (40–55) | 163 | 25.4 (22–29) | ↓ 0.53× |
| · · 其中 Qwen2.5-Math | 17 | 9.6 | 20 | 3.1 | ↓ 0.32× |
| · Qwen2/2.5-VL / Omni / Audio | 22 | 12.4 | 41 | 6.4 | ↓ 0.52× |
| · Qwen3 文本（含 Base/Thinking/Coder） | 48 | 27.1 (21–34) | 282 | 43.9 (40–48) | ↑ 1.62× |
| · Qwen3-VL / Omni | 0 | 0 | 58 | 9.0 | 新出现 |
| · Qwen3.5 / 3.6 / 3.x | 0 | 0 | 105 | 16.4 (14–19) | 新出现 |
| **Llama（不含 R1-Distill-Llama）** | 51 | 28.8 (23–36) | 61 | 9.5 (7–12) | ↓ 0.33× |
| **DeepSeek-R1-Distill（Qwen/Llama）** | 18 | 10.2 (7–16) | 16 | 2.5 (2–4) | ↓ 0.25× |
| OLMo（2027 主要是 OLMo-3） | 3 | 1.7 | 29 | 4.5 (3–6) | ↑（2026 年只有 3 篇） |
| Gemma（2027 主要是 Gemma 3/4） | 5 | 2.8 | 18 | 2.8 | 持平 |
| Mistral / Ministral / Magistral | 7 | 4.0 | 8 | 1.2 | ↓（篇数少） |
| gpt-oss | 2 | 1.1 | 9 | 1.4 | 篇数太少 |
| Nemotron | 3 | 1.7 | 8 | 1.2 | 篇数太少 |
| SmolLM / Phi / MiMo / InternVL / LLaVA | 各 0–2 | ≤1.1 | 各 2–8 | ≤1.4 | 篇数太少 |
| **只提 Qwen、不提其他开源家族** | 98 | 55.4 (48–62) | 496 | 77.3 (74–80) | ↑ 1.40× |
| 提到至少一个非 Qwen 家族 | 79 | 44.6 | 146 | 22.7 | ↓ 0.51× |

下面这些也被点名了，但大多不是基座，所以不计入上表。我读了提到它们的段落：

| 被点名的模型 | 2026（占总体 %） | 2027（占总体 %） | 实际角色 |
|---|---:|---:|---|
| DeepSeek-R1 / V3 / V4 / Math（非 Distill） | 57 篇（6.7%） | 27 篇（1.5%） | 九成左右是开篇引子（"Since DeepSeek-R1…"）或对比基线。真正拿来训练的只有少数，如 DeepSeekMath-7B、DeepSeek-Prover |
| GPT / o 系列 | 85 篇（10.0%） | 39 篇（2.2%） | 引子、基线或评审模型 |
| Kimi、GLM | 各 1–13 篇 | | 多是"前沿开源模型"对比项。2027 年有个别论文训练 GLM-5.x、Kimi-K2.6 |

## 主要观察

1. **Qwen 内部在换代，主力从 Qwen2.5 变成了 Qwen3。** 2026 年最常见的单个 checkpoint 是 Qwen2.5-7B（占点名论文的 13%）和 Qwen2.5-Math-7B（6.8%）。2027 年变成 Qwen3-4B（17%）、Qwen3-8B（15%）、Qwen3-1.7B（8.6%），Qwen3.5-9B / 4B 也到了 4–5%。Qwen2.5-Math 曾经是 "spurious reward / zero-RL" 讨论的标准基座，现在少了很多（9.6% → 3.1%）。
2. **Llama 退成了"验证泛化性的第二个家族"。** 它的占比从 29% 跌到 10%。2027 年的写法通常是"主实验在 Qwen3 上做，再拿 Llama-3.1-8B / Llama-3.2-3B 验证一下"。2026 年有一批论文专门讨论"Qwen 上有效的 RLVR 信号在 Llama/OLMo 上无效"（如 Spurious Rewards）。但从 2027 年的数据看，这并没有让大家分散到更多家族，反而更集中在 Qwen 上。
3. **专门的"推理蒸馏模型"基座在退场。** DeepSeek-R1-Distill-Qwen-1.5B/7B 在 2026 年是做"高效推理、长度压缩 RL"的标准起点（10%），2027 年降到 2.5%。原因可能是 Qwen3 自带 thinking 模式，可以直接替代它。这只是推测，数据本身不能证明。
4. **多模态 RL 跟着换代。** Qwen2.5-VL 从 12% 降到 6%，Qwen3-VL 从 0 涨到 9%。所以 Qwen-VL 系在多模态 RL 里的总份额变化不大，变的是版本。
5. **完全开放的模型和新一代开源模型有小幅上涨，但量很小。** OLMo-3 常被用来研究 RLVR 训练过程本身，因为它公开了 SFT/DPO/RLVR 各阶段的 checkpoint。Gemma 4、gpt-oss、Nemotron 3、MiMo 在 2027 年都有零星的基座用法，每个都只占 1–5%。
6. **模型规模往小端集中。** 在点名基座的论文里，提到 3–4B 规模的比例从 24% 升到 37%，提到 ≤2B 的从 19% 升到 24%，7–9B 一直是主流（约 51%），14–32B 从 19% 降到 15%。这和 Qwen3-4B / 1.7B 的流行一致。这一项是按摘要里出现的参数量粗算的，精度比家族统计低。

## 稳健性

- **排除 2027 年的模板化写法（formulaic_style）后，结论不变。** Qwen 85% → 92%，Qwen3 27% → 43%，Qwen3.5/3.x 16%，Llama 28% → 10%，R1-Distill 10% → 3.4%，OLMo 1.2% → 5.3%，"只提 Qwen" 56% → 76%。
- **换一个更严格的总体，结论也不变。** 只用 RLVR / GRPO 主题簇（47、213、148、258，2026 年 452 篇、2027 年 641 篇）重算：Qwen 88% → 91%，Qwen2.5 文本 54% → 25%，Qwen3 24% → 48%，Llama 36% → 10%，OLMo 2.2% → 6.8%。

## 代表论文（可点开核对分类）

- 2027 · Qwen3.5 基座：[ReCrit: Transition-Aware RL for Scientific Critic Reasoning](https://openreview.net/forum?id=7Pq65oEpUz)，在 Qwen3.5-4B / 9B 上训练
- 2027 · Qwen2.5-VL 与 Qwen3-VL 并用：[DSE-GRPO](https://openreview.net/forum?id=9tCqG6qhEe)
- 2027 · OLMo-3：[Questioning Instrumental Convergence in RLVR: Checkpoint Evidence from OLMo-3](https://openreview.net/forum?id=iKvECCrAgT)；[Fork Where the Model Changes Its Mind](https://openreview.net/forum?id=M0U0oFBtCG)，用 OLMo-3-7B
- 2027 · Gemma 4 + Qwen3：[Let Intuition Teach Deliberation (PSP-ME)](https://openreview.net/forum?id=ed5Ey0bNLU)
- 2027 · gpt-oss：[AutoCode-RL](https://openreview.net/forum?id=iB68aU9HOu)，训练 GPT-OSS-20B
- 2026 · Llama 基座：[Language Models That Think, Chat Better](https://openreview.net/forum?id=trBEiQFkxw)，用 Llama-3.1-8B 和 Qwen-2.5-7B
- 2026 · R1-Distill 基座：[Towards Flash Thinking via Decoupled Advantage Policy Optimization](https://openreview.net/forum?id=HUmX5C9uF4)
- 家族差异的争论：2026 年的 [Spurious Rewards](https://openreview.net/forum?id=4NeiwxQ2Bp)，2027 年的 [Recovering RLVR from Failing Spurious Rewards](https://openreview.net/forum?id=nkauNYPBcW)

## 方法说明

- **总体。** 范围是 2026–27 年的全部投稿，包括被撤稿和桌拒的论文。满足以下任一条件即计入：
  1. 标题、关键词或摘要命中 RLVR / GRPO 类术语（RLVR、verifiable reward、GRPO、DAPO、GSPO、RLOO、R1-Zero、rule-based reward 等），并且提到 LLM、VLM 或推理模型；
  2. 属于 RL-for-LLM 主题簇（47、213、148、258、111）并提到 RL。

  我排除了图像/视频扩散生成方向的 GRPO 论文，因为它们的基座是 SD、FLUX 这类模型，不是 LLM。结果是 2026 年 852 篇（每万篇投稿 430 篇），2027 年 1,804 篇（每万篇 419 篇），也就是这个方向占全部投稿的比例基本没变。没有使用 TL;DR 字段，因为只有 2027 年有。
- **测量。** 模型名是有固定拼写的实体，所以我用正则词典逐篇匹配标题、关键词和摘要。匹配 Qwen、Llama 时排除了 "R1-Distill-Qwen/Llama"，这类单独计入 R1-Distill。
- **分母。** 主表的分母是"点名了至少一个开源基座家族的论文"。原因是点名率本身变化很大：2026 年只有 20.8% 的论文点名基座，2027 年是 35.6%，其中一部分来自 2027 年的模板化写法。如果按占总体的比例看，Qwen 是 17.7% → 33.3%，Llama 是 6.0% → 3.4%。
- **"提到"不等于"用作基座"。** 我读了被点名段落的上下文：DeepSeek 非 Distill 系列和 R1-Distill 全部读了，Llama、OLMo、Gemma、gpt-oss、Kimi、GLM、Mistral、Nemotron 也全部读了，Qwen 每年抽读 30 篇，总计约 400 段。Qwen、Llama 和 R1-Distill 有约 90–95% 确实是被训练或研究的模型，OLMo 和 Gemma 约 80–85%，gpt-oss 约一半。DeepSeek-R1/V3、GPT、Kimi、GLM 大多不是基座，所以单列说明，没有放进主表。
- **局限。**
  - 只能看到摘要里写出来的模型。约 64–79% 的论文没有点名基座，只写"a 7B model"之类，或者完全不提。
  - 本次没有子代理可用，所以没有按 skill 推荐的方式逐篇阅读、给每篇论文打"基座/对比"标签，只做了上下文抽读。逐篇打标签可以把主表从"被点名"进一步收紧到"被训练"。
  - 2027 年还没有审稿结果，所以没法看哪些基座更受审稿人认可。
