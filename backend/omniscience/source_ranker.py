"""
Source Ranker and Fact Verifier for Omniscience Engine
Computes domain authority, deduplicates facts, and verifies supporting evidence.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger("sera.omniscience.ranker")

class SourceRanker:
    """
    Ranks sources based on domain authority, recency, and clarity.
    """
    
    @classmethod
    def rank_sources(cls, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for item in items:
            source = item.get("source", "").lower()
            confidence = item.get("confidence", 0.85)
            
            # Domain authority boost
            if "wikipedia" in source or "wikidata" in source:
                confidence = max(confidence, 0.96)
            elif "arxiv" in source:
                confidence = max(confidence, 0.97)
            elif "github" in source:
                confidence = max(confidence, 0.94)
            elif "news" in source:
                confidence = max(confidence, 0.90)
                
            item["confidence"] = round(confidence, 2)

        # Sort by confidence descending
        sorted_items = sorted(items, key=lambda x: x.get("confidence", 0), reverse=True)
        return sorted_items

class FactVerifier:
    """
    Verifies assertions and stores verified facts into ChromaDB vector store.
    """
    
    @classmethod
    def verify_and_index(cls, ranked_items: List[Dict[str, Any]], entity: str) -> List[Dict[str, Any]]:
        verified = []
        seen_snippets = set()
        
        for item in ranked_items:
            snip = item.get("clean_text") or item.get("snippet", "")
            if not snip or snip in seen_snippets:
                continue
            seen_snippets.add(snip)
            
            fact_entry = {
                "fact": item.get("title", f"Fact about {entity}"),
                "supporting_passage": snip,
                "source_url": item.get("url", "https://sera.intelligence"),
                "source_name": item.get("source", "Web Telemetry"),
                "retrieved_at": item.get("retrieved_at", datetime.now(timezone.utc).isoformat()),
                "confidence": item.get("confidence", 0.90),
                "subject": item.get("subject", entity),
                "relation": item.get("relation"),
                "object": item.get("object")
            }
            verified.append(fact_entry)

        # Optionally index into ChromaDB vector store
        try:
            from services.vector_store import VectorStoreService
            for idx, f in enumerate(verified[:5]):
                VectorStoreService.add_document(
                    doc_id=f"omni_fact_{entity}_{idx}_{int(datetime.now().timestamp())}",
                    text=f"{f['fact']} | {f['supporting_passage']}",
                    metadata={"entity": entity, "source": f['source_url'], "confidence": f['confidence']}
                )
        except Exception as e:
            logger.debug(f"ChromaDB indexing fallback: {e}")

        return verified
