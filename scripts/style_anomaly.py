"""Stylistic / production-mode anomaly in ICLR 2027 submissions.

    python scripts/style_anomaly.py            # writes work/insights/style_anomaly.json (+ _detail.json, _papers.parquet)

Steps
 1. Lexical markers: unigrams+bigrams of the ABSTRACT (titles handled separately as templates).
    Ranking = Monroe, Colaresi & Quinn (2008) log-odds ratio with informative Dirichlet prior
    (prior alpha_w = 0.01 * pooled 2025-27 token count of w), z-scored; reported with per-paper (document) rates.
    Restricted to style/function vocabulary:
      - topic-neutral: KL(term's 2027 primary-area distribution || overall 2027 area distribution) < 0.10 nats
      - not a topic/content noun (hand list TOPIC_NOUNS below, applied after the automatic filters)
      - per-paper rate in 2026 < 0.5 (saturated function words such as "the" carry no per-paper signal)
      - support: rising markers need r27 >= 2% and r27/r26 >= 2 ; falling markers need r26 >= 2% and r26/r27 >= 2
      - bigram/unigram de-duplication (drop a bigram whose component unigram is already selected and
        covers >= 80% of its 2027 papers, and vice versa)
 2. Formulaic-style score = sum over the top-40 rising markers of ln(r27/r26) * 1[marker in abstract].
    Threshold = 99th percentile of 2026 scores (so <= 1% of 2026 papers exceed it).
    Robustness: (a) split-half - markers/weights learned on a random half, evaluated on the other half;
    (b) length-stratified thresholds (abstract-length quintiles).
 3. Separating signals: title templates, abstract structure, keyword count, TL;DR (2027 only - absent in
    2025/26 data), near-duplicate abstracts (TF-IDF cosine > 0.8), snapshot status (2027), acceptance (2026).
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore", message="This pattern is interpreted as a regular expression")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work" / "insights"
OUT.mkdir(parents=True, exist_ok=True)
YEARS = (2025, 2026, 2027)
RNG = np.random.default_rng(0)
N_MARKERS = 40
KL_MAX = 0.10

# content/topic nouns that pass the automatic topic-neutrality filter but are subject matter, not style.
TOPIC_NOUNS = set("""
trajectories trajectory routing interface repair context task tasks teacher student agent agents action actions
execution answer answers response responses interaction interactions coverage decision decisions rule rules source
sources residual recovery correction score scores error errors baseline baselines state states candidate candidates
budget budgets target targets reference references selection learned local failure failures cost costs observations
observation mean policy policies reward rewards memory tool tools retrieval prompt prompts token tokens layer layers
attention feature features signal signals label labels query queries user users verifier verifiers trace traces
step steps loss gradient gradients update updates sample samples noise distribution distributions estimator estimate
estimates objective objectives constraint constraints weight weights head heads expert experts domain domains
instance instances example examples input inputs output outputs graph graphs node nodes image images video text
language code program programs proof proofs environment environments
""".split())

TITLE_TEMPLATES = {
    "question title (contains ?)": r"\?",
    "When does/do/is/are/can ...": r"(?i)\bwhen (does|do|is|are|can|should)\b",
    "starts with When/What": r"(?i)^(when|what)\b",
    "X Is/Are Not Y": r"(?i)\b(is|are) not\b",
    "contains 'Not' (contrastive)": r"(?i)\bnot\b",
    "Beyond ...": r"(?i)\bbeyond\b",
    "audit/auditing": r"(?i)\baudit",
    "evidence": r"(?i)\bevidence",
    "X Hides/Fails/Breaks/Matters/Collapses": r"(?i)\b(hides?|fails?|breaks?|matters?|collapses?|misses)\b",
    "preserve/preserving": r"(?i)\bpreserv",
    "under ...": r"(?i)\bunder\b",
    "ALL-CAPS title": None,
    "Towards ...": r"(?i)^towards?\b",
}
WATCHLIST = {
    "held fixed / holding ... fixed": r"\bheld fixed\b|\bhold(ing)? [a-z\- ]{0,30}fixed\b|\bkept fixed\b",
    "paired": r"\bpaired\b", "matched": r"\bmatched\b", "exact/exactly": r"\bexact(ly)?\b",
    "certified/certify/certificate": r"\bcertif", "pre-registration / preregistered": r"\bpre-?regist",
    "audit/auditing": r"\baudit", "evidence": r"\bevidence\b", "same ... budget/backbone/compute": r"\bsame [a-z\- ]{0,20}(budget|backbone|compute|model|data)\b",
    "frozen": r"\bfrozen\b", "confound": r"\bconfound", "held-out": r"\bheld[- ]out\b",
    "is not / are not": r"\b(is|are) not\b", "rather than": r"\brather than\b",
    # classic 2023-25 LLM-associated vocabulary (Liang et al. 2024; Kobak et al. 2024)
    "delve/delves": r"\bdelv(e|es|ing)\b", "intricate": r"\bintricate\b", "pivotal": r"\bpivotal\b",
    "showcase/showcasing": r"\bshowcas", "underscore(s)": r"\bunderscor", "notably": r"\bnotably\b",
    "comprehensive": r"\bcomprehensive\b", "novel": r"\bnovel\b", "seamless(ly)": r"\bseamless",
}
FORMULAIC_TITLE_KEYS = ["When does/do/is/are/can ...", "starts with When/What", "X Is/Are Not Y", "audit/auditing",
                        "evidence", "X Hides/Fails/Breaks/Matters/Collapses"]


def monroe_z(ya, yb, prior):
    """Monroe et al. 2008, eq. 22: log-odds ratio with informative Dirichlet prior, divided by its s.d."""
    a0 = prior.sum()
    na, nb = ya.sum(), yb.sum()
    da = np.log((ya + prior) / (na + a0 - ya - prior))
    db = np.log((yb + prior) / (nb + a0 - yb - prior))
    return (da - db) / np.sqrt(1.0 / (ya + prior) + 1.0 / (yb + prior))


def build_counts(text):
    cv = CountVectorizer(ngram_range=(1, 2), min_df=30, lowercase=True,
                         token_pattern=r"(?u)\b[a-z][a-z\-]*[a-z]\b|\b[a-z]\b")
    X = cv.fit_transform(text).tocsr()
    return X, np.array(cv.get_feature_names_out())


def marker_table(X, terms, yr, area, mask=None):
    """Return per-term table of rates, Monroe z (27 vs 26, 26 vs 25), area-KL."""
    if mask is None:
        mask = np.ones(len(yr), bool)
    B = X.copy()
    B.data[:] = 1
    c, r, n = {}, {}, {}
    for y in YEARS:
        m = mask & (yr == y)
        c[y] = np.asarray(X[m].sum(0)).ravel().astype(float)
        r[y] = np.asarray(B[m].sum(0)).ravel() / m.sum()
        n[y] = m.sum()
    prior = 0.01 * (c[2025] + c[2026] + c[2027])
    z76 = monroe_z(c[2027], c[2026], prior)
    z65 = monroe_z(c[2026], c[2025], prior)
    m27 = mask & (yr == 2027)
    cats = pd.Categorical(area[m27])
    P = sp.csr_matrix((np.ones(m27.sum()), (cats.codes, np.arange(m27.sum()))), shape=(len(cats.categories), m27.sum()))
    TA = np.asarray((P @ B[m27]).todense()).T + 0.5
    TA = TA / TA.sum(1, keepdims=True)
    base = np.bincount(cats.codes, minlength=len(cats.categories)) / m27.sum()
    kl = (TA * np.log(TA / base)).sum(1)
    eps = 0.5
    t = pd.DataFrame(dict(term=terms, z76=z76, z65=z65, r25=r[2025], r26=r[2026], r27=r[2027], kl=kl))
    t["ratio76"] = (t.r27 * n[2027] + eps) / (n[2027] + eps) / ((t.r26 * n[2026] + eps) / (n[2026] + eps))
    t["ratio65"] = (t.r26 * n[2026] + eps) / (n[2026] + eps) / ((t.r25 * n[2025] + eps) / (n[2025] + eps))
    t["col"] = np.arange(len(t))
    return t


def is_style(term):
    toks = term.split()
    return not any(tok in TOPIC_NOUNS for tok in toks) and not any(ch.isdigit() for ch in term)


def dedupe(sel):
    """Drop bigrams redundant with a selected unigram (or unigrams redundant with a selected bigram)."""
    keep = []
    for _, row in sel.iterrows():
        redundant = False
        for k in keep:
            a, b = row.term.split(), k.term.split()
            if set(a) & set(b) and (len(a) != len(b)):
                small, big = (row, k) if len(a) < len(b) else (k, row)
                if big.r27 >= 0.8 * small.r27:
                    redundant = True
            if redundant:
                break
        if not redundant:
            keep.append(row)
    return pd.DataFrame(keep)


def select_markers(t, rising=True, k=N_MARKERS):
    base = (t.kl < KL_MAX) & (t.r26 < 0.5) & t.term.map(is_style)
    if rising:
        s = t[base & (t.r27 >= 0.02) & (t.ratio76 >= 2)].sort_values("z76", ascending=False)
    else:
        s = t[base & (t.r26 >= 0.02) & (1 / t.ratio76 >= 2)].sort_values("z76", ascending=True)
    s = dedupe(s.head(3 * k))
    return s.head(k).copy()


def doc_score(B, markers):
    w = np.log(markers.ratio76.values)
    return np.asarray(B[:, markers.col.values] @ w).ravel(), np.asarray(B[:, markers.col.values].sum(1)).ravel()


def near_dup_flags(abstracts, idx_sets, thrs=(0.6, 0.7, 0.8), chunk=1500):
    """For each index set (one corpus-year or subsample), flag docs with >=1 other doc at TF-IDF cosine > thr."""
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, min_df=2, max_df=0.5)
    vec.fit(abstracts)
    res = {}
    for name, idx in idx_sets.items():
        X = vec.transform(abstracts[idx]).tocsr()
        flags = {t: np.zeros(len(idx), bool) for t in thrs}
        npairs = {t: 0 for t in thrs}
        XT = X.T.tocsc()
        for s in range(0, X.shape[0], chunk):
            S = (X[s:s + chunk] @ XT).tocoo()
            for t in thrs:
                keep = (S.data > t) & (S.row + s != S.col)
                rows, cols = S.row[keep] + s, S.col[keep]
                flags[t][rows] = True
                flags[t][cols] = True
                npairs[t] += int((rows < cols).sum())
        res[name] = (idx, flags, npairs)
    return res


def logit_with_se(Xm, y):
    lr = LogisticRegression(C=1e6, max_iter=5000).fit(Xm, y)
    Xd = np.column_stack([np.ones(len(Xm)), Xm])
    p = lr.predict_proba(Xm)[:, 1]
    H = (Xd * (p * (1 - p))[:, None]).T @ Xd
    se = np.sqrt(np.diag(np.linalg.pinv(H)))
    return np.r_[lr.intercept_, lr.coef_.ravel()], se


NOTES = ("score = sum over 40 rising style markers (abstract only) of ln(r27/r26) * presence; threshold = 2026 p99. "
         "Markers ranked by Monroe et al. (2008) log-odds z (2026->2027, informative Dirichlet prior = 1% of pooled counts), "
         "restricted to topic-neutral terms (primary-area KL < 0.10), non-topic nouns, r26 < 0.5, r27/r26 >= 2. "
         "2027 is a pre-review snapshot (status active/withdrawn/desk_rejected as of 2026-10-07), so its desk/withdraw rates are not "
         "comparable with final 2025/26 rates. TL;DR is empty for 2025/26 in this corpus; rating (mean reviewer score) exists for 2025/26 only (2027 is pre-review). "
         "The score measures a writing register, NOT authorship; it must not be read as AI-detection.")


def main():
    d = pd.read_parquet(ROOT / "data" / "corpus.parquet")
    cl = pd.read_parquet(ROOT / "data" / "clusters.parquet")
    d = d.merge(cl, on=["year", "id"], how="left").reset_index(drop=True)
    labels = []
    for f in sorted((ROOT / "work" / "clusters" / "labels").glob("g*.json")):
        labels += json.load(open(f))
    lab = pd.DataFrame(labels)[["cluster", "name_en", "theme", "coherence"]]
    d = d.merge(lab, on="cluster", how="left")
    yr = d.year.values
    abstract = d.abstract.fillna("").str.lower()

    # ---------------- 1. markers ----------------
    X, terms = build_counts(abstract)
    B = X.copy()
    B.data[:] = 1
    t = marker_table(X, terms, yr, d.primary_area.values)
    rising = select_markers(t, True)
    falling = select_markers(t, False, 25)
    print("rising markers\n", rising[["term", "z76", "z65", "r25", "r26", "r27", "ratio76", "kl"]].round(3).to_string())
    print("falling markers\n", falling[["term", "z76", "z65", "r25", "r26", "r27", "ratio76", "kl"]].round(3).to_string())
    unfiltered_top = t[(t.r27 >= 0.02)].sort_values("z76", ascending=False).head(25)
    # same filters, but for the earlier transition 2025 -> 2026 (does the 2027 register already start in 2026?)
    base65 = (t.kl < KL_MAX) & (t.r26 < 0.5) & t.term.map(is_style)
    rising65 = dedupe(t[base65 & (t.r26 >= 0.02) & (t.ratio65 >= 1.5)].sort_values("z65", ascending=False).head(60)).head(20)
    print("rising 2025->2026\n", rising65[["term", "z65", "z76", "r25", "r26", "r27"]].round(3).to_string())
    # watch-list: phrases named in the observation + classic 2023-25 "LLM-ese" words (title OR abstract, per paper)
    ta = (d.title.fillna("") + " . " + d.abstract.fillna("")).str.lower()
    watch = {}
    for k, pat in WATCHLIST.items():
        hit = ta.str.contains(pat, regex=True)
        watch[k] = {int(y): float(hit[yr == y].mean()) for y in YEARS}
    watch = pd.DataFrame(watch).T
    print("watch-list per paper\n", (watch * 1000).round(1).to_string())

    # title templates
    title = d.title.fillna("").str.strip()
    TT = pd.DataFrame(index=d.index)
    for k, pat in TITLE_TEMPLATES.items():
        if pat is None:
            TT[k] = title.map(lambda s: sum(c.isalpha() for c in s) > 10 and s.upper() == s)
        else:
            TT[k] = title.str.contains(pat, regex=True)
    tt_rates = TT.groupby(yr).mean().T
    d["formulaic_title"] = TT[FORMULAIC_TITLE_KEYS].any(axis=1)

    # ---------------- 2. score ----------------
    d["score"], d["n_markers"] = doc_score(B, rising)
    thr = float(np.quantile(d.score[yr == 2026], 0.99))
    d["high"] = d.score > thr
    share = {int(y): float(d.high[yr == y].mean()) for y in YEARS}
    q = d.groupby("year").score.quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.99]).unstack().round(2)
    print("threshold", thr, "share", share, "\nquantiles\n", q)
    # tail vs shift: share of each year above 2026 quantiles
    tails = {}
    for qq in (0.5, 0.9, 0.99, 0.999):
        v = np.quantile(d.score[yr == 2026], qq)
        tails[str(qq)] = {int(y): float((d.score[yr == y] > v).mean()) for y in YEARS}
    print("share above 2026 quantiles", tails)

    # legacy (falling) index
    d["legacy"], _ = doc_score(B, falling)
    d["legacy_any"] = np.asarray(B[:, falling.col.values].sum(1)).ravel() > 0
    legacy_any = d.groupby("year").legacy_any.mean().round(3).to_dict()

    # histogram
    bins = np.arange(0, np.ceil(d.score.max()) + 1, 1.0)
    hist = {"bins": bins.tolist()}
    hist_counts = {"bins": bins.tolist()}
    for y in YEARS:
        h, _ = np.histogram(d.score[yr == y], bins=bins)
        hist[str(y)] = (h / h.sum()).round(5).tolist()
        hist_counts[str(y)] = h.astype(int).tolist()

    # length
    d["abs_words"] = d.abstract.fillna("").str.split().str.len()
    corr_len = {int(y): float(np.corrcoef(d.score[yr == y], d.abs_words[yr == y])[0, 1]) for y in YEARS}
    d["lenq"] = pd.qcut(d.abs_words.where(yr == 2026), 5, labels=False, retbins=False)
    edges = np.quantile(d.abs_words[yr == 2026], [0, .2, .4, .6, .8, 1])
    edges[0], edges[-1] = -1, 1e9
    d["lenq"] = pd.cut(d.abs_words, edges, labels=False)
    thr_len = d[yr == 2026].groupby("lenq").score.quantile(0.99)
    d["high_lenadj"] = d.score > d.lenq.map(thr_len)
    share_lenadj = {int(y): float(d.high_lenadj[yr == y].mean()) for y in YEARS}
    print("length corr", corr_len, "length-stratified share", share_lenadj)

    # marker co-occurrence: variance of marker count vs. independent-marker (Poisson-binomial) variance,
    # within 2026-defined abstract-length quintiles. >1 = markers cluster in the same papers.
    Bm = B[:, rising.col.values]
    disp = {}
    for y in YEARS:
        vals = []
        for qb in range(5):
            m = (yr == y) & (d.lenq.values == qb)
            p_ = np.asarray(Bm[m].mean(0)).ravel()
            cnt_ = np.asarray(Bm[m].sum(1)).ravel()
            vals.append(cnt_.var() / (p_ * (1 - p_)).sum())
        disp[int(y)] = float(np.mean(vals))
    print("dispersion index (length-stratified)", disp)

    # split-half validation
    half = RNG.random(len(d)) < 0.5
    tA = marker_table(X, terms, yr, d.primary_area.values, mask=half)
    rA = select_markers(tA, True)
    sB, _ = doc_score(B, rA)
    thrB = np.quantile(sB[~half & (yr == 2026)], 0.99)
    split = {int(y): float((sB[~half & (yr == y)] > thrB).mean()) for y in YEARS}
    overlap = len(set(rA.term) & set(rising.term))
    print("split-half", split, "marker overlap", overlap)

    # by area
    by_area = (d[yr >= 2026].groupby(["primary_area", "year"]).high.mean().unstack()
               .rename(columns={2026: "share26", 2027: "share27"}))
    by_area["n27"] = d[yr == 2027].groupby("primary_area").size()
    by_area = by_area.sort_values("share27", ascending=False)
    print(by_area.round(3).to_string())

    # by theme / cluster (2027)
    d27 = d[yr == 2027]
    by_theme = d27.groupby(d27.theme.fillna("(unlabelled)")).agg(n=("high", "size"), share27=("high", "mean"),
                                                                  mean_score=("score", "mean")).sort_values("share27", ascending=False)
    print(by_theme.round(3).to_string())
    cs = pd.read_csv(ROOT / "work" / "clusters" / "clusters_summary.csv")
    by_cl = d27.groupby("cluster").agg(n27=("high", "size"), share27=("high", "mean"), mean_score=("score", "mean"))
    by_cl = by_cl.join(cs.set_index("cluster")[["n25", "n26", "growth"]]).join(lab.set_index("cluster")[["name_en", "theme", "coherence"]])
    named = by_cl.loc[[137, 70, 83, 15, 33, 196]]
    print(named.round(3).to_string())
    top_cl = by_cl[by_cl.n27 >= 50].sort_values("share27", ascending=False).head(15)
    print(top_cl.round(3).to_string())
    # concentration: high-score 2027 papers in "new" clusters (<=10 papers in 2025+2026)
    new_cl = set(cs.cluster[(cs.n25 + cs.n26) <= 10])
    d27new = d27.cluster.isin(new_cl)
    conc = {"n_new_clusters": len(new_cl),
            "share_of_2027_in_new_clusters": float(d27new.mean()),
            "share_of_high_2027_in_new_clusters": float(d27new[d27.high].mean()),
            "high_rate_in_new_clusters": float(d27.high[d27new].mean()),
            "high_rate_elsewhere": float(d27.high[~d27new].mean())}
    print(conc)
    # coherence=1 (stylistic) clusters
    coh = d27.groupby(d27.coherence.fillna(-1)).high.agg(["size", "mean"])
    print(coh)

    # ---------------- 3. separating signals ----------------
    ab = d.abstract.fillna("")
    d["n_sent"] = ab.str.count(r"[.!?](\s+|$)").clip(lower=1)
    d["words_per_sent"] = d.abs_words / d.n_sent
    d["n_numerals"] = ab.str.count(r"\b\d[\d.,]*\b")
    d["has_percent"] = ab.str.contains(r"%|percent|percentage point")
    d["has_we"] = ab.str.contains(r"\b[Ww]e\b")
    d["n_kw"] = d.keywords.map(len)
    d["title_words"] = title.str.split().str.len()
    d["has_tldr"] = d.tldr.fillna("").str.len() > 0
    d["has_colon_title"] = title.str.contains(":")
    d["allcaps_title"] = TT["ALL-CAPS title"]
    d["desk_rejected"] = d.status.eq("desk_rejected")
    d["withdrawn"] = d.status.eq("withdrawn")
    med26 = np.median(d.score[yr == 2026])
    d["grp"] = np.where(yr != 2027, d.year.astype(str), np.where(d.high, "2027 high", np.where(d.score <= med26, "2027 low (<=2026 median)", "2027 mid")))
    sig_cols = ["abs_words", "n_sent", "words_per_sent", "n_numerals", "has_percent", "has_we", "n_kw", "title_words",
                "has_colon_title", "allcaps_title", "formulaic_title", "has_tldr", "legacy_any", "desk_rejected", "withdrawn"]
    agg = {c: "mean" for c in sig_cols}
    d["grp2"] = np.where(yr == 2027, "2027 all", "")
    sig_all = d[yr == 2027][sig_cols].mean().to_frame("2027 all").T
    sig_all.insert(0, "n", int((yr == 2027).sum()))
    signals = d.groupby("grp").agg(n=("id", "size"), **{c: (c, "mean") for c in sig_cols})
    signals["abs_words_median"] = d.groupby("grp").abs_words.median()
    signals["submission_number_median"] = d.groupby("grp").number.median()
    sig_all["abs_words_median"] = d.abs_words[yr == 2027].median()
    sig_all["submission_number_median"] = d.number[yr == 2027].median()
    signals = pd.concat([signals, sig_all])
    print(signals.round(3).T.to_string())

    d27 = d[yr == 2027]
    # formulaic titles vs score within 2027 (title is NOT part of score -> partly independent check)
    ft = d27.groupby(pd.qcut(d27.score.rank(method="first"), 10, labels=False)).formulaic_title.mean()
    print("formulaic title share by 2027 score decile", ft.round(3).tolist())

    # submission number vs score (2027): order of submission
    nb = d27.groupby(pd.qcut(d27.number, 10, labels=False)).high.mean()
    print("high share by submission-number decile", nb.round(3).tolist())

    # status in 2027 by score decile & logistic (desk reject)
    dec27 = d27.groupby(pd.qcut(d27.score.rank(method="first"), 10, labels=False)).agg(
        desk=("desk_rejected", "mean"), wd=("withdrawn", "mean"), mean_score=("score", "mean"))
    print(dec27.round(4).to_string())

    # near-duplicates
    idx26 = np.where(yr == 2026)[0]
    idx27 = np.where(yr == 2027)[0]
    idx27s = np.sort(RNG.choice(idx27, size=len(idx26), replace=False))
    idx25 = np.where(yr == 2025)[0]
    d["near_dup"] = False
    nd = near_dup_flags(d.abstract.fillna("").values, {"2025": idx25, "2026": idx26, "2027": idx27, "2027_sub": idx27s})
    near = {}
    for k, (idx, flags, npairs) in nd.items():
        hi = d.high.values[idx]
        near[k] = {"n": int(len(idx))}
        for t, flag in flags.items():
            near[k][f"cos>{t}"] = {"pairs": npairs[t], "share_with_dup": float(flag.mean()),
                                   "share_with_dup_high": float(flag[hi].mean()) if hi.any() else None,
                                   "share_with_dup_nonhigh": float(flag[~hi].mean())}
        if k in ("2025", "2026", "2027"):
            d.loc[idx, "near_dup"] = flags[0.8]
    print("near-dup", json.dumps(near, indent=1))
    d27 = d[yr == 2027]
    ex_pairs = d27[d27.near_dup.astype(bool)]
    nd_status = ex_pairs.status.value_counts().to_dict()
    print("2027 near-dup (cos>0.8) status counts", nd_status)
    for r in ex_pairs.sort_values("title").itertuples():
        print("   ", r.id, r.status, round(r.score, 1), r.title[:90])

    # 2026 acceptance vs score
    d26 = d[yr == 2026].copy()
    dec26 = d26.groupby(pd.qcut(d26.score.rank(method="first"), 10, labels=False)).agg(
        mean_score=("score", "mean"), accept=("accepted", "mean"), withdrawn=("withdrawn", "mean"), desk=("desk_rejected", "mean"))
    print(dec26.round(3).to_string())
    acc_high = {"high": float(d26.accepted[d26.high].mean()), "rest": float(d26.accepted[~d26.high].mean()), "n_high": int(d26.high.sum())}
    nonwd = d26[~d26.withdrawn & ~d26.desk_rejected]
    acc_high["high_nonwithdrawn"] = float(nonwd.accepted[nonwd.high].mean())
    acc_high["rest_nonwithdrawn"] = float(nonwd.accepted[~nonwd.high].mean())
    # logistic: accepted ~ z(score) + log(abstract words) + area FE  (among reviewed papers)
    A = pd.get_dummies(nonwd.primary_area, drop_first=True).astype(float).values
    zs = (nonwd.score - nonwd.score.mean()) / nonwd.score.std()
    Xm = np.column_stack([zs, np.log(nonwd.abs_words.clip(lower=10)), A])
    coef, se = logit_with_se(Xm, nonwd.accepted.astype(int).values)
    logit = {"beta_score_per_sd": float(coef[1]), "se": float(se[1]), "odds_ratio_per_sd": float(np.exp(coef[1])),
             "n": int(len(nonwd)), "controls": "log abstract length + primary-area fixed effects; desk-rejected/withdrawn excluded"}
    print("2026 acceptance", acc_high, logit)
    # same for the legacy index
    zl = (nonwd.legacy - nonwd.legacy.mean()) / nonwd.legacy.std()
    coefL, seL = logit_with_se(np.column_stack([zl, np.log(nonwd.abs_words.clip(lower=10)), A]), nonwd.accepted.astype(int).values)
    logit_legacy = {"beta_per_sd": float(coefL[1]), "se": float(seL[1])}
    print("legacy index logit", logit_legacy)

    # 2026 rating vs score (reviewed papers with a rating)
    from scipy.stats import spearmanr
    rr = nonwd[nonwd.rating.notna()]
    rho, prho = spearmanr(rr.score, rr.rating)
    Ar = pd.get_dummies(rr.primary_area, drop_first=True).astype(float).values
    zr = (rr.score - rr.score.mean()) / rr.score.std()
    Xr = np.column_stack([np.ones(len(rr)), zr, np.log(rr.abs_words.clip(lower=10)), Ar])
    bet, *_ = np.linalg.lstsq(Xr, rr.rating.values, rcond=None)
    res_ = rr.rating.values - Xr @ bet
    cov = np.linalg.pinv(Xr.T @ Xr) * (res_ @ res_) / (len(rr) - Xr.shape[1])
    rating = {"spearman_rho": float(rho), "p": float(prho), "n": int(len(rr)),
              "ols_rating_per_sd_score": float(bet[1]), "se": float(np.sqrt(cov[1, 1])),
              "mean_rating_high": float(rr.rating[rr.high].mean()), "mean_rating_rest": float(rr.rating[~rr.high].mean()),
              "n_high": int(rr.high.sum()),
              "by_decile": rr.groupby(pd.qcut(rr.score.rank(method="first"), 10, labels=False)).rating.mean().round(3).tolist(),
              "controls": "OLS: log abstract length + primary-area FE; withdrawn/desk-rejected excluded"}
    print("2026 rating", rating)

    # ---------------- 4. examples ----------------
    top = d27.sort_values("score", ascending=False).head(12)
    low_pool = d27[(d27.score <= med26) & (d27.abs_words.between(150, 250))]
    low = low_pool.sample(5, random_state=1)
    for name, df_ in [("TOP", top), ("LOW", low)]:
        print(name)
        for _, r in df_.iterrows():
            print(f"  {r.id}  {r.score:.2f}  n={r.n_markers}  [{r.status}]  c{r.cluster} {r.title[:110]}")

    # ---------------- write ----------------
    def mk(df_):
        return [{"term": r.term, "r25": round(r.r25, 4), "r26": round(r.r26, 4), "r27": round(r.r27, 4),
                 "z_26to27": round(r.z76, 1), "z_25to26": round(r.z65, 1), "weight": round(float(np.log(r.ratio76)), 3),
                 "area_kl": round(r.kl, 3)} for r in df_.itertuples()]
    res = {
        "markers": mk(rising),
        "falling_markers": mk(falling),
        "title_templates": [{"template": k, "r25": round(v[2025], 4), "r26": round(v[2026], 4), "r27": round(v[2027], 4)}
                            for k, v in tt_rates.iterrows()],
        "score_hist": hist,
        "score_quantiles": {int(y): q.loc[y].to_dict() for y in YEARS},
        "threshold": round(thr, 3),
        "share_above_threshold": share,
        "share_above_2026_quantiles": tails,
        "share_above_threshold_length_stratified": share_lenadj,
        "share_above_threshold_split_half": split,
        "split_half_marker_overlap": overlap,
        "marker_dispersion_index": disp,
        "score_length_corr": corr_len,
        "legacy_marker_any_share": {int(k): v for k, v in legacy_any.items()},
        "by_area": [{"area": a, "share27": round(r.share27, 4), "share26": round(r.share26, 4), "n27": int(r.n27)}
                    for a, r in by_area.iterrows()],
        "by_theme": [{"theme": a, "n27": int(r.n), "share27": round(r.share27, 4), "mean_score": round(r.mean_score, 3)}
                     for a, r in by_theme.iterrows()],
        "named_clusters": [{"cluster": int(c), "name_en": r.name_en, "n25": int(r.n25), "n26": int(r.n26), "n27": int(r.n27),
                            "share27": round(r.share27, 3), "mean_score": round(r.mean_score, 2)} for c, r in named.iterrows()],
        "top_clusters_by_share": [{"cluster": int(c), "name_en": r.name_en if isinstance(r.name_en, str) else None,
                                   "n26": int(r.n26), "n27": int(r.n27), "share27": round(r.share27, 3)} for c, r in top_cl.iterrows()],
        "new_cluster_concentration": conc,
        "signals_by_group": json.loads(signals.round(4).to_json(orient="index")),
        "formulaic_title_by_2027_score_decile": ft.round(4).tolist(),
        "high_share_by_2027_submission_number_decile": nb.round(4).tolist(),
        "status_by_2027_score_decile": json.loads(dec27.round(4).to_json(orient="index")),
        "near_duplicates": near,
        "near_dup_2027_status_mix": nd_status,
        "acceptance_2026_by_score_decile": json.loads(dec26.round(4).to_json(orient="index")),
        "acceptance_2026_high_vs_rest": acc_high,
        "acceptance_2026_logit": logit,
        "acceptance_2026_logit_legacy_index": logit_legacy,
        "rating_2026": rating,
        "rising_markers_2025_to_2026": [{"term": r.term, "r25": round(r.r25, 4), "r26": round(r.r26, 4), "r27": round(r.r27, 4),
                                         "z_25to26": round(r.z65, 1), "z_26to27": round(r.z76, 1)} for r in rising65.itertuples()],
        "watchlist_per_paper": {k: {int(y): round(v, 5) for y, v in row.items()} for k, row in watch.iterrows()},
        "score_hist_counts": hist_counts,
        "unfiltered_top_rising": [{"term": r.term, "r26": round(r.r26, 4), "r27": round(r.r27, 4), "z": round(r.z76, 1)}
                                  for r in unfiltered_top.itertuples()],
        "examples": [{"id": r.id, "title": r.title, "score": round(r.score, 2), "n_markers": int(r.n_markers),
                      "status": r.status, "cluster": int(r.cluster)} for r in top.itertuples()],
        "low_examples": [{"id": r.id, "title": r.title, "score": round(r.score, 2), "n_markers": int(r.n_markers),
                          "status": r.status, "cluster": int(r.cluster)} for r in low.itertuples()],
    }
    res["notes"] = NOTES
    json.dump(res, open(OUT / "style_anomaly.json", "w"), indent=1, ensure_ascii=False, default=float)
    d[["year", "id", "title", "primary_area", "status", "cluster", "score", "n_markers", "high", "legacy", "abs_words",
       "formulaic_title", "near_dup", "n_kw", "has_tldr"]].to_parquet(OUT / "style_anomaly_papers.parquet", index=False)


if __name__ == "__main__":
    main()
