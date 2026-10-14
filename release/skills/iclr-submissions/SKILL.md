---
name: iclr-submissions
description: Answer questions about ICLR 2025, 2026 and 2027 submissions from the bundled dataset (74k papers with abstracts, 300 topic clusters, 10k AI-safety labels). Use it for any question that needs evidence from ICLR papers, such as trends between years, how many papers do X, what methods, benchmarks, environments, models or threat models papers use, which subfields grew, acceptance patterns, or finding representative papers. The skill shows how to turn a vague question into a measurable one, count with scripts, hand per-paper reading to subagents when keywords are not enough, and report shares with links and caveats. Use it even when the question only says "ICLR papers", "this year's submissions" or names a subfield (agent safety, RLVR, world models...) without naming the dataset.
---

# Answering questions with the ICLR submissions dataset

The dataset holds every ICLR 2025, 2026 and 2027 submission with title, keywords, TL;DR, abstract, primary area, status, a topic cluster label and, for 2026–2027 safety candidates, a paper-level safety label. Most questions need more than reading the labels. You decide which papers count, measure an attribute that is often only implied in an abstract, and compare years fairly. This skill covers how to do that reliably.

Paths below are relative to the dataset root, the folder that contains `submissions/`. The helper is `skills/iclr-submissions/scripts/iclr.py`; run it with `-h` for options. It needs `pandas` and `pyarrow`.

## Data at a glance

| file | rows | use it for |
|---|---|---|
| `submissions/iclr{2025,2026,2027}.parquet` | 11,672 / 19,813 / 43,013 | text search, topic cluster (`topic_cluster`, `topic_name_en`, `theme`), status, 2025–26 decisions and ratings |
| `topics/clusters.csv` | 300 | find clusters for a subject, and their per-year shares |
| `safety/labels.csv` | 10,381 (2026–27) | AI-safety populations: `relevance`, `subfield`, `subfield_2`, `contribution_type`, `target_system`, `topic` |
| `safety/TAXONOMY.md` | | definitions of the 26 safety subfield codes |
| `aggregates/*.json` | | precomputed statistics behind the dashboard |

Column details, value lists and known quirks are in `references/data.md`. Read it before the first query in a session.

## Workflow

### 1. Make the question measurable

Write down four things before touching data:
- **population**: which papers count (e.g. "2026–27 papers whose main or secondary safety subfield is agent safety or prompt injection, relevance ≥ 1");
- **unit**: papers, not mentions; a paper may fall into several values;
- **attribute**: what you record per paper, and its categories;
- **comparison**: usually 2026 vs 2027 as shares, sometimes 2025 too.

If the question is ambiguous (e.g. "environment" could mean benchmark, deployment setting or simulator), choose the reading that best serves the asker, state it, and if it is cheap, report the other reading in one line.

### 2. Build the population and check it

```bash
python3 skills/iclr-submissions/scripts/iclr.py select --years 2026 2027 --relevance 1 --subfield AGENT_SAFE PI --out work/pop.parquet
python3 skills/iclr-submissions/scripts/iclr.py show --population work/pop.parquet -n 15
```

Prefer existing labels (safety labels, clusters, themes) over ad-hoc regex. Labels were assigned by reading each abstract, so they have far better recall than keywords. Use `--regex` to narrow a labelled set or for subjects with no label. Then check the set from both sides:
- **precision**: skim 15–20 random titles. Are they on topic?
- **recall**: run a regex for the subject across *all* papers, then look at what falls outside your population. Which clusters or subfields hold the misses?

Adjust and say what you chose. Safety labels cover only 2026 and 2027. For 2025, or for subjects outside safety, use clusters (`topics/clusters.csv`, `--cluster`), themes or regex.

### 3. Pick the measurement method

| the attribute is... | method |
|---|---|
| a named thing with a stable spelling (model, benchmark, library, method name) | lexicon count: `count --lexicon file.json` |
| a judgment or described in varied words (environment type, threat model, evaluation setup, data source, claimed contribution) | read each paper: `batch` → subagents → `merge` → `tally` |
| already a label column | `tally` on the population file |

Run a lexicon pass first even when you plan to read: it costs seconds, shows the vocabulary, and gives you categories for the codebook. Look at the `ANY TERM (coverage)` line.
- **Coverage well below ~80%.** The unmatched papers are unknown, not "none". They need reading.
- **Generic terms dominate.** Patterns like "tool-use agent" or "web agent" say little about the attribute; treat their hits as unresolved too.
- **Scale.** Read all papers when the population is up to roughly 1,500. Above that, read a per-year random sample (`batch --sample-per-year 200`) and report the sample size.

### 4. Read with subagents (when needed)

Follow `references/reading.md`. In short:
1. Write a codebook: fields, allowed values, one-line definitions, and 2–3 edge-case rulings. Save it as JSON for `merge`.
2. Run `batch` to write JSONL files of about 40 papers each.
3. Give each subagent the codebook, the output format and several batch files. Run them in parallel.
4. Run `merge` with the codebook to validate every row and list missing papers.
5. Re-batch the missing papers, fix invalid values, then `tally`.
6. Spot-check about 20 labels yourself before trusting the distribution.

If your environment has no subagents, read the batches yourself in sequence. If that is too many, read a per-year sample and say so.

### 5. Compare fairly

- **Shares, not counts.** 2027 has 2.17× the submissions of 2026, so counts always rise. Use percent of the population for within-population distributions and per-10k submissions for field size (`select` prints both).
- **Mentions are not usage.** Abstracts mention only some of a paper's setup. Phrase results as "named in the abstract" and treat "none stated" as its own category.
- **2027 writing shift.** 42% of 2027 abstracts use a new formulaic wording style (`formulaic_style`). For any 2027 trend that rests on vocabulary, rerun the selection with `--exclude-formulaic` and report whether the result holds.
- **Small numbers.** Avoid ratios when the earlier year has fewer than about 10 papers. Report both counts instead.
- **2027 has no decisions yet.** `rating` and `accepted` are empty for 2027; 2026 acceptance can serve as a signal of what reviewers rewarded.

### 6. Report

Lead with the answer, then the evidence:
1. one or two sentences answering the question;
2. a table: category, n and % per year, change;
3. two to four observations, each tied to numbers;
4. three to six representative papers with OpenReview links (use `show`);
5. a short method note: population definition and size, how the attribute was measured (lexicon, read all, or sample), and caveats that apply.

Keep method detail out of the main answer; put it in the method note.

## Worked example

`references/example-agent-environments.md` walks through "What environments do 2026 and 2027 agent-safety papers use?" from definition to report. `lexicons/agent_environments.json` is the lexicon used there. Read the example the first time you face a question that needs per-paper reading.
