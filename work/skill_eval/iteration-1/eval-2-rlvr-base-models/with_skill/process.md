# Process log: RLVR/GRPO base models, ICLR 2026 vs 2027

## Steps
1. Read SKILL.md, references/data.md, references/reading.md, references/example-agent-environments.md, and `iclr.py -h` (all subcommands).
2. Made the question measurable:
   - population: 2026–27 LLM RL post-training (RLVR/GRPO family)
   - unit: paper
   - attribute: open-weight model families and versions named in title/keywords/TL;DR/abstract
   - comparison: share of papers naming at least one open model, plus share of the whole population
3. Searched topics/clusters.csv for RL and post-training clusters. Relevant ones: 47, 213 and 148 (RLVR), 258 (GRPO variants), 111, 28, 128 (agentic RL), 218 (multimodal RL), 97 (SFT→RL).
4. Built the population as a union of two selections:
   - `select --years 2026 2027 --regex '\bRLVR\b|verifiable rewards?|\bGRPO\b|group relative policy|\bDAPO\b|\bGSPO\b|\bRLOO\b|\bR1-Zero\b|\bRL-?Zero\b'` (748 / 1755)
   - `select --cluster 47 213 148 258 111 28 128 218 97 --regex 'reinforcement learning|\bRL\b|policy optimization|...|reward'` (635 / 1333)
   - Dropped papers in the gen, vision, embodied and rl themes that never mention LLM/VLM/language model (20 / 74 papers, mostly diffusion Flow-GRPO).
   - Final: 970 (2026) and 2,172 (2027). 2025 has 0 papers matching the RLVR regex.
5. Precision check: 40 random titles, about 85% on topic. Recall check: looked at wide-cluster papers outside the regex set and added the cluster-based arm.
6. Discovered vocabulary by mining tokens before "xB" sizes. Found Qwen3.5, Qwen3.6, Qwen3.8, Gemma-4, OLMo-3, GPT-OSS, DeepSeek-V4, Kimi-K2.6/K3 and GLM-5.x. Some of these postdate my training, so the lexicon was built from the data.
7. Wrote lexicons work/lex_family.json and work/lex_version.json. Ran `count` and `analyze.py` (custom script for share-among-named, Qwen generation, size buckets, MoE, `--exclude-formulaic`-equivalent split, and 2026-accepted vs 2027-active split).
8. Lexicon fixes after inspection:
   - excluded Qwen-Image and Qwen-Max/Plus
   - "Gemma 4B" was false-matching Gemma-4
   - allowed MedGemma
   - added Qwen3.7/3.8 and DeepSeek-V4
9. Role check, done by me (no subagents): read match contexts for about 50 random matched papers (work/precision_sample.txt) and about 150 contexts for the non-Qwen families (work/role_contexts.txt). For Qwen, Llama, OLMo and Gemma, about 90% of matches are the trained or analysed model. Kimi, GLM and DeepSeek-V4 are mostly frontier comparisons. Closed models (GPT, o-series, Claude, Gemini) are comparisons or judges.
10. Picked representative papers with `show` and verified the model claims in their abstracts.

## Files (work/)
- pop*.parquet: populations
- lex_*.json: lexicons
- count_*.txt, fam_matches.csv, ver_matches.csv: `count` outputs
- flags.parquet: per-paper flags
- analyze.py, analysis_out.txt, table_*.csv: analysis script and results
- precision_sample.txt, role_contexts.txt: reading evidence

## Friction / candid notes
- **No Agent/subagent tool was available.** I did not run the batch→subagent→merge pipeline. The skill's method table says named things should use lexicon counts, so I treated family names that way. I replaced full reading with targeted context reading to classify the role of each mentioned model (trained base vs comparison). There is therefore no codebook, merge or tally, and the "trained base vs mention" distinction is estimated, not labelled per paper.
- **The skill says coverage well below 80% needs reading.** Coverage here is about 30–35%. For model names that rule fits poorly: reading cannot recover a family name the abstract does not state. About 290 unmatched abstracts give only a size ("a 7B model"). I report "named in abstract" and use papers naming a model as the denominator.
- **The `count` tool reports share of the whole population only.** The key fair-comparison measure here was share among papers that name a model, because the 2027 formulaic style raises the naming rate from 21.6% to 33.5% (26.0% excluding formulaic). I had to write my own script for it. A `--denominator` option or "share among matched" column in `count` would help.
- **`count` has no `--exclude-formulaic` option.** I did the robustness split in my own script.
- **No population label exists for "RLVR / LLM-RL".** There are about 9 relevant clusters, and two are both named "RLVR for LLM reasoning" (47, 213), plus cluster 148 "RL for LLM reasoning (RLVR)". This is confusing, so I used a union of regex and clusters. The skill's guidance on combining clusters with regex was adequate.
- **Minor tool quirk.** pandas warns about regex capture groups in lexicons (harmless).
- **Model versions that look "future" relative to my knowledge** (Qwen3.6/3.8, Gemma-4, Kimi-K3, GLM-5.3, GPT-5.5/6) are taken as given from the data.
