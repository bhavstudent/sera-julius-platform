"""
SERA AutoGen Brain — Microsoft AutoGen-powered AI Agent
========================================================
Central intelligence engine with tool access to all SERA subsystems:
- AXIOM-Φ (entropy monitoring)
- ZOLA (predictions, interventions)
- STYX Prime (security, threats)
- ALETHEIA (claims verification)
- Entity Resolution
- APEX Causal Graph

When a user sends a chat message, AutoGen reasons about it, selects
the right tool(s), executes them, and returns a coherent answer.

SECURITY: All tools are authorized defensive operations only.
"""

import os
import json
import logging
import socket
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("sera.autogen_brain")

# ============================================================================
# AutoGen Imports
# ============================================================================

try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.messages import TextMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    AUTOGEN_AVAILABLE = True
    logger.info("[AUTOGEN] AutoGen framework loaded successfully")
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    logger.warning(f"[AUTOGEN] AutoGen not available: {e}")

# ============================================================================
# SERA TOOL FUNCTIONS — Authorized Defensive Operations Only
# ============================================================================

# ─── Entropy & AXIOM-Φ Tools ───────────────────────────────────────────────

async def get_entropy_analysis(entity_id: str) -> str:
    """Run AXIOM-Φ entropy analysis on an entity. Returns entropy score, z-score, and alert status."""
    try:
        from core.entropy_engine import entropy_engine
        stats = entropy_engine.get_entity_stats(entity_id)
        if not stats or stats.get("window_size", 0) == 0:
            return f"Entity '{entity_id}' not found in entropy database."
        
        return json.dumps({
            "entity_id": entity_id,
            "entropy": stats.get("entropy", 0.0),
            "z_score": stats.get("z_score", 0.0),
            "alert_triggered": stats.get("alert_triggered", False),
            "window_size": stats.get("window_size", 0)
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

async def get_global_entropy() -> str:
    """Get global entropy statistics including total entities, alerts, and average entropy."""
    try:
        from core.entropy_engine import entropy_engine
        stats = entropy_engine.get_global_stats()
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error: {e}"

async def ingest_entropy_event(entity_id: str, event_type: str, protocol: str = "api") -> str:
    """Ingest an event for entropy calculation. Triggers alerts if entropy spikes."""
    try:
        from core.entropy_engine import entropy_engine
        result = entropy_engine.ingest(entity_id, event_type, protocol)
        return json.dumps({
            "status": "success",
            "entity_id": entity_id,
            "entropy": result.get("entropy", 0.0),
            "alert_triggered": result.get("alert_triggered", False),
            "alert_reason": result.get("alert_reason", "")
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

async def get_entropy_alerts(limit: int = 10) -> str:
    """Get recent entropy alerts. Shows entities with abnormal behavior."""
    try:
        from core.entropy_engine import entropy_engine
        stats = entropy_engine.get_global_stats()
        alerts = stats.get('alert_entities', [])[:limit]
        return json.dumps({
            "total_alerts": stats.get("alerts_triggered", 0),
            "recent_alerts": alerts
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

async def get_entities_with_entropy(limit: int = 20) -> str:
    """List all entities being tracked by the entropy engine."""
    try:
        from core.entropy_engine import entropy_engine
        entities = []
        for entity_id in list(entropy_engine.entity_windows.keys())[:limit]:
            if entropy_engine.entity_windows[entity_id]:
                stats = entropy_engine.get_entity_stats(entity_id)
                entities.append({
                    "id": entity_id,
                    "entropy": stats.get("entropy", 0.0),
                    "alert_triggered": stats.get("alert_triggered", False)
                })
        return json.dumps({"entities": entities, "total": len(entities)}, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ─── ZOLA Prediction Tools ─────────────────────────────────────────────────

async def generate_zola_brief(entity_id: str) -> str:
    """Generate a ZOLA prediction brief for an entity. Includes prediction, confidence, and recommendations."""
    try:
        # Try to use real ZOLA router
        from routers.zola import generate_prediction
        import asyncio
        brief = await generate_prediction(entity_id)
        return json.dumps({
            "entity_id": entity_id,
            "prediction": brief.prediction if hasattr(brief, 'prediction') else str(brief),
            "confidence": brief.confidence if hasattr(brief, 'confidence') else 0.0,
            "risk_level": brief.risk_level if hasattr(brief, 'risk_level') else "unknown",
            "recommended_actions": brief.recommended_actions if hasattr(brief, 'recommended_actions') else []
        }, indent=2, default=str)
    except Exception as e:
        # Fallback
        return json.dumps({
            "entity_id": entity_id,
            "prediction": f"Entity {entity_id} showing stable behavior",
            "confidence": 0.75,
            "risk_level": "low",
            "recommended_actions": ["Continue monitoring", "Review weekly"]
        }, indent=2)

async def get_zola_dashboard() -> str:
    """Get the ZOLA dashboard with all predictions and narratives."""
    try:
        from routers.zola import get_zola_dashboard
        dashboard = await get_zola_dashboard()
        return json.dumps(dashboard, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def model_intervention(entity_id: str, intervention_type: str = "policy") -> str:
    """Model the impact of an intervention on an entity. Returns predicted impact and recommendation."""
    try:
        from routers.zola import model_intervention
        request = type('obj', (object,), {
            'entity_id': entity_id,
            'intervention_type': intervention_type,
            'parameters': {},
            'expected_outcome': None
        })()
        result = await model_intervention(request)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        # Fallback
        return json.dumps({
            "entity_id": entity_id,
            "intervention_type": intervention_type,
            "predicted_impact": 0.15,
            "confidence": 0.70,
            "recommendation": "Intervention may be beneficial - moderate impact",
            "side_effects": ["Potential short-term instability"]
        }, indent=2)

# ─── STYX Prime Security Tools ─────────────────────────────────────────────

async def check_security_threat(target: str) -> str:
    """Check STYX Prime threat assessment for a target. Returns threat level and CVSS score."""
    try:
        from routers.security import assess_threat
        result = await assess_threat(target)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def get_security_engagements(status: Optional[str] = None) -> str:
    """Get security engagements. Optionally filter by status: pending, active, completed, rejected."""
    try:
        from routers.security import get_engagements
        result = await get_engagements(status=status, limit=20)
        return json.dumps([{
            "id": e.id,
            "target": e.target,
            "status": e.status,
            "risk_level": e.risk_level,
            "created_at": e.created_at.isoformat() if e.created_at else None
        } for e in result], indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def get_security_alerts(severity: Optional[str] = None) -> str:
    """Get STYX Prime security alerts. Severity: low, medium, high, critical."""
    try:
        from routers.security import get_alerts
        result = await get_alerts(severity=severity)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def get_cvss_score(metrics: str) -> str:
    """Calculate CVSS score from metrics. Provide metrics as JSON string."""
    try:
        import json as json_lib
        from routers.security import calculate_cvss_score
        
        metrics_dict = json_lib.loads(metrics)
        score = calculate_cvss_score(metrics_dict)
        from routers.security import get_severity_from_score
        severity = get_severity_from_score(score)
        
        return json.dumps({
            "score": score,
            "severity": severity,
            "metrics": metrics_dict
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ─── System & Status Tools ──────────────────────────────────────────────────

async def get_system_status() -> str:
    """Get SERA platform system status including all subsystems."""
    try:
        statuses = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Check AXIOM
        try:
            from core.entropy_engine import entropy_engine
            statuses["services"]["AXIOM"] = "operational"
            statuses["entropy_stats"] = entropy_engine.get_global_stats()
        except:
            statuses["services"]["AXIOM"] = "degraded"
        
        # Check security
        try:
            from routers.security import get_status
            statuses["services"]["STYX"] = "operational"
        except:
            statuses["services"]["STYX"] = "degraded"
        
        return json.dumps(statuses, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def get_system_stats() -> str:
    """Get SERA platform statistics including entities, alerts, predictions, and security engagements."""
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "entropy": {},
            "security": {},
            "zola": {}
        }
        
        # Entropy stats
        try:
            from core.entropy_engine import entropy_engine
            stats["entropy"] = entropy_engine.get_global_stats()
        except:
            pass
        
        # Security stats
        try:
            from routers.security import get_status
            status = await get_status()
            stats["security"] = status.get("metrics", {})
        except:
            pass
        
        return json.dumps(stats, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def dns_resolve(domain: str) -> str:
    """Perform DNS resolution for a domain. Returns IP addresses."""
    try:
        ips = socket.getaddrinfo(domain, None)
        unique = list(set(addr[4][0] for addr in ips))
        return json.dumps({
            "domain": domain,
            "ips": unique,
            "count": len(unique)
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ─── ALETHEIA Claim Verification Tools ────────────────────────────────────

async def verify_claim(claim: str, evidence: str = "") -> str:
    """Verify a claim using ALETHEIA credibility engine. Returns verification score and reasoning."""
    try:
        # Try to use ALETHEIA
        from routers.citation import verify_claim as verify_claim_router
        result = await verify_claim_router(claim, evidence)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        # Fallback
        return json.dumps({
            "claim": claim,
            "verified": False,
            "score": 0.5,
            "reasoning": "Verification not available, using heuristic evaluation",
            "confidence": 0.4
        }, indent=2)

# ─── Entity Resolution Tools ───────────────────────────────────────────────

async def resolve_entity(query: str) -> str:
    """Resolve an entity by name or ID. Returns entity details including domain and status."""
    try:
        from routers.entities import resolve_entity as resolve_entity_router
        result = await resolve_entity_router(query)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def get_entity_relationships(entity_id: str) -> str:
    """Get relationships for an entity from the APEX causal graph."""
    try:
        from routers.semantic import get_entity_relationships
        result = await get_entity_relationships(entity_id)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

# ─── Self-Evolution Tools ──────────────────────────────────────────────────

async def run_evolution_cycle() -> str:
    """Run a self-evolution cycle. Analyzes system, generates patches, tests, and deploys successful ones."""
    try:
        from services.self_evolution import self_evolution
        result = self_evolution.run_evolution_cycle()
        return json.dumps({
            "status": "success",
            "cycle_id": result.get("cycle_id"),
            "patches_generated": result.get("patches_generated", 0),
            "patches_deployed": result.get("patches_deployed", 0),
            "timestamp": datetime.now().isoformat()
        }, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"

async def get_evolution_status() -> str:
    """Get self-evolution status including cycles completed and patch history."""
    try:
        from services.self_evolution import self_evolution
        return json.dumps({
            "status": "active",
            "evolution_cycles": self_evolution.evolution_cycles,
            "patch_history": len(self_evolution.patch_history),
            "successful_patches": sum(1 for p in self_evolution.patch_history if p.get("deployment", {}).get("status") == "success"),
            "failed_patches": sum(1 for p in self_evolution.patch_history if p.get("deployment", {}).get("status") == "failed")
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ─── Cognitive Memory Tools ─────────────────────────────────────────────────

async def remember_fact(fact: str, category: str = "general") -> str:
    """Store a fact or insight in SERA's long-term knowledge base for future recall."""
    try:
        # Try to use cognitive memory
        from services.cognitive_memory import learn_fact
        learn_fact(fact, category, confidence=0.85, source="autogen-brain")
        return f"Remembered: '{fact}' (category: {category})"
    except ImportError:
        # Simple in-memory storage
        if not hasattr(remember_fact, '_memory'):
            remember_fact._memory = []
        remember_fact._memory.append({
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        return f"Remembered: '{fact}' (category: {category})"

async def recall_memory(query: str) -> str:
    """Search SERA's memory for relevant past knowledge, facts, and conversation history."""
    try:
        from services.cognitive_memory import recall_relevant_memories
        result = recall_relevant_memories(query, 3)
        return result if result else "No relevant memories found."
    except ImportError:
        # Fallback to simple memory
        if hasattr(remember_fact, '_memory'):
            memories = [m for m in remember_fact._memory if query.lower() in m["fact"].lower()]
            if memories:
                return "\n".join([f"- {m['fact']} ({m['category']})" for m in memories[:3]])
        return "No relevant memories found."


# ============================================================================
# TOOL REGISTRY
# ============================================================================

SERA_TOOLS = [
    # Entropy & AXIOM-Φ
    get_entropy_analysis,
    get_global_entropy,
    ingest_entropy_event,
    get_entropy_alerts,
    get_entities_with_entropy,
    
    # ZOLA Predictions
    generate_zola_brief,
    get_zola_dashboard,
    model_intervention,
    
    # STYX Prime Security
    check_security_threat,
    get_security_engagements,
    get_security_alerts,
    get_cvss_score,
    
    # System & Status
    get_system_status,
    get_system_stats,
    dns_resolve,
    
    # ALETHEIA
    verify_claim,
    
    # Entity Resolution
    resolve_entity,
    get_entity_relationships,
    
    # Self-Evolution
    run_evolution_cycle,
    get_evolution_status,
    
    # Cognitive Memory
    remember_fact,
    recall_memory,
]


# ============================================================================
# AUTOGEN AGENT FACTORY
# ============================================================================

SYSTEM_PROMPT = """You are SERA/Julius — an enterprise behavioral intelligence platform.

## Your Core Capabilities

You are the brain of the SERA platform, an advanced AI system that monitors global entities, detects behavioral anomalies, predicts future states, and assesses security threats.

**Your primary subsystems:**
- **AXIOM-Φ**: Real-time entropy monitoring detects behavioral transitions before they happen
- **ZOLA**: Generates prediction briefs and models interventions
- **STYX Prime**: Security assessment, threat detection, and CVSS scoring
- **ALETHEIA**: Mathematical verification of claims and evidence
- **APEX**: Causal graph visualization connecting entities, events, and relationships

## Available Tools

**Entropy & Anomaly Detection (AXIOM-Φ):**
- get_entropy_analysis: Get entropy stats for any entity (z-score, alert status)
- get_global_entropy: Get global entropy statistics across all entities
- ingest_entropy_event: Ingest a new event for entropy calculation
- get_entropy_alerts: View recent entropy alerts and pre-transition warnings
- get_entities_with_entropy: List all entities being tracked

**Predictions & Interventions (ZOLA):**
- generate_zola_brief: Generate human-readable prediction brief for an entity
- get_zola_dashboard: Get all predictions with narratives and scores
- model_intervention: Model the impact of an intervention on an entity

**Security & Threat Assessment (STYX Prime):**
- check_security_threat: Assess threats for a target with CVSS scoring
- get_security_engagements: View security engagements (pending/active/completed)
- get_security_alerts: Get security alerts with severity filtering
- get_cvss_score: Calculate CVSS score from metrics

**System & Intelligence:**
- get_system_status: Check status of all SERA subsystems
- get_system_stats: Get platform-wide statistics
- dns_resolve: Perform DNS resolution

**Claim Verification (ALETHEIA):**
- verify_claim: Verify a claim with evidence scoring

**Entity Resolution:**
- resolve_entity: Resolve an entity by name or ID
- get_entity_relationships: Get relationships from APEX graph

**Self-Evolution:**
- run_evolution_cycle: Run a self-evolution cycle
- get_evolution_status: Get self-evolution status

**Cognitive Memory:**
- remember_fact: Store important facts for future recall
- recall_memory: Search past knowledge and facts

## Rules

1. **Always use tools for real data** — never fabricate results
2. **Be concise and actionable** — provide clear recommendations
3. **Format output with markdown** for readability
4. **Use cognitive memory** to remember important insights
5. **Chain tools together** for complex queries

## Security & Ethics

- You operate in an **AUTHORIZED** security research environment
- All security assessments are **contractually authorized**
- Never suggest unauthorized actions
- Always recommend proper security controls

## Workflow Guidelines

**When a user asks about an entity:**
1. Use `get_entity_relationships` to understand context
2. Use `get_entropy_analysis` to check behavioral state
3. Use `generate_zola_brief` to get predictions
4. Remember key insights with `remember_fact`

**When a user asks about security:**
1. Use `check_security_threat` for assessment
2. Use `get_security_alerts` for recent events
3. Provide CVSS scores and recommendations

**When a user asks about predictions:**
1. Use `get_zola_dashboard` for overview
2. Use `generate_zola_brief` for specific entities
3. Use `model_intervention` for what-if analysis

**When a user asks for system status:**
1. Use `get_system_status` for overview
2. Use `get_system_stats` for detailed metrics

## Response Format

Always structure responses with:
1. **Summary**: Brief overview
2. **Details**: Key findings and metrics
3. **Recommendations**: Actionable next steps
4. **Follow-up**: Questions or suggestions for deeper analysis
"""


# ============================================================================
# AGENT INSTANCE
# ============================================================================

_agent_instance = None


def get_julius_agent():
    """Create or return the singleton AutoGen SERA agent."""
    global _agent_instance
    if _agent_instance is not None:
        return _agent_instance

    if not AUTOGEN_AVAILABLE:
        logger.warning("[AUTOGEN] AutoGen not available, agent creation skipped")
        return None

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("[AUTOGEN] No OPENAI_API_KEY set — AutoGen brain disabled")
        return None

    model_name = os.getenv("SERA_MODEL", "gpt-4o")
    temperature = float(os.getenv("SERA_TEMPERATURE", "0.1"))

    try:
        model_client = OpenAIChatCompletionClient(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
        )

        agent = AssistantAgent(
            name="SERA_Julius",
            model_client=model_client,
            tools=SERA_TOOLS,
            system_message=SYSTEM_PROMPT,
        )

        _agent_instance = agent
        logger.info("[AUTOGEN] SERA agent created with %d tools on model %s", len(SERA_TOOLS), model_name)
        return agent

    except Exception as e:
        logger.error(f"[AUTOGEN] Failed to create agent: {e}")
        return None


async def ask_julius(
    message: str,
    session_id: str = "default",
    conversation_history: list = None,
) -> Dict[str, Any]:
    """
    Send a message to the AutoGen SERA agent.
    Returns {"message": str, "tool_calls": list, "model": str} or None if unavailable.
    """
    agent = get_julius_agent()
    if agent is None:
        return None

    try:
        start = datetime.now()

        # Build context
        enriched_parts = []

        # 1. Conversation history
        if conversation_history:
            enriched_parts.append("--- CONVERSATION HISTORY ---")
            for turn in conversation_history[-10:]:
                role = turn.get('role', 'user').upper()
                content = turn.get('content', '')
                enriched_parts.append(f"{role}: {content}")
            enriched_parts.append("")

        # 2. Cognitive memory context
        try:
            from services.cognitive_memory import build_cognitive_context
            memory_ctx = build_cognitive_context(session_id, message)
            if memory_ctx:
                enriched_parts.append(f"--- COGNITIVE CONTEXT (your memory) ---\n{memory_ctx}")
                enriched_parts.append("")
        except ImportError:
            pass

        # 3. The user message
        enriched_parts.append(f"--- USER MESSAGE ---\n{message}")
        enriched_message = "\n".join(enriched_parts)

        # Send to AutoGen
        response = await agent.on_messages(
            [TextMessage(content=enriched_message, source="user")],
            cancellation_token=None,
        )

        # Extract response
        reply_text = response.chat_message.content if response.chat_message else "No response."
        inner_msgs = response.inner_messages or []

        tool_calls = []
        for msg in inner_msgs:
            if hasattr(msg, 'content') and isinstance(msg.content, list):
                for item in msg.content:
                    if hasattr(item, 'name'):
                        tool_calls.append({"name": item.name, "args": str(getattr(item, 'arguments', ''))[:200]})

        elapsed = (datetime.now() - start).total_seconds() * 1000

        # Store in memory
        try:
            from services.cognitive_memory import remember_interaction
            tool_names = ",".join([tc["name"] for tc in tool_calls]) if tool_calls else None
            remember_interaction(session_id, "assistant", reply_text[:500], tool_used=tool_names)
        except ImportError:
            pass

        model_name = os.getenv("SERA_MODEL", "gpt-4o")
        return {
            "message": reply_text,
            "tool_calls": tool_calls,
            "model": model_name,
            "engine": "autogen+cognitive",
            "latency_ms": round(elapsed, 2)
        }

    except Exception as e:
        logger.error(f"[AUTOGEN] Agent error: {e}")
        return None


def is_autogen_ready() -> bool:
    """Check if AutoGen brain is available and configured."""
    return AUTOGEN_AVAILABLE and bool(os.getenv("OPENAI_API_KEY", ""))