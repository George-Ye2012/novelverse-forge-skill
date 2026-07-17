/**
 * timeline.js v2 — Interactive Timeline for Novelverse Forge
 * ============================================================
 * Wheel zoom, drag-to-pan, SVG-shaped event nodes, pulse glow on unread,
 * gradient connection line, expanded detail panels with animation.
 */

const NovelverseTimeline = (() => {
  'use strict';

  const CFG = {
    zoomStep: 0.15, minZoom: 0.3, maxZoom: 3.0,
    defaultGap: 28,
    scrollToEndDelay: 600,
    dragThreshold: 4,
  };

  let state = { zoomLevel: 1.0, currentEra: 'all', mainOnly: false,
                isDragging: false, dragStartX: 0, dragScrollLeft: 0, expandedCard: null };
  let dom = {};

  function init() {
    dom.container = document.getElementById('timeline-container');
    dom.track = dom.container?.querySelector('.timeline-track');
    dom.zoomIn = document.getElementById('timeline-zoom-in');
    dom.zoomOut = document.getElementById('timeline-zoom-out');
    dom.reset = document.getElementById('timeline-reset');
    dom.mainOnly = document.getElementById('timeline-main-only');
    dom.eraBtns = document.querySelectorAll('.era-filter-btn');

    if (!dom.container) return;
    bindAll();
    setTimeout(() => scrollToEnd(), CFG.scrollToEndDelay);
  }

  function bindAll() {
    dom.zoomIn?.addEventListener('click', () => zoom(1));
    dom.zoomOut?.addEventListener('click', () => zoom(-1));
    dom.reset?.addEventListener('click', resetAll);
    dom.mainOnly?.addEventListener('change', (e) => { state.mainOnly = e.target.checked; filterAll(); });

    dom.eraBtns.forEach(b => b.addEventListener('click', () => {
      dom.eraBtns.forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      state.currentEra = b.dataset.era;
      filterAll();
    }));

    // Wheel zoom
    dom.container.addEventListener('wheel', (e) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        zoom(e.deltaY < 0 ? 1 : -1);
      }
    }, { passive: false });

    // Drag pan
    dom.container.addEventListener('mousedown', onDragStart);
    dom.container.addEventListener('mousemove', onDragMove);
    dom.container.addEventListener('mouseup', onDragEnd);
    dom.container.addEventListener('mouseleave', onDragEnd);
    dom.container.addEventListener('touchstart', onDragStart, { passive: false });
    dom.container.addEventListener('touchmove', onDragMove, { passive: false });
    dom.container.addEventListener('touchend', onDragEnd);

    // Event card clicks
    dom.container.addEventListener('click', (e) => {
      const card = e.target.closest('.timeline-event-card');
      if (!card || state.isDragging) return;
      toggleExpand(card);
    });

    // Pulse animation on load
    document.querySelectorAll('.timeline-event-card:not(.seen)').forEach(c => {
      c.querySelector('.timeline-dot')?.classList.add('pulse-glow');
    });
  }

  function onDragStart(e) {
    state.isDragging = true;
    state.dragStartX = e.clientX || (e.touches?.[0]?.clientX ?? 0);
    state.dragScrollLeft = dom.container.scrollLeft;
    dom.container.style.cursor = 'grabbing';
    dom.container.style.userSelect = 'none';
  }
  function onDragMove(e) {
    if (!state.isDragging) return;
    const cx = e.clientX || (e.touches?.[0]?.clientX ?? 0);
    const dx = state.dragStartX - cx;
    if (Math.abs(dx) < CFG.dragThreshold) return;
    dom.container.scrollLeft = state.dragScrollLeft + dx;
    if (e.cancelable) e.preventDefault();
  }
  function onDragEnd() {
    state.isDragging = false;
    if (dom.container) {
      dom.container.style.cursor = 'grab';
      dom.container.style.userSelect = '';
    }
  }

  function zoom(dir) {
    const nz = Math.min(CFG.maxZoom, Math.max(CFG.minZoom, state.zoomLevel + dir * CFG.zoomStep));
    if (nz === state.zoomLevel) return;
    state.zoomLevel = nz;
    applyZoom();
  }
  function resetAll() { state.zoomLevel = 1.0; applyZoom(); scrollToEnd(); }
  function applyZoom() {
    if (!dom.track) return;
    dom.track.style.gap = `${CFG.defaultGap * state.zoomLevel}px`;
    const scale = 0.75 + state.zoomLevel * 0.25;
    document.querySelectorAll('.timeline-event-card').forEach(c => {
      c.style.transform = `scale(${scale})`;
    });
  }

  function filterAll() {
    document.querySelectorAll('.timeline-event-card').forEach(card => {
      const era = card.dataset.era;
      let show = state.currentEra === 'all' || era === state.currentEra;
      if (state.mainOnly) show = show && card.dataset.main === 'true';
      card.style.display = show ? '' : 'none';
    });
  }

  function toggleExpand(card) {
    const wasExpanded = card.classList.contains('expanded');
    // Collapse previous
    if (state.expandedCard && state.expandedCard !== card) {
      state.expandedCard.classList.remove('expanded');
      const oldPanel = state.expandedCard.querySelector('.event-detail-panel');
      if (oldPanel) oldPanel.remove();
    }
    if (wasExpanded) {
      card.classList.remove('expanded');
      card.querySelector('.event-detail-panel')?.remove();
      state.expandedCard = null;
    } else {
      card.classList.add('expanded');
      // Build detail panel from data attributes
      const panel = document.createElement('div');
      panel.className = 'event-detail-panel';
      panel.innerHTML = `
        <div class="event-desc">${card.querySelector('.event-content p')?.textContent || ''}</div>
        <div class="event-meta">
          ${card.dataset.year ? `<span>📅 ${card.dataset.year}</span>` : ''}
          ${card.dataset.location ? `<span>📍 ${card.dataset.location}</span>` : ''}
          ${card.dataset.conflict === 'true' ? '<span class="warning-badge">⚠ Temporal note</span>' : ''}
        </div>
      `;
      card.appendChild(panel);
      state.expandedCard = card;
    }
  }

  function scrollToEnd() {
    if (!dom.container) return;
    dom.container.scrollTo({ left: dom.container.scrollWidth, behavior: 'smooth' });
  }

  return { init };
})();
