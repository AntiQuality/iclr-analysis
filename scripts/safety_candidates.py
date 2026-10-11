"""Select the AI-safety candidate pool (recall-oriented) for LLM sub-agent labelling.

A paper is a candidate if its primary area is the safety area, or if its title/keywords/abstract
match the broad safety lexicon below. Sub-agents then decide relevance and fine-grained labels.

    python3 scripts/safety_candidates.py      # writes data/safety_candidates.parquet
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SAFETY_AREA = "alignment, fairness, safety, privacy, and societal considerations"

LEXICON = r"""
\bsafety\b|\bsafe(ty)?[- ]?(alignment|guard|rlhf|fine-?tun)|\bunsafe\b|\bharm(ful|less|s)?\b|jailbreak|red[- ]?team|
prompt injection|\binjection attack|guardrail|refusal|over-?refus|\balignment (tax|faking)|misalign|deceptiv|deception|
\bscheming\b|sandbag|situational awareness|reward hack|specification gaming|sycophan|power[- ]seeking|
\bai control\b|scalable oversight|weak-to-strong|\bmonitor(ing|ability)\b.{0,40}(chain|cot|reasoning|agent)|
cot faithfulness|faithful(ness)? (of )?(chain|reasoning|cot)|unlearn|backdoor|trojan|data poison|poisoning attack|
watermark|membership inference|differential(ly)? privat|privacy|\bpii\b|data extraction|model (stealing|extraction)|
fingerprint|copyright|\bfairness\b|\bbias(es|ed)?\b.{0,30}(social|gender|racial|demographic)|stereotyp|toxic|
hate speech|misinformation|disinformation|persuasi|manipulat(ion|ive) (of|users|human)|dangerous capabilit|
\bbio(security|weapon|risk)|\bcbrn\b|cyber(security|attack|offen)|catastrophic risk|existential|frontier (ai )?risk|
dual[- ]use|adversarial (attack|robust|example|prompt|suffix)|certified robust|robustness certif|
concept erasure|erasing concepts|\bnsfw\b|deepfake|ai-generated (text|image|content) detect|machine-generated text|
llm-generated text detect|hallucinat|honest|truthful|value alignment|pluralistic|
human values|moral|\bethic|constitutional|\brlhf\b|preference (optimization|alignment)|\bdpo\b|reward model|
(steering|representation engineering).{0,60}(safety|refus|harm|truth|behavio)|sparse autoencoder|mechanistic interp|
trustworth|accountab|governance|(model|safety|alignment) audit|evaluation awareness|emergent misalignment|
agent(ic)? (safety|security|risk|misuse)|tool[- ]use (safety|attack)|computer[- ]use.{0,40}(safety|attack|risk)|
safe (rl|reinforcement|exploration|control)|constrained (rl|reinforcement|policy)|shield(ing)?\b|out-of-distribution detection
"""
RX = re.compile(LEXICON.replace("\n", ""), re.I)


def main():
    df = pd.read_parquet(ROOT / "data" / "corpus.parquet")
    text = df.title + " | " + df.keywords.map("; ".join) + " | " + df.abstract
    df["lex_hits"] = text.map(lambda t: len(set(m.group(0).lower() for m in RX.finditer(t))))
    df["in_area"] = df.primary_area.eq(SAFETY_AREA)
    title_kw = (df.title + " | " + df.keywords.map("; ".join)).map(lambda t: bool(RX.search(t)))
    # area papers always; elsewhere require a hit in title/keywords or >=2 distinct hits in the abstract
    cand = df[df.in_area | title_kw | (df.lex_hits >= 2)]
    cand = cand[cand.year.isin([2026, 2027])]
    print(cand.groupby(["year", "in_area"]).size())
    cand[["year", "id", "title", "keywords", "abstract", "tldr", "primary_area", "status", "rating", "in_area", "lex_hits"]] \
        .to_parquet(ROOT / "data" / "safety_candidates.parquet", index=False)


if __name__ == "__main__":
    main()
