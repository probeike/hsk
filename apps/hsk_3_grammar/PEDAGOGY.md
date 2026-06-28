# HSK 3 Grammar & Reading — Pedagogy and Authoring Guide

This document records the **why** behind the grammar lessons (`lessonNN.html`) and the reading workouts
(`readingNN.html`) in this folder, plus the concrete conventions that encode it. Read it before adding or
revising any lesson/reading so the collection stays coherent. It is written for both humans and future
agents.

The audience is an **English-speaking adult** learning Mandarin alongside the official *HSK Standard Course
3* textbook. Everything here serves that learner.

---

## 1. Pedagogical foundations

The design is grounded in mainstream second-language-acquisition (SLA) research for English→Mandarin
learners. Five ideas drive it (they are also stated on `index.html`):

1. **Function before form.** Teach *when a speaker reaches for a structure* before any rule about its shape.
   A learner who knows the communicative job of 把/被/了 acquires the form faster than one who memorises a
   pattern in the abstract.
2. **Name the "English trap."** For each structure, call out the specific English-speaker instinct that
   misleads (e.g. reaching for the verb first, reading 少 as "few", treating 那 as the demonstrative "that").
   Misconceptions that are named are easier to unlearn.
3. **Image schemas.** Give markers (把, 被, 着, 了, 会) a reusable mental picture; reuse the same icon/colour
   whenever the marker reappears so the image consolidates across lessons.
4. **Contrastive minimal pairs.** Show one sentence with vs without the structure (or one word order vs
   another) and spell out the meaning delta — 吃完 vs 吃好, 才 vs 就, 刚 vs 刚才.
5. **Processing-instruction tasks.** For structures that rewire word order (把, 被), use exercises that force
   the learner to *decode the marker to get meaning right*, training them past the "first noun = doer"
   instinct rather than just producing the pattern.

The reading files add four more, from research on extensive reading and vocabulary acquisition:

6. **Comprehensible input (i+1).** Text should be ~90%+ understandable, with new material inferable from
   context. The cumulative vocabulary rule (§3) builds this automatically.
7. **Forced recycling.** Words and structures must *reappear* across passages and lessons, not be met once.
   Cumulative scoping guarantees earlier vocab keeps returning.
8. **Productive, cognitively-engaging output.** Reconstruction, translation, and free writing beat passive
   recognition. Every reading file ends with productive tasks (§5, Part 2).
9. **Varied contexts for transfer.** The *same* grammar shown across *different* everyday domains (cooking,
   shopping, sport, work) generalises better than the same structure always tied to one scenario (§6).

---

## 2. The two file types and how they relate

- **`lessonNN.html` — grammar walkthrough (reference).** One HSK 3 chapter's grammar, taught from first
  exposure to practice. This is where a structure is *explained*.
- **`readingNN.html` — reading & writing workout (practice).** ~1 hour of graded reading + exercises that
  *apply* the grammar in connected text. This is where a structure is *used*.

They are paired and cross-linked (top and bottom nav of each lesson links to its reading, and vice versa).
`index.html` lists both. Appendices (`particles.html`, `three-le.html`) cover cross-cutting patterns owned
by no single lesson.

---

## 3. The cumulative comprehensible-input rule (non-negotiable)

**Reading/lesson `N` may use only:**
- All **HSK 1 + HSK 2** vocabulary (≈300 words), plus
- **HSK 3 vocabulary from lessons 1…N** (never N+1 or later), and
- **grammar structures from HSK 3 lessons 1…N** (the lesson's own structures are the focus; earlier ones mix
  in for recycling).

**Allowances** that keep prose natural without breaking the rule:
- **Proper names** (人名/地名: 小丽, 小刚, 北京…) freely.
- **≤ 2 "glossed" words per passage** that fall outside the allowed set, each marked inline:
  `词<span class="gloss-note">(pīnyīn — meaning)</span>`. Use sparingly.
- Common single characters that combine allowed words (们, 不, 没, 很, basic numbers/measure words) are fine.

So `reading01` is the narrowest (HSK1–2 + L1 only — a tight pool; expect to reword a lot); `reading20` may
draw on the whole course. **Always verify** new prose against the allowed set for that exact N (see §8).

Data sources for the allowed set (read these; don't invent vocab):
- `../../wordlists/hsk_1.txt`, `hsk_2.txt`, `hsk_3.txt` — tab-separated word lists.
- `../../knowledge/hsk_3/lesson_0N.md` — per-lesson vocab table + `grammar_introduced` YAML.
- `../../lesson_texts/hsk_3/HSK3-LessonNN.txt` — OCR of the real textbook chapter (themes, dialogue style).

---

## 4. Grammar lesson (`lessonNN.html`) conventions

Standard skeleton: `head` → `nav.topnav` → `header.lesson-hero` (title, pinyin, English) → `section.overview`
("What you'll learn") → numbered `section.gp` grammar points → "Mixed practice" → `nav.lesson-nav` →
`<script src="script.js">`.

Within each grammar point (`section.gp`), use these building blocks (all already styled in `styles.css`):
- `.when` — "When a speaker reaches for this" (function first, principle 1).
- `.callout.trap` — "The English trap" (principle 2). Also `.callout.pts` (temporal-sequence note),
  `.callout.pitfall` (common error).
- `.schema` — an inline SVG image schema + `.caption` (principle 3).
- `.formula` — dark box with colour-coded slots showing the structure's shape.
- `.ex` — worked example: `.cn` (Chinese) / `.py` (pinyin) / `.gloss` (interlinear) / `.en` (translation).
- `.contrast` — two-column minimal pair with `.label` / `.cn` / `.mean` (principle 4).
- `.exercise` widgets for practice (§7).

**Colour-coding is global and consistent** — reuse the same role colours everywhere, via inline spans inside
`.han`/`.cn`:
`.subject` (blue) · `.verb` (green) · `.object` (orange) · `.marker` (purple: 把/被/着/了/会/呢) ·
`.complement` (teal: result/directional/state complements). Don't recolour roles per lesson.

---

## 5. Reading workout (`readingNN.html`) structure

Each reading file is a **two-part, 9-section** workout (~700–900 hanzi of reading, 23–24 exercises),
modelled on the real HSK textbook 课文 + the HSK reading exam. Keep this shape:

**Part 1 · 阅读 (Reading)** — a `section.overview` divider, then:
1. **课文** — a multi-turn dialogue scene (~280–350 hanzi) + 4 comprehension MC.
2. **配对** — sentence matching, 5 pairs (`data-exercise="match"`).
3. **短文** — a narrative passage (~250–300 hanzi) + 3–4 MC.
4. **选词填空** — word-bank cloze with one extra distractor (`data-exercise="cloze"`).
5. **阅读** — 3–4 short exam-style mini-passages, one MC each.
6. **判断对错** — 4 true/false items (MC widget with 对/错 choices).

**Part 2 · 练习 (Practice)** — a divider, then productive output (principle 8):
7. **连词成句** — 2 sentence builders (`data-exercise="builder"`).
8. **翻译** — 3 English→Chinese (`data-exercise="fill"` + reveal model).
9. **写一写** — free-writing prompt + `reveal` model answer (allowed vocab only).

Receptive → productive ordering is deliberate. The passages are the heart; the drills consolidate.

**Reading-specific conventions:**
- Each passage lives in a `.reading-text` box. The **`.py-toggle` button must be the first child** (the JS
  uses `btn.closest('.reading-text')`); pinyin (`.py`) is hidden by default and revealed on toggle — this
  forces real character reading.
- Dialogue turns: `<span class="speaker">名：</span>… <br>`.
- Use the role colour-spans only to **spotlight the lesson's target grammar** in a passage; passages should
  otherwise read as plain text (don't rainbow everything).

---

## 6. Topic variety (how to keep readings from going stale)

A real failure mode: passages over-recycle the *current lesson's own new words* and one situation, so the
whole file reads like "did you bring the map and water / finished the homework" on repeat. Avoid it:

- **Per-passage variety.** Within a file, the 课文 / 短文 / 阅读 passages must each be a **different**
  everyday scenario, so the target grammar is seen across multiple domains (principle 9). Each passage stays
  internally coherent (one mini-scene).
- **Draw on the whole allowed pool**, not just lesson N's ~17 new words — pull nouns/verbs from all of
  HSK 1–2 and earlier HSK 3.
- **Keep the recurring cast** (小丽, 小刚, 妈妈, 老师, …) so the learner isn't constantly relearning
  characters — vary the *situations*, not the people.
- **Topic palette to rotate:** cooking/eating, shopping, sport/exercise, work/office, family visit,
  weather/seasons, health/feeling unwell, hobbies (music/photos/reading), transport, tidying, parties,
  phones/computers, evening plans, the weekend.
- **Worn-motif blocklist** (avoid unless genuinely apt for the lesson, and never let one dominate a file):
  作业, 复习, 考试, 地图, 面包, 带, 南方, 北方, 机场, 飞机, "bring water". The result-complement 好, for
  instance, shines in 做好饭 / 买好票 / 准备好 — many domains, not just 写好作业.
- The grammar must still be the star: every passage should clearly exercise the lesson's target
  structure(s), occasionally weaving in an earlier one.

---

## 7. Exercise widgets (shared `script.js`)

All interactivity is wired on `DOMContentLoaded` by `data-exercise` attribute — no per-page JS. Authors only
write markup; never add inline `<script>`. Available types:

| `data-exercise` | Purpose | Answer mechanism |
|---|---|---|
| `fill` | type-in blank / translation | `data-answer="a|b"` (`|` = alternatives; punctuation/space-insensitive). Optional `.reveal` + `.reveal-box`. |
| `mc` | multiple choice / true-false | `<li data-correct="true|false">` + `.why` rationale. **Exactly one** correct. |
| `si` | "what does this mean?" interpretation | reuses the MC widget. |
| `builder` | sentence reordering | `.bank` of `.chunk`s → `.drop`; `data-answer="…"` (alternatives with `|`). Bank shuffles on load. |
| `match` | pairing (配对) | left items `data-key="a…"`, correct right item `data-match="a…"` (same id). 5 pairs; right column shuffles. |
| `cloze` | word-bank fill (选词填空) | `data-answers="key:word;…"` maps each `.blank data-key` to its word; bank = answers **+ exactly one distractor**. |
| `reveal` | show a model answer / note | `.reveal` button toggles `.reveal-box`. |
| `.py-toggle` | show/hide a passage's pinyin | first child of its `.reading-text`. |

When adding new widget *types*, add the wiring to `script.js` and styles to `styles.css` **once**, and keep
existing widgets untouched.

**Authoring invariants the verification scripts enforce (§8):** every `mc`/`si` has exactly one
`data-correct="true"`; every `match` has equal left `data-key` and right `data-match` id-sets (5 each); every
`cloze`'s `data-answers` keys equal its `.blank` keys, all answers appear in the bank, and the bank has
exactly one extra distractor.

---

## 8. Verification before considering work done

Run these checks (scripts have lived in the session scratchpad; reproduce as needed) after any edit:

1. **Vocab gate.** Extract Han characters from every passage (`<p class="cn">`) and answer (`data-answer`,
   `data-word`, MC text) and diff against the allowed cumulative set for that N (HSK1–2 + HSK3 L1…N + that
   file's glossed words + proper names). Investigate every flag. (Note: an inline gloss that *follows* the
   word won't be auto-credited by a naive scanner — confirm flagged items are genuinely glossed or are
   target grammar like 把/被/使.)
2. **Widget integrity.** Check the invariants in §7 across all files.
3. **Motif scan.** Count the worn-motif words (§6) per file's passages; no file should be dominated by one
   motif (rule of thumb: < ~8 hits, no single motif ≫ others).
4. **Structure/nav.** 9 `section.gp`, `.py-toggle` first child of each `.reading-text`, `reading20`'s "next"
   links disabled, lesson↔reading cross-links intact.
5. **Render check (do not skip).** Open `index.html` → a lesson and a reading in a browser; click through one
   of each widget type (mc, fill, builder, match, cloze, py-toggle, reveal) to confirm the interactions and
   that comprehension questions read correctly against their passages. Static checks can't catch a question
   that no longer matches a rewritten passage.

---

## 9. Hard constraints (don't violate)

- **Offline-first.** No CDN, no web fonts, no external assets, no network calls. Everything works from the
  local filesystem.
- **Shared files are shared.** `styles.css`, `script.js`, and `index.html` are edited once and centrally;
  per-lesson work should not fork them. Reuse existing classes/widgets rather than inventing parallel ones.
- **Don't break the cumulative rule** for the sake of a nicer sentence — reword, or use a ≤2/passage gloss.
- **Keep the cast and the colour-coding stable** across the whole collection.
