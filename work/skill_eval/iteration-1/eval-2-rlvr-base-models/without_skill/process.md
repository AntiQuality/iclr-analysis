# Process log

All work was done by a single agent (me). No subagents were used. The repo was read-only, and I did not open `skills/`.

## Steps
1. Read `README.md`. Listed `submissions/`, `topics/`, `aggregates/`, `safety/`. Inspected the parquet schema and `topics/clusters.csv`.
2. Checked the topic clusters for RL with LLMs. RLVR is split across several clusters, including 47, 148 and 213 ("RLVR for LLM reasoning" ×3), 258 (GRPO variants), 97, 111, 124, 128 and 218. Because of that split, I chose a **keyword definition** instead of cluster membership.
3. `work/select.py` flags each paper on title + keywords + abstract:
   - `strong`: explicit RLVR / GRPO / DAPO / GSPO / verifiable reward / R1-Zero / zero-RL terms.
   - `broad`: any RL term + any LLM term, excluding RLHF/preference.

   Output: `work/all.pkl`, `work/rl_llm.pkl`. The 2025 `strong` set has only 2 papers, so the analysis is 2026 vs 2027.
4. `work/models.py`: a regex extractor over about 25 model families, applied in order with masking:
   - R1-Distill is matched first so that `DeepSeek-R1-Distill-Qwen` is not also counted as Qwen.
   - It also tags Qwen generation and variant, Llama version, and parameter sizes.
   - `core` = strong ∩ LLM context. That gives 713 papers in 2026 and 1,451 in 2027.
5. `work/table.py` produces `work/tables.md`. Denominator = papers naming ≥1 open family, under 4 variants: main core, excluding withdrawn/desk-rejected, excluding formulaic_style, and the broad set. Each variant has a two-proportion z-test.
6. `work/table2.py` produces `work/tables_variantB.md`, the version used in the answer. Its denominator excludes DeepSeek-R1/V3/V4 and closed models from "base candidates", because they are mostly cited as motivation, teacher or judge.
7. Manual validation. `work/validation_contexts.txt` holds the sentences around each model mention for about 70 sampled papers: Qwen, Llama and DeepSeek in each year, plus OLMo and Gemma in 2027. I read all of them myself. Findings:
   - Qwen and Llama mentions are mostly the policy actually being trained.
   - 2026 DeepSeek mentions are mostly "inspired by DeepSeek-R1" or "GRPO introduced by DeepSeek".
   - The sample showed that Qwen-Image (a text-to-image model) was being counted as Qwen. I excluded it: 1 paper in 2026 and 5 in 2027.
8. `work/context_all.py` produces `work/context_all.md`. It runs the same extractor on all other 2026/2027 papers, to separate the RLVR-specific shift from the general rise of Qwen. Qwen went from 47% to 70% and Llama from 44% to 22% in non-RLVR papers.

## Friction / data issues
- **The `tldr` field is asymmetric.** It is empty for every 2025 and 2026 paper and filled for 56% of 2027 papers. My first pass included tldr, which inflated 2027. I re-ran everything without it. The README does not mention this.
- **2027 abstracts are longer and name models more often.** They average 1,517 characters against 1,395 in 2026. Qwen mentions across all papers went from 3.7% to 8.7%. Raw "% of all papers" therefore inflates every family, so I normalized by papers that name a model.
- **2026 includes withdrawn papers** (205 of 764 strong). The robustness run without them gives the same conclusions.
- **Regex false positives fixed:** `seed-0` and `seed-42` (random seeds matched as the Seed model), `LlamaPointInPart`, and `HunyuanVideo`. `o1`/`o3` matches for closed models may still contain a little noise, but closed models are not in the main conclusions.
- **Version names are taken as they appear in the data and not verified externally:** Qwen3.5/3.6/3.8, Gemma-4, GLM-5.x, DeepSeek-V4, GPT-5.x/6.
- `pandas.to_markdown` needs `tabulate`, which is not installed. I used `to_string` instead.
- Abstract-only data is a hard limit. Only 28% (2026) and 41% (2027) of core RLVR abstracts name any open model.

## Commands (key)
Run in `outputs/work/`, in this order:
1. `python3 -I select.py`
2. `python3 -I models.py`
3. `python3 -I table.py`
4. `python3 -I table2.py`
5. `python3 -I context_all.py`
