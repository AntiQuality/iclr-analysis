# Process log

## Steps
1. Read `release/README.md` and `safety/TAXONOMY.md`. Did not open `skills/`.
2. Inspected `aggregates/safety.json`. It already has per-subfield `n` (2026 and 2027), `share` per 10k and `acc26`/`rating26`, with relevance ≥ 1 and the primary subfield. I used this as a cross-check, not as the source.
3. Checked the join `labels.csv` ⨝ `iclr{2026,2027}.parquet` on `(year, id)`: 3,510/3,510 and 6,871/6,871 matched, titles identical, no duplicate ids.
4. `work/analyze.py` (run as `python3 -I work/analyze.py <release> <work>`) computes per subfield:
   - 2026 acceptance rate with all submissions as the denominator, a Wilson CI, a binomial test against the ICLR-wide rate (27.0%), the rate among reviewed papers only (excluding withdrawn and desk-rejected), the withdrawal rate and the mean rating;
   - 2027 vs 2026 share per 10k submissions (`share_ratio`), the same share among non-formulaic papers only (`robust_ratio`), and the share within safety;
   - Spearman correlations between the reviewer-preference metrics and the author-flow ratios;
   - context tables by contribution_type and target_system.
   It runs everything for relevance ≥ 1 (main) and relevance = 2 (robustness). Outputs: `work/subfield_table.csv`, `work/summary.json`, `work/*_table.csv`, `work/top_topics.csv` and `work/analyze_output.txt`.
5. Sensitivity checks (inline script, output in `work/sensitivity_output.txt`): multi-label counting with subfield OR subfield_2, Bonferroni threshold, Mann-Whitney test of each subfield's ratings against all of ICLR 2026, stability of the candidate pool across years, and the top free-text topics in the rising subfields.
6. My acc26 numbers reproduce `aggregates/safety.json` exactly, e.g. FT_ROBUST 0.545 and BACKDOOR 0.130.

## Friction / confusion
- **What counts as "AI safety".** relevance 1 and 2 give different sets. The dashboard uses ≥ 1, which pulls in INTERP_GEN and OOD (by rule always rel = 1) and many generic ALIGN_TRAIN papers. I reported ≥ 1 as the main view and = 2 as the check. The extremes are stable; DANGER_EVAL rises to #2 under rel = 2.
- **Acceptance denominator.** About 25% of 2026 safety papers were withdrawn (2026 has no accept_spotlight status; only oral and poster). I used all submissions, as the dashboard does, and also gave the reviewed-only rate. The ranking barely changes.
- **2027 has no decisions**, so "热度" can only be submission share. The raw count ratio is misleading because of the 2.17× total growth.
- **Formulaic style.** 42% of 2027 abstracts are flagged. Excluding them roughly halves the apparent growth of INTERP_GEN and OVERSIGHT, while AGENT_SAFE, PI and SAFE_RL stay strongly up. I reported both.
- **Free-text `topic` is sparse.** Few topics have more than 5 papers, so I only used it for illustration (e.g. "sycophancy in LLMs" 2 → 20).
- **Small n.** Many subfields have 30–70 papers in 2026. Only FT_ROBUST (high) and BACKDOOR (low) survive Bonferroni.
