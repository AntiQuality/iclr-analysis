"""Build work/insights/style_dashboard.json (dashboard section) from work/insights/style_anomaly.json.

    python scripts/style_anomaly.py && python scripts/style_dashboard.py
"""
import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INS = ROOT / "work" / "insights"


def pct(x, nd=1):
    return f"{100 * x:.{nd}f}%"


def main():
    r = json.load(open(INS / "style_anomaly.json"))
    corpus = pd.read_parquet(ROOT / "data" / "corpus.parquet", columns=["year", "id", "title"])
    title = {(int(y), i): t for y, i, t in corpus[["year", "id", "title"]].itertuples(index=False)}

    def ev(ids, year=2027):
        return [{"id": i, "year": year, "title": title[(year, i)]} for i in ids]

    sh = r["share_above_threshold"]
    sp = r["share_above_threshold_split_half"]
    ls = r["share_above_threshold_length_stratified"]
    q = r["score_quantiles"]
    nd = r["near_duplicates"]
    lg = r["acceptance_2026_logit"]
    rt = r["rating_2026"]
    sig = r["signals_by_group"]
    s26, hi, lo = sig["2026"], sig["2027 high"], sig["2027 low (<=2026 median)"]
    dec = r["status_by_2027_score_decile"]
    wl = r["watchlist_per_paper"]
    conc = r["new_cluster_concentration"]
    disp = r["marker_dispersion_index"]
    areas = r["by_area"]
    themes = {t["theme"]: t for t in r["by_theme"]}
    named = {c["cluster"]: c for c in r["named_clusters"]}
    topcl = {c["cluster"]: c for c in r["top_clusters_by_share"]}
    ft = r["formulaic_title_by_2027_score_decile"]
    nb = r["high_share_by_2027_submission_number_decile"]
    novel = next(m for m in r["falling_markers"] if m["term"] == "novel")
    ci_lo, ci_hi = math.exp(lg["beta_score_per_sd"] - 1.96 * lg["se"]), math.exp(lg["beta_score_per_sd"] + 1.96 * lg["se"])
    thr = r["threshold"]
    n27 = nd["2027"]["n"]

    out = {
        "title_zh": "2027 年的“程式化文风”：一次全领域的写作语域迁移",
        "intro_zh": [
            f"2027 年投稿的摘要整体换了一种写法：“evidence / held fixed / matched / frozen / the same … / every …”这类强调对照、控制变量与证据边界的措辞大幅上升，"
            f"而 2023–25 年常见的“a novel … approach … significantly …”几乎消失（“novel”出现率从每千篇 {novel['r26']*1000:.0f} 降到 {novel['r27']*1000:.0f}）。"
            f"按 2026 年第 99 百分位定阈值后，2027 年有 {pct(sh['2027'])} 的论文超过阈值（2026 年按构造为 {pct(sh['2026'])}，2025 年 {pct(sh['2025'], 2)}）；"
            f"2027 年的中位数论文（{q['2027']['0.5']:.1f}）已接近 2026 年的第 99 百分位（{thr:.1f}）。这不是少数论文构成的小浪潮，而是整个分布的右移，外加一个更重的尾部。",
            "方法：在摘要的 unigram/bigram 上用 Monroe et al. (2008) 带信息性 Dirichlet 先验的 log-odds 比较 2026→2027，只保留与主题无关的风格/功能词"
            "（在 2027 年 primary area 间分布的 KL < 0.10、剔除手工列出的主题名词、2026 年覆盖率 < 50%、2027/2026 比值 ≥ 2）。取最上升的 40 个标记，"
            "论文分数 = Σ ln(r27/r26) × 1[标记出现在摘要中]。标题不参与打分，用作独立旁证。阈值取 2026 年分数的第 99 百分位；"
            f"用一半数据选词、另一半评估的 split-half 复核得到 {pct(sp['2027'])}，按摘要长度分层定阈值得到 {pct(ls['2027'])}。",
            "该分数度量的是写作语域（register），不是作者身份；它不能、也不被用来判定任何具体论文是否由 AI 生成。",
        ],
        "facts": [
            {"label": "2027 年超过阈值的比例", "value": pct(sh["2027"]),
             "note": f"阈值 = 2026 年第 99 百分位（score > {thr:.2f}）；2025 年 {pct(sh['2025'], 2)}；split-half 复核 {pct(sp['2027'])}"},
            {"label": "“novel” 每千篇出现数", "value": f"{novel['r26']*1000:.0f} → {novel['r27']*1000:.0f}",
             "note": f"2026→2027 的摘要；delve / showcase / comprehensive / intricate 等 2023–25 年典型“LLM 腔”词汇同步下降约 70–90%"},
            {"label": "近重复摘要（TF-IDF cos > 0.8）", "value": pct(nd["2027"]["cos>0.8"]["share_with_dup"], 2),
             "note": f"2027 年 {n27:,} 篇中仅 {nd['2027']['cos>0.8']['pairs']} 对（2026 年 {pct(nd['2026']['cos>0.8']['share_with_dup'], 2)}）；高分论文几乎没有 → 不是模板批量复制"},
            {"label": "2026 年录用 OR（每 1 SD 分数）", "value": f"{lg['odds_ratio_per_sd']:.2f}",
             "note": f"95% CI {ci_lo:.2f}–{ci_hi:.2f}，控制摘要长度与 primary area，n = {lg['n']:,}；与平均评分的 Spearman ρ = {rt['spearman_rho']:.3f}"},
        ],
        "score_hist": {k: r["score_hist_counts"][k] for k in ("bins", "2025", "2026", "2027")},
        "hist_caption_zh": (f"每篇论文的程式化文风分数（每格宽 1，纵轴为论文数）。2025/2026 的分布几乎重合且集中在 0–4；2027 年整体右移，中位数 {q['2027']['0.5']:.1f}，"
                            f"第 90 百分位 {q['2027']['0.9']:.1f}，尾部延伸到近 30。阈值 {thr:.2f}（2026 年第 99 百分位）。分布为单峰，没有分离出一个独立的“第二群体”。"),
        "markers": [{"term": m["term"], "r25": round(m["r25"] * 1000, 1), "r26": round(m["r26"] * 1000, 1), "r27": round(m["r27"] * 1000, 1)}
                    for m in r["markers"][:20]],
        "markers_caption_zh": ("2026→2027 上升最显著的 20 个风格标记（按 Monroe log-odds z 排序，只含与主题无关的功能/风格词），数值为每 1,000 篇摘要中出现该词的论文数。"
                               "这些词在 2025→2026 基本持平，说明这种写法在 2027 年突然出现，而非延续此前的趋势。"),
        "sections": [
            {
                "title_zh": "区分信号：同一种语域，而非复制粘贴",
                "nav": "区分信号",
                "paras_zh": [
                    f"标题不参与打分，但与摘要高度一致：“When does …?”“X Is Not Y”、含 evidence/audit 的标题合计占 2027 年高分论文的 {pct(hi['formulaic_title'])}，"
                    f"2027 年低分论文仅 {pct(lo['formulaic_title'])}，2026 年 {pct(s26['formulaic_title'])}；按 2027 年分数十分位，这一比例从 {pct(ft[0])} 单调升到 {pct(ft[-1])}。",
                    f"高分摘要更长（平均 {hi['abs_words']:.0f} 词，2026 年 {s26['abs_words']:.0f}，2027 年低分 {lo['abs_words']:.0f}），数字更多（{hi['n_numerals']:.1f} 个 vs {s26['n_numerals']:.1f}），"
                    f"含百分比的占 {pct(hi['has_percent'], 0)}（2026 年 {pct(s26['has_percent'], 0)}），关键词更多（{hi['n_kw']:.1f} vs {s26['n_kw']:.1f}），"
                    f"填写 TL;DR 的比例更高（{pct(hi['has_tldr'], 0)} vs 2027 年低分 {pct(lo['has_tldr'], 0)}；2025/26 的数据里没有 TL;DR，无法跨年比较）。"
                    f"分数与摘要长度相关（2027 年 r = {r['score_length_corr']['2027']:.2f}），但按长度分层定阈值后比例仍为 {pct(ls['2027'])}。",
                    f"没有复制粘贴的痕迹：TF-IDF cos > 0.8 的近重复摘要在 2027 年仅 {nd['2027']['cos>0.8']['pairs']} 对（{pct(nd['2027']['cos>0.8']['share_with_dup'], 2)}），"
                    f"与 2025/2026 同量级，高分论文中几乎没有。截至 2026-10-07 的快照里，桌拒率在各分数十分位间平稳（{min(v['desk'] for v in dec.values())*100:.1f}–{max(v['desk'] for v in dec.values())*100:.1f}%），撤稿率同样平稳。"
                    f"在 2026 年，分数与录用（OR {lg['odds_ratio_per_sd']:.2f}/SD）和平均评分（ρ = {rt['spearman_rho']:.3f}）都无关。",
                ],
                "evidence": ev(["0yDuLVVVWn", "lR4zW6Vb8x", "2BvVbECpwS", "wvkbSz7VnD", "hzOkOeFHYG"]),
            },
            {
                "title_zh": "集中在哪里：全领域右移，加上少数“文风簇”",
                "nav": "集中位置",
                "paras_zh": [
                    f"21 个 primary area 在 2026 年都 ≤ 1.6%，到 2027 年全部在 {min(a['share27'] for a in areas)*100:.0f}–{max(a['share27'] for a in areas)*100:.0f}% 之间："
                    f"最高的是可解释性（{pct(areas[0]['share27'], 0)}）、迁移/元学习、基础模型和数据集与基准，最低的是优化、生成模型和图学习。"
                    f"按主题看，评测（eval {pct(themes['eval']['share27'], 0)}）、可解释性（{pct(themes['interp']['share27'], 0)}）、智能体（{pct(themes['agents']['share27'], 0)}）最高，"
                    f"生成模型（{pct(themes['gen']['share27'], 0)}）、强化学习（{pct(themes['rl']['share27'], 0)}）最低。",
                    f"尾部则集中在少数几乎只出现在 2027 年的簇里：簇 70（评测效度审计，{pct(named[70]['share27'], 0)}）、137（审计式模板摘要，{pct(named[137]['share27'], 0)}）、"
                    f"252（RAG 证据选择，{pct(topcl[252]['share27'], 0)}）、196（工具智能体运行时治理，{pct(named[196]['share27'], 0)}）。"
                    f"15 个“新簇”（2025+2026 合计 ≤ 10 篇）占 2027 年论文的 {pct(conc['share_of_2027_in_new_clusters'])}，其中 {pct(conc['high_rate_in_new_clusters'], 0)} 超过阈值（其余簇为 {pct(conc['high_rate_elsewhere'], 0)}）。"
                    f"不过 {pct(1 - conc['share_of_high_2027_in_new_clusters'], 0)} 的高分论文仍落在已有主题簇中。",
                    f"标记在同一篇论文中扎堆出现：按长度分层后，标记计数的方差与“各标记独立出现”时的方差之比在 2026 年为 {disp['2026']:.2f}，2027 年为 {disp['2027']:.2f}。"
                    f"这说明 2027 年的写法存在明显的异质性，有一部分论文几乎“整套”采用这种语域。越晚提交的论文，超过阈值的比例越高（按 submission number 十分位，从 {pct(nb[0], 0)} 升到 {pct(nb[-1], 0)}）。",
                ],
                "evidence": ev(["R1QnIz34Ut", "kRtggxSTIi", "tnpnMhdOiW", "uZENhr0H8D", "22qeQUAXBC", "N67rP3UbVx"]),
            },
            {
                "title_zh": "前后对照：从“推销式”修辞到“对照式”修辞",
                "nav": "词汇对照",
                "paras_zh": [
                    "2025→2026 年上升最多的风格词是“framework that / strong / consistently / achieves / paradigm / enabling / critical / unified”，属于推销式修辞；"
                    "这些词在 2027 年全部回落。2027 年上升的是另一套词：evidence、matched、frozen、held fixed、held-out、rather than、whether、does。"
                    f"多数 2027 年标记在 2025→2026 期间几乎没有变化，只有“these results”和“rather than”提前出现了上升。",
                    f"2023–25 年文献里被用作“LLM 辅助写作”指标的词（delve、intricate、showcase、underscore、pivotal、comprehensive）在 2027 年降到接近零"
                    f"（如 underscore 每千篇 {wl['underscore(s)']['2026']*1000:.0f} → {wl['underscore(s)']['2027']*1000:.0f}，comprehensive {wl['comprehensive']['2026']*1000:.0f} → {wl['comprehensive']['2027']*1000:.0f}）。"
                    "因此，旧的词频式 AI 检测指标在 2027 年会给出“AI 使用下降”的结论，与新语域的出现方向相反。仅凭词频，两者都不能识别作者或工具。",
                    "作为对照，右侧列出几篇随机抽取的 2027 年低分论文（分数不高于 2026 年中位数、摘要 150–250 词）。它们采用常规的“问题背景、现有方法的局限、本文方法”结构，几乎不用对照/证据类措辞。所以 2027 年的写法并非整齐划一。",
                ],
                "evidence": ev([e["id"] for e in r["low_examples"]]),
            },
            {
                "title_zh": "对解读 2026→2027 趋势意味着什么",
                "nav": "如何读趋势",
                "paras_zh": [
                    "主题聚类部分受到措辞影响：coherence = 1 的簇（如 137、83、15）以及簇 70、196、252 里超过阈值的比例都在 68–93%，而且这些簇在 2025/26 年几乎没有论文。"
                    "它们的“爆发式增长”应理解为“一种写法 + 若干相近话题”的混合，不宜直接解读为研究方向的兴起。",
                    "主题层面的结论（如评测、智能体治理、可解释性的增长）需要做稳健性检验：只用 keywords 重新计数、在嵌入前去掉标记词，或剔除高分论文后再看增速。"
                    "反过来，“novel / significantly”等词的消失也会让基于摘要关键词的计数系统性偏低。",
                    "这种写法与 2026 年的录用和评分都无关，所以它本身不能作为论文质量的代理指标。2027 年的评审结果出来之前，也无法判断评审是否会对它作出反应。",
                ],
                "evidence": ev(["2BvVbECpwS", "qd4q2OE0OE", "28hXY8kEKI", "Cja2oEWHhS"]),
            },
        ],
        "examples": [{"id": e["id"], "title": e["title"], "score": e["score"]} for e in r["examples"]],
        "caveat_zh": ("数据层面能确认的只有三点：2027 年摘要与标题的措辞发生了大规模、跨领域的语域迁移；这种迁移在部分新簇中最集中；它不表现为文本重复，也与 2026 年的录用和评分无关。"
                      "它的来源无法从元数据中确定。新一代写作助手的默认文风、自动化研究流水线、社区对“去推销化”写作的规范变化，以及 2027 年新增的 AI 使用声明与 20 篇投稿上限（本数据没有声明内容和作者信息），都与观察结果相容。"
                      "分数只度量措辞，不度量作者身份，不能、也不应用来判定任何具体论文由 AI 生成；示例论文仅代表措辞上的典型，不代表其来源。2027 年数据是 2026-10-07 的评审前快照，桌拒/撤稿率与 2025/26 的最终状态不可比。"),
    }
    json.dump(out, open(INS / "style_dashboard.json", "w"), ensure_ascii=False, indent=1)
    print("wrote", INS / "style_dashboard.json")


if __name__ == "__main__":
    main()
