# AI-safety labelling guide (shared by all labelling sub-agents)

Each input line is one ICLR submission: `{"id", "y" (year), "t" (title), "k" (keywords), "area" (author-chosen primary area), "a" (abstract, may be truncated)}`.
Judge from the content, not from the year. Output one JSON object per paper:

```
{"id": "...", "y": 2027, "rel": 2, "sub": "JB_ATK", "sub2": "AGENT_SAFE", "type": "attack", "target": "agent", "topic": "indirect prompt injection via web pages"}
```

## rel — how central is AI safety / trustworthy AI to this paper?
- `2` core: the paper's main contribution is about safety, security, alignment, privacy, fairness, trust, misuse or societal risk of AI systems.
- `1` adjacent: a trust-related property is a real secondary motivation (e.g. general interpretability, OOD robustness, hallucination reduction as one of several results, generic preference optimisation for helpfulness).
- `0` not safety: the lexicon match was incidental (e.g. "multimodal alignment", "safe" in a different sense, "bias" as a statistical term, "privacy" only mentioned in passing, reward models for math RL only).
For rel=0 still fill `sub`="NONE", `type`, `target`, `topic` briefly.

## sub / sub2 — fine-grained subfield (sub2 optional, null if none)
| code | meaning |
|---|---|
| JB_ATK | jailbreak attacks, red-teaming methods, automated adversarial prompting of LLMs/VLMs |
| JB_DEF | jailbreak defenses, guardrails, safety classifiers/moderation, refusal behaviour, over-refusal |
| PI | prompt injection (direct/indirect), tool/MCP/plug-in security, agent hijacking |
| AGENT_SAFE | safety of autonomous agents beyond injection: risky actions, computer-use/web/coding agent safety, multi-agent risk, agent safety benchmarks |
| FT_ROBUST | safety under fine-tuning: harmful fine-tuning attacks & defenses, safety-alignment durability, shallow alignment, safety of model merging/customisation |
| ALIGN_TRAIN | alignment training: RLHF, DPO & preference optimisation, safe RLHF, constitutional/principle-based training, reward modelling for alignment, safety data |
| REWARD_HACK | reward hacking, reward over-optimisation, specification gaming, sycophancy, goal misgeneralisation |
| DECEPTION | deception, lying, scheming, sandbagging, alignment faking, situational / evaluation awareness, emergent misalignment, hidden goals |
| OVERSIGHT | CoT monitoring & faithfulness, scalable oversight, weak-to-strong, debate, AI control protocols, model auditing |
| DANGER_EVAL | dangerous-capability & frontier-risk evaluation (bio/chem/cyber/autonomy), general safety benchmarks & safety evaluation methodology |
| INTERP_SAFE | interpretability used for safety: SAEs/probes/steering/representation engineering targeting refusal, harm, truthfulness, deception |
| INTERP_GEN | interpretability not aimed at a safety behaviour (circuits, features, attribution in general) |
| UNLEARN | machine unlearning (LLM or other), knowledge removal, unlearning evaluation/attacks |
| BACKDOOR | backdoors, trojans, data poisoning (attacks or defenses), sleeper agents |
| WATERMARK | watermarking, AI-generated text/image detection, provenance, content credentials |
| PRIVACY | differential privacy, membership inference, training-data extraction, PII leakage, private/federated learning |
| IP | model IP protection: fingerprinting, model stealing/extraction, copyright & data-attribution/licensing |
| ADV_ROBUST | adversarial examples & certified robustness (non-jailbreak), robustness of classifiers |
| GEN_SAFE | safety of image/video/audio generators: unsafe content, concept erasure, deepfakes, misuse of diffusion models |
| HALLU | hallucination, factuality, honesty, truthfulness, calibration & uncertainty for trust, knowing-what-you-don't-know |
| FAIR | fairness, social bias, stereotypes, demographic disparities |
| VALUES | value / pluralistic / cultural alignment, moral reasoning, normative judgement, human values |
| SOCIETAL | societal impact: misinformation, persuasion/manipulation, governance/policy/regulation, labour, human-AI interaction harms, AI welfare, ethics |
| SAFE_RL | safe RL, constrained RL, safe control, embodied/robot/autonomous-driving safety |
| OOD | OOD detection, distribution-shift robustness, anomaly detection for reliability |
| OTHER | clearly safety-related but none of the above |
| NONE | rel = 0 |

Pick the most specific code. Interpretability on refusal → INTERP_SAFE (not JB_DEF). A jailbreak benchmark → JB_ATK with type=eval. A paper that attacks agents through injected web content → PI.

## type — what kind of contribution
`attack` | `defense` (incl. mitigation/detection/guardrail) | `eval` (benchmark, dataset, evaluation protocol, red-team study) | `analysis` (empirical understanding / mechanism / measurement study) | `method` (training/alignment/technique that is not framed as attack/defense) | `theory` | `position` (position, survey, policy argument)

## target — the main AI system studied
`llm` (chat/text LLM) | `reasoning` (long-CoT / reasoning models, test-time compute) | `mllm` (VLM / multimodal LLM / audio-LLM) | `agent` (single tool-using / web / computer-use / coding agent) | `multiagent` | `diffusion` (image/video/audio generators) | `rl_robot` (RL agents, robots, driving) | `classic` (classifiers, CNNs, GNNs, tabular, federated nets) | `general` (method-agnostic / theory)

## topic
A 3–8 word specific English phrase naming the concrete problem the paper attacks, written so that papers on the same concrete problem get near-identical phrases (e.g. "harmful fine-tuning defense", "CoT monitorability", "sycophancy in LLMs", "membership inference on LLMs", "concept erasure in diffusion", "indirect prompt injection in web agents", "LLM unlearning robustness/relearning"). Prefer reusing a canonical phrase over inventing a new wording.

## Consistency rulings (apply exactly)
- Detecting AI-generated text/image/video/audio **and** deepfake detection (incl. face/voice forgery) → `WATERMARK` (provenance & detection). `GEN_SAFE` is for unsafe generation, concept erasure, misuse of generators.
- Hallucination / factuality as the main contribution → rel=2 `HALLU`; as a secondary benefit → rel=1.
- General interpretability (not targeting a safety behaviour) → rel=1 `INTERP_GEN`.
- Generic preference optimisation / DPO variants aimed at helpfulness or quality → rel=1 `ALIGN_TRAIN`; explicitly safety/harmlessness-oriented → rel=2.
- Process/outcome reward models or verifiers for math/code RL → rel=0, unless the paper studies reward hacking (then `REWARD_HACK`).
- OOD detection / distribution-shift robustness → rel=1 `OOD`.
- Diffusion-model RL for image quality only → rel=0.
