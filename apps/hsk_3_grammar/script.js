/* HSK 3 Grammar Lessons — shared interactivity
 * Widgets wire up on DOMContentLoaded via data-* attributes.
 */

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-exercise="fill"]').forEach(wireFill);
  document.querySelectorAll('[data-exercise="mc"]').forEach(wireMC);
  document.querySelectorAll('[data-exercise="builder"]').forEach(wireBuilder);
  document.querySelectorAll('[data-exercise="si"]').forEach(wireMC); // structured input reuses MC
  document.querySelectorAll('[data-exercise="reveal"]').forEach(wireReveal);
});

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
