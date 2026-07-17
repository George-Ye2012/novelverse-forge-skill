/**
 * search.js v3 — Cross-Page Search Overlay for Novelverse Forge
 * ===============================================================
 * Full-screen search overlay triggered by nav button or Ctrl+K.
 * Filters across ALL entities regardless of current page.
 * Selecting a result navigates to the correct page and highlights the card.
 */

const NovelverseSearch = (() => {
  'use strict';

  const CFG = { debounceMs: 150, maxResults: 10, minQueryLen: 1 };
  const TYPE_ICONS = { character:'👤', faction:'🏛️', location:'📍', creature:'🐉', event:'📜', item:'⚔️' };

  // Which page each entity type belongs to
  const TYPE_PAGE = {
    character: 'characters',
    faction: 'factions',
    location: 'characters',
    creature: 'beings',
    event: 'timeline',
    item: 'characters',
  };

  let state = { query:'', results:[], highlightedIdx:-1, index:[] };
  let dom = {};

  function init(worldData) {
    dom.trigger = document.getElementById('search-trigger');
    dom.overlay = document.getElementById('search-overlay');
    dom.input = document.getElementById('overlay-search-input');
    dom.resultsList = document.getElementById('overlay-results-list');
    dom.closeBtn = document.getElementById('search-close');

    if (!dom.overlay || !dom.input) return;

    buildIndex(worldData?.entities || []);
    bindEvents();
  }

  function buildIndex(entities) {
    state.index = entities.map(e => {
      const sb = [e.name||'', ...(e.aliases||[]), e.type||''];
      const attrs = e.attributes || {};
      for (const v of Object.values(attrs)) {
        if (typeof v === 'string') sb.push(v);
        if (Array.isArray(v)) sb.push(...v.filter(x => typeof x === 'string'));
      }
      return { entity: e, searchable: sb.filter(Boolean).join(' ').toLowerCase() };
    });
  }

  function bindEvents() {
    // Open overlay
    dom.trigger?.addEventListener('click', openOverlay);
    dom.closeBtn?.addEventListener('click', closeOverlay);
    dom.overlay?.addEventListener('click', (e) => { if (e.target === dom.overlay) closeOverlay(); });

    // Keyboard shortcut: Ctrl+K or Cmd+K
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openOverlay();
      }
      if (e.key === 'Escape' && dom.overlay?.classList.contains('open')) {
        closeOverlay();
      }
    });

    // Input
    let timer;
    dom.input?.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.query = dom.input.value.trim(); performSearch(); }, CFG.debounceMs);
    });

    dom.input?.addEventListener('keydown', onKeyDown);
  }

  function openOverlay() {
    if (!dom.overlay) return;
    dom.overlay.classList.add('open');
    setTimeout(() => dom.input?.focus(), 100);
    state.query = ''; state.results = []; state.highlightedIdx = -1;
    if (dom.input) dom.input.value = '';
    if (dom.resultsList) dom.resultsList.innerHTML = '';
  }

  function closeOverlay() {
    dom.overlay?.classList.remove('open');
    state.highlightedIdx = -1;
  }

  function onKeyDown(e) {
    if (!dom.resultsList || dom.resultsList.children.length === 0) return;
    switch(e.key) {
      case 'ArrowDown': e.preventDefault(); state.highlightedIdx = Math.min(state.results.length-1, state.highlightedIdx+1); updateHighlight(); break;
      case 'ArrowUp': e.preventDefault(); state.highlightedIdx = Math.max(-1, state.highlightedIdx-1); updateHighlight(); break;
      case 'Enter': e.preventDefault();
        if (state.highlightedIdx>=0 && state.highlightedIdx<state.results.length) selectResult(state.results[state.highlightedIdx]);
        else if (state.results.length===1) selectResult(state.results[0]);
        break;
    }
  }

  function updateHighlight() {
    dom.resultsList?.querySelectorAll('li').forEach((li,i) => li.classList.toggle('highlighted', i===state.highlightedIdx));
    if (state.highlightedIdx>=0) {
      const el = dom.resultsList?.children[state.highlightedIdx];
      el?.scrollIntoView({ block:'nearest' });
    }
  }

  function performSearch() {
    state.highlightedIdx = -1; state.results = [];
    if (state.query.length < CFG.minQueryLen) { if(dom.resultsList) dom.resultsList.innerHTML = ''; return; }
    const q = state.query.toLowerCase();
    const terms = q.split(/\s+/).filter(Boolean);
    const scored = state.index.map(entry => {
      let s = 0;
      const nm = entry.entity.name?.toLowerCase()||'';
      for (const t of terms) {
        if (nm===t) s+=10; else if (nm.startsWith(t)) s+=8; else if (nm.includes(t)) s+=5;
        else if ((entry.entity.aliases||[]).some(a=>a.toLowerCase().includes(t))) s+=4;
        else if (entry.searchable.includes(t)) s+=2;
      }
      return {...entry, score:s};
    });
    state.results = scored.filter(r=>r.score>0).sort((a,b)=>b.score-a.score).slice(0,CFG.maxResults);
    renderResults();
  }

  function renderResults() {
    if (!dom.resultsList) return;
    if (!state.results.length) {
      dom.resultsList.innerHTML = `<li style="padding:20px;text-align:center;color:var(--nv-color-text-muted);">🔍 No results for "<strong>${escHtml(state.query)}</strong>"<br><small>Try a character name or faction</small></li>`;
      return;
    }
    const q = state.query.toLowerCase();
    dom.resultsList.innerHTML = state.results.map(r => {
      const icon = TYPE_ICONS[r.entity.type]||'📄';
      const name = escHtml(r.entity.name);
      const hl = highlightMatch(name, q);
      const pageId = TYPE_PAGE[r.entity.type] || 'characters';
      const pageLabel = {overview:'总览',timeline:'时间线',characters:'人物',factions:'派别',beings:'生物',relations:'关系网'}[pageId]||pageId;
      return `<li data-eid="${escHtml(r.entity.id)}" data-etype="${escHtml(r.entity.type)}" data-page="${pageId}">
        <span class="result-type-icon">${icon}</span>
        <div><span class="result-name">${hl}</span></div>
        <span class="result-page-hint">${pageLabel}</span>
        <span class="result-type-label">${r.entity.type}</span>
      </li>`;
    }).join('');

    dom.resultsList.querySelectorAll('li').forEach(li => {
      li.addEventListener('click', () => {
        const r = state.results.find(x=>x.entity.id===li.dataset.eid);
        if (r) selectResult(r);
      });
      li.addEventListener('mouseenter', () => {
        const items = [...dom.resultsList.querySelectorAll('li')];
        state.highlightedIdx = items.indexOf(li); updateHighlight();
      });
    });
  }

  function selectResult(result) {
    const pageId = TYPE_PAGE[result.entity.type] || 'characters';
    closeOverlay();

    // Navigate to the correct page
    if (typeof NovelverseNavigation !== 'undefined') {
      const currentPage = NovelverseNavigation.getCurrentPage();
      const delay = (currentPage === pageId) ? 100 : 500;
      NovelverseNavigation.navigateTo(pageId);

      // After navigation + transition, scroll to and highlight the entity card
      setTimeout(() => {
        const card = document.getElementById(`entity-${result.entity.id}`);
        if (card) {
          const group = card.closest('.entity-group');
          if (group) group.style.display = '';

          card.scrollIntoView({ behavior:'smooth', block:'center' });
          card.style.boxShadow = '0 0 0 4px var(--nv-color-glow, var(--nv-color-accent, #ffff00))';
          card.style.transition = 'box-shadow 0.3s ease';
          card.style.zIndex = '10';
          card.style.position = 'relative';
          setTimeout(() => {
            card.style.boxShadow = '';
            card.style.zIndex = '';
            card.style.position = '';
          }, 2800);
        } else {
          // Maybe it's a timeline event
          const eventCard = document.getElementById(`event-${result.entity.id}`);
          if (eventCard) {
            eventCard.scrollIntoView({ behavior:'smooth', block:'center' });
            eventCard.style.boxShadow = '0 0 0 4px var(--nv-color-glow, var(--nv-color-accent, #ffff00))';
            eventCard.style.transition = 'box-shadow 0.3s ease';
            setTimeout(() => { eventCard.style.boxShadow = ''; }, 2800);
          }
        }
      }, delay);
    } else {
      if (typeof NovelverseInteractions !== 'undefined') {
        NovelverseInteractions.toast(`Navigate to ${result.entity.name}`, 'info', 2500);
      }
    }
  }

  function highlightMatch(text, query) {
    const terms = query.split(/\s+/).filter(Boolean);
    let r = text;
    for (const t of terms) {
      r = r.replace(new RegExp(`(${escRegex(t)})`,'gi'), '<mark class="search-highlight">$1</mark>');
    }
    return r;
  }

  function escHtml(s) { if(!s)return''; const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }
  function escRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); }

  return { init, openOverlay, closeOverlay };
})();
