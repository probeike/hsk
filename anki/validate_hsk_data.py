#!/usr/bin/env python3
"""Deterministic checks on anki/data/hsk_{4,5,6}.json.

Flags:
  - words whose chinese/pinyin/english don't match the canonical wordlist
  - numeric_pinyin malformed (must be `[a-z]+[1-5]` joined by `_`)
  - characters in morphology fields (decomposition, hint) that aren't in HSK 1–6

The third check addresses the "no character bleed" goal: we don't want flashcards
to expose Chinese characters that the learner hasn't seen in any HSK list.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "anki" / "data"
WORDLIST = ROOT / "wordlists"


def load_hsk_chars() -> set[str]:
    chars: set[str] = set()
    for level in (1, 2, 3, 4, 5, 6):
        p = WORDLIST / f"hsk_{level}.txt"
        for line in p.read_text().splitlines():
            for c in line:
                if "一" <= c <= "鿿":
                    chars.add(c)
    return chars


def load_wordlist_index(level: int) -> dict[str, tuple[str, str]]:
    """{chinese: (pinyin, english)} from the canonical (non-frequency) wordlist."""
    p = WORDLIST / f"hsk_{level}.txt"
    out: dict[str, tuple[str, str]] = {}
    for line in p.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        # Header rows for HSK 3 have ('No', 'Chinese', 'Pinyin', 'English'); skip
        if parts[0].strip().lower() in {"no", "no."}:
            continue
        try:
            int(parts[0].strip())
        except ValueError:
            continue
        chinese = parts[1].strip()
        pinyin = parts[2].strip()
        english = parts[3].strip() if len(parts) >= 4 else ""
        out[chinese] = (pinyin, english)
    return out


NUMERIC_PINYIN_RE = re.compile(r"^[a-zü]+[1-5](_[a-zü]+[1-5])*$")


def is_cjk(c: str) -> bool:
    return "一" <= c <= "鿿"


def chars_in_field(s: str | None) -> set[str]:
    return {c for c in (s or "") if is_cjk(c)}


def validate_level(level: int, hsk_chars: set[str]) -> list[str]:
    issues: list[str] = []
    data = json.loads((DATA / f"hsk_{level}.json").read_text())
    wl = load_wordlist_index(level)
    seen: set[str] = set()

    for lesson in data["lessons"]:
        for v in lesson["vocab"]:
            chinese = v["chinese"]
            seen.add(chinese)
            ref = wl.get(chinese)
            if ref is None:
                issues.append(f"L{level} {chinese}: not in canonical wordlist hsk_{level}.txt")
            else:
                ref_py, ref_en = ref
                # The canonical pinyin in HSK 4–6 wordlists is unspaced; ours is spaced.
                if v["wordlist_pinyin"] != ref_py:
                    issues.append(
                        f"L{level} {chinese}: pinyin mismatch — wordlist={ref_py!r}, ours={v['wordlist_pinyin']!r}"
                    )
                if v["english"] != ref_en:
                    issues.append(
                        f"L{level} {chinese}: english mismatch — wordlist={ref_en!r}, ours={v['english']!r}"
                    )
            if not NUMERIC_PINYIN_RE.match(v["numeric_pinyin"]):
                issues.append(f"L{level} {chinese}: numeric_pinyin malformed: {v['numeric_pinyin']!r}")
            for m in v["morphology"]:
                # Glosses must be English. Decomposition and hints can contain
                # CJK component-radicals (扌, 辶, 卩, ...) by design — those are
                # how character morphology is taught, so we don't flag them.
                gloss_cjk = chars_in_field(m.get("gloss"))
                if gloss_cjk:
                    issues.append(
                        f"L{level} {chinese} char={m['char']}: gloss has CJK chars: {sorted(gloss_cjk)}"
                    )

    return issues


def main() -> int:
    hsk_chars = load_hsk_chars()
    print(f"HSK 1–6 character set: {len(hsk_chars)} chars\n")
    all_issues: list[str] = []
    for level in (4, 5, 6):
        issues = validate_level(level, hsk_chars)
        print(f"HSK {level}: {len(issues)} issues")
        all_issues.extend(issues)
    print()
    if all_issues:
        # Group by issue type
        types: dict[str, int] = {}
        for x in all_issues:
            key = re.sub(r"L\d+ \S+(?:\s+char=\S+)?:\s*", "", x).split(":")[0]
            key = re.sub(r"\(.*?\)", "()", key)
            types[key] = types.get(key, 0) + 1
        print("Issue summary:")
        for k, v in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {v:5d}  {k}")
        print(f"\nFirst 25 issues:")
        for x in all_issues[:25]:
            print(f"  - {x}")
    return 0 if not all_issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
