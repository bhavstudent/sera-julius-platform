"""
Search Router for Omniscience Engine
Executes sub-tasks across specialized search providers concurrently,
including LLM-powered entity intelligence & SEC EDGAR financial queries.
"""

import asyncio
import logging
from typing import Dict, Any, List

from .providers import (
    WebSearchProvider,
    WikipediaProvider,
    WikidataProvider,
    GitHubProvider,
    ArxivProvider,
    NewsProvider,
    LLMEntityProvider,
    SECFinancialsProvider,
    AuthenticatedGitHubProvider
)

logger = logging.getLogger("sera.omniscience.router")

class SearchRouter:
    """
    Executes subtasks concurrently across targeted specialized providers.
    """
    
    @classmethod
    async def route_and_execute(cls, plan: Dict[str, Any]) -> Dict[str, Any]:
        subtasks = plan.get("subtasks", [])
        entity = plan.get("entity", "Entity")
        
        logger.info(f"[SEARCH-ROUTER] Routing subtasks for entity '{entity}'")
        
        tasks = [
            WikipediaProvider.fetch_summary(entity),
            WikidataProvider.fetch_claims(entity),
            WebSearchProvider.search(entity),
            NewsProvider.fetch_news(entity),
            AuthenticatedGitHubProvider.fetch_repos(entity),
            ArxivProvider.fetch_papers(entity),
            LLMEntityProvider.fetch_entity_intelligence(entity),
            SECFinancialsProvider.fetch_financials(entity)
        ]
        
        # Concurrently gather all responses
        results_nested = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = []
        llm_data = {}
        sec_data = {}

        for idx, res in enumerate(results_nested):
            if isinstance(res, Exception):
                logger.warning(f"[SEARCH-ROUTER] Task {idx} exception caught: {res}")
                continue
            
            if idx == 6 and isinstance(res, dict):
                llm_data = res
            elif idx == 7 and isinstance(res, dict):
                sec_data = res
            elif isinstance(res, list):
                all_results.extend(res)
                
        logger.info(f"[SEARCH-ROUTER] Successfully gathered {len(all_results)} raw results (LLM enriched: {bool(llm_data)}, SEC verified: {bool(sec_data)})")
        
        return {
            "raw_results": all_results,
            "llm_data": llm_data,
            "sec_data": sec_data
        }
