# Cluster-labelling guide

Each packet lists 50 data-driven topic clusters (TF-IDF + KMeans over all ICLR 2025–2027 submissions). For each cluster you see counts per year,
counts per 10k submissions (the *share* — use this, not raw counts, to judge growth because total submissions grew 11.7k → 19.8k → 43.0k),
top terms, top author keywords and sample titles with OpenReview ids.

Output one JSON object per cluster (a JSON array for the whole packet):
```
{"cluster": 17,
 "name_en": "On-policy distillation for LLMs",           // <= 6 words, concrete, a practitioner's term
 "name_zh": "LLM 在线策略蒸馏",                            // <= 14 Chinese chars
 "theme": "llm_post",                                      // one code from the list below
 "desc_zh": "一句话：这个簇具体在研究什么（30–60字）",
 "trend_zh": "一句话：2026→2027 份额变化背后具体发生了什么（新范式？旧方法退潮？新 benchmark？）。份额基本持平就写'稳定'加一个细节",
 "coherence": 3,                                           // 3 = tight single topic, 2 = mostly coherent, 1 = mixed bag
 "example_ids": ["abc123XYZ0", "..."]                      // 3 ids of the most representative 2027 papers from the samples
}
```

Theme codes:
- `llm_post` LLM 推理与后训练（RL/RLVR、推理、蒸馏、SFT、对齐数据）
- `llm_core` LLM 预训练、架构与高效化（scaling、MoE、注意力/SSM、长上下文、量化、推理加速、tokenizer）
- `agents` 智能体（工具使用、web/GUI/coding agent、多智能体、记忆、自我进化）
- `mm` 多模态理解（VLM/MLLM、视频理解、语音-语言）
- `gen` 生成模型（扩散、flow matching、图像/视频/音频/3D 生成、扩散语言模型）
- `vision` 视觉与 3D 感知（检测分割、3D 重建、NeRF/3DGS、经典 CV 表征）
- `embodied` 具身智能、机器人与世界模型（VLA、操作、自动驾驶、世界模型）
- `rl` 强化学习（非 LLM：理论、离线、多智能体、探索、控制）
- `safety` AI 安全、对齐、隐私、公平与可信
- `interp` 可解释性与模型理解
- `theory` 学习理论与优化
- `struct` 图、时序、概率与因果
- `science` AI for Science（生物、化学、材料、物理、医学、气候）
- `eval` 数据、评测与基准（评测方法论、数据集、LLM-as-judge）
- `repr` 表示学习、迁移、持续/联邦/元学习
- `systems` 系统、基础设施与硬件
- `apps` 其他应用（推荐、语音、代码以外的垂直应用等）

Write in a crisp, specific, non-generic style. Avoid filler like "该领域持续发展". If a cluster looks like a stylistic artefact (e.g. grouped by abstract wording rather than topic) say so in desc_zh and set coherence=1.
