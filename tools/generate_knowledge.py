#!/usr/bin/env python3
"""Generate knowledge/ markdown from existing source content.

Outputs:
  knowledge/hsk_{1,2,3}/lesson_NN.md           — per-lesson scope-tagged markdown
  knowledge/hsk_3/appendices/{particles,three_les}.md
  knowledge/grammar_reference/hsk_1_2/NN_topic.md   — explanation only (no exercises)
  knowledge/grammar_reference/hsk_1_2/full_reference.md
  knowledge/{README.md,INDEX.md}

Run from repo root:
  tools/.venv/bin/python tools/generate_knowledge.py
"""

import re
import sys
import textwrap
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"
WORDLISTS = ROOT / "wordlists"
LESSON_TEXTS = ROOT / "lesson_texts"
APPS = ROOT / "apps"

CJK_RE = re.compile(r"[一-鿿]+")


def yaml_str(s: str) -> str:
    """Render a string as a YAML scalar safely.

    Strategy: single-quoted YAML, with internal single quotes doubled.
    Single-quoted YAML treats every character literally except `'` itself,
    so embedded double quotes (which appear in our titles like 结果补语 "好")
    don't need escaping.
    """
    return "'" + str(s).replace("'", "''") + "'"


# ============================================================
# Wordlist loading (clean reference for HSK 1/2 vocab lookup)
# ============================================================

def load_wordlist(path: Path, has_header: bool = False) -> dict:
    """Return {chinese: (pinyin, english)} for the given wordlist file."""
    out = {}
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if has_header and i == 0:
            continue
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        chinese = parts[1].strip()
        pinyin = parts[2].strip()
        english = parts[3].strip()
        if not chinese or not CJK_RE.search(chinese):
            continue
        # Some entries have variant in parentheses, e.g. "这 (这儿)"; index by both.
        out[chinese] = (pinyin, english)
        # Also index a stripped form (just the Chinese before any space/paren)
        primary = re.split(r"[ （(]", chinese)[0].strip()
        if primary and primary != chinese and primary not in out:
            out[primary] = (pinyin, english)
    return out


# ============================================================
# HSK 1/2 lesson parser
# ============================================================

LESSON_HEAD_RE = re.compile(
    r"^LESSON\s+(\d+):\s+(\S+)\s+\((.+?)\)\s*$", re.MULTILINE
)


def parse_hsk12_lessons(book_text: str):
    """Yield dicts: {n, title_zh, title_pinyin, vocab_chars: [str]}."""
    matches = list(LESSON_HEAD_RE.finditer(book_text))
    for i, m in enumerate(matches):
        n = int(m.group(1))
        title_zh = m.group(2).strip()
        title_pinyin = m.group(3).strip()
        # Body is between this header and the next (or EOF)
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(book_text)
        body = book_text[body_start:body_end]

        # Pull the title-line below the LESSON header for the English title:
        # Format: '\n  "Hello"\n'
        title_en_match = re.search(r'^\s+"([^"]+)"', body, re.MULTILINE)
        title_en = title_en_match.group(1).strip() if title_en_match else ""

        # Vocabulary block lives between the VOCABULARY header and the next "---" section.
        vocab_match = re.search(
            r"---\s*VOCABULARY[^\n]*---\s*\n(.*?)(?=\n---|\Z)",
            body,
            re.DOTALL,
        )
        vocab_chars = []
        if vocab_match:
            vocab_text = vocab_match.group(1)
            # Vocab entries look like "1.4% ni pron." where Chinese is intact;
            # collect every CJK token. Dedup but preserve order.
            seen = set()
            for tok in CJK_RE.findall(vocab_text):
                # Some tokens are joined ("你好"); split to single chars to be safe?
                # Keep as-is — wordlist entries are full words.
                if tok not in seen:
                    seen.add(tok)
                    vocab_chars.append(tok)
        yield {
            "n": n,
            "title_zh": title_zh,
            "title_pinyin": title_pinyin,
            "title_en": title_en,
            "vocab_tokens": vocab_chars,
        }


def resolve_vocab_against_wordlist(tokens: list, wordlist: dict) -> list:
    """For each token, return (chinese, pinyin, english, source) matched against wordlist.

    Source is 'wordlist' if found, 'unmatched' if not. Tokens are tried whole first,
    then progressively shorter prefixes from the right (handles OCR sometimes joining
    adjacent chars).
    """
    out = []
    for tok in tokens:
        if tok in wordlist:
            py, en = wordlist[tok]
            out.append((tok, py, en, "wordlist"))
            continue
        # Try splitting the token into known sub-words by greedy prefix match.
        sub_results = []
        rest = tok
        while rest:
            matched = False
            for length in range(len(rest), 0, -1):
                cand = rest[:length]
                if cand in wordlist:
                    py, en = wordlist[cand]
                    sub_results.append((cand, py, en, "wordlist"))
                    rest = rest[length:]
                    matched = True
                    break
            if not matched:
                sub_results.append((rest, "", "", "unmatched"))
                break
        out.extend(sub_results)
    # Dedupe by (chinese) preserving order
    seen = set()
    deduped = []
    for entry in out:
        if entry[0] not in seen:
            seen.add(entry[0])
            deduped.append(entry)
    return deduped


def render_hsk12_lesson(level: int, lesson: dict, wordlist: dict) -> str:
    n = lesson["n"]
    vocab = resolve_vocab_against_wordlist(lesson["vocab_tokens"], wordlist)
    matched = sum(1 for v in vocab if v[3] == "wordlist")

    md = []
    md.append("---")
    md.append(f"hsk_level: {level}")
    md.append(f"lesson: {n}")
    md.append(f"title_zh: {yaml_str(lesson['title_zh'])}")
    md.append(f"title_pinyin: {yaml_str(lesson['title_pinyin'])}")
    if lesson["title_en"]:
        md.append(f"title_en: {yaml_str(lesson['title_en'])}")
    md.append(f"vocab_count: {matched}")
    md.append("---")
    md.append("")
    md.append(f'# HSK {level} · Lesson {n} · {lesson["title_zh"]}')
    md.append("")
    md.append(f"*{lesson['title_pinyin']}* — {lesson['title_en']}" if lesson["title_en"] else f"*{lesson['title_pinyin']}*")
    md.append("")
    md.append("## New vocabulary")
    md.append("")
    if vocab:
        md.append("| Chinese | Pinyin | English |")
        md.append("|---|---|---|")
        for ch, py, en, src in vocab:
            if src == "wordlist":
                md.append(f"| {ch} | {py} | {en} |")
            # Skip unmatched tokens — they're typically OCR artefacts, not real words.
    md.append("")
    md.append("## Topic summary")
    md.append("")
    md.append(
        f"This lesson centres on “{lesson['title_zh']}” — *{lesson['title_pinyin']}*"
        + (f" (“{lesson['title_en']}”)." if lesson["title_en"] else ".")
    )
    md.append("")
    md.append(
        "Use the vocab above with grammar topics covered up to this point. "
        "For HSK 1/2 grammar reference see "
        "`knowledge/grammar_reference/hsk_1_2/`."
    )
    md.append("")
    return "\n".join(md)


# ============================================================
# HSK 3 lesson parser
# ============================================================

def _parse_hsk3_vocab_line(entry: str):
    """Parse a single vocab entry like '周末 zhōumò (weekend)' or
    '南(方) nán(fāng) (south)'. Returns (chinese, pinyin, english).

    The english is the content of the LAST top-level (...) at end of line;
    the rest splits on first whitespace into chinese / pinyin.
    """
    entry = entry.strip()
    if not entry.endswith(")"):
        return (entry, "", "")

    depth = 0
    open_idx = None
    for i in range(len(entry) - 1, -1, -1):
        if entry[i] == ")":
            depth += 1
        elif entry[i] == "(":
            depth -= 1
            if depth == 0:
                open_idx = i
                break

    if open_idx is None:
        return (entry, "", "")

    head = entry[:open_idx].strip()
    english = entry[open_idx + 1 : -1].strip()
    parts = head.split(None, 1)
    if len(parts) == 2:
        return (parts[0].strip(), parts[1].strip(), english)
    return (head, "", english)


def parse_hsk3_lesson(text: str) -> dict:
    """Parse one HSK3-LessonNN.txt file."""
    out = {"grammar": [], "vocab": []}

    # Title lines
    m = re.search(r"^HSK 3 — Lesson (\d+)", text, re.MULTILINE)
    out["n"] = int(m.group(1)) if m else None
    m = re.search(r"^Title \(Chinese\):\s*(.+)$", text, re.MULTILINE)
    out["title_zh"] = m.group(1).strip() if m else ""
    m = re.search(r"^Title \(English\):\s*(.+)$", text, re.MULTILINE)
    out["title_en"] = m.group(1).strip() if m else ""

    # GRAMMAR block
    m = re.search(
        r"GRAMMAR STRUCTURES\s*\n[-]+\n(.*?)\n\s*\nNEW WORDS",
        text, re.DOTALL,
    )
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                out["grammar"].append(line[2:].strip())

    # VOCABULARY block
    m = re.search(
        r"NEW WORDS / VOCABULARY\s*\n[-]+\n(.*?)\n\s*\nFULL LESSON TEXT",
        text, re.DOTALL,
    )
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line.startswith("- "):
                continue
            out["vocab"].append(_parse_hsk3_vocab_line(line[2:].strip()))

    return out


# ============================================================
# HSK 3 grammar HTML enrichment
# ============================================================

def html_to_clean_text(node, indent: str = "") -> str:
    """Walk a BeautifulSoup node and emit reasonably clean markdown text.

    Drops <script>, <style>, <nav>, <svg>; collapses whitespace; preserves
    headings, paragraphs, lists, code, and strong/em emphasis.
    """
    if isinstance(node, NavigableString):
        return str(node)
    if isinstance(node, Tag):
        if node.name in {"script", "style", "nav", "svg", "defs", "marker"}:
            return ""
        if node.name == "br":
            return "\n"
        # Block-level handling
        children = "".join(html_to_clean_text(c) for c in node.children)
        children = re.sub(r"[ \t]+", " ", children)
        if node.name in {"h1"}:
            return f"\n\n# {children.strip()}\n\n"
        if node.name in {"h2"}:
            return f"\n\n## {children.strip()}\n\n"
        if node.name in {"h3"}:
            return f"\n\n### {children.strip()}\n\n"
        if node.name in {"h4"}:
            return f"\n\n#### {children.strip()}\n\n"
        if node.name in {"strong", "b"}:
            return f"**{children.strip()}**"
        if node.name in {"em", "i"}:
            return f"*{children.strip()}*"
        if node.name in {"code"}:
            return f"`{children.strip()}`"
        if node.name in {"li"}:
            return f"- {children.strip()}\n"
        if node.name in {"p"}:
            return f"\n{children.strip()}\n\n"
        if node.name in {"ul", "ol"}:
            return f"\n{children}\n"
        if node.name in {"div", "section", "article", "header", "footer"}:
            return f"\n{children}\n"
        return children
    return ""


def collapse_whitespace(s: str) -> str:
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def parse_hsk3_grammar_html(html_path: Path):
    """Extract grammar sections from an HSK 3 lesson HTML file.

    Returns list of {heading, body_md}.
    """
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    sections = []
    for sec in soup.find_all("section", class_="gp"):
        h2 = sec.find("h2")
        heading = ""
        if h2:
            # Strip nested <span class="en-sub"> from heading text
            sub = h2.find("span", class_="en-sub")
            sub_text = sub.get_text(" ", strip=True) if sub else ""
            if sub:
                sub.extract()
            heading_main = h2.get_text(" ", strip=True)
            heading = f"{heading_main} — {sub_text}".strip(" —")
        # Body: render the rest of the section as text
        for tag in sec.find_all(["nav", "svg", "defs", "marker"]):
            tag.decompose()
        body_md = html_to_clean_text(sec)
        body_md = collapse_whitespace(body_md)
        # Drop the heading line that html_to_clean_text already emitted —
        # we'll prepend our own.
        body_md = re.sub(r"^.*?\n\n", "", body_md, count=1)
        sections.append({"heading": heading, "body_md": body_md.strip()})
    return sections


def render_hsk3_lesson(lesson: dict, grammar_sections: list) -> str:
    n = lesson["n"]
    md = []
    md.append("---")
    md.append("hsk_level: 3")
    md.append(f"lesson: {n}")
    md.append(f"title_zh: {yaml_str(lesson['title_zh'])}")
    md.append(f"title_en: {yaml_str(lesson['title_en'])}")
    if lesson["grammar"]:
        md.append("grammar_introduced:")
        for g in lesson["grammar"]:
            md.append(f"  - {yaml_str(g)}")
    md.append(f"vocab_count: {len(lesson['vocab'])}")
    md.append("---")
    md.append("")
    md.append(f'# HSK 3 · Lesson {n} · {lesson["title_zh"]}')
    md.append("")
    md.append(f"*{lesson['title_en']}*")
    md.append("")
    md.append("## New vocabulary")
    md.append("")
    md.append("| Chinese | Pinyin | English |")
    md.append("|---|---|---|")
    for ch, py, en in lesson["vocab"]:
        md.append(f"| {ch} | {py} | {en} |")
    md.append("")
    md.append("## Grammar introduced")
    md.append("")
    if grammar_sections:
        for sec in grammar_sections:
            md.append(f"### {sec['heading']}")
            md.append("")
            md.append(sec["body_md"])
            md.append("")
    else:
        # Fallback: just the lesson_text grammar list
        for g in lesson["grammar"]:
            md.append(f"- {g}")
        md.append("")
    return "\n".join(md)


# ============================================================
# HSK 3 appendices (particles, three-le)
# ============================================================

def render_html_to_markdown(html_path: Path, title_for_md: str, hsk_level: int = 3, kind: str = "appendix") -> str:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    # Drop nav and svg
    for tag in soup.find_all(["nav", "svg", "script", "style"]):
        tag.decompose()
    body = soup.body or soup
    md_body = html_to_clean_text(body)
    md_body = collapse_whitespace(md_body)
    md = []
    md.append("---")
    md.append(f"hsk_level: {hsk_level}")
    md.append(f"kind: {kind}")
    md.append(f"title: {yaml_str(title_for_md)}")
    md.append("---")
    md.append("")
    md.append(md_body)
    return "\n".join(md)


# ============================================================
# HSK 1/2 review sheets — extract the "reminder" block only
# ============================================================

REVIEW_TOPIC_RE = re.compile(r"^(\d+)-(.+)\.html$")


def parse_review_sheet(html_path: Path):
    """Extract title + reminder block from one review sheet.

    Returns {n, slug, title, reminder_md}.
    """
    m = REVIEW_TOPIC_RE.match(html_path.name)
    if not m:
        return None
    n = int(m.group(1))
    slug = m.group(2).replace("-", "_")

    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    title_h1 = soup.find("h1")
    title = title_h1.get_text(" ", strip=True) if title_h1 else slug

    reminder = soup.find("details", class_="reminder")
    reminder_md = ""
    if reminder:
        # Drop the <summary>
        summary = reminder.find("summary")
        if summary:
            summary.extract()
        reminder_md = html_to_clean_text(reminder)
        reminder_md = collapse_whitespace(reminder_md).strip()
    return {"n": n, "slug": slug, "title": title, "reminder_md": reminder_md}


def render_review_sheet(item: dict) -> str:
    md = []
    md.append("---")
    md.append("hsk_level: [1, 2]")
    md.append("kind: grammar_reference")
    md.append(f"title: {yaml_str(item['title'])}")
    md.append(f"topic_n: {item['n']}")
    md.append("---")
    md.append("")
    md.append(f"# {item['title']}")
    md.append("")
    md.append(item["reminder_md"])
    md.append("")
    return "\n".join(md)


# ============================================================
# HSK 1/2 reference.html — full grammar reference
# ============================================================

def render_full_reference(html_path: Path) -> str:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    for tag in soup.find_all(["nav", "svg", "script", "style"]):
        tag.decompose()
    body = soup.body or soup
    md_body = html_to_clean_text(body)
    md_body = collapse_whitespace(md_body)
    md = []
    md.append("---")
    md.append("hsk_level: [1, 2]")
    md.append("kind: grammar_reference_full")
    md.append('title: "HSK 1/2 grammar reference (full)"')
    md.append("---")
    md.append("")
    md.append(md_body)
    return "\n".join(md)


# ============================================================
# README + INDEX
# ============================================================

README = """\
# HSK knowledge

Agent-parseable scope-tagged content for natural Chinese practice (reading, writing, conversation).
Generated from `lesson_texts/`, `apps/hsk_3_grammar/*.html`, `apps/hsk_1_2_review/*.html`,
and `wordlists/*.txt` by `tools/generate_knowledge.py`.

## How to query (for an agent)

Each lesson file has YAML frontmatter with `hsk_level` and `lesson` keys.
Glob patterns scope a query naturally:

| User intent | Glob |
|---|---|
| "All HSK 1" | `knowledge/hsk_1/lesson_*.md` |
| "HSK 1+2 + HSK 3 lessons 1-3" | `knowledge/hsk_{1,2}/lesson_*.md` + `knowledge/hsk_3/lesson_0[1-3].md` |
| "Just HSK 3 lesson 7" | `knowledge/hsk_3/lesson_07.md` |
| "Particle 了 deep dive" | `knowledge/hsk_3/appendices/three_les.md` + `knowledge/grammar_reference/hsk_1_2/11_le_completed.md`, `12_le_change.md` |

After scoping, also include relevant `knowledge/grammar_reference/hsk_1_2/*.md` for HSK 1/2
grammar context (the 18 review-sheet topics — exercises stripped, explanations only).

## Layout

```
knowledge/
├── README.md           — this file
├── INDEX.md            — table of contents
├── hsk_1/              — 15 lesson files: vocab + topic summary
├── hsk_2/              — 15 lesson files: vocab + topic summary
├── hsk_3/              — 20 lesson files: vocab + grammar (rich) + grammar list
│   └── appendices/     — particles, three-le (cross-cutting)
└── grammar_reference/
    └── hsk_1_2/        — 18 topic sheets + full_reference.md
```

## Caveats

- HSK 1/2 lesson files contain vocab + topic summary only. Source dialogues were OCR-noisy
  past usable; an agent should generate fresh dialogues using the in-scope vocab.
- HSK 1/2 vocab is cross-referenced against `wordlists/hsk_{1,2}.txt` (clean canonical
  pinyin/English) — items in the lesson text that don't match a wordlist entry are skipped
  to avoid OCR garbage in the output.
- HSK 3 lesson files include both a structured grammar list (from the textbook TOC) and
  rich grammar explanations (parsed from the hand-written grammar app).

## Regenerating

```sh
tools/.venv/bin/python tools/generate_knowledge.py
```
"""


def write_readme():
    (KNOWLEDGE / "README.md").write_text(README, encoding="utf-8")


def write_index(hsk1_lessons, hsk2_lessons, hsk3_lessons, appendices, ref_topics):
    md = ["# Knowledge index", ""]
    md.append("## HSK 1 lessons")
    md.append("")
    for L in hsk1_lessons:
        md.append(f"- [Lesson {L['n']:02d}](hsk_1/lesson_{L['n']:02d}.md) — {L['title_zh']} ({L['title_en']})")
    md.append("")
    md.append("## HSK 2 lessons")
    md.append("")
    for L in hsk2_lessons:
        md.append(f"- [Lesson {L['n']:02d}](hsk_2/lesson_{L['n']:02d}.md) — {L['title_zh']} ({L['title_en']})")
    md.append("")
    md.append("## HSK 3 lessons")
    md.append("")
    for L in hsk3_lessons:
        md.append(f"- [Lesson {L['n']:02d}](hsk_3/lesson_{L['n']:02d}.md) — {L['title_zh']} ({L['title_en']})")
    md.append("")
    md.append("## HSK 3 grammar appendices")
    md.append("")
    for slug, title in appendices:
        md.append(f"- [{title}](hsk_3/appendices/{slug}.md)")
    md.append("")
    md.append("## HSK 1/2 grammar reference")
    md.append("")
    for r in ref_topics:
        md.append(f"- [{r['title']}](grammar_reference/hsk_1_2/{r['n']:02d}_{r['slug']}.md)")
    md.append("- [Full reference (single doc)](grammar_reference/hsk_1_2/full_reference.md)")
    md.append("")
    (KNOWLEDGE / "INDEX.md").write_text("\n".join(md), encoding="utf-8")


# ============================================================
# Main
# ============================================================

def main():
    KNOWLEDGE.mkdir(exist_ok=True)
    (KNOWLEDGE / "hsk_1").mkdir(exist_ok=True)
    (KNOWLEDGE / "hsk_2").mkdir(exist_ok=True)
    (KNOWLEDGE / "hsk_3").mkdir(exist_ok=True)
    (KNOWLEDGE / "hsk_3" / "appendices").mkdir(exist_ok=True)
    (KNOWLEDGE / "grammar_reference" / "hsk_1_2").mkdir(parents=True, exist_ok=True)

    # ---- HSK 1/2 lessons ----
    print("Loading wordlists...", file=sys.stderr)
    wl1 = load_wordlist(WORDLISTS / "hsk_1.txt", has_header=False)
    wl2 = load_wordlist(WORDLISTS / "hsk_2.txt", has_header=False)
    print(f"  hsk_1.txt: {len(wl1)} entries", file=sys.stderr)
    print(f"  hsk_2.txt: {len(wl2)} entries", file=sys.stderr)

    hsk1_lessons = []
    print("Generating HSK 1 lessons...", file=sys.stderr)
    book = (LESSON_TEXTS / "hsk_1" / "HSK-1_lessons.txt").read_text(encoding="utf-8")
    for L in parse_hsk12_lessons(book):
        md = render_hsk12_lesson(1, L, wl1)
        out = KNOWLEDGE / "hsk_1" / f"lesson_{L['n']:02d}.md"
        out.write_text(md, encoding="utf-8")
        hsk1_lessons.append(L)
    print(f"  wrote {len(hsk1_lessons)} HSK 1 lesson files", file=sys.stderr)

    hsk2_lessons = []
    print("Generating HSK 2 lessons...", file=sys.stderr)
    book = (LESSON_TEXTS / "hsk_2" / "HSK-2_lessons.txt").read_text(encoding="utf-8")
    for L in parse_hsk12_lessons(book):
        md = render_hsk12_lesson(2, L, wl2)
        out = KNOWLEDGE / "hsk_2" / f"lesson_{L['n']:02d}.md"
        out.write_text(md, encoding="utf-8")
        hsk2_lessons.append(L)
    print(f"  wrote {len(hsk2_lessons)} HSK 2 lesson files", file=sys.stderr)

    # ---- HSK 3 lessons (rich) ----
    print("Generating HSK 3 lessons...", file=sys.stderr)
    hsk3_lessons = []
    for n in range(1, 21):
        txt_path = LESSON_TEXTS / "hsk_3" / f"HSK3-Lesson{n:02d}.txt"
        html_path = APPS / "hsk_3_grammar" / f"lesson{n:02d}.html"
        if not txt_path.exists():
            print(f"  [skip] {txt_path.name} missing", file=sys.stderr)
            continue
        lesson = parse_hsk3_lesson(txt_path.read_text(encoding="utf-8"))
        sections = parse_hsk3_grammar_html(html_path) if html_path.exists() else []
        md = render_hsk3_lesson(lesson, sections)
        out = KNOWLEDGE / "hsk_3" / f"lesson_{n:02d}.md"
        out.write_text(md, encoding="utf-8")
        hsk3_lessons.append(lesson)
    print(f"  wrote {len(hsk3_lessons)} HSK 3 lesson files", file=sys.stderr)

    # ---- HSK 3 appendices ----
    print("Generating HSK 3 appendices...", file=sys.stderr)
    appendices = []
    for src, slug, title in [
        ("particles.html", "particles", "Discourse particles (HSK 3)"),
        ("three-le.html", "three_les", "The three 了s"),
    ]:
        p = APPS / "hsk_3_grammar" / src
        if not p.exists():
            continue
        md = render_html_to_markdown(p, title, hsk_level=3, kind="appendix")
        (KNOWLEDGE / "hsk_3" / "appendices" / f"{slug}.md").write_text(md, encoding="utf-8")
        appendices.append((slug, title))

    # ---- HSK 1/2 review sheets → grammar reference ----
    print("Generating HSK 1/2 grammar reference...", file=sys.stderr)
    ref_topics = []
    for sheet in sorted((APPS / "hsk_1_2_review" / "sheets").glob("*.html")):
        item = parse_review_sheet(sheet)
        if not item:
            continue
        md = render_review_sheet(item)
        out = KNOWLEDGE / "grammar_reference" / "hsk_1_2" / f"{item['n']:02d}_{item['slug']}.md"
        out.write_text(md, encoding="utf-8")
        ref_topics.append(item)
    print(f"  wrote {len(ref_topics)} HSK 1/2 review topic files", file=sys.stderr)

    # ---- HSK 1/2 full reference ----
    ref_html = APPS / "hsk_1_2_review" / "reference.html"
    if ref_html.exists():
        md = render_full_reference(ref_html)
        (KNOWLEDGE / "grammar_reference" / "hsk_1_2" / "full_reference.md").write_text(
            md, encoding="utf-8"
        )

    # ---- README and INDEX ----
    print("Writing README and INDEX...", file=sys.stderr)
    write_readme()
    write_index(hsk1_lessons, hsk2_lessons, hsk3_lessons, appendices, ref_topics)
    print("Done.", file=sys.stderr)


if __name__ == "__main__":
    main()
