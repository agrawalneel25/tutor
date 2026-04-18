// tutor web UI  -  sidebar nav + markdown viewer + sheet practice mode.

const state = {
  tree: null,
  current: null,  // { kind: 'doc'|'sheet', subject, slug, path }
};

const $nav = document.getElementById('nav');
const $content = document.getElementById('content');
const $breadcrumbs = document.getElementById('breadcrumbs');
const $greeting = document.getElementById('user-greeting');
const $refresh = document.getElementById('refresh');

$refresh.addEventListener('click', () => loadTree());

async function loadTree() {
  const res = await fetch('/api/tree');
  state.tree = await res.json();
  if (state.tree.user?.name) {
    $greeting.textContent = `Hi, ${state.tree.user.name}`;
  }
  renderNav();
  if (state.current) reopen();
}

function renderNav() {
  $nav.innerHTML = '';
  for (const s of state.tree.subjects) {
    const subj = document.createElement('div');
    subj.className = 'subject';
    subj.innerHTML = `<div class="code">${s.code}</div><div class="title">${s.title}</div>`;
    $nav.appendChild(subj);

    if (s.chapters.length) {
      const sec = section('Chapters');
      for (const c of s.chapters) sec.appendChild(navLink(
        c.slug.replace(/^ch\d+-/, 'ch $& ').replace('ch ch', 'ch '),
        null,
        () => openDoc(s.slug, 'chapters', c.slug, c.has_teach ? 'teach' : 'notes')
      ));
      $nav.appendChild(sec);
    }

    if (s.lectures.length) {
      const sec = section('Lectures');
      for (const l of s.lectures) {
        const title = l.number != null ? `L${String(l.number).padStart(2,'0')} · ${l.title}` : l.slug;
        sec.appendChild(navLink(title, null,
          () => openDoc(s.slug, 'lectures', l.slug, l.has_teach ? 'teach' : (l.has_notes ? 'notes' : 'transcript'))));
      }
      $nav.appendChild(sec);
    }

    if (s.sheets.length) {
      const sec = section('Problem Sheets');
      for (const sh of s.sheets) {
        const meta = sh.total ? `${sh.done}/${sh.total}` : ' - ';
        sec.appendChild(navLink(sh.slug, meta,
          () => openSheet(s.slug, sh.slug)));
      }
      $nav.appendChild(sec);
    }
  }
}

function section(label) {
  const d = document.createElement('div');
  d.className = 'section';
  const l = document.createElement('div');
  l.className = 'section-label';
  l.textContent = label;
  d.appendChild(l);
  return d;
}

function navLink(label, meta, onClick) {
  const a = document.createElement('a');
  a.textContent = label;
  if (meta) {
    const m = document.createElement('span');
    m.className = 'meta';
    m.textContent = meta;
    a.appendChild(m);
  }
  a.addEventListener('click', () => {
    for (const el of $nav.querySelectorAll('a.active')) el.classList.remove('active');
    a.classList.add('active');
    onClick();
  });
  return a;
}

async function openDoc(subject, kind, slug, file) {
  // kind ∈ chapters|lectures ; file ∈ teach|notes|transcript
  const ext = file === 'transcript' ? '.txt' : '.md';
  const path = `subjects/${subject}/${kind}/${slug}/${file}${ext}`;
  state.current = { kind: 'doc', subject, slug, path, which: file };
  setBreadcrumbs([subject, kind, slug, file]);

  const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  if (!res.ok) {
    $content.innerHTML = `<h2>Not found</h2><p><code>${path}</code> doesn't exist yet. Run <code>/teach ${subject} ${slug}</code> in Claude Code.</p>`;
    return;
  }
  const md = await res.text();
  const availableTabs = ['teach', 'notes', 'transcript'].filter(t => {
    // We don't know which files exist without re-fetching, but tree tells us.
    const subj = state.tree.subjects.find(s => s.slug === subject);
    const entry = (subj?.[kind] || []).find(x => x.slug === slug);
    if (!entry) return true;
    if (t === 'teach') return entry.has_teach;
    if (t === 'notes') return entry.has_notes;
    if (t === 'transcript') return entry.has_transcript;
    return false;
  });
  const tabs = availableTabs.map(t => {
    const cls = t === file ? 'primary' : 'ghost';
    return `<button class="${cls}" data-tab="${t}">${t}</button>`;
  }).join(' ');
  $content.innerHTML = `<div class="reveal-controls">${tabs}</div><div id="doc"></div>`;
  renderMarkdown(document.getElementById('doc'), file === 'transcript' ? '```\n' + md + '\n```' : md);
  for (const btn of $content.querySelectorAll('[data-tab]')) {
    btn.addEventListener('click', () => openDoc(subject, kind, slug, btn.dataset.tab));
  }
}

async function openSheet(subject, slug) {
  state.current = { kind: 'sheet', subject, slug };
  setBreadcrumbs([subject, 'sheets', slug]);
  const res = await fetch(`/api/sheet?subject=${subject}&slug=${slug}`);
  if (!res.ok) {
    $content.innerHTML = `<h2>Sheet not found</h2><p>Run <code>/practice ${subject} ${slug}</code> in Claude Code to prepare it.</p>`;
    return;
  }
  const sheet = await res.json();
  renderSheet(sheet);
}

function renderSheet(sheet) {
  const total = sheet.questions.length;
  const done = sheet.questions.filter(q => q.state?.status === 'done').length;
  const pct = total ? Math.round(100 * done / total) : 0;
  const current = sheet.current || sheet.questions[0]?.id;

  $content.innerHTML = `
    <div class="sheet-view">
      <div class="sheet-header">
        <h1 style="margin:0">${sheet.slug}</h1>
        <div class="progress-bar"><div style="width:${pct}%"></div></div>
        <div style="font-size:13px;color:var(--fg-dim);font-variant-numeric:tabular-nums">${done}/${total}</div>
      </div>
      <div class="sheet-pager" id="pager"></div>
      <div id="q-body"></div>
    </div>
  `;

  const pager = document.getElementById('pager');
  for (const q of sheet.questions) {
    const cls = ['pill', q.state?.status || 'pending'];
    if (q.id === current) cls.push('active');
    const p = document.createElement('div');
    p.className = cls.join(' ');
    p.textContent = q.id.replace(/^q0?/, 'Q');
    p.addEventListener('click', () => showQuestion(sheet, q.id));
    pager.appendChild(p);
  }

  if (current) showQuestion(sheet, current);
}

async function showQuestion(sheet, qid) {
  const q = sheet.questions.find(x => x.id === qid);
  if (!q) return;
  const res = await fetch(`/api/file?path=${encodeURIComponent(q.path)}`);
  const md = await res.text();
  const { frontmatter, body } = splitFrontmatter(md);

  const sections = parseSections(body);
  const state_q = q.state || { status: 'pending', hints_shown: 0 };

  // Persist current
  await postProgress({ subject: sheet.subject, slug: sheet.slug, qid, set_current: true, status: 'in_progress' });

  // Re-render pager active state
  for (const el of document.querySelectorAll('#pager .pill')) {
    el.classList.toggle('active', el.textContent === qid.replace(/^q0?/, 'Q'));
  }

  const fm = frontmatter
    ? `<div class="q-frontmatter">
         <strong>${frontmatter.title || qid}</strong>
         ${frontmatter.technique ? ` · technique: <em>${frontmatter.technique}</em>` : ''}
         ${Array.isArray(frontmatter.theorems) ? ` · ${frontmatter.theorems.map(t => `<code>${t}</code>`).join(' ')}` : ''}
       </div>`
    : '';

  const statementHtml = sections['Statement'] ? render(sections['Statement']) : '<p><em>No statement found.</em></p>';

  const hintButtons = [];
  if (sections['Hint 1']) hintButtons.push('<button data-reveal="hint1">Show Hint 1</button>');
  if (sections['Hint 2']) hintButtons.push('<button data-reveal="hint2">Show Hint 2</button>');
  if (sections['Solution']) hintButtons.push('<button data-reveal="solution" class="primary">Reveal Solution</button>');
  hintButtons.push('<button data-action="skip" class="ghost">Skip</button>');
  hintButtons.push('<button data-action="done" class="ghost">Mark Done</button>');

  const body_html = `
    ${fm}
    <h2>Statement</h2>
    ${statementHtml}
    <div class="reveal-controls">${hintButtons.join(' ')}</div>
    <div id="reveal-area"></div>
    <div class="attempt-box">
      <h3>Your attempt</h3>
      <textarea id="attempt" placeholder="Type your solution here. This is local-only, no Claude invocation.">${state_q.last_attempt || ''}</textarea>
      <div style="margin-top:8px;display:flex;gap:8px">
        <button id="save-attempt">Save attempt</button>
        <button id="check-attempt" class="primary">Check via Claude (copy prompt)</button>
      </div>
    </div>
  `;
  document.getElementById('q-body').innerHTML = body_html;
  // Math in statement was already rendered inline via render(); no extra pass needed.

  const revealArea = document.getElementById('reveal-area');
  const reveals = {};

  function reveal(which, title, cls, content) {
    if (reveals[which]) return;
    reveals[which] = true;
    const div = document.createElement('div');
    div.className = cls;
    div.innerHTML = `<h3>${title}</h3>${render(content)}`;
    revealArea.appendChild(div);
  }

  for (const btn of document.querySelectorAll('[data-reveal]')) {
    btn.addEventListener('click', async () => {
      const r = btn.dataset.reveal;
      if (r === 'hint1') {
        reveal('hint1', 'Hint 1', 'hint-block', sections['Hint 1']);
        await postProgress({ subject: sheet.subject, slug: sheet.slug, qid, hints_shown: Math.max(1, state_q.hints_shown || 0) });
      } else if (r === 'hint2') {
        reveal('hint2', 'Hint 2', 'hint-block', sections['Hint 2']);
        await postProgress({ subject: sheet.subject, slug: sheet.slug, qid, hints_shown: Math.max(2, state_q.hints_shown || 0) });
      } else if (r === 'solution') {
        reveal('sol', 'Solution', 'solution-block', sections['Solution']);
        if (sections['Common pitfalls']) reveal('pit', 'Common pitfalls', 'pitfalls-block', sections['Common pitfalls']);
      }
    });
  }

  document.querySelector('[data-action="skip"]').addEventListener('click', async () => {
    await postProgress({ subject: sheet.subject, slug: sheet.slug, qid, status: 'skipped' });
    const next = nextQuestion(sheet, qid);
    if (next) showQuestion(sheet, next);
  });
  document.querySelector('[data-action="done"]').addEventListener('click', async () => {
    await postProgress({ subject: sheet.subject, slug: sheet.slug, qid, status: 'done' });
    const next = nextQuestion(sheet, qid);
    if (next) showQuestion(sheet, next);
  });

  document.getElementById('save-attempt').addEventListener('click', async () => {
    const val = document.getElementById('attempt').value;
    await postProgress({ subject: sheet.subject, slug: sheet.slug, qid, last_attempt: val });
    flash('saved');
  });

  document.getElementById('check-attempt').addEventListener('click', () => {
    const val = document.getElementById('attempt').value;
    const prompt = `/check ${val}`;
    navigator.clipboard?.writeText(prompt);
    flash('copied /check prompt');
  });
}

function nextQuestion(sheet, qid) {
  const i = sheet.questions.findIndex(x => x.id === qid);
  for (let j = i + 1; j < sheet.questions.length; j++) {
    if (sheet.questions[j].state?.status !== 'done') return sheet.questions[j].id;
  }
  return null;
}

async function postProgress(update) {
  await fetch('/api/progress', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(update),
  });
}

// --- markdown + math helpers ---

function renderMarkdown(target, md) {
  target.innerHTML = render(md);
}

// Marked's parser treats `_` and `*` inside $...$ as emphasis, which mangles
// subscripts like $P_{n,a}$ before KaTeX sees them. We protect math spans
// with unique placeholders, run marked on the rest, then swap KaTeX HTML in.
function render(md) {
  if (!md) return '';
  const spans = [];
  const token = (i) => `@@MATH_${i}_ZZ@@`;

  // Block math first — $$...$$ — can span multiple lines.
  let src = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, body) => {
    spans.push({ display: true, body });
    return token(spans.length - 1);
  });

  // Inline math — $...$ — single line, non-empty, no surrounding whitespace
  // inside the delimiters so "$5 and $10" currency does not match.
  src = src.replace(/\$(\S(?:[^\n$]*\S)?)\$/g, (_, body) => {
    spans.push({ display: false, body });
    return token(spans.length - 1);
  });

  let html = marked.parse(src, { gfm: true, breaks: false });

  html = html.replace(/@@MATH_(\d+)_ZZ@@/g, (_, i) => {
    const { display, body } = spans[parseInt(i, 10)];
    if (!window.katex) return (display ? '$$' : '$') + body + (display ? '$$' : '$');
    try {
      return katex.renderToString(body, { displayMode: display, throwOnError: false });
    } catch (err) {
      return `<span class="katex-error" title="${String(err).replace(/"/g, "'")}">${display ? '$$' : '$'}${body}${display ? '$$' : '$'}</span>`;
    }
  });

  return html;
}

function splitFrontmatter(md) {
  if (!md.startsWith('---')) return { frontmatter: null, body: md };
  const end = md.indexOf('\n---', 3);
  if (end < 0) return { frontmatter: null, body: md };
  const yaml = md.slice(3, end).trim();
  const body = md.slice(end + 4).replace(/^\n+/, '');
  try {
    const fm = jsyaml.load(yaml);
    return { frontmatter: fm, body };
  } catch (e) {
    return { frontmatter: null, body: md };
  }
}

function parseSections(md) {
  // Split on '## Heading' into a map { heading: body }.
  const out = {};
  const parts = md.split(/^##\s+/m);
  // First part is pre-section preamble; skip.
  for (let i = 1; i < parts.length; i++) {
    const [first, ...rest] = parts[i].split('\n');
    out[first.trim()] = rest.join('\n').trim();
  }
  return out;
}

function setBreadcrumbs(parts) {
  $breadcrumbs.innerHTML = parts.map((p, i) =>
    `<span>${p}</span>${i < parts.length - 1 ? '<span class="sep">/</span>' : ''}`
  ).join('');
}

function reopen() {
  const c = state.current;
  if (!c) return;
  if (c.kind === 'doc') openDoc(c.subject, c.path.split('/')[2], c.slug, c.which);
  else if (c.kind === 'sheet') openSheet(c.subject, c.slug);
}

let flashTimer = null;
function flash(msg) {
  let el = document.getElementById('flash');
  if (!el) {
    el = document.createElement('div');
    el.id = 'flash';
    Object.assign(el.style, {
      position: 'fixed', bottom: '16px', right: '16px',
      background: 'var(--bg-panel)', border: '1px solid var(--border)',
      padding: '8px 14px', borderRadius: '6px', fontSize: '13px',
      color: 'var(--fg)', zIndex: 100,
    });
    document.body.appendChild(el);
  }
  el.textContent = msg;
  el.style.opacity = '1';
  clearTimeout(flashTimer);
  flashTimer = setTimeout(() => el.style.opacity = '0', 1400);
}

window.addEventListener('DOMContentLoaded', () => loadTree());
