#!/usr/bin/env python3
"""Build per-word mp3s by concatenating syllable mp3s from third_party/audio-cmn.

The HSK 1/2/3 decks reference audio as `[sound:cmn-{numeric_pinyin}.mp3]` where
multi-syllable words use underscore-joined numeric pinyin (e.g. `da3_suan4` for
打算). We rebuild the same convention by concatenating individual syllable
files.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HSK_AUDIO_DIR = ROOT / "third_party" / "audio-cmn" / "96k" / "hsk"
SYLLAB_DIR = ROOT / "third_party" / "audio-cmn" / "64k" / "syllabs"
CACHE_DIR = ROOT / "anki" / "build" / "audio_cache"


def _split_syllables(numeric_pinyin: str) -> list[str]:
    return [s for s in numeric_pinyin.split("_") if s]


def _resolve_syllab(syl: str, syllab_dir: Path) -> Path | None:
    """Return the syllab mp3 for `syl` (e.g. 'nai5'), with a tone-1 fallback for
    missing neutral-tone files (most syllables have tone-1 but not tone-5)."""
    p = syllab_dir / f"cmn-{syl}.mp3"
    if p.exists():
        return p
    if syl.endswith("5"):
        alt = syllab_dir / f"cmn-{syl[:-1]}1.mp3"
        if alt.exists():
            return alt
    return None


def get_or_build_word_audio(
    chinese: str,
    numeric_pinyin: str,
    hsk_audio_dir: Path = HSK_AUDIO_DIR,
    syllab_dir: Path = SYLLAB_DIR,
    cache_dir: Path = CACHE_DIR,
) -> Path | None:
    """Build a single mp3 for the word, naming it `cmn-{numeric_pinyin}.mp3`.

    Strategy:
      1. If `third_party/audio-cmn/96k/hsk/cmn-{chinese}.mp3` exists, copy it.
      2. Otherwise concatenate `third_party/audio-cmn/64k/syllabs/cmn-{syl}.mp3`
         for each syllable (with tone-1 fallback for missing tone-5).

    Returns None if all sources fail.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"cmn-{numeric_pinyin}.mp3"
    if out.exists():
        return out

    # Strategy 1: hanzi-named full-word audio
    hanzi_src = hsk_audio_dir / f"cmn-{chinese}.mp3"
    if hanzi_src.exists():
        shutil.copyfile(hanzi_src, out)
        return out

    # Strategy 2: syllab concat
    syllables = _split_syllables(numeric_pinyin)
    if not syllables:
        return None
    syllab_paths = [_resolve_syllab(s, syllab_dir) for s in syllables]
    if any(p is None for p in syllab_paths):
        return None
    if len(syllab_paths) == 1:
        shutil.copyfile(syllab_paths[0], out)
        return out
    list_file = cache_dir / f".concat-{numeric_pinyin}.txt"
    list_file.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in syllab_paths) + "\n"
    )
    try:
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                str(out),
            ],
            check=True,
        )
    finally:
        list_file.unlink(missing_ok=True)
    return out


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if len(args) % 2 != 0:
        print("usage: audio_concat.py <chinese> <numeric_pinyin> [<chinese> <numeric_pinyin> ...]")
        sys.exit(1)
    for i in range(0, len(args), 2):
        ch, np = args[i], args[i + 1]
        p = get_or_build_word_audio(ch, np)
        print(ch, np, "->", p)
