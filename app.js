/* FlowMap-OPD project page: gallery, student wall, lightbox, BibTeX. No dependencies. */
(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const el = (tag, attrs, kids) => {
    const n = document.createElement(tag);
    for (const k in attrs || {}) { if (k === 'class') n.className = attrs[k]; else if (k === 'text') n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]); }
    (kids || []).forEach(c => n.append(c));
    return n;
  };

  /* ---------- BibTeX from the paper header (single place for title and authors) ---------- */
  const titleEl = $('#paper-title'), bib = $('#bib');
  if (titleEl && bib) {
    const authors = $$('#paper-authors .author').map(a => a.dataset.bib).filter(Boolean).join(' and ');
    bib.textContent = '@article{li2026flowmapopd,\n  title   = {' + titleEl.dataset.bibTitle + '},\n  author  = {' + authors +
      '},\n  journal = {arXiv preprint arXiv:2609.37851},\n  year    = {2026}\n}';
  }
  $('#copy-bib').addEventListener('click', async () => {
    const t = bib.textContent, b = $('#copy-bib');
    try { await navigator.clipboard.writeText(t); } catch (e) {
      const r = document.createRange(); r.selectNodeContents(bib); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
      try { document.execCommand('copy'); } catch (e2) { /* selection stays for manual copy */ }
    }
    b.textContent = 'Copied'; setTimeout(() => { b.textContent = 'Copy'; }, 1600);
  });

  const q = new URLSearchParams(location.search);
  if (q.get('open') === 'all') $$('details.fold').forEach(d => { d.open = true; });   /* testing aid: unfold everything */

  /* ---------- gallery ---------- */
  const G = window.GALLERY; if (!G) return;
  const MODELS = {
    base: 'Base', ocr: 'OCR teacher', pick: 'PickScore teacher', geneval: 'GenEval teacher',
    opd: 'FlowMap-OPD'
  };
  const SUB = {};
  const SPECIALIST = { ocr: 'ocr', pickscore: 'pick', geneval: 'geneval' };
  const BB = { flux: 'FLUX.1', sd35: 'SD3.5-Medium' };
  const TASK = { ocr: 'Text rendering', pickscore: 'Visual preference', geneval: 'Object relations' };
  const SETNAME = { ocr: 'OCR test prompt', pickscore: 'DrawBench prompt', geneval: 'GenEval test prompt' };
  const src = (bb, s, m) => 'assets/gallery/' + bb + '/' + s.id + '_' + m + '.webp';
  const role = (task, m) => m === 'opd' ? 'student' : (m === SPECIALIST[task] ? 'specialist' : '');

  const st = { bb: G[q.get('backbone')] ? q.get('backbone') : 'flux', task: 'ocr', i: 0 };
  if (TASK[q.get('task')]) st.task = q.get('task');
  const list = () => G[st.bb][st.task];
  st.i = Math.min(Math.max(parseInt(q.get('i') || '0', 10) || 0, 0), list().length - 1);
  const cur = () => list()[st.i];

  if (q.get('focus') === 'gallery') document.body.classList.add('focus-gallery');   /* testing aid: show the gallery only */
  const stage = $('#g-stage'), thumbs = $('#g-thumbs');

  function renderStage() {
    const s = cur();
    stage.style.setProperty('--n', s.cols.length);
    stage.replaceChildren(...s.cols.map((m, j) => {
      const r = role(st.task, m);
      const img = el('img', { src: src(st.bb, s, m), alt: MODELS[m] + ' output for the prompt: ' + s.prompt, width: 512, height: 512, decoding: 'async' });
      const btn = el('button', { type: 'button', class: 'tile', 'aria-label': 'Enlarge ' + MODELS[m] + ' image' }, [img]);
      btn.addEventListener('click', () => openLightbox(j));
      const cap = el('figcaption', {}, [el('span', { class: 'mname', text: MODELS[m] })]);
      if (SUB[m]) cap.append(el('span', { class: 'msub', text: SUB[m] }));
      if (r) cap.append(el('span', { class: 'badge', text: r === 'student' ? 'Student' : 'Specialist' }));
      return el('figure', { class: 'cell ' + r }, [cap, btn]);
    }));
    $('#g-prompt').textContent = s.prompt;
    const meta = $('#g-meta'); meta.replaceChildren();
    const bits = [BB[st.bb], TASK[st.task]];
    if (st.bb === 'sd35') bits.push(SETNAME[st.task] + ' ' + parseInt(s.id.split('_')[1], 10));
    bits.push('seed ' + s.seed);
    bits.forEach(b => meta.append(el('span', { text: b })));
    if (s.lc) { const c = el('span'); c.innerHTML = 'student checkpoint λ<sub>c</sub> = ' + s.lc; meta.append(c); }
    meta.append(el('span', { class: 'count', text: (st.i + 1) + ' / ' + list().length }));
  }
  function renderThumbs() {
    thumbs.replaceChildren(...list().map((s, i) => {
      const b = el('button', { type: 'button', class: 'thumb', 'aria-label': 'Example ' + (i + 1) + ': ' + s.prompt.slice(0, 80), 'aria-pressed': String(i === st.i) },
        [el('img', { src: 'assets/gallery/' + st.bb + '/' + s.id + '_thumb.webp', alt: '', width: 120, height: 120, loading: 'lazy' })]);
      b.addEventListener('click', () => go(i));
      return b;
    }));
  }
  function markThumb(scroll) {
    $$('.thumb', thumbs).forEach((b, i) => {
      b.setAttribute('aria-pressed', String(i === st.i));
      if (i === st.i && scroll) thumbs.scrollTo({ left: b.offsetLeft - thumbs.clientWidth / 2 + b.clientWidth / 2, behavior: 'smooth' });
    });
  }
  function syncControls() {
    $$('[data-bb]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.bb === st.bb)));
    $$('[data-task]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.task === st.task)));
  }
  function syncUrl() {
    const p = new URLSearchParams(location.search);
    p.set('backbone', st.bb); p.set('task', st.task); p.set('i', st.i);
    try { history.replaceState(null, '', location.pathname + '?' + p + location.hash); } catch (e) { /* file:// */ }
  }
  function go(i) { const n = list().length; st.i = (i + n) % n; renderStage(); markThumb(true); syncUrl(); }
  function setView(bb, task, i) {
    st.bb = bb; st.task = task; st.i = i || 0;
    syncControls(); renderThumbs(); renderStage(); markThumb(true); syncUrl();
    const sc = $('.stage-scroll'); if (sc) sc.scrollLeft = 0;
  }
  $$('[data-bb]').forEach(b => b.addEventListener('click', () => setView(b.dataset.bb, st.task, 0)));
  $$('[data-task]').forEach(b => b.addEventListener('click', () => setView(st.bb, b.dataset.task, 0)));
  $('#g-prev').addEventListener('click', () => go(st.i - 1));
  $('#g-next').addEventListener('click', () => go(st.i + 1));

  /* ---------- lightbox ---------- */
  const lb = $('#lightbox'); let lbj = 0;
  function showLightbox() {
    const s = cur(), m = s.cols[lbj], r = role(st.task, m);
    const img = $('#lb-img'); img.src = src(st.bb, s, m); img.alt = MODELS[m] + ' output for the prompt: ' + s.prompt;
    img.className = r;
    $('#lb-label').replaceChildren(el('b', { text: MODELS[m] + (SUB[m] ? ' (' + SUB[m] + ')' : '') }),
      document.createTextNode(' · ' + BB[st.bb] + ' · ' + (lbj + 1) + ' / ' + s.cols.length + (r ? ' · ' + (r === 'student' ? 'student' : 'specialist for this task') : '')));
    $('#lb-prompt').textContent = s.prompt;
  }
  function openLightbox(j) { lbj = j; showLightbox(); if (lb.showModal) lb.showModal(); else lb.setAttribute('open', ''); }
  const lbStep = d => { const n = cur().cols.length; lbj = (lbj + n + d) % n; showLightbox(); };
  $('#lb-prev').addEventListener('click', () => lbStep(-1));
  $('#lb-next').addEventListener('click', () => lbStep(1));
  $('#lb-close').addEventListener('click', () => lb.close());
  lb.addEventListener('click', e => { if (e.target === lb) lb.close(); });

  document.addEventListener('keydown', e => {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    const d = e.key === 'ArrowLeft' ? -1 : 1;
    if (lb.open) { lbStep(d); e.preventDefault(); return; }
    if (/^(INPUT|TEXTAREA|SELECT)$/.test((e.target.tagName || ''))) return;
    const r = $('#gallery').getBoundingClientRect();
    if (r.bottom < 80 || r.top > innerHeight - 80) return;
    go(st.i + d); e.preventDefault();
  });

  /* ---------- student wall ---------- */
  const wall = $('#wall');
  if (wall && G.wall) {
    G.wall.forEach(w => {
      const s = G[w.bb][w.task][w.i];
      const b = el('button', { type: 'button', class: 'walltile', 'aria-label': BB[w.bb] + ' student, ' + TASK[w.task] + ': ' + s.prompt.slice(0, 100) + '. Open comparison.' }, [
        el('img', { src: src(w.bb, s, 'opd'), alt: '', width: 512, height: 512, loading: 'lazy', decoding: 'async' }),
        el('span', { class: 'walltag' }, [el('b', { text: BB[w.bb] }), document.createTextNode(' ' + TASK[w.task])])
      ]);
      b.addEventListener('click', () => { setView(w.bb, w.task, w.i); $('#gallery').scrollIntoView({ behavior: 'smooth', block: 'start' }); });
      wall.append(b);
    });
  }

  syncControls(); renderThumbs(); renderStage(); markThumb(false);
  if (q.get('lightbox')) { const j = cur().cols.indexOf(q.get('lightbox')); if (j >= 0) openLightbox(j); }
})();
