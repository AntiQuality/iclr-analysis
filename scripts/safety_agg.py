"""Aggregate sub-agent safety labels -> data/safety_labels.parquet + data/safety.json

    python3 scripts/safety_agg.py
"""
import glob
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SUB_ZH = {
    "JB_ATK": "越狱攻击与红队", "JB_DEF": "越狱防御与护栏", "PI": "提示注入与工具安全", "AGENT_SAFE": "智能体安全",
    "FT_ROBUST": "微调安全性", "ALIGN_TRAIN": "对齐训练", "REWARD_HACK": "奖励黑客与谄媚", "DECEPTION": "欺骗、Scheming 与涌现失配",
    "OVERSIGHT": "监督、CoT 监控与 AI Control", "DANGER_EVAL": "危险能力与安全评测", "INTERP_SAFE": "面向安全的可解释性",
    "INTERP_GEN": "通用可解释性", "UNLEARN": "机器遗忘", "BACKDOOR": "后门与数据投毒", "WATERMARK": "水印与生成内容检测",
    "PRIVACY": "隐私", "IP": "模型知识产权", "ADV_ROBUST": "对抗鲁棒性", "GEN_SAFE": "生成模型（图像/视频）安全",
    "HALLU": "幻觉与诚实性", "FAIR": "公平与偏见", "VALUES": "价值与多元对齐", "SOCIETAL": "社会影响与治理",
    "SAFE_RL": "安全 RL 与具身安全", "OOD": "OOD 与分布偏移", "OTHER": "其他安全",
}
GROUPS = {
    "攻防对抗": ["JB_ATK", "JB_DEF", "ADV_ROBUST", "BACKDOOR", "GEN_SAFE"],
    "智能体安全": ["PI", "AGENT_SAFE"],
    "对齐与失配": ["ALIGN_TRAIN", "FT_ROBUST", "REWARD_HACK", "DECEPTION", "VALUES"],
    "监督、评测与可解释": ["OVERSIGHT", "DANGER_EVAL", "INTERP_SAFE", "INTERP_GEN"],
    "数据与模型治理": ["UNLEARN", "PRIVACY", "WATERMARK", "IP"],
    "可信与社会": ["HALLU", "FAIR", "SOCIETAL", "SAFE_RL", "OOD", "OTHER"],
}


def main():
    rows = []
    for f in sorted(glob.glob(str(ROOT / "work/safety/out/b*_p*.jsonl"))):
        rows += [json.loads(l) for l in open(f) if l.strip()]
    lab = pd.DataFrame(rows).drop_duplicates("id", keep="last")
    cand = pd.read_parquet(ROOT / "data" / "safety_candidates.parquet")
    df = cand.merge(lab.drop(columns=["y"]), on="id", how="inner")
    df["accepted"] = df.status.str.startswith("accept")
    df.to_parquet(ROOT / "data" / "safety_labels.parquet", index=False)
    corpus_tot = pd.read_parquet(ROOT / "data" / "corpus.parquet").groupby("year").size()
    labelled_frac = df.groupby("year").size() / cand.groupby("year").size()
    out = dict(labelled=int(len(df)), candidates=int(len(cand)), labelled_frac={int(k): round(v, 3) for k, v in labelled_frac.items()},
               totals={int(k): int(v) for k, v in corpus_tot.items()}, sub_zh=SUB_ZH, groups=GROUPS)
    core = df[df.rel >= 1]
    out["rel_counts"] = {int(y): g.rel.value_counts().sort_index().to_dict() for y, g in df.groupby("year")}
    def per_sub(d):
        res = []
        for s in SUB_ZH:
            g = d[d["sub"] == s]
            n = g.groupby("year").size().reindex([2026, 2027], fill_value=0)
            g2 = g[g.rel == 2].groupby("year").size().reindex([2026, 2027], fill_value=0)
            a = g[g.year == 2026]
            res.append(dict(sub=s, zh=SUB_ZH[s], n=n.astype(int).tolist(), n_core=g2.astype(int).tolist(),
                            share=[round(n[y] / corpus_tot[y] * 1e4, 1) for y in [2026, 2027]],
                            acc26=round(float(a.accepted.mean()), 3) if len(a) >= 10 else None,
                            rating26=round(float(a.rating.mean()), 2) if len(a) >= 10 and a.rating.notna().any() else None))
        return res
    out["subs"] = per_sub(core)
    for k in ["type", "target"]:
        t = core.groupby(["year", k]).size().unstack(fill_value=0)
        out[k] = {c: [int(t.loc[y, c]) if y in t.index else 0 for y in [2026, 2027]] for c in t.columns}
    hm = core[core.year == 2027].groupby(["sub", "target"]).size().unstack(fill_value=0)
    hm6 = core[core.year == 2026].groupby(["sub", "target"]).size().unstack(fill_value=0)
    out["heat"] = {"2027": {s: hm.loc[s].to_dict() for s in hm.index}, "2026": {s: hm6.loc[s].to_dict() for s in hm6.index}}
    tp = core.copy()
    tp["topic_n"] = tp.topic.str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    c26, c27 = Counter(tp[tp.year == 2026].topic_n), Counter(tp[tp.year == 2027].topic_n)
    out["top_topics27"] = [(t, c26[t], n) for t, n in c27.most_common(80)]
    out["safety_share"] = {int(y): round(len(core[core.year == y]) / corpus_tot[y] * 100, 2) for y in [2026, 2027]}
    out["safety_core_share"] = {int(y): round(len(df[(df.year == y) & (df.rel == 2)]) / corpus_tot[y] * 100, 2) for y in [2026, 2027]}
    json.dump(out, open(ROOT / "data" / "safety.json", "w"), ensure_ascii=False)
    print(json.dumps({k: out[k] for k in ["labelled", "labelled_frac", "rel_counts", "safety_share", "safety_core_share"]}))
    print(pd.DataFrame(out["subs"]).to_string())
    print(out["type"]); print(out["target"])


if __name__ == "__main__":
    main()
