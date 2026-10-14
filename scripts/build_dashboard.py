"""Build the bilingual two-page site into dashboard/site/

    python3 scripts/build_dashboard.py

Layout (copy the folder anywhere, e.g. <homepage>/blogs/trends/iclr-2027/):
    index.html                 picks zh/ or en/ from the browser language
    zh/index.html              overview      zh/safety/index.html   AI safety
    en/index.html              overview      en/safety/index.html   AI safety
    assets/                    app.css, app.js, core.js, text.{zh,en}.js, papers27.js, safety_papers.js
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "dashboard/src"
OUT = ROOT / "dashboard/site"
LANGS = ["zh", "en"]
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
# English copy uses ASCII punctuation; translators kept a few full-width brackets in copied values
FULLWIDTH = [("（", " ("), ("）", ")"), ("，", ", "), ("；", "; "), ("：", ": "), ("、", ", "), ("。", ". ")]


def jload(p):
    return json.loads((ROOT / p).read_text())


def insight(name, lang):
    """Chinese copy-edited chapters live in work/insights/edited/, English ones in work/insights/en/."""
    sub = "edited" if lang == "zh" else "en"
    p = ROOT / "work/insights" / sub / name
    return json.loads(p.read_text()) if p.exists() else None


def walk_strings(o, fn):
    if isinstance(o, dict):
        return {k: walk_strings(v, fn) for k, v in o.items()}
    if isinstance(o, list):
        return [walk_strings(v, fn) for v in o]
    return fn(o) if isinstance(o, str) else o


def ascii_punct(t):
    for a, b in FULLWIDTH:
        t = t.replace(a, b)
    return re.sub(r" {2,}", " ", t).replace("( ", "(")


def js_asset(name, var, obj):
    body = f"window.{var}=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n"
    (OUT / "assets" / name).write_text(body)
    return hashlib.sha1(body.encode()).hexdigest()[:8]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    macro = jload("data/macro.json")
    corpus = pd.read_parquet(ROOT / "data/corpus.parquet")
    cl = pd.read_parquet(ROOT / "data/clusters.parquet")
    title = dict(zip(corpus.id, corpus.title))

    # ---- language-neutral numbers
    clusters = []
    for c in macro["clusters"]:
        c = {k: v for k, v in c.items() if k not in ("desc_zh", "trend_zh", "example_ids")}
        c["examples"] = [{"id": i, "title": title.get(i, i)} for i in (dict(zip([x["cluster"] for x in macro["clusters"]], [x.get("example_ids") or [] for x in macro["clusters"]]))[c["cluster"]])]
        clusters.append(c)
    for a in macro["areas"]:
        a["zh"] = AREA_ZH.get(a["area"], a["area"])
    core = dict(meta=dict(totals=macro["totals"], acc_base26=macro["acc_base26"]), themes=macro["themes"], areas=macro["areas"],
                clusters=clusters, concepts=jload("data/concepts.json")["concepts"],
                kw={k: macro[k] for k in ["kw_rise", "kw_fall", "kw_new"]}, models=macro["models"], benchmarks=macro["benchmarks"],
                safety=jload("data/safety.json"))
    ver = {"core.js": js_asset("core.js", "ATLAS_CORE", core)}

    # ---- paper lists
    lab = pd.read_parquet(ROOT / "data/safety_labels.parquet")
    lab = lab[lab.rel >= 1].sort_values(["year", "rel"], ascending=[False, False])
    sp = [[r.id, int(r.year), r.title, r.sub, (r.sub2 if isinstance(r.sub2, str) else ""), r.type, r.target, int(r.rel), r.topic, r.status] for r in lab.itertuples()]
    p27 = corpus[corpus.year == 2027][["id", "title"]].merge(cl[cl.year == 2027][["id", "cluster"]], on="id")
    ver["papers27.js"] = js_asset("papers27.js", "ATLAS_PAPERS27", [[r.id, r.title, int(r.cluster)] for r in p27.itertuples()])
    ver["safety_papers.js"] = js_asset("safety_papers.js", "ATLAS_SAFETY_PAPERS", sp)

    # ---- one text bundle per language
    ui_src = jload("dashboard/src/ui.json")
    cl_en = {d["cluster"]: d for d in jload("work/clusters/labels_en.json")}
    ids = set(corpus.id)
    ui = {}
    for lang in LANGS:
        u = {k: ({kk: vv[lang] for kk, vv in v.items()} if "zh" not in v else v[lang]) for k, v in ui_src.items()}
        text = jload("dashboard/src/text.json" if lang == "zh" else "dashboard/src/text.en.json")
        bundle = dict(
            ui=u, text=text,
            domains=[d for d in (insight(f"macro_{k}.json", lang) for k in DOMAIN_ORDER) if d],
            safetyChapters=[d for d in (insight(f"safety_{k}.json", lang) for k in SAFETY_ORDER) if d],
            safetyThesis=insight("safety_thesis.json", lang), style=insight("style_dashboard.json", lang),
            clusterText={c["cluster"]: ({"desc": c["desc_zh"], "trend": c["trend_zh"]} if lang == "zh"
                                        else {"desc": cl_en[c["cluster"]]["desc_en"], "trend": cl_en[c["cluster"]]["trend_en"]})
                         for c in macro["clusters"]},
        )
        if lang == "en":
            bundle = walk_strings(bundle, ascii_punct)
        blob = json.dumps(bundle, ensure_ascii=False)
        cited = {m for m in re.findall(r"(?<![A-Za-z0-9_\-])[A-Za-z0-9_\-]{10}(?![A-Za-z0-9_\-])", blob) if m in ids}
        bundle["idTitles"] = {i: title[i] for i in sorted(cited)}
        ver[f"text.{lang}.js"] = js_asset(f"text.{lang}.js", "ATLAS_TEXT", bundle)
        ui[lang] = u
        left = re.findall(r"[一-鿿]", blob) if lang == "en" else []
        print(f"text.{lang}.js: {len(blob)/1e6:.2f} MB, cited ids {len(cited)}" + (f", Chinese chars left {len(left)}" if lang == "en" else ""))

    for f in ["app.css", "app.js"]:
        shutil.copy(SRC / f, OUT / "assets" / f)
        ver[f] = hashlib.sha1((SRC / f).read_bytes()).hexdigest()[:8]

    # ---- pages
    shell = (SRC / "pages/shell.html").read_text()
    for lang in LANGS:
        other = "en" if lang == "zh" else "zh"
        for page in ["main", "safety"]:
            depth = 1 if page == "main" else 2
            up = "../" * depth
            a = up + "assets/"
            href_main = "index.html" if page == "main" else "../index.html"
            href_safety = "safety/index.html" if page == "main" else "index.html"
            href_lang = up + other + "/" + ("index.html" if page == "main" else "safety/index.html")
            body = (SRC / f"pages/{page}.html").read_text()
            u = ui[lang]
            title_ = u["title"] if page == "main" else f"{u['titleSafety']} · {u['site']}"
            desc = u["dek"] if page == "main" else u["dekSafety"]
            extra = f'<script src="{a}{"papers27.js" if page == "main" else "safety_papers.js"}?v={ver["papers27.js" if page == "main" else "safety_papers.js"]}"></script>'
            html = shell.replace("{{BODY}}", body).replace("{{EXTRA_SCRIPTS}}", extra)
            for f, v in ver.items():  # cache-busting query strings
                html = html.replace(f'{{{{A}}}}{f}"', f'{{{{A}}}}{f}?v={v}"')
            html = html.replace('{{A}}text.{{LANG}}.js"', f'{{{{A}}}}text.{lang}.js?v={ver[f"text.{lang}.js"]}"')
            rep = {"LANG_HTML": "zh-CN" if lang == "zh" else "en", "LANG": lang, "OTHER_LANG": other, "TITLE": title_, "DESC": desc,
                   "A": a, "PAGE": page, "HREF_MAIN": href_main, "HREF_SAFETY": href_safety, "HREF_LANG": href_lang,
                   "ON_MAIN": "on" if page == "main" else "", "ON_SAFETY": "on" if page == "safety" else ""}
            for k, v in rep.items():
                html = html.replace("{{" + k + "}}", v)
            html = re.sub(r"\{\{t:(\w+)\}\}", lambda m: u[m.group(1)], html)
            assert "{{" not in html, re.findall(r"\{\{[^}]*\}\}", html)[:5]
            dst = OUT / lang / ("index.html" if page == "main" else "safety/index.html")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(html)
    (OUT / "index.html").write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ICLR 2027 Submission Atlas</title>
<script>var zh=/^zh/i.test(navigator.language||'');location.replace((zh?'zh':'en')+'/index.html'+location.hash);</script>
</head><body style="font-family:system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem">
<p><a href="zh/index.html">ICLR 2027 投稿图谱（中文）</a></p><p><a href="en/index.html">ICLR 2027 Submission Atlas (English)</a></p>
</body></html>
""")
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"site -> {OUT.relative_to(ROOT)}  {total/1e6:.1f} MB")


if __name__ == "__main__":
    main()
