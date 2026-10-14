# Process log: world models 2025→2027

## Steps
1. Read SKILL.md, references/data.md, references/reading.md, references/example-agent-environments.md, and `iclr.py -h` plus the subcommand helps.
2. Searched `topics/clusters.csv` for world-model clusters. Found 8 (interactive video WMs), 30 (world action models), 161 (latent WMs for planning), 228 (JEPA latent WMs), and related ones (76 driving, 73, 112, 235...).
3. Population, first pass: `select --regex 'world[- ]?models?'` gave 119 / 229 / 1567. Checked recall against WM clusters: 228 cluster papers in 2027 did not match, mostly **"World Action Model / WAM"** papers. Of the 343 papers that say "world action model", 223 never say "world model".
   - Final regex, in custom script `work/scripts/build_pop.py`: `world[- ]?model | world[- –]?action model | world simulat*`, excluding matches only preceded by "real-/open-". Result: 120 / 229 / 1801.
   - Did not add cluster-only papers: a sample showed generic JEPA SSL and generic video generation.
   - Did not add a bare `\bWAM\b`: in 2025 it matched an unrelated paper.
4. Robustness variants of total growth, in `work/growth_variants.csv`: core (title/keyword), excluding formulaic, active-only, ≥2 mentions. Every variant gives 3.5–4.1× (2027 vs 2026).
5. Cluster decomposition of the per-10k growth (`work/cluster_decomposition.csv`): clusters 30 / 161 / 228 / 8 give about 62% of the 2026→27 increase.
6. Lexicon pass (`work/wm_lexicon.json`, `count` on the full population, with and without `--exclude-formulaic`): coverage 85–88%. Converted to per-10k in `work/lexicon_per10k.csv`.
7. Reading. No Agent/subagent tool was available in this session (only remote-session tools that would not see the local files), so I read everything myself, as the skill prescribes for that case:
   - `batch --sample-per-year 200 --seed 7`: all of 2025 (120), 200 from 2026, 200 from 2027, in 13 batches of 40.
   - Codebook in `work/codebook.json`: domain (9 values), role (7), representation (6), evidence.
   - I read all 520 abstracts, truncated at 950 chars by my viewer script `work/scripts/view.py`, and wrote compact label files `work/lab/*.txt`. A converter turned them into JSONL in `work/out/`.
   - `merge`: 520/520, 0 invalid, 0 missing.
8. Composite "direction" rules (`work/scripts/directions.py`) produced the per-10k estimates with 95% CI (finite-population corrected) for all papers and for non-formulaic papers (`work/tally_*.csv`).
9. Spot check: re-examined 20 random labels (ids in `work/spotcheck_ids.csv`). About 2–3 are borderline, e.g. real-robot offline MBRL labelled rl_benchmarks rather than robot, and EVOKE labelled mention_only rather than an LLM-WM method. Within the skill's tolerance.
10. Context: 2025 and 2026 acceptance for the WM population vs all papers. Representative papers via `show` (`work/representative_papers.txt`).

## Papers read and by whom
All 520 sampled abstracts (2025: 120 of 120; 2026: 200 of 229; 2027: 200 of 1801) were read and labelled by me, the main agent. No subagents were used.

## Friction / confusion with the skill or data (candid)
- **Subagents unavailable.** Reading 520 abstracts alone took most of the session's effort. The skill's "without subagents" fallback says to read all of the smaller year and sample the larger, but `--sample-per-year` applies one N to every year. I used 200, which kept all of 2025 and sampled 2026 at 200/229. That worked here, but per-year N values would help.
- **The WAM recall trap is big and not mentioned anywhere.** A naive `world model` regex misses about 12% of 2027 WM papers, and they are exactly the fastest-growing direction. The skill's recall check (regex vs clusters) caught it, which is good. A note in data.md, or a ready-made world-model lexicon, would save time.
- **"Real-world model" false positives.** `world[- ]?model` matches "real-world model(s)". There are only about 24 cases, but newcomers will not think of it.
- **Stale help text.** `select --regex` says it searches "title+keywords+tldr+abstract", but TL;DR is excluded by default. I verified in the code (`WITH_TLDR=False`) that it is excluded. The help string should be fixed.
- **`count` has no per-10k output.** It reports shares within the population only. For "which direction is cooling", within-population share and field share (per 10k) disagree sharply: almost everything grows in absolute terms. I had to write my own per-10k conversion. A `--per10k` flag on `count` and `tally` would help, plus a note that "cooling" should be stated in field-share terms.
- **Estimating per-10k from a sampled reading** (sample share × population per10k, with an FPC interval) is not covered by the skill. I wrote it myself.
- **No guidance on composing mutually exclusive "directions"** from several label fields. I used ordered rules, and they are somewhat arbitrary, e.g. where a driving WAM goes. Domain-only and role-only tallies are reported too, so readers can check.
- **The `batch` viewer output was too large for one tool call** (40 abstracts ≈ 50KB). I had to split into halves, and once the output spilled to a file. A `--abstract-chars` default near 900 for self-reading would help.
- **Formulaic-style effect on labels.** The "benchmark/analysis" role share rises in 2027 only because of formulaic papers (17% overall vs 10% non-formulaic). The skill's warning was useful here.
- The skill's acceptance-rate guidance (two denominators) was clear and easy to apply.
