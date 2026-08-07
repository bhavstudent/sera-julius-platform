"""
SERA Workflow Engine — Orchestrates multi-step automated investigations
========================================================================
Chains AXIOM, ZOLA, STYX Prime, ALETHEIA, and Entity Resolution subsystems.

Features:
- Template-based workflow creation
- Dynamic step execution with context passing
- Background processing
- Database logging and tracking
- Error recovery and retry
"""

import logging
import json
import re
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger("sera.workflow_engine")

# ============================================================================
# WORKFLOW TEMPLATES
# ============================================================================

WORKFLOW_TEMPLATES = {
    # ─── Entity Analysis ──────────────────────────────────────────────────
    "entity_analysis": {
        "name": "Comprehensive Entity Analysis",
        "description": "Analyze an entity across all SERA subsystems",
        "steps": [
            {"service": "entity", "action": "resolve", "params": {"query": "{{input.entity}}}"}},
            {"service": "axiom", "action": "entropy", "params": {"entity": "{{input.entity}}}"}},
            {"service": "zola", "action": "predict", "params": {"entity": "{{input.entity}}}"}},
            {"service": "security", "action": "assess", "params": {"entity": "{{input.entity}}}"}},
        ]
    },
    
    # ─── Threat Response ──────────────────────────────────────────────────
    "threat_response": {
        "name": "Automated Threat Response",
        "description": "Respond to detected security threat",
        "steps": [
            {"service": "security", "action": "detect", "params": {"target": "{{input.target}}"}},
            {"service": "security", "action": "score", "params": {}},
            {"service": "zola", "action": "intervene", "params": {"entity": "{{input.target}}"}},
            {"service": "aletheia", "action": "verify", "params": {"claim": "{{input.claim}}"}},
        ]
    },
    
    # ─── Market Intelligence ─────────────────────────────────────────────
    "market_intelligence": {
        "name": "Market Intelligence Analysis",
        "description": "Analyze market signals and generate insights",
        "steps": [
            {"service": "entity", "action": "resolve", "params": {"query": "{{input.company}}"}},
            {"service": "axiom", "action": "entropy", "params": {"entity": "{{input.company}}"}},
            {"service": "zola", "action": "predict", "params": {"entity": "{{input.company}}"}},
            {"service": "zola", "action": "brief", "params": {"entity": "{{input.company}}"}},
        ]
    },
    
    # ─── Evolution Pipeline ──────────────────────────────────────────────
    "evolution_pipeline": {
        "name": "Self-Evolution Pipeline",
        "description": "Analyze → Generate → Test → Deploy evolution patches",
        "steps": [
            {"service": "evolution", "action": "analyze", "params": {}},
            {"service": "evolution", "action": "patch", "params": {}},
            {"service": "evolution", "action": "test", "params": {"patch": "{{step_1_result.patch}}"}},
            {"service": "evolution", "action": "deploy", "params": {"patch": "{{step_1_result.patch}}", "test": "{{step_2_result.test}}"}},
        ]
    },
    
    # ─── Entity Monitoring ───────────────────────────────────────────────
    "entity_monitor": {
        "name": "Entity Monitoring",
        "description": "Monitor an entity for changes and alerts",
        "steps": [
            {"service": "axiom", "action": "entropy", "params": {"entity": "{{input.entity}}"}},
            {"service": "axiom", "action": "alerts", "params": {"entity": "{{input.entity}}"}},
            {"service": "security", "action": "assess", "params": {"entity": "{{input.entity}}"}},
        ]
    },
    
    # ─── Full Platform Scan ──────────────────────────────────────────────
    "full_scan": {
        "name": "Full Platform Scan",
        "description": "Complete scan of all subsystems",
        "steps": [
            {"service": "axiom", "action": "global", "params": {}},
            {"service": "security", "action": "engagements", "params": {}},
            {"service": "security", "action": "alerts", "params": {}},
            {"service": "zola", "action": "dashboard", "params": {}},
            {"service": "evolution", "action": "status", "params": {}},
        ]
    },
}


# ============================================================================
# DATABASE HELPERS
# ============================================================================

def _db():
    """Get database instance."""
    try:
        from database import db
        return db
    except ImportError:
        # Fallback in-memory
        return None


# ============================================================================
# STEP EXECUTION
# ============================================================================

async def _execute_step(service: str, action: str, params: dict, context: dict) -> dict:
    """Execute a single workflow step by dispatching to the appropriate service."""
    logger.info(f"[WORKFLOW] Executing {service}.{action} with params {params}")
    
    # ─── AXIOM-Φ Services ──────────────────────────────────────────────────
    if service == "axiom" and action == "entropy":
        try:
            from core.entropy_engine import entropy_engine
            entity = params.get("entity", "default")
            stats = entropy_engine.get_entity_stats(entity)
            return {"status": "success", "stats": stats, "entity": entity}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "axiom" and action == "alerts":
        try:
            from core.entropy_engine import entropy_engine
            entity = params.get("entity")
            if entity:
                stats = entropy_engine.get_entity_stats(entity)
                return {"status": "success", "alerts": [stats] if stats.get("alert_triggered") else []}
            else:
                stats = entropy_engine.get_global_stats()
                return {"status": "success", "alerts": stats.get("alert_entities", [])}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "axiom" and action == "global":
        try:
            from core.entropy_engine import entropy_engine
            stats = entropy_engine.get_global_stats()
            return {"status": "success", "stats": stats}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── ZOLA Services ────────────────────────────────────────────────────
    elif service == "zola" and action == "predict":
        try:
            from routers.zola import generate_prediction
            entity = params.get("entity", "default")
            result = await generate_prediction(entity)
            return {"status": "success", "prediction": result, "entity": entity}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "zola" and action == "brief":
        try:
            from routers.zola import get_brief
            entity = params.get("entity", "default")
            result = await get_brief(entity)
            return {"status": "success", "brief": result, "entity": entity}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "zola" and action == "intervene":
        try:
            from routers.zola import model_intervention
            entity = params.get("entity", "default")
            request = type('obj', (object,), {
                'entity_id': entity,
                'intervention_type': params.get("type", "policy"),
                'parameters': {},
                'expected_outcome': None
            })()
            result = await model_intervention(request)
            return {"status": "success", "intervention": result, "entity": entity}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "zola" and action == "dashboard":
        try:
            from routers.zola import get_zola_dashboard
            result = await get_zola_dashboard()
            return {"status": "success", "dashboard": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── Security Services ────────────────────────────────────────────────
    elif service == "security" and action == "assess":
        try:
            from routers.security import assess_threat
            target = params.get("entity", params.get("target", "default"))
            result = await assess_threat(target)
            return {"status": "success", "assessment": result, "target": target}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "security" and action == "detect":
        try:
            from routers.security import detect_threats
            target = params.get("target", "default")
            result = await detect_threats(target)
            return {"status": "success", "threats": result, "target": target}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "security" and action == "score":
        try:
            from routers.security import get_cvss_details
            # Get score from context
            threats = context.get("step_0_result", {}).get("threats", [])
            score = threats[0].get("cvss_score", 5.0) if threats else 5.0
            result = await get_cvss_details(score)
            return {"status": "success", "cvss": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "security" and action == "engagements":
        try:
            from routers.security import get_engagements
            result = await get_engagements(limit=20)
            return {"status": "success", "engagements": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "security" and action == "alerts":
        try:
            from routers.security import get_alerts
            result = await get_alerts()
            return {"status": "success", "alerts": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── Entity Services ──────────────────────────────────────────────────
    elif service == "entity" and action == "resolve":
        try:
            from routers.entities import resolve_entity
            query = params.get("query", params.get("entity", "default"))
            result = await resolve_entity(query)
            return {"status": "success", "entity": result, "query": query}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── ALETHEIA Services ────────────────────────────────────────────────
    elif service == "aletheia" and action == "verify":
        try:
            from routers.citation import verify_claim
            claim = params.get("claim", "default claim")
            evidence = params.get("evidence", "")
            result = await verify_claim(claim, evidence)
            return {"status": "success", "verification": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── Evolution Services ───────────────────────────────────────────────
    elif service == "evolution" and action == "analyze":
        try:
            from services.self_evolution import self_evolution
            result = self_evolution.analyze_repository()
            return {"status": "success", "analysis": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "evolution" and action == "patch":
        try:
            from services.self_evolution import self_evolution
            analysis = context.get("step_0_result", {}).get("analysis", {})
            result = self_evolution.generate_patch(analysis)
            return {"status": "success", "patch": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "evolution" and action == "test":
        try:
            from services.self_evolution import self_evolution
            patch = params.get("patch", {})
            result = self_evolution.test_patch(patch)
            return {"status": "success", "test": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "evolution" and action == "deploy":
        try:
            from services.self_evolution import self_evolution
            patch = params.get("patch", {})
            test = params.get("test", {})
            result = self_evolution.deploy_patch(patch, test)
            return {"status": "success", "deployment": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    elif service == "evolution" and action == "status":
        try:
            from services.self_evolution import self_evolution
            result = self_evolution.review_queue()
            return {"status": "success", "status": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ─── Unknown Service ──────────────────────────────────────────────────
    else:
        return {"status": "error", "error": f"Unknown service/action: {service}/{action}"}


def _resolve_params(params: dict, context: dict) -> dict:
    """Replace template variables like {{step_0_result.scan_id}} with actual values."""
    resolved = {}
    for key, val in params.items():
        if isinstance(val, str) and "{{" in val:
            for match in re.findall(r'\{\{(.+?)\}\}', val):
                parts = match.split(".")
                value = context
                for p in parts:
                    if isinstance(value, dict):
                        value = value.get(p, "")
                    else:
                        value = ""
                        break
                val = val.replace(f"{{{{{match}}}}}", str(value))
        resolved[key] = val
    return resolved


# ============================================================================
# WORKFLOW EXECUTION
# ============================================================================

async def execute_workflow(workflow_id: int) -> Dict:
    """Execute all steps of a workflow sequentially."""
    db = _db()
    
    if db:
        workflow = db.get_workflow_with_steps(workflow_id)
        if not workflow:
            logger.error(f"[WORKFLOW] Workflow {workflow_id} not found")
            return {"status": "error", "message": f"Workflow {workflow_id} not found"}
        
        db.update_workflow_status(workflow_id, "running")
    else:
        # In-memory fallback
        workflow = {"id": workflow_id, "name": "workflow", "steps": []}
    
    context: Dict[str, Any] = {}
    steps = workflow.get("steps", [])
    
    if not steps:
        actions = workflow.get("actions", [])
        if isinstance(actions, list):
            for i, step_def in enumerate(actions):
                if isinstance(step_def, dict):
                    if db:
                        db.add_workflow_step(
                            workflow_id, i,
                            step_def.get("service", "unknown"),
                            step_def.get("action", "unknown"),
                            step_def.get("params", {}),
                        )
            if db:
                steps = db.get_workflow_steps(workflow_id)
    
    for step in steps:
        step_idx = step.get("step_index", 0)
        
        if db:
            db.update_workflow_step(workflow_id, step_idx, "running")
        
        try:
            params = _resolve_params(step.get("params", {}), context)
            result = await _execute_step(step["service"], step["action"], params, context)
            context[f"step_{step_idx}_result"] = result
            
            if db:
                db.update_workflow_step(workflow_id, step_idx, "completed", result)
                
        except Exception as e:
            logger.error(f"[WORKFLOW] Workflow {workflow_id} step {step_idx} failed: {e}")
            if db:
                db.update_workflow_step(workflow_id, step_idx, "failed", {"error": str(e)})
                db.update_workflow_status(workflow_id, "failed")
            return {"status": "error", "step": step_idx, "error": str(e)}
    
    if db:
        db.update_workflow_status(workflow_id, "completed")
        db.add_event(
            event_id=f"evt_wf_done_{uuid.uuid4().hex[:8]}",
            event_type="workflow_completed",
            source="julius-workflow-engine",
            data={"workflow_id": workflow_id, "name": workflow.get("name"), "steps": len(steps)},
        )
    
    logger.info(f"[WORKFLOW] Workflow {workflow_id} completed: {len(steps)} steps")
    return {"status": "success", "completed": True, "steps": len(steps), "context": context}


def create_from_template(template_name: str, input_params: dict) -> Optional[int]:
    """Create a workflow from a named template with input parameters."""
    template = WORKFLOW_TEMPLATES.get(template_name)
    if not template:
        logger.error(f"[WORKFLOW] Template {template_name} not found")
        return None
    
    db = _db()
    if not db:
        logger.error("[WORKFLOW] Database not available")
        return None
    
    result = db.add_workflow(
        name=f"{template['name']} - {datetime.utcnow().strftime('%H:%M')}",
        description=template["description"],
        trigger_type="template",
        actions=template["steps"],
    )
    
    workflow_id = result["id"]
    
    for i, step_def in enumerate(template["steps"]):
        params = step_def.get("params", {})
        resolved = {}
        for k, v in params.items():
            if isinstance(v, str) and "{{input." in v:
                key = v.replace("{{input.", "").replace("}}", "")
                resolved[k] = input_params.get(key, v)
            else:
                resolved[k] = v
        db.add_workflow_step(workflow_id, i, step_def["service"], step_def["action"], resolved)
    
    logger.info(f"[WORKFLOW] Created workflow {workflow_id} from template {template_name}")
    return workflow_id


# ============================================================================
# WORKFLOW STATUS
# ============================================================================

def get_workflow_status(workflow_id: int) -> Dict:
    """Get the status of a workflow."""
    db = _db()
    if not db:
        return {"status": "error", "message": "Database not available"}
    
    workflow = db.get_workflow_with_steps(workflow_id)
    if not workflow:
        return {"status": "error", "message": f"Workflow {workflow_id} not found"}
    
    steps = workflow.get("steps", [])
    completed = sum(1 for s in steps if s.get("status") == "completed")
    total = len(steps)
    
    return {
        "workflow_id": workflow_id,
        "name": workflow.get("name"),
        "status": workflow.get("status", "unknown"),
        "progress": f"{completed}/{total}",
        "steps": steps
    }


def list_workflows(limit: int = 20) -> List[Dict]:
    """List recent workflows."""
    db = _db()
    if not db:
        return []
    
    workflows = db.get_workflows(limit=limit)
    return [
        {
            "id": w.get("id"),
            "name": w.get("name"),
            "status": w.get("status"),
            "created_at": w.get("created_at"),
            "steps": len(w.get("steps", []))
        }
        for w in workflows
    ]


# ============================================================================
# INITIALIZATION
# ============================================================================

logger.info("[WORKFLOW] Workflow engine initialized with %d templates", len(WORKFLOW_TEMPLATES))