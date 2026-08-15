/* Dynamic practice — generates a fresh exercise set from live Anki vocabulary.
 * Principles: DYNAMIC_PRINCIPLES.md. Authoring contract: PEDAGOGY.md.
 * Loads after script.js and reuses its globals: norm, wireFill, wireMC,
 * wireBuilder, wireReveal, aiKey, aiErrorMessage, aiAddGradeButton; overrides
 * the (inert on this page) progressMark so widget completions land in cg-dyn:set.
 * Test without Anki / API spend: dynamic.html?mock=all (or ?mock=anki / ?mock=ai).
 */

const DYN_MODEL = 'claude-sonnet-5';   // flip to 'claude-haiku-4-5' for cheap tests
const DYN_EFFORT = 'low';              // explicit reasoning effort for generation
const DYN_MAXTOK = 10000;              // caps thinking + JSON together — keep headroom
const DYN_PRICE = [3, 15];             // Sonnet 5 $/MTok in, out (sticker price)
const DYN_ANKI_URL = 'http://127.0.0.1:8765';
const DYN_DECK = 'HSK new';
const DYN_Q = {
  struggling: 'deck:"' + DYN_DECK + '" (rated:7:1 OR prop:lapses>=2) -is:suspended',
  recent:     'deck:"' + DYN_DECK + '" introduced:7 -is:suspended',
  due:        'deck:"' + DYN_DECK + '" (is:due OR rated:2) -is:suspended',
  known:      'deck:"' + DYN_DECK + '" -is:new',
};
const DYN_BUCKET_CAP = 30;
const DYN_SET_KEY = 'cg-dyn:set';
const DYN_LESSONS_KEY = 'cg-dyn:lessons';
const dynN = t => Math.min(14, Math.max(6, 2 * t));
// NEW (recent) and SHAKY (struggling) targets each earn one extra usage-mc
// scaffold item on top of the base size, within the same cap.
const dynScaffoldTargets = targets => targets.filter(w => w.bucket === 'struggling' || w.bucket === 'recent');
const dynScaffoldN = targets => Math.min(dynScaffoldTargets(targets).length, 14 - dynN(targets.length));

// Closed-class function words the deck/wordlists lack as standalone notes.
// The learner reads these fine; without them segmentation would reject
// otherwise-legal sentences.
const DYN_EXTRA = ('的 得 地 了 着 过 吗 呢 吧 啊 别 每 些 个 位 件 张 条 本 只 块 次 遍 场 又 之 ' +
  '与 而 并 或 或者 但是 可是 因为 所以 如果 虽然 而且 还是 以后 以前 时候 这 那 这儿 那儿 ' +
  '这么 那么 事 们 人们 大家 一起 已经 正在 刚才 马上 都 也 就 才 还 太 更 最 和 跟 很 是 ' +
  '不 没 有 在 去 来 到 会 能 要 想 可以 应该 什么 谁 哪 哪儿 怎么 为什么 多少 几 ' +
  '一 二 三 四 五 六 七 八 九 十 百 千 万 零 两').split(' ');

// HSK 3 grammar points per textbook lesson (from knowledge/hsk_3/lesson_NN.md
// frontmatter `grammar_introduced`; lesson 20 is pure review — nothing to gate).
const DYN_LESSONS = [
  { n: 1,  pts: ['结果补语 "好"', '"一……也/都 + 不/没……" 表示否定', '连词 "那"'] },
  { n: 2,  pts: ['简单趋向补语', '两个动作的先后发生', '反问的表达: 不……吗?'] },
  { n: 3,  pts: ['"还是" 和 "或者"', '存在句: 处所 + V着 + 数量 + N', '"会" 表示可能'] },
  { n: 4,  pts: ['又……又……', '伴随动作: V1着(O1)+V2(O2)', '"了" 表示变化', '越来越 + Adj'] },
  { n: 5,  pts: ['可能补语: V得/不 + 补语', '"呢" 询问处所: N+呢', '"刚" 和 "刚才"'] },
  { n: 6,  pts: ['时段的表达', '兴趣的表达', '用 "半""刻""差" 表示时间'] },
  { n: 7,  pts: ['"又" 和 "再"', '疑问代词活用1'] },
  { n: 8,  pts: ['越A越B', '比较句1: A跟B一样(+Adj)'] },
  { n: 9,  pts: ['比较句2: A比B+Adj+一点儿/得多/多了', '概数的表达1'] },
  { n: 10, pts: ['"把"字句1: A把B+V了', '概数的表达2: 左右'] },
  { n: 11, pts: ['"才" 和 "就"', '"把"字句2: A把B+V+在/到……'] },
  { n: 12, pts: ['复合趋向补语', '"一边……一边……"'] },
  { n: 13, pts: ['"把"字句3: A把B+V+结果/趋向补语', '先……，再/又……，然后……'] },
  { n: 14, pts: ['除了……以外，都/还/也……', '疑问代词活用2', '程度的表达: 极了'] },
  { n: 15, pts: ['"如果……，(的话)，(就)……"', '复杂的状态补语', '单音节形容词重叠'] },
  { n: 16, pts: ['双音节动词重叠', '疑问代词活用3'] },
  { n: 17, pts: ['只要……，就……', '介词 "关于"'] },
  { n: 18, pts: ['趋向补语的引申义', '"使""叫""让"'] },
  { n: 19, pts: ['"被"字句', '"只有……才……"'] },
  { n: 20, pts: [], label: '综合复习 把/被/着/了 (no new structures)' },
];

const DYN_MOCK = new URLSearchParams(location.search).get('mock') || '';
const DYN_MOCK_ANKI = DYN_MOCK === 'all' || DYN_MOCK === 'anki';
const DYN_MOCK_AI = DYN_MOCK === 'all' || DYN_MOCK === 'ai';

let dynWords = null;   // { buckets: [{key,label,words:[{zh,py,en,bucket}]}], known: Set }
let dynSel = new Set();
let dynState = null;   // { at, model, usage, gen, kept, items, done:{}, drafts:{} }
let dynAbort = null;
let dynBusy = false;

const dynEl = id => document.getElementById(id);

/* ============================ AnkiConnect ============================ */

async function dynAnki(action, params) {
  const res = await fetch(DYN_ANKI_URL, {
    method: 'POST',
    body: JSON.stringify({ action: action, version: 6, params: params || {} }),
  });
  const data = await res.json();
  if (data.error) throw new Error('ANKI: ' + data.error);
  return data.result;
}

function dynClean(s) {
  return (s || '').replace(/\[sound:[^\]]*\]/g, '').replace(/<[^>]*>/g, '').trim();
}

async function dynNotes(query, cap) {
  const ids = await dynAnki('findNotes', { query: query });
  ids.sort((a, b) => b - a); // note IDs are creation timestamps — newest first
  const info = await dynAnki('notesInfo', { notes: ids.slice(0, cap) });
  const out = [];
  for (const n of info) {
    const f = n.fields || {};
    const pick = (...names) => {
      for (const k of names) if (f[k] && f[k].value) return dynClean(f[k].value);
      return '';
    };
    const zh = pick('Chinese', 'Hanzi', 'Simplified', 'Expression', 'Front');
    if (zh) out.push({ zh: zh, py: pick('Pinyin', 'Reading'), en: pick('English', 'Meaning', 'Translation', 'Back') });
  }
  return out;
}

async function dynAnkiLoad() {
  if (DYN_MOCK_ANKI) return dynMockAnki();
  await dynAnki('requestPermission');
  const [struggling, recent, due, known] = await Promise.all([
    dynNotes(DYN_Q.struggling, DYN_BUCKET_CAP),
    dynNotes(DYN_Q.recent, DYN_BUCKET_CAP),
    dynNotes(DYN_Q.due, DYN_BUCKET_CAP),
    dynNotes(DYN_Q.known, 3000),
  ]);
  return dynBuildWords(struggling, recent, due, known.map(w => w.zh));
}

function dynBuildWords(struggling, recent, due, knownZh) {
  const seen = new Set();
  const take = (words, key) => words.filter(w => {
    if (seen.has(w.zh)) return false;
    seen.add(w.zh);
    w.bucket = key;
    return true;
  });
  return {
    buckets: [
      { key: 'struggling', label: 'Struggling', words: take(struggling, 'struggling') },
      { key: 'recent', label: 'New this week', words: take(recent, 'recent') },
      { key: 'due', label: 'Due for review', words: take(due, 'due') },
    ],
    known: new Set(knownZh),
  };
}

function dynKnownAll() {
  if (!dynWords._all) {
    dynWords._all = new Set(dynWords.known);
    for (const w of DYN_EXTRA) dynWords._all.add(w);
    dynWords._all.add('小丽'); dynWords._all.add('小刚');
  }
  return dynWords._all;
}

function dynMockAnki() {
  const known = ('她 听 音乐 打扫 房间 然后 我 终于 找到 找 到 手机 经过 昨天 在 公园 遇到 老师 ' +
    '先 吃饭 吃 饭 去 上班 再 对 很 重要 他 拿 书 家 你 干净 谁 请 写 句 话 每 星期 星期六 ' +
    '自己 休息 觉得 什么 最 为什么 做 今天 一边 是 有 不 没 好 人 说 看 想 来 回 开始 工作 学习 朋友').split(' ');
  return dynBuildWords(
    [
      { zh: '打扫', py: 'dǎsǎo', en: 'to clean' },
      { zh: '终于', py: 'zhōngyú', en: 'finally' },
      { zh: '遇到', py: 'yùdào', en: 'to run into' },
      { zh: '经过', py: 'jīngguò', en: 'to pass by' },
    ],
    [],
    [
      { zh: '一边', py: 'yìbiān', en: 'while' },
      { zh: '然后', py: 'ránhòu', en: 'then' },
      { zh: '拿', py: 'ná', en: 'to take / hold' },
      { zh: '自己', py: 'zìjǐ', en: 'oneself' },
      { zh: '重要', py: 'zhòngyào', en: 'important' },
      { zh: '音乐', py: 'yīnyuè', en: 'music' },
    ],
    known);
}

/* ============================ Setup UI ============================ */

function dynStatus(msg, cls) {
  const s = dynEl('dyn-status');
  s.textContent = msg;
  s.className = 'dyn-status' + (cls ? ' ' + cls : '');
}

function dynSetupBox(msg) {
  const box = dynEl('dyn-anki');
  box.innerHTML = '';
  const d = document.createElement('div');
  d.className = 'dyn-setupbox';
  const p = document.createElement('p');
  p.textContent = msg;
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.textContent = 'Retry';
  btn.addEventListener('click', dynLoadWords);
  d.appendChild(p); d.appendChild(btn);
  box.appendChild(d);
}

async function dynLoadWords() {
  const box = dynEl('dyn-anki');
  box.textContent = 'Connecting to Anki…';
  try {
    dynWords = await dynAnkiLoad();
    box.textContent = '';
    dynRenderBuckets();
    dynUpdateGen();
  } catch (e) {
    if (e instanceof TypeError) {
      dynSetupBox("Can't reach Anki. Open Anki on this machine (the AnkiConnect add-on, 2055492159, must be installed).");
    } else if (/permission|denied|origin/i.test(e.message)) {
      dynSetupBox('AnkiConnect blocked this page. In Anki: Tools → Add-ons → AnkiConnect → Config, add "null" to webCorsOriginList, restart Anki.');
    } else {
      dynSetupBox(e.message);
    }
  }
}

function dynRenderBuckets() {
  const wrap = dynEl('dyn-buckets');
  wrap.innerHTML = '';
  for (const b of dynWords.buckets) {
    const sec = document.createElement('div');
    sec.className = 'dyn-bucket';
    const h = document.createElement('h3');
    h.textContent = b.label;
    sec.appendChild(h);
    if (!b.words.length) {
      const none = document.createElement('p');
      none.className = 'dyn-none';
      none.textContent = 'none right now';
      sec.appendChild(none);
    } else {
      const chips = document.createElement('div');
      chips.className = 'dyn-chips';
      for (const w of b.words) {
        const c = document.createElement('button');
        c.type = 'button';
        c.className = 'dyn-chip';
        c.textContent = w.zh;
        c.title = w.py + ' — ' + w.en;
        c.addEventListener('click', () => {
          if (dynSel.has(w.zh)) dynSel.delete(w.zh); else dynSel.add(w.zh);
          c.classList.toggle('on', dynSel.has(w.zh));
          dynUpdateGen();
        });
        chips.appendChild(c);
      }
      sec.appendChild(chips);
    }
    wrap.appendChild(sec);
  }
}

function dynRenderLessons() {
  const wrap = dynEl('dyn-lessons');
  let ticked = [];
  try { ticked = JSON.parse(localStorage.getItem(DYN_LESSONS_KEY) || '[]'); } catch (e) {}
  const tickedSet = new Set(ticked);
  for (const l of DYN_LESSONS) {
    const label = document.createElement('label');
    label.className = 'dyn-lesson';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.value = l.n;
    cb.checked = tickedSet.has(l.n);
    cb.addEventListener('change', () => {
      const on = Array.from(wrap.querySelectorAll('input:checked')).map(x => +x.value);
      try { localStorage.setItem(DYN_LESSONS_KEY, JSON.stringify(on)); } catch (e) {}
    });
    const txt = document.createElement('span');
    txt.textContent = 'L' + l.n + ' · ' + (l.label || l.pts.join('；'));
    label.appendChild(cb); label.appendChild(txt);
    wrap.appendChild(label);
  }
}

function dynLessonPts() {
  const on = new Set(Array.from(dynEl('dyn-lessons').querySelectorAll('input:checked')).map(x => +x.value));
  const pts = [];
  for (const l of DYN_LESSONS) if (on.has(l.n)) pts.push(...l.pts);
  return pts;
}

function dynTargets() {
  const out = [];
  if (!dynWords) return out;
  for (const b of dynWords.buckets) for (const w of b.words) if (dynSel.has(w.zh)) out.push(w);
  return out;
}

function dynPassive(targets) {
  const t = new Set(targets.map(w => w.zh));
  const out = [];
  for (const b of dynWords.buckets) for (const w of b.words) if (!t.has(w.zh)) out.push(w);
  return out;
}

function dynUpdateGen() {
  const btn = dynEl('dyn-generate');
  const t = dynSel.size;
  const total = t ? dynN(t) + dynScaffoldN(dynTargets()) : 0;
  btn.textContent = (dynState ? 'Regenerate' : 'Generate') + (t ? ' ' + total + ' exercises' : '');
  btn.disabled = dynBusy || !t || !dynWords;
}

/* ============================ Generation ============================ */

const DYN_SCHEMA = {
  type: 'object',
  properties: {
    items: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          type: { type: 'string', enum: ['si', 'mc', 'fill', 'builder', 'reveal'] },
          prompt: { type: 'string' },
          hint_en: { type: 'string' },
          answers: { type: 'array', items: { type: 'string' } },
          chunks: { type: 'array', items: { type: 'string' } },
          choices: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                text: { type: 'string' },
                correct: { type: 'boolean' },
                why: { type: 'string' },
              },
              required: ['text', 'correct', 'why'],
              additionalProperties: false,
            },
          },
          explain: { type: 'string' },
          checklist: { type: 'array', items: { type: 'string' } },
        },
        required: ['type', 'prompt', 'hint_en', 'answers', 'chunks', 'choices', 'explain', 'checklist'],
        additionalProperties: false,
      },
    },
  },
  required: ['items'],
  additionalProperties: false,
};

const DYN_SYSTEM =
  'You author Mandarin grammar exercises for one adult English-speaking learner at ~HSK 3. ' +
  'Return a JSON exercise set following the schema exactly; leave unused fields empty ("" or []).\n\n' +
  'Exercise types — the set follows a five-stage arc, in order: structured input ("si") → discrimination ' +
  '("mc") → cued fill (short "fill") → constrained production (full-sentence "fill", then "builder") → ' +
  'free writing ("reveal"):\n' +
  '- "si" (structured input): prompt = ONE Chinese sentence whose grammar form is the only clue to its meaning. ' +
  'choices = 3-4 ENGLISH meanings, EXACTLY ONE with correct=true; each wrong meaning is what an English speaker ' +
  'who misread the structure would think it says. Every choice gets a short English "why" rationale.\n' +
  '- "mc" (discrimination): prompt = a Chinese sentence or question (use ___ for a gap). choices = 3-4 CHINESE ' +
  'forms, EXACTLY ONE with correct=true. Distractors are errors an English speaker actually makes; each differs ' +
  'from the correct choice in exactly one dimension — never gibberish. Every choice gets a short English "why".\n' +
  '- short "fill" (cued production): prompt = Chinese with ___ blanking the DECISION POINT (the grammar choice), ' +
  'never a guessable content word. answers = 1-3 short variants. explain = why the answer works (shown after checking).\n' +
  '- full-sentence "fill" (constrained production — the learner types a whole sentence): use one of these formats. ' +
  'F1 transformation: show a base Chinese sentence and ask for a rewrite using the target structure. ' +
  'F2 constrained translation: give an English sentence to say in Chinese. ' +
  'F4 question→answer: prompt = a Chinese question the learner answers with a full sentence. ' +
  'For F1/F2 the prompt opens with a short English task line naming the required content words ' +
  '("Keep the subject X; use the measure word Y") so the answer space stays enumerable. ' +
  'answers = EVERY natural correct variant (word-order variants, 也/都, 没/没有, optional 的/儿), 3-8 entries. ' +
  'If you cannot confidently enumerate the variant space within 8 entries, make the item a "reveal" instead. ' +
  'explain = why the answer works.\n' +
  '- "builder": word order. chunks = 4-8 tiles that concatenate EXACTLY into each string in answers ' +
  '(no missing text; punctuation may be omitted). answers = every acceptable order. explain = the rule at work.\n' +
  '- "reveal": free production — the highest-value items, graded by AI. prompt = an open Chinese question or task ' +
  'the learner answers in writing (2-3 sentences), naming the structures to use. ' +
  'explain = one model answer in Chinese followed by a short English gloss in parentheses. ' +
  'checklist = 3-5 short English self-check items naming the required structures and likely mistakes.\n\n' +
  'New-word scaffolding: targets tagged [NEW] (just introduced) or [SHAKY] (frequently missed) are words the ' +
  'learner recognizes but cannot yet USE — the typical failure is an English calque (reaching for 开/闭 where ' +
  'Chinese pairs 关 with 灯, or 病 where a machine is 坏了). For EACH such target: ' +
  '(1) one "mc" item tests usage — which word combines with it (collocation), or which word the situation ' +
  'calls for — with distractors that are exactly the words an English speaker would pick by translating ' +
  'word-for-word. Never use a distractor that is also correct or nearly correct; the "why" lines teach the pairing. ' +
  '(2) The same word must ALSO appear in at least one later fill/builder/reveal item, so it gets produced, ' +
  'not just recognized. If there are fewer mc slots than NEW/SHAKY targets, scaffold the SHAKY ones first.\n\n' +
  'Hard rules:\n' +
  '- prompt is CHINESE ONLY (Chinese punctuation; no English words, no pinyin). All English scaffolding — ' +
  'situational setup, hints — goes in hint_en (shown only on request; "" if none needed). ' +
  'SOLE EXCEPTION: F1/F2 full-sentence fills, whose prompt opens with the English task line described above.\n' +
  '- Vocabulary: use ONLY words from ALLOWED WORDS (小丽 and 小刚 are available as names). Words, not characters — ' +
  'never coin a compound out of known characters; a word is usable only if listed.\n' +
  '- Every TARGET word appears in at least one exercise and is central to the item that uses it. ' +
  'PASSIVE words are supporting colour only — natural re-exposure, never the tested point, never forced in.\n' +
  '- One difficulty per item: everything around the tested point must read easily.\n' +
  '- Grammar: any HSK 1-2 structure, plus ONLY the HSK 3 structures listed as allowed. ' +
  '把/被/result/directional/得-complements count as HSK 3.\n' +
  '- Vary scenarios and content words across items; never reuse the same sentence twice. ' +
  'Rotate vocabulary: no content word (noun/verb/adjective) is central to more than 2 items in the set.\n' +
  '- explain teaches the rule, not just the answer.';

// Per-stage mix: base counts from nBase (always even, 6-14), weighted toward
// production per PEDAGOGY's target ratios; fillShort absorbs the remainder and
// stays >= 1 for every legal nBase. Each granted scaffold slot adds one
// usage-mc on top, so the set totals nBase + scaffold.
function dynMix(nBase, scaffold) {
  const reveal = Math.max(2, Math.round(nBase * 0.25));
  const builder = nBase >= 10 ? 2 : 1;
  const si = nBase >= 8 ? 1 : 0;
  const mc = (nBase >= 12 ? 2 : 1) + (scaffold || 0);
  const fillFull = Math.max(1, Math.round(nBase * 0.2));
  const fillShort = nBase - si - (nBase >= 12 ? 2 : 1) - fillFull - builder - reveal;
  return { si: si, mc: mc, fillShort: fillShort, fillFull: fillFull, builder: builder, reveal: reveal };
}

const DYN_TAG = { struggling: 'SHAKY', recent: 'NEW', due: 'REVIEW' };

function dynPrompt(targets, n, scaffold) {
  const passive = dynPassive(targets);
  const pts = dynLessonPts();
  const m = dynMix(n, scaffold);
  const scaffolded = dynScaffoldTargets(targets);
  return 'ALLOWED WORDS (complete list — use no Chinese word outside it):\n' +
    Array.from(dynKnownAll()).join(' ') + '\n\n' +
    'TARGET WORDS (drill each one):\n' +
    targets.map(w => w.zh + ' (' + w.py + ' — ' + w.en + ') [' + (DYN_TAG[w.bucket] || w.bucket) + ']').join('\n') + '\n\n' +
    'PASSIVE WORDS (supporting vocabulary only):\n' +
    (passive.length ? passive.slice(0, 40).map(w => w.zh).join(' ') : '(none)') + '\n\n' +
    'ALLOWED HSK 3 GRAMMAR POINTS:\n' +
    (pts.length ? pts.map(p => '- ' + p).join('\n') : '(none ticked — HSK 1-2 grammar only)') + '\n\n' +
    'Generate exactly ' + (n + (scaffold || 0)) + ' exercises, in this order: ' +
    (m.si ? m.si + ' si, ' : '') + m.mc + ' mc' +
    (scaffolded.length ? ' (including one usage-mc per NEW/SHAKY target — see the scaffolding rule)' : '') +
    ', ' + m.fillShort + ' short fill, ' +
    m.fillFull + ' full-sentence fill (F1/F2/F4), ' + m.builder + ' builder, ' + m.reveal + ' reveal.';
}

async function dynCallGenerate(targets, n, scaffold, onProgress) {
  const key = aiKey();
  if (!key) throw new Error('NO_KEY');
  dynAbort = new AbortController();
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    signal: dynAbort.signal,
    headers: {
      'content-type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: DYN_MODEL,
      max_tokens: DYN_MAXTOK,
      stream: true,
      system: DYN_SYSTEM,
      messages: [{ role: 'user', content: dynPrompt(targets, n, scaffold) }],
      output_config: { effort: DYN_EFFORT, format: { type: 'json_schema', schema: DYN_SCHEMA } },
    }),
  });
  if (res.status === 401 || res.status === 403) throw new Error('BAD_KEY');
  if (!res.ok) throw new Error('HTTP_' + res.status);
  return dynStream(res, onProgress);
}

async function dynStream(res, onProgress) {
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = '', acc = '', stop = null;
  const usage = { in: 0, out: 0 };
  for (;;) {
    const r = await reader.read();
    if (r.done) break;
    buf += dec.decode(r.value, { stream: true });
    const lines = buf.split('\n');
    buf = lines.pop();
    for (const line of lines) {
      if (!line.startsWith('data:')) continue;
      let ev;
      try { ev = JSON.parse(line.slice(5)); } catch (e) { continue; }
      if (ev.type === 'message_start') {
        usage.in = (ev.message && ev.message.usage && ev.message.usage.input_tokens) || 0;
      } else if (ev.type === 'content_block_start' && ev.content_block && ev.content_block.type === 'thinking') {
        onProgress('thinking');
      } else if (ev.type === 'content_block_delta' && ev.delta && ev.delta.type === 'text_delta') {
        acc += ev.delta.text;
        onProgress('writing', acc);
      } else if (ev.type === 'message_delta') {
        if (ev.usage && ev.usage.output_tokens) usage.out = ev.usage.output_tokens;
        if (ev.delta && ev.delta.stop_reason) stop = ev.delta.stop_reason;
      } else if (ev.type === 'error') {
        throw new Error((ev.error && ev.error.message) || 'stream error');
      }
    }
  }
  return { acc: acc, usage: usage, stop: stop };
}

/* ============================ Validation ============================ */

function dynHanRuns(s) {
  return (s || '').match(/[㐀-鿿]+/g) || [];
}

// Word-level segmentation (words, not characters): every Han run must split
// entirely into known words. Backtracking so an early greedy match can't
// wrongly reject a legal split.
function dynSegOK(run, known) {
  const dead = new Set();
  function go(pos) {
    if (pos === run.length) return true;
    if (dead.has(pos)) return false;
    for (let len = Math.min(6, run.length - pos); len >= 1; len--) {
      if (known.has(run.substr(pos, len)) && go(pos + len)) return true;
    }
    dead.add(pos);
    return false;
  }
  return go(0);
}

// Can some subset of chunks, each used at most once, concatenate to the target?
function dynComposable(chunks, target) {
  const t = norm(target);
  const parts = chunks.map(c => norm(c));
  const used = new Array(parts.length).fill(false);
  function go(pos) {
    if (pos === t.length) return true;
    for (let i = 0; i < parts.length; i++) {
      if (!used[i] && parts[i] && t.startsWith(parts[i], pos)) {
        used[i] = true;
        if (go(pos + parts[i].length)) return true;
        used[i] = false;
      }
    }
    return false;
  }
  return go(0);
}

function dynCheckItem(it, known) {
  if (['si', 'mc', 'fill', 'builder', 'reveal'].indexOf(it.type) < 0) return 'unknown type';
  if (!it.prompt || !it.prompt.trim()) return 'empty prompt';
  if (it.type === 'mc' || it.type === 'si') {
    const cs = it.choices || [];
    if (cs.length < 2) return 'needs 2+ choices';
    if (cs.filter(c => c.correct).length !== 1) return 'needs exactly one correct choice';
  } else if (it.type === 'fill') {
    const ans = (it.answers || []).filter(a => norm(a));
    if (!ans.length) return 'no answers';
    // Tier-2 rule: a full-sentence fill graded by string match needs the
    // variant space enumerated (也/都, 没/没有, word order…), not one answer.
    if (norm(ans[0]).length >= 5 && ans.length < 2) return 'full-sentence fill needs 2+ answer variants';
  } else if (it.type === 'builder') {
    const ans = (it.answers || []).filter(a => norm(a));
    if (!ans.length) return 'no answers';
    if ((it.chunks || []).length < 3) return 'too few chunks';
    if (!ans.some(a => dynComposable(it.chunks, a))) return 'chunks cannot build the answer';
  } else if (it.type === 'reveal') {
    if (!it.explain || !it.explain.trim()) return 'no model answer';
    if (!(it.checklist || []).length) return 'no checklist';
  }
  const zhFields = [it.prompt, it.explain]
    .concat(it.answers || [], it.chunks || [], (it.choices || []).map(c => c.text));
  for (const s of zhFields) {
    for (const run of dynHanRuns(s)) {
      if (!dynSegOK(run, known)) return 'unknown word in “' + run + '”';
    }
  }
  return '';
}

// Pedagogical arc position: si → mc → short fill → full-sentence fill →
// builder → reveal. Applied once at set creation (a stable sort), so the
// rendered order honours the arc even when the model's ordering drifts.
function dynStageOrder(it) {
  if (it.type === 'si') return 0;
  if (it.type === 'mc') return 1;
  if (it.type === 'fill') return norm((it.answers && it.answers[0]) || '').length >= 5 ? 3 : 2;
  if (it.type === 'builder') return 4;
  return 5; // reveal
}

function dynValidate(items, known) {
  const kept = [], dropped = [];
  for (const it of items) {
    const err = dynCheckItem(it, known);
    if (err) { dropped.push(it.type + ': ' + err); console.warn('[dyn] dropped', err, it); }
    else kept.push(it);
  }
  return { kept: kept, dropped: dropped };
}

// Every NEW/SHAKY target should be featured by a recognition item (si/mc)
// before it is produced. The arc sort already puts all si/mc first, so the
// check reduces to: does such an item exist at all? Gaps are surfaced in the
// set note, never dropped — a set missing a scaffold is still usable.
function dynScaffoldGaps(items, targets) {
  const gaps = [];
  for (const w of dynScaffoldTargets(targets)) {
    const has = items.some(it => (it.type === 'mc' || it.type === 'si') &&
      [it.prompt].concat((it.choices || []).map(c => c.text)).some(s => (s || '').indexOf(w.zh) >= 0));
    if (!has) gaps.push(w.zh);
  }
  return gaps;
}

/* ============================ Renderer ============================ */

function dynEsc(s) {
  return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function dynAnswerBlock(it) {
  // Contract: .reveal-box lives only inside fill/reveal exercises, so builders
  // get a dyn-hint style toggle instead.
  return '<button type="button" class="dyn-hintbtn">show answer</button>' +
    '<div class="dyn-hint"><strong>' + dynEsc(it.answers[0]) + '</strong> — ' + dynEsc(it.explain) + '</div>';
}

function dynItemHTML(it, i) {
  const open = '<div class="exercise" data-exercise="' + it.type + '" data-dyn-idx="' + i + '"';
  const hint = it.hint_en
    ? '<button type="button" class="dyn-hintbtn">hint</button><div class="dyn-hint">' + dynEsc(it.hint_en) + '</div>'
    : '';
  const head = '<p class="prompt">' + dynEsc(it.prompt) + '</p>' + hint;
  if (it.type === 'mc' || it.type === 'si') {
    const lis = it.choices.map(c =>
      '<li data-correct="' + (c.correct ? 'true' : 'false') + '">' + dynEsc(c.text) +
      ' <span class="why">' + (c.correct ? '✓ ' : '✗ ') + dynEsc(c.why) + '</span></li>').join('');
    return open + '>' + head + '<ul class="choices">' + lis + '</ul><div class="feedback"></div></div>';
  }
  if (it.type === 'fill') {
    return open + ' data-answer="' + dynEsc(it.answers.join('|')) + '">' + head +
      '<div class="dyn-inputrow"><input type="text" placeholder="输入你的答案"> <button type="button" class="check">Check</button></div>' +
      '<div class="feedback"></div>' +
      '<button type="button" class="reveal">Show answer</button>' +
      '<div class="reveal-box"><p><strong>' + dynEsc(it.answers[0]) + '</strong></p><p>' + dynEsc(it.explain) + '</p></div></div>';
  }
  if (it.type === 'builder') {
    const chunks = it.chunks.map(c => '<span class="chunk">' + dynEsc(c) + '</span>').join('');
    return open + ' data-answer="' + dynEsc(it.answers.join('|')) + '">' + head +
      '<div class="builder"><div class="bank">' + chunks + '</div><div class="drop"></div></div>' +
      '<div class="actions"><button type="button" class="check">Check</button>' +
      '<button type="button" class="reset">Reset</button></div><div class="feedback"></div>' +
      dynAnswerBlock(it) + '</div>';
  }
  const cl = it.checklist.map(c => '<li>' + dynEsc(c) + '</li>').join('');
  return open + '>' + head +
    '<div class="writing-area"><textarea rows="3" placeholder="写你的答案……"></textarea></div>' +
    '<button type="button" class="reveal">Show a model answer</button>' +
    '<div class="reveal-box"><p>' + dynEsc(it.explain) + '</p><ul>' + cl + '</ul></div></div>';
}

function dynRender() {
  const wrap = dynEl('dyn-items');
  wrap.innerHTML = dynState.items.map(dynItemHTML).join('\n');
  wrap.querySelectorAll('[data-exercise="fill"]').forEach(wireFill);
  wrap.querySelectorAll('[data-exercise="mc"], [data-exercise="si"]').forEach(wireMC);
  wrap.querySelectorAll('[data-exercise="builder"]').forEach(wireBuilder);
  wrap.querySelectorAll('[data-exercise="reveal"]').forEach(el => { wireReveal(el); aiAddGradeButton(el); });
  wrap.querySelectorAll('[data-exercise]').forEach(el => {
    const i = el.getAttribute('data-dyn-idx');
    if (dynState.done[i]) {
      el.classList.add('done');
      const fb = el.querySelector('.feedback');
      if (fb && !fb.textContent) { fb.textContent = '✓ completed earlier'; fb.className = 'feedback ok'; }
    }
    const ta = el.querySelector('textarea');
    if (ta) {
      if (dynState.drafts[i]) ta.value = dynState.drafts[i];
      let t = null;
      ta.addEventListener('input', () => {
        clearTimeout(t);
        t = setTimeout(() => {
          if (ta.value.trim()) dynState.drafts[i] = ta.value; else delete dynState.drafts[i];
          dynSave();
        }, 500);
      });
    }
  });
  dynNote();
  dynEl('dyn-set').hidden = false;
}

function dynNote() {
  const s = dynState;
  const cost = (s.usage.in / 1e6) * DYN_PRICE[0] + (s.usage.out / 1e6) * DYN_PRICE[1];
  dynEl('dyn-note').textContent =
    'Generated ' + s.gen + ' · kept ' + s.kept +
    (s.gen > s.kept ? ' (' + (s.gen - s.kept) + ' failed the vocabulary/format checks)' : '') +
    (s.scaffoldGaps && s.scaffoldGaps.length ? ' · no usage-mc for ' + s.scaffoldGaps.join('、') : '') +
    ' · ' + (s.usage.in / 1000).toFixed(1) + 'k in / ' + (s.usage.out / 1000).toFixed(1) + 'k out ≈ $' +
    cost.toFixed(2) + ' · ' + s.model;
}

/* ============================ State ============================ */

// Every widget success path in script.js funnels through progressMark; on this
// page the stock one is inert (progressInit saw zero exercises at load), so
// replace it to record completion in the dynamic set instead.
progressMark = function (el) {
  el.classList.add('done');
  if (!dynState || !el.getAttribute) return;
  const i = el.getAttribute('data-dyn-idx');
  if (i != null && !dynState.done[i]) { dynState.done[i] = true; dynSave(); }
};

function dynSave() {
  try { localStorage.setItem(DYN_SET_KEY, JSON.stringify(dynState)); } catch (e) {}
}

function dynRestoreSet() {
  try {
    const s = JSON.parse(localStorage.getItem(DYN_SET_KEY) || 'null');
    if (s && s.items && s.items.length) { dynState = s; dynRender(); }
  } catch (e) {}
}

/* ============================ Generate ============================ */

function dynErrMessage(e) {
  if (e.message === 'NO_KEY' || e.message === 'BAD_KEY') return aiErrorMessage(e);
  return 'Generation failed: ' + e.message;
}

async function dynMockGenerate(onProgress) {
  const text = JSON.stringify(DYN_MOCK_BATCH);
  onProgress('thinking');
  await new Promise(r => setTimeout(r, 500));
  for (let i = 80; i < text.length; i += 80) {
    onProgress('writing', text.slice(0, i));
    await new Promise(r => setTimeout(r, 25));
  }
  return { acc: text, usage: { in: 2900, out: 3400 }, stop: 'end_turn' };
}

async function dynGenerate() {
  const targets = dynTargets();
  if (!targets.length || dynBusy) return;
  const nb = dynN(targets.length);
  const sc = dynScaffoldN(targets);
  const n = nb + sc;
  dynBusy = true;
  dynUpdateGen();
  dynEl('dyn-cancel').hidden = false;
  const t0 = Date.now();
  const onProgress = (phase, acc) => {
    if (phase === 'thinking') { dynStatus('Model is thinking…', 'busy'); return; }
    const k = Math.min(n, (acc.match(/"type"/g) || []).length);
    dynStatus('Writing item ' + k + ' of ' + n + ' · ' + (acc.length / 1000).toFixed(1) + 'k chars', 'busy');
  };
  try {
    dynStatus('Connecting…', 'busy');
    const r = DYN_MOCK_AI ? await dynMockGenerate(onProgress) : await dynCallGenerate(targets, nb, sc, onProgress);
    if (r.stop === 'max_tokens') throw new Error('response truncated — raise DYN_MAXTOK');
    const items = (JSON.parse(r.acc).items) || [];
    const v = dynValidate(items, dynKnownAll());
    if (!v.kept.length) throw new Error('all ' + items.length + ' generated items failed validation');
    // Sort into arc order once, before persisting — done{} keys by index.
    const ordered = v.kept.slice().sort((a, b) => dynStageOrder(a) - dynStageOrder(b));
    dynState = {
      at: Date.now(), model: DYN_MODEL, usage: r.usage,
      gen: items.length, kept: ordered.length, items: ordered, done: {}, drafts: {},
      scaffoldGaps: dynScaffoldGaps(ordered, targets),
    };
    dynSave();
    dynRender();
    dynStatus('Done in ' + Math.round((Date.now() - t0) / 1000) + 's', 'ok');
  } catch (e) {
    if (e.name === 'AbortError') dynStatus('Cancelled.', '');
    else dynStatus(dynErrMessage(e), 'bad');
  } finally {
    dynBusy = false;
    dynAbort = null;
    dynEl('dyn-cancel').hidden = true;
    dynUpdateGen();
  }
}

/* ============================ Init ============================ */

document.addEventListener('DOMContentLoaded', () => {
  if (!dynEl('dyn-setup')) return;
  dynRenderLessons();
  dynRestoreSet();
  dynLoadWords();
  dynEl('dyn-generate').addEventListener('click', dynGenerate);
  dynEl('dyn-cancel').addEventListener('click', () => { if (dynAbort) dynAbort.abort(); });
  document.addEventListener('click', e => {
    if (e.target.classList && e.target.classList.contains('dyn-hintbtn')) {
      const d = e.target.nextElementSibling;
      if (d) d.classList.toggle('shown');
    }
  });
});

/* ============================ Mock batch ============================ */
// Canned generation for ?mock=ai / ?mock=all, fed through the same
// accumulate → parse → validate → render pipeline as a real call. The last
// item is deliberately invalid (two correct choices) to prove the discard path.
function dynMockItem(type, prompt, hint, extra) {
  return Object.assign(
    { type: type, prompt: prompt, hint_en: hint, answers: [], chunks: [], choices: [], explain: '', checklist: [] },
    extra);
}
const DYN_MOCK_BATCH = { items: [
  dynMockItem('si', '她一边听音乐一边打扫房间。', 'What does this sentence mean?', { choices: [
    { text: 'She listens to music while cleaning the room.', correct: true, why: '一边 A 一边 B marks two simultaneous ongoing actions by the same person.' },
    { text: 'She listens to music and then cleans the room.', correct: false, why: 'Sequencing would be 先…然后; 一边…一边 means at the same time.' },
    { text: 'She sometimes listens to music, sometimes cleans.', correct: false, why: 'Alternation would be 有时…有时; 一边…一边 is simultaneous.' } ] }),
  dynMockItem('mc', '我找了一个星期，___找到了手机。', 'Finally — after a long effort.', { choices: [
    { text: '终于', correct: true, why: '终于 marks success after a long process; it sits before the verb.' },
    { text: '马上', correct: false, why: '马上 means "right away" — it contradicts a week of searching.' },
    { text: '已经', correct: false, why: '已经 marks completion but loses the finally-after-effort meaning.' } ] }),
  dynMockItem('fill', '我昨天在公园___了我的老师。', 'The verb you need means "to run into (unexpectedly)".', {
    answers: ['遇到'],
    explain: '遇到 = meet by chance. It takes a person as its object and pairs with 了 for the completed event.' }),
  dynMockItem('fill', '我先吃饭，___去上班。', 'First..., then...', {
    answers: ['然后', '然后再', '再'],
    explain: '先 A，然后(再) B orders two actions; 再 alone also works before the second verb.' }),
  dynMockItem('fill', '这件事对我很___。', '', {
    answers: ['重要'],
    explain: '对 + person + 很 + Adj frames who something matters to: 这件事对我很重要。' }),
  dynMockItem('builder', '他做了什么？', 'Arrange the tiles into one sentence describing what he did.', {
    answers: ['他拿着一本书回家了'], chunks: ['他', '拿着', '一本书', '回家', '了'],
    explain: 'V着 (拿着) marks the ongoing background action while 回家 is the main motion; sentence-final 了 marks the completed event.' }),
  // Full-sentence F4 fill, deliberately listed AFTER the builder: the arc sort
  // must move it ahead of the builder when the set renders.
  dynMockItem('fill', '你昨天去公园了吗？', 'Answer no — you did not go. Type a full sentence; use 没.', {
    answers: ['我昨天没去公园', '昨天我没去公园', '我昨天没有去公园', '昨天我没有去公园'],
    explain: '没(有) negates a completed past event, and 昨天 may sit before or after the subject. No 了 after 没 — the 了 of completion disappears under negation.' }),
  dynMockItem('reveal', '你的房间谁打扫？请写两三句话。', 'Say who cleans, how often, and what you do afterwards — try 自己 and 然后.', {
    explain: '我自己打扫房间。我每个星期六打扫，然后一边听音乐一边休息。(I clean my room myself, every Saturday, then I rest while listening to music.)',
    checklist: ['Did you use 打扫 as the main verb?', '自己 goes right before the verb it emphasises.',
      '然后 links your follow-up action.', 'Time words (每个星期六) come before the verb.'] }),
  dynMockItem('reveal', '对你来说，什么最重要？为什么？', 'Name the thing, then give the reason with 因为.', {
    explain: '对我来说，朋友最重要，因为好朋友都想听我说话。(To me friends matter most, because good friends want to hear what I have to say.)',
    checklist: ['对…来说 frames whose view it is.', '最 + Adj marks the superlative.', 'Did you give a reason with 因为?'] }),
  dynMockItem('mc', '我___去上班。', 'Deliberately broken mock item — the validator must drop it.', { choices: [
    { text: '昨天', correct: true, why: 'broken' },
    { text: '今天', correct: true, why: 'broken — two correct answers' } ] }),
] };
