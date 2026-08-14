import sys, os
sys.path.insert(0, 'backend')

modules = {
    'AXIOM Math Engine':      ('services.axiom.axiom_compressor', 'AXIOMCompressor'),
    'KRONOS Neural Engine':   ('services.kronos.kronecker_scaler', 'KroneckerScaler'),
    'Causal Functor':         ('services.causal_functor.inference', 'forward_inference'),
    'VEIL Post-Quantum':      ('services.veil', None),
    'Robin Dark Web':         ('services.robin', None),
    'Stratum Omnis':          ('services.stratum_omnis', None),
    'Intelligence Engine':    ('services.intelligence_engine', None),
    'Pantheon Policy':        ('services.pantheon', None),
    'Julius AI Core':         ('services.julius_ai', 'JuliusAI'),
    'KRONOS Service':         ('services.kronos_service', 'KronosService'),
    'Cognitive Memory':       ('services.cognitive_memory', None),
    'Person Extraction':      ('services.person_entity_extraction', None),
    'BGP/MITM Engine':        ('services.bgp_mitm', None),
    'LAN Recon':              ('services.lan_recon', None),
    'Signal Collector':       ('services.julius_signal_collector', None),
    'UK OSINT':               ('services.uk_osint_extensions', None),
}

ok, fail = 0, 0
online, offline = [], []

for name, (mod, cls) in modules.items():
    try:
        m = __import__(mod, fromlist=[cls] if cls else [])
        if cls:
            getattr(m, cls)
        online.append(name)
        ok += 1
    except Exception as e:
        offline.append((name, str(e)[:50]))
        fail += 1

dist_built = os.path.exists('frontend/dist/index.html')
panels     = len(os.listdir('frontend/src/panels')) if os.path.exists('frontend/src/panels') else 0
pages      = len(os.listdir('frontend/src/pages')) if os.path.exists('frontend/src/pages') else 0
components = len(os.listdir('frontend/src/components')) if os.path.exists('frontend/src/components') else 0
routers    = len([f for f in os.listdir('backend/routers') if f.endswith('.py') and f != '__init__.py']) if os.path.exists('backend/routers') else 0
dbs        = [f for f in os.listdir('backend/database') if f.endswith('.db')] if os.path.exists('backend/database') else []

print('')
print('=' * 58)
print('      SERA + JULIUS AI  -  FULL PLATFORM CONDITION')
print('=' * 58)
print('')
print('  BACKEND ENGINE')
print(f'    API Routers       : {routers} files active')
print(f'    SQLite Databases  : {len(dbs)} ({", ".join(dbs)})')
print('')
print('  FRONTEND')
build_status = "BUILT AND READY" if dist_built else "NOT BUILT"
print(f'    Build Status      : {build_status}')
print(f'    Pages             : {pages}')
print(f'    Panels            : {panels}')
print(f'    Components        : {components}')
print('')
print('  JULIUS AI MODULES')
for name in online:
    print(f'    [ONLINE]  {name}')
for name, err in offline:
    print(f'    [OFFLINE] {name}')
print('')
print('  SERVERS')
print('    Backend API       : http://localhost:8000')
print('    API Docs (Swagger): http://localhost:8000/docs')
print('    Frontend UI       : http://localhost:5173')
print('')
print('=' * 58)
pct = int((ok / (ok+fail)) * 100)
print(f'  MODULES ONLINE : {ok}/{ok+fail} ({pct}%)')
print(f'  MODULES OFFLINE: {fail}/{ok+fail}')
print(f'  FRONTEND BUILD : {"OK" if dist_built else "MISSING"}')
overall = "FULLY OPERATIONAL" if (pct >= 80 and dist_built) else "PARTIALLY OPERATIONAL"
print(f'  OVERALL STATUS : {overall}')
print('=' * 58)
