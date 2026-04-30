#!/usr/bin/env python3
"""Build per-lesson vocab + grammar text files from HSK-1 and HSK-2 OCR output."""
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OCR = Path(__file__).resolve().parent
LESSON_TEXTS = REPO_ROOT / "lesson_texts"

# Page ranges are 1-indexed PDF pages where the lesson title page appears.
HSK1 = {
    "title_en": "HSK Standard Course 1 (Student Book)",
    "lessons": [
        (1,  22,  27, "你好",                 "Ni hao",                          "Hello"),
        (2,  28,  33, "谢谢你",                "Xiexie ni",                       "Thank you"),
        (3,  34,  41, "你叫什么名字",           "Ni jiao shenme mingzi",           "What's your name"),
        (4,  42,  49, "她是我的汉语老师",       "Ta shi wo de Hanyu laoshi",       "She is my Chinese teacher"),
        (5,  50,  59, "她女儿今年二十岁",       "Ta nv'er jinnian ershi sui",      "Her daughter is 20 years old this year"),
        (6,  60,  67, "我会说汉语",             "Wo hui shuo Hanyu",               "I can speak Chinese"),
        (7,  68,  75, "今天几号",               "Jintian ji hao",                  "What's the date today"),
        (8,  76,  83, "我想喝茶",               "Wo xiang he cha",                 "I'd like some tea"),
        (9,  84,  91, "你儿子在哪儿工作",       "Ni erzi zai nar gongzuo",         "Where does your son work"),
        (10, 92, 101, "我能坐这儿吗",           "Wo neng zuo zher ma",             "Can I sit here"),
        (11,102, 109, "现在几点",               "Xianzai ji dian",                 "What's the time now"),
        (12,110, 117, "明天天气怎么样",         "Mingtian tianqi zenmeyang",       "What will the weather be like tomorrow"),
        (13,118, 125, "他在学做中国菜呢",       "Ta zai xue zuo Zhongguo cai ne",  "He is learning to cook Chinese food"),
        (14,126, 133, "她买了不少衣服",         "Ta mai le bushao yifu",           "She has bought quite a few clothes"),
        (15,134, 141, "我是坐飞机来的",         "Wo shi zuo feiji lai de",         "I came here by air"),
    ],
    "ocr_dir": OCR / "hsk1_txt",
    "page_fmt": "p-{:03d}.png.txt",
}

HSK2 = {
    "title_en": "HSK Standard Course 2 (Student Book)",
    "lessons": [
        (1,  17,  24, "九月去北京旅游最好",     "Jiu yue qu Beijing lvyou zui hao", "September is the best time to visit Beijing"),
        (2,  25,  32, "我每天六点起床",         "Wo mei tian liu dian qichuang",   "I get up at six every day"),
        (3,  33,  40, "左边那个红色的是我的",   "Zuobian nage hongse de shi wo de","The red one on the left is mine"),
        (4,  41,  48, "这个工作是他帮我介绍的", "Zhege gongzuo shi ta bang wo jieshao de", "He recommended me for this job"),
        (5,  49,  56, "就买这件吧",             "Jiu mai zhe jian ba",             "Take this one"),
        (6,  57,  64, "你怎么不吃了",           "Ni zenme bu chi le",              "Why don't you eat more"),
        (7,  65,  72, "你家离公司远吗",         "Ni jia li gongsi yuan ma",        "Do you live far from your company"),
        (8,  73,  80, "让我想想再告诉你",       "Rang wo xiangxiang zai gaosu ni", "Let me think about it and I'll tell you later"),
        (9,  81,  90, "题太多，我没做完",       "Ti tai duo, wo mei zuo wan",      "There were too many questions; I didn't finish all of them"),
        (10, 91,  98, "别找了，手机在桌子上",   "Bie zhao le, shouji zai zhuozi shang", "Stop looking for your cell phone; it's on the desk"),
        (11, 99, 106, "他比我大三岁",           "Ta bi wo da san sui",             "He is three years older than me"),
        (12,107, 114, "你穿得太少了",           "Ni chuan de tai shao le",         "You're wearing too little"),
        (13,115, 122, "门开着呢",               "Men kai zhe ne",                  "The door is open"),
        (14,123, 130, "你看过那个电影吗",       "Ni kanguo nage dianying ma",      "Have you seen that movie"),
        (15,131, 140, "新年就要到了",           "Xinnian jiu yao dao le",          "The New Year is coming"),
    ],
    "ocr_dir": OCR / "hsk2_txt",
    "page_fmt": "p-{:03d}.png.txt",
}


def load_page(ocr_dir: Path, page: int, fmt: str) -> str:
    f = ocr_dir / fmt.format(page)
    if not f.exists():
        return ""
    return f.read_text(encoding="utf-8", errors="replace")


def strip_page_chrome(txt: str) -> str:
    """Remove standard headers/footers that repeat on every page."""
    lines = txt.splitlines()
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            out.append(ln)
            continue
        if re.match(r"^标准教程\s*[12]\s*$", s):
            continue
        if re.match(r"^Standard Course\s*[12I工]\s*$", s):
            continue
        out.append(ln)
    return "\n".join(out)


# ------ Vocabulary extractor ------
# Lines that look like a vocab entry. Format is typically:
#   N. <Chinese>  <pinyin>  <pos>  <gloss>
# OCR corrupts this a lot; we keep blocks around "New Word" / "生词" headings.

VOCAB_HEADER_RE = re.compile(r"(New Word[s]?|New Word|生\s*词|Proper Noun[s]?|专有名词)", re.IGNORECASE)
NOTE_HEADER_RE  = re.compile(r"(注\s*释|Notes|语言点|Language Point[s]?)")
EXERCISE_RE     = re.compile(r"(练\s*习|Exercises|运\s*用|Application|小组活动|Group Work|双人活动|Pair Work|Role-play|Describe the pictures)")


def extract_blocks(pages_txt: list[tuple[int, str]]) -> dict:
    """Pull (vocab_lines, grammar_lines, raw) from a list of (page_no, text) pages."""
    full = []
    for pno, t in pages_txt:
        full.append(f"\n----- PDF page {pno} -----\n{t}")
    raw = "".join(full)

    vocab_chunks = []
    grammar_chunks = []

    for pno, t in pages_txt:
        t = strip_page_chrome(t)
        lines = t.splitlines()
        mode = None
        buf = []

        def flush():
            nonlocal buf, mode
            if buf:
                chunk = "\n".join(buf).strip()
                if chunk:
                    if mode == "vocab":
                        vocab_chunks.append(f"[PDF p.{pno}]\n{chunk}")
                    elif mode == "grammar":
                        grammar_chunks.append(f"[PDF p.{pno}]\n{chunk}")
                buf = []

        for ln in lines:
            s = ln.strip()
            if VOCAB_HEADER_RE.search(s):
                flush()
                mode = "vocab"
                buf.append(ln)
                continue
            if NOTE_HEADER_RE.search(s):
                flush()
                mode = "grammar"
                buf.append(ln)
                continue
            if EXERCISE_RE.search(s):
                flush()
                mode = None
                continue
            if mode:
                buf.append(ln)
        flush()

    return {
        "vocab": "\n\n".join(vocab_chunks).strip(),
        "grammar": "\n\n".join(grammar_chunks).strip(),
        "raw": raw,
    }


def build_book(cfg: dict, out_file: Path):
    sections = []
    sections.append("=" * 78)
    sections.append(cfg["title_en"])
    sections.append("Vocabulary and Grammar Structures — extracted via OCR from the PDF.")
    sections.append("=" * 78)
    sections.append("")

    for (num, p0, p1, zh, py, en) in cfg["lessons"]:
        pages = []
        for pg in range(p0, p1 + 1):
            t = load_page(cfg["ocr_dir"], pg, cfg["page_fmt"])
            if t:
                pages.append((pg, t))
        extracted = extract_blocks(pages)

        sections.append("#" * 78)
        sections.append(f"LESSON {num}: {zh}  ({py})")
        sections.append(f"  \"{en}\"")
        sections.append(f"  PDF pages {p0}-{p1}")
        sections.append("#" * 78)
        sections.append("")
        sections.append("--- VOCABULARY (生词 / New Words / Proper Nouns) ---")
        sections.append(extracted["vocab"] or "[No clean vocab block detected — see raw OCR below.]")
        sections.append("")
        sections.append("--- GRAMMAR / LANGUAGE POINTS (注释 / Notes) ---")
        sections.append(extracted["grammar"] or "[No clean grammar block detected — see raw OCR below.]")
        sections.append("")
        sections.append("--- RAW OCR (for verification, includes dialogues & warm-up) ---")
        sections.append(extracted["raw"])
        sections.append("")

    out_file.write_text("\n".join(sections), encoding="utf-8")
    print(f"Wrote {out_file} ({out_file.stat().st_size} bytes)")


if __name__ == "__main__":
    build_book(HSK1, LESSON_TEXTS / "hsk_1" / "HSK-1_lessons.txt")
    build_book(HSK2, LESSON_TEXTS / "hsk_2" / "HSK-2_lessons.txt")
