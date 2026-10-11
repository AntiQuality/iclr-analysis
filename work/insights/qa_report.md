# QA report: quantitative claims in dashboard/src/text.json

Checked on 2026-10-11 against data/corpus.parquet, data/macro.json, data/concepts.json, data/safety.json, data/safety_labels.parquet, work/insights/style_anomaly_papers.parquet (`high`) and the chapter JSONs in work/insights/. No source files were edited.

**Conventions.** "Robust" means formulaic papers (`high`) are excluded. Recomputed robust totals are 11,620 / 19,614 / 24,794, which match `macro.json.robust_totals`. Per-10k is papers per 10,000 submissions in that year. "Recomputed" means I computed it independently from the raw parquet files, not from the aggregate JSONs. 45+ claims were recomputed this way. "Quote" means the number matches the chapter text, but I could not rebuild the chapter's exact regex.

**Summary:** 92 claims checked. **74 OK**, **4 WRONG**, **8 MISLEADING**, **6 UNVERIFIABLE**.

---

## WRONG / MISLEADING (action items)

| # | Field | Claim | Status | Correct value / issue | How checked |
|---|---|---|---|---|---|
| 40, 74 | findings[3].body + fig, ecoIntro | Qwen mentions 2026 = **3.7%** | WRONG (rounding) | 723/19,813 = **3.649% → 3.6%**. Double rounding from macro.json's 3.65. (2027 8.67% → 8.7% is fine.) | Recomputed with regex `\bqwen` over title+kw+abstract+tldr |
| 49 | findings[4].fig | "经典 RL 在 RL 论文中 **56% → 26%**" | WRONG (period) | 55.6% is the **2025** value. The chapter series is 55.6% → 30.1% → 26.2% (2025→2026→2027). For 2026→2027 it should read **30% → 26%**. | macro_embodied.json stats "548 → 471 → 359 /万篇; 55.6% → 30.1% → 26.2%" |
| 45 | findings[4].body | RAG, math reasoning, RLHF/preference optimization, MLLM eval benchmarks, GNN and classic deep RL "份额都下降了一半以上" | WRONG (partly) | Holds for RAG (cl.27 89.8→24.9), math (cl.245 95.4→26.7), RLHF/preference optimization (cl.234 42.9→10.5) and MLLM eval (cl.178 71.2→20.0). **Classic RL** by the chapter's own definition: 471→359/10k = **−24%**; only cluster 1 "general deep RL" halves (65→18). **GNN**: mention share 308→177/10k = **−43%** (robust 310→199, −36%). Main GNN cluster 285 is 95.9→54.6 (−43%). Only the 3-cluster sum (285+114+288, 161→79) reaches −51%. | Recomputed from clusters + regex; chapter quote |
| 3 | abstract[0] | 智能体 "跃升为第一大类" | MISLEADING | Raw: agents 11.55% is #1. **Robust: gen 9.95% > agents 9.43%**, so agents are #2. (In 2026 agents were #8 of 17 at 6.26%.) The page tells readers to prefer the robust measure. | Recomputed theme shares (raw and robust) from clusters.parquet + macro themes |
| 24 | findings[0].body | Agents "超过 LLM 后训练成为最大的研究方向" | MISLEADING | Beating llm_post still holds robustly (9.43% vs 8.78%). "Largest" does not: robust gen is 9.95%. The fig gives the robust 9.4% but not the rank change. | Same as above |
| 5 | abstract[0]; findings[1].title/body | Post-training mainstream recipe moved from GRPO/RLVR to OPD ("OPD 接过主角") | MISLEADING (overstated) | OPD is the fastest riser, but in 2027 **GRPO is still mentioned more**: GRPO 304/10k (GRPO+RLVR family 394) vs OPD 211 (robust 278 vs 182). GRPO did not fall (260→304). In the chapter's post-training method pool, GRPO is 38.2% and OPD 20.5%. "OPD 与 GRPO 并列" is accurate. "接过主角" is not. | concepts.json + recomputed regex; macro_llm.json |
| 10 | abstract[1] | 智能体安全、**奖励黑客**、**AI Control 和监控**"快速上升" | MISLEADING (robustness) | AGENT_SAFE 3.18× (robust 2.27×) is fine. **REWARD_HACK 1.76× falls to 1.34× robust.** **OVERSIGHT 1.54× falls to 1.13× robust** (the "AI control" microtopic is 3.0→7.0/10k, but only 6→30 papers). The radar's own keyword "reward hacking" share **falls** 55.5→46.0/10k (robust 56→44). | Recomputed sub-shares from safety_labels (rel≥1), raw and robust |
| 15 | nest[2] | "**1,062** 以智能体为对象的安全研究" | MISLEADING (definition mismatch) | 1,062 is the agent-safety chapter's *scope*: sub/sub2 ∈ {PI, AGENT_SAFE} **or** target ∈ {agent, multiagent}. That is 17.8% of safety papers. Everywhere else, "以智能体为对象" (findings[7], safetyKpis) means target ∈ {agent, multiagent}, which is **982 papers = 16.4%**. Either relabel the nest as "智能体安全（范围）" or use 982. | Recomputed both definitions from safety_labels |
| 25 | findings[0].body | "RAG、通用多智能体框架和 deep research 基准在该大类中的占比从 42% 降到 14%" | MISLEADING (minor) | The 42.3%→13.9% basket also contains **LLM 具身任务规划 (cl.69)** and **社会模拟/心智理论 (cl.168)**, i.e. clusters 27+69+168+157+251. Robust: **42% → 19%**. | Recomputed from cluster shares (264.4/626 → 160.3/1155) |
| 51 | findings[5].body | "flow matching **取代**扩散 … VGGT 式前馈 3D 重建**取代**逐场景优化" | MISLEADING (overstated) | This is a share shift, not a replacement. In 2027 diffusion phrasing is still **2.3×** flow matching (730 vs 317/10k; radar 521 vs 266). 3DGS is still about 105/10k vs feed-forward 3D at 36/10k. Robust, diffusion falls less (radar 813→644). | macro_mmgen.json + concepts.json + recomputed regex |
| 63 | findings[8].fig | "持久状态 **16 → 206 篇**" | MISLEADING (counts not shares) | Raw counts (12.9×) while safety papers doubled. As a share of safety papers it is **0.5% → 3.4% (robust 2.8%)**, about 6×. Use the share as the thesis chapter does. | safety_thesis.json fig; approximate regex recompute is directionally consistent (robust < raw) |

## UNVERIFIABLE

| # | Field | Claim | Note |
|---|---|---|---|
| 53 | findings[5].fig | flow matching 200→317 vs diffusion 998→730 /10k | Matches macro_mmgen.json, but I could not reproduce it with any reasonable regex (e.g. `flow matching\|rectified flow` gives 179→266; `diffusion model\|denoising` gives 899→670). The dashboard's own radar shows **179→266 vs 811→521**, so two sets of numbers for the same concept appear on one page. |
| 54 | findings[5].fig | feed-forward 3D 12.6→35.8 | Matches the chapter. The radar (concepts.json) shows 15.6→33.0. Not reproduced exactly. |
| 76 | ecoIntro | "GSM8K、AIME 等数学基准开始饱和" | Saturation is not measured. Mention shares: GSM8K flat (86→87/10k raw; robust 84→58), AIME 130→56. |
| 87 | method[0] | Official 2026 valid submissions 19,525 | External fact; not in the data. |
| 88 | method[0] | Media "2027 年超过 6 万篇" were abstract registrations | External fact. |
| 92 | method[0] / byline2 | 2027 snapshot date 2026-10-07 | Not in the data. Consistent with the guides. |

Also worth noting (consistency, not counted as errors):
- Bio/chem risk counts differ across chapters. safety_thesis (used in findings[9]) gives **4→9**. safety_oversight microtopic gives **4→12**. The "~0.2% of safety papers" conclusion holds either way (9/5,974 = 0.15%; 12/5,974 = 0.20%).
- DPO 96→57 / RLHF 94→27 (findings[1].fig) reproduce **only** with acronym-only regexes (`\bdpo\b`, `\brlhf\b`). The radar uses full names and shows 113→65 / 98→29. macro_llm calls the RLHF series "经典 RLHF+奖励模型", but it counts only the token "RLHF".
- The robust Spearman 0.04 (findings[9]) reproduces only when formulaic papers are dropped from 2027 alone and 2026 keeps the full denominator. Dropping them in both years, as macro.json share_r does, gives 0.01. The conclusion is unchanged.
- The single 2026 OPD paper ("2026 年没有一篇 OPD 论文被录用") was **withdrawn**, so n = 1. This is true but carries little information.

---

## Full claim ledger

R = recomputed independently from raw data; Q = matches chapter quote; A = arithmetic or aggregate JSON check.

| # | Field | Claim | Status | Check |
|---|---|---|---|---|
| 1 | abstract[0] | 43,013 submissions | OK | R: corpus count |
| 2 | abstract[0] | 2.17× of 19,813 | OK | R: 43,013/19,813 = 2.171 |
| 3 | abstract[0] | agents became the largest category | MISLEADING | see above |
| 4 | abstract[0] | increment from agent components | OK | R: clusters 282/57/176/92/225 go 9.1→234.6/10k (robust 175) |
| 5 | abstract[0] | GRPO/RLVR → OPD mainstream | MISLEADING | see above |
| 6 | abstract[0] | world models/embodied share more than doubled | OK | R: 2.62%→6.29% (2.4×), robust 6.40% |
| 7 | abstract[0] | RAG, RLHF/DPO, MLLM eval, GNN clearly receding | OK | R: all fall (RAG −72%, DPO −42%, MLLM-eval cl.178 −72%, GNN −43%) |
| 8 | abstract[1] | safety share 15.0%→13.9% | OK | R: 2,975/19,813 = 15.02%; 5,974/43,013 = 13.89% (robust 2027 = 13.0%) |
| 9 | abstract[1] | jailbreak attacks halved | OK | R: JB_ATK 59.6→27.0/10k (0.45×, robust 0.51×) |
| 10 | abstract[1] | reward hacking / AI control / monitoring rising fast | MISLEADING | see above |
| 11 | abstract[2] | 21 primary areas | OK | R: 21 unique per year |
| 12 | abstract[2] | 300 clusters / 114 trackers / 26 safety subfields | OK | A: macro.clusters = 300, concepts = 114, safety subs = 26 |
| 13 | nest[0] | 43,013 | OK | R |
| 14 | nest[1] | 5,974 with rel ≥ 1 | OK | R: 1,679 + 4,295 |
| 15 | nest[2] | 1,062 agent-targeted safety papers | MISLEADING | see above |
| 16 | nest[3] | 56 Agent-Skills supply-chain papers, 0 in 2026 | OK | Q: safety_agent microtopic; R approx: skill-attack regex 0→51 |
| 17 | kpis[0] | 43,013, 2.17× | OK | R |
| 18 | kpis[1] | 216 withdrawn / 419 desk reject | OK | R: status counts 2027 |
| 19 | kpis[2] | 300 clusters, TF-IDF + KMeans | OK | scripts/cluster_topics.py |
| 20 | kpis[3] | 10,381 labelled, 60 agents | OK | R: safety_labels rows; work/safety/batches has 60 |
| 21 | kpis[4] | 27.0% = 5,358/19,813 | OK | R: 224 oral + 5,134 poster; 27.04% |
| 22 | kpiNote | share-based comparison; same population basis | OK | Both years are all submissions incl. withdrawn/desk-rejected. Caveat: 2027 withdrawals are mostly still to come. |
| 23 | findings[0] | agents 6.3%→11.6% | OK | R: 6.26→11.55 |
| 24 | findings[0] | largest research direction | MISLEADING | see above |
| 25 | findings[0] | classic basket 42%→14% | MISLEADING | see above |
| 26 | findings[0].fig | robust 9.4% | OK | R: 2,337/24,794 = 9.43% |
| 27 | findings[0].fig | harness/skills/self-improvement/experience memory 9→235/10k | OK | R: 9.08→234.58 (robust 8.7→175) |
| 28 | findings[1] | OPD 1→907 papers | OK | R: `on-policy (self-)?distillation\|\bopd\b\|\bopsd\b` gives 1→907 |
| 29 | findings[1] | GRPO share roughly unchanged | OK | R: GRPO 260→304/10k (+17%), robust 257→278 (+8%); chapter family +7% |
| 30 | findings[1] | DPO and RLHF clearly falling | OK | R |
| 31 | findings[1] | no 2026 OPD paper accepted | OK (trivial) | R: n = 1, withdrawn |
| 32 | findings[1].fig | OPD 0.5→211/10k, robust 182 | OK | R: 210.87; robust 181.9 |
| 33 | findings[1].fig | DPO 96→57, RLHF 94→27 | OK (acronym-only) | R: `\bdpo\b` 95.9→57.2; `\brlhf\b` 94.4→27.4; see note |
| 34 | findings[1].title | "OPD 接过主角" | (covered by #5) | |
| 35 | findings[2] | embodied 2.6%→6.3%, fastest-growing theme | OK | R: 2.40× vs agents 1.85× (robust 2.44× vs 1.51×) |
| 36 | findings[2] | WAM 1→372 papers | OK | R: concept regex 1→372 |
| 37 | findings[2] | JEPA/latent planning ~10× | OK | R: JEPA 8.6→89.5 (10.4×; robust 9.8×) |
| 38 | findings[2].fig | LIBERO 21→131 | OK | R: `libero` 20.7→130.9/10k (unit "/万篇" missing in fig) |
| 39 | findings[2].fig | embodied robust 6.4% | OK | R |
| 40 | findings[3] | Qwen 3.7%→8.7% | WRONG (rounding) | see above |
| 41 | findings[3] | Llama and GPT falling | OK | R: Llama 3.07→2.47%, GPT 3.71→1.83% |
| 42 | findings[3].fig | LLM papers: Qwen 21.1% vs Llama 6.6% (~3:1) | OK | R: llm_core + llm_post clusters 21.1% / 6.6% |
| 43 | findings[3] | RL/OPD papers ~10:1 | OK | R: GRPO/RLVR/OPD papers in LLM themes 33.7% vs 3.4% (9.9:1); chapter 31.4 vs 3.0 |
| 44 | findings[3] | Qwen3-VL becomes default; GPT-4o → GPT-5 | OK | R: Qwen3-VL 0.5→74.4/10k; GPT-4o/4V 144→28; GPT-5 77→126 |
| 45 | findings[4] | all fell by more than half | WRONG (partly) | see above |
| 46 | findings[4].fig | RAG 90→25 | OK | R: cl.27 89.8→24.9 (robust 90.8→32.7) |
| 47 | findings[4].fig | math reasoning 95→27 | OK | R: cl.245 95.4→26.7 |
| 48 | findings[4].fig | RLHF/preference optimization 43→11 | OK | R: cl.234 42.9→10.5 |
| 49 | findings[4].fig | classic RL 56%→26% of RL papers | WRONG | see above |
| 50 | findings[5] | generative theme did not expand | OK | R: gen 9.61→8.31% raw; robust 9.63→9.95% (~flat); mm+gen+vision 21.4→19.3% |
| 51 | findings[5] | flow replaces diffusion; feed-forward 3D replaces per-scene optimization | MISLEADING | see above |
| 52 | findings[5] | autoregressive streaming video ~3× | OK | A: cl.112 12.6→38.4 (3.05×; robust 3.4×) |
| 53 | findings[5].fig | flow 200→317 vs diffusion 998→730 | UNVERIFIABLE | see above |
| 54 | findings[5].fig | feed-forward 3D 12.6→35.8 | UNVERIFIABLE | see above |
| 55 | findings[6] | 42% / 1.0%→42.4% above threshold | OK | R: high rate 0.45% / 1.00% / 42.36% |
| 56 | findings[6].fig | "novel" 287→48 per 1,000 | OK | R: `\bnovel\b` in abstracts 288→51 (chapter tokenization differs slightly) |
| 57 | findings[6] | unrelated to 2026 acceptance | OK | R: acceptance by score decile 26–29%; Spearman(score, rating) = 0.01 |
| 58 | findings[6] | not copy-paste | OK | R: near_dup = 18 papers (9 pairs) in 2027 |
| 59 | findings[7] | safety 15.0%→13.9% | OK | R |
| 60 | findings[7].fig | agent-targeted 6.3%→16.4% (robust 13.8%) | OK | R: target ∈ {agent, multiagent}: 186/2,975, 982/5,974; robust 13.8% |
| 61 | findings[7].fig | AGENT_SAFE 3.2×, jailbreak 0.45×, alignment training 0.51× | OK | R: 3.18 / 0.453 / 0.506 (robust 2.27 / 0.51 / 0.52) |
| 62 | findings[7] | alignment / oversight / governance / trust also becoming agent-focused | OK | Q: safety_thesis (2.8→10.1, 4.4→9.1, 1.8→4.9, 3.7→6.3) |
| 63 | findings[8].fig | persistent state 16→206 papers | MISLEADING | see above |
| 64 | findings[8].fig | deployment transforms 42→188; 1.4%→3.1% (robust 3.3%) | OK | Q + A: 42/2,975 = 1.41%, 188/5,974 = 3.15%; broad regex shows robust ≈ raw |
| 65 | findings[8].fig | verifier/rubric : RM/RLHF 0.82→3.19 | OK | Q + A: 6.7/8.2 = 0.82, 12.8/4.0 = 3.2 (robust 2.27 not shown) |
| 66 | findings[8] | deployment cluster 2026 acceptance 31% | OK (quote) | Q: safety_thesis |
| 67 | findings[8] | three trends survive robustness check | OK | Q: thesis says the first four survive |
| 68 | findings[9].fig | Spearman ρ = 0.16 (robust 0.04) | OK | R: 0.162 (p = 0.43) over 26 subfields; robust 0.038 (see note) |
| 69 | findings[9] | harmful fine-tuning robustness 55% acceptance, barely grew | OK | R: FT_ROBUST 0.545, ×1.07 |
| 70 | findings[9] | value alignment 38%, share halved | OK | R: VALUES 0.379, ×0.52 |
| 71 | findings[9] | agent safety 2026 acceptance 21.5% | OK | R: AGENT_SAFE 0.215 (also chapter scope 47/219) |
| 72 | findings[9].fig | baseline 27% | OK | R |
| 73 | findings[9].fig | bio/chem 4→9, loss-of-control 5→11, ~0.2% each | OK | Q: thesis; 0.15% / 0.18%; oversight chapter says bio 4→12 (see note) |
| 74 | ecoIntro | Qwen 3.7%→8.7% | WRONG (rounding) | see #40 |
| 75 | ecoIntro | LIBERO ~6×, SWE-bench ~3× | OK | R: 6.3× (20.7→130.9); 3.4× (18.7→63.2) |
| 76 | ecoIntro | GSM8K/AIME saturating | UNVERIFIABLE | see above |
| 77 | safetyIntro[0] | 10,381 candidates, 60 agents, rel 0/1/2, 26 subfields | OK | R |
| 78 | safetyIntro[1] | 15.0%→13.9%; core 11.0%→10.0% | OK | R: rel = 2: 2,179/19,813 = 11.0%; 4,295/43,013 = 9.99% |
| 79 | safetyIntro[2] | 46% of 2027 safety papers formulaic vs 42% overall | OK | R: 45.97% / 42.36% |
| 80 | safetyKpis[0] | 5,974; 2026 2,975; 15.0%→13.9% | OK | R |
| 81 | safetyKpis[1] | AGENT_SAFE 3.2×, 32.8→104.4 | OK | R (robust 2.27× not shown) |
| 82 | safetyKpis[2] | jailbreak 0.45×, 59.6→27.0 | OK | R |
| 83 | safetyKpis[3] | agent-targeted 16.4% / 6.3% / robust 13.8% | OK | R (conflicts with nest 1,062, see #15) |
| 84 | safetyKpis[4] | deployment transforms 3.1% / 1.4% / robust 3.3% | OK | Q + A |
| 85 | method[1] | 74,498 papers | OK | R |
| 86 | method[1] | title 2×, keywords 2×, 1–2 gram, SVD 300, KMeans 300 | OK | scripts/cluster_topics.py |
| 87 | method[0] | official 19,525 | UNVERIFIABLE | external |
| 88 | method[0] | "6万" were abstract registrations | UNVERIFIABLE | external |
| 89 | method[2] | 60 batches of ~173 | OK | 10,381/60 = 173.0; 60 batch files |
| 90 | method[2] | candidate pool = all safety-area papers + lexicon hits | OK | R: in_area 1,696 / 3,271 equals all area papers in corpus |
| 91 | method[4] | 2027 median abstract ~9% longer | OK | R: 182→198 words (+8.8%) |
| 92 | method[0] | snapshot 2026-10-07 | UNVERIFIABLE | not in data |
