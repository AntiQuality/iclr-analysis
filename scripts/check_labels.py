"""Validate a labelling sub-agent's output for one batch.

    python3 scripts/check_labels.py b07     # checks work/safety/out/b07*.jsonl against work/safety/batches/b07.jsonl
"""
import glob, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUBS = set("JB_ATK JB_DEF PI AGENT_SAFE FT_ROBUST ALIGN_TRAIN REWARD_HACK DECEPTION OVERSIGHT DANGER_EVAL INTERP_SAFE "
           "INTERP_GEN UNLEARN BACKDOOR WATERMARK PRIVACY IP ADV_ROBUST GEN_SAFE HALLU FAIR VALUES SOCIETAL SAFE_RL OOD OTHER NONE".split())
TYPES = {"attack", "defense", "eval", "analysis", "method", "theory", "position"}
TARGETS = {"llm", "reasoning", "mllm", "agent", "multiagent", "diffusion", "rl_robot", "classic", "general"}

b = sys.argv[1]
want = {json.loads(l)["id"] for l in open(ROOT / f"work/safety/batches/{b}.jsonl")}
got, errs = {}, []
for f in sorted(glob.glob(str(ROOT / f"work/safety/out/{b}*.jsonl"))):
    for n, line in enumerate(open(f), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            errs.append(f"{f}:{n} bad json"); continue
        e = []
        if o.get("rel") not in (0, 1, 2): e.append("rel")
        if o.get("sub") not in SUBS: e.append("sub")
        if o.get("sub2") not in SUBS | {None}: e.append("sub2")
        if o.get("type") not in TYPES: e.append("type")
        if o.get("target") not in TARGETS: e.append("target")
        if not isinstance(o.get("topic"), str) or not o["topic"].strip(): e.append("topic")
        if o.get("rel") == 0 and o.get("sub") != "NONE": e.append("rel0 needs sub=NONE")
        if o.get("rel") in (1, 2) and o.get("sub") == "NONE": e.append("rel>0 needs a real sub")
        if e: errs.append(f"{o.get('id')}: invalid {e}")
        got[o.get("id")] = o
missing, extra = want - set(got), set(got) - want
print(f"{b}: {len(want & set(got))}/{len(want)} labelled, {len(missing)} missing, {len(extra)} unknown ids, {len(errs)} errors")
for x in list(missing)[:20]: print("  missing", x)
for x in list(extra)[:10]: print("  unknown", x)
for x in errs[:30]: print("  ", x)
sys.exit(1 if missing or extra or errs else 0)
