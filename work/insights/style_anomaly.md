# ICLR 2027 投稿中的“程式化文风”：定量检验

> 复现：`python scripts/style_anomaly.py && python scripts/style_dashboard.py`
> 产出：`work/insights/style_anomaly.json`（全部数字）、`style_anomaly_papers.parquet`（逐篇分数）、`style_dashboard.json`（看板段落）
> 数据：2025 年 11,672 篇，2026 年 19,813 篇（均为最终状态，含撤稿/桌拒），2027 年 43,013 篇（2026-10-07 评审前快照：active 42,378 / desk_rejected 419 / withdrawn 216）。

## 0. 结论速览

1. **范围比预想的大得多，不是少数几簇的小浪潮。** 阈值按“2026 年只有 1% 超过”校准，2027 年有 **42.4%** 超过（2025 年 0.45%）。2027 年的中位数论文（6.2）已接近 2026 年的第 99 百分位（7.2），所有 21 个 primary area 都在 32–57% 之间。
2. **这是一次语域替换，不只是新增了一些词。** 上升的是 *evidence, the same, fixed, every, frozen, matched, whether, held-out, rather than*；下降的是 *novel (287→48‰), approach, significantly, our approach, propose a, due to*。2023–25 年常被当作“LLM 腔”的词（delve, showcase, underscore, comprehensive, intricate）同样下降约 70–90%。
3. **语域在单篇论文内部是一致的。** 标题不参与打分，但“X Is Not Y / When does …? / evidence / audit”这类标题模板的比例随摘要分数单调上升（2.5% → 21.7%）。标记在同一篇论文中扎堆出现（离散指数 2027 年 2.04，2026 年 1.29）。
4. **没有复制粘贴或批量模板的迹象，也没有“质量”信号。** 近重复摘要（cos > 0.8）在 2027 年为 0.04%，与往年同量级。快照中的桌拒/撤稿率不随分数变化。2026 年分数与录用（OR 0.99/SD）、评分（ρ ≈ 0）都无关。
5. **对趋势解读的影响：** 簇 70 / 137 / 252 / 196 中 85–93% 的论文超过阈值，coherence = 1 的簇平均 55%。这些簇的增长有相当部分来自措辞，而不是研究方向本身。

---

## 1. 词汇标记

**方法。** 只用摘要的 unigram + bigram（min_df = 30；标题单独作为模板分析）。用 Monroe, Colaresi & Quinn (2008) 的带信息性 Dirichlet 先验的 log-odds ratio（先验 = 2025–27 合并词频的 1%）计算 z 值，分别比较 2026→2027 和 2025→2026。“风格/功能词”的限制条件如下：

- **与主题无关**：该词在 2027 年各 primary area 间的分布与总体分布的 KL < 0.10 nats；
- 不在手工列出的主题名词表中（agent, policy, reward, retrieval, token 等约 150 个），不含数字；
- 2026 年覆盖率 < 50%（排除 *the* 这类已饱和、逐篇无区分度的词）；
- 支持度要求：2027 年覆盖率 ≥ 2%，2027/2026 比值 ≥ 2；
- unigram 与 bigram 去冗余（如果 bigram 的 2027 年论文有 ≥ 80% 已被所含 unigram 覆盖，就只保留 unigram）。

**上升最显著的 40 个标记**（每 1,000 篇摘要中出现该词的论文数）：

| # | 标记 | 2025 | 2026 | 2027 | z 26→27 | z 25→26 | 权重 ln(r27/r26) |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | evidence | 22 | 37 | 175 | 59.7 | 7.4 | 1.56 |
| 2 | same | 66 | 56 | 242 | 53.0 | -4.6 | 1.47 |
| 3 | fixed | 29 | 46 | 202 | 47.9 | 6.7 | 1.48 |
| 4 | every | 14 | 14 | 156 | 46.7 | -1.4 | 2.43 |
| 5 | one | 105 | 73 | 200 | 46.4 | -9.7 | 1.00 |
| 6 | points | 38 | 36 | 139 | 42.2 | -3.5 | 1.36 |
| 7 | shared | 21 | 36 | 147 | 40.2 | 7.5 | 1.39 |
| 8 | frozen | 8 | 14 | 113 | 38.6 | 3.6 | 2.12 |
| 9 | whether | 41 | 44 | 149 | 37.9 | 1.6 | 1.21 |
| 10 | no | 45 | 51 | 151 | 37.6 | 3.0 | 1.08 |
| 11 | changes | 28 | 28 | 122 | 37.3 | -1.4 | 1.48 |
| 12 | does | 45 | 30 | 132 | 37.3 | -6.9 | 1.49 |
| 13 | so | 30 | 22 | 114 | 36.9 | -4.9 | 1.66 |
| 14 | what | 22 | 22 | 102 | 35.9 | -0.6 | 1.52 |
| 15 | from … to | 17 | 20 | 94 | 35.2 | 1.6 | 1.54 |
| 16 | support | 35 | 53 | 146 | 35.0 | 7.3 | 1.00 |
| 17 | before | 21 | 26 | 110 | 33.7 | 2.4 | 1.47 |
| 18 | four | 35 | 44 | 134 | 33.6 | 3.8 | 1.10 |
| 19 | matched | 3 | 6 | 99 | 33.3 | 1.5 | 2.90 |
| 20 | controlled | 14 | 26 | 114 | 33.3 | 6.4 | 1.50 |
| 21 | evaluated | 27 | 30 | 118 | 33.3 | 1.2 | 1.38 |
| 22 | uses | 41 | 43 | 136 | 32.5 | 0.6 | 1.15 |
| 23 | alone | 9 | 15 | 97 | 32.4 | 3.3 | 1.89 |
| 24 | after | 40 | 33 | 112 | 31.0 | -2.8 | 1.21 |
| 25 | rather than | 31 | 56 | 143 | 30.7 | 10.2 | 0.93 |
| 26 | change | 16 | 15 | 77 | 30.6 | -0.8 | 1.66 |
| 27 | therefore | 32 | 23 | 101 | 29.9 | -4.4 | 1.46 |
| 28 | the resulting | 16 | 22 | 97 | 29.7 | 2.9 | 1.48 |
| 29 | a fixed | 13 | 18 | 86 | 29.4 | 2.4 | 1.59 |
| 30 | whose | 15 | 20 | 86 | 29.0 | 3.2 | 1.44 |
| 31 | strongest | 3 | 9 | 75 | 28.8 | 5.2 | 2.10 |
| 32 | these results | 19 | 58 | 151 | 28.8 | 14.7 | 0.96 |
| 33 | five | 21 | 30 | 95 | 28.3 | 4.5 | 1.15 |
| 34 | own | 12 | 17 | 73 | 28.2 | 3.3 | 1.47 |
| 35 | relative | 25 | 43 | 116 | 28.2 | 8.2 | 0.99 |
| 36 | must | 21 | 27 | 94 | 28.1 | 2.9 | 1.24 |
| 37 | separate | 13 | 18 | 81 | 28.0 | 2.3 | 1.52 |
| 38 | requires | 60 | 74 | 160 | 27.2 | 4.9 | 0.76 |
| 39 | should | 24 | 22 | 78 | 26.9 | -1.3 | 1.27 |
| 40 | together | 18 | 37 | 108 | 26.8 | 9.2 | 1.06 |

**观察中点名的短语**（标题或摘要中出现，每 1,000 篇）：

| 短语 | 2025 | 2026 | 2027 |
|---|---:|---:|---:|
| held fixed / holding … fixed | 0.0 | 0.2 | 11.8 |
| matched | 3.3 | 7.0 | 127.0 |
| exact / exactly | 19.6 | 22.0 | 119.1 |
| frozen | 7.5 | 14.1 | 119.1 |
| paired | 10.4 | 19.6 | 68.3 |
| held-out | 2.3 | 3.0 | 64.4 |
| audit / auditing | 4.5 | 10.8 | 52.9 |
| certified / certify | 4.8 | 5.7 | 32.5 |
| pre-registration / preregistered | 0.3 | 0.1 | 8.1 |
| evidence | 22.4 | 39.1 | 181.9 |

**下降的词，以及 2025→2026 的情况。** 下降最显著的是 *novel*（366 → 287 → 48）、*a novel*、*approach*、*significantly*（208 → 166 → 33）、*in this*、*our approach*、*critical*、*due to*、*propose a*。旧的“LLM 腔”词表（Liang et al. 2024; Kobak et al. 2024）在 2027 年接近消失：delve 5.5 → 0.6 → 0.1，showcase 28 → 11 → 1.2，underscore 27 → 27 → 2.2，comprehensive 105 → 91 → 17。
用同样的过滤条件看 2025→2026，上升最多的是 *framework that* (60 → 188)、*benchmarks*、*strong*、*consistently*、*achieves*、*paradigm*、*enabling*、*critical*、*unified*，属于推销式修辞，而且**这些词在 2027 年全部回落**（z₂₆→₂₇ 为 −7 到 −45）。40 个 2027 年标记中，绝大多数在 2025→2026 的 |z| < 10，只有 *these results*（14.7）和 *rather than*（10.2）提前出现了上升。也就是说，这套写法在 2027 年是**突然出现**的。

**标题模板**（每 1,000 篇）：

| 模板 | 2025 | 2026 | 2027 |
|---|---:|---:|---:|
| 含 “?” 的问句标题 | 27.9 | 28.5 | 53.7 |
| 以 When / What 开头 | 4.5 | 7.6 | 32.7 |
| “When does/is/can …” | 0.6 | 1.1 | 8.6 |
| “X Is/Are Not Y” | 0.7 | 1.7 | 11.4 |
| 含 evidence | 0.6 | 3.0 | 29.4 |
| 含 audit | 1.5 | 2.3 | 14.4 |
| 全大写标题 | 13.4 | 11.3 | 22.9 |
| Towards …（对照：下降） | 16.7 | 13.6 | 5.3 |

## 2. 程式化文风分数

**定义（透明、可复算）。** `score = Σ_{k=1..40} ln(r27_k / r26_k) · 1[标记 k 出现在摘要中]`，即对出现的标记按“2027 年相对 2026 年的倍数”取对数加权求和。权重在 0.76–2.90 之间，常见标记约为 1.0–1.5。阈值取 2026 年分数的第 99 百分位，**score > 7.18**。

| 年份 | P10 | P25 | 中位数 | P75 | P90 | P99 | 超过阈值 | 平均标记数 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025 | 0.0 | 0.0 | 1.15 | 2.32 | 3.60 | 6.54 | 0.45% | 1.10 |
| 2026 | 0.0 | 0.0 | 1.24 | 2.53 | 4.02 | 7.18 | 1.00% | 1.29 |
| 2027 | 1.27 | 3.07 | 6.16 | 9.97 | 13.69 | 19.93 | **42.4%** | 4.93 |

- **分布形态。** 2027 年是单峰的整体右移加长尾，并没有分离出一个独立的“第二群体”。90.1% 的 2027 年论文高于 2026 年中位数，24.1% 高于 2026 年的第 99.9 百分位。
- **稳健性。** (a) Split-half：在随机一半论文上重新选词定权，在另一半上评估，2027 年超过阈值的比例为 44.2%（2026 年 1.01%），两次选出的 40 个标记有 39 个重合。(b) 分数与摘要长度相关（r = 0.28 / 0.28 / 0.48），按 2026 年摘要长度五分位分别定阈值后，比例为 41.2%。(c) 标记共现：按长度分层后，标记计数的方差与“标记独立出现”时的方差之比，2025 年 1.21，2026 年 1.29，2027 年 2.04。2027 年标记明显扎堆，说明存在“整套采用”这种写法的论文。
- **按 primary area。** 2026 年所有领域都 ≤ 1.6%。2027 年最高的是可解释性 56.8%、迁移/元学习 51.0%、基础/前沿模型 50.5%、基础设施 48.3%、数据集与基准 47.9%；最低的是优化 31.7%、生成模型 33.1%、图学习 34.0%、因果推理 35.1%。
- **按主题。** eval 61.6%、interp 57.4%、agents 53.0%、llm_post 46.0% …… vision 32.3%、rl 31.5%、gen 31.0%。
- **按簇。** 观察中点名的簇如下：

| 簇 | 名称 | n25 / n26 / n27 | 超过阈值 | 平均分 |
|---|---|---|---:|---:|
| 70 | Benchmark validity and evaluation audits | 1 / 1 / 367 | 92.9% | 14.3 |
| 137 | Audit-style boilerplate abstracts (coh = 1) | 0 / 0 / 561 | 87.7% | 12.4 |
| 196 | Tool-agent runtime governance | 0 / 1 / 337 | 85.2% | 11.6 |
| 15 | Formulaic gradient-analysis papers (coh = 1) | 1 / 6 / 267 | 68.9% | 9.7 |
| 83 | Representation geometry diagnostics (coh = 1) | 2 / 7 / 248 | 68.1% | 10.0 |
| 33 | Sample complexity & minimax bounds | 6 / 16 / 348 | 58.3% | 8.2 |

  其他比例很高的簇：252 RAG evidence selection（87.7%）、263 Causal interventions in mech-interp（79.9%）、223 Test-time training（71.1%）。
  15 个“新簇”（2025+2026 合计 ≤ 10 篇）占 2027 年论文的 9.3%，其中 70.3% 超过阈值（其余簇为 39.5%）。但这些新簇只占全部高分论文的 15.5%，**84.5% 的高分论文仍落在已有主题簇中**。coherence = 1 的簇合计 54.7%，coherence = 3 的簇为 40.7%。

## 3. 区分信号

| 指标（均值） | 2025 | 2026 | 2027 高分（> 阈值） | 2027 中间 | 2027 低分（≤ 2026 中位数） |
|---|---:|---:|---:|---:|---:|
| n | 11,672 | 19,813 | 18,219 | 20,517 | 4,277 |
| 摘要词数 | 188 | 185 | 223 | 192 | 173 |
| 句数 | 8.1 | 7.9 | 9.6 | 8.4 | 7.6 |
| 每句词数 | 23.5 | 23.8 | 23.8 | 23.3 | 23.4 |
| 摘要中的数字个数 | 1.4 | 1.7 | 5.3 | 2.6 | 1.5 |
| 含百分比 | 18% | 23% | 50% | 30% | 18% |
| 关键词数 | 3.73 | 3.77 | 4.93 | 4.11 | 3.79 |
| 标题词数 | 9.1 | 9.3 | 9.7 | 9.3 | 9.3 |
| 程式化标题模板 | 1.4% | 2.3% | 15.1% | 5.9% | 2.5% |
| 全大写标题 | 1.3% | 1.1% | 3.3% | 1.7% | 1.1% |
| 有 TL;DR | – | – | 60.6% | 52.6% | 49.7% |
| 含至少一个“旧式”下降词 | 98.5% | 96.0% | 46.2% | 70.8% | 86.5% |
| 桌拒（2027 年为快照） | 0.6% | 4.6% | 1.05% | 0.9% | 0.8% |
| 撤稿（2027 年为快照） | 25.6% | 25.7% | 0.52% | 0.5% | 0.6% |

- **标题是独立旁证。** 标题不参与打分，但程式化标题模板的比例按 2027 年分数十分位依次为 2.5, 3.8, 4.7, 6.0, 7.3, 8.9, 10.5, 13.3, 15.8, 21.7%，单调上升。
- **写法特征。** 高分摘要更长（多出约 2 句），句子长度不变，数字是 2026 年的 3 倍，并大量交代控制条件，例如“primary reading fixed before dispatch”“frozen before access”“exact p = 1.0; bootstrap 95% interval”。低分的 2027 年论文在各项指标上都和 2026 年几乎一样。
- **TL;DR。** 2025/26 年的数据里没有 TL;DR，无法跨年比较；2027 年内部，高分论文填写 TL;DR 的比例高出约 11 个百分点。
- **近重复摘要**（TF-IDF，sublinear tf，cos > 0.8，在同一年内比较）：2025 年 3 对（0.05%），2026 年 2 对（0.02%），2027 年 9 对（0.04%）；从 2027 年等量抽取 19,813 篇时为 2 对。高分论文中的比例为 0.02%，比非高分论文还低。这 9 对多是同一题材的成对论文（例如两篇同名 dataset 论文、3DGS 水印、缝纫版型、两篇占位标题“interactive world model”），分数在 0–9.4 之间，与程式化文风无关。阈值放宽到 0.6 后结论不变。**没有证据表明存在批量生成的近似变体。**
- **快照状态。** 桌拒率在 2027 年各分数十分位间为 0.70–1.26%，撤稿率为 0.35–0.67%，都没有梯度。注意快照是评审前的状态，与 2025/26 的最终撤稿率不可比。
- **提交顺序。** 按 submission number 十分位，高分比例从 39% 升到 53%，越晚提交的论文这种写法越多。
- **2026 年的录用与评分**（只看进入评审的论文，n = 13,811）：
  - 未加控制时，高分论文的录用率为 46.7%（n = 137），其余为 38.7%；
  - Logit（控制 log 摘要长度和 primary area 固定效应）：每 1 SD 分数对应 OR = 0.99（95% CI 0.96–1.03）；
  - 平均评分：Spearman ρ = −0.002（p = 0.78）；OLS 每 1 SD 分数对应 −0.019 分（SE 0.010），实际上可以忽略；评分按分数十分位在 4.49–4.55 之间波动；
  - 未加控制时的录用差异在控制领域和摘要长度后消失。由于 2026 年采用这种写法的论文很少（n = 137），不能外推到 2027 年的评审。

## 4. 示例

**分数最高的 12 篇 2027 年论文**（仅表示措辞上的典型，不对来源作任何判断）：

| id | score | 簇 | 标题 |
|---|---:|---|---|
| R1QnIz34Ut | 29.9 | 137 | HOW MUCH INDEPENDENT INFORMATION DOES AN LLM COMMITTEE PROVIDE? |
| 8QGJ2dnd8j | 29.6 | 70 | StrataBench: Expert-Grounded Evaluation for Oil and Gas Land and Title（快照中为 desk_rejected） |
| 90ibjymozF | 29.1 | 263 | Reading and Writing: Testing Natural Language as a Causal Channel for Refusal |
| 950or2jh05 | 29.1 | 57 | Learning a Behavioral Skill Basis for AI Agents |
| 0yDuLVVVWn | 28.4 | 70 | Matched Twins Show What an Evidence Contract Cannot Carry to a Verifier of ML-Experiment Claims |
| aCc0AKg8B4 | 28.1 | 173 | What Can a Leaderboard Certify? Compositional Controllability for Fair Evaluation and Training of Biomedical Literature-Review Agents |
| lSUr28odRy | 28.0 | 123 | Relational Composition as Parallel Transport: What Per-Entity Frames Force in Attention |
| iFUFUDHcyH | 27.7 | 131 | SAUNA: Source-Anchored Unsupervised Neural Adaptation for Cross-Subject EEG Decoding |
| qd4q2OE0OE | 27.3 | 83 | Hidden Tape: Addressable Communication Beneath Identical Text |
| btB6Cx4HsN | 27.2 | 165 | Relic: From Multi-Agent Collaboration to Persistent Organizational Capability |
| QsOlwlev7g | 27.1 | 2 | Same Probe, Different Numbers: Are Activation Probes Robust to Inference-Time Numerical Non-Determinism? |
| kRtggxSTIi | 27.0 | 137 | Auditing Size Dependence in Zero-Cost NAS Proxies: Confound-Controlled Discovery and Held-Out Evaluation |

“Success Is Not …”这一标题家族集中在簇 196：uZENhr0H8D *Intervention Success Is Not Mechanism Identification in Tool-Using Agents*、wvkbSz7VnD *Success Is Not Completion: …*、4Ny1njoCu6 *Success Is Not Evidence: Verifiable Autoresearch for Cryo-Electron Tomography*。

**典型低分 2027 年论文**（随机抽取，分数 ≤ 2026 年中位数，摘要 150–250 词）。它们采用常规的“问题背景、现有方法的局限、本文方法”结构：

| id | score | 标题 |
|---|---:|---|
| AeW8zDu5nu | 0.0 | Back to the Future: Reverse-Consequence Modeling for Long-Horizon Particle Dynamics |
| U5zDnvH5JD | 0.0 | Quantum Sharpness-Aware Minimization |
| AuiiWB2mFR | 1.1 | Gradient Subspace Dynamics During Supervised Fine-Tuning of LLMs: Input–Output Asymmetry |
| VUFj5cptA9 | 0.0 | Textual Environmental Context and Spatial Graphs for LLM-Based Regional SST Forecasting |
| OIbjUInQex | 1.1 | ChartGalaxy++: A Richly Annotated Dataset for Chart Understanding and Generation |

## 5. 解读（与上面的数据分开）

**数据能确认的：**
(i) 2027 年摘要和标题的措辞发生了大规模、跨领域、在单篇论文内部一致的语域迁移，从推销式（novel / significantly / framework that）转向对照与证据式（evidence / matched / held fixed / the same / whether）；
(ii) 这种迁移在部分 2027 年新簇中最集中，并且足以让基于嵌入的聚类按措辞成簇；
(iii) 它不表现为文本重复，与快照中的桌拒/撤稿无关，与 2026 年的录用和评分也无关。

**关于来源的几种假说，以及数据与它们的关系：**

- **自动化研究流水线的投稿浪潮。** 支持的证据：尾部集中在“审计 / 评测效度 / 智能体运行时治理”这类适合自动化实验的题目；高分摘要高度结构化，数字密集，带有预注册式的表述；标记扎堆出现；越晚提交的论文比例越高。不支持的证据：42% 的比例、所有领域都整体右移、没有近重复。仅靠流水线很难解释整个中位数的移动，除非这类投稿规模巨大，而本数据无法检验这一点。
- **AI 辅助写作的风格变化。** 这与“全分布右移、跨领域一致”的形态相容。但旧的 LLM 指示词在 2027 年反而几乎消失，所以如果是 AI 辅助写作，那是一种和 2023–25 年完全不同的风格指纹。这也意味着旧的词频式检测方法在 2027 年会失效，甚至给出相反的结论。
- **规范或政策的变化。** 去推销化的写作规范、2027 年新增的强制 AI 使用声明和 20 篇投稿上限，都可能改变作者的写法或投稿人群。本数据中没有 AI 使用声明的内容，也没有作者信息，所以这些机制**都无法检验**。

以上几种机制可能同时存在，而且彼此不互斥。**不应据此断言任何具体论文由 AI 生成。** 分数只度量措辞，人类作者完全可以、也确实会采用这种写法。

## 6. 对解读 2026→2027 趋势的影响

- **簇的增长要打折扣。** 簇 70 / 137 / 196 / 252 / 15 / 83 中 68–93% 的论文超过阈值，且 2025/26 年几乎没有。它们的增长应理解为“一种写法 + 若干相近话题”的混合，不能直接读作研究方向的兴起。建议对主题结论做稳健性检验：只用 keywords 或标题重新计数；在嵌入前去掉这 40 个标记和点名的短语后重新聚类；或比较剔除高分论文前后的增速。
- **关键词计数会有偏差。** 依赖 *novel / framework / significantly* 等词的计数在 2027 年会系统性偏低，依赖 *evidence / audit / certified* 的计数会偏高。
- **不要把文风当作质量信号。** 在 2026 年，它与录用和评分都无关。2027 年评审会不会对它作出反应，要等评审结果出来才知道。
- **局限。** 标记的选取用到了 2026/2027 的数据（split-half 复核已缓解过拟合）；主题名词表是人工编写的，可能有遗漏（例如 *evidence* 在 RAG 簇里同时是主题词）；2027 年是快照，状态还会变化；本数据无法区分作者、工具和流水线。
