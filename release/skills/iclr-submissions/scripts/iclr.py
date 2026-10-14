#!/usr/bin/env python3
"""Query helper for the ICLR 2025-2027 submissions dataset.

Subcommands (run `iclr.py <cmd> -h` for options):
  select   filter papers into a population file and report its size per year
  count    count lexicon (regex) matches in a population, per year, with coverage
  batch    split a population into JSONL batches for reading by subagents
  merge    validate subagent outputs against a codebook and merge them
  tally    distribution of a labelled field per year, with shares and ratios
  show     print papers (year, title, link) from a population or id list

Requires pandas and pyarrow. The data folder is found from --data, the
ICLR_DATA environment variable, or by walking up from this file until a
folder containing submissions/ is found.
"""
import argparse
import glob
import json
import os
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

YEARS = (2025, 2026, 2027)
warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression")
TEXT_COLS = ("title", "keywords", "tldr", "abstract")


# ---------------------------------------------------------------- loading

def data_root(arg=None):
    for cand in [arg, os.environ.get("ICLR_DATA")]:
        if cand and (Path(cand) / "submissions").is_dir():
            return Path(cand)
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "submissions").is_dir():
            return parent
    sys.exit("Cannot find the data folder (one containing submissions/). Pass --data or set ICLR_DATA.")


def load_papers(root, years=YEARS):
    df = pd.concat([pd.read_parquet(root / f"submissions/iclr{y}.parquet") for y in years], ignore_index=True)
    kw = df.keywords.map(lambda k: "; ".join(k) if k is not None and len(k) else "")
    df["text"] = df.title + "\n" + kw + "\n" + df.tldr.fillna("") + "\n" + df.abstract.fillna("")
    return df


def load_safety(root):
    return pd.read_csv(root / "safety/labels.csv")


def totals(root, years=YEARS, exclude_formulaic=False):
    """Submissions per year: the denominator for per-10k shares."""
    out = {}
    for y in years:
        d = pd.read_parquet(root / f"submissions/iclr{y}.parquet", columns=["formulaic_style"])
        out[y] = int((~d.formulaic_style).sum()) if exclude_formulaic else len(d)
    return out


def read_population(path):
    path = Path(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    return pd.read_csv(path)


def write_table(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        df.to_parquet(path, index=False)
    elif path.suffix == ".jsonl":
        df.to_json(path, orient="records", lines=True, force_ascii=False)
    else:
        df.to_csv(path, index=False)


def per_year(df, years):
    return {int(y): int((df.year == y).sum()) for y in years}


def print_table(rows, cols):
    widths = {c: max(len(str(c)), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print("  ".join(str(c).ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def fmt_ratio(a, b):
    if not a:
        return "new" if b else "-"
    return f"{b / a:.2f}x"


# ---------------------------------------------------------------- select

def cmd_select(a):
    root = data_root(a.data)
    years = a.years or list(YEARS)
    df = load_papers(root, years)
    if a.exclude_formulaic:
        df = df[~df.formulaic_style]

    if any([a.relevance is not None, a.subfield, a.target, a.type, a.safety_only]):
        s = load_safety(root)
        if a.relevance is not None:
            s = s[s.relevance >= a.relevance]
        if a.subfield:
            s = s[s.subfield.isin(a.subfield) | s.subfield_2.isin(a.subfield)]
        if a.target:
            s = s[s.target_system.isin(a.target)]
        if a.type:
            s = s[s.contribution_type.isin(a.type)]
        cols = ["year", "id", "relevance", "subfield", "subfield_2", "contribution_type", "target_system", "topic"]
        df = df.merge(s[cols], on=["year", "id"], how="inner")

    if a.theme:
        df = df[df.theme.isin(a.theme)]
    if a.cluster:
        df = df[df.topic_cluster.isin(a.cluster)]
    if a.area:
        df = df[df.primary_area.str.contains("|".join(a.area), case=False, na=False)]
    if a.status:
        df = df[df.status.isin(a.status)]
    if a.active_only:
        df = df[~df.status.isin(["withdrawn", "desk_rejected"])]
    for pat in a.regex or []:
        df = df[df.text.str.contains(pat, flags=re.I, regex=True)]
    for pat in a.not_regex or []:
        df = df[~df.text.str.contains(pat, flags=re.I, regex=True)]

    tot = totals(root, years, a.exclude_formulaic)
    rows = [{"year": y, "papers": n, "per10k_submissions": f"{1e4 * n / tot[y]:.1f}", "submissions": tot[y]}
            for y, n in per_year(df, years).items()]
    print_table(rows, ["year", "papers", "per10k_submissions", "submissions"])
    if a.out:
        write_table(df.drop(columns=["text"]), a.out)
        print(f"wrote {len(df)} rows -> {a.out}")


# ---------------------------------------------------------------- count

def load_lexicon(path):
    """{"name": "regex"} or {"category": {"name": "regex"}} -> list of (category, name, regex)."""
    lex = json.loads(Path(path).read_text())
    items = []
    for k, v in lex.items():
        if isinstance(v, dict):
            items += [(k, n, r) for n, r in v.items()]
        else:
            items.append((None, k, v))
    return items


def match_lexicon(df, items):
    hits = pd.DataFrame(index=df.index)
    for _, name, rx in items:
        hits[name] = df.text.str.contains(rx, flags=re.I, regex=True)
    return hits


def cmd_count(a):
    root = data_root(a.data)
    pop = read_population(a.population)
    if "text" not in pop:
        pop = pop[["year", "id"]].merge(load_papers(root, sorted(pop.year.unique())), on=["year", "id"])
    items = load_lexicon(a.lexicon)
    hits = match_lexicon(pop, items)
    years = sorted(int(y) for y in pop.year.unique())
    size = per_year(pop, years)

    def row(label, mask):
        r = {"term": label}
        for y in years:
            n = int((mask & (pop.year == y)).sum())
            r[str(y)] = f"{n} ({100 * n / size[y]:.1f}%)" if size[y] else "0"
            r[f"_{y}"] = n / size[y] if size[y] else 0
        if len(years) >= 2:
            r["share ratio"] = fmt_ratio(r[f"_{years[-2]}"], r[f"_{years[-1]}"])
        return r

    rows = [row(name, hits[name]) for _, name, _ in items]
    cats = sorted({c for c, _, _ in items if c})
    cat_rows = [row(f"[{c}]", hits[[n for cc, n, _ in items if cc == c]].any(axis=1)) for c in cats]
    rows = sorted(rows, key=lambda r: -r[f"_{years[-1]}"])
    cols = ["term"] + [str(y) for y in years] + (["share ratio"] if len(years) >= 2 else [])
    print(f"population: {size}  (percent = share of population that year)")
    if cat_rows:
        print_table(cat_rows, cols)
        print()
    print_table([r for r in rows if any(r[f"_{y}"] for y in years)], cols)
    print()
    print_table([row("ANY TERM (coverage)", hits.any(axis=1))], cols)

    if a.out:
        out = pop[["year", "id", "title"]].copy()
        out["matched"] = hits.apply(lambda r: "; ".join(n for n in hits.columns if r[n]), axis=1)
        write_table(out, a.out)
        print(f"wrote per-paper matches -> {a.out}")
    if a.unmatched:
        rest = pop[~hits.any(axis=1)].drop(columns=["text"], errors="ignore")
        write_table(rest, a.unmatched)
        print(f"wrote {len(rest)} unmatched papers -> {a.unmatched}")


# ---------------------------------------------------------------- batch

def cmd_batch(a):
    root = data_root(a.data)
    pop = read_population(a.population)
    full = load_papers(root, sorted(pop.year.unique()))
    pop = pop[["year", "id"]].merge(full, on=["year", "id"])
    if a.sample_per_year:
        pop = pop.sample(frac=1, random_state=a.seed).groupby("year").head(a.sample_per_year)
        print("sampled per year:", per_year(pop, sorted(pop.year.unique())))
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    recs = []
    for r in pop.itertuples():
        kw = list(r.keywords) if r.keywords is not None else []
        abs_ = (r.abstract or "")[: a.abstract_chars]
        if r.tldr:
            abs_ += "\nTL;DR: " + r.tldr
        recs.append({"id": r.id, "y": int(r.year), "t": r.title, "k": kw, "area": r.primary_area, "a": abs_})
    files = []
    for i in range(0, len(recs), a.size):
        f = out / f"batch_{i // a.size:03d}.jsonl"
        f.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in recs[i: i + a.size]) + "\n")
        files.append(f.name)
    (out / "manifest.json").write_text(json.dumps({"papers": len(recs), "batch_size": a.size, "files": files}, indent=1))
    print(f"{len(recs)} papers -> {len(files)} batches of <= {a.size} in {out}")


# ---------------------------------------------------------------- merge

def cmd_merge(a):
    code = json.loads(Path(a.codebook).read_text())
    fields = code["fields"]  # {"name": {"type": "enum|list|text|bool|int", "values": [...]}}
    pop = read_population(a.population)
    want = set(zip(pop.year.astype(int), pop.id))
    rows, problems = [], []
    for f in sorted(glob.glob(a.inputs)):
        for ln, line in enumerate(Path(f).read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"{f}:{ln} bad JSON ({e})")
                continue
            o["year"] = int(o.pop("y", o.get("year", 0)))
            for name, spec in fields.items():
                v = o.get(name)
                t = spec.get("type", "text")
                allowed = spec.get("values")
                if v is None:
                    if not spec.get("optional"):
                        problems.append(f"{f}:{ln} {o.get('id')} missing {name}")
                    continue
                if t == "enum" and allowed and v not in allowed:
                    problems.append(f"{f}:{ln} {o.get('id')} {name}={v!r} not in codebook")
                if t == "list":
                    if not isinstance(v, list):
                        problems.append(f"{f}:{ln} {o.get('id')} {name} should be a list")
                    elif allowed:
                        bad = [x for x in v if x not in allowed]
                        if bad:
                            problems.append(f"{f}:{ln} {o.get('id')} {name} has values not in codebook: {bad}")
            rows.append(o)
    df = pd.DataFrame(rows)
    got = set(zip(df.year, df.id)) if len(df) else set()
    dup = df[df.duplicated(["year", "id"], keep=False)] if len(df) else df
    missing = want - got
    extra = got - want
    print(f"rows {len(df)}  population {len(want)}  missing {len(missing)}  extra {len(extra)}  duplicated {dup.id.nunique() if len(dup) else 0}")
    for p in problems[: a.max_problems]:
        print("  ", p)
    if len(problems) > a.max_problems:
        print(f"   ... {len(problems) - a.max_problems} more problems")
    if missing:
        print("missing ids:", " ".join(sorted(i for _, i in missing)[:30]), "..." if len(missing) > 30 else "")
        if a.missing_out:
            write_table(pd.DataFrame(sorted(missing), columns=["year", "id"]), a.missing_out)
            print(f"wrote missing ids -> {a.missing_out} (re-batch them with `batch`)")
    if a.out and len(df):
        df = df.drop_duplicates(["year", "id"], keep="last")
        df = df[[(y, i) in want for y, i in zip(df.year, df.id)]]
        for name, spec in fields.items():  # parquet needs consistent list columns
            if spec.get("type") == "list" and name in df:
                df[name] = df[name].map(lambda v: v if isinstance(v, list) else ([] if v is None else [v]))
        write_table(df, a.out)
        print(f"wrote {len(df)} merged rows -> {a.out}")
    sys.exit(1 if (problems or missing) and a.strict else 0)


# ---------------------------------------------------------------- tally

def cmd_tally(a):
    df = read_population(a.table)
    col = a.column
    vals = df[col]
    if vals.map(lambda v: isinstance(v, (list, tuple)) or hasattr(v, "tolist")).any():
        df = df.assign(**{col: vals.map(lambda v: list(v) if v is not None else [])}).explode(col)
    elif a.split:
        df = df.assign(**{col: vals.fillna("").str.split(a.split)}).explode(col)
        df[col] = df[col].str.strip()
    df = df[df[col].notna() & (df[col] != "")]
    years = sorted(int(y) for y in df.year.unique())
    base = read_population(a.table)
    if a.where:
        base = base.query(a.where)
        df = df.query(a.where)
    size = per_year(base, years)
    ct = df.groupby([col, "year"]).id.nunique().unstack(fill_value=0)
    ct = ct.reindex(columns=years, fill_value=0)
    ct = ct.sort_values(years[-1], ascending=False).head(a.top)
    rows = []
    for v, r in ct.iterrows():
        row = {col: v}
        for y in years:
            row[str(y)] = f"{r[y]} ({100 * r[y] / size[y]:.1f}%)" if size[y] else "0"
        if len(years) >= 2:
            p, q = r[years[-2]] / max(size[years[-2]], 1), r[years[-1]] / max(size[years[-1]], 1)
            row["share ratio"] = fmt_ratio(p, q)
        rows.append(row)
    print(f"papers per year: {size}  (percent = share of papers that year; a paper can count under several values)")
    print_table(rows, [col] + [str(y) for y in years] + (["share ratio"] if len(years) >= 2 else []))


# ---------------------------------------------------------------- show

def cmd_show(a):
    root = data_root(a.data)
    if a.population:
        df = read_population(a.population)
    else:
        df = pd.DataFrame({"id": a.ids})
    full = load_papers(root)
    keys = ["year", "id"] if "year" in df else ["id"]
    df = df[keys].merge(full, on=keys)
    if a.sort:
        df = df.sort_values(a.sort, ascending=False)
    for r in df.head(a.n).itertuples():
        print(f"{r.year}  {r.title}\n      https://openreview.net/forum?id={r.id}  [{r.status}] {r.topic_name_en}")
        if a.abstract:
            print("      " + (r.abstract or "")[: a.abstract].replace("\n", " "))


# ---------------------------------------------------------------- cli

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", help="dataset folder (contains submissions/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("select", help="filter papers into a population")
    s.add_argument("--years", type=int, nargs="+")
    s.add_argument("--theme", nargs="+", help="broad theme codes, e.g. agents safety llm_post")
    s.add_argument("--cluster", type=int, nargs="+", help="topic cluster ids (0-299)")
    s.add_argument("--area", nargs="+", help="substring of the author-chosen primary area")
    s.add_argument("--status", nargs="+")
    s.add_argument("--active-only", action="store_true", help="drop withdrawn and desk-rejected papers")
    s.add_argument("--regex", nargs="+", help="case-insensitive regex on title+keywords+tldr+abstract (all must match)")
    s.add_argument("--not-regex", nargs="+")
    s.add_argument("--safety-only", action="store_true", help="restrict to papers with a safety label")
    s.add_argument("--relevance", type=int, help="minimum safety relevance (1 or 2); implies 2026-2027 only")
    s.add_argument("--subfield", nargs="+", help="safety subfield codes; matches subfield or subfield_2")
    s.add_argument("--target", nargs="+", help="safety target_system values")
    s.add_argument("--type", nargs="+", help="safety contribution_type values")
    s.add_argument("--exclude-formulaic", action="store_true", help="robustness check: drop formulaic_style papers")
    s.add_argument("--out", help="write the population (.parquet/.csv/.jsonl)")
    s.set_defaults(fn=cmd_select)

    c = sub.add_parser("count", help="count lexicon matches in a population")
    c.add_argument("--population", required=True)
    c.add_argument("--lexicon", required=True, help='JSON {"name": "regex"} or {"category": {"name": "regex"}}')
    c.add_argument("--out", help="write per-paper matched terms")
    c.add_argument("--unmatched", help="write papers matching no term (candidates for subagent reading)")
    c.set_defaults(fn=cmd_count)

    b = sub.add_parser("batch", help="write JSONL batches for subagents")
    b.add_argument("--population", required=True)
    b.add_argument("--out-dir", required=True)
    b.add_argument("--size", type=int, default=40)
    b.add_argument("--abstract-chars", type=int, default=2500)
    b.add_argument("--sample-per-year", type=int, help="read a random sample of N papers per year instead of all")
    b.add_argument("--seed", type=int, default=0)
    b.set_defaults(fn=cmd_batch)

    m = sub.add_parser("merge", help="validate and merge subagent outputs")
    m.add_argument("--inputs", required=True, help="glob of JSONL outputs, quoted")
    m.add_argument("--population", required=True)
    m.add_argument("--codebook", required=True, help="JSON with a 'fields' spec")
    m.add_argument("--out")
    m.add_argument("--missing-out")
    m.add_argument("--max-problems", type=int, default=40)
    m.add_argument("--strict", action="store_true", help="exit 1 on any problem")
    m.set_defaults(fn=cmd_merge)

    t = sub.add_parser("tally", help="distribution of a field per year")
    t.add_argument("--table", required=True)
    t.add_argument("--column", required=True)
    t.add_argument("--split", help="separator for multi-valued text columns, e.g. ';'")
    t.add_argument("--where", help="pandas query applied first, e.g. \"relevance == 2\"")
    t.add_argument("--top", type=int, default=40)
    t.set_defaults(fn=cmd_tally)

    w = sub.add_parser("show", help="print papers with links")
    w.add_argument("--population")
    w.add_argument("--ids", nargs="+")
    w.add_argument("-n", type=int, default=20)
    w.add_argument("--sort", help="column to sort by, descending (e.g. topic_centrality, rating)")
    w.add_argument("--abstract", type=int, default=0, help="also print the first N characters of the abstract")
    w.set_defaults(fn=cmd_show)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
