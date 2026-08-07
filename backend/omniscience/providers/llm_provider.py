"""
LLM Intelligence Provider
Uses NVIDIA / Llama 3.1 API to generate rich, accurate, real-time company dossiers
and the SEC EDGAR API for verified financial data.
"""

import aiohttp
import asyncio
import json
import os
import re
import urllib.parse
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("sera.omniscience.llm_provider")

def get_ai_credentials():
    base_url = os.getenv("AI_BASE_URL", "https://integrate.api.nvidia.com/v1")
    api_key  = os.getenv("AI_API_KEY", "")
    model    = os.getenv("AI_MODEL", "meta/llama-3.1-8b-instruct")
    github_token = os.getenv("GITHUB_TOKEN", "")
    return base_url, api_key, model, github_token


class LLMEntityProvider:
    """
    Uses the NVIDIA-hosted LLM to generate a rich, factual entity intelligence briefing.
    Falls back gracefully if the API is unavailable.
    """

    @classmethod
    async def fetch_entity_intelligence(cls, entity: str) -> Dict[str, Any]:
        """Ask the LLM to return structured company/entity data as JSON with full global presence."""
        now = datetime.now(timezone.utc).isoformat()
        ai_base, ai_key, ai_model, _ = get_ai_credentials()

        prompt = (
            f"You are an expert global enterprise intelligence analyst. "
            f"Provide an accurate, high-fidelity, global JSON profile for: '{entity}'.\n\n"
            f"IMPORTANT REQUIREMENTS:\n"
            f"1. CEO: Provide the exact, official global CEO (e.g. Nitin Rakesh for Mphasis, Tim Cook for Apple, Jensen Huang for NVIDIA, Satya Nadella for Microsoft).\n"
            f"2. HEADQUARTERS & GLOBAL FOOTPRINT: List ALL major global headquarters and primary country presences (e.g. 'Bengaluru, India & New York, USA' for Mphasis, 'Cupertino, California, USA' for Apple).\n"
            f"3. FOUNDERS & HISTORY: List true founders (e.g. Jerry Rao & Jeroen Tas for Mphasis, Steve Jobs & Steve Wozniak for Apple) and founding year (1998 for Mphasis, 1976 for Apple).\n"
            f"4. FINANCIALS & PARENT: List accurate revenue, market cap, and primary parent/investor (e.g. Blackstone Group for Mphasis).\n\n"
            f"Return ONLY valid JSON with these exact keys:\n"
            f"{{\n"
            f'  "entity_name": "official name",\n'
            f'  "entity_type": "COMPANY | PERSON | TECHNOLOGY | COUNTRY | CONCEPT",\n'
            f'  "description": "2-3 sentence factual overview of what this entity is and its global presence",\n'
            f'  "founded_year": 1998,\n'
            f'  "founders": ["Founder Name 1", "Founder Name 2"],\n'
            f'  "ceo": "Exact Official Global CEO Name",\n'
            f'  "headquarters": "City, Country & Global Hubs (e.g. Bengaluru, India & New York, USA)",\n'
            f'  "global_locations": ["United States", "India", "United Kingdom", "Europe"],\n'
            f'  "employees": 35000,\n'
            f'  "stock_symbol": "MPHASIS / AAPL",\n'
            f'  "stock_exchange": "NSE/BSE / NASDAQ",\n'
            f'  "revenue_usd": 1600000000,\n'
            f'  "revenue_year": 2024,\n'
            f'  "market_cap_usd": 6000000000,\n'
            f'  "industry": "Information Technology & Cloud Solutions",\n'
            f'  "products": ["Cloud Migration", "Cognitive Solutions", "Digital Engineering"],\n'
            f'  "subsidiaries": ["Mphasis Corporation USA", "Silverline"],\n'
            f'  "parent_company": "Blackstone Group (Majority Owner)",\n'
            f'  "website": "https://www.mphasis.com",\n'
            f'  "timeline": [\n'
            f'    {{"year": 1998, "event": "Founded by Jerry Rao and Jeroen Tas in California & India"}},\n'
            f'    {{"year": 2006, "event": "Merged with EDS (Electronic Data Systems)"}},\n'
            f'    {{"year": 2016, "event": "Blackstone acquired majority controlling stake"}},\n'
            f'    {{"year": 2024, "event": "Expanded AI & Next-Gen Cloud Engineering globally"}}\n'
            f'  ],\n'
            f'  "key_people": [\n'
            f'    {{"name": "Nitin Rakesh", "role": "CEO & Managing Director", "since": 2017}},\n'
            f'    {{"name": "Jerry Rao", "role": "Co-Founder", "since": 1998}}\n'
            f'  ],\n'
            f'  "competitors": ["TCS", "Infosys", "Wipro", "Cognizant"],\n'
            f'  "notable_facts": ["Multinational IT service provider with major operations in US, India, UK, Europe", "Blackstone-backed enterprise IT titan"]\n'
            f"}}\n\n"
            f"Use ONLY real, verified facts. Return ONLY the JSON object, no markdown, no conversational text."
        )

        if not ai_key:
            logger.warning("[LLM-PROVIDER] No AI_API_KEY configured, skipping LLM enrichment")
            return {}

        try:
            url = f"{ai_base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {ai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": ai_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0.1
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_text = data["choices"][0]["message"]["content"].strip()
                        json_match = re.search(r'\{[\s\S]*\}', raw_text)
                        if json_match:
                            parsed = json.loads(json_match.group(0))
                            parsed["_source"] = "NVIDIA Llama 3.1 Intelligence API"
                            parsed["_retrieved_at"] = now
                            logger.info(f"[LLM-PROVIDER] Successfully fetched LLM data for '{entity}'")
                            return parsed
        except Exception as e:
            logger.warning(f"[LLM-PROVIDER] LLM fetch failed for '{entity}': {e}")

        return {}


class SECFinancialsProvider:
    """
    Fetches real, SEC-EDGAR-verified financial data: revenue, employees, CIK, SIC industry.
    """

    _ticker_cache: Dict[str, Any] = {}

    @classmethod
    async def _load_ticker_map(cls) -> Dict[str, Any]:
        if cls._ticker_cache:
            return cls._ticker_cache
        try:
            headers = {"User-Agent": "sera-intelligence-platform@test.com"}
            async with aiohttp.ClientSession(headers=headers) as sess:
                r = await sess.get(
                    "https://www.sec.gov/files/company_tickers.json",
                    timeout=aiohttp.ClientTimeout(total=12)
                )
                data = await r.json(content_type=None)
                cls._ticker_cache = {
                    v["ticker"].upper(): {"cik": str(v["cik_str"]).zfill(10), "name": v["title"]}
                    for k, v in data.items()
                }
                logger.info(f"[SEC-PROVIDER] Loaded {len(cls._ticker_cache)} SEC tickers")
        except Exception as e:
            logger.warning(f"[SEC-PROVIDER] Ticker map load failed: {e}")
        return cls._ticker_cache

    @classmethod
    async def fetch_financials(cls, entity: str, ticker_hint: str = "") -> Dict[str, Any]:
        """Try to find the entity in SEC EDGAR and pull real annual financials."""
        now = datetime.now(timezone.utc).isoformat()
        result = {"sec_verified": False}

        ticker_guesses = []
        if ticker_hint:
            ticker_guesses.append(ticker_hint.upper())
        name_clean = entity.upper().replace(" INC", "").replace(" CORP", "").replace(" LTD", "").replace(" LLC", "").replace(" PVT", "").strip()
        ticker_guesses += [
            name_clean.replace(" ", "")[:5],
            name_clean.split()[0][:5] if " " in name_clean else "",
        ]

        ticker_map = await cls._load_ticker_map()

        cik = None
        matched_name = None
        for guess in ticker_guesses:
            if guess and guess in ticker_map:
                cik = ticker_map[guess]["cik"]
                matched_name = ticker_map[guess]["name"]
                result["stock_symbol"] = guess
                break

        if not cik:
            entity_lower = entity.lower()
            for ticker, info in ticker_map.items():
                if entity_lower in info["name"].lower():
                    cik = info["cik"]
                    matched_name = info["name"]
                    result["stock_symbol"] = ticker
                    break

        if not cik:
            logger.debug(f"[SEC-PROVIDER] No SEC match found for '{entity}'")
            return result

        try:
            headers = {"User-Agent": "sera-intelligence-platform@test.com"}
            async with aiohttp.ClientSession(headers=headers) as sess:
                r = await sess.get(
                    f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                    timeout=aiohttp.ClientTimeout(total=15)
                )
                if r.status != 200:
                    return result

                facts = await r.json(content_type=None)
                us_gaap = facts.get("facts", {}).get("us-gaap", {})

                revenue_val = None
                revenue_end = None
                for rev_key in ["SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueGoodsNet"]:
                    units = us_gaap.get(rev_key, {}).get("units", {}).get("USD", [])
                    annual = sorted([x for x in units if x.get("form") == "10-K" and x.get("val")], key=lambda x: x.get("end", ""))
                    if annual:
                        latest = annual[-1]
                        revenue_val = latest["val"]
                        revenue_end = latest["end"]
                        break

                emp_val = None
                emp_end = None
                for emp_key in ["NumberOfEmployees", "EntityNumberOfEmployees"]:
                    emp_units = us_gaap.get(emp_key, {}).get("units", {}).get("pure", [])
                    annual_emp = sorted([x for x in emp_units if x.get("form") in ["10-K", "DEF 14A"] and x.get("val")], key=lambda x: x.get("end", ""))
                    if annual_emp:
                        emp_val = annual_emp[-1]["val"]
                        emp_end = annual_emp[-1]["end"]
                        break

                result.update({
                    "sec_verified": True,
                    "sec_entity_name": matched_name,
                    "sec_cik": cik,
                    "revenue_usd_sec": revenue_val,
                    "revenue_period_sec": revenue_end,
                    "employees_sec": emp_val,
                    "employees_period_sec": emp_end,
                    "sec_source_url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=10",
                    "_retrieved_at": now
                })
                logger.info(f"[SEC-PROVIDER] ✓ Fetched SEC financials for {matched_name} (CIK: {cik}): Rev={revenue_val}, Emp={emp_val}")

        except Exception as e:
            logger.warning(f"[SEC-PROVIDER] SEC facts fetch failed for CIK {cik}: {e}")

        return result


class AuthenticatedGitHubProvider:
    """
    GitHub Search with graceful fallback if token is expired or rate-limited.
    """

    @classmethod
    async def fetch_repos(cls, query: str) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        _, _, _, github_token = get_ai_credentials()
        encoded = urllib.parse.quote(query)
        url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page=5"

        headers_auth = {"User-Agent": "SERA-Omniscience-Engine/1.0"}
        if github_token:
            headers_auth["Authorization"] = f"token {github_token}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers_auth, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        items = data.get("items", [])
                        results = []
                        for item in items:
                            desc = item.get("description") or "Open source repository."
                            results.append({
                                "title": f"GitHub Repo: {item.get('full_name')}",
                                "snippet": f"{desc} | ⭐ {item.get('stargazers_count', 0):,} stars | Language: {item.get('language') or 'Software'}",
                                "url": item.get("html_url"),
                                "stars": item.get("stargazers_count", 0),
                                "source": "GitHub Open Source",
                                "retrieved_at": now,
                                "confidence": 0.95
                            })
                        if results:
                            return results
        except Exception as e:
            logger.debug(f"[GITHUB] Auth search error: {e}")

        try:
            headers_public = {"User-Agent": "SERA-Omniscience-Engine/1.0"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers_public, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        items = data.get("items", [])
                        results = []
                        for item in items:
                            desc = item.get("description") or "Open source repository."
                            results.append({
                                "title": f"GitHub Repo: {item.get('full_name')}",
                                "snippet": f"{desc} | ⭐ {item.get('stargazers_count', 0):,} stars | Language: {item.get('language') or 'Software'}",
                                "url": item.get("html_url"),
                                "stars": item.get("stargazers_count", 0),
                                "source": "GitHub Open Source",
                                "retrieved_at": now,
                                "confidence": 0.95
                            })
                        if results:
                            return results
        except Exception as e:
            logger.debug(f"[GITHUB] Unauth search error: {e}")

        return [{
            "title": f"GitHub Repositories: {query}",
            "snippet": f"Open source code, SDKs, and developer tools for {query}.",
            "url": f"https://github.com/search?q={encoded}",
            "source": "GitHub Open Source",
            "retrieved_at": now,
            "confidence": 0.88
        }]
