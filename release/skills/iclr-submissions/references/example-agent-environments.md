# Worked example: environments in agent-safety papers, 2026 vs 2027

> "I want to know the distribution of environments used by agent-safety work in ICLR 2026 and 2027."

## 1. Make it measurable

- **Population.** 2026–27 papers labelled safety-related (`relevance >= 1`) whose main or secondary subfield is `AGENT_SAFE` or `PI` (prompt injection, which is about agents almost by definition). Agents studied under other subfields, such as backdoors or jailbreaks of agents, are a variant: add `--target agent multiagent` and report both if they differ.
- **Unit.** A paper. A paper can use several environments.
- **Attribute.** "Environment" covers two things: the kind of setting the agent acts in (web, OS, code, tools/APIs, MCP or skills, email/office, multi-agent, embodied) and the named benchmark or simulator (AgentDojo, OSWorld...). Record both: a category list for the distribution and a list of names for the long tail.
- **Comparison.** Share of population per year. Counts rise anyway, because the population grows fivefold.

## 2. Population

```bash
S=skills/iclr-submissions/scripts/iclr.py
python3 $S select --years 2026 2027 --relevance 1 --subfield AGENT_SAFE PI --out work/agent_safety.parquet
#   2026: 177 papers (89 per 10k)   2027: 891 papers (207 per 10k)
python3 $S select --years 2026 2027 --relevance 1 --target agent multiagent --out work/agent_target.parquet
#   2026: 186   2027: 982   (overlaps heavily; differs by agent papers in other subfields)
python3 $S show --population work/agent_safety.parquet -n 15
```

## 3. Lexicon pilot

```bash
python3 $S count --population work/agent_safety.parquet --lexicon skills/iclr-submissions/lexicons/agent_environments.json \
    --out work/env_matches.csv --unmatched work/env_unmatched.parquet
```

Pilot result (abridged):

```
[tool_api_mcp]        35 (19.8%)  289 (32.4%)
[multi_agent_social]  41 (23.2%)  132 (14.8%)
[coding_terminal]      9 (5.1%)    77 (8.6%)
AgentDojo             10 (5.6%)    64 (7.2%)
Agent Skills           0 (0.0%)    42 (4.7%)
ANY TERM (coverage)  103 (58.2%)  554 (62.2%)
```

Coverage is about 60%, and much of it comes from generic phrases such as "tool-use agent". A named benchmark appears in only about 15% of abstracts. The lexicon alone cannot give the distribution. It is still useful, because it shows the vocabulary (AgentDojo, MCP, Agent Skills, SWE-bench, Claude Code...) for the codebook.

## 4. Read every paper

1,068 papers is small enough to read in full: `batch --size 40` gives 27 files, so 6–7 subagents with 4 files each. Codebook:

| category | definition |
|---|---|
| `web` | browsing or web-navigation agents, web pages as the medium |
| `os_desktop_mobile` | GUI or computer-use agents on desktop, OS or phone |
| `coding_terminal` | coding agents, repositories, shells, CLIs |
| `tool_api` | function-calling or tool-use over APIs; tool-use suites (AgentDojo, InjecAgent, τ-bench, ToolEmu, ASB) |
| `mcp_skills` | Model Context Protocol servers, agent skills, plugin or skill registries |
| `email_office` | email, calendar, documents or enterprise workflows as the main setting |
| `memory_rag` | the attack or defense surface is the agent's memory or retrieval store |
| `multi_agent` | several interacting LLM agents |
| `embodied` | robots, driving, simulated physical worlds, games |
| `chat_only` | the "agent" is evaluated only as a chat model, with no tools or environment |
| `none_stated` | the abstract does not say |

Rulings:
- **AgentDojo** → `tool_api`, even though its tasks include email and banking.
- **Benchmark papers** → the environments the benchmark contains.
- **Only "real-world agents" stated** → `none_stated`, plus a note in `evidence`.

Then `merge`, repair, and `tally` both fields.

## 5. Robustness and report

- Rerun the population with `--exclude-formulaic` and recompute the 2027 shares from the merged labels on that subset. Report the result if it changes a conclusion.
- Report the category table with n and % for each year, the top named environments in each year, and which named environments are new in 2027.
- Add the share of `none_stated`. It is itself a finding: many agent-safety abstracts never say where the agent runs.
- Give representative papers per rising category, with links.
- State the caveat: these are environments named in abstracts, which undercounts environments used in experiments.
