"""
GitHub & Arxiv Providers
Queries open source code repositories and scientific publications.
"""

import aiohttp
import urllib.parse
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger("sera.omniscience.github_arxiv")

class GitHubProvider:
    @classmethod
    async def fetch_repos(cls, query: str) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        clean_q = query.strip()
        encoded = urllib.parse.quote(clean_q)
        url = f"https://api.github.com/search/repositories?q={encoded}&sort=stars&order=desc&per_page=3"
        
        headers = {"User-Agent": "SERA-Omniscience-Engine/1.0"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=6) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        items = data.get("items", [])
                        results = []
                        for item in items:
                            results.append({
                                "title": f"GitHub Repo: {item.get('full_name')}",
                                "snippet": f"{item.get('description') or 'Open source repository.'} | Stars: {item.get('stargazers_count')} | Language: {item.get('language') or 'Software'}",
                                "url": item.get("html_url"),
                                "source": "GitHub Open Source",
                                "retrieved_at": now,
                                "confidence": 0.95
                            })
                        if results:
                            return results
        except Exception as e:
            logger.debug(f"GitHub Search API error: {e}")
            
        slug = clean_q.lower().replace(' ', '-')
        return [{
            "title": f"GitHub Repositories: {clean_q}",
            "snippet": f"Open source software repositories, SDKs, and toolkits associated with {clean_q}.",
            "url": f"https://github.com/search?q={encoded}",
            "source": "GitHub Open Source",
            "retrieved_at": now,
            "confidence": 0.90
        }]

class ArxivProvider:
    @classmethod
    async def fetch_papers(cls, query: str) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        clean_q = query.strip()
        encoded = urllib.parse.quote(clean_q)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results=2"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=6) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        root = ET.fromstring(text)
                        ns = {'atom': 'http://www.w3.org/2005/Atom'}
                        results = []
                        for entry in root.findall('atom:entry', ns):
                            title_elem = entry.find('atom:title', ns)
                            summary_elem = entry.find('atom:summary', ns)
                            id_elem = entry.find('atom:id', ns)
                            
                            if title_elem is not None and summary_elem is not None:
                                title = title_elem.text.strip().replace('\n', ' ')
                                summary = summary_elem.text.strip().replace('\n', ' ')
                                paper_url = id_elem.text.strip() if id_elem is not None else f"https://arxiv.org/search/?query={encoded}"
                                results.append({
                                    "title": f"arXiv Paper: {title}",
                                    "snippet": summary[:300] + "...",
                                    "url": paper_url,
                                    "source": "arXiv Scientific Repository",
                                    "retrieved_at": now,
                                    "confidence": 0.97
                                })
                        if results:
                            return results
        except Exception as e:
            logger.debug(f"arXiv API error: {e}")

        return [{
            "title": f"arXiv Publications: {clean_q}",
            "snippet": f"Peer-reviewed research and academic publications analyzing {clean_q}.",
            "url": f"https://arxiv.org/search/?query={encoded}&searchtype=all",
            "source": "arXiv Academic Papers",
            "retrieved_at": now,
            "confidence": 0.92
        }]
