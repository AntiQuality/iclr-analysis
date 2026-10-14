# Process log

## Steps
1. Read `release/README.md` and `release/safety/TAXONOMY.md` (did not open `release/skills/`). Listed `aggregates/`, `topics/`, `submissions/`, `safety/`.
2. Defined scope from `safety/labels.csv`:
   - main: `subfield == AGENT_SAFE` or `subfield_2 == AGENT_SAFE` → 128 (2026) + 774 (2027) = 902 (820 rel=2, 82 rel=1)
   - plus `subfield == PI` with `target_system in {agent, multiagent}` not already included → 20 + 57 = 77
   - total 979 (148 / 831). Joined to `submissions/iclr{2026,2027}.parquet` on (year, id, title); 0 missing abstracts.
   - saved `work/agent_safety_papers.parquet`.
3. Mined frequent benchmark-like names in abstracts (regex on *Bench/*Arena/*World/*Dojo/...) to seed a vocabulary.
4. Wrote `work/classify_env.py`: regex tagging of title+keywords+tldr+abstract into 20 environment domains (multi-label), 3 instantiation types (real sandbox / LLM-emulated / static trajectory), ~40 named benchmarks, a "builds new env" flag, and a single `primary_env` by a specificity priority order. Outputs `work/env_tags.csv`, `work/env_summary.json`, `work/summary_tables.txt`, `work/primary_env_by_year_{all,agentsafe}.csv`, `work/macro_env_by_year_all.csv`, `work/examples_by_env.txt`.
5. Iterated regexes 4 times after inspecting match contexts (e.g. `defi` matched "define", `vulnerabilit`/`exploit` made "cyber" fire on 46% of 2026 papers, `compliance`/`workspace`/"financial loss"/"natural laboratory" false positives). Added new 2027-specific categories after seeing the text: Agent Skills ecosystem, production harnesses (OpenClaw/Claude Code/Codex/OpenCode/Moltbook), MCP split from generic tool-use, memory/self-evolving.
6. Manual validation: I read two random samples myself (40 papers with seed 1, 50 with seed 7; 90 abstracts total, stratified by year) and judged tags; ~85% of primary-environment assignments acceptable on the second round. Also checked every example paper cited in answer.md against its assigned primary env and swapped out mis-assigned ones.
7. Wrote `answer.md` (Chinese).

## Who read papers
- No subagents were available in this session (no Agent tool), so all reading was done by me: ~90 abstracts read in full (truncated at 650–900 chars), plus ~60 titles/snippets when debugging regexes. The remaining ~890 papers were tagged only by the regex script.

## Commands (representative)
- `python3 -c` with pandas to crosstab labels.csv by subfield/year/target
- `python3 -I work/classify_env.py work/` (rerun after each regex revision)
- small `python3 -I -` heredocs for context snippets, validation samples (`work/validation_sample*.txt`), example lists

## Friction / confusion
- "Environment distribution" is not a field in the dataset; only title/abstract/keywords are available (no full text), so environments used only in experiments sections are invisible → named-benchmark counts are lower bounds; ~9% of abstracts name no environment at all.
- Scope ambiguity: taxonomy defines AGENT_SAFE as "beyond injection", but users usually include agent prompt injection in "agent safety"; many PI-on-agent papers already carry AGENT_SAFE as subfield_2. I reported the union and noted the AGENT_SAFE-only variant.
- Safety labels are LLM-generated, not hand-checked (per README); 2027 is an in-review snapshot; 2027 has 2.17× more submissions so only shares are compared; README notes 42% of 2027 abstracts are flagged formulaic, which may inflate keyword frequencies.
- Keyword regexes are fragile (domain words used as motivation, e.g. "healthcare, finance" listed in intro sentences); primary-env priority ordering is a judgment call (e.g. SafeSearch → web, GhostEI-Bench → embodied are known errors).
- 2026 sample is small (148), so 2026 per-category shares carry roughly ±3–4 pp noise.
