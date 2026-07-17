/**
 * interactions.js — Unified Interaction Layer for Novelverse Forge v2
 * ====================================================================
 * Scroll effects, IntersectionObserver entrance animations, ripple effect,
 * tooltip system, toast notifications, counter animations, header shrink.
 */

const NovelverseInteractions = (() => {
  'use strict';

  // ------------------------------------------------------------------
  // Ripple Effect on all .btn elements
  // ------------------------------------------------------------------
  function initRipple() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn, button:not([data-no-ripple])');
      if (!btn) return;

      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = `${size}px`;
      ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
      ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
      btn.appendChild(ripple);
      ripple.addEventListener('animationend', () => ripple.remove());
    });
  }

  // ------------------------------------------------------------------
  // Header shrink on scroll
  // ------------------------------------------------------------------
  function initHeaderShrink() {
    const header = document.querySelector('.site-header');
    if (!header) return;

    let lastScrollY = 0;
    const onScroll = () => {
      const scrollY = window.scrollY;
      header.classList.toggle('scrolled', scrollY > 60);

      // Hide on scroll down, show on scroll up (optional)
      if (scrollY > 200 && scrollY > lastScrollY) {
        header.style.transform = 'translateY(-100%)';
      } else {
        header.style.transform = '';
      }
      lastScrollY = scrollY;
    };

    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ------------------------------------------------------------------
  // IntersectionObserver — entrance animations
  // ------------------------------------------------------------------
  function initScrollReveal() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.entity-card, .timeline-event-card, .section-header')
      .forEach((el) => {
        el.classList.add('reveal-target');
        observer.observe(el);
      });
  }

  // ------------------------------------------------------------------
  // Counter Animation (hero stats)
  // ------------------------------------------------------------------
  function initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-count]');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.count, 10);
          const duration = 1500;
          const start = performance.now();

          const animate = (now) => {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(eased * target);
            if (progress < 1) requestAnimationFrame(animate);
            else el.textContent = target;
          };
          requestAnimationFrame(animate);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach((c) => observer.observe(c));
  }

  // ------------------------------------------------------------------
  // Entity Card Mouse Tracking (glow follows cursor)
  // ------------------------------------------------------------------
  function initCardGlow() {
    document.querySelectorAll('.entity-card').forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        card.style.setProperty('--mouse-x', `${x}%`);
        card.style.setProperty('--mouse-y', `${y}%`);
      });
    });
  }

  // ------------------------------------------------------------------
  // Toast Notification System
  // ------------------------------------------------------------------
  function toast(message, type = 'info', duration = 3000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const icons = { info: '📋', success: '✅', error: '❌', bookmark: '🔖' };
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `<span>${icons[type] || '📋'}</span> ${message}`;
    container.appendChild(el);

    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(40px)';
      el.style.transition = 'all 0.3s ease';
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  // ------------------------------------------------------------------
  // Tooltip System (hover on any [data-tooltip] element)
  // ------------------------------------------------------------------
  function initTooltips() {
    let tooltipEl = null;

    const getTooltip = () => {
      if (!tooltipEl) {
        tooltipEl = document.createElement('div');
        tooltipEl.className = 'graph-tooltip';
        tooltipEl.style.display = 'none';
        document.body.appendChild(tooltipEl);
      }
      return tooltipEl;
    };

    document.addEventListener('mouseenter', (e) => {
      const target = e.target.closest('[data-tooltip]');
      if (!target) return;
      const tip = getTooltip();
      tip.textContent = target.dataset.tooltip;
      tip.style.display = 'block';
    }, true);

    document.addEventListener('mousemove', (e) => {
      if (!tooltipEl || tooltipEl.style.display === 'none') return;
      tooltipEl.style.left = `${e.clientX + 15}px`;
      tooltipEl.style.top = `${e.clientY - 12}px`;
    }, true);

    document.addEventListener('mouseleave', (e) => {
      const target = e.target.closest('[data-tooltip]');
      if (!target) return;
      if (tooltipEl) tooltipEl.style.display = 'none';
    }, true);
  }

  // ------------------------------------------------------------------
  // Entity Detail Modal — click any entity card to see full details
  // ------------------------------------------------------------------

  /** Icons and labels for entity types */
  var ENTITY_TYPE_ICONS = { character:'👤', faction:'🏛️', location:'📍', creature:'🐉', event:'📜', item:'⚔️' };
  var ENTITY_TYPE_LABELS = { character:'Character', faction:'Faction', location:'Location', creature:'Being', event:'Event', item:'Item' };

  /** Full field list for each entity type (shown in detail modal) */
  var ENTITY_DETAIL_FIELDS = {
    character:  ['full_name','age','gender','species','appearance','personality','abilities','affiliation','rank','status','first_appearance','narrative_role'],
    faction:    ['full_name','type','leader','members_count','territory','philosophy','alignment','status','symbol'],
    location:   ['full_name','type','parent_location','climate','population','description','significance','controlled_by'],
    creature:   ['full_name','species','habitat','abilities','danger_level','description','is_sentient'],
    event:      ['full_name','date','location','participants','outcome','significance','era','predecessor','successor'],
    item:       ['full_name','type','owner','abilities','description','origin','significance'],
  };

  /** Field display labels (human-readable) */
  var FIELD_LABELS = {
    full_name:'Full Name', age:'Age', gender:'Gender', species:'Species',
    appearance:'Appearance', personality:'Personality', abilities:'Abilities',
    affiliation:'Affiliation', rank:'Rank', status:'Status',
    first_appearance:'First Appearance', narrative_role:'Role',
    type:'Type', leader:'Leader', members_count:'Members', territory:'Territory',
    philosophy:'Philosophy', alignment:'Alignment', symbol:'Symbol',
    parent_location:'Parent Location', climate:'Climate', population:'Population',
    description:'Description', significance:'Significance', controlled_by:'Controlled By',
    habitat:'Habitat', danger_level:'Danger Level', is_sentient:'Sentient',
    date:'Date', location:'Location', participants:'Participants',
    outcome:'Outcome', era:'Era', predecessor:'Predecessor', successor:'Successor',
    owner:'Owner', origin:'Origin',
  };

  /**
   * Initialize click handlers on entity cards to open detail modals.
   */
  function initEntityDetailModals() {
    // Use event delegation on the app container for all entity cards
    var app = document.getElementById('app');
    if (!app) return;

    app.addEventListener('click', function(e) {
      // Find the closest entity card from the click target
      var card = e.target.closest('.entity-card');
      if (!card) return;

      // Don't open modal if user clicked on a <details> summary or <button>
      if (e.target.closest('details') || e.target.closest('button') || e.target.closest('a')) return;

      var entityId = getEntityIdFromCard(card);
      if (!entityId) return;

      var entity = findEntityById(entityId);
      if (!entity) return;

      var modalHTML = buildDetailModalHTML(entity);
      openModal(modalHTML);

      // Bind close button inside the modal
      setTimeout(function() {
        var closeBtn = document.querySelector('.entity-detail-close');
        var overlay = document.querySelector('.modal-overlay');
        if (closeBtn && overlay) {
          closeBtn.addEventListener('click', function() { closeModal(overlay); });
        }
      }, 50);
    });
  }

  /**
   * Extract entity ID from a card element.
   * Cards have id="entity-char_001" format.
   */
  function getEntityIdFromCard(card) {
    var cardId = card.id || '';
    if (cardId.startsWith('entity-')) {
      return cardId.replace('entity-', '');
    }
    // Fallback: try data attribute
    return card.getAttribute('data-entity-id') || '';
  }

  /**
   * Find an entity in WORLD_DATA by its ID.
   */
  function findEntityById(entityId) {
    if (!window.WORLD_DATA || !window.WORLD_DATA.entities) return null;
    var entities = window.WORLD_DATA.entities;
    for (var i = 0; i < entities.length; i++) {
      if (entities[i].id === entityId) return entities[i];
    }
    return null;
  }

  /**
   * Build the full detail modal HTML for a given entity.
   */
  function buildDetailModalHTML(entity) {
    var etype = entity.type || 'character';
    var typeIcon = ENTITY_TYPE_ICONS[etype] || '📄';
    var typeLabel = ENTITY_TYPE_LABELS[etype] || etype;
    var name = escHtml(entity.name || 'Unknown');
    var confidence = entity.confidence || 'medium';
    var attrs = entity.attributes || {};
    var evidence = entity.source_evidence || [];
    var aliases = entity.aliases || [];
    var mentionCount = entity.mention_count || 0;
    var firstMention = entity.first_mention || null;

    // Confidence badge
    var confColors = { high:'#22c55e', medium:'#f59e0b', low:'#ef4444' };
    var confColor = confColors[confidence] || '#6b7280';

    // Build attributes table
    var fields = ENTITY_DETAIL_FIELDS[etype] || [];
    var attrRows = '';
    for (var i = 0; i < fields.length; i++) {
      var field = fields[i];
      var val = attrs[field];
      if (val === null || val === undefined || val === '') continue;
      if (Array.isArray(val)) val = val.join(', ');
      val = String(val);
      if (val.length > 300) val = val.substring(0, 300) + '…';
      var label = FIELD_LABELS[field] || field.replace(/_/g, ' ').replace(/\b\w/g, function(c){ return c.toUpperCase(); });
      attrRows += '<tr><th>' + escHtml(label) + '</th><td>' + escHtml(val) + '</td></tr>';
    }
    var attrTable = attrRows ? '<table class="entity-detail-table">' + attrRows + '</table>' : '<p class="entity-detail-empty">No detailed attributes available.</p>';

    // Aliases
    var aliasesHTML = '';
    if (aliases.length > 0) {
      aliasesHTML = '<div class="entity-detail-aliases"><span class="detail-label">Also known as:</span> ' +
        aliases.map(function(a){ return '<span class="alias-tag">' + escHtml(a) + '</span>'; }).join(' ') +
        '</div>';
    }

    // Source evidence (all citations)
    var evidenceHTML = '';
    if (evidence.length > 0) {
      var evItems = '';
      for (var i = 0; i < Math.min(evidence.length, 10); i++) {
        evItems += '<li>' + escHtml(String(evidence[i]).substring(0, 250)) + '</li>';
      }
      evidenceHTML = '<div class="entity-detail-evidence"><h4>📖 Source Evidence</h4><ul>' + evItems + '</ul></div>';
    }

    // Related relationships
    var relationshipsHTML = '';
    if (window.WORLD_DATA && window.WORLD_DATA.relationships) {
      var rels = window.WORLD_DATA.relationships;
      var related = [];
      for (var i = 0; i < rels.length; i++) {
        if (rels[i].source === entity.id || rels[i].target === entity.id) {
          related.push(rels[i]);
        }
      }
      if (related.length > 0) {
        var REL_TYPE_LABELS = {
          romantic:'💕 Romantic', sibling:'👥 Sibling', parent_child:'👶 Parent-Child',
          master_apprentice:'📚 Master-Apprentice', enmity:'⚔️ Enmity', ally:'🤝 Ally',
          allegiance:'🏴 Allegiance', blood_bond:'🩸 Blood Bond',
          creator_creation:'🔧 Creator-Creation', possessor_possessed:'🔑 Possession', mentor:'🧭 Mentor',
        };
        var relItems = '';
        for (var i = 0; i < Math.min(related.length, 15); i++) {
          var rel = related[i];
          var otherId = rel.source === entity.id ? rel.target : rel.source;
          var otherEntity = findEntityById(otherId);
          var otherName = otherEntity ? otherEntity.name : otherId;
          var relLabel = REL_TYPE_LABELS[rel.relation_type] || rel.relation_type;
          var direction = rel.source === entity.id ? '→' : '←';
          relItems += '<li><span class="rel-badge">' + relLabel + '</span> ' + direction + ' <strong>' + escHtml(otherName) + '</strong></li>';
        }
        relationshipsHTML = '<div class="entity-detail-relationships"><h4>🕸️ Relationships</h4><ul>' + relItems + '</ul></div>';
      }
    }

    // Mention stats
    var mentionsInfo = '';
    if (mentionCount > 0 || firstMention) {
      var chap = firstMention ? (firstMention.chapter || '?') : '?';
      var para = firstMention ? (firstMention.paragraph || '?') : '?';
      mentionsInfo = '<div class="entity-detail-mentions"><span>📌 Mentioned <strong>' + mentionCount + '</strong> time(s)</span>' +
        (firstMention ? '<span> · First: Chapter ' + chap + ', Paragraph ' + para + '</span>' : '') +
        '</div>';
    }

    return '' +
      '<div class="entity-detail-modal">' +
        '<button class="entity-detail-close" aria-label="Close detail">✕</button>' +
        '<div class="entity-detail-header">' +
          '<span class="entity-detail-icon">' + typeIcon + '</span>' +
          '<div>' +
            '<h2>' + escHtml(name) + '</h2>' +
            '<span class="entity-detail-type">' + typeLabel + '</span>' +
            '<span class="entity-detail-confidence" style="background:' + confColor + '">' + confidence.toUpperCase() + '</span>' +
          '</div>' +
        '</div>' +
        aliasesHTML +
        mentionsInfo +
        '<hr class="entity-detail-divider">' +
        attrTable +
        relationshipsHTML +
        evidenceHTML +
      '</div>';
  }

  function escHtml(s) {
    if (!s) return '';
    var d = document.createElement('div');
    d.textContent = String(s);
    return d.innerHTML;
  }

  // ------------------------------------------------------------------
  // Modal System (generic)
  // ------------------------------------------------------------------
  function openModal(contentHTML) {
    var overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = '<div class="modal-content entity-detail-modal-wrapper">' + contentHTML + '</div>';
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeModal(overlay);
    });
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    // Focus trap — close on Escape
    var onEsc = function(e) {
      if (e.key === 'Escape') { closeModal(overlay); document.removeEventListener('keydown', onEsc); }
    };
    document.addEventListener('keydown', onEsc);
  }

  function closeModal(overlay) {
    overlay.style.opacity = '0';
    overlay.style.transition = 'opacity 0.2s ease';
    setTimeout(function() {
      overlay.remove();
      document.body.style.overflow = '';
    }, 200);
  }

  // ------------------------------------------------------------------
  // Init
  // ------------------------------------------------------------------
  function init() {
    initRipple();
    initHeaderShrink();
    initScrollReveal();
    initCounters();
    initCardGlow();
    initTooltips();
    initEntityDetailModals();
  }

  return { init, toast, openModal, closeModal };
})();
