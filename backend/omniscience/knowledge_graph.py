"""
Knowledge Graph Builder for Omniscience Engine
Constructs relational graph nodes & edges with clean labels, confidence, and supporting passages.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone

logger = logging.getLogger("sera.omniscience.kg")

class KnowledgeGraphBuilder:
    """
    Builds property graph node-and-edge network from verified facts.
    Outputs clean, human-readable labels (not raw IDs).
    """
    
    @classmethod
    def build_graph(cls, verified_facts: List[Dict[str, Any]], root_entity: str) -> Dict[str, Any]:
        nodes = []
        edges = []
        node_ids = set()

        def add_node(node_id: str, label: str, node_type: str):
            if node_id not in node_ids:
                node_ids.add(node_id)
                nodes.append({
                    "id": node_id,
                    "label": label,
                    "type": node_type
                })

        # Add Root Entity Node
        root_id = "root"
        add_node(root_id, root_entity, "Primary Entity")

        # Process facts and add claim relationships
        for idx, fact in enumerate(verified_facts):
            rel = fact.get("relation")
            obj = fact.get("object")
            
            if rel and obj:
                # Clean the object label for display
                clean_label = obj.strip()
                obj_id = f"node_{idx}"
                add_node(obj_id, clean_label, "Property/Value")
                
                edges.append({
                    "id": f"edge_{idx}",
                    "source": root_entity,
                    "target": clean_label,
                    "relation": rel,
                    "confidence": fact.get("confidence", 0.95),
                    "source_url": fact.get("source_url"),
                    "supporting_passage": fact.get("supporting_passage")
                })
            else:
                # Extract a clean label from the fact title
                fact_title = fact.get("fact", "")
                # Remove prefixes like "Wikidata Claim:", "GitHub Repo:", etc.
                clean_label = fact_title
                for prefix in ["Wikidata Claim:", "GitHub Repo:", "arXiv Paper:", "Wikipedia:", f"{root_entity} ->"]:
                    clean_label = clean_label.replace(prefix, "").strip()
                # Truncate to reasonable length
                if len(clean_label) > 50:
                    clean_label = clean_label[:47] + "..."
                if not clean_label:
                    clean_label = f"Fact #{idx + 1}"
                    
                fact_id = f"fact_{idx}"
                add_node(fact_id, clean_label, "Fact")
                edges.append({
                    "id": f"edge_{idx}",
                    "source": root_entity,
                    "target": clean_label,
                    "relation": "Related To",
                    "confidence": fact.get("confidence", 0.90),
                    "source_url": fact.get("source_url"),
                    "supporting_passage": fact.get("supporting_passage")
                })

        logger.info(f"[KNOWLEDGE-GRAPH] Built graph for '{root_entity}' with {len(nodes)} nodes and {len(edges)} edges")

        return {
            "root_entity": root_entity,
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
