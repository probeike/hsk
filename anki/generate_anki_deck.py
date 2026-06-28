#!/usr/bin/env python3
"""Generate an HSK Anki deck from a JSON data file.

The format (model, fields, templates, CSS) is fixed and matches the existing
HSK 1/2/3 v2 decks. The vocab content lives in JSON — see anki/data/hsk_*.json.

Usage:
    python anki/generate_anki_deck.py anki/data/hsk_4.json

Writes to anki/output/HSK{level}_Ordered.apkg.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

import genanki

from audio_concat import get_or_build_word_audio


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "anki" / "output"


CSS = """
.card {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 20px;
    text-align: center;
    color: #ffffff;
    background-color: #1a1a2e;
    padding: 20px;
}
.chinese { font-size: 56px; font-weight: bold; color: #ffffff; margin-bottom: 10px; }
.pinyin  { font-size: 24px; color: #ff6b81; margin-bottom: 8px; }
.english { font-size: 22px; color: #7ec8e3; margin-bottom: 14px; }
.prompt-en { font-size: 30px; color: #7ec8e3; margin-bottom: 8px; }
.lesson-tag { font-size: 13px; color: #888; margin-top: 14px; letter-spacing: 1px; }
.morph-label { font-size: 13px; color: #f0a500; margin-top: 14px; margin-bottom: 6px; letter-spacing: 1px; }
.morph {
    font-family: "Noto Sans CJK SC", "Source Han Sans SC",
                 "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 15px; color: #d8d8d8; text-align: left;
    margin: 0 auto; max-width: 620px;
    background: #20203a; border-left: 3px solid #f0a500;
    padding: 10px 14px; border-radius: 4px;
    line-height: 1.55;
}
.morph ul { margin: 0; padding-left: 20px; }
.morph li { margin-bottom: 6px; }
.morph b { color: #ffd166; font-size: 18px; }
hr { border: 0; border-top: 1px solid #444; margin: 14px 0; }
"""


def make_model(model_id: int) -> genanki.Model:
    return genanki.Model(
        model_id,
        "HSK Vocab (Audio + Morphology)",
        fields=[
            {"name": "Chinese"},
            {"name": "Pinyin"},
            {"name": "English"},
            {"name": "Morphology"},
            {"name": "Audio"},
            {"name": "Lesson"},
        ],
        templates=[
            {
                "name": "Recognize (ZH to EN)",
                "qfmt": '<div class="chinese">{{Chinese}}</div>'
                        '<div class="lesson-tag">{{Lesson}}</div>',
                "afmt": '{{FrontSide}}<hr>'
                        '<div class="pinyin">{{Pinyin}}</div>'
                        '<div class="english">{{English}}</div>'
                        '{{Audio}}'
                        '<div class="morph-label">CHARACTER BREAKDOWN</div>'
                        '<div class="morph">{{Morphology}}</div>',
            },
            {
                "name": "Produce (EN to ZH)",
                "qfmt": '<div class="prompt-en">{{English}}</div>'
                        '<div class="lesson-tag">{{Lesson}}</div>',
                "afmt": '{{FrontSide}}<hr>'
                        '<div class="chinese">{{Chinese}}</div>'
                        '<div class="pinyin">{{Pinyin}}</div>'
                        '{{Audio}}'
                        '<div class="morph-label">CHARACTER BREAKDOWN</div>'
                        '<div class="morph">{{Morphology}}</div>',
            },
        ],
        css=CSS,
    )


def render_morphology(items: list[dict]) -> str:
    """Build the morphology HTML matching v2 format byte-for-byte.

    Format per item: <li><b>{char}</b> ({pinyin}) — {gloss} · radical {radical}; {decomposition}[; {hint}]</li>
    """
    lis = []
    for it in items:
        char = it["char"]
        pinyin = it.get("pinyin", "") or ""
        gloss = it.get("gloss", "") or ""
        radical = it.get("radical")
        decomposition = it.get("decomposition")
        hint = it.get("hint")
        suffix_parts = []
        if radical:
            suffix_parts.append(f"radical {radical}")
        if decomposition:
            suffix_parts.append(decomposition)
        if hint:
            suffix_parts.append(hint)
        suffix = "; ".join(suffix_parts)
        body = f"<b>{html.escape(char)}</b> ({pinyin}) — {gloss}"
        if suffix:
            body += f" · {suffix}"
        lis.append(f"<li>{body}</li>")
    return "<ul>" + "".join(lis) + "</ul>"


def build_deck(data: dict, deck: genanki.Deck, package_media: list[Path]) -> tuple[int, list[str]]:
    model = make_model(data["model_id"])
    level = data["level"]
    tag_prefix = data["tag_prefix"]
    notes_added = 0
    audio_misses: list[str] = []

    for lesson in data["lessons"]:
        lesson_n = lesson["n"]  # string like "01" or "Extra"
        lesson_field = (
            f"HSK {level} · Lesson {int(lesson_n)}"
            if lesson_n.isdigit()
            else f"HSK {level} · {lesson_n}"
        )
        lesson_tag = f"{tag_prefix}::Lesson_{lesson_n}"
        for v in lesson["vocab"]:
            chinese = v["chinese"]
            pinyin = v["pinyin"]
            numeric_pinyin = v.get("numeric_pinyin") or ""
            english = v["english"]
            morph_html = render_morphology(v.get("morphology", []))
            audio_field = ""
            if numeric_pinyin:
                mp3 = get_or_build_word_audio(chinese, numeric_pinyin)
                if mp3 is not None:
                    audio_field = f"[sound:cmn-{numeric_pinyin}.mp3]"
                    package_media.append(mp3)
                else:
                    audio_misses.append(f"{chinese} ({numeric_pinyin})")

            note = genanki.Note(
                model=model,
                fields=[chinese, pinyin, english, morph_html, audio_field, lesson_field],
                tags=[lesson_tag, f"{tag_prefix}::Vocabulary"],
            )
            deck.add_note(note)
            notes_added += 1
    return notes_added, audio_misses


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("data", type=Path, help="Path to anki/data/hsk_X.json")
    args = ap.parse_args(argv)

    data = json.loads(args.data.read_text())
    deck = genanki.Deck(data["deck_id"], data["deck_name"])
    package_media: list[Path] = []
    n_notes, audio_misses = build_deck(data, deck, package_media)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"HSK{data['level']}_Ordered.apkg"
    pkg = genanki.Package(deck, media_files=[str(p) for p in package_media])
    pkg.write_to_file(out_path)

    print(f"wrote {out_path}")
    print(f"  notes: {n_notes}")
    print(f"  audio files: {len(package_media)}")
    if audio_misses:
        print(f"  audio missing for {len(audio_misses)} word(s):")
        for w in audio_misses[:30]:
            print(f"    - {w}")
        if len(audio_misses) > 30:
            print(f"    ... and {len(audio_misses) - 30} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
