#!/usr/bin/env python3
"""Build a character-keyed HSK1-3 morphology JSON for languagegrader.

Unlike anki/build_hsk_data.py (word-level, HSK 4-6, needs pypinyin), this is
pure stdlib and character-keyed: one entry per CJK character appearing in
  - wordlists/hsk_{1,2,3}.txt (canonical HSK 1-3 vocabulary), and
  - the "New vocabulary" tables of apps/hsk_3_grammar/lesson*.html
    (covers off-list lesson words: proper names, parenthesised variants, ...).

Sources: third_party/makemeahanzi/dictionary.txt, falling back to
third_party/Unihan/Unihan_Readings.txt. A character missing from both is a
hard failure. Output is deterministic (sorted keys, no timestamps); the
`generator` block records the script, the hsk repo commit, and the sha256 of
every input, so staleness is checkable without this repo.

The output file is COMMITTED into languagegrader at
packages/curriculum/vendor/hsk123-morphology.json — regenerate with:
    python3 tools/build_hsk123_morphology.py > /tmp/hsk123-morphology.json
    cp /tmp/hsk123-morphology.json \
       ../languagegrader/packages/curriculum/vendor/hsk123-morphology.json
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDLIST_DIR = ROOT / "wordlists"
GRAMMAR_DIR = ROOT / "apps" / "hsk_3_grammar"
MAKEMEAHANZI = ROOT / "third_party" / "makemeahanzi" / "dictionary.txt"
UNIHAN_READINGS = ROOT / "third_party" / "Unihan" / "Unihan_Readings.txt"

IDS_OPS = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")
VOCAB_ROW = re.compile(r"<tr><td>([^<]+)</td><td>[^<]*</td><td>[^<]*</td></tr>")


def is_cjk(c: str) -> bool:
    return "一" <= c <= "鿿"


def load_makemeahanzi() -> dict[str, dict]:
    out: dict[str, dict] = {}
    with MAKEMEAHANZI.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ch = obj.get("character")
            if ch:
                out[ch] = obj
    return out


def load_unihan_fallback(needed: set[str]) -> dict[str, dict]:
    if not needed:
        return {}
    needed_codepoints = {f"U+{ord(c):04X}": c for c in needed}
    out: dict[str, dict] = {}
    with UNIHAN_READINGS.open() as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            code, key, value = parts
            ch = needed_codepoints.get(code)
            if not ch:
                continue
            entry = out.setdefault(ch, {})
            if key == "kMandarin":
                entry["pinyin"] = value.split()[0].lower() if value else ""
            elif key == "kDefinition":
                entry["definition"] = value
    return out


def format_decomposition(s: str | None) -> str | None:
    if not s:
        return None
    leaves = ["?" if c == "？" else c for c in s if c not in IDS_OPS]
    return " + ".join(leaves) if leaves else None


def collect_characters() -> tuple[set[str], list[Path]]:
    chars: set[str] = set()
    inputs: list[Path] = []
    for level in (1, 2, 3):
        p = WORDLIST_DIR / f"hsk_{level}.txt"
        inputs.append(p)
        for line in p.read_text().splitlines():
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            for c in parts[1].strip():
                if is_cjk(c):
                    chars.add(c)
    for p in sorted(GRAMMAR_DIR.glob("lesson*.html")):
        inputs.append(p)
        for m in VOCAB_ROW.finditer(p.read_text()):
            for c in m.group(1):
                if is_cjk(c):
                    chars.add(c)
    return chars, inputs


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def main() -> int:
    chars, inputs = collect_characters()
    mmh = load_makemeahanzi()
    missing_from_mmh = {c for c in chars if c not in mmh}
    unihan = load_unihan_fallback(missing_from_mmh)
    missing_everywhere = sorted(c for c in missing_from_mmh if c not in unihan)
    if missing_everywhere:
        print(
            f"FATAL: {len(missing_everywhere)} characters missing from both "
            f"makemeahanzi and Unihan: {' '.join(missing_everywhere)}",
            file=sys.stderr,
        )
        return 1

    characters: dict[str, dict] = {}
    for c in sorted(chars):
        if c in mmh:
            d = mmh[c]
            characters[c] = {
                "pinyin": d.get("pinyin") or [],
                "gloss": d.get("definition") or None,
                "radical": d.get("radical") or None,
                "decomposition": format_decomposition(d.get("decomposition")),
                "hint": (d.get("etymology") or {}).get("hint") or None,
                "source": "makemeahanzi",
            }
        else:
            u = unihan[c]
            characters[c] = {
                "pinyin": [u["pinyin"]] if u.get("pinyin") else [],
                "gloss": u.get("definition") or None,
                "radical": None,
                "decomposition": None,
                "hint": None,
                "source": "unihan",
            }

    out = {
        "generator": {
            "repo": "hsk",
            "script": "tools/build_hsk123_morphology.py",
            "gitSha": git_sha(),
            "inputs": {
                str(p.relative_to(ROOT)): f"sha256:{sha256_of(p)}"
                for p in [MAKEMEAHANZI, UNIHAN_READINGS, *inputs]
            },
        },
        "characters": characters,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1, sort_keys=True)
    sys.stdout.write("\n")
    print(f"OK: {len(characters)} characters "
          f"({sum(1 for v in characters.values() if v['source'] == 'unihan')} via Unihan)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
