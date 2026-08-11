#!/usr/bin/env python3
"""Mechanical checker for custom_grammar practice docs.

Checks per file:
  1. OVERLAP  - exercise Chinese vs taught example sentences (exact + high-similarity)
  2. VOCAB    - exercise Chinese segmented against HSK1-3 wordlists + page vocab table
  3. LINT     - widget contract violations
  4. COUNTS   - exercises by data-exercise type

Usage: python3 check_exercises.py FILE.html [FILE2.html ...] [--against OTHER.html ...]
  --against: additional files whose taught sentences also count for the overlap check
             (used for mixed-review and reading pages).
"""
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path("/Users/agouws/project/hsk")
APP = ROOT / "apps/custom_grammar"

PUNCT = "，。！？?!,.、；：""''：…—·（）()《》 　"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return "".join(ch for ch in s if ch not in PUNCT and not ch.isspace())


def han_only(s: str) -> str:
    return "".join(ch for ch in s if "一" <= ch <= "鿿")


# ---------------------------------------------------------------- HTML parsing
class DocParser(HTMLParser):
    """Extracts taught examples (div.ex p.cn) and exercise blocks."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.taught = []          # list of cn strings
        self.exercises = []       # list of dicts
        self._stack = []          # (tag, classes, attrs)
        self._in_ex_cn = 0
        self._cur_text = []
        self._cur_exercise = None
        self._capture = None      # which field of exercise we're appending text to
        self._cloze_text = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        classes = d.get("class", "").split()
        self._stack.append((tag, classes, d))
        if tag == "div" and "exercise" in classes:
            self._cur_exercise = {
                "type": d.get("data-exercise", "?"),
                "answers": (d.get("data-answer", "") or "").split("|"),
                "cloze_answers": d.get("data-answers", ""),
                "prompt": "",
                "chunks": [],
                "choices": [],
                "correct_count": 0,
                "has_feedback": False,
                "has_input": False,
                "has_check": False,
                "has_reveal_btn": False,
                "has_reveal_box": False,
                "has_textarea": False,
                "blank_keys": [],
                "bank_words": [],
                "reveal_text": "",
                "line": self.getpos()[0],
            }
            self.exercises.append(self._cur_exercise)
        ex = self._cur_exercise
        if ex is not None:
            if tag == "p" and "prompt" in classes:
                self._capture = "prompt"
            elif "chunk" in classes:
                self._capture = "chunk"
                ex["chunks"].append("")
            elif tag == "li" and self._in("choices"):
                ex["choices"].append("")
                self._capture = "choice"
                if d.get("data-correct") == "true":
                    ex["correct_count"] += 1
            elif "feedback" in classes:
                ex["has_feedback"] = True
            elif tag == "input":
                ex["has_input"] = True
            elif tag == "textarea":
                ex["has_textarea"] = True
            elif tag == "button" and "check" in classes:
                ex["has_check"] = True
            elif tag == "button" and "reveal" in classes:
                ex["has_reveal_btn"] = True
            elif "reveal-box" in classes:
                ex["has_reveal_box"] = True
                self._capture = "reveal"
            elif "blank" in classes and d.get("data-key"):
                ex["blank_keys"].append(d["data-key"])
            elif "word" in classes and d.get("data-word"):
                ex["bank_words"].append(d["data-word"])
        # taught examples
        if tag == "p" and "cn" in classes and self._in("ex") and ex is None:
            self._in_ex_cn = 1
            self._cur_text = []

    def _in(self, cls):
        return any(cls in c for _, c, _ in self._stack)

    def handle_endtag(self, tag):
        if self._in_ex_cn and tag == "p":
            self.taught.append("".join(self._cur_text))
            self._in_ex_cn = 0
        if self._cur_exercise is not None and tag == "div":
            # closing the exercise div? check stack depth
            pass
        if self._stack:
            popped_tag, popped_classes, _ = self._stack.pop()
            if self._cur_exercise is not None and popped_tag == "div" and "exercise" in popped_classes:
                self._cur_exercise = None
            if self._capture and popped_tag in ("p", "span", "li", "div"):
                if (self._capture == "prompt" and popped_tag == "p") or \
                   (self._capture == "chunk" and popped_tag == "span") or \
                   (self._capture == "choice" and popped_tag == "li") or \
                   (self._capture == "reveal" and popped_tag == "div" and "reveal-box" in popped_classes):
                    self._capture = None

    def handle_data(self, data):
        if self._in_ex_cn:
            self._cur_text.append(data)
        ex = self._cur_exercise
        if ex is None or not self._capture:
            return
        if self._capture == "prompt":
            ex["prompt"] += data
        elif self._capture == "chunk" and ex["chunks"]:
            ex["chunks"][-1] += data
        elif self._capture == "choice" and ex["choices"]:
            ex["choices"][-1] += data
        elif self._capture == "reveal":
            ex["reveal_text"] += data


def parse(path: Path) -> DocParser:
    p = DocParser()
    p.feed(path.read_text(encoding="utf-8"))
    return p


# ---------------------------------------------------------------- vocab lexicon
def load_lexicon():
    words = set()
    for f in ["hsk_1.txt", "hsk_1_alt.txt", "hsk_2.txt", "hsk_3.txt"]:
        for line in (ROOT / "wordlists" / f).read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                # Chinese column: strip parenthetical variants like 这 (这儿)
                cn = parts[1]
                for token in re.split(r"[（()）/、,，\s]+", cn):
                    token = han_only(token)
                    if token:
                        words.add(token)
    # cast names, place names the app uses, and derived time words
    words |= {
        "小丽", "小刚", "小", "丽", "刚",
        "纽约", "首尔", "北京", "上海", "韩国", "中国", "美国",
        "后天", "前天", "前年", "明年", "去年", "今年", "以前", "以后", "之后", "之前",
        "聊天", "聊天儿", "上个", "下个", "这个", "每天", "明天", "昨天", "今天",
    }
    return words


def page_vocab(path: Path) -> set:
    """Words from the page's own New vocabulary table + any han in taught text is NOT included."""
    text = path.read_text(encoding="utf-8")
    words = set()
    m = re.search(r"vocab-overview.*?</table>", text, re.S)
    if m:
        for td in re.findall(r"<td>([^<]+)</td>", m.group(0)):
            token = han_only(td)
            if token:
                words.add(token)
    return words


def segment_unknown(s: str, lexicon: set) -> list:
    """Greedy longest-match; returns unmatched han substrings."""
    s = han_only(s)
    unknown = []
    i = 0
    while i < len(s):
        for L in range(min(6, len(s) - i), 0, -1):
            if s[i:i + L] in lexicon:
                i += L
                break
        else:
            unknown.append(s[i])
            i += 1
    # merge adjacent singles
    merged, cur = [], ""
    prev_end = None
    for ch in unknown:
        cur += ch
    return ["".join(unknown)] if unknown else []


def exercise_chinese(ex: dict) -> list:
    """All Chinese strings belonging to an exercise (prompt, answers, chunks, choices)."""
    out = []
    for a in ex["answers"]:
        if han_only(a):
            out.append(a)
    if ex["chunks"]:
        out.append("".join(ex["chunks"]))
    for c in ex["choices"]:
        if han_only(c):
            # strip the .why rationale which got concatenated - take up to first ✓/✗
            c2 = re.split(r"[✓✗]", c)[0]
            out.append(c2)
    if han_only(ex["prompt"]):
        out.append(ex["prompt"])
    for part in ex["cloze_answers"].split(";"):
        if ":" in part:
            out.append(part.split(":", 1)[1])
    return out


# ---------------------------------------------------------------- checks
def run(files, against):
    lexicon = load_lexicon()
    against_taught = []
    for f in against:
        dp = parse(f)
        against_taught += [(t, f.name) for t in dp.taught]

    failures = 0
    for f in files:
        dp = parse(f)
        pv = page_vocab(f)
        lex = lexicon | pv
        taught = [(t, f.name) for t in dp.taught] + against_taught
        taught_norm = [(norm(t), src, t) for t, src in taught if han_only(t)]

        print(f"\n{'='*70}\n{f.name}: {len(dp.exercises)} exercises, {len(dp.taught)} taught examples")

        # counts
        counts = {}
        for ex in dp.exercises:
            counts[ex["type"]] = counts.get(ex["type"], 0) + 1
        print("  COUNTS:", dict(sorted(counts.items(), key=lambda kv: -kv[1])))

        # overlap
        exact, close = [], []
        for ex in dp.exercises:
            for cn in exercise_chinese(ex):
                n = norm(cn)
                if len(han_only(n)) < 5:
                    continue
                for tn, src, traw in taught_norm:
                    if len(tn) < 5:
                        continue
                    if n == tn or (tn in n) or (n in tn and len(n) >= 7):
                        exact.append((ex["line"], ex["type"], cn.strip()[:40], src))
                    elif SequenceMatcher(None, n, tn).ratio() > 0.85:
                        close.append((ex["line"], ex["type"], cn.strip()[:30], traw.strip()[:30], src))
        if exact:
            failures += len(exact)
            print(f"  OVERLAP-EXACT ({len(exact)}):")
            for line, t, cn, src in exact[:15]:
                print(f"    L{line} [{t}] {cn}  == taught in {src}")
        if close:
            print(f"  OVERLAP-CLOSE ({len(close)}) [review manually]:")
            for line, t, cn, traw, src in close[:10]:
                print(f"    L{line} [{t}] {cn} ~ {traw} ({src})")
        if not exact and not close:
            print("  OVERLAP: clean")

        # vocab
        vocab_issues = []
        for ex in dp.exercises:
            for cn in exercise_chinese(ex):
                for unk in segment_unknown(cn, lex):
                    if unk:
                        vocab_issues.append((ex["line"], unk, cn.strip()[:30]))
        vocab_issues = [(l, u, c) for l, u, c in vocab_issues if len(u) >= 2]
        if vocab_issues:
            seen = set()
            uniq = [(l, u, c) for l, u, c in vocab_issues if not (u in seen or seen.add(u))]
            print(f"  VOCAB ({len(uniq)} unique unknown strings) [review manually]:")
            for line, unk, cn in uniq[:20]:
                print(f"    L{line} '{unk}' in: {cn}")
        else:
            print("  VOCAB: clean")

        # lint
        lint = []
        for ex in dp.exercises:
            t = ex["type"]
            if t in ("fill", "builder", "match", "cloze") and not ex["has_feedback"]:
                lint.append((ex["line"], t, "missing .feedback"))
            if t in ("mc", "si") and ex["correct_count"] != 1:
                lint.append((ex["line"], t, f"data-correct=true count = {ex['correct_count']}"))
            if t == "fill" and not ex["has_input"]:
                lint.append((ex["line"], t, "missing <input>"))
            if t == "builder":
                joined = norm("".join(ex["chunks"]))
                for a in ex["answers"]:
                    an = norm(a)
                    if an and sorted(joined) != sorted(an) and not _composable(ex["chunks"], an):
                        lint.append((ex["line"], t, f"chunks can't compose answer: {a[:30]}"))
                        break
            if t == "cloze":
                keys = {}
                for part in ex["cloze_answers"].split(";"):
                    if ":" in part:
                        k, v = part.split(":", 1)
                        keys[k.strip()] = v.strip()
                for bk in ex["blank_keys"]:
                    if bk not in keys:
                        lint.append((ex["line"], t, f"blank key '{bk}' not in data-answers"))
                for k, v in keys.items():
                    if ex["bank_words"] and v not in ex["bank_words"]:
                        lint.append((ex["line"], t, f"answer '{v}' not in wordbank"))
                    if any(ch in PUNCT for ch in v):
                        lint.append((ex["line"], t, f"punctuation in cloze answer '{v}'"))
            if t == "reveal" and not ex["has_reveal_box"]:
                lint.append((ex["line"], t, "reveal without .reveal-box"))
            if ex["has_reveal_box"] and t not in ("fill", "reveal"):
                lint.append((ex["line"], t, ".reveal-box outside fill/reveal"))
        if lint:
            failures += len(lint)
            print(f"  LINT ({len(lint)}):")
            for line, t, msg in lint:
                print(f"    L{line} [{t}] {msg}")
        else:
            print("  LINT: clean")

    print(f"\n{'='*70}\nHARD FAILURES (exact overlap + lint): {failures}")
    return failures


def _composable(chunks, target):
    """Can some subset/order of chunks concatenate to target? (greedy check)"""
    from functools import lru_cache
    chunks = [norm(c) for c in chunks if norm(c)]

    @lru_cache(maxsize=None)
    def solve(rest, used):
        if not rest:
            return True
        for i, c in enumerate(chunks):
            if not (used >> i) & 1 and rest.startswith(c):
                if solve(rest[len(c):], used | (1 << i)):
                    return True
        return False

    return solve(target, 0)


if __name__ == "__main__":
    args = sys.argv[1:]
    against = []
    if "--against" in args:
        i = args.index("--against")
        against = [Path(a) if "/" in a else APP / a for a in args[i + 1:]]
        args = args[:i]
    files = [Path(a) if "/" in a else APP / a for a in args]
    sys.exit(1 if run(files, against) else 0)
