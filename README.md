# ICLR 2027 投稿图谱

ICLR 2027（43,013 篇）与 ICLR 2026 / 2025 投稿的对比分析，重点是细粒度主题变化与 AI Safety。

- 成品：`dashboard/index.html`（单文件，直接用浏览器打开）
- 流水线：
  1. `scripts/build_corpus.py` — 从公开镜像组装三年投稿（2027：yzc-666/iclr2027-explorer，OpenReview API 快照 2026-10-07；2025/26：papercopilot/paperlists）
  2. `scripts/cluster_topics.py` — TF-IDF + SVD + KMeans 300 个细主题；`work/clusters/labels/` 为 agent 命名
  3. `scripts/concepts.py`、`scripts/macro.py` — 技术雷达、关键词 log-odds、模型/基准、2026 录用信号
  4. `scripts/safety_candidates.py` → 60 个 agent 逐篇标注（`work/safety/`，规范见 `TAXONOMY.md`，校验 `scripts/check_labels.py`）→ `scripts/safety_agg.py`
  5. `scripts/style_anomaly.py` — 2027 模板化写作风格研究，及剔除后的稳健份额
  6. `work/insights/*.json` — 6 个宏观领域 + 6 个安全子领域深挖、跨子领域综合、核查报告 `qa_report.md`
  7. `scripts/build_dashboard.py` — 组装 `dashboard/src/template.html` + 数据 → `dashboard/index.html`
