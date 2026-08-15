# Dynamic practice — design principles

The dynamic page turns the learner's current Anki vocabulary into a fresh set of interactive
grammar exercises on demand: the words being reviewed today are put to work in sentences today.
This document states the principles the page is built on. It deliberately says nothing about how
any of them are implemented.

## Anki is the source of truth for vocabulary

- The page reads the learner's live deck state through **AnkiConnect** (installed; available
  whenever Anki is open on this machine).
- What the learner "knows" is defined by Anki, not by a syllabus: the allowed vocabulary is the
  set of words the learner has actually been introduced to in the deck. No exercise may assume a
  word outside that set.
- The words currently under review drive each session, with priority given to words the learner
  is struggling with, then recently introduced words, then general review words.

## Words, not characters

- Vocabulary knowledge is tracked at the **word** level. The learner reads word-by-word, not
  character-by-character.
- A word is usable only if it has been learned as a word. Knowing every character inside a
  compound does not make the compound known, and new compounds must never be coined from known
  characters.

## Two tiers of vocabulary in every set

- **Target words** — explicitly selected by the learner — are drilled directly: each one appears
  in the exercises, and the exercises test it.
- Every other word in the current review pool is **passive**: preferred as supporting vocabulary
  inside sentences (incidental re-exposure), but never the point being tested, and never forced
  in where it reads unnaturally.

## Grammar scope is explicit

- All HSK 1 and HSK 2 structures are assumed known and always available.
- HSK 3 grammar is opt-in, lesson by lesson, through a clickable lesson list; only structures
  from ticked lessons may appear. The selection is remembered.
- Structures on the HSK 2/3 boundary (把, 被, result and directional complements, 得-complements)
  are treated as HSK 3 and gated accordingly.

## Exercise design

- Each set follows PEDAGOGY.md's five-stage arc, in rendered order: **structured input
  (meaning-choice) → discrimination (form-choice) → cued fill → constrained production
  (full-sentence typing, then word order) → free writing.** The order is enforced at set
  creation, not merely requested of the generator.
- Structured input and discrimination are distinct: in structured input the learner picks the
  **English meaning** of a Chinese sentence whose form is the only clue; in discrimination the
  learner picks between **Chinese forms** that differ in exactly one dimension, with distractors
  drawn from real English-speaker errors.
- Words the learner is still encoding — introduced this week, or repeatedly missed — get
  **recognition-first scaffolding**: before such a word is produced, one choice item teaches how
  the word is *used* — which words it pairs with (collocations), which situations call for it —
  with distractors drawn from word-for-word English transfer (in Chinese you 关 a 灯; a machine
  is 坏了, not "sick"). The same word is still produced later in the set: recognition opens the
  gate, production consolidates. Sets grow by one item per such word, so scaffolding never
  crowds out production, and the set note names any scaffold the generator failed to deliver.
- Constrained production uses PEDAGOGY.md's formats (transformation, constrained translation,
  question→answer). Typed full sentences are graded against an enumerated variant list; an item
  whose variant space cannot be confidently enumerated is demoted to free writing instead of
  being graded wrong.
- Free writing (AI-graded) is the highest-value category and every set ends with it.
- Generated exercises use the same interactive widget language, grading, and AI feedback as the
  hand-authored lesson pages, and are held to the same authoring contract (PEDAGOGY.md). Content
  that does not meet the contract is not shown.
- One difficulty per item: everything around the tested point must read easily with the known
  vocabulary.
- Content words rotate across the set; no scenario or sentence repeats, and no content word is
  the tested point of more than two items.
- Exercise prompts are Chinese-only. English scaffolding (situational setup, hints) exists but is
  hidden until the learner asks for it, so every item is first attempted as bare Chinese. The
  sole exception is constrained production in transformation/translation format, where the task
  instruction itself is English — as on the hand-authored pages.
- Explanations teach the rule at work, not just the answer.

## Generation follows current Claude API best practices

- Calls are made directly from the browser with the learner's own Anthropic key, which is stored
  locally and never leaves this machine except to authenticate with the API.
- **Structured outputs**: generated content is constrained to a defined schema by the API itself,
  never scraped out of free text.
- **Streaming** is used for long generations, with progress visible to the learner while the
  model works.
- **Reasoning effort is set explicitly** to match the task, and the **model is right-sized** to
  content authoring rather than defaulting to the largest available.
- **Cost is transparent**: token usage is tracked and an estimated cost per set is visible.

## Session behavior

- A generated set is ephemeral: regenerating replaces it wholesale with fresh material, so
  nothing is around long enough to be memorized as an artifact.
- Progress within the current set (completed items, drafts) survives page reloads.
- Everything is local: no server and no accounts. The only network traffic is to Anki on this
  machine and to the Claude API.
