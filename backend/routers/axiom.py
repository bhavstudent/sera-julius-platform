from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from database import async_session_maker
from models.commerce import CompanyModel
from services.axiom_monitor import AxiomMonitor

router = APIRouter(prefix="/api/axiom", tags=["axiom"])

@router.get("/monitor")
async def get_axiom_monitor():
    try:
        from services.live_engine import get_live_state
        live_state = get_live_state()

        async with async_session_maker() as session:
            # Count total companies in DB
            from sqlalchemy import func
            total_res = await session.execute(select(func.count(CompanyModel.id)))
            db_entities = total_res.scalar() or 0
            
            # Fetch companies for detailed display
            comp_res = await session.execute(select(CompanyModel).limit(50))
            companies = comp_res.scalars().all()

        # Real-time dynamic entity count (grows as AI discovers new entities)
        total_entities = max(db_entities, live_state.get("total_entities", 59))

        entropy_summary = []
        active_alerts = 0

        # Build detailed entropy summary with fallback when database is empty
        display_companies = companies if companies else [
            type("Company", (), {"id": f"comp_{i}", "legal_name": name})()
            for i, name in enumerate([
                "CrowdStrike Cyber Ltd", "NVIDIA AI Infrastructure", "Palantir Defense", 
                "SentinelOne Systems", "Palo Alto Networks", "Cloudflare Global Net"
            ])
        ]

        for company in display_companies:
            metrics = AxiomMonitor.get_live_entropy_metrics(company.id, company.legal_name)
            is_pre = metrics["is_pre_transition"]
            
            if is_pre:
                active_alerts += 1

            status = "pre-transition" if is_pre else "stable"

            entropy_summary.append({
                "entity_id": company.id,
                "entity_name": company.legal_name,
                "domain": company.sector or "technology",
                "entropy": metrics["current_entropy"],
                "baseline": metrics["baseline_entropy"],
                "z_score": metrics["z_score"],
                "status": status,
                "history": metrics["history"]
            })

        # Extract high risk entities with rich live siren telemetry
        high_risk_entities = [
            {
                "entity_id": item["entity_id"],
                "entity_name": item["entity_name"],
                "risk_factor": "entropy_spike",
                "entropy": item["entropy"],
                "z_score": item["z_score"],
                "domain": item["domain"],
                "timestamp": datetime.utcnow().strftime("%H:%M:%S") + " UTC"
            }
            for item in entropy_summary if item["status"] == "pre-transition" or item["entropy"] > 1.8
        ]

        return {
            "total_entities": total_entities,
            "active_alerts": len(high_risk_entities),
            "high_risk_entities": high_risk_entities,
            "entropy_summary": entropy_summary,
            "ai_engine_status": "ONLINE_ACTIVE_SCANNING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/entropy")
async def get_entropy_data():
    # Keep backward compatibility if other places call it
    res = await get_axiom_monitor()
    return res["entropy_summary"]

@router.get("/alerts")
async def get_alerts():
    # Keep backward compatibility if other places call it
    res = await get_axiom_monitor()
    alerts = []
    for item in res["entropy_summary"]:
        if item["status"] == "pre-transition":
            alerts.append({
                "entity_id": item["entity_id"],
                "entity_name": item["entity_name"],
                "alert_type": "entropy_spike",
                "severity": "warning" if item["entropy"] < 2.0 else "critical",
                "entropy_value": item["entropy"],
                "description": f"Entity {item['entity_name']} showing entropy spike in {item['domain']} domain"
            })
    return alerts