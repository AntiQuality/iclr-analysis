# Process log

## Steps
1. Read SKILL.md, references/data.md, references/reading.md, references/example-agent-environments.md (the worked example is literally this question, so I followed it closely), and lexicons/agent_environments.json.
2. Population (helper `iclr.py`, run from dataset root):
   - `select --years 2026 2027 --relevance 1 --subfield AGENT_SAFE PI` -> 177 / 891 (matches the worked example exactly).
   - Variant `--target agent multiagent` -> 186 / 982; 42 / 171 of those are outside the subfield population (OVERSIGHT, HALLU, REWARD_HACK...). Not separately labelled; reported via the agent-target subset of the sample instead.
   - `--exclude-formulaic` population -> 176 / 406 (saved).
   - Precision: `show -n 20`; a few PI papers are non-agent (MRAG-Corrupter, MLLM adversarial examples) -> handled with `chat_only`.
   - Recall: regex `\bagent` + safety words across 2026-27 -> 2,349 hits, 1,460 outside population; mostly unlabelled reliability/RL papers (regex too noisy), plus labelled papers in SAFE_RL/OVERSIGHT/DANGER_EVAL. Kept the skill's definition.
3. Lexicon pilot: `count --lexicon agent_environments.json` -> coverage 58.2% / 62.2%, dominated by generic terms; identical to the worked example. Used for named-benchmark table on full population.
4. Codebook = the example's 11 categories + free `env_named` + `evidence` (work/codebook.json). Rulings used: AgentDojo -> tool_api; CTF/vuln-repo/cyber ranges -> coding_terminal; LLM-vs-LLM games/social sims -> multi_agent; grid-world/game control -> embodied; non-agent PI/IH work -> chat_only; "benchmarks unnamed" -> none_stated.
5. Reading: `batch --size 40 --sample-per-year 200 --seed 0` -> 377 papers (all 177 of 2026 + 200 of 891 in 2027), 10 batch files. **No subagent tool was available in this environment** (no Agent/Task tool), so per the skill I read all 10 batches myself sequentially and wrote out/batch_00*.jsonl. 377 papers read, all by me (single reader).
6. `merge` -> 0 invalid, 0 duplicates. `tally` on env_category and env_named. Robustness: formulaic vs non-formulaic split of the 2027 sample; agent-target subset; 95% CI with FPC.
7. Spot check: instead of a second reader, cross-checked my labels against lexicon hits per category (web: 0 lexicon-only; os/coding/embodied: 7 lexicon-only cases, all mentions that are not the experimental environment). Fixed one label of my own (SafeShopBench web -> tool_api only).

## Friction / confusion (candid)
- **No subagents.** The skill assumes an Agent tool; without one, reading 1,068 abstracts (~460k tokens) solo was too much, so I fell back to a per-year sample (which the skill permits). I picked 200 for 2027 because the skill's example flag uses 200; the skill gives no guidance on how to choose n when one year is fully read and the other sampled.
- **`merge` vs. sampling.** `batch --sample-per-year` does not write the sampled population, and `merge --population pop.parquet` then reports 691 "missing" papers (the unsampled ones) and suggests re-batching them, which is wrong advice in the sampled case. I had to rebuild a sample population from batch ids by hand. Suggest: `batch` writes `sample_population.parquet` (or ids in manifest.json), and `merge`/docs mention it.
- `manifest.json` lists only file names, not ids or seed/sample sizes.
- `count` `--out` CSV has only a `matched` string column (term names joined), no category columns, so category-level cross-checks need regex on term names.
- `tally` output has no CI option for sampled years; I computed CIs manually. A `--population-size` / `--ci` flag would help.
- Formulaic check: the skill says rerun selection with `--exclude-formulaic`, but for a read-labelled sample the useful check is splitting labels by `formulaic_style`, which needs a manual join (labels.parquet does not carry population columns). It did matter here: the 2027 tool_api share is 46.9% in formulaic vs 28.4% in non-formulaic abstracts.
- The worked example matches the question almost exactly, which made the task easy to structure but also makes it tempting to reuse its numbers; I re-ran everything.
- Large batch text (~70KB/40 papers) exceeds the single Read limit (~25k tokens) so each batch needed 2 reads.
- Category boundary ambiguities: tool_api vs email_office (AgentDojo includes email), coding_terminal for cyber/CTF ranges, multi_agent vs "agent societies" with no tools, and chat_only for PI-defense papers that only cite "agentic benchmarks" generically.

## Files
- work/agent_safety.parquet (pop), agent_target.parquet, agent_safety_nf.parquet, pop_sample.parquet
- work/codebook.json, work/batches/, work/out/ (labels per batch), work/labels.parquet
- work/tally_env_category.txt, work/tally_env_named.txt, work/lexicon_pilot_full_population.txt, work/env_matches.csv
