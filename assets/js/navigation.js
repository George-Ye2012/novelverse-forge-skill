/**
 * navigation.js v4 — Enhanced SPA Router for Novelverse Forge
 * =============================================================
 * Hash-based routing with smooth page transitions, hamburger menu for mobile,
 * browser history support, keyboard shortcuts, deep linking, and transition
 * progress indication.
 *
 * Features:
 *   - 7-page SPA routing (#overview, #timeline, #characters, #factions,
 *     #beings, #relations, #interactive)
 *   - Smooth fade+slide page transitions (400ms in, 200ms out)
 *   - Hamburger menu on mobile (< 768px)
 *   - Keyboard navigation: ← → to cycle pages, 1-7 to jump directly
 *   - Browser back/forward support via hashchange + pushState
 *   - Transition progress bar in the nav
 *   - Deep linking: index.html#characters opens directly to characters
 *   - Scroll-to-top on page change
 *   - Auto-reveals cards on newly activated pages
 */

const NovelverseNavigation = (() => {
  'use strict';

  const CFG = {
    transitionIn: 400,     // ms — page enter animation duration
    transitionOut: 200,    // ms — page exit animation duration
    defaultPage: 'overview',
    mobileBreakpoint: 767, // px — below this, hamburger menu activates
  };

  /** Ordered page list for keyboard cycling */
  const PAGE_ORDER = [
    'overview', 'timeline', 'characters', 'factions',
    'beings', 'relations', 'interactive',
  ];

  /** Page metadata for display labels */
  const PAGE_META = {
    overview:    { label: '总览',    icon: '🏠', shortcut: '1' },
    timeline:    { label: '时间线',  icon: '⏳', shortcut: '2' },
    characters:  { label: '人物',    icon: '👤', shortcut: '3' },
    factions:    { label: '派别',    icon: '🏛️', shortcut: '4' },
    beings:      { label: '生物',    icon: '🐉', shortcut: '5' },
    relations:   { label: '关系网',  icon: '🕸️', shortcut: '6' },
    interactive: { label: '互动',    icon: '🔮', shortcut: '7' },
  };

  let state = {
    currentPage: null,
    isTransitioning: false,
    allPages: [],
    navLinks: [],
    transitionTimer: null,
  };

  // ──────────────────────────────────────────────
  // Initialization
  // ──────────────────────────────────────────────

  function init() {
    // Collect all page sections and nav links
    state.allPages = Array.from(document.querySelectorAll('.page[data-page]'));
    state.navLinks = Array.from(
      document.querySelectorAll('#main-nav a[data-page], .quick-nav-item, .mobile-nav-list a[data-page]')
    );

    // Inject hamburger button if mobile
    injectHamburger();

    // Read initial hash or default to overview
    const hash = window.location.hash.replace('#', '') || CFG.defaultPage;
    navigateTo(hash, { replace: true, animate: false });

    // Bind all navigation events
    bindNavClicks();
    bindHamburger();
    bindOverlayClose();
    bindKeyboard();

    // Browser back/forward
    window.addEventListener('hashchange', onHashChange);

    // Close mobile menu on window resize to desktop
    window.addEventListener('resize', () => {
      if (window.innerWidth > CFG.mobileBreakpoint) {
        closeMobileMenu();
      }
    });
  }

  // ──────────────────────────────────────────────
  // Hamburger Menu Injection
  // ──────────────────────────────────────────────

  function injectHamburger() {
    const nav = document.getElementById('main-nav');
    if (!nav) return;

    // Hamburger toggle button
    const burger = document.createElement('button');
    burger.id = 'hamburger-toggle';
    burger.className = 'hamburger-btn';
    burger.setAttribute('aria-label', 'Toggle navigation menu');
    burger.setAttribute('aria-expanded', 'false');
    burger.innerHTML = '<span class="hamburger-line"></span><span class="hamburger-line"></span><span class="hamburger-line"></span>';
    nav.appendChild(burger);

    // Mobile menu overlay
    const overlay = document.createElement('div');
    overlay.id = 'mobile-nav-overlay';
    overlay.className = 'mobile-nav-overlay';
    overlay.setAttribute('aria-hidden', 'true');

    // Build mobile nav list from PAGE_ORDER, respecting available pages
    const existingPages = new Set(state.allPages.map(p => p.dataset.page));
    let listHTML = '<ul class="mobile-nav-list">';
    for (const pageId of PAGE_ORDER) {
      if (existingPages.has(pageId)) {
        const meta = PAGE_META[pageId] || { label: pageId, icon: '' };
        listHTML += `<li><a href="#${pageId}" data-page="${pageId}">
          <span class="mni-icon">${meta.icon}</span>${meta.label}
        </a></li>`;
      }
    }
    listHTML += '</ul>';
    overlay.innerHTML = `
      <div class="mobile-nav-panel">
        <div class="mobile-nav-header">
          <span class="mobile-nav-title">📖 Navigate</span>
          <button class="mobile-nav-close" aria-label="Close menu">✕</button>
        </div>
        ${listHTML}
      </div>
    `;
    document.body.appendChild(overlay);
  }

  function bindHamburger() {
    const burger = document.getElementById('hamburger-toggle');
    const overlay = document.getElementById('mobile-nav-overlay');
    if (!burger || !overlay) return;

    burger.addEventListener('click', () => {
      const isOpen = overlay.classList.contains('open');
      if (isOpen) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });

    // Close button inside overlay
    overlay.querySelector('.mobile-nav-close')?.addEventListener('click', closeMobileMenu);

    // Click outside the panel to close
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeMobileMenu();
    });

    // Click a mobile nav link → close menu and navigate
    overlay.querySelectorAll('.mobile-nav-list a[data-page]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const pageId = link.dataset.page;
        if (pageId) {
          closeMobileMenu();
          navigateTo(pageId);
        }
      });
    });
  }

  function openMobileMenu() {
    const overlay = document.getElementById('mobile-nav-overlay');
    const burger = document.getElementById('hamburger-toggle');
    if (overlay) {
      overlay.classList.add('open');
      overlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
    if (burger) {
      burger.classList.add('active');
      burger.setAttribute('aria-expanded', 'true');
    }
  }

  function closeMobileMenu() {
    const overlay = document.getElementById('mobile-nav-overlay');
    const burger = document.getElementById('hamburger-toggle');
    if (overlay) {
      overlay.classList.remove('open');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
    if (burger) {
      burger.classList.remove('active');
      burger.setAttribute('aria-expanded', 'false');
    }
  }

  function bindOverlayClose() {
    // Escape key closes mobile menu
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const overlay = document.getElementById('mobile-nav-overlay');
        if (overlay?.classList.contains('open')) {
          closeMobileMenu();
        }
      }
    });
  }

  // ──────────────────────────────────────────────
  // Page Navigation
  // ──────────────────────────────────────────────

  /**
   * Navigate to a page by its data-page identifier.
   * @param {string} pageId — e.g. 'overview', 'timeline'
   * @param {Object} [opts]
   * @param {boolean} [opts.replace] — use replaceState (no history entry)
   * @param {boolean} [opts.animate] — play transition animation
   */
  function navigateTo(pageId, opts = {}) {
    // Validate target page exists (skip conditional pages that weren't built)
    const targetPage = state.allPages.find(p => p.dataset.page === pageId);
    if (!targetPage) {
      // If the target page doesn't exist, redirect to overview
      if (pageId !== CFG.defaultPage) {
        navigateTo(CFG.defaultPage, { replace: true });
      }
      return;
    }

    // No-op if already on this page
    if (pageId === state.currentPage && !state.isTransitioning) return;

    // Prevent rapid double-clicks during transition
    if (state.isTransitioning) {
      // Allow forced navigation but clear pending timer
      if (state.transitionTimer) clearTimeout(state.transitionTimer);
    }

    const doAnimate = opts.animate !== false;
    state.isTransitioning = true;

    // Show transition progress bar
    if (doAnimate) showProgressBar();

    // Update URL hash
    const newHash = `#${pageId}`;
    if (opts.replace) {
      window.history.replaceState(null, '', newHash);
    } else if (window.location.hash !== newHash) {
      window.history.pushState(null, '', newHash);
    }

    // Exit current page with animation
    const current = getActivePage();
    if (current && doAnimate) {
      current.classList.add('exiting');
      current.classList.remove('active');
      setTimeout(() => {
        current.classList.remove('exiting');
      }, CFG.transitionOut);
    } else if (current) {
      current.classList.remove('active');
    }

    // Enter target page
    targetPage.classList.remove('exiting');
    targetPage.classList.add('active');

    if (doAnimate) {
      // Force animation restart
      targetPage.style.animation = 'none';
      targetPage.offsetHeight; // trigger reflow
      targetPage.style.animation = '';
    }

    state.currentPage = pageId;

    // Scroll to top
    window.scrollTo({ top: 0, behavior: doAnimate ? 'smooth' : 'instant' });

    // Update all nav highlights (desktop + mobile)
    updateNavHighlight(pageId);

    // Reveal cards on the new page after transition
    setTimeout(() => {
      targetPage.querySelectorAll(
        '.entity-card.reveal-target, .timeline-event-card.reveal-target, .rel-sentence.reveal-target, .section-header.reveal-target'
      ).forEach(el => el.classList.add('revealed'));
    }, doAnimate ? CFG.transitionIn : 50);

    // Initialize page-specific modules
    if (pageId === 'timeline' && typeof NovelverseTimeline !== 'undefined') {
      setTimeout(() => NovelverseTimeline.init(), CFG.transitionIn + 50);
    }

    // Complete transition
    state.transitionTimer = setTimeout(() => {
      state.isTransitioning = false;
      hideProgressBar();
      // Dispatch custom event for other modules
      window.dispatchEvent(new CustomEvent('nv-page-changed', {
        detail: { page: pageId, pageElement: targetPage },
      }));
    }, CFG.transitionIn + 20);
  }

  function getActivePage() {
    return state.allPages.find(p => p.classList.contains('active')) || null;
  }

  // ──────────────────────────────────────────────
  // Nav Highlights
  // ──────────────────────────────────────────────

  function updateNavHighlight(pageId) {
    // Desktop nav links
    state.navLinks.forEach(link => {
      const target = link.getAttribute('href')?.replace('#', '') || link.dataset.page;
      const isActive = target === pageId;
      link.classList.toggle('active', isActive);
      if (link.tagName === 'A') {
        link.setAttribute('aria-current', isActive ? 'page' : 'false');
      }
    });

    // Mobile nav links (if overlay exists)
    document.querySelectorAll('.mobile-nav-list a[data-page]').forEach(link => {
      const target = link.dataset.page;
      link.classList.toggle('active', target === pageId);
    });
  }

  // ──────────────────────────────────────────────
  // Event Binding
  // ──────────────────────────────────────────────

  function bindNavClicks() {
    // Top nav links (uses event delegation on #main-nav)
    document.getElementById('main-nav')?.addEventListener('click', (e) => {
      const link = e.target.closest('a[data-page]');
      if (!link) return;
      e.preventDefault();
      const pageId = link.dataset.page;
      if (pageId) navigateTo(pageId);
    });

    // Quick nav circle buttons on overview
    document.querySelectorAll('.quick-nav-item').forEach(item => {
      item.addEventListener('click', () => {
        const pageId = item.dataset.page;
        if (pageId) navigateTo(pageId);
      });
    });

    // Brand/logo → overview
    document.querySelector('.nav-brand')?.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo('overview');
    });
  }

  function bindKeyboard() {
    document.addEventListener('keydown', (e) => {
      // Ignore when focused in input/textarea/contenteditable
      const tag = e.target.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || e.target.isContentEditable) return;

      // Arrow keys: cycle pages
      if (e.key === 'ArrowRight' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        cyclePage(1);
      }
      if (e.key === 'ArrowLeft' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        cyclePage(-1);
      }

      // Number keys 1-7: jump directly to page
      if (!e.ctrlKey && !e.metaKey && !e.altKey) {
        for (const [pageId, meta] of Object.entries(PAGE_META)) {
          if (e.key === meta.shortcut && state.allPages.some(p => p.dataset.page === pageId)) {
            e.preventDefault();
            navigateTo(pageId);
            break;
          }
        }
      }
    });
  }

  function onHashChange() {
    const hash = window.location.hash.replace('#', '') || CFG.defaultPage;
    if (hash !== state.currentPage) {
      navigateTo(hash, { replace: true });
    }
  }

  // ──────────────────────────────────────────────
  // Page Cycling
  // ──────────────────────────────────────────────

  /**
   * Cycle to the next or previous page in PAGE_ORDER.
   * Skips pages that don't exist (weren't built due to no content).
   */
  function cyclePage(direction) {
    // Build ordered list of existing pages
    const existingOrder = PAGE_ORDER.filter(
      pageId => state.allPages.some(p => p.dataset.page === pageId)
    );
    if (existingOrder.length === 0) return;

    const currentIdx = existingOrder.indexOf(state.currentPage);
    if (currentIdx < 0) {
      navigateTo(existingOrder[0]);
      return;
    }

    let nextIdx = currentIdx + direction;
    if (nextIdx < 0) nextIdx = existingOrder.length - 1;
    if (nextIdx >= existingOrder.length) nextIdx = 0;

    navigateTo(existingOrder[nextIdx]);
  }

  // ──────────────────────────────────────────────
  // Progress Bar
  // ──────────────────────────────────────────────

  function showProgressBar() {
    let bar = document.getElementById('nav-progress-bar');
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'nav-progress-bar';
      bar.className = 'nav-progress-bar';
      bar.innerHTML = '<div class="nav-progress-fill"></div>';
      document.getElementById('main-nav')?.appendChild(bar);
    }
    bar.classList.add('active');
    const fill = bar.querySelector('.nav-progress-fill');
    if (fill) {
      fill.style.transition = 'none';
      fill.style.width = '0%';
      fill.offsetHeight; // reflow
      fill.style.transition = `width ${CFG.transitionIn}ms cubic-bezier(0.16,1,0.3,1)`;
      fill.style.width = '100%';
    }
  }

  function hideProgressBar() {
    const bar = document.getElementById('nav-progress-bar');
    if (bar) {
      bar.classList.remove('active');
      const fill = bar.querySelector('.nav-progress-fill');
      if (fill) fill.style.width = '0%';
    }
  }

  // ──────────────────────────────────────────────
  // Public API
  // ──────────────────────────────────────────────

  return {
    init,
    navigateTo,
    getActivePage,
    getCurrentPage: () => state.currentPage,
    cyclePage,
    openMobileMenu,
    closeMobileMenu,
  };
})();
