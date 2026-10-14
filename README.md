# ICLR 2027 投稿图谱

ICLR 2027（43,013 篇）与 ICLR 2026 / 2025 投稿的对比分析，重点是细粒度主题变化与 AI Safety。

- 成品：`dashboard/site/`（静态网站，中英双语、两个页面：ICLR 全景 `{zh,en}/index.html` 与 AI Safety 专页 `{zh,en}/safety/index.html`；根目录 `index.html` 按浏览器语言跳转。整个文件夹可直接放到任意静态托管路径下，例如个人主页的 `blogs/trends/iclr-2027/`）
- 可公开数据：`release/`（三年全部投稿 + 细主题 + 安全标注 + 汇总统计，说明见 `release/README.md`，由 `scripts/export_release.py` 生成）
- 流水线：
  1. `scripts/build_corpus.py` — 从公开镜像组装三年投稿（2027：yzc-666/iclr2027-explorer，OpenReview API 快照 2026-10-07；2025/26：papercopilot/paperlists）
  2. `scripts/cluster_topics.py` — TF-IDF + SVD + KMeans 300 个细主题；`work/clusters/labels/` 为 agent 命名
  3. `scripts/concepts.py`、`scripts/macro.py` — 技术雷达、关键词 log-odds、模型/基准、2026 录用信号
  4. `scripts/safety_candidates.py` → 60 个 agent 逐篇标注（`work/safety/`，规范见 `TAXONOMY.md`，校验 `scripts/check_labels.py`）→ `scripts/safety_agg.py`
  5. `scripts/style_anomaly.py` — 2027 模板化写作风格研究；`scripts/robust_shares.py` — 剔除模板化论文后的份额（写入 macro.json / concepts.json）
  6. `work/insights/*.json` — 6 个宏观领域 + 6 个安全子领域深挖、跨子领域综合、核查报告 `qa_report.md`
  7. `scripts/build_dashboard.py` — `dashboard/src/`（`pages/*.html` 页面骨架、`app.js`、`app.css`、`ui.json` 界面文案、`text.json` / `text.en.json` 正文）+ 数据 → `dashboard/site/`。中文章节取自 `work/insights/edited/`，英文取自 `work/insights/en/`（翻译规范 `work/insights/STYLE_GUIDE_EN.md`），细主题英文说明在 `work/clusters/labels_en.json`
