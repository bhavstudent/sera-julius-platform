"""
Wikipedia & Wikidata Providers
Fetches canonical summaries and REAL structured entity relationships from Wikidata API.
"""

import aiohttp
import urllib.parse
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger("sera.omniscience.wikipedia")

class WikipediaProvider:
    @classmethod
    async def fetch_summary(cls, entity: str) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        encoded = urllib.parse.quote(entity)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=8) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        title = data.get("title", entity)
                        extract = data.get("extract", "")
                        wiki_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{encoded}")
                        if extract:
                            return [{
                                "title": f"Wikipedia: {title}",
                                "snippet": extract,
                                "url": wiki_url,
                                "source": "Wikipedia",
                                "retrieved_at": now,
                                "confidence": 0.96
                            }]
        except Exception as e:
            logger.debug(f"Wikipedia REST API error: {e}")
            
        # Fallback: try search API
        try:
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded}&format=json&srlimit=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, timeout=8) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("query", {}).get("search", [])
                        if results:
                            r = results[0]
                            # Strip HTML tags from snippet
                            snippet = r.get("snippet", "")
                            import re
                            snippet = re.sub(r'<[^>]+>', '', snippet)
                            page_title = r.get("title", entity)
                            return [{
                                "title": f"Wikipedia: {page_title}",
                                "snippet": snippet,
                                "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page_title)}",
                                "source": "Wikipedia",
                                "retrieved_at": now,
                                "confidence": 0.93
                            }]
        except Exception as e:
            logger.debug(f"Wikipedia search fallback error: {e}")
        
        return []


class WikidataProvider:
    """Fetches REAL entity data from Wikidata SPARQL/search API."""

    @classmethod
    async def fetch_claims(cls, entity: str) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        results = []
        
        # Step 1: Search Wikidata for the entity ID
        entity_id = await cls._search_entity_id(entity)
        if not entity_id:
            return []
        
        # Step 2: Fetch entity data from Wikidata API
        try:
            url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        entity_data = data.get("entities", {}).get(entity_id, {})
                        claims = entity_data.get("claims", {})
                        labels = entity_data.get("labels", {})
                        entity_label = labels.get("en", {}).get("value", entity)
                        
                        # Map important property IDs to human-readable names
                        PROPERTY_MAP = {
                            "P31": "Instance Of",
                            "P17": "Country",
                            "P159": "Headquarters",
                            "P112": "Founded By",
                            "P154": "Logo",
                            "P169": "CEO",
                            "P452": "Industry",
                            "P571": "Founded",
                            "P856": "Official Website",
                            "P1128": "Employees",
                            "P414": "Stock Exchange",
                            "P1454": "Legal Form",
                            "P127": "Owned By",
                            "P355": "Subsidiary",
                            "P1056": "Product",
                            "P361": "Part Of",
                            "P737": "Influenced By",
                            "P18": "Image",
                            "P910": "Topic Main Category",
                            "P740": "Formation Location",
                            "P166": "Award Received",
                            "P2139": "Revenue",
                            "P2403": "Total Assets",
                        }
                        
                        for prop_id, prop_label in PROPERTY_MAP.items():
                            if prop_id in claims:
                                claim_list = claims[prop_id]
                                for c in claim_list[:1]:  # Take first claim per property
                                    mainsnak = c.get("mainsnak", {})
                                    datavalue = mainsnak.get("datavalue", {})
                                    value = datavalue.get("value", {})
                                    
                                    # Extract the readable value
                                    obj_text = None
                                    if isinstance(value, dict):
                                        if "id" in value:
                                            # It's a reference to another entity — resolve label later
                                            obj_text = await cls._get_entity_label(value["id"])
                                        elif "time" in value:
                                            obj_text = value["time"].lstrip("+").split("T")[0]
                                        elif "amount" in value:
                                            obj_text = value["amount"].lstrip("+")
                                        elif "text" in value:
                                            obj_text = value["text"]
                                    elif isinstance(value, str):
                                        obj_text = value
                                    
                                    if obj_text:
                                        results.append({
                                            "title": f"{entity_label} — {prop_label}: {obj_text}",
                                            "snippet": f"{entity_label} has {prop_label.lower()}: {obj_text}. (Verified from Wikidata entity {entity_id})",
                                            "url": f"https://www.wikidata.org/wiki/{entity_id}",
                                            "source": "Wikidata",
                                            "retrieved_at": now,
                                            "confidence": 0.97,
                                            "subject": entity_label,
                                            "relation": prop_label,
                                            "object": obj_text
                                        })
                                        
        except Exception as e:
            logger.debug(f"Wikidata entity data error: {e}")
        
        return results[:8]  # Limit to top 8 properties
    
    @classmethod
    async def _search_entity_id(cls, entity: str) -> str:
        """Search Wikidata for the entity's Q-ID."""
        try:
            encoded = urllib.parse.quote(entity)
            url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={encoded}&language=en&format=json&limit=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=8) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("search", [])
                        if results:
                            return results[0].get("id", "")
        except Exception as e:
            logger.debug(f"Wikidata search error: {e}")
        return ""
    
    @classmethod
    async def _get_entity_label(cls, qid: str) -> str:
        """Resolve a Wikidata Q-ID to its English label."""
        try:
            url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}&props=labels&languages=en&format=json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("entities", {}).get(qid, {}).get("labels", {}).get("en", {}).get("value", qid)
        except Exception:
            pass
        return qid
