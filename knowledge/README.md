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
