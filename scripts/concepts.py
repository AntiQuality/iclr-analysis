"""Concept tracker: share of submissions mentioning concrete techniques / paradigms, 2025 -> 2026 -> 2027.

Matches title + keywords + abstract (case-insensitive unless the pattern starts with (?-i)).
    python3 scripts/concepts.py     # writes data/concepts.json
"""
import json
import warnings
warnings.filterwarnings("ignore")
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# group -> [(label_zh, label_en, regex)]
CONCEPTS = {
    "LLM 后训练与推理": [
        ("GRPO 及其变体", "GRPO & variants", r"\bgrpo\b|group relative policy|\bdapo\b|\bgspo\b"),
        ("RLVR 可验证奖励 RL", "RLVR", r"\brlvr\b|verifiable reward"),
        ("PPO", "PPO", r"\bppo\b|proximal policy optimi"),
        ("DPO / 直接偏好优化", "DPO", r"\bdpo\b|direct preference optimi"),
        ("RLHF", "RLHF", r"\brlhf\b|reinforcement learning from human feedback"),
        ("在线策略蒸馏 OPD", "On-policy distillation", r"on-policy (self-)?distillation|\bopd\b"),
        ("自蒸馏", "Self-distillation", r"self-distill"),
        ("思维链 CoT", "Chain-of-thought", r"chain[- ]of[- ]thought|\bcot\b"),
        ("长推理 / 推理模型", "Reasoning models / long CoT", r"reasoning model|long[- ]cot|large reasoning model|\blrms?\b|o1-like|r1-like|deepseek-r1"),
        ("过度思考 / 推理效率", "Overthinking / efficient reasoning", r"overthink|efficient reasoning|reasoning length|token budget|adaptive thinking"),
        ("隐式 / 连续潜空间推理", "Latent reasoning", r"latent reasoning|continuous (thought|reasoning)|reasoning in (the )?latent|coconut\b|latent chain"),
        ("测试时扩展", "Test-time scaling", r"test-time (scaling|compute)|inference-time (scaling|compute)"),
        ("测试时训练 / 适应", "Test-time training", r"test-time (training|adaptation|learning)"),
        ("过程奖励模型 PRM", "Process reward models", r"process reward|\bprms?\b"),
        ("LLM-as-a-Judge", "LLM-as-a-judge", r"llm[- ]as[- ]a[- ]judge|llm judges?|\bjudge models?\b"),
        ("Rubric 奖励", "Rubric-based rewards", r"rubric"),
        ("自我改进 / 自我进化", "Self-improvement / self-evolving", r"self-improv|self-evolv|recursive self"),
        ("熵坍缩 / 探索（LLM RL）", "Entropy collapse in LLM RL", r"entropy collapse|policy entropy|entropy regulariz.{0,30}(llm|rl)"),
        ("合成数据", "Synthetic data", r"synthetic data|data synthesis"),
        ("模型合并", "Model merging", r"model merging|merging models|task arithmetic|task vectors?"),
    ],
    "LLM 架构与效率": [
        ("混合专家 MoE", "Mixture-of-Experts", r"mixture[- ]of[- ]experts|\bmoe\b"),
        ("状态空间模型 / Mamba", "SSM / Mamba", r"\bmamba\b|state[- ]space model|\bssms?\b"),
        ("线性注意力", "Linear attention", r"linear attention|linear-time attention|gated delta|deltanet"),
        ("稀疏注意力", "Sparse attention", r"sparse attention"),
        ("循环 / Looped 架构", "Looped / recurrent-depth", r"looped (transformer|language model|model)|recurrent depth|universal transformer"),
        ("长上下文", "Long context", r"long[- ]context"),
        ("KV Cache 压缩", "KV-cache compression", r"kv[- ]?cache"),
        ("投机解码", "Speculative decoding", r"speculative decoding|draft model"),
        ("量化", "Quantization", r"quantiz"),
        ("剪枝 / 稀疏化", "Pruning", r"\bprun(e|ing)\b"),
        ("LoRA / PEFT", "LoRA / PEFT", r"\blora\b|low-rank adaptation|parameter-efficient"),
        ("Scaling law", "Scaling laws", r"scaling law"),
        ("Muon 等新优化器", "Muon & matrix optimizers", r"\bmuon\b|\bshampoo\b|\bsoap\b optimizer"),
        ("Tokenizer / 分词", "Tokenization", r"tokeniz"),
        ("扩散语言模型", "Diffusion language models", r"diffusion language model|\bdllms?\b|masked diffusion (language )?model|discrete diffusion"),
        ("多 token 预测", "Multi-token prediction", r"multi-token prediction|next-token prediction.{0,40}beyond"),
    ],
    "智能体": [
        ("LLM 智能体（全部）", "LLM agents (any)", r"\bagents?\b|agentic"),
        ("Agentic RL", "Agentic RL", r"agentic (rl|reinforcement)|multi-turn (rl|reinforcement)|agent(ic)? .{0,20}reinforcement learning"),
        ("工具使用 / 函数调用", "Tool use", r"tool[- ](use|using|call|calling|augmented|learning)|function[- ]call"),
        ("MCP 协议", "Model Context Protocol", r"model context protocol|\bmcp\b"),
        ("Agent 记忆", "Agent memory", r"(agent|agentic|long-term|episodic) memory|memory (system|module|bank|management) for (llm|agent)"),
        ("Agent Skills / 技能库", "Agent skills", r"\bskills? (library|librar|evolution|discovery|reuse)|agent skills?|\bskill packages?"),
        ("Agent Harness / 脚手架", "Agent harness / scaffolding", r"agent(ic)? harness|harness(es)? (evolution|engineering|design|optimi)|\bharnesses\b|scaffold"),
        ("Coding Agent / SWE", "Coding agents", r"coding agent|software engineering agent|swe-?bench|swe agent|repository-level"),
        ("GUI / Computer-use Agent", "GUI / computer-use agents", r"gui agent|computer[- ]use|web agent|os agent|mobile agent|osworld|webarena|android"),
        ("Deep Research Agent", "Deep research agents", r"deep research|search agent|browsecomp"),
        ("多智能体系统", "Multi-agent LLM systems", r"multi-agent (llm|system|framework|debate|collaboration)|llm-based multi-agent|multi-agent debate"),
        ("AI Scientist / 自动科研", "AI scientist / automated research", r"ai scientist|automated (scientific )?research|research agent|autonomous research|scientific discovery agent"),
        ("上下文工程 / 压缩", "Context engineering", r"context engineering|context (compression|compaction|management)"),
    ],
    "多模态与生成": [
        ("VLM / MLLM", "VLM / MLLM", r"vision[- ]language model|\bvlms?\b|multimodal large language|\bmllms?\b|\blvlms?\b"),
        ("视频理解", "Video understanding", r"video (understanding|question|llm|reasoning)|long video"),
        ("多模态推理 / Think with images", "Multimodal reasoning", r"multimodal reasoning|visual reasoning|thinking with images|visual chain"),
        ("统一理解+生成模型", "Unified understanding & generation", r"unified (multimodal )?(model|understanding|generation)|understanding and generation"),
        ("扩散模型", "Diffusion models", r"diffusion model|denoising diffusion|score-based"),
        ("Flow Matching", "Flow matching", r"flow matching|rectified flow"),
        ("一步 / 少步生成", "One/few-step generation", r"one-step|few-step|single-step (generation|diffusion)|consistency model|distribution matching distillation|mean ?flow"),
        ("自回归图像生成", "Autoregressive visual generation", r"autoregressive (image|visual|video) generation|visual autoregressive|\bvar\b model"),
        ("视频生成", "Video generation", r"video generation|text-to-video|video diffusion"),
        ("3D 高斯泼溅", "3D Gaussian splatting", r"gaussian splatting|\b3dgs\b"),
        ("NeRF", "NeRF", r"\bnerf\b|neural radiance"),
        ("前馈式 3D 重建", "Feed-forward 3D reconstruction", r"feed-forward (3d )?reconstruction|\bdust3r\b|\bvggt\b|\bmast3r\b"),
        ("扩散 RL / 对齐（图像）", "RL for diffusion", r"(diffusion|flow).{0,30}(reinforcement learning|grpo|reward fine-?tun|preference optimi)"),
        ("语音 / 音频 LLM", "Speech / audio LLMs", r"speech (language )?model|audio (language )?model|spoken|full-duplex|text-to-speech"),
    ],
    "具身与世界模型": [
        ("世界模型", "World models", r"world model"),
        ("VLA 视觉-语言-动作", "Vision-language-action", r"vision-language-action|\bvlas?\b"),
        ("World Action Model (WAM)", "World-action models", r"world[- ]action model|\bwams?\b"),
        ("JEPA", "JEPA", r"\bjepa\b|joint[- ]embedding predictive"),
        ("机器人操作", "Robot manipulation", r"robot(ic)? manipulation|manipulation (task|polic|skill)|dexterous|grasp"),
        ("自动驾驶", "Autonomous driving", r"autonomous driving|self-driving"),
        ("模仿学习 / 扩散策略", "Imitation / diffusion policy", r"imitation learning|diffusion polic|behavior cloning"),
        ("Sim-to-real", "Sim-to-real", r"sim-to-real|sim2real"),
        ("人形机器人", "Humanoids", r"humanoid"),
    ],
    "安全与可解释": [
        ("越狱", "Jailbreak", r"jailbreak"),
        ("提示注入", "Prompt injection", r"prompt injection"),
        ("红队", "Red teaming", r"red[- ]team"),
        ("Guardrail / 安全分类器", "Guardrails", r"guardrail|guard model|safety classifier|llama ?guard"),
        ("拒答 / 过度拒答", "Refusal / over-refusal", r"refus"),
        ("对齐伪装 / 欺骗 / Scheming", "Deception / scheming", r"decepti|scheming|sandbag|alignment faking"),
        ("涌现失配", "Emergent misalignment", r"emergent misalignment"),
        ("奖励黑客", "Reward hacking", r"reward hacking|reward over-?optimi|specification gaming"),
        ("谄媚", "Sycophancy", r"sycophan"),
        ("CoT 监控 / 忠实性", "CoT monitoring / faithfulness", r"(cot|chain[- ]of[- ]thought|reasoning) (monitor|faithful)|monitorability|unfaithful (reasoning|cot)"),
        ("AI Control / 监控", "AI control", r"\bai control\b|control protocol|untrusted (model|monitor)|trusted monitor"),
        ("评测意识 / 情境感知", "Eval / situational awareness", r"evaluation awareness|eval awareness|situational awareness|test awareness"),
        ("机器遗忘", "Machine unlearning", r"unlearn"),
        ("后门 / 投毒", "Backdoor / poisoning", r"backdoor|poison"),
        ("水印", "Watermarking", r"watermark"),
        ("AI 生成内容检测", "AI-generated content detection", r"(ai|machine|llm)-generated (text|image|content|video).{0,20}detect|detect.{0,30}(ai|machine|llm)-generated|deepfake"),
        ("差分隐私", "Differential privacy", r"differential(ly)? privat"),
        ("成员推断", "Membership inference", r"membership inference"),
        ("幻觉", "Hallucination", r"hallucinat"),
        ("稀疏自编码器 SAE", "Sparse autoencoders", r"sparse autoencoder|\bsaes?\b|transcoder"),
        ("激活引导 / 表征工程", "Steering / RepE", r"steering vector|activation steering|representation engineering|\bsteer(ing)? (llm|model|language)"),
        ("机制可解释 / 电路", "Mechanistic interp / circuits", r"mechanistic interpret|circuit discovery|\bcircuits?\b.{0,20}(model|transformer)|activation patching|attribution graph"),
        ("线性探针 / Probing", "Probing", r"linear prob|probing classifier|(activation|linear|representation) probes?|probes? (on|trained)"),
        ("Model Spec / 宪法", "Model spec / constitution", r"model spec|constitution"),
        ("公平性", "Fairness", r"fairness"),
    ],
    "科学、评测与其他": [
        ("蛋白质", "Protein", r"protein"),
        ("分子 / 药物", "Molecules / drug", r"molecul|drug"),
        ("材料 / 晶体", "Materials / crystals", r"materials? (science|discovery|design|propert|generation)|crystal"),
        ("单细胞 / 基因组", "Single-cell / genomics", r"single-cell|genom|\bdna\b|\brna\b"),
        ("医学影像 / 临床", "Medical", r"medical|clinical|patient|radiolog|patholog"),
        ("天气 / 气候", "Weather / climate", r"weather|climate|precipitation"),
        ("PDE / 神经算子", "PDE / neural operators", r"\bpdes?\b|neural operator|partial differential"),
        ("定理证明 / Lean", "Theorem proving / Lean", r"theorem prov|\blean ?4?\b|autoformaliz|formal (proof|verification)"),
        ("时间序列基础模型", "Time-series foundation models", r"time[- ]series foundation|foundation model.{0,20}time[- ]series"),
        ("图神经网络", "GNNs", r"graph neural network|\bgnns?\b"),
        ("联邦学习", "Federated learning", r"federated"),
        ("持续学习", "Continual learning", r"continual learning|lifelong learning|catastrophic forgetting"),
        ("对比学习 / 自监督", "Contrastive / SSL", r"contrastive learning|self-supervised"),
        ("Benchmark（标题/关键词）", "Benchmark papers", r"__BENCH__"),
        ("评测方法论 / 有效性", "Eval methodology / validity", r"evaluation methodology|construct validity|benchmark (validity|contamination|saturation)|measurement validity|statistical (rigor|significance)"),
        ("数据污染", "Data contamination", r"contaminat"),
        ("Transformer 理论（ICL 等）", "In-context learning theory", r"in-context learning"),
    ],
}


def main():
    df = pd.read_parquet(ROOT / "data" / "corpus.parquet")
    text = (df.title + " | " + df.keywords.map("; ".join) + " | " + df.abstract + " " + df.tldr.fillna("")).str.lower()
    tk = (df.title + " | " + df.keywords.map("; ".join)).str.lower()
    tot = df.groupby("year").size()
    y26 = df.year == 2026
    acc_base = df[y26].accepted.mean()
    out = []
    for g, items in CONCEPTS.items():
        for zh, en, pat in items:
            if pat == "__BENCH__":
                m = tk.str.contains(r"\bbenchmark", regex=True)
            else:
                m = text.str.contains(pat, regex=True)
            n = df[m].groupby("year").size().reindex([2025, 2026, 2027], fill_value=0)
            mt = tk.str.contains(pat, regex=True) if pat != "__BENCH__" else m
            ntk = df[mt].groupby("year").size().reindex([2025, 2026, 2027], fill_value=0)
            sh = (n / tot * 100).round(3)
            acc = df[m & y26].accepted.mean() if (m & y26).sum() else None
            rat = df[m & y26].rating.mean() if (m & y26).sum() else None
            out.append(dict(group=g, zh=zh, en=en, n=n.tolist(), share=sh.tolist(), share_tk=(ntk / tot * 100).round(3).tolist(),
                            acc26=None if acc is None else round(float(acc), 3),
                            rating26=None if rat is None or pd.isna(rat) else round(float(rat), 2)))
    json.dump(dict(totals=tot.tolist(), acc_base26=round(float(acc_base), 3), concepts=out),
              open(ROOT / "data" / "concepts.json", "w"), ensure_ascii=False, indent=1)
    t = pd.DataFrame(out)
    t["ratio"] = (t.share.str[2] + 0.05) / (t.share.str[1] + 0.05)
    pd.set_option("display.width", 250)
    print(t.sort_values("ratio", ascending=False)[["group", "zh", "n", "share", "ratio", "acc26"]].to_string())


if __name__ == "__main__":
    main()
