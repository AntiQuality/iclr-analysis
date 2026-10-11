"""Data-driven fine-grained topic map over ICLR 2025-2027 submissions.

TF-IDF (title and keywords up-weighted) -> truncated SVD -> L2 -> MiniBatchKMeans.
Embedding models are not reachable from the build environment; TF-IDF+SVD is a strong
baseline on exactly this corpus (Gonzalez-Marquez & Kobak, 2024).

    python3 scripts/cluster_topics.py K      # writes data/clusters.parquet, work/clusters/*.md
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.preprocessing import normalize

ROOT = Path(__file__).resolve().parent.parent
K = int(sys.argv[1]) if len(sys.argv) > 1 else 300
EXTRA_STOP = {"paper", "propose", "proposed", "method", "methods", "approach", "results", "show", "model", "models",
              "based", "novel", "new", "using", "use", "learning", "performance", "existing", "work", "framework",
              "experiments", "demonstrate", "task", "tasks", "state", "art", "data", "however", "significantly",
              "address", "achieves", "furthermore", "extensive", "code", "available", "introduce", "study", "large"}


def main():
    df = pd.read_parquet(ROOT / "data" / "corpus.parquet")
    kw = df.keywords.map("; ".join)
    text = (df.title + ". ") * 2 + (kw + ". ") * 2 + df.abstract
    vec = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS | EXTRA_STOP), ngram_range=(1, 2), min_df=8, max_df=0.3,
                          sublinear_tf=True, max_features=120000, token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9\-]+\b")
    X = vec.fit_transform(text)
    Z = normalize(TruncatedSVD(300, random_state=0).fit_transform(X))
    km = KMeans(K, random_state=0, n_init=2, max_iter=200).fit(Z)
    df["cluster"] = km.labels_
    dist = 1 - (Z * km.cluster_centers_[km.labels_] / np.linalg.norm(km.cluster_centers_[km.labels_], axis=1, keepdims=True)).sum(1)
    df["centrality"] = -dist
    terms = np.array(vec.get_feature_names_out())
    out = ROOT / "work" / "clusters"
    out.mkdir(parents=True, exist_ok=True)
    tot = df.groupby("year").size()
    rows = []
    for c in range(K):
        m = (df.cluster == c).values
        sub = df[m]
        cen = np.asarray(X[m].mean(0)).ravel()
        top = terms[np.argsort(-cen)[:15]]
        n = sub.groupby("year").size().reindex([2025, 2026, 2027], fill_value=0)
        rows.append(dict(cluster=c, n25=n[2025], n26=n[2026], n27=n[2027], terms=", ".join(top)))
    cl = pd.DataFrame(rows)
    for y, col in [(2025, "n25"), (2026, "n26"), (2027, "n27")]:
        cl["s" + col[1:]] = cl[col] / tot[y] * 1e4  # per 10k submissions
    cl["growth"] = (cl.s27 + 1) / (cl.s26 + 1)
    cl.to_csv(out / "clusters_summary.csv", index=False)
    df[["year", "id", "cluster", "centrality"]].to_parquet(ROOT / "data" / "clusters.parquet", index=False)
    print(cl.describe().round(2))
    print(cl.sort_values("growth").tail(15)[["cluster", "n26", "n27", "growth", "terms"]].to_string())


if __name__ == "__main__":
    main()
