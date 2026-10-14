# Data reference

## Contents
- Paper tables
- Topic clusters
- Safety labels
- Choosing a population
- Known quirks

## Paper tables: `submissions/iclr{year}.parquet`

One row per submission. Join key across files: `(year, id)`.

| column | notes |
|---|---|
| `year` | 2025, 2026, 2027 |
| `id` | OpenReview forum id; link is `https://openreview.net/forum?id=<id>` (also in `openreview_url`) |
| `number` | submission number |
| `title`, `abstract`, `tldr`, `keywords` | as submitted; `keywords` is a list; `tldr` may be empty |
| `primary_area` | author-chosen ICLR area (21 values, e.g. `alignment, fairness, safety, privacy, and societal considerations`, `reinforcement learning`, `datasets and benchmarks`) |
| `status` | 2025–26: `accept_oral`, `accept_spotlight` (2025 only), `accept_poster`, `reject`, `withdrawn`, `desk_rejected`. 2027: `active`, `withdrawn`, `desk_rejected` |
| `rating`, `accepted` | mean reviewer score and decision, 2025–26 only |
| `topic_cluster` | 0–299, fitted jointly on all three years, so the same id means the same topic every year |
| `topic_name_en`, `topic_name_zh`, `theme` | cluster name and one of 17 themes: `agents`, `llm_post` (reasoning/RL/post-training), `llm_core` (architecture/efficiency), `mm` (multimodal understanding), `gen` (generative models), `vision`, `embodied`, `rl` (non-LLM RL), `safety`, `interp`, `theory`, `struct` (graphs/time series/probabilistic/causal), `science`, `eval` (data/benchmarks), `repr` (representation/transfer/continual), `systems`, `apps` |
| `topic_centrality` | higher = more typical of its cluster; sort by it to get representative papers |
| `style_score`, `formulaic_style` | wording-style score; `formulaic_style` marks scores above the 2026 99th percentile (42% of 2027, 1% of 2026) |

Withdrawn and desk-rejected papers are included. Keep them for questions about what people submitted, and drop them (`--active-only`) for questions about what is under review or accepted.

## Topic clusters: `topics/clusters.csv`

Columns: `cluster`, `name_en`, `name_zh`, `theme`, `theme_zh`, `desc_zh`, `trend_zh`, `coherence`, `n_<year>`, `per10k_<year>`, `per10k_excl_formulaic_<year>`, `accept_rate_2026`, `mean_rating_2026`, `example_ids`.

- To find clusters for a subject, grep `name_en` and `desc_zh`, then confirm with `select --cluster <ids>` and `show`.
- `coherence` 1 marks 15 clusters grouped by shared wording rather than subject. Do not base trend claims on them.
- Clusters are coarse (~250 papers each in 2027). A subject often spans several clusters, and a cluster can mix subjects. For a precise population, combine clusters with regex or with reading.

## Safety labels: `safety/labels.csv`

Covers the 10,381 papers from 2026–27 that entered the safety candidate pool, either through a safety-related primary area or through a safety keyword lexicon. Each was labelled from its abstract.

| column | values |
|---|---|
| `relevance` | 2 = safety is the main contribution (6,474); 1 = secondary motivation (2,475); 0 = keyword hit only (1,432) |
| `subfield`, `subfield_2` | main and optional secondary code; see `safety/TAXONOMY.md`. Largest: `INTERP_GEN`, `HALLU`, `PRIVACY`, `WATERMARK`, `ADV_ROBUST`, `ALIGN_TRAIN`, `AGENT_SAFE`, `UNLEARN`, `BACKDOOR`, `FAIR`, `JB_DEF`, `PI`, `OVERSIGHT`, `SAFE_RL`, `JB_ATK`, `OOD`, `REWARD_HACK`, `INTERP_SAFE`, `IP`, `GEN_SAFE`, `SOCIETAL`, `VALUES`, `DANGER_EVAL`, `DECEPTION`, `FT_ROBUST`, `OTHER`; `NONE` when relevance is 0 |
| `contribution_type` | `attack`, `defense`, `eval`, `analysis`, `method`, `theory`, `position` |
| `target_system` | `llm`, `reasoning`, `mllm`, `agent`, `multiagent`, `diffusion`, `rl_robot`, `classic`, `general` |
| `topic` | a few words naming the specific problem; useful for grouping with regex |
| `candidate_by_area`, `candidate_lexicon_hits` | why the paper entered the pool |

Use `relevance >= 1` for "safety-related" and `relevance == 2` for "safety papers". Match codes on `subfield` or `subfield_2` (`select --subfield` does both). `target_system` captures papers on agent systems even when the subfield is something else, for example backdoors in agents.

## Choosing a population: common patterns

| question about | start from |
|---|---|
| a safety subfield (2026–27) | `select --relevance 1 --subfield ...` |
| safety work on a kind of system | `select --relevance 1 --target agent multiagent` |
| a research area in any year | clusters matching the subject (`--cluster`) or `--theme`, refined with `--regex` |
| a named method/model/benchmark | `select --regex '<pattern>'` across all papers |
| acceptance patterns | 2025–26 only; `status` / `accepted` / `rating` |

## Known quirks

- **Volume.** Submissions grew from 11.7k to 19.8k to 43.0k. Always compare shares.
- **2027 snapshot.** Taken on 2026-10-07, after both deadlines and before reviews.
- **2027 wording.** Abstracts shifted toward a formulaic style: hedged claims, "matched/held fixed" phrasing, fewer "novel". Word-frequency trends on 2027 can reflect wording rather than topic, so check them with `--exclude-formulaic`.
- **Abstracts only.** Full texts are not included. Anything not stated in title, keywords, TL;DR or abstract is invisible.
- **Label noise.** Topic and safety labels were produced by language models from abstracts and are suited to aggregate analysis. Verify individual labels before citing a specific paper as an example of a category.
