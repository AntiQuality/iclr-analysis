# English edition: translation and style guide

The dashboard ships in Chinese and English. You are producing the English edition of a Chinese source file. The reader is an ML researcher. Write the way the best lab research posts read, for example OpenAI's "The Hugging Face incident and the road ahead" or Anthropic's "Patterns and problems in multiagent systems": plain, specific, confident, short.

## Rules

1. **Same structure.**
   - **Keys.** Output JSON with exactly the same keys, nesting, array lengths and order as the source. Keep key names unchanged, even those ending in `_zh`; the build picks the file by language.
   - **What to translate.** Translate only string values that contain Chinese.
   - **What to copy unchanged.** Copy every other value exactly: ids, numbers, codes, tags such as `"shift"`, URLs, evidence objects and `year` fields.
2. **Numbers are sacred.** Every number in the source string must appear in the translation with the same value and precision, including `→` arrows, `×` ratios, `%`, ranges and paper ids. Do not round, recompute, add or drop numbers.
3. **Footnote markers.** Keep `{{fn:...}}` markers in the same position relative to the sentence. Translate the text inside them.
4. **Conclusion first.** Keep sentences short. Prefer active voice and concrete nouns. One idea per sentence.
5. **No filler.** Do not use these words and phrases: delve, landscape (except where the source means "the research landscape" section title), tapestry, crucial, pivotal, notably, importantly, it is worth noting, in conclusion, overall (as an opener), showcase, leverage (as a verb), robust (except the statistical "robustness check"), seamless, cutting-edge, game-changer, paradigm shift (use "shift"), unlock, empower, realm, navigate (figuratively).
6. **Headlines.** Titles stay short, ≤ 8 words where the Chinese is short, in sentence case (capitalise only the first word and proper nouns). No colons unless the source has one.
7. **Do not add hedges or claims.** Translate what is there. If the Chinese is terse, stay terse.
8. **Consistency.** Use the glossary below. Paper titles, model names and benchmark names stay in their original form.
9. **Units.** Use "per 10k submissions" for 每万篇. Write a share change as "6.3% → 11.6%" (keep the arrow). Write "×" ratios as "2.4×".

## Glossary

| Chinese | English |
|---|---|
| 投稿 | submissions |
| 录用率 / 接收率 | acceptance rate |
| 均分 | mean rating |
| 每万篇 | per 10k submissions |
| 份额 / 占比 | share |
| 细主题 / 簇 | topic cluster (or "cluster") |
| 大类 / 主题 | theme |
| 主领域 (primary area) | primary area |
| 模板化（措辞/写法/论文） | formulaic (wording / writing / papers) |
| 剔除模板化论文后 | excluding formulaic papers |
| 稳健口径 / 稳健性检验 | robustness check / excluding formulaic papers |
| 智能体 | agent(s) |
| 多智能体 | multi-agent |
| 具身智能 | embodied AI |
| 世界模型 | world models |
| 后训练 | post-training |
| 在线策略蒸馏 (OPD) | on-policy distillation (OPD) |
| 可验证奖励 (RLVR) | RLVR |
| 越狱 | jailbreak |
| 提示注入 | prompt injection |
| 护栏 | guardrails |
| 后门 / 投毒 | backdoors / data poisoning |
| 奖励黑客 | reward hacking |
| 谄媚 | sycophancy |
| 欺骗 / 密谋 | deception / scheming |
| 监督 / 监控 | oversight / monitoring |
| 可解释性 | interpretability |
| 机器遗忘 | machine unlearning |
| 水印 | watermarking |
| 幻觉 | hallucination |
| 公平性 | fairness |
| 安全相关论文（rel ≥ 1） | safety-related papers (relevance ≥ 1) |
| 核心安全论文（rel = 2） | core safety papers (relevance 2) |
| 子领域 / 子方向 | subfield |
| 一线观察 | on the ground |
| 2026 年评审的偏好 | what 2026 reviewers rewarded |
| 空白 | gaps |
| 值得关注 | watch list |
| 涨落 | risers and fallers |
| 具体问题 | specific problems |
| 范式转移 / 转向 | shift |
| 新风险 | new risk |
| 待观察 | to watch |
| 错位 | mismatch |
| 上升 / 下降 | rising / falling |
| 撤稿 / desk reject | withdrawn / desk-rejected |
| 注释与方法 | Notes and methods |
