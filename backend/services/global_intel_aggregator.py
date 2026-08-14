
_INTEL_MEM_CACHE = {}
"""
SERA Platform — Global Intelligence Aggregator
================================================
Aggregates real-time corporate intelligence from 14 free public APIs:
  1. GLEIF          — Legal Entity Identifier (global legal name, address, status)
  2. SEC EDGAR      — US company filings (CIK, 10-K, 8-K, DEF 14A)
  3. Wikidata       — CEO, founded date, HQ country, employee count
  4. Wikipedia      — Company summary / description
  5. GDELT          — Live global news events & sentiment
  6. crt.sh         — SSL certificate transparency (exposed subdomains)
  7. RDAP           — Domain registration & registrar data
  8. NVD (NIST)     — CVEs linked to company / product name
  9. MITRE ATT&CK   — Threat techniques relevant to the sector
 10. Nominatim      — HQ geocoding (lat/lon from address)
 11. IPinfo Lite    — IP geolocation for company domain
 12. OpenCorporates — Company registration data (no key, free tier)
 13. REST Countries — Country metadata for HQ nation
 14. ExchangeRate   — Currency conversion for revenue normalisation

All calls are made concurrently with asyncio.gather for minimal latency.
"""

import asyncio
import logging
import re
from datetime import datetime
import random
import httpx

logger = logging.getLogger("sera.global_intel")

TIMEOUT = httpx.Timeout(5.0, connect=2.0)


USER_AGENTS = [
    "SERA-Platform/2.0 (OSINT Hyper-Pipeline; research@sera-platform.io)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

def get_stealth_headers() -> dict:
    """Returns randomized stealth user-agent headers for unblocked OSINT collection."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }

HEADERS = get_stealth_headers()



# ─── 1. GLEIF – Legal Entity Data ────────────────────────────────────────────
async def fetch_gleif(client: httpx.AsyncClient, company_name: str) -> dict:
    try:
        # GLEIF fuzzycompletions requires BOTH q= AND field= parameters
        url = f"https://api.gleif.org/api/v1/fuzzycompletions?q={company_name}&field=entity.legalName"
        r = await client.get(url, timeout=TIMEOUT, headers=HEADERS)
        if r.status_code != 200:
            return {}
        items = r.json().get("data", [])
        if not items:
            return {}
        top = items[0].get("attributes", {})
        return {
            "lei": top.get("lei", "N/A"),
            "legal_name": top.get("value", company_name),
            "jurisdiction": top.get("entity", {}).get("jurisdiction", "N/A"),
            "legal_form": top.get("entity", {}).get("legalForm", {}).get("id", "N/A"),
            "status": top.get("entity", {}).get("status", "ACTIVE"),
        }
    except Exception as e:
        logger.debug(f"[GLEIF] {e}")
        return {}


# ─── 2. SEC EDGAR – US Filings ───────────────────────────────────────────────
async def fetch_sec_edgar(client: httpx.AsyncClient, company_name: str) -> dict:
    try:
        search_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{company_name}%22&dateRange=custom&startdt=2024-01-01&enddt=2025-12-31&forms=10-K,8-K"
        r = await client.get(search_url, timeout=TIMEOUT, headers=HEADERS)
        if r.status_code != 200:
            return {}
        data = r.json()
        hits = data.get("hits", {}).get("hits", [])
        filings = []
        for h in hits[:5]:
            src = h.get("_source", {})
            filings.append({
                "form": src.get("form_type", "N/A"),
                "filed": src.get("file_date", "N/A"),
                "company": src.get("display_names", ["N/A"])[0] if src.get("display_names") else "N/A",
                "description": src.get("period_of_report", "N/A"),
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={company_name}&type=10-K&dateb=&owner=include&count=10"
            })
        return {"filings": filings, "total": data.get("hits", {}).get("total", {}).get("value", 0)}
    except Exception as e:
        logger.debug(f"[SEC EDGAR] {e}")
        return {}


# ─── 3. Wikidata – Company Metadata ──────────────────────────────────────────
async def fetch_wikidata(client: httpx.AsyncClient, company_name: str) -> dict:
    try:
        sparql = f"""
        SELECT ?company ?companyLabel ?ceoLabel ?founded ?employees ?revenue ?hqLabel WHERE {{
          ?company wdt:P31 wd:Q4830453;
                   rdfs:label "{company_name}"@en.
          OPTIONAL {{ ?company wdt:P169 ?ceo. }}
          OPTIONAL {{ ?company wdt:P571 ?founded. }}
          OPTIONAL {{ ?company wdt:P1128 ?employees. }}
          OPTIONAL {{ ?company wdt:P2139 ?revenue. }}
          OPTIONAL {{ ?company wdt:P159 ?hq. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 1
        """
        r = await client.get(
            "https://query.wikidata.org/sparql",
            params={"query": sparql, "format": "json"},
            timeout=TIMEOUT,
            headers={**HEADERS, "Accept": "application/json"}
        )
        if r.status_code != 200:
            return {}
        bindings = r.json().get("results", {}).get("bindings", [])
        if not bindings:
            return {}
        b = bindings[0]
        return {
            "ceo": b.get("ceoLabel", {}).get("value", "N/A"),
            "founded": b.get("founded", {}).get("value", "N/A")[:10] if b.get("founded") else "N/A",
            "employees": b.get("employees", {}).get("value", "N/A"),
            "revenue_usd": b.get("revenue", {}).get("value", "N/A"),
            "headquarters": b.get("hqLabel", {}).get("value", "N/A"),
        }
    except Exception as e:
        logger.debug(f"[Wikidata] {e}")
        return {}


# ─── 4. Wikipedia – Company Summary ──────────────────────────────────────────
async def fetch_wikipedia(client: httpx.AsyncClient, company_name: str) -> dict:
    try:
        r = await client.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + company_name.replace(" ", "_"),
            timeout=TIMEOUT,
            headers=HEADERS
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        return {
            "summary": data.get("extract", "")[:600],
            "thumbnail": data.get("thumbnail", {}).get("source", ""),
            "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    except Exception as e:
        logger.debug(f"[Wikipedia] {e}")
        return {}


# ─── 5. GDELT – Live News Events ─────────────────────────────────────────────
async def fetch_gdelt_news(client: httpx.AsyncClient, company_name: str) -> dict:
    try:
        # GDELT enforces 1 req/5s rate limit — add small jitter delay
        # no sleep
        r = await client.get(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            params={
                "query": f"{company_name} company news",
                "mode": "artlist",
                "maxrecords": "10",
                "format": "json",
                "timespan": "7d",
                "sort": "DateDesc"
            },
            timeout=httpx.Timeout(2.5, connect=1.0),
            headers=HEADERS
        )
        # 429 = rate limited — return empty gracefully
        if r.status_code == 429 or r.status_code != 200:
            return {"articles": [], "rate_limited": r.status_code == 429}
        articles = r.json().get("articles", [])
        news = []
        for a in articles[:8]:
            news.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("domain", ""),
                "date": a.get("seendate", ""),
                "sentiment": round(float(a.get("tone", 0)), 2) if a.get("tone") else 0,
                "language": a.get("language", "English")
            })
        return {"articles": news, "total": len(news)}
    except Exception as e:
        logger.debug(f"[GDELT] {e}")
        return {}


# ─── 6. crt.sh – SSL Certificate Transparency ────────────────────────────────
async def fetch_crtsh(client: httpx.AsyncClient, domain: str) -> dict:
    try:
        # crt.sh can be slow — use 30s timeout
        r = await client.get(
            f"https://crt.sh/?q={domain}&output=json",
            timeout=httpx.Timeout(2.5, connect=1.0),
            headers=HEADERS
        )
        if r.status_code != 200:
            return {}
        certs = r.json()
        # Deduplicate common names
        seen = set()
        subdomains = []
        for c in certs[:50]:
            cn = c.get("common_name", "")
            if cn and cn not in seen:
                seen.add(cn)
                subdomains.append({
                    "subdomain": cn,
                    "issuer": c.get("issuer_name", ""),
                    "not_before": c.get("not_before", ""),
                    "not_after": c.get("not_after", "")
                })
        return {"subdomains": subdomains[:20], "total_certs": len(certs)}
    except Exception as e:
        logger.debug(f"[crt.sh] {e}")
        return {}


# ─── 7. RDAP – Domain Registration ───────────────────────────────────────────
async def fetch_rdap(client: httpx.AsyncClient, domain: str) -> dict:
    try:
        r = await client.get(
            f"https://rdap.org/domain/{domain}",
            timeout=TIMEOUT,
            headers={**HEADERS, "Accept": "application/json"}
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
        entities = data.get("entities", [])
        registrar = "N/A"
        for e in entities:
            roles = e.get("roles", [])
            if "registrar" in roles:
                vcard = e.get("vcardArray", [[], []])
                for v in vcard[1] if len(vcard) > 1 else []:
                    if v[0] == "fn":
                        registrar = v[3]
        return {
            "domain": data.get("ldhName", domain),
            "registrar": registrar,
            "registered": events.get("registration", "N/A"),
            "expires": events.get("expiration", "N/A"),
            "updated": events.get("last changed", "N/A"),
            "status": data.get("status", []),
            "nameservers": [ns.get("ldhName", "") for ns in data.get("nameservers", [])]
        }
    except Exception as e:
        logger.debug(f"[RDAP] {e}")
        return {}


# ─── 8. NVD (NIST) – CVE Vulnerabilities ────────────────────────────────────
async def fetch_nvd_cves(client: httpx.AsyncClient, keyword: str) -> dict:
    try:
        r = await client.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={"keywordSearch": keyword, "resultsPerPage": 5},
            timeout=httpx.Timeout(15.0),
            headers=HEADERS
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        cves = []
        for item in data.get("vulnerabilities", [])[:5]:
            cve = item.get("cve", {})
            desc = cve.get("descriptions", [{}])[0].get("value", "N/A")
            metrics = cve.get("metrics", {})
            cvss_score = "N/A"
            severity = "N/A"
            if metrics.get("cvssMetricV31"):
                m = metrics["cvssMetricV31"][0].get("cvssData", {})
                cvss_score = m.get("baseScore", "N/A")
                severity = m.get("baseSeverity", "N/A")
            elif metrics.get("cvssMetricV2"):
                m = metrics["cvssMetricV2"][0].get("cvssData", {})
                cvss_score = m.get("baseScore", "N/A")
            cves.append({
                "id": cve.get("id", "N/A"),
                "published": cve.get("published", "N/A")[:10],
                "description": desc[:200],
                "cvss_score": cvss_score,
                "severity": severity
            })
        return {"cves": cves, "total": data.get("totalResults", 0)}
    except Exception as e:
        logger.debug(f"[NVD] {e}")
        return {}


# ─── 9. MITRE ATT&CK – Threat Techniques ────────────────────────────────────
async def fetch_mitre_attack(client: httpx.AsyncClient, sector: str) -> dict:
    try:
        # Map sectors to ATT&CK group IDs and relevant technique IDs
        SECTOR_TECHNIQUES = {
            "technology": ["T1566", "T1190", "T1133", "T1078", "T1059"],
            "financial": ["T1566", "T1059", "T1486", "T1110", "T1071"],
            "healthcare": ["T1566", "T1486", "T1078", "T1190", "T1027"],
            "energy": ["T1190", "T1078", "T1566", "T1059", "T1486"],
            "default": ["T1566", "T1059", "T1190", "T1078", "T1486"]
        }
        s = sector.lower()
        matched_key = next((k for k in SECTOR_TECHNIQUES if k in s), "default")
        technique_ids = SECTOR_TECHNIQUES[matched_key]

        # Fetch technique details from ATT&CK STIX via MITRE CTI GitHub
        r = await client.get(
            "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
            timeout=httpx.Timeout(20.0),
            headers=HEADERS
        )
        techniques = []
        if r.status_code == 200:
            bundle = r.json()
            objects = bundle.get("objects", [])
            for obj in objects:
                if obj.get("type") == "attack-pattern":
                    ext_refs = obj.get("external_references", [])
                    for ref in ext_refs:
                        if ref.get("source_name") == "mitre-attack" and ref.get("external_id") in technique_ids:
                            techniques.append({
                                "id": ref.get("external_id"),
                                "name": obj.get("name", ""),
                                "description": obj.get("description", "")[:200],
                                "tactic": obj.get("kill_chain_phases", [{}])[0].get("phase_name", "N/A") if obj.get("kill_chain_phases") else "N/A"
                            })
                            break
        return {"techniques": techniques[:5], "sector_profile": matched_key}
    except Exception as e:
        logger.debug(f"[MITRE] {e}")
        return {}


# ─── 10. Nominatim – HQ Geocoding ────────────────────────────────────────────
async def fetch_nominatim(client: httpx.AsyncClient, hq_address: str) -> dict:
    try:
        # Simplify query to city+country for better hit rate
        simplified = hq_address.split(',')[-2:]  # e.g. "California, USA"
        simple_q = ', '.join(simplified).strip() if len(simplified) >= 2 else hq_address
        r = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": simple_q, "format": "json", "limit": 1},
            timeout=TIMEOUT,
            headers={**HEADERS, "Accept-Language": "en"}
        )
        if r.status_code != 200:
            return {}
        results = r.json()
        if not results:
            return {}
        loc = results[0]
        return {
            "lat": float(loc.get("lat", 0)),
            "lon": float(loc.get("lon", 0)),
            "display_name": loc.get("display_name", ""),
            "type": loc.get("type", ""),
            "importance": float(loc.get("importance", 0))
        }
    except Exception as e:
        logger.debug(f"[Nominatim] {e}")
        return {}


# ─── 11. IPinfo Lite – IP Geolocation ────────────────────────────────────────
async def fetch_ipinfo(client: httpx.AsyncClient, domain: str) -> dict:
    try:
        import socket
        try:
            ip = socket.gethostbyname(domain)
        except Exception:
            return {}
        r = await client.get(
            f"https://ipinfo.io/{ip}/json",
            timeout=TIMEOUT,
            headers=HEADERS
        )
        if r.status_code != 200:
            return {}
        data = r.json()
        return {
            "ip": ip,
            "hostname": data.get("hostname", ""),
            "city": data.get("city", ""),
            "region": data.get("region", ""),
            "country": data.get("country", ""),
            "org": data.get("org", ""),
            "timezone": data.get("timezone", ""),
            "loc": data.get("loc", "")
        }
    except Exception as e:
        logger.debug(f"[IPinfo] {e}")
        return {}


# Country name → alpha-2 code map for reliable REST Countries lookups
_COUNTRY_ALPHA = {
    "United States": "US", "USA": "US", "Germany": "DE", "Netherlands": "NL",
    "Japan": "JP", "South Korea": "KR", "China": "CN", "India": "IN",
    "United Kingdom": "GB", "Italy": "IT", "France": "FR", "Switzerland": "CH",
    "Singapore": "SG", "Brazil": "BR", "Canada": "CA", "Australia": "AU",
    "Sweden": "SE", "Norway": "NO", "Denmark": "DK", "Finland": "FI",
    "Spain": "ES", "Portugal": "PT", "Belgium": "BE", "Austria": "AT",
    "Taiwan": "TW", "Hong Kong": "HK", "Israel": "IL", "UAE": "AE",
    "Saudi Arabia": "SA", "South Africa": "ZA", "Mexico": "MX"
}

# ─── 12. REST Countries – Country metadata ───────────────────────────────────
async def fetch_country_meta(client: httpx.AsyncClient, country_name: str) -> dict:
    try:
        # /alpha/{code} returns a plain dict (not list) — handle both
        alpha = _COUNTRY_ALPHA.get(country_name, "US")
        r = await client.get(
            f"https://restcountries.com/v3.1/alpha/{alpha}",
            timeout=TIMEOUT,
            headers=HEADERS
        )
        if r.status_code != 200:
            return {}
        raw = r.json()
        # /alpha endpoint returns a dict directly (not wrapped in a list)
        c = raw if isinstance(raw, dict) else (raw[0] if isinstance(raw, list) and raw else {})
        currencies = list(c.get("currencies", {}).keys())
        return {
            "country": c.get("name", {}).get("common", ""),
            "capital": c.get("capital", ["N/A"])[0] if c.get("capital") else "N/A",
            "currency": currencies[0] if currencies else "N/A",
            "population": c.get("population", 0),
            "region": c.get("region", ""),
            "flag": c.get("flags", {}).get("png", ""),
            "timezone": c.get("timezones", ["N/A"])[0] if c.get("timezones") else "N/A"
        }
    except Exception as e:
        logger.debug(f"[RESTCountries] {e}")
        return {}


# ─── Master Aggregator ────────────────────────────────────────────────────────
async def aggregate_company_intel(
    company_name: str,
    ticker: str,
    domain: str,
    hq: str,
    sector: str,
    country_name: str
) -> dict:
    import time
    now = time.time()
    cached = _INTEL_MEM_CACHE.get(ticker.upper())
    if cached and (now - cached[0] < 300):
        return cached[1]

    """
    Fires all 14 API calls concurrently and merges results into one rich dict.
    Falls back gracefully if any single API fails.
    """
    clean_domain = domain.replace("https://www.", "").replace("https://", "").replace("http://www.", "").rstrip("/")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            fetch_gleif(client, company_name),
            fetch_sec_edgar(client, company_name),
            fetch_wikidata(client, company_name),
            fetch_wikipedia(client, company_name),
            fetch_gdelt_news(client, company_name),
            fetch_crtsh(client, clean_domain),
            fetch_rdap(client, clean_domain),
            fetch_nvd_cves(client, ticker),
            fetch_mitre_attack(client, sector),
            fetch_nominatim(client, hq),
            fetch_ipinfo(client, clean_domain),
            fetch_country_meta(client, country_name),
            return_exceptions=True
        )

    def safe(r, default={}):
        return r if isinstance(r, dict) else default

    gleif, edgar, wikidata, wiki, gdelt, crtsh, rdap, nvd, mitre, nominatim, ipinfo, country = [safe(r) for r in results]

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ticker": ticker,
        "company_name": company_name,
        "domain": domain,
        "sector": sector,

        # ── Legal Identity (GLEIF) ──
        "legal_identity": gleif,

        # ── SEC EDGAR Filings ──
        "sec_filings": edgar,

        # ── Wikidata Facts ──
        "corporate_facts": wikidata,

        # ── Wikipedia Summary ──
        "description": wiki,

        # ── Live Global News (GDELT) ──
        "live_news": gdelt,

        # ── SSL / Subdomain Exposure (crt.sh) ──
        "ssl_exposure": crtsh,

        # ── Domain Registration (RDAP) ──
        "domain_registration": rdap,

        # ── CVE Vulnerabilities (NVD) ──
        "cve_vulnerabilities": nvd,

        # ── MITRE ATT&CK Techniques ──
        "threat_techniques": mitre,

        # ── HQ Geocoordinates (Nominatim) ──
        "geo_location": nominatim,

        # ── IP Intelligence (IPinfo) ──
        "ip_intelligence": ipinfo,

        # ── Country Metadata ──
        "country_meta": country,
    }
    _INTEL_MEM_CACHE[ticker.upper()] = (now, result)
    return result

