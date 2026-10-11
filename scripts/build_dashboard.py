"""Assemble all analysis outputs into the single-file dashboard: dashboard/index.html

    python3 scripts/build_dashboard.py
"""
import glob
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
THEMES = {"agents": "智能体", "llm_post": "LLM 推理与后训练", "llm_core": "LLM 架构与效率", "mm": "多模态理解", "gen": "生成模型",
          "vision": "视觉与 3D", "embodied": "具身 / 机器人 / 世界模型", "rl": "强化学习（非 LLM）", "safety": "安全与可信",
          "interp": "可解释性", "theory": "理论与优化", "struct": "图、时序、概率与因果", "science": "AI for Science",
          "eval": "数据、评测与基准", "repr": "表示 / 迁移 / 持续学习", "systems": "系统与基础设施", "apps": "其他应用"}
AREA_ZH = {
    "foundation or frontier models, including LLMs": "基础 / 前沿模型（含 LLM）",
    "applications to computer vision, audio, language, and other modalities": "CV / 音频 / 语言等应用",
    "alignment, fairness, safety, privacy, and societal considerations": "对齐、公平、安全、隐私与社会",
    "datasets and benchmarks": "数据集与基准",
    "generative models": "生成模型",
    "reinforcement learning": "强化学习",
    "applications to robotics, autonomy, planning": "机器人、自主与规划",
    "unsupervised, self-supervised, semi-supervised, and supervised representation learning": "表示学习（自/半/有监督）",
    "applications to physical sciences (physics, chemistry, biology, etc.)": "物理科学应用（物理/化学/生物）",
    "interpretability and explainable AI": "可解释性",
    "optimization": "优化",
    "learning theory": "学习理论",
    "transfer learning, meta learning, and lifelong learning": "迁移 / 元学习 / 终身学习",
    "other topics in machine learning (i.e., none of the above)": "其他",
    "learning on time series and dynamical systems": "时间序列与动力系统",
    "learning on graphs and other geometries & topologies": "图与几何拓扑学习",
    "probabilistic methods (Bayesian methods, variational inference, sampling, UQ, etc.)": "概率方法",
    "applications to neuroscience & cognitive science": "神经科学与认知科学",
    "infrastructure, software libraries, hardware, systems, etc.": "基础设施、软件、硬件与系统",
    "neurosymbolic & hybrid AI systems (physics-informed, logic & formal reasoning, etc.)": "神经符号与混合系统",
    "causal reasoning": "因果推理",
}
DOMAIN_ORDER = ["llm", "agents", "mmgen", "embodied", "science", "foundations"]
SAFETY_ORDER = ["agent", "attack", "align", "oversight", "govern", "trust"]


def load(p, default=None):
    """Load a JSON file; for work/insights/* prefer the copy-edited version in work/insights/edited/."""
    p = ROOT / p
    ed = p.parent / "edited" / p.name
    if p.parent.name == "insights" and ed.exists():
        p = ed
    return json.loads(p.read_text()) if p.exists() else default


def main():
    macro = load("data/macro.json")
    corpus = pd.read_parquet(ROOT / "data/corpus.parquet")
    cl = pd.read_parquet(ROOT / "data/clusters.parquet")
    title = dict(zip(corpus.id, corpus.title))
    for c in macro["clusters"]:
        c["examples"] = [{"id": i, "title": title.get(i, i)} for i in (c.get("example_ids") or [])]
        c.pop("example_ids", None)
    for a in macro["areas"]:
        a["zh"] = AREA_ZH.get(a["area"], a["area"])
    lab = pd.read_parquet(ROOT / "data/safety_labels.parquet")
    lab = lab[lab.rel >= 1].sort_values(["year", "rel"], ascending=[False, False])
    sp = [[r.id, int(r.year), r.title, r.sub, (r.sub2 if isinstance(r.sub2, str) else ""), r.type, r.target, int(r.rel), r.topic, r.status] for r in lab.itertuples()]
    p27 = corpus[corpus.year == 2027][["id", "title"]].merge(cl[cl.year == 2027][["id", "cluster"]], on="id")
    papers27 = [[r.id, r.title, int(r.cluster)] for r in p27.itertuples()]
    domains = [d for d in (load(f"work/insights/macro_{k}.json") for k in DOMAIN_ORDER) if d]
    schap = [d for d in (load(f"work/insights/safety_{k}.json") for k in SAFETY_ORDER) if d]
    D = dict(
        meta=dict(totals=macro["totals"], acc_base26=macro["acc_base26"]),
        themeNames=THEMES, themes=macro["themes"], areas=macro["areas"], clusters=macro["clusters"],
        concepts=load("data/concepts.json")["concepts"], kw={k: macro[k] for k in ["kw_rise", "kw_fall", "kw_new"]},
        models=macro["models"], benchmarks=macro["benchmarks"],
        style=load("work/insights/style_dashboard.json"), domains=domains,
        safety=load("data/safety.json"), safetyChapters=schap, safetyThesis=load("work/insights/safety_thesis.json"),
        safetyPapers=sp, papers27=papers27, text=load("dashboard/src/text.json"),
    )
    blob = json.dumps(D, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
    html = (ROOT / "dashboard/src/template.html").read_text().replace("/*__DATA__*/", blob)
    (ROOT / "dashboard/index.html").write_text(html)
    print(f"dashboard/index.html {len(html)/1e6:.2f} MB; domains={len(domains)} safety chapters={len(schap)} safety papers={len(sp)} papers27={len(papers27)}")


if __name__ == "__main__":
    main()
