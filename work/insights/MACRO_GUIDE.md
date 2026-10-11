# Domain deep-dive guide (macro analysts)

You are a senior ML researcher writing one domain chapter of an ICLR 2026 → 2027 submission-trend dashboard for a demanding,
expert audience. They explicitly do NOT want generic statements ("X continues to grow"). They want front-line, specific,
evidence-backed insight: which concrete methods / problem formulations / benchmarks / model families rose or fell, what replaced what,
what the new "default recipe" looks like, what got rewarded last year, and what to watch.

## Data (repo root /home/user/iclr-analysis; use python + pandas; read-only)
- data/corpus.parquet — all submissions: year (2025/2026/2027), id (OpenReview forum id → https://openreview.net/forum?id=ID),
  title, abstract, tldr, keywords (list), primary_area, status, rating (mean reviewer score; 2025/2026 only), accepted (bool; 2025/2026 only).
  2027 = snapshot of all submissions on 2026-10-07 (no reviews yet). Totals: 2025 11,672 · 2026 19,813 · 2027 43,013.
  ALWAYS compare shares (per 10k submissions or %), never raw counts alone, because volume grew 2.17x.
- data/clusters.parquet — (year,id,cluster) for a 300-cluster TF-IDF/KMeans topic map.
- data/macro.json — clusters[] with name_zh/name_en/theme/desc_zh/trend_zh/coherence/example_ids, n & share per year (share is per 10k),
  acc26 (2026 acceptance rate in cluster; base rate acc_base26 ≈ 0.27), rating26; themes[]; kw_rise/kw_fall/kw_new (author-keyword log-odds 2026→2027);
  models[] and benchmarks[] mention shares.
- data/concepts.json — regex concept tracker: share (% of papers, full text) and share_tk (title+keywords only) per year, acc26.
- work/insights/style_anomaly.md (may appear while you work) — notes that some 2027 clusters are held together by formulaic wording
  (clusters with coherence 1 such as 137, 15, 83, 220, 13, 100, 3 are artefacts) — do not report such clusters as research trends;
  if relevant to your domain, mention the caveat in one line.

## Method expectations
- Start from the clusters whose theme is in your scope, then go deeper: read titles/abstracts of 2027 vs 2026 papers in the
  clusters and keyword groups that moved, run your own regex/keyword counts to quantify sub-trends (report shares), and check
  2026 acceptance rates/ratings for the sub-trends (what reviewers rewarded).
- Every quantitative claim must come from your own computation on these files. Every cited paper must exist (check id in corpus).
  Prefer 2027 papers as evidence for new trends and 2026 papers for "last year's" baseline; for 2026 you may highlight accepted/oral ones.
- Be specific: name methods (e.g. "GRPO → on-policy distillation"), benchmarks (e.g. LIBERO, SWE-bench Verified), model families (Qwen3, …).

## Output: work/insights/macro_<KEY>.json (valid JSON, Chinese prose, English technical terms kept)
{
 "key": "<KEY>", "title_zh": "<chapter title>", "headline_zh": "<1–2 sentence thesis of the chapter>",
 "stats": [{"label_zh": "...", "value": "e.g. 0.5 → 108 /万篇", "note_zh": "..."}],              // 3–5 key numbers
 "insights": [{"title_zh": "<punchy, specific>", "tag": "rising|fading|shift|stable|watch",
               "body_zh": "<3–5 sentences, with numbers, mechanisms, what replaced what>",
               "evidence": [{"id": "...", "year": 2027, "title": "..."}]}],                   // 6–9 insights, 2–4 papers each
 "rising": [{"name_zh": "...", "from": 1.0, "to": 47.4, "unit": "per10k", "note_zh": "..."}],   // 6–10 items
 "fading": [{"name_zh": "...", "from": 89.8, "to": 24.9, "unit": "per10k", "note_zh": "..."}],  // 4–8 items
 "rewarded_2026_zh": "<what 2026 acceptance/rating data says about this domain, with numbers>",
 "frontline_zh": ["<6–10 concrete micro-observations: specific new recipes, benchmark names, model names, problem formulations>"],
 "watchlist_zh": ["<3–5 forward-looking things to watch, each one line>"]
}
Validate with python json.load. Reply only with a 4-bullet summary.
