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

- Each set follows a pedagogical arc: **recognition first, then guided production, then free
  writing.**
- Generated exercises use the same interactive widget language, grading, and AI feedback as the
  hand-authored lesson pages, and are held to the same authoring contract (PEDAGOGY.md). Content
  that does not meet the contract is not shown.
- One difficulty per item: everything around the tested point must read easily with the known
  vocabulary.
- Exercise prompts are Chinese-only. English scaffolding (situational setup, hints) exists but is
  hidden until the learner asks for it, so every item is first attempted as bare Chinese.
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
