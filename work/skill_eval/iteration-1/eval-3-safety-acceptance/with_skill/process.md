# Process log

## Steps
1. Read `skills/iclr-submissions/SKILL.md`, then `references/data.md`, `references/reading.md`, the first part of `references/example-agent-environments.md`, `safety/TAXONOMY.md`, and peeked at `aggregates/safety.json` (it already has per-subfield `acc26`, `rating26`, counts and per-10k — I used it only as a cross-check; my numbers match it exactly).
2. Made the question measurable:
   - population: 2026–27 papers with safety `relevance >= 1`; unit = paper; grouping = main `subfield` (variant: subfield or subfield_2; variant: relevance == 2).
   - attribute: 2026 acceptance (`accepted`), two denominators (all submissions; accept+reject only), mean rating; 2027 heat = per-10k-submissions ratio 2027/2026, plus `--exclude-formulaic` rerun.
   - comparison: Spearman across 26 subfields of 2026 acceptance/rating vs heat ratio; quadrant classification; composition-implied acceptance.
3. Commands (from dataset root):
   - `python3 skills/iclr-submissions/scripts/iclr.py select --years 2026 2027 --relevance 1 --out work/safety_rel1.parquet` (2026: 2,975; 2027: 5,974)
   - same with `--exclude-formulaic` → `work/safety_rel1_nofs.parquet` (2027: 3,228 of 24,794 non-formulaic submissions)
   - `work/analyze.py` → `analyze_out.txt`, `subfield_main.csv`, `subfield_any.csv`, `area_adjusted.csv`
   - `work/checks.py` → chi-square heterogeneity, precision skim (12 random titles × 4 subfields), regex recall check, topic-level table → `checks_out.txt`
   - `work/quadrants.py` → quadrant/agreement counts, composition-implied acceptance → `quadrants_out.txt`, `subfield_quadrants.csv`
4. No per-paper reading/subagents: every attribute needed (subfield, status, rating, year) is already a label column, so per the skill's method table I used `tally`-style aggregation (via pandas, since I needed acceptance rates, not just distributions).

## Friction / confusion (candid)
- The helper `tally` only gives distributions per year; there is no built-in "rate of X by group" (acceptance by subfield), so I wrote pandas scripts. A `--rate accepted` option or a `crosstab` subcommand would have saved time.
- The skill doesn't say which acceptance denominator to use. 2026 has 5,097 withdrawn + 905 desk-rejected papers (30% of submissions), which changes rates a lot (27.0% vs 38.8% overall). I reported both; the precomputed `aggregates/safety.json` `acc26` turned out to use all submissions as denominator (undocumented — I inferred it by matching numbers).
- The skill says "2026 acceptance can serve as a signal of what reviewers rewarded" but doesn't caution about causality/timing when relating it to 2027 submission choices; I added that caveat myself.
- Heat baseline: since total safety per-10k falls (0.93×), "heat ratio > 1" vs "share within safety rising" differ slightly; I noted the 0.93× threshold. The skill's guidance ("per-10k for field size") was clear enough.
- `select` with `--exclude-formulaic` nicely also adjusts the per-10k denominators (19,614 / 24,794) — helpful, though I had to hard-code those totals in my script because the population file doesn't carry them.
- Small-n: several subfields have 31–66 papers in 2026, so Wilson CIs are wide; the skill's "small numbers" rule is about ratio denominators < 10, which doesn't directly cover rate uncertainty — I added CIs and a chi-square test.
- `topic` free-text field was too fragmented for topic-level acceptance analysis (only 7 exact topics with ≥8 papers in 2026); mentioned briefly only.
- Regex recall check for "backdoor" matched "front-door" etc.; out-of-population hits were mostly false positives, so recall of labels looks fine.
