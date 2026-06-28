#!/usr/bin/env python3
"""Build anki/data/hsk_{4,5,6}.json from frequency-sorted wordlists.

Pipeline per word:
  - canonical row: (chinese, pinyin, english) from wordlists/hsk_X_by_frequency.txt
  - numeric_pinyin: derived from the Chinese characters via pypinyin (TONE3 + neutral=5)
  - morphology[]: per-character lookup in third_party/makemeahanzi/dictionary.txt;
                  fall back to Unihan (kMandarin + kDefinition) for any character
                  missing from makemeahanzi.

Outputs are chunked into 50-word lessons (numbered "01", "02", ...).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypinyin import Style, lazy_pinyin


ROOT = Path(__file__).resolve().parent.parent
WORDLIST_DIR = ROOT / "wordlists"
MAKEMEAHANZI = ROOT / "third_party" / "makemeahanzi" / "dictionary.txt"
UNIHAN_READINGS = ROOT / "third_party" / "Unihan" / "Unihan_Readings.txt"
OUTPUT_DIR = ROOT / "anki" / "data"

LESSON_SIZE = 50

DECK_IDS = {4: 2059400204, 5: 2059400205, 6: 2059400206}
MODEL_ID = 1607392401


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
    """Parse the subset of Unihan_Readings.txt that covers chars we need."""
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


def is_cjk(c: str) -> bool:
    return "一" <= c <= "鿿"


def numeric_pinyin_for(chinese: str) -> str:
    syls = lazy_pinyin(
        chinese,
        style=Style.TONE3,
        neutral_tone_with_five=True,
        errors="ignore",
    )
    syls = [s.strip().lower() for s in syls if s.strip()]
    return "_".join(syls)


def display_pinyin_for(chinese: str) -> str:
    syls = lazy_pinyin(chinese, style=Style.TONE, errors="ignore")
    return " ".join(s for s in syls if s)


def make_morph_entry(
    char: str,
    mmh: dict[str, dict],
    unihan: dict[str, dict],
) -> dict | None:
    if char in mmh:
        d = mmh[char]
        py_list = d.get("pinyin") or []
        # Pick the first pinyin that has a tone mark; otherwise first.
        pinyin = next((p for p in py_list if any(c in p for c in "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ")), py_list[0] if py_list else "")
        gloss = d.get("definition") or ""
        radical = d.get("radical")
        decomposition = d.get("decomposition")
        # decomposition starts with an IDS operator like ⿰⿱⿲... — strip it for display
        decomposition_display = _format_decomposition(decomposition)
        etym = d.get("etymology") or {}
        hint = etym.get("hint") or None
        return {
            "char": char,
            "pinyin": pinyin,
            "gloss": gloss,
            "radical": radical,
            "decomposition": decomposition_display,
            "hint": hint,
        }
    if char in unihan:
        u = unihan[char]
        return {
            "char": char,
            "pinyin": u.get("pinyin", ""),
            "gloss": u.get("definition", ""),
            "radical": None,
            "decomposition": None,
            "hint": None,
        }
    return None


IDS_OPS = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")


def _format_decomposition(s: str | None) -> str | None:
    """Render a makemeahanzi decomposition string as 'A + B' or 'A + B + C'.

    The input uses IDS operators (⿰, ⿱, ...) prefixed in operator form, e.g.
    ⿰丿㇔ → 丿 + ㇔. Multi-level composites get flattened into a list of
    leaves. '？' indicates an unknown component — we keep it as '?'.
    """
    if not s:
        return None
    # Strip IDS operators, keep the rest, splitting into characters.
    leaves = []
    for c in s:
        if c in IDS_OPS:
            continue
        if c == "？":
            leaves.append("?")
        else:
            leaves.append(c)
    if not leaves:
        return None
    return " + ".join(leaves)


def build_level(
    level: int,
    mmh: dict[str, dict],
    issues: list[str],
) -> dict:
    src = WORDLIST_DIR / f"hsk_{level}_by_frequency.txt"
    rows: list[tuple[str, str, str]] = []
    for line in src.read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        # cols: new_rank, orig_rank, chinese, pinyin, english (some HSK 4–6 entries
        # have stray trailing whitespace in chinese — strip)
        if len(parts) < 5:
            issues.append(f"L{level}: short row: {line!r}")
            continue
        chinese = parts[2].strip()
        wordlist_pinyin = parts[3].strip()
        english = parts[4].strip()
        rows.append((chinese, wordlist_pinyin, english))

    # Collect all characters needed for fallback lookup
    all_chars: set[str] = set()
    for chinese, _, _ in rows:
        for c in chinese:
            if is_cjk(c):
                all_chars.add(c)
    missing = [c for c in all_chars if c not in mmh]
    print(f"  L{level}: {len(rows)} rows, {len(all_chars)} unique CJK chars, {len(missing)} missing from makemeahanzi")
    unihan = load_unihan_fallback(set(missing)) if missing else {}

    lessons: list[dict] = []
    for i in range(0, len(rows), LESSON_SIZE):
        chunk = rows[i : i + LESSON_SIZE]
        n = f"{i // LESSON_SIZE + 1:02d}"
        vocab = []
        for chinese, wordlist_pinyin, english in chunk:
            morph = []
            for c in chinese:
                if not is_cjk(c):
                    continue
                entry = make_morph_entry(c, mmh, unihan)
                if entry is None:
                    issues.append(f"L{level}: no morphology for char {c!r} in word {chinese!r}")
                    continue
                morph.append(entry)
            entry = {
                "chinese": chinese,
                "pinyin": display_pinyin_for(chinese),
                "wordlist_pinyin": wordlist_pinyin,
                "numeric_pinyin": numeric_pinyin_for(chinese),
                "english": english,
                "morphology": morph,
            }
            vocab.append(entry)
        lessons.append({"n": n, "vocab": vocab})

    return {
        "deck_name": f"HSK {level} — Ordered (Frequency)",
        "deck_id": DECK_IDS[level],
        "level": level,
        "tag_prefix": f"HSK{level}",
        "model_id": MODEL_ID,
        "lessons": lessons,
    }


def main(argv: list[str]) -> int:
    levels = [int(a) for a in argv] if argv else [4, 5, 6]
    print("Loading makemeahanzi/dictionary.txt ...")
    mmh = load_makemeahanzi()
    print(f"  loaded {len(mmh)} characters")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    issues: list[str] = []
    for level in levels:
        data = build_level(level, mmh, issues)
        out = OUTPUT_DIR / f"hsk_{level}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        n_words = sum(len(l["vocab"]) for l in data["lessons"])
        print(f"  wrote {out} — {len(data['lessons'])} lessons, {n_words} words")

    if issues:
        print(f"\n{len(issues)} issues:")
        for x in issues[:30]:
            print(f"  - {x}")
        if len(issues) > 30:
            print(f"  ... and {len(issues) - 30} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
