"""Add shares that exclude formulaic-style papers to data/macro.json and data/concepts.json.

    python3 scripts/robust_shares.py      # after macro.py, concepts.py and style_anomaly.py

Robust share = papers in the group without the formulaic flag / submissions without the flag,
per year. Clusters and themes are per 10k submissions, concepts in percent.
"""
import json
from pathlib import Path

import pandas as pd

from concepts import CONCEPTS, concept_text

ROOT = Path(__file__).resolve().parent.parent
YEARS = [2025, 2026, 2027]


def main():
    df = pd.read_parquet(ROOT / "data/corpus.parquet")
    st = pd.read_parquet(ROOT / "work/insights/style_anomaly_papers.parquet")[["year", "id", "high"]]
    df = df.merge(st, on=["year", "id"], how="left")
    df["high"] = df.high.fillna(False).astype(bool)
    cl = pd.read_parquet(ROOT / "data/clusters.parquet")[["year", "id", "cluster"]]
    df = df.merge(cl, on=["year", "id"], how="left")
    keep = ~df.high
    rtot = df[keep].groupby("year").size().reindex(YEARS)

    def per10k(mask):
        n = df[mask & keep].groupby("year").size().reindex(YEARS, fill_value=0)
        return (n / rtot * 1e4).round(1).tolist()

    macro = json.loads((ROOT / "data/macro.json").read_text())
    for c in macro["clusters"]:
        m = df.cluster == c["cluster"]
        c["share_r"] = per10k(m)
        c["high27"] = round(float(df[m & (df.year == 2027)].high.mean()), 3)
    theme_of = {c["cluster"]: c["theme"] for c in macro["clusters"]}
    th = df.cluster.map(theme_of)
    for t in macro["themes"]:
        n = df[(th == t["theme"]) & keep].groupby("year").size().reindex(YEARS, fill_value=0)
        t["share_r"] = (n / rtot * 100).round(2).tolist()  # percent, like themes[].share
    macro["robust_totals"] = rtot.astype(int).tolist()
    macro["high_share27"] = round(float(df[df.year == 2027].high.mean()), 4)
    (ROOT / "data/macro.json").write_text(json.dumps(macro, ensure_ascii=False, indent=1))

    con = json.loads((ROOT / "data/concepts.json").read_text())
    text, tk = concept_text(df)
    pats = {en: pat for items in CONCEPTS.values() for _, en, pat in items}
    for c in con["concepts"]:
        pat = pats[c["en"]]
        m = tk.str.contains(r"\bbenchmark", regex=True) if pat == "__BENCH__" else text.str.contains(pat, regex=True)
        c["share_r"] = [round(v / 100, 3) for v in per10k(m)]
    (ROOT / "data/concepts.json").write_text(json.dumps(con, ensure_ascii=False, indent=1))
    print("robust totals", rtot.tolist())


if __name__ == "__main__":
    main()
