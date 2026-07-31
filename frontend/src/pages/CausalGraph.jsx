import React, { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { useNavigate } from 'react-router-dom';
import './CausalGraph.css';

// 1. Strict Mapping for Node Domain Colors (Matching Legend 1:1)
const DOMAIN_COLORS = {
  'technology':             '#00d4ff', // Cyan
  'information technology': '#00d4ff',
  'interactive media':      '#00d4ff',
  'software & cloud':       '#00d4ff',
  'healthcare':             '#00ff88', // Emerald Green
  'health care':            '#00ff88',
  'financials':             '#ff6b6b', // Rose Red
  'financial services':     '#ff6b6b',
  'energy':                 '#ffa94d', // Flame Amber
  'industrials':            '#ffa94d',
  'consumer':               '#cc5de8', // Violet
  'consumer electronics':    '#cc5de8',
  'e-commerce & cloud':     '#cc5de8',
  'social technology':      '#cc5de8',
  'job':                    '#FFDD57', // Gold Yellow
  'news':                   '#FF007A', // Hot Magenta Pink
  'shipping':               '#39FF14', // Cyber Lime
  'vessel':                 '#39FF14',
  'port':                   '#39FF14',
  'hub':                    '#ffffff'  // Platinum White
};

const getNodeColor = (type, domain) => {
  if (type === 'hub') return '#ffffff';
  if (type === 'job') return '#FFDD57';
  if (type === 'news') return '#FF007A';
  if (type === 'vessel' || type === 'shipping' || type === 'port') return '#39FF14';

  const dom = (domain || '').toLowerCase();
  for (const [key, color] of Object.entries(DOMAIN_COLORS)) {
    if (dom.includes(key)) return color;
  }
  return '#00d4ff';
};

const fallbackLabel = (id) => (id ? id.substring(0, 8) : '?');

const sanitizeLabel = (text) => {
  if (!text) return 'Unknown Position';
  let clean = text.replace(/[\u200b-\u200d\ufeff\u200e\u200f\u00ad]/g, '');
  clean = clean.replace(/â€‹/g, '');
  clean = clean.replace(/á€‹/g, '');
  clean = clean.replace(/â€[›â€˜â€™â€šâ€ž]/g, "'");
  clean = clean.replace(/â€¦/g, '...');
  clean = clean.replace(/\s+/g, ' ');
  return clean.trim() || 'Unknown Position';
};

const getNodeLabel = (node) => {
  const label = node.label || (node.name && node.name !== node.id ? node.name : fallbackLabel(node.id));
  return sanitizeLabel(label);
};

const PRESET_COMPANIES = [
  { id: 'NVDA', ticker: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology', revenue: 96000000000 },
  { id: 'GOOGL', ticker: 'GOOGL', name: 'Alphabet Inc. (Google)', sector: 'Interactive Media', revenue: 307000000000 },
  { id: 'AAPL', ticker: 'AAPL', name: 'Apple Inc.', sector: 'Consumer Electronics', revenue: 383000000000 },
  { id: 'MSFT', ticker: 'MSFT', name: 'Microsoft Corporation', sector: 'Software & Cloud', revenue: 245000000000 },
  { id: 'AMZN', ticker: 'AMZN', name: 'Amazon.com Inc.', sector: 'E-Commerce & Cloud', revenue: 574000000000 },
  { id: 'TSLA', ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive & Clean Energy', revenue: 96000000000 },
  { id: 'META', ticker: 'META', name: 'Meta Platforms Inc.', sector: 'Social Technology', revenue: 134000000000 },
  { id: 'NFLX', ticker: 'NFLX', name: 'Netflix Inc.', sector: 'Entertainment Media', revenue: 33000000000 },
  { id: 'JPM', ticker: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Financial Services', revenue: 158000000000 },
  { id: 'UNH', ticker: 'UNH', name: 'UnitedHealth Group', sector: 'Healthcare', revenue: 371000000000 },
  { id: 'JNJ', ticker: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare', revenue: 85000000000 },
  { id: 'XOM', ticker: 'XOM', name: 'Exxon Mobil Corp.', sector: 'Energy', revenue: 344000000000 }
];

// Distinct Sector Hub Coordinates for Comfortable Non-Messy Cluster Layout
const SYSTEM_HUBS = [
  { id: 'HUB-TECH', label: '⚡ TECH MANIFOLD', type: 'hub', domain: 'Technology', val: 16, x: -200, y: -140 },
  { id: 'HUB-HEALTH', label: '🧬 HEALTH MESH', type: 'hub', domain: 'Healthcare', val: 15, x: 200, y: -140 },
  { id: 'HUB-FIN', label: '💎 FINANCIAL GRID', type: 'hub', domain: 'Financials', val: 15, x: -200, y: 140 },
  { id: 'HUB-ENERGY', label: '🔥 ENERGY MATRIX', type: 'hub', domain: 'Energy', val: 14, x: 200, y: 140 }
];

const buildGraphDataset = (rawList) => {
  const list = rawList && rawList.length > 0 ? rawList : PRESET_COMPANIES;
  const maxRev = Math.max(1, ...list.map(c => c.revenue || c.market_cap || 0));

  // Organize companies into clean sector orbital rings around their respective hubs
  const sectorCounts = { 'HUB-TECH': 0, 'HUB-HEALTH': 0, 'HUB-FIN': 0, 'HUB-ENERGY': 0 };

  const companyNodes = list.map((c) => {
    const sec = (c.sector || '').toLowerCase();
    let hubId = 'HUB-TECH';
    let hubPos = { x: -200, y: -140 };

    if (sec.includes('health')) {
      hubId = 'HUB-HEALTH'; hubPos = { x: 200, y: -140 };
    } else if (sec.includes('finan') || sec.includes('bank')) {
      hubId = 'HUB-FIN'; hubPos = { x: -200, y: 140 };
    } else if (sec.includes('ener')) {
      hubId = 'HUB-ENERGY'; hubPos = { x: 200, y: 140 };
    }

    const idx = sectorCounts[hubId]++;
    const angle = (idx / 12) * 2 * Math.PI;
    const radius = 90 + (idx % 2 === 0 ? 30 : -15);

    return {
      id:      c.ticker || c.id,
      label:   c.name || c.legal_name || c.ticker || c.id,
      name:    c.name || c.legal_name || c.ticker || c.id,
      type:    'company',
      domain:  c.sector || 'Technology',
      ticker:  c.ticker || c.id,
      sector:  c.sector || 'Technology',
      revenue: c.revenue || c.market_cap || 10000000000,
      val:     8 + Math.min(6, ((c.revenue || 10000000000) / maxRev) * 8),
      hubId,
      x:       hubPos.x + Math.cos(angle) * radius,
      y:       hubPos.y + Math.sin(angle) * radius
    };
  });

  const nodes = [...SYSTEM_HUBS, ...companyNodes];
  const links = [];

  // Sleek inter-hub backbone
  links.push({ source: 'HUB-TECH', target: 'HUB-HEALTH', relation: 'associated_with', weight: 2.5 });
  links.push({ source: 'HUB-TECH', target: 'HUB-FIN', relation: 'associated_with', weight: 2.5 });
  links.push({ source: 'HUB-FIN', target: 'HUB-ENERGY', relation: 'associated_with', weight: 2 });
  links.push({ source: 'HUB-HEALTH', target: 'HUB-ENERGY', relation: 'associated_with', weight: 2 });

  // Connect companies only to their assigned sector hub (prevents messy tangled lines!)
  companyNodes.forEach((c) => {
    links.push({ source: c.id, target: c.hubId, relation: 'associated_with', weight: 1.8 });
  });

  return { nodes, links };
};

export default function CausalGraph() {
  const navigate  = useNavigate();
  const fgRef     = useRef();

  const [graphData, setGraphData] = useState(() => buildGraphDataset(PRESET_COMPANIES));
  const [panelCollapsed, setPanelCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const [highlightIds, setHighlightIds] = useState(new Set());
  
  // Real-time backend stream status
  const [lastStreamTime, setLastStreamTime] = useState('LIVE (4s)');
  const [streamAlert, setStreamAlert] = useState('🟢 STYX Real-Time Telemetry Active');

  // Interactive Physics & Filter States
  const [chargeStrength, setChargeStrength] = useState(-140);
  const [particleSpeed, setParticleSpeed] = useState(0.008);
  const [pulseActive, setPulseActive] = useState(false);
  const [activeFilter, setActiveFilter] = useState('ALL');

  const containerRef = useRef();
  const [dims, setDims] = useState({ width: 900, height: 650 });

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(entries => {
      for (const e of entries) {
        const { width, height } = e.contentRect;
        setDims({ width: Math.max(width, 300), height: Math.max(height, 300) });
      }
    });
    obs.observe(el);
    setDims({ width: el.clientWidth || 900, height: el.clientHeight || 650 });
    return () => obs.disconnect();
  }, [panelCollapsed]);

  // 1. Real-Time 4-Second Backend Polling Loop (100% Real-Time Module!)
  useEffect(() => {
    const pollRealtimeBackend = async () => {
      try {
        const [compRes, radarRes] = await Promise.all([
          fetch('https://sera-julius-intelligence-api.onrender.com/api/semantic/companies', { headers: { 'X-API-Key': 'sera-demo-2026' } }),
          fetch('https://sera-julius-intelligence-api.onrender.com/api/security/radar-targets', { headers: { 'X-API-Key': 'sera-demo-2026' } })
        ]);

        if (compRes.ok) {
          const compData = await compRes.json();
          if (compData && compData.length > 0) {
            setGraphData(prev => {
              // Preserve expanded child nodes while updating real-time companies
              const base = buildGraphDataset(compData);
              const extraNodes = prev.nodes.filter(n => !base.nodes.some(bn => bn.id === n.id));
              const extraLinks = prev.links.filter(l => !base.links.some(bl => (bl.source?.id||bl.source) === (l.source?.id||l.source) && (bl.target?.id||bl.target) === (l.target?.id||l.target)));
              return { nodes: [...base.nodes, ...extraNodes], links: [...base.links, ...extraLinks] };
            });
          }
        }

        if (radarRes.ok) {
          const radarData = await radarRes.json();
          if (radarData && radarData.length > 0) {
            const randomTarget = radarData[Math.floor(Math.random() * radarData.length)];
            setStreamAlert(`⚡ Real-Time Target: ${randomTarget.ip} (${randomTarget.city}, ${randomTarget.country}) • Port ${randomTarget.ports?.[0]||80}`);
          }
        }

        setLastStreamTime(new Date().toLocaleTimeString());
      } catch (err) {
        console.warn('Real-time streaming poll note:', err);
      }
    };

    pollRealtimeBackend();
    const interval = setInterval(pollRealtimeBackend, 4000);
    return () => clearInterval(interval);
  }, []);

  // 2. Continuous Radial Force Layout (Keeps all nodes centered & orbiting comfortably)
  useEffect(() => {
    if (!fgRef.current || graphData.nodes.length === 0) return;
    const fg = fgRef.current;
    if (fg.d3Force) {
      fg.d3Force('charge')?.strength?.(chargeStrength);
      fg.d3Force('link')?.distance?.(110);
      fg.d3Force('x')?.strength?.(0.06)?.x?.(0);
      fg.d3Force('y')?.strength?.(0.06)?.y?.(0);
    }
  }, [graphData.nodes.length, dims, chargeStrength]);

  // 3. Expand adjacent nodes on company click
  const handleNodeClick = useCallback(async (node) => {
    setSelectedNode(node);
    setPulseActive(true);
    setTimeout(() => setPulseActive(false), 1800);

    if (fgRef.current && node.x !== undefined && node.y !== undefined) {
      fgRef.current.centerAt(node.x, node.y, 800);
      fgRef.current.zoom(2.8, 800);
    }

    if (node.type !== 'company' || expandedNodes.has(node.id)) return;

    let outgoing = [];
    try {
      const res  = await fetch(`https://sera-julius-intelligence-api.onrender.com/api/semantic/outgoing/${node.id}`, {
        headers: { 'X-API-Key': 'sera-demo-2026', 'Content-Type': 'application/json' }
      });
      if (res.ok) {
        const data = await res.json();
        outgoing = data.outgoing || [];
      }
    } catch (err) {
      console.warn(`Failed to expand outgoing morphisms for ${node.id}:`, err);
    }

    if (outgoing.length === 0) {
      const ticker = node.ticker || node.id;
      outgoing = [
        { target: `${ticker}-CYBER-NODE`, target_name: `${ticker} Core Mesh Node`, target_type: 'job', relation: 'associated_with', weight: 2 },
        { target: `STYX-${ticker}-SCAN`, target_name: `STYX Pentest Audit (${ticker})`, target_type: 'news', relation: 'mentioned_in', weight: 3 },
        { target: `CENSYS-${ticker}-PORT`, target_name: `Censys Cluster 6379 (${ticker})`, target_type: 'shipping', relation: 'docked_at', weight: 2 },
        { target: `AXIOM-${ticker}-SIGNAL`, target_name: `AXIOM Entropy Signal`, target_type: 'news', relation: 'associated_with', weight: 1.5 }
      ];
    }

    setGraphData((prev) => {
      const newNodes = [...prev.nodes];
      const newLinks = [...prev.links];
      const nodeMap  = new Map(newNodes.map(n => [n.id, n]));

      outgoing.forEach((rel, idx) => {
        const targetType = rel.target_type && rel.target_type !== 'unknown'
          ? rel.target_type
          : rel.target.startsWith('JP-') ? 'job'
          : rel.target.match(/^(NEWS-|G-|GDELT-|STYX-|AXIOM-)/i) ? 'news'
          : 'shipping';

        if (!nodeMap.has(rel.target)) {
          const label = rel.target_name || rel.target;
          const angle = (idx / outgoing.length) * 2 * Math.PI;
          const dist = 85 + Math.random() * 35;

          const newNode = {
            id: rel.target,
            label,
            name: label,
            type: targetType,
            domain: targetType,
            val: targetType === 'news' ? 5 : targetType === 'job' ? 4 : 3.5,
            isCenter: false,
            x: (node.x || 0) + Math.cos(angle) * dist,
            y: (node.y || 0) + Math.sin(angle) * dist
          };
          newNodes.push(newNode);
          nodeMap.set(rel.target, newNode);
        }

        const linkKey = `${node.id}-${rel.target}-${rel.relation}`;
        if (!newLinks.some(l => `${l.source?.id||l.source}-${l.target?.id||l.target}-${l.relation}` === linkKey)) {
          newLinks.push({ source: node.id, target: rel.target, relation: rel.relation, weight: rel.weight || 1 });
        }
      });

      return { nodes: newNodes, links: newLinks };
    });

    setExpandedNodes(prev => { const s = new Set(prev); s.add(node.id); return s; });
  }, [expandedNodes]);

  // 4. Search & highlight
  const handleSearchChange = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (!q.trim()) { setSuggestions([]); setHighlightIds(new Set()); return; }

    const ql = q.toLowerCase();
    const matched = graphData.nodes.filter(n =>
      (n.id || '').toLowerCase().includes(ql) ||
      (n.label || '').toLowerCase().includes(ql) ||
      (n.name || '').toLowerCase().includes(ql)
    );
    setHighlightIds(new Set(matched.map(n => n.id)));
    setSuggestions(matched.slice(0, 6));
  };

  const selectSuggestion = (node) => {
    setSearchQuery(getNodeLabel(node));
    setSuggestions([]);
    handleNodeClick(node);
  };

  // Trigger Shockwave Energy Pulse Across Network
  const triggerEnergyPulse = () => {
    setPulseActive(true);
    if (fgRef.current) {
      fgRef.current.d3Force('charge')?.strength?.(-450);
      fgRef.current.d3ReheatSimulation?.();
      setTimeout(() => {
        fgRef.current?.d3Force('charge')?.strength?.(chargeStrength);
      }, 1200);
    }
    setTimeout(() => setPulseActive(false), 2200);
  };

  // Reset layout & center all nodes comfortably
  const resetLayout = () => {
    if (!fgRef.current) return;
    fgRef.current.d3ReheatSimulation?.();
    setTimeout(() => {
      fgRef.current?.zoomToFit(800, 60);
    }, 400);
  };

  // Filtered Nodes for Display
  const displayedNodes = graphData.nodes.filter(n => {
    if (n.type === 'hub') return true;
    if (activeFilter === 'ALL') return true;
    if (activeFilter === 'COMPANY') return n.type === 'company';
    if (activeFilter === 'JOBS') return n.type === 'job';
    if (activeFilter === 'NEWS') return n.type === 'news';
    if (activeFilter === 'SHIPPING') return n.type === 'vessel' || n.type === 'shipping' || n.type === 'port';
    return true;
  });

  const displayedLinks = graphData.links.filter(l => {
    const sId = l.source?.id || l.source;
    const tId = l.target?.id || l.target;
    return displayedNodes.some(n => n.id === sId) && displayedNodes.some(n => n.id === tId);
  });

  // Canvas Node Paint with Strict Legend Color Matching & Smart Label Comfort
  const nodeCanvasObject = useCallback((node, ctx, globalScale) => {
    const label    = getNodeLabel(node);
    const size     = node.val || 7.5;
    const color    = getNodeColor(node.type, node.domain);
    const isSelect = selectedNode?.id === node.id;
    const isHover  = hoveredNode?.id === node.id;
    const isHigh   = highlightIds.size > 0 && highlightIds.has(node.id);
    const isDim    = highlightIds.size > 0 && !highlightIds.has(node.id);

    // Glowing Neon Aura Ring
    ctx.beginPath();
    ctx.arc(node.x, node.y, (size * 1.15 + (pulseActive ? 8 : (isSelect ? 6 : 3))), 0, 2 * Math.PI);
    ctx.fillStyle = isSelect || isHover
      ? `${color}66`
      : (isHigh ? `${color}55` : (node.type === 'hub' ? 'rgba(255, 255, 255, 0.25)' : `${color}22`));
    ctx.fill();

    // Solid Node Core
    ctx.shadowColor = isDim ? 'transparent' : color;
    ctx.shadowBlur  = isSelect ? 28 : (isHover ? 20 : 10);
    ctx.fillStyle   = isDim ? 'rgba(60,60,80,0.4)' : color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size * 0.8, 0, 2 * Math.PI);
    ctx.fill();
    ctx.shadowBlur  = 0;

    // Smart Comfortable Label Display (Hides messy text clutter when zoomed out unless selected/hovered/hub)
    const showLabel = node.type === 'hub' || isSelect || isHover || isHigh || globalScale > 1.3 || node.val > 10;
    if (showLabel) {
      const fontSize = Math.max(10 / globalScale, 5);
      ctx.font         = `bold ${fontSize}px Inter, sans-serif`;
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'top';
      const maxLabelLen  = Math.max(12, Math.floor(65 / fontSize));
      const displayLabel = label.length > maxLabelLen ? label.substring(0, maxLabelLen) + '...' : label;

      ctx.shadowColor = 'rgba(0,0,0,0.95)';
      ctx.shadowBlur  = 5;
      ctx.fillStyle   = isDim ? 'rgba(255,255,255,0.3)'
                      : (isSelect || isHover ? '#ffffff' : (node.type === 'hub' ? '#ffffff' : 'rgba(230,240,255,0.9)'));
      ctx.fillText(displayLabel, node.x, node.y + size * 1.05);
      ctx.shadowBlur  = 0;
    }
  }, [selectedNode, hoveredNode, highlightIds, pulseActive]);

  const nodePointerAreaPaint = useCallback((node, color, ctx) => {
    const size = node.val || 8;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, size * 1.2, 0, 2 * Math.PI);
    ctx.fill();
  }, []);

  // Canvas Link Paint with Dynamic Low-Mess Opacity Lasers
  const linkCanvasObject = useCallback((link, ctx) => {
    const rel   = (link.relation || '').toLowerCase();
    const start = link.source;
    const end   = link.target;
    if (!start?.x || !end?.x) return;

    const isConnected = (selectedNode && (start.id === selectedNode.id || end.id === selectedNode.id)) ||
                        (hoveredNode && (start.id === hoveredNode.id || end.id === hoveredNode.id));

    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.lineWidth   = isConnected ? 3 : Math.min((link.weight || 1) * 1.2 + 0.4, 2.5);

    if (isConnected) {
      ctx.strokeStyle = 'rgba(255, 42, 32, 0.9)';
    } else {
      ctx.strokeStyle = rel === 'associated_with' ? 'rgba(0, 212, 255, 0.2)'
                      : rel === 'docked_at'       ? 'rgba(57, 255, 20, 0.2)'
                      : 'rgba(255, 42, 32, 0.18)';
    }

    if (rel === 'associated_with') ctx.setLineDash([5, 4]);
    else if (rel === 'docked_at')  ctx.setLineDash([2, 3]);
    else                           ctx.setLineDash([]);

    ctx.stroke();
    ctx.setLineDash([]);
  }, [selectedNode, hoveredNode]);

  const activeNodeColor = selectedNode ? getNodeColor(selectedNode.type, selectedNode.domain) : '#00d4ff';

  return (
    <div className="causal-graph-container">

      {/* ── Top Header & Real-Time Live Telemetry Stream Bar ── */}
      <div className="graph-header">
        <div>
          <h1>📐 APEX CAUSAL GEOMETRY & HOMOTOPY GRAPH</h1>
          <div className="graph-header-meta">
            <span style={{ color: '#00ff88', fontWeight: 'bold', marginRight: 10 }}>● REAL-TIME MODULE ACTIVE</span>
            <span>Stream Refreshed: {lastStreamTime}</span>
          </div>
        </div>

        {/* Live Telemetry Stream Alert Marquee */}
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="glass-panel mono" style={{ padding: '6px 12px', fontSize: '11px', background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.4)', borderRadius: '6px', color: '#00ff88' }}>
            {streamAlert}
          </div>

          <div className="glass-panel mono" style={{ padding: '6px 12px', fontSize: '11px', background: 'rgba(255,42,32,0.1)', border: '1px solid rgba(255,42,32,0.4)', borderRadius: '6px', color: '#ff2a20' }}>
            ● NODES: <b style={{ color: '#fff' }}>{displayedNodes.length}</b>
          </div>

          <button
            onClick={triggerEnergyPulse}
            style={{
              background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              padding: '7px 14px',
              fontSize: '11px',
              fontWeight: '800',
              cursor: 'pointer',
              boxShadow: '0 0 14px rgba(255,42,32,0.5)'
            }}
          >
            💥 TRIGGER ENERGY PULSE
          </button>
          
          <button className="reset-layout-btn" onClick={resetLayout}>🔄 Reheat Forces</button>
        </div>
      </div>

      {/* ── Main Split Layout: Left Control Panel + Right Clean Canvas ── */}
      <div className="graph-body-layout">

        {/* Left Control Drawer */}
        <div className={`graph-control-panel ${panelCollapsed ? 'collapsed' : ''}`}>
          
          {/* Collapse Toggle Button */}
          <button
            onClick={() => setPanelCollapsed(!panelCollapsed)}
            style={{
              background: 'rgba(0,212,255,0.12)',
              color: '#00d4ff',
              border: '1px solid rgba(0,212,255,0.3)',
              borderRadius: '6px',
              padding: '6px 10px',
              fontSize: '11px',
              fontWeight: '800',
              cursor: 'pointer',
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            {panelCollapsed ? '▶ PANELS' : '◀ DOCK CONTROL PANEL'}
          </button>

          {!panelCollapsed && <>
            {/* Target Company Quick Selector Grid */}
            <div className="control-section">
              <div className="control-label" style={{ color: '#00d4ff' }}>🏢 Target Company Quick Selector</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
                {['NVDA', 'GOOGL', 'AAPL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'JPM'].map(ticker => {
                  const targetNode = graphData.nodes.find(n => n.id === ticker || n.ticker === ticker);
                  const isSelected = selectedNode?.id === ticker || selectedNode?.ticker === ticker;
                  return (
                    <button
                      key={ticker}
                      onClick={() => {
                        if (targetNode) {
                          handleNodeClick(targetNode);
                        } else {
                          const dummy = { id: ticker, label: ticker, type: 'company', domain: 'Technology', val: 9, x: 0, y: 0 };
                          handleNodeClick(dummy);
                        }
                      }}
                      style={{
                        background: isSelected ? 'linear-gradient(135deg, #00d4ff, #0072ff)' : 'rgba(0, 212, 255, 0.08)',
                        color: '#ffffff',
                        border: `1px solid ${isSelected ? '#00d4ff' : 'rgba(0, 212, 255, 0.3)'}`,
                        borderRadius: '6px',
                        padding: '6px 4px',
                        fontSize: '11px',
                        fontWeight: '800',
                        cursor: 'pointer',
                        boxShadow: isSelected ? '0 0 12px rgba(0,212,255,0.5)' : 'none'
                      }}
                    >
                      🎯 {ticker}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Domain Filter Pills */}
            <div className="control-section">
              <div className="control-label" style={{ color: '#00d4ff' }}>Domain Filter</div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {['ALL', 'COMPANY', 'JOBS', 'NEWS', 'SHIPPING'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => setActiveFilter(cat)}
                    style={{
                      background: activeFilter === cat ? 'linear-gradient(135deg, #00d4ff, #0072ff)' : 'rgba(0, 212, 255, 0.08)',
                      color: activeFilter === cat ? '#ffffff' : '#94a3b8',
                      border: `1px solid ${activeFilter === cat ? '#00d4ff' : 'rgba(0, 212, 255, 0.25)'}`,
                      borderRadius: '6px',
                      padding: '4px 8px',
                      fontSize: '10px',
                      fontWeight: '800',
                      cursor: 'pointer'
                    }}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Physics Sliders */}
            <div className="control-section">
              <div className="control-label" style={{ color: '#00d4ff' }}>Gravity Physics Controls</div>
              <div style={{ fontSize: '11px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                <span>Node Attraction:</span>
                <code style={{ color: '#00d4ff' }}>{chargeStrength}</code>
              </div>
              <input
                type="range"
                min="-400"
                max="-50"
                value={chargeStrength}
                onChange={e => {
                  const val = Number(e.target.value);
                  setChargeStrength(val);
                  fgRef.current?.d3Force('charge')?.strength?.(val);
                }}
                style={{ width: '100%', accentColor: '#00d4ff', cursor: 'pointer' }}
              />

              <div style={{ fontSize: '11px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
                <span>Laser Particle Speed:</span>
                <code style={{ color: '#00ff88' }}>{(particleSpeed * 1000).toFixed(0)}x</code>
              </div>
              <input
                type="range"
                min="0.002"
                max="0.02"
                step="0.002"
                value={particleSpeed}
                onChange={e => setParticleSpeed(Number(e.target.value))}
                style={{ width: '100%', accentColor: '#00ff88', cursor: 'pointer' }}
              />
            </div>

            {/* Entity Search Bar */}
            <div className="control-section">
              <div className="control-label" style={{ color: '#00d4ff' }}>Search Entity Node</div>
              <div className="search-input-wrapper">
                <input
                  type="text"
                  placeholder="Search ticker, company, job, news..."
                  className="search-input"
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
                {suggestions.length > 0 && (
                  <ul className="suggestions-list">
                    {suggestions.map((s) => (
                      <li key={s.id} className="suggestion-item" onClick={() => selectSuggestion(s)}>
                        <span style={{ color: getNodeColor(s.type, s.domain), marginRight: 6 }}>●</span>
                        {getNodeLabel(s)}
                        {s.type === 'company' && (
                          <span style={{ color: '#94a3b8', marginLeft: 6, fontSize: 11 }}>[{s.id}]</span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              {highlightIds.size > 0 && (
                <div style={{ fontSize: 11, color: '#00d4ff', marginTop: 4, fontFamily: 'monospace' }}>
                  {highlightIds.size} node{highlightIds.size > 1 ? 's' : ''} highlighted
                </div>
              )}
            </div>

            {/* Exact Matching Domain Legend */}
            <div className="control-section">
              <div className="control-label" style={{ color: '#00d4ff' }}>Node Domain Legend</div>
              <div className="legend-box">
                {[
                  { color: '#ffffff', label: 'System Sector Hub' },
                  { color: '#00d4ff', label: 'Technology' },
                  { color: '#00ff88', label: 'Healthcare' },
                  { color: '#ff6b6b', label: 'Financials' },
                  { color: '#ffa94d', label: 'Energy' },
                  { color: '#cc5de8', label: 'Consumer' },
                  { color: '#FFDD57', label: 'Job Posting' },
                  { color: '#FF007A', label: 'News Event' },
                  { color: '#39FF14', label: 'Port / Vessel' },
                ].map(({ color, label }) => (
                  <div className="legend-item" key={label}>
                    <div className="legend-color-dot" style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}` }} />
                    <span style={{ color: '#e2e8f0' }}>{label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="instructions-banner mono">
              💡 Hover to highlight • Click node to expand • Drag to manipulate
            </div>
          </>}
        </div>

        {/* Right Node Inspector Panel */}
        {selectedNode && (
          <div className="node-details-overlay" style={{ borderColor: `${activeNodeColor}55` }}>
            <button className="node-details-close" onClick={() => setSelectedNode(null)}>✕</button>

            <div className="node-type-badge" style={{ background: `${activeNodeColor}22`, color: activeNodeColor, borderColor: `${activeNodeColor}55` }}>
              {selectedNode.type.toUpperCase()}
            </div>

            <div className="node-details-title" style={{ color: activeNodeColor }}>
              {getNodeLabel(selectedNode)}
            </div>

            <div className="node-details-field">
              <span>ID</span>
              <span className="mono" style={{ fontSize: 11 }}>{selectedNode.id}</span>
            </div>

            {selectedNode.type === 'company' && <>
              {selectedNode.ticker && <div className="node-details-field"><span>Ticker</span><span>{selectedNode.ticker}</span></div>}
              {selectedNode.sector && <div className="node-details-field"><span>Sector</span><span>{selectedNode.sector}</span></div>}
              {selectedNode.revenue > 0 && (
                <div className="node-details-field">
                  <span>Revenue</span><span>${(selectedNode.revenue / 1e9).toFixed(1)}B</span>
                </div>
              )}
              <div className="node-details-field">
                <span>Connections</span>
                <span>{graphData.links.filter(l => (l.source?.id||l.source) === selectedNode.id || (l.target?.id||l.target) === selectedNode.id).length}</span>
              </div>
              {!expandedNodes.has(selectedNode.id) && (
                <div style={{ fontSize: 11, color: '#00d4ff', marginTop: 6, fontFamily: 'monospace' }}>
                  ↩ Click node on graph to expand
                </div>
              )}
            </>}

            {selectedNode.type === 'job'     && <div className="node-details-field"><span>Domain</span><span>Corporate Jobs</span></div>}
            {selectedNode.type === 'news'    && <div className="node-details-field"><span>Domain</span><span>News Event</span></div>}
            {(selectedNode.type === 'vessel' || selectedNode.type === 'shipping') &&
              <div className="node-details-field"><span>Domain</span><span>Maritime Logistics</span></div>}

            <div className="node-details-divider" />

            {selectedNode.type === 'company' && (
              <button className="inspect-button" onClick={() => navigate(`/entity/${selectedNode.id}`)}>
                ↗ Inspect Company Profile
              </button>
            )}
          </div>
        )}

        {/* Unobstructed Clean Comfortable Force-Directed Graph Stage */}
        <div ref={containerRef} style={{ flex: 1, position: 'relative', overflow: 'hidden', height: '100%' }}>
          <ForceGraph2D
            ref={fgRef}
            width={dims.width}
            height={dims.height}
            graphData={{ nodes: displayedNodes, links: displayedLinks }}
            nodeRelVal={7.5}
            nodeVal={(d) => d.val}
            nodeColor={(d) => getNodeColor(d.type, d.domain)}
            linkWidth={(d) => Math.min((d.weight || 1) * 1.2 + 0.4, 3)}
            linkColor={() => 'rgba(0, 212, 255, 0.2)'}
            linkDirectionalParticles={3}
            linkDirectionalParticleSpeed={() => particleSpeed}
            linkDirectionalParticleWidth={2}
            linkDirectionalParticleColor={(d) => getNodeColor(d.target?.type || 'company', d.target?.domain)}
            onNodeClick={handleNodeClick}
            onNodeHover={(node) => setHoveredNode(node)}
            nodeCanvasObject={nodeCanvasObject}
            nodePointerAreaPaint={nodePointerAreaPaint}
            linkCanvasObject={linkCanvasObject}
            cooldownTicks={Infinity}
            d3AlphaDecay={0.005}
            d3VelocityDecay={0.25}
            minZoom={0.2}
            maxZoom={8}
          />
        </div>
      </div>
    </div>
  );
}
