"""
Omniscience Router for SERA Platform
Exposes APIs for:
1. Unified Global Perception Stream
2. Live Internet Retrieval & Knowledge Graph RAG Query
3. Downloadable Detailed PDF Intelligence Report
4. 100% Autonomous AI Self-Update Ticker Logs
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from services.omniscience_service import OmniscienceService, OmniscienceGuardian

router = APIRouter(prefix="/api/omniscience", tags=["Omniscience Engine"])

class RAGQueryRequest(BaseModel):
    query: str

class PDFReportRequest(BaseModel):
    query: str
    entity: str
    synthesis: str
    facts: List[Dict[str, Any]] = []
    knowledge_graph: Dict[str, Any] = {}

@router.get("/perception")
async def get_global_perception():
    try:
        perception = await OmniscienceService.get_global_perception()
        return perception
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute global perception: {str(e)}")

@router.post("/query")
async def query_omniscience(req: RAGQueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
    try:
        res = await OmniscienceService.query_omniscience_rag(req.query)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Omniscience query execution error: {str(e)}")

@router.post("/report/pdf")
async def generate_pdf_report(req: PDFReportRequest):
    try:
        pdf_bytes = OmniscienceService.generate_pdf_report(
            query=req.query,
            entity=req.entity,
            synthesis=req.synthesis,
            facts=req.facts,
            graph=req.knowledge_graph
        )
        filename = f"SERA_Omniscience_Report_{req.entity.replace(' ', '_')}.pdf"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF report generation failed: {str(e)}")

@router.get("/guardian/logs")
@router.get("/evolution/logs")
async def get_evolution_logs():
    logs = OmniscienceGuardian.get_remediation_logs()
    return {"count": len(logs), "logs": logs}


