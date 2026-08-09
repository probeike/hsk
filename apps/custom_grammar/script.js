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
    } else {
      fb.textContent = '✗ Not quite. Try again, or click Show answer.';
      fb.className = 'feedback bad';
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
