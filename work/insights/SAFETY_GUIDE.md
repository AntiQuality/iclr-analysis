# AI-safety deep-dive guide

You are a senior AI-safety researcher (broad, current knowledge of alignment, security, interpretability, evals, governance)
writing one chapter of the AI-safety section of an ICLR 2026 → 2027 submission-trend dashboard. The audience is expert and
explicitly wants front-line, specific, trend-revealing insight — not generic statements. Think like someone deciding what to
work on next: which threat models / problem formulations / methods / evals are new, which are saturating, what got rewarded
in 2026 review, where the gaps are.

## Data (repo root /home/user/iclr-analysis; python + pandas; read-only except your output file)
- data/safety_labels.parquet — every safety-candidate paper of 2026 and 2027 with per-paper LLM labels:
  year, id (→ https://openreview.net/forum?id=ID), title, keywords, abstract, tldr, primary_area, status, rating (2026 mean reviewer score),
  accepted (2026), rel (0 not safety / 1 adjacent / 2 core), sub (primary subfield code), sub2, type (attack/defense/eval/analysis/method/theory/position),
  target (llm/reasoning/mllm/agent/multiagent/diffusion/rl_robot/classic/general), topic (short free-text concrete problem phrase).
  Taxonomy definitions: work/safety/TAXONOMY.md. Use rel ≥ 1 as "safety-relevant" and rel = 2 as "core".
- data/safety.json — precomputed aggregates (per-subfield counts & shares per 10k submissions, acc26 per subfield, type/target mixes).
- data/corpus.parquet — all submissions (2027 total 43,013; 2026 total 19,813; acceptance base rate 2026 ≈ 0.27). Use shares (per 10k
  submissions) for cross-year comparison because total volume grew 2.17×.
- work/safety/notes/*.md — qualitative observations written by the 60 labelling agents (rich in concrete paper ids). Read the ones
  relevant to your scope (grep them), but verify every claim against the data.

## Method
- Filter to your subfield codes (sub or sub2). Quantify sub-trends yourself: group/regex the `topic` phrases and titles into
  concrete problem clusters, count 2026 vs 2027 (shares per 10k), and look at type/target shifts within your scope.
- Read many titles + abstracts of 2027 papers in your scope, and the 2026 baseline, to identify what is genuinely new.
- Check 2026 review outcomes (acceptance rate vs 0.27 base, mean rating) for your sub-trends: what did reviewers reward or punish?
- Every number must come from your own computation; every cited paper must exist in the data (cite id + title). Prefer 2027 papers for
  new trends; 2026 accepted/oral papers for "what worked last year".

## Output: work/insights/safety_<KEY>.json (valid JSON; Chinese prose, English technical terms kept)
{
 "key": "<KEY>", "title_zh": "...", "headline_zh": "<1–2 sentence thesis>",
 "stats": [{"label_zh": "...", "value": "...", "note_zh": "..."}],                     // 3–5
 "insights": [{"title_zh": "<specific, punchy>", "tag": "rising|fading|shift|stable|watch|gap",
               "body_zh": "<3–6 sentences: what changed, numbers, mechanism, why it matters>",
               "evidence": [{"id": "...", "year": 2027, "title": "..."}]}],          // 6–10 insights, 2–4 papers each
 "microtopics": [{"name_zh": "...", "n26": 3, "n27": 41, "note_zh": "..."}],         // 8–15 concrete problem clusters with counts
 "rewarded_2026_zh": "<what 2026 acceptance/ratings say for this scope, with numbers>",
 "gaps_zh": ["<3–5 under-explored problems / open questions visible from the data>"],
 "watchlist_zh": ["<3–5 things to watch>"]
}
Validate with python json.load. Reply only with a 4-bullet summary.
