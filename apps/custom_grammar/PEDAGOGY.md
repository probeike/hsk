# Pedagogy & authoring spec — custom grammar practice

This document records **why** the exercises in this app are built the way they are (research base,
2026-08 redesign), and **how** to author new ones (rules, target mixes, widget contract). Every
writer — human or agent — follows this spec.

## The problem this redesign fixed

An audit (2026-08-10) found that 49–66% of exercises across the lessons and sheets reused the exact
taught example sentences (timeline.html: 66%, 15 character-for-character; coverbs.html: 14/16;
shi-de-gallery: 9/11). Doing the exercises was answer-recall, not grammar practice. Separately, the
exercise diet was ~95% recognition: across ~137 lesson exercises there were only 5 typed full
sentences and zero free writing; the six drill sheets had no typed answer longer than 3 characters.
Vocabulary was extremely narrow (老板/辞职/舞蹈/跳舞/老师/纽约/地铁/公司 everywhere).

## Research base (what makes grammar stick)

1. **Retrieval practice / testing effect** — retrieval beats re-exposure by large margins on delayed
   tests; retrieval strength scales with effort (typed recall > word-bank > multiple choice).
   Recycling a taught sentence turns retrieval into recognition of the answer key.
   [Karpicke & Roediger 2008](http://psychnet.wustl.edu/memory/wp-content/uploads/2018/04/Karpicke-Roediger-2008_Sci.pdf) ·
   [Karpicke, Retrieval-Based Learning](https://files.eric.ed.gov/fulltext/ED599273.pdf)
2. **Output hypothesis / production effect** — comprehension can ride semantic shortcuts; only
   *production* forces full syntactic processing and exposes gaps. Recognition of 得 doesn't build
   the verb-copy rule; typing 他跳舞跳得很好 does.
   [Comprehensible output](https://en.wikipedia.org/wiki/Comprehensible_output)
3. **Structured input (VanPatten)** — input items where the form is the *only* clue to meaning are
   effective early, for form-meaning mapping — but output-trained learners do better on production.
   So `si` items stay, as stage 1 of each point, never the whole diet.
   [Processing Instruction](https://onlinelibrary.wiley.com/doi/10.1002/9781118784235.eelt0094)
4. **Transfer-appropriate processing** — you get good at what you practice; MC practice makes you
   good at MC tests. The practice endpoint per point must be *generating* sentences.
   [Lightbown, TAP](https://www.researchgate.net/publication/292461381_Transfer_appropriate_processing_as_a_model_for_classroom_second_language_acquisition)
5. **Variability of practice** — varied items build the generalizable schema; constant items build
   item-specific memory. Variability is what tells the brain which features are structural (的 after
   the modifier) vs incidental (the word 咖啡). **This is the direct scientific answer to the
   recycling problem.** [Variability of Practice](https://link.springer.com/10.1007/978-1-4419-1428-6_415) ·
   [Raviv et al. 2022](https://phys.org/news/2022-05-variability.html)
6. **Interleaving** — interleaved practice of confusable structures (的/得/地, 不/没) beats blocked
   practice for discrimination; block briefly per point, interleave hard in mixed practice, and
   revisit other lessons' structures. [Suzuki et al. 2022](https://journals.sagepub.com/doi/abs/10.1177/1362168820913985) ·
   [Suzuki, Nakata & DeKeyser 2019](https://onlinelibrary.wiley.com/doi/abs/10.1111/modl.12582)
7. **Personalization / self-generated content** — self-referential encoding measurably improves L2
   retention; "write about YOUR week/dance class/commute" prompts are high-value.
   [Self-reference & vocabulary 2025](https://link.springer.com/article/10.3758/s13423-025-02674-w)
8. **Errorful learning + explained feedback** — generating an error and receiving corrective
   feedback *helps*; error-correction exercises are effective and cheap; every reveal explains
   *why*, not just the answer. [Metcalfe 2017](https://www.columbia.edu/cu/psychology/metcalfe/PDFs/Learning%20from%20errorsAnnual%20ReviewMetcalfe2016.pdf)
9. **Skill acquisition theory (DeKeyser)** — declarative rule → proceduralized through *varied use*.
   Identical drills don't proceduralize; short declarative phase, then many varied production reps.
   [DeKeyser & Suzuki 2025](https://yuichisuzuki.net/wp-content/uploads/2025/07/PreprintDeKeyser-R.-M.-Suzuki-Y.-2025.-Skill-acquisition-theory.-In-B.-VanPatten-G.-D.-Keating-S.-Wulff-Eds.-Theories-in-second-language-acquisition-An-introduction-4th-ed.-pp.-157-182-.pdf)

## Exercise typology — 5 stages per grammar point

Stage order within each grammar point section: **Notice → Discriminate → Cue → Construct → Own it.**
Not every point needs all five; every point needs at least one item from stage 3+.

| Stage | Function | Widget | Format |
|---|---|---|---|
| 1. Structured input | Form→meaning; the form is the only clue | `si` | "Which meaning?" where only the target morpheme disambiguates |
| 2. Discrimination | Choose between confusable forms | `mc`, `match` | Minimal pairs differing in exactly one dimension; distractors = real learner errors |
| 3. Cued production | Retrieve the form, small typed unit | `fill` (short), `cloze` | Blank the *decision point*, sentence content novel |
| 4. Constrained construction | Build the whole sentence | `builder`, `fill` (full sentence) | Formats F1–F4 below |
| 5. Free production | Own it with personal content | `reveal` (textarea + model + checklist) | Format F5 |

### The five production formats (all zero-JS-change)

- **F1 Transformation** (`fill`, full sentence): give a sentence, ask for a systematic change, type
  the whole result. Polarity flip (我看了那个电影 → negative → `我没看那个电影|我没有看那个电影` —
  teaches 了-drop under 没), aspect shift, intensify-to-"not even one". The single highest-value
  format: it makes the learner *operate the rule*.
- **F2 EN→CN translation** (`fill`, full sentence, constrained): English prompt + "用: …" word
  constraint so the answer space is enumerable.
- **F3 Error correction**: graded via `fill` when repairs are enumerable ("Find the error, type the
  corrected sentence"); via `reveal` when several repairs are fine. Errors must be attested
  English-speaker errors.
- **F4 Q→A production** (`fill`, full sentence): a question the target structure naturally answers —
  你吃早饭了吗？(No — not yet) → `我还没吃早饭呢|我还没吃早饭|我还没有吃早饭呢`. Closest a static
  page gets to communicative use.
- **F5 Personalize it** (`reveal`): micro free-writing per point ("Write ONE true sentence about
  something you still haven't done this week. Use 还没…呢") with model answer **plus 3–5-item
  self-check checklist** keyed to probable errors. Plus one integrative end-of-lesson prompt.

Also allowed: **think-then-check rule retrieval** (`reveal`) at the top of mixed practice — "From
memory: what's the difference between 不 and 没? Say it out loud, then check."

## Grading model — every exercise is exactly one tier

1. **Closed, mechanical** (mc / si / match / cloze / builder / short fill): one correct answer by design.
2. **Constrained production, mechanical** (full-sentence `fill`): the prompt pins content (subject
   given, required words listed) so valid answers are enumerable; `data-answer` lists **every**
   natural variant, `|`-separated, typically 3–8: word-order swaps (time-first/subject-first), 也/都,
   没/没有, optional 儿 and 的, alternative particle positions where natural. `norm()` already
   ignores punctuation and whitespace. **Hard rule: if you can't confidently cover the space in ~8
   variants, the item is under-constrained — tighten the prompt or demote to tier 3. A list that
   marks correct Chinese wrong is worse than no grading.**
3. **Open production, self-checked + AI-graded** (`reveal`): model answer + structural checklist;
   plus the script.js "Grade with AI" button (Claude call, see index/settings) for real feedback.
   The AI "Ask AI — is my answer actually OK?" fallback on rejected tier-2 fills is the runtime
   safety net behind the enumerate-everything rule.

QA enforcement: after writing, an independent checker role-plays the learner, produces 2–3 correct
answers per tier-2 item, and verifies each is accepted. Valid-but-rejected → add the variant or
demote; wrong-but-accepted → fix.

## Anti-memorization authoring rules (hard rules)

- **R1** No exercise reuses a taught example's subject+verb+object combination; ≥2 of the 3 content
  slots must change. Verbatim reuse of a taught sentence: zero. (mixed-review.html: applies against
  ALL files in the app.)
- **R2** Rotation quota: ≥5 distinct verbs and ≥5 distinct nouns per grammar point's exercise set;
  no content word in >2 of that point's exercises.
- **R3** Fills blank the *decision point* (的/得/地, 不/没, 也/都, marker position) — never a
  content word guessable from vocabulary alone.
- **R4** MC minimal pairs differ in exactly one dimension; distractors are attested English-speaker
  errors (他说汉语得很好; 我昨天不去; 我学中文一年), never gibberish. One "both are fine" item per
  lesson is allowed and valuable (e.g. 也 vs 都).
- **R5** Tier-2 fills follow the grading model above (constrained prompt, 3–8 complete alternatives).
- **R6** ≥50% of a file's exercise sentences describe situations that appear nowhere in its teaching
  text — new scenario, not just new nouns.
- **R7** Mixed/final sections are shuffled across points (never section order) and include 2–3 items
  retrieving *other* docs' structures — as fresh sentences, never copies.
- **R8** Every reveal-box explains *why*: correct answer + one-sentence metalinguistic rationale +
  (for traps) why the tempting wrong answer fails. House style: not-even-one.html's boxes.
- **R9** Free-writing reveals name the required structures and give a model + 3–5-item self-check
  checklist.

## Vocabulary policy

- Allowed pool: `wordlists/hsk_1.txt` + `wordlists/hsk_2.txt` + `wordlists/hsk_3.txt` (full HSK 3 —
  the learner's known words) + the page's own "New vocabulary" table + the cast names 小丽/小刚.
- Persona words (辞职, 老板, 舞蹈, 软件工程师, 压力, 纽约, dance/NYC/quitting-context) stay but are
  capped at ~1/3 of items; the rest use varied everyday scenarios (family, food, travel, weather,
  school, shopping, health, work-generic).

## Target mixes

**Lesson pages** (~40–44 exercises; was ~34 nearly-all-recognition):

| Category | Widgets | Count |
|---|---|---|
| Structured input / discrimination | si, mc, 1 match | ~11 |
| Cued production (short fill, novel sentences) | fill, cloze | ~9 |
| Sentence assembly (word-order-critical points only) | builder | ~3 |
| Transformation (F1) | fill | ~5 |
| Translation EN→CN (F2) | fill | ~5 |
| Q→A production (F4) | fill | ~3 |
| Error correction (F3) | fill + reveal | ~3 |
| Free production (F5) | reveal | ~3 |

**Sheets** (drill-first character preserved): every recycled item replaced with a fresh-vocab
equivalent; ~4–6 tier-2 typed items (F1/F2/F4) and 1–2 checklist reveals added per sheet.
shi-de-gallery grows 11→~18. complements-drill keeps its rapid-fire single-character fills but on
novel sentences. mixed-review is fully regenerated: interleaved retrieval of all structures with
new sentences tagged back to source sheets (S1–S5, C1–C3), zero copies.

**Reading pages**: Part 1 (comprehension) unchanged. Part 2 rebuilt to 8–9 productive items:
2 transformation fills anchored to passage sentences ("the passage says X; she has now arrived —
rewrite it"), 2 Q→A about the passage, 2 fresh translations, 1 error-correction (fix a bad summary
sentence), 1 from-memory retell reveal ("cover the passage, write 3–4 sentences"), 1
personalized-response reveal. Nothing recycled from the paired lesson.

## Widget contract (script.js) — authoring cheat sheet

| Goal | Type | Answer syntax |
|---|---|---|
| One-blank typed answer | `fill` | `data-answer="A\|B\|C"` on the container |
| Pick correct sentence | `mc` | `data-correct="true"` on exactly one `li` |
| Pick correct meaning | `si` | same as `mc` |
| Word-order drill | `builder` | `data-answer="…\|…"`; `.chunk` spans in `.bank`; chunks must compose every alternative |
| Match Q↔A | `match` | `data-key="x"` left ↔ `data-match="x"` right |
| Word-bank gap fill | `cloze` | `data-answers="a:词;b:词"`, `.blank[data-key]`; comparison is raw `===` — **no punctuation in cloze answers, no per-blank alternatives** |
| Free writing / self-check | `reveal` | none — `button.reveal` + `.reveal-box`; optional `.writing-area > textarea` |

Rules that bite:
- `.feedback` div required in every graded widget (fill/builder/match handlers dereference it unguarded).
- Exactly one `data-correct="true"` per mc/si.
- `fill` reads only the **first** `<input>` — one blank per card; use two cards or `cloze` for multi-blank.
- `norm()` strips whitespace and `，。！？?!,.` from both sides — but NOT `、；：""''`; keep those out of answers.
- Never place a `.reveal-box` outside a `fill` or `reveal` container (it can never open).
- Builder chunks are joined with no separator and compared against `data-answer` after `norm()`.
- Don't hand-author `.match-badge` (JS generates it). HTML injected after page load is inert.
- Structure/markup examples: copy an existing widget of the same type from the file being edited.

## File-writing protocol (learned the hard way)

- Teaching sections (`div.ex`, explanations, schemas) stay untouched unless the task says otherwise.
- Modify exercise blocks **in place with Edit calls** — one block or a small batch per edit. Never
  rewrite a ~1000-line file in a single Write call: streamed giant writes get killed mid-response
  and lose everything (happened 3× building not-even-one.html, 2026-08-10).
- New sections are inserted the same way, adjacent to related content.

## Learnings log

- **2026-08-10/11 (redesign):** template-first waves (one file reviewed before fan-out) keep 13
  parallel rewrites consistent. Adversarial answer-coverage QA (independent checker generating
  alternative answers) is the only reliable way to keep `|`-alternative lists honest — it found
  ~30 valid-but-rejected answers across the app, clustered on: split-的 forms with separable verbs
  (生的病, 见的面), the 没有 long form, 之前/以前, 那么 in 没有-comparisons, and 我的+kin-term.
  When in doubt between an incomplete graded list and a self-check reveal, demote to the reveal.
  The AI-grading button (Haiku via direct browser fetch) closes the remaining gap at runtime.
- Recognition items are cheap to author and feel productive; production items are the ones that
  transfer. When trimming for time, cut recognition, never production.
- **Mechanical verification:** run `python3 tools/check_exercises.py <file>.html` after any exercise
  edit (add `--against <paired files>` for mixed-review and the reading pages). It checks
  taught-sentence overlap, HSK 1–3 vocab (report is noisy on separable verbs — verify flags against
  the wordlists before acting), widget-contract lint, and counts.
- Watch reveal-box prose for contradictions with answer lists (two found and fixed: "never after
  打算", and a 很-filler rule the list itself violated). The QA pass should always read the reveal
  alongside the list.
