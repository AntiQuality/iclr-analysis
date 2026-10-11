"""Assemble one table of ICLR 2025 / 2026 / 2027 submissions from public GitHub mirrors.

Sources (OpenReview itself is unreachable from the build environment):
  2027  github.com/yzc-666/iclr2027-explorer   docs/data/papers.json + abs/*.json
        (OpenReview API v2 snapshot taken 2026-10-07, all statuses)
  2026  github.com/papercopilot/paperlists     iclr/iclr2026.json  (Git LFS)
  2025  github.com/papercopilot/paperlists     iclr/iclr2025.json  (Git LFS)

    python3 scripts/build_corpus.py EXT_DIR      # writes data/corpus.parquet
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EXT = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/user/ext")

STATUS_2027 = ["active", "withdrawn", "desk_rejected"]
STATUS_PC = {"Poster": "accept_poster", "Oral": "accept_oral", "Spotlight": "accept_spotlight",
             "Reject": "reject", "Withdraw": "withdrawn", "Desk Reject": "desk_rejected"}


def load_2027():
    base = EXT / "iclr2027-explorer" / "docs" / "data"
    meta = json.loads((base / "meta.json").read_text())
    rows = json.loads((base / "papers.json").read_text())
    shard = meta.get("shardSize", 500)
    abstracts = []
    for k in range((len(rows) + shard - 1) // shard):
        abstracts += json.loads((base / "abs" / f"{k}.json").read_text())
    assert len(abstracts) == len(rows)
    out = []
    for r, a in zip(rows, abstracts):
        pid, number, title, kws, area, status, _tags = r
        abstract, _, tldr = a.partition("\n\nTL;DR: ")
        out.append(dict(year=2027, id=pid, number=number, title=title, abstract=abstract.strip(), tldr=tldr.strip(),
                        keywords=[k.strip() for k in kws.split(";") if k.strip()], primary_area=meta["areas"][area],
                        status=STATUS_2027[status], rating=None))
    return out


def load_pc(year):
    data = json.loads((EXT / "pc" / f"iclr{year}.json").read_text())
    out = []
    for p in data:
        if p.get("track", "main") != "main":
            continue
        status = p["status"]
        status = STATUS_PC.get(status, "accept_poster" if "Poster" in status else "accept_oral" if "Oral" in status
                               else "accept_spotlight" if "Spotlight" in status else status)
        rating = p.get("rating_avg")
        if isinstance(rating, str):
            try:
                rating = json.loads(rating)
            except ValueError:
                rating = None
        rating = float(rating[0]) if isinstance(rating, list) and rating and rating[0] else None
        out.append(dict(year=year, id=p["id"], number=None, title=p["title"].strip(), abstract=(p.get("abstract") or "").strip(),
                        tldr=(p.get("tldr") or "").strip(),
                        keywords=[k.strip() for k in (p.get("keywords") or "").split(";") if k.strip()],
                        primary_area=(p.get("primary_area") or "").strip() or None, status=status, rating=rating))
    return out


def main():
    rows = load_pc(2025) + load_pc(2026) + load_2027()
    df = pd.DataFrame(rows).drop_duplicates(["year", "id"])
    df["accepted"] = df.status.str.startswith("accept")
    df.to_parquet(ROOT / "data" / "corpus.parquet", index=False)
    print(df.groupby("year").size())
    print(df.groupby(["year", "status"]).size())
    print("missing area:", df[df.primary_area.isna()].groupby("year").size().to_dict())


if __name__ == "__main__":
    main()
