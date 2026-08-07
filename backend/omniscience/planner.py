"""
Query Planner for Omniscience Layer
Decomposes high-level queries into targeted sub-research tasks.
Detects platform/self-referencing queries vs external entity searches.
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("sera.omniscience.planner")

# Phrases that indicate the user is asking about the SERA platform itself
PLATFORM_PHRASES = [
    "our platform", "this platform", "sera platform", "how does sera",
    "how does this", "how do you work", "how does it work", "how this works",
    "what is sera", "what is this platform", "explain sera", "about sera",
    "sera system", "sera architecture", "our system", "this system",
    "how are you working", "how you work", "your capabilities",
    "what can you do", "what do you do", "tell me about yourself",
    "how our platform", "our project", "this project",
]

class QueryPlanner:
    """
    Analyzes query intent and generates a multi-provider execution plan.
    Distinguishes between platform-self queries and external entity searches.
    """
    
    @classmethod
    def plan_query(cls, raw_query: str) -> Dict[str, Any]:
        query_clean = raw_query.strip()
        query_lower = query_clean.lower()
        
        # Check if user is asking about the platform itself
        is_platform_query = any(phrase in query_lower for phrase in PLATFORM_PHRASES)
        
        if is_platform_query:
            logger.info(f"[PLANNER] Detected platform-self query: '{raw_query}'")
            return cls._build_platform_plan(query_clean)
        
        # External entity search
        entity_name = cls._extract_entity(query_clean)
        
        subtasks = [
            {
                "id": "task_1",
                "title": f"Canonical Entity Overview ({entity_name})",
                "provider": "wikipedia",
                "query": entity_name,
                "domain": "general"
            },
            {
                "id": "task_2",
                "title": "Structured Property Claims & Relationships",
                "provider": "wikidata",
                "query": entity_name,
                "domain": "entity_graph"
            },
            {
                "id": "task_3",
                "title": "Live 2026 Web Search & News",
                "provider": "web_news",
                "query": f"{entity_name} latest news 2026",
                "domain": "news"
            },
            {
                "id": "task_4",
                "title": "Open Source Repositories & Tech Stack",
                "provider": "github",
                "query": entity_name.lower().replace(" ", "-"),
                "domain": "github"
            },
            {
                "id": "task_5",
                "title": "Scientific Publications & Research Papers",
                "provider": "arxiv",
                "query": entity_name,
                "domain": "arxiv"
            }
        ]

        logger.info(f"[PLANNER] Decomposed query '{raw_query}' into {len(subtasks)} subtasks for entity '{entity_name}'")

        return {
            "raw_query": raw_query,
            "entity": entity_name,
            "subtasks": subtasks,
            "total_subtasks": len(subtasks),
            "is_platform_query": False
        }

    @classmethod
    def _build_platform_plan(cls, query: str) -> Dict[str, Any]:
        """Returns a special plan for platform-self queries (no external search needed)."""
        return {
            "raw_query": query,
            "entity": "SERA Intelligence Platform",
            "subtasks": [],
            "total_subtasks": 0,
            "is_platform_query": True
        }

    @classmethod
    def _extract_entity(cls, text: str) -> str:
        """
        Strips conversational framing to extract the core subject entity.
        e.g. 'tell me each single details about Apple company' -> 'Apple'
        """
        cleaned = text.strip()
        
        prefixes = [
            r'^(?:can\s+you|please|kindly|i\s+want|i\s+need|tell\s+me|give\s+me|show\s+me|find|search|fetch|get|explain|analyze|describe|what\s+is|who\s+is|where\s+is|how\s+about)\s+',
            r'^(?:all|every|each|single|full|complete|detailed|latest|more|few|\s+)+\s*',
            r'^(?:and\s+every\s+)*',
            r'^(?:info|information|detail|details|detailes|fact|facts|data|news|report|overview|summary|thing|things)\s+',
            r'^(?:about|on|of|for)\s+',
        ]
        
        for _ in range(5):
            for p in prefixes:
                cleaned = re.sub(p, '', cleaned, flags=re.IGNORECASE).strip()

        cleaned = re.sub(r'\s+(?:company|firm|organization|corp\.?|corporation)$', '', cleaned, flags=re.IGNORECASE).strip()

        if not cleaned:
            return "General System Entity"
            
        return cleaned.title()
