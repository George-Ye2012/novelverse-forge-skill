/**
 * relation_graph.js v2 — D3.js Relationship Graph for Novelverse Forge
 * ======================================================================
 * Force-directed graph with: elastic node drag, hover glow + scale,
 * double-click focus lock, flow particles on edges, legend click filter,
 * time-slice transitions, SVG shapes by entity type.
 */

const NovelverseRelationGraph = (() => {
  'use strict';

  const CFG = {
    forceStrength: -350, linkDistance: 100, linkStrength: 0.4,
    gravity: 0.04, alphaDecay: 0.015,
    nodeRMin: 8, nodeRMax: 26,
    hoverScale: 1.2, hoverDim: 0.08,
    focusDuration: 800,
    flowSpeed: 30, flowCount: 3,
    nodeColors: { character:'#E74C3C', faction:'#3498DB', location:'#2ECC71',
                  creature:'#9B59B6', event:'#F39C12', item:'#1ABC9C' },
    edgeColors: { sibling:'#FF6B6B', parent_child:'#4ECDC4', master_apprentice:'#FFD93D',
                  romantic:'#FF8C94', enmity:'#FF3333', ally:'#6BCB77',
                  allegiance:'#4D96FF', blood_bond:'#9B59B6',
                  creator_creation:'#00CED1', possessor_possessed:'#FFD700' },
    edgeDash: { enmity:'6,3', romantic:'2,2' },
  };

  let state = { sim: null, svgSel: null, zoom: null, nodes: [], links: [],
                focusedNode: null, timeSlice: 'all', hiddenTypes: new Set() };
  let dom = {};

  function init(worldData) {
    dom.container = document.getElementById('relation-graph');
    dom.svg = document.getElementById('graph-svg');
    dom.tooltip = document.getElementById('graph-tooltip');
    dom.resetBtn = document.getElementById('graph-reset-btn');
    dom.timeSlice = document.getElementById('time-slice-select');
    dom.legend = document.getElementById('graph-legend');

    if (!dom.container || !dom.svg) return;
    if (typeof d3 === 'undefined') { showFallback(worldData); return; }

    buildData(worldData);
    render();
    bindControls();
    buildLegend();
  }

  function buildData(wd) {
    const entities = wd?.entities || [];
    const rels = wd?.relationships || [];
    const idMap = {};
    state.nodes = entities.map((e, i) => { idMap[e.id] = i; return {
      id: e.id, name: e.name, type: e.type || 'character',
      mentionCount: e.mention_count || 1, confidence: e.confidence || 'medium',
      attrs: e.attributes || {},
    };});
    state.links = [];
    rels.forEach(r => {
      const si = idMap[r.source], ti = idMap[r.target];
      if (si !== undefined && ti !== undefined) {
        state.links.push({ source: si, target: ti, type: r.relation_type || 'ally',
                           confidence: r.confidence || 'medium' });
      }
    });
  }

  function render() {
    const W = dom.container.clientWidth || 960;
    const H = dom.container.clientHeight || 600;
    dom.svg.innerHTML = '';
    dom.svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const svg = d3.select('#graph-svg');
    state.svgSel = svg;

    // Defs: glow filter + arrow marker
    const defs = svg.append('defs');
    defs.append('filter').attr('id','glow').append('feGaussianBlur')
      .attr('stdDeviation','2.5').attr('result','blur');
    const merge = defs.select('#glow').append('feMerge');
    merge.append('feMergeNode').attr('in','blur');
    merge.append('feMergeNode').attr('in','SourceGraphic');

    defs.append('marker').attr('id','arrow').attr('viewBox','0 -5 10 10')
      .attr('refX',22).attr('refY',0).attr('markerWidth',5).attr('markerHeight',5)
      .attr('orient','auto').append('path').attr('d','M0,-5L10,0L0,5').attr('fill','#888');

    // Background grid
    const gGrid = svg.append('g').attr('class','grid');
    for (let x = 0; x < W; x += 80) gGrid.append('line').attr('x1',x).attr('y1',0).attr('x2',x).attr('y2',H)
      .attr('stroke','rgba(255,255,255,0.02)').attr('stroke-width',0.5);
    for (let y = 0; y < H; y += 80) gGrid.append('line').attr('x1',0).attr('y1',y).attr('x2',W).attr('y2',y)
      .attr('stroke','rgba(255,255,255,0.02)').attr('stroke-width',0.5);

    const g = svg.append('g');
    state.zoom = d3.zoom().scaleExtent([0.15, 5]).on('zoom', (ev) => g.attr('transform', ev.transform));
    svg.call(state.zoom);

    // Edges
    const linkG = g.append('g').attr('class','links');
    const link = linkG.selectAll('line').data(state.links).join('line')
      .attr('stroke', d => CFG.edgeColors[d.type] || '#888')
      .attr('stroke-width', d => d.confidence === 'low' ? 1 : 2)
      .attr('stroke-dasharray', d => CFG.edgeDash[d.type] || '')
      .attr('stroke-opacity', 0.55)
      .attr('marker-end', d => ['parent_child','master_apprentice','allegiance','creator_creation'].includes(d.type) ? 'url(#arrow)' : '');

    // Flow particles on edges
    const flowG = g.append('g').attr('class','flow-particles');
    state.links.forEach((l, i) => {
      for (let p = 0; p < CFG.flowCount; p++) {
        flowG.append('circle').attr('r', 2).attr('fill', CFG.edgeColors[l.type] || '#888')
          .attr('opacity', 0.6).attr('data-link', i).attr('data-offset', p / CFG.flowCount);
      }
    });

    // Node shapes by type
    const nodeG = g.append('g').attr('class','nodes');
    const nodeGroups = nodeG.selectAll('g.node').data(state.nodes).join('g')
      .attr('class','node').attr('cursor','pointer');

    // Shape paths
    nodeGroups.each(function(d) {
      const g = d3.select(this);
      const r = radius(d);
      switch(d.type) {
        case 'faction': g.append('polygon').attr('points', hexPoints(r)).attr('fill', CFG.nodeColors[d.type]).attr('stroke','#fff').attr('stroke-width',2); break;
        case 'location': g.append('rect').attr('x',-r).attr('y',-r).attr('width',r*2).attr('height',r*2).attr('rx',3).attr('fill', CFG.nodeColors[d.type]).attr('stroke','#fff').attr('stroke-width',2); break;
        default: g.append('circle').attr('r',r).attr('fill', CFG.nodeColors[d.type]).attr('stroke','#fff').attr('stroke-width',2); break;
      }
      // Initial letter
      const initial = (d.name || '?')[0];
      g.append('text').text(initial).attr('text-anchor','middle').attr('dy','0.35em')
        .attr('fill','#fff').attr('font-size', Math.min(r*1.1, 14)).attr('font-weight','700')
        .attr('pointer-events','none');
    });

    // Labels
    const lblG = g.append('g').attr('class','labels');
    lblG.selectAll('text').data(state.nodes).join('text')
      .text(d => d.name.length > 14 ? d.name.slice(0,12)+'…' : d.name)
      .attr('font-size',9).attr('fill','currentColor').attr('text-anchor','middle')
      .attr('dy', d => -radius(d) - 6).attr('pointer-events','none');

    // Simulation
    state.sim = d3.forceSimulation(state.nodes)
      .force('link', d3.forceLink(state.links).id(d => d.id).distance(CFG.linkDistance).strength(CFG.linkStrength))
      .force('charge', d3.forceManyBody().strength(CFG.forceStrength))
      .force('center', d3.forceCenter(W/2, H/2))
      .force('collision', d3.forceCollide().radius(d => radius(d) + 4))
      .alphaDecay(CFG.alphaDecay)
      .on('tick', () => {
        link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        nodeGroups.attr('transform', d => `translate(${d.x},${d.y})`);
        lblG.selectAll('text').attr('x', d => d.x).attr('y', d => d.y);
        // Flow particles
        flowG.selectAll('circle').each(function() {
          const li = +this.dataset.link, off = +this.dataset.offset;
          const l = state.links[li];
          if (!l || !l.source.x) return;
          const phase = (Date.now() / (CFG.flowSpeed * 100) + off) % 1;
          const x = l.source.x + (l.target.x - l.source.x) * phase;
          const y = l.source.y + (l.target.y - l.source.y) * phase;
          d3.select(this).attr('cx', x).attr('cy', y);
        });
      });

    // Drag with elastic feel
    nodeGroups.call(d3.drag()
      .on('start', (ev, d) => { if (!ev.active) state.sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (ev, d) => { d.fx = ev.x; d.fy = ev.y; })
      .on('end', (ev, d) => { if (!ev.active) state.sim.alphaTarget(0); d.fx = null; d.fy = null; }));

    // Hover
    nodeGroups.on('mouseenter', (ev, d) => {
      const connected = new Set(); connected.add(d.id);
      state.links.forEach(l => {
        const sid = typeof l.source === 'object' ? l.source.id : state.nodes[l.source]?.id;
        const tid = typeof l.target === 'object' ? l.target.id : state.nodes[l.target]?.id;
        if (sid === d.id) connected.add(tid); if (tid === d.id) connected.add(sid);
      });
      nodeGroups.selectAll('*').transition().duration(200)
        .attr('opacity', n => connected.has(n.id) ? 1 : CFG.hoverDim);
      link.transition().duration(200).attr('stroke-opacity', l => {
        const sid = typeof l.source === 'object' ? l.source.id : state.nodes[l.source]?.id;
        const tid = typeof l.target === 'object' ? l.target.id : state.nodes[l.target]?.id;
        return (sid === d.id || tid === d.id) ? 1 : CFG.hoverDim;
      });
      nodeGroups.filter(n => n.id === d.id).select('circle,rect,polygon')
        .transition().duration(200).attr('filter','url(#glow)');
      showTooltip(ev, d, connected);
    });
    nodeGroups.on('mousemove', (ev) => {
      if (!dom.tooltip || dom.tooltip.style.display === 'none') return;
      dom.tooltip.style.left = `${ev.clientX + 15}px`; dom.tooltip.style.top = `${ev.clientY - 12}px`;
    });
    nodeGroups.on('mouseleave', () => {
      nodeGroups.selectAll('*').transition().duration(200).attr('opacity', 1);
      link.transition().duration(200).attr('stroke-opacity', 0.55);
      nodeGroups.selectAll('circle,rect,polygon').attr('filter', null);
      hideTooltip();
    });

    // Double-click → focus lock
    nodeGroups.on('dblclick', (ev, d) => {
      ev.stopPropagation();
      if (state.focusedNode === d.id) { resetFocus(W, H); return; }
      state.focusedNode = d.id;
      const scale = 2.5;
      svg.transition().duration(CFG.focusDuration).call(
        state.zoom.transform, d3.zoomIdentity.translate(W/2 - d.x*scale, H/2 - d.y*scale).scale(scale));
    });
    svg.on('click', () => { if (state.focusedNode) resetFocus(W, H); });
  }

  function radius(d) { return Math.min(CFG.nodeRMax, Math.max(CFG.nodeRMin, CFG.nodeRMin + (d.mentionCount/15)*(CFG.nodeRMax-CFG.nodeRMin))); }
  function hexPoints(r) {
    const pts = []; for (let i=0;i<6;i++) { const a=Math.PI/3*i-Math.PI/6; pts.push(`${Math.cos(a)*r},${Math.sin(a)*r}`); }
    return pts.join(' ');
  }

  function showTooltip(ev, d, connected) {
    if (!dom.tooltip) return;
    const conns = state.links.filter(l => {
      const sid = typeof l.source === 'object' ? l.source.id : state.nodes[l.source]?.id;
      const tid = typeof l.target === 'object' ? l.target.id : state.nodes[l.target]?.id;
      return sid === d.id || tid === d.id;
    });
    const relList = conns.slice(0,4).map(l => {
      const otherId = (typeof l.source==='object'?l.source.id:state.nodes[l.source]?.id)===d.id
        ? (typeof l.target==='object'?l.target.id:state.nodes[l.target]?.id)
        : (typeof l.source==='object'?l.source.id:state.nodes[l.source]?.id);
      const other = state.nodes.find(n=>n.id===otherId);
      return `<div>→ ${escHtml(other?.name||'?')} <em>(${l.type})</em></div>`;
    }).join('');
    dom.tooltip.innerHTML = `<div class="tooltip-name">${escHtml(d.name)}</div><div class="tooltip-type">${d.type} · ${d.mentionCount} mentions</div>${relList}`;
    dom.tooltip.style.display = 'block';
    dom.tooltip.style.left = `${ev.clientX+15}px`; dom.tooltip.style.top = `${ev.clientY-12}px`;
  }
  function hideTooltip() { if (dom.tooltip) dom.tooltip.style.display = 'none'; }
  function resetFocus(W, H) {
    state.focusedNode = null;
    state.svgSel?.transition().duration(CFG.focusDuration).call(state.zoom?.transform, d3.zoomIdentity);
  }

  function buildLegend() {
    if (!dom.legend) return;
    let h = '';
    for (const [t,c] of Object.entries(CFG.nodeColors)) {
      h += `<div class="legend-item" data-legend-type="${t}" data-legend-cat="node"><span class="legend-color" style="background:${c}"></span>${t}</div>`;
    }
    h += '<div style="width:100%;height:1px;background:rgba(255,255,255,0.06);margin:4px 0"></div>';
    for (const [t,c] of Object.entries(CFG.edgeColors).slice(0,7)) {
      h += `<div class="legend-item" data-legend-type="${t}" data-legend-cat="edge"><span style="display:inline-block;width:18px;height:2px;background:${c};vertical-align:middle;margin-right:4px"></span>${t.replace(/_/g,' ')}</div>`;
    }
    dom.legend.innerHTML = h;

    // Click to filter
    dom.legend.querySelectorAll('.legend-item').forEach(item => {
      item.addEventListener('click', () => {
        const t = item.dataset.legendType;
        item.classList.toggle('dimmed');
        if (item.classList.contains('dimmed')) state.hiddenTypes.add(t);
        else state.hiddenTypes.delete(t);
        applyLegendFilter();
      });
    });
  }

  function applyLegendFilter() {
    const svg = d3.select('#graph-svg');
    svg.selectAll('.node').style('display', d => state.hiddenTypes.has(d.type) ? 'none' : '');
    svg.selectAll('.links line').style('display', l => state.hiddenTypes.has(l.type) ? 'none' : '');
  }

  function bindControls() {
    dom.resetBtn?.addEventListener('click', () => resetFocus(dom.container.clientWidth, dom.container.clientHeight));
    dom.timeSlice?.addEventListener('change', (e) => {
      state.timeSlice = e.target.value;
      // Re-render with same data (time-slice filtering would go here when timeline data is linked)
    });
  }

  function showFallback(wd) {
    if (!dom.container) return;
    const em = {}; (wd?.entities||[]).forEach(e=>{em[e.id]=e;});
    let h = '<div style="padding:2rem;text-align:center;"><p style="color:var(--nv-color-text-muted)">⚠ D3.js not loaded — static list.</p><div style="display:flex;flex-wrap:wrap;gap:0.75rem;justify-content:center;margin-top:1rem">';
    (wd?.relationships||[]).slice(0,20).forEach(r=>{
      const s=em[r.source]||{name:r.source}, t=em[r.target]||{name:r.target};
      h+=`<div style="padding:0.5rem 1rem;border:1px solid var(--nv-color-border);border-radius:8px;font-size:0.85rem"><strong>${escHtml(s.name)}</strong> →${r.relation_type}→ <strong>${escHtml(t.name)}</strong></div>`;
    });
    h+='</div></div>'; dom.container.innerHTML = h;
  }

  function escHtml(s) { if(!s)return''; const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

  return { init };
})();
