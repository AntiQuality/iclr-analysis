"""Export the publishable ICLR dataset to release/.

    python3 scripts/export_release.py

Reads the intermediate tables built by the other scripts and writes a
self-contained folder (paper tables, topic clusters, safety labels, aggregate
statistics) that can be published as its own repository.
"""
import json
import shutil
from pathlib import Path

import pandas as pd

from build_dashboard import THEMES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release"
YEARS = [2025, 2026, 2027]


def main():
    corpus = pd.read_parquet(ROOT / "data/corpus.parquet")
    clusters = pd.read_parquet(ROOT / "data/clusters.parquet")
    style = pd.read_parquet(ROOT / "work/insights/style_anomaly_papers.parquet")
    macro = json.loads((ROOT / "data/macro.json").read_text())
    meta = pd.DataFrame(macro["clusters"])

    # topic clusters
    cl = meta[["cluster", "name_en", "name_zh", "theme", "desc_zh", "trend_zh", "coherence"]].copy()
    cl.insert(4, "theme_zh", cl.theme.map(THEMES))
    for i, y in enumerate(YEARS):
        cl[f"n_{y}"] = meta.n.str[i]
        cl[f"per10k_{y}"] = meta.share.str[i]
        cl[f"per10k_excl_formulaic_{y}"] = meta.share_r.str[i]
    cl["accept_rate_2026"] = meta.acc26
    cl["mean_rating_2026"] = meta.rating26
    cl["example_ids"] = meta.example_ids.str.join(" ")
    (OUT / "topics").mkdir(parents=True, exist_ok=True)
    cl.to_csv(OUT / "topics/clusters.csv", index=False)

    # paper tables
    df = (corpus
          .merge(clusters[["year", "id", "cluster", "centrality"]], on=["year", "id"], how="left")
          .merge(style[["year", "id", "score", "high"]], on=["year", "id"], how="left")
          .merge(cl[["cluster", "name_en", "name_zh", "theme"]], on="cluster", how="left"))
    df = df.rename(columns={"cluster": "topic_cluster", "centrality": "topic_centrality",
                            "name_en": "topic_name_en", "name_zh": "topic_name_zh",
                            "score": "style_score", "high": "formulaic_style"})
    df["number"] = df.number.astype("Int64")
    df["accepted"] = df.accepted.astype("boolean").mask(df.year == 2027)  # no decisions yet
    df["openreview_url"] = "https://openreview.net/forum?id=" + df.id
    cols = ["year", "id", "number", "title", "abstract", "tldr", "keywords", "primary_area", "status",
            "rating", "accepted", "openreview_url", "topic_cluster", "topic_name_en", "topic_name_zh",
            "theme", "topic_centrality", "style_score", "formulaic_style"]
    (OUT / "submissions").mkdir(exist_ok=True)
    for y in YEARS:
        part = df[df.year == y][cols].sort_values("number").reset_index(drop=True)
        part.to_parquet(OUT / f"submissions/iclr{y}.parquet", index=False, compression="zstd")
        print(y, len(part))

    # safety labels (join to submissions on year + id for text)
    sl = pd.read_parquet(ROOT / "data/safety_labels.parquet")
    sl = sl[["year", "id", "title", "primary_area", "in_area", "lex_hits", "rel", "sub", "sub2", "type", "target", "topic"]]
    sl = sl.rename(columns={"in_area": "candidate_by_area", "lex_hits": "candidate_lexicon_hits", "rel": "relevance",
                            "sub": "subfield", "sub2": "subfield_2", "type": "contribution_type", "target": "target_system"})
    (OUT / "safety").mkdir(exist_ok=True)
    sl.sort_values(["year", "id"]).to_csv(OUT / "safety/labels.csv", index=False)
    shutil.copy(ROOT / "work/safety/TAXONOMY.md", OUT / "safety/TAXONOMY.md")

    # aggregates behind the dashboard
    (OUT / "aggregates").mkdir(exist_ok=True)
    for name in ["macro.json", "concepts.json", "safety.json"]:
        shutil.copy(ROOT / "data" / name, OUT / "aggregates" / name)
    shutil.copy(ROOT / "work/insights/style_anomaly.json", OUT / "aggregates/style.json")


if __name__ == "__main__":
    main()
