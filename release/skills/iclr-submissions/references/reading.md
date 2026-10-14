# Reading papers with subagents

Use this when an attribute has to be judged from each abstract. Examples: what environment, threat model, evaluation protocol, data source or base model a paper uses, or what kind of claim it makes.

## 1. Codebook

Write a short codebook before batching. Include:
- **Fields.** Each field is either a closed set of categories or a free list of names. Prefer a closed `list` field for the distribution plus a free `list` field for names; the free field lets you find new categories later.
- **Definitions.** One line per category, written so two readers would agree.
- **Explicit "not stated".** Use `none_stated` for papers whose abstract does not say, so silence is not mistaken for a category.
- **Edge-case rulings.** Add two or three, picked from the papers you skimmed in the pilot.
- **Evidence.** A short `evidence` quote or phrase per paper makes spot checks fast.

Save the machine-readable part for `merge`:

```json
{"fields": {
  "env_category": {"type": "list", "values": ["web", "os_desktop_mobile", "coding_terminal", "tool_api", "mcp_skills", "email_office", "memory_rag", "multi_agent", "embodied", "chat_only", "none_stated"]},
  "env_named": {"type": "list"},
  "evidence": {"type": "text", "optional": true}
}}
```

Types: `enum` (one value from `values`), `list` (values from `values` if given), `text`, `bool`, `int`. Mark a field `"optional": true` if it may be absent.

## 2. Batches

```bash
python3 skills/iclr-submissions/scripts/iclr.py batch --population work/pop.parquet --out-dir work/batches --size 40
```

Each line is `{"id", "y", "t" (title), "k" (keywords), "area", "a" (abstract, plus TL;DR)}`. About 40 papers per file keeps one file within a comfortable reading load. Give each subagent 3–6 files and run the subagents in parallel.

## 3. Subagent prompt template

Adapt the bracketed parts. Keep the codebook identical across subagents; that keeps labels consistent.

```
You are labelling ICLR submissions from their abstracts for a research question:
"[question]".

Read every line of these files: [work/batches/batch_000.jsonl ...].
Each line is one paper: id, y (year), t (title), k (keywords), area, a (abstract).

For each paper, write one JSON object per line to [work/out/<batch name>.jsonl]:
{"id": "...", "y": 2027, [field]: [...], "evidence": "<= 15 words quoted or paraphrased from the abstract"}

Codebook:
[fields, categories with one-line definitions, edge-case rulings]

Rules:
- Judge only from the given text. If the abstract does not say, use "none_stated".
- Do not guess from the title alone when the abstract says otherwise.
- Output exactly one line per input paper, same id and year, valid JSON, nothing else in the file.
When done, reply with the number of papers written per file and any category you found missing from the codebook.
```

The year is in the input. Remind readers to judge from content, not year, so they do not project expected trends.

## 4. Merge, repair, tally

```bash
python3 skills/iclr-submissions/scripts/iclr.py merge --inputs "work/out/*.jsonl" --population work/pop.parquet \
    --codebook work/codebook.json --out work/labels.parquet --missing-out work/missing.csv
python3 skills/iclr-submissions/scripts/iclr.py tally --table work/labels.parquet --column env_category
python3 skills/iclr-submissions/scripts/iclr.py tally --table work/labels.parquet --column env_named --top 25
```

`merge` lists invalid values, duplicates and missing papers. Handle each problem before you report:
- **Missing papers.** Re-batch them from `work/missing.csv` with `batch`.
- **Invalid values.** Map an obvious synonym in a small script. Otherwise send the paper back to a reader.
- **Missing categories.** If readers report a category the codebook lacks, decide whether to add it. If you add it, have the affected batches relabelled.

## 5. Quality checks

- **Spot check.** Open about 20 random labelled papers (`show --ids ... --abstract 600`) and compare against the labels. If more than ~3 disagree, tighten the definitions and relabel.
- **Sampled reading.** When you read a sample instead of the whole population, give a 95% interval for key shares: ±1.96·sqrt(p(1−p)/n).
- **Report two measures.** Use the share of papers with at least one value in a category, and also the share of `none_stated`.
