"""Macro-level aggregates for the dashboard -> data/macro.json

    python3 scripts/macro.py
"""
import glob
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
YEARS = [2025, 2026, 2027]

MODELS = {
    "Qwen": r"\bqwen", "Llama": r"\bllama", "GPT / OpenAI": r"\bgpt-?(3|4|5|o|-oss)|\bchatgpt|\bo[134](-mini)?\b",
    "Claude": r"\bclaude\b", "DeepSeek": r"deepseek", "Gemma": r"\bgemma", "Gemini": r"\bgemini\b",
    "Mistral": r"\bmi[sx]tral", "OLMo": r"\bolmo", "Kimi": r"\bkimi\b", "GLM": r"\bglm-?\d", "Phi": r"\bphi-\d",
    "Stable Diffusion": r"stable diffusion|\bsdxl\b", "FLUX": r"\bflux(\.1)?\b", "Wan (video)": r"\bwan ?2\.\d|\bwan2", "SAM": r"segment anything|\bsam ?2?\b",
}
BENCH = {
    "GSM8K": r"gsm8k", "MATH(-500)": r"\bmath-?500\b|\bmath benchmark|\bmath dataset", "AIME": r"\baime", "GPQA": r"\bgpqa",
    "MMLU": r"\bmmlu", "HumanEval/MBPP": r"humaneval|\bmbpp", "LiveCodeBench": r"livecodebench", "SWE-bench": r"swe-?bench",
    "OSWorld": r"osworld", "WebArena": r"webarena", "τ-bench": r"τ\^?2?[- ]?bench|\btau\^?2?-bench", "BrowseComp": r"browsecomp",
    "ARC-AGI": r"arc-agi", "HLE": r"humanity'?s last exam|\bhle\b", "AgentDojo": r"agentdojo", "HarmBench": r"harmbench",
    "LIBERO": r"\blibero", "ImageNet": r"imagenet", "VBench": r"vbench", "MMMU": r"\bmmmu",
}


def norm_kw(k):
    k = k.lower().strip().replace("–", "-")
    k = re.sub(r"\s+", " ", k)
    if k.endswith("s") and not k.endswith("ss") and len(k) > 4 and not k.endswith("sis"):
        k = k[:-1]
    return k


def logodds(c1, c2, prior_scale=0.01):
    """Monroe et al. informative-Dirichlet log-odds z-scores, c2 vs c1."""
    vocab = set(c1) | set(c2)
    a = {w: (c1[w] + c2[w]) for w in vocab}
    a0 = sum(a.values()) * prior_scale
    a = {w: v * prior_scale for w, v in a.items()}
    n1, n2 = sum(c1.values()), sum(c2.values())
    out = {}
    for w in vocab:
        l1 = np.log((c1[w] + a[w]) / (n1 + a0 - c1[w] - a[w]))
        l2 = np.log((c2[w] + a[w]) / (n2 + a0 - c2[w] - a[w]))
        var = 1 / (c1[w] + a[w]) + 1 / (c2[w] + a[w])
        out[w] = (l2 - l1) / np.sqrt(var)
    return out


def main():
    df = pd.read_parquet(ROOT / "data" / "corpus.parquet")
    cl = pd.read_parquet(ROOT / "data" / "clusters.parquet")
    df = df.merge(cl, on=["year", "id"])
    tot = df.groupby("year").size()
    out = {"totals": {int(y): int(n) for y, n in tot.items()}}
    out["status"] = {int(y): g.status.value_counts().to_dict() for y, g in df.groupby("year")}
    y26 = df[df.year == 2026]
    out["acc_base26"] = round(float(y26.accepted.mean()), 4)
    out["rating_base26"] = round(float(y26.rating.mean()), 3)

    # primary areas
    pa = df.groupby(["primary_area", "year"]).size().unstack(fill_value=0)
    acc = y26.groupby("primary_area").accepted.mean()
    out["areas"] = [dict(area=a, n=[int(pa.loc[a, y]) for y in YEARS], share=[round(pa.loc[a, y] / tot[y] * 100, 2) for y in YEARS],
                         acc26=round(float(acc.get(a, np.nan)), 3)) for a in pa.index]

    # clusters + labels
    labels = {}
    for f in sorted(glob.glob(str(ROOT / "work/clusters/labels/g*.json"))):
        for o in json.load(open(f)):
            labels[int(o["cluster"])] = o
    rows = []
    for c, g in df.groupby("cluster"):
        n = g.groupby("year").size().reindex(YEARS, fill_value=0)
        g26 = g[g.year == 2026]
        lab = labels.get(int(c), {})
        rows.append(dict(cluster=int(c), n=n.astype(int).tolist(), share=[round(n[y] / tot[y] * 1e4, 1) for y in YEARS],
                         acc26=round(float(g26.accepted.mean()), 3) if len(g26) >= 15 else None,
                         rating26=round(float(g26.rating.mean()), 2) if len(g26) >= 15 and g26.rating.notna().any() else None,
                         **{k: lab.get(k) for k in ["name_en", "name_zh", "theme", "desc_zh", "trend_zh", "coherence", "example_ids"]}))
    out["clusters"] = rows
    th = pd.DataFrame([dict(theme=r["theme"], **{str(y): r["n"][i] for i, y in enumerate(YEARS)}) for r in rows]).groupby("theme").sum()
    out["themes"] = [dict(theme=t, n=[int(th.loc[t, str(y)]) for y in YEARS], share=[round(th.loc[t, str(y)] / tot[y] * 100, 2) for y in YEARS]) for t in th.index]

    # keywords log-odds 2026 -> 2027 (document frequency of normalised author keywords)
    kc = {y: Counter(k for ks in df[df.year == y].keywords for k in {norm_kw(x) for x in ks}) for y in YEARS}
    z = logodds(kc[2026], kc[2027])
    def kwrow(w):
        return dict(kw=w, n=[kc[y][w] for y in YEARS], share=[round(kc[y][w] / tot[y] * 100, 3) for y in YEARS], z=round(float(z[w]), 2))
    ranked = sorted(z, key=z.get)
    out["kw_rise"] = [kwrow(w) for w in reversed(ranked) if kc[2027][w] >= 20][:60]
    out["kw_fall"] = [kwrow(w) for w in ranked if kc[2026][w] >= 15][:60]
    out["kw_new"] = [kwrow(w) for w, n in kc[2027].most_common() if n >= 25 and kc[2026][w] <= 2 and kc[2025][w] <= 2][:60]
    out["kw_top27"] = [kwrow(w) for w, _ in kc[2027].most_common(40)]

    text = (df.title + " " + df.keywords.map("; ".join) + " " + df.abstract).str.lower()
    def mentions(d):
        res = []
        for k, rx in d.items():
            m = text.str.contains(rx, regex=True)
            n = df[m].groupby("year").size().reindex(YEARS, fill_value=0)
            res.append(dict(name=k, n=n.astype(int).tolist(), share=[round(n[y] / tot[y] * 100, 2) for y in YEARS]))
        return res
    import warnings; warnings.filterwarnings("ignore")
    out["models"] = mentions(MODELS)
    out["benchmarks"] = mentions(BENCH)
    json.dump(out, open(ROOT / "data" / "macro.json", "w"), ensure_ascii=False)
    print("clusters labelled:", sum(1 for r in rows if r["name_zh"]), "/", len(rows))
    print(pd.DataFrame(out["themes"]).to_string())
    for k in ["kw_rise", "kw_fall", "kw_new"]:
        print(k, [(r["kw"], r["n"][1], r["n"][2]) for r in out[k][:30]])
    print(pd.DataFrame(out["models"]).to_string()); print(pd.DataFrame(out["benchmarks"]).to_string())


if __name__ == "__main__":
    main()
