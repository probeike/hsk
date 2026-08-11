/* HSK 3 Grammar Lessons — shared interactivity
 * Widgets wire up on DOMContentLoaded via data-* attributes.
 */

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-exercise="fill"]').forEach(wireFill);
  document.querySelectorAll('[data-exercise="mc"]').forEach(wireMC);
  document.querySelectorAll('[data-exercise="builder"]').forEach(wireBuilder);
  document.querySelectorAll('[data-exercise="si"]').forEach(wireMC); // structured input reuses MC
  document.querySelectorAll('[data-exercise="reveal"]').forEach(wireReveal);
  document.querySelectorAll('[data-exercise="match"]').forEach(wireMatch);
  document.querySelectorAll('[data-exercise="cloze"]').forEach(wireCloze);
  document.querySelectorAll('.py-toggle').forEach(wirePinyinToggle);
  aiInit();
});

// Reading passages (reading01.html …): hide pinyin until the learner asks.
// The button toggles .show-pinyin on its nearest .reading-text container.
function wirePinyinToggle(btn) {
  const box = btn.closest('.reading-text') || btn.nextElementSibling;
  if (!box) return;
  const labelShow = btn.getAttribute('data-show') || 'Show pinyin';
  const labelHide = btn.getAttribute('data-hide') || 'Hide pinyin';
  btn.setAttribute('aria-pressed', 'false');
  btn.textContent = labelShow;
  btn.addEventListener('click', () => {
    const on = box.classList.toggle('show-pinyin');
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.textContent = on ? labelHide : labelShow;
  });
}

function norm(s) {
  return (s || '').trim().replace(/[\s，。！？?!,\.]/g, '');
}

function wireFill(el) {
  const input = el.querySelector('input[type="text"]');
  const btn = el.querySelector('button.check');
  const fb = el.querySelector('.feedback');
  const reveal = el.querySelector('button.reveal');
  const box = el.querySelector('.reveal-box');
  const answers = (el.getAttribute('data-answer') || '').split('|').map(norm).filter(Boolean);

  const check = () => {
    const val = norm(input.value);
    if (!val) { fb.textContent = 'Type an answer first.'; fb.className = 'feedback bad'; return; }
    if (answers.some(a => a === val)) {
      fb.textContent = '✓ Correct.';
      fb.className = 'feedback ok';
      if (el._aiBtn) el._aiBtn.style.display = 'none';
    } else {
      fb.textContent = '✗ Not quite. Try again, or click Show answer.';
      fb.className = 'feedback bad';
      // Full-sentence items: offer an AI second opinion (the answer list may
      // be missing a valid variant). Short 1-3 char fills don't need it.
      if (answers.length && answers[0].length >= 5 && val.length >= 4) {
        aiOfferFillCheck(el, input.value, (el.getAttribute('data-answer') || '').split('|'));
      }
    }
  };
  btn && btn.addEventListener('click', check);
  input && input.addEventListener('keydown', e => { if (e.key === 'Enter') check(); });
  if (reveal && box) {
    reveal.addEventListener('click', () => { box.classList.toggle('shown'); });
  }
}

function wireMC(el) {
  const items = el.querySelectorAll('.choices li');
  let resolved = false;
  items.forEach(li => {
    li.addEventListener('click', () => {
      if (resolved) return;
      items.forEach(x => x.classList.remove('picked'));
      li.classList.add('picked');
      const correct = li.getAttribute('data-correct') === 'true';
      if (correct) {
        li.classList.add('correct');
        resolved = true;
        items.forEach(x => {
          if (x !== li) {
            x.classList.add('revealed');
          }
        });
      } else {
        li.classList.add('wrong');
        li.classList.add('revealed');
      }
      const fb = el.querySelector('.feedback');
      if (fb) {
        if (correct) { fb.textContent = '✓ Correct.'; fb.className = 'feedback ok'; }
        else { fb.textContent = '✗ Check the highlighted hint.'; fb.className = 'feedback bad'; }
      }
    });
  });
}

function wireBuilder(el) {
  const bank = el.querySelector('.bank');
  const drop = el.querySelector('.drop');
  const fb = el.querySelector('.feedback');
  const check = el.querySelector('button.check');
  const resetBtn = el.querySelector('button.reset');
  const answers = (el.getAttribute('data-answer') || '').split('|').map(norm).filter(Boolean);

  const shuffled = Array.from(bank.querySelectorAll('.chunk'));
  // randomise bank order on load
  shuffled.sort(() => Math.random() - 0.5).forEach(c => bank.appendChild(c));

  function bindChunk(c) {
    c.addEventListener('click', () => {
      if (c.parentElement === bank) drop.appendChild(c);
      else bank.appendChild(c);
    });
  }
  el.querySelectorAll('.chunk').forEach(bindChunk);

  check && check.addEventListener('click', () => {
    const built = Array.from(drop.querySelectorAll('.chunk')).map(c => c.textContent.trim()).join('');
    const got = norm(built);
    if (answers.some(a => a === got)) {
      fb.textContent = '✓ Correct order.';
      fb.className = 'feedback ok';
    } else {
      fb.textContent = '✗ Not the right order. Think about where the marker goes.';
      fb.className = 'feedback bad';
    }
  });

  resetBtn && resetBtn.addEventListener('click', () => {
    Array.from(drop.querySelectorAll('.chunk')).forEach(c => bank.appendChild(c));
    fb.textContent = '';
    fb.className = 'feedback';
  });
}

function wireReveal(el) {
  const btn = el.querySelector('button.reveal');
  const box = el.querySelector('.reveal-box');
  if (btn && box) btn.addEventListener('click', () => box.classList.toggle('shown'));
}

// Matching / pairing (配对). Left items carry data-key; the right item that
// answers a left carries data-match with the same id. Right column is shuffled.
// Click a left item, then a right item, to pair them; a number badge links them.
function wireMatch(el) {
  const fb = el.querySelector('.feedback');
  const lefts = Array.from(el.querySelectorAll('.match-col.left .match-item'));
  const rcol = el.querySelector('.match-col.right');
  const rights = Array.from(rcol.querySelectorAll('.match-item'));
  rights.sort(() => Math.random() - 0.5).forEach(r => rcol.appendChild(r));

  lefts.forEach((l, i) => {
    l.dataset.idx = i + 1;
    const b = document.createElement('span');
    b.className = 'match-badge';
    b.textContent = i + 1;
    l.prepend(b);
  });

  let active = null;
  const pairOf = new Map(); // left -> right

  function rightBadge(r, num) {
    let b = r.querySelector('.match-badge');
    if (!b) { b = document.createElement('span'); b.className = 'match-badge'; r.prepend(b); }
    b.textContent = num == null ? '' : num;
    r.classList.toggle('paired', num != null);
  }

  lefts.forEach(l => l.addEventListener('click', () => {
    if (active) active.classList.remove('active');
    active = l; l.classList.add('active');
  }));

  rights.forEach(r => r.addEventListener('click', () => {
    if (!active) return;
    if (pairOf.has(active)) rightBadge(pairOf.get(active), null);          // free active's old right
    for (const [lk, rv] of Array.from(pairOf)) {                           // free this right from another left
      if (rv === r) { pairOf.delete(lk); lk.classList.remove('done'); }
    }
    pairOf.set(active, r);
    rightBadge(r, active.dataset.idx);
    active.classList.add('done');
    active.classList.remove('active');
    active = null;
  }));

  el.querySelector('button.check') && el.querySelector('button.check').addEventListener('click', () => {
    if (pairOf.size < lefts.length) { fb.textContent = 'Pair them all first.'; fb.className = 'feedback bad'; return; }
    let ok = true;
    for (const [l, r] of pairOf) { if (l.dataset.key !== r.dataset.match) { ok = false; break; } }
    fb.textContent = ok ? '✓ All matched.' : '✗ Some pairs are wrong — try again.';
    fb.className = 'feedback ' + (ok ? 'ok' : 'bad');
  });

  el.querySelector('button.reset') && el.querySelector('button.reset').addEventListener('click', () => {
    pairOf.clear();
    rights.forEach(r => rightBadge(r, null));
    lefts.forEach(l => l.classList.remove('done', 'active'));
    active = null; fb.textContent = ''; fb.className = 'feedback';
  });
}

// Word-bank cloze (选词填空). data-answers="key:word;key:word;…" maps each blank's
// data-key to its correct word. Click a word, then a blank, to place it; click a
// filled blank to clear it. The bank may include one extra distractor word.
function wireCloze(el) {
  const fb = el.querySelector('.feedback');
  const ans = {};
  (el.dataset.answers || '').split(';').forEach(p => {
    const i = p.indexOf(':');
    if (i > 0) ans[p.slice(0, i).trim()] = p.slice(i + 1).trim();
  });
  const bank = el.querySelector('.wordbank');
  const words = Array.from(bank.querySelectorAll('.word'));
  words.sort(() => Math.random() - 0.5).forEach(w => bank.appendChild(w));
  const blanks = Array.from(el.querySelectorAll('.blank'));
  let active = null;

  words.forEach(w => w.addEventListener('click', () => {
    if (w.classList.contains('used')) return;
    if (active) active.classList.remove('active');
    active = w; w.classList.add('active');
  }));

  blanks.forEach(b => b.addEventListener('click', () => {
    if (b._word) { b._word.classList.remove('used'); b._word = null; b.textContent = ''; b.classList.remove('filled'); }
    if (active) {
      b._word = active; b.textContent = active.dataset.word;
      b.classList.add('filled'); active.classList.add('used'); active.classList.remove('active'); active = null;
    }
  }));

  el.querySelector('button.check') && el.querySelector('button.check').addEventListener('click', () => {
    if (blanks.some(b => !b._word)) { fb.textContent = 'Fill every blank first.'; fb.className = 'feedback bad'; return; }
    const ok = blanks.every(b => ans[b.dataset.key] === b._word.dataset.word);
    fb.textContent = ok ? '✓ Correct.' : '✗ Some words are misplaced — try again.';
    fb.className = 'feedback ' + (ok ? 'ok' : 'bad');
  });

  el.querySelector('button.reset') && el.querySelector('button.reset').addEventListener('click', () => {
    blanks.forEach(b => { b._word = null; b.textContent = ''; b.classList.remove('filled'); });
    words.forEach(w => w.classList.remove('used', 'active'));
    active = null; fb.textContent = ''; fb.className = 'feedback';
  });
}

/* ===================================================================
 * AI grading (Claude). Free-production reveals get a "Grade with AI"
 * button; full-sentence fills marked wrong get an "Ask AI" fallback
 * that checks whether the answer is a valid variant the answer list
 * missed. Needs an Anthropic API key — click the "AI ⚙" button
 * (bottom-right of every page) and paste it once; it is stored in
 * this browser's localStorage only, never in any file.
 * =================================================================== */
const AI_MODEL = 'claude-haiku-4-5';
const AI_KEY_STORAGE = 'anthropic_api_key';

function aiKey() { try { return localStorage.getItem(AI_KEY_STORAGE) || ''; } catch (e) { return ''; } }

function aiInit() {
  aiKeyPanel();
  // Free-production graders: any reveal exercise with a textarea
  document.querySelectorAll('[data-exercise="reveal"]').forEach(el => {
    if (el.querySelector('textarea')) aiAddGradeButton(el);
  });
}

function aiKeyPanel() {
  const btn = document.createElement('button');
  btn.className = 'ai-key-btn';
  btn.type = 'button';
  btn.textContent = 'AI ⚙';
  btn.title = 'Set your Anthropic API key for AI grading';
  const panel = document.createElement('div');
  panel.className = 'ai-key-panel';
  panel.innerHTML =
    '<label>Anthropic API key <span class="ai-key-note">(stored only in this browser)</span></label>' +
    '<input type="password" placeholder="sk-ant-...">' +
    '<div class="ai-key-row"><button type="button" class="ai-save">Save</button>' +
    '<button type="button" class="ai-clear">Clear</button>' +
    '<span class="ai-key-status"></span></div>';
  document.body.appendChild(btn);
  document.body.appendChild(panel);
  const input = panel.querySelector('input');
  const status = panel.querySelector('.ai-key-status');
  const setStatus = () => {
    const has = !!aiKey();
    status.textContent = has ? '✓ key set' : 'no key';
    status.className = 'ai-key-status ' + (has ? 'ok' : '');
    btn.classList.toggle('has-key', has);
  };
  setStatus();
  btn.addEventListener('click', () => {
    panel.classList.toggle('shown');
    if (panel.classList.contains('shown')) { input.value = aiKey(); input.focus(); }
  });
  panel.querySelector('.ai-save').addEventListener('click', () => {
    try { localStorage.setItem(AI_KEY_STORAGE, input.value.trim()); } catch (e) {}
    setStatus(); panel.classList.remove('shown');
  });
  panel.querySelector('.ai-clear').addEventListener('click', () => {
    try { localStorage.removeItem(AI_KEY_STORAGE); } catch (e) {}
    input.value = ''; setStatus();
  });
}

async function aiCall(system, userText, schema) {
  const key = aiKey();
  if (!key) throw new Error('NO_KEY');
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: AI_MODEL,
      max_tokens: 600,
      system: system,
      messages: [{ role: 'user', content: userText }],
      output_config: { format: { type: 'json_schema', schema: schema } },
    }),
  });
  if (res.status === 401 || res.status === 403) throw new Error('BAD_KEY');
  if (!res.ok) throw new Error('HTTP_' + res.status);
  const data = await res.json();
  const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('');
  return JSON.parse(text);
}

function aiErrorMessage(e) {
  if (e.message === 'NO_KEY') return 'No API key — click "AI ⚙" (bottom-right) and paste your Anthropic key.';
  if (e.message === 'BAD_KEY') return 'API key rejected — click "AI ⚙" to update it.';
  return 'AI grading unavailable (offline, or: ' + e.message + ').';
}

function aiFeedbackDiv(el) {
  let d = el.querySelector('.ai-feedback');
  if (!d) { d = document.createElement('div'); d.className = 'ai-feedback'; el.appendChild(d); }
  return d;
}

const AI_GRADE_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['correct', 'minor_issues', 'incorrect'] },
    feedback: { type: 'string' },
    corrected: { type: 'string' },
  },
  required: ['verdict', 'feedback', 'corrected'],
  additionalProperties: false,
};

function aiAddGradeButton(el) {
  const ta = el.querySelector('textarea');
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'ai-btn';
  btn.textContent = 'Grade with AI';
  const anchor = el.querySelector('button.reveal');
  anchor ? anchor.after(btn) : el.appendChild(btn);
  btn.addEventListener('click', async () => {
    const out = aiFeedbackDiv(el);
    const answer = (ta.value || '').trim();
    if (!answer) { out.textContent = 'Write your answer first.'; out.className = 'ai-feedback bad'; return; }
    const prompt = (el.querySelector('.prompt') || {}).textContent || '';
    const model = (el.querySelector('.reveal-box') || {}).textContent || '';
    out.textContent = 'Grading…'; out.className = 'ai-feedback busy';
    btn.disabled = true;
    try {
      const r = await aiCall(
        'You grade a Mandarin production exercise written by an adult English-speaking learner at ~HSK 3. ' +
        'Judge grammar and whether the required structures named in the exercise prompt are used correctly; ' +
        'accept any natural HSK 1-3 vocabulary and any content the learner chose — do NOT require them to match the model answer. ' +
        'verdict: "correct" = grammatical and uses the required structure(s); "minor_issues" = understandable, small slips; ' +
        '"incorrect" = required structure wrong or missing. ' +
        'feedback: 2-4 short English sentences; name each error and WHY it is wrong, referencing the target structure; be encouraging. ' +
        'corrected: a corrected version of the learner\'s own sentences (unchanged if correct).',
        'Exercise prompt:\n' + prompt.trim() +
        '\n\nModel answer (reference only):\n' + model.trim().slice(0, 600) +
        '\n\nLearner\'s answer:\n' + answer,
        AI_GRADE_SCHEMA);
      const icon = { correct: '✓', minor_issues: '△', incorrect: '✗' }[r.verdict] || '';
      out.className = 'ai-feedback ' + (r.verdict === 'correct' ? 'ok' : r.verdict === 'minor_issues' ? 'mid' : 'bad');
      out.innerHTML = '';
      const head = document.createElement('div'); head.className = 'ai-verdict';
      head.textContent = icon + ' ' + r.verdict.replace('_', ' ');
      const body = document.createElement('div'); body.textContent = r.feedback;
      out.appendChild(head); out.appendChild(body);
      if (r.verdict !== 'correct' && r.corrected) {
        const fix = document.createElement('div'); fix.className = 'ai-corrected';
        fix.textContent = '→ ' + r.corrected;
        out.appendChild(fix);
      }
    } catch (e) {
      out.textContent = aiErrorMessage(e); out.className = 'ai-feedback bad';
    } finally { btn.disabled = false; }
  });
}

const AI_CHECK_SCHEMA = {
  type: 'object',
  properties: {
    acceptable: { type: 'boolean' },
    explanation: { type: 'string' },
    corrected: { type: 'string' },
  },
  required: ['acceptable', 'explanation', 'corrected'],
  additionalProperties: false,
};

// Called from wireFill when a full-sentence answer is marked wrong: offers a
// second opinion in case the learner produced a valid variant the answer list missed.
function aiOfferFillCheck(el, learnerAnswer, answers) {
  if (el._aiBtn) { el._aiBtn.style.display = ''; return; }
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'ai-btn ai-btn-small';
  btn.textContent = 'Ask AI — is my answer actually OK?';
  el._aiBtn = btn;
  const fb = el.querySelector('.feedback');
  fb ? fb.after(btn) : el.appendChild(btn);
  btn.addEventListener('click', async () => {
    const out = aiFeedbackDiv(el);
    const input = el.querySelector('input[type="text"]');
    const current = input ? input.value.trim() : learnerAnswer;
    const prompt = (el.querySelector('.prompt') || {}).textContent || '';
    out.textContent = 'Checking…'; out.className = 'ai-feedback busy';
    btn.disabled = true;
    try {
      const r = await aiCall(
        'A Mandarin exercise for a ~HSK 3 learner marked their typed answer wrong because it is not in the accepted-answer list. ' +
        'Decide whether their answer is nonetheless a fully correct, natural completion of the exercise. ' +
        'acceptable: true ONLY if it is grammatical AND satisfies everything the prompt asks (required words, required structure, intended meaning). ' +
        'explanation: 1-3 short English sentences saying why, referencing the grammar point. ' +
        'corrected: the closest fully-correct version of their answer.',
        'Exercise prompt:\n' + prompt.trim() +
        '\n\nAccepted answers:\n' + answers.join('\n') +
        '\n\nLearner\'s answer:\n' + current,
        AI_CHECK_SCHEMA);
      out.className = 'ai-feedback ' + (r.acceptable ? 'ok' : 'bad');
      out.textContent = (r.acceptable ? '✓ Your answer is fine. ' : '✗ ') + r.explanation +
        (!r.acceptable && r.corrected ? '  → ' + r.corrected : '');
    } catch (e) {
      out.textContent = aiErrorMessage(e); out.className = 'ai-feedback bad';
    } finally { btn.disabled = false; }
  });
}
