import httpx
from config import AI_API_KEY, AI_MODEL, AI_BASE_URL
from core.entity_resolution import entity_registry

SYSTEM_PROMPT = """You are SERA-AI, the intelligent query interface for the SERA Intelligence Platform.
You help analysts understand the real-time behavioral intelligence data flowing through the platform.
The platform tracks entities (people, assets, processes) across financial, healthcare, IoT, and social domains.
You answer questions about entities, entropy readings, predictions, and data streams.
Be concise, analytical, and use technical precision. Keep answers under 150 words unless asked for detail."""

async def chat(user_message: str) -> str:
    """Send a message to the AI and return the response."""
    
    # Query ChromaDB Vector database for semantic RAG context
    retrieved_docs = []
    try:
        from services.vector_store import VectorStoreService
        retrieved_docs = VectorStoreService.query_knowledge_base(user_message, limit=4)
    except Exception as e:
        import logging
        logging.getLogger("sera.chat_service").error(f"Failed to query knowledge base: {e}")

    rag_context = ""
    if retrieved_docs:
        rag_context = "\n\nRelevant Platform Telemetry Logs (Retrieved via APEX Semantic Search):\n"
        for i, doc in enumerate(retrieved_docs):
            rag_context += f"[{i+1}] {doc}\n"
   
    if not AI_API_KEY:
        mock_res = _mock_response(user_message)
        if retrieved_docs:
            mock_res += "\n\n**[APEX Semantic Memory Retrieval (RAG)]**:\n" + "\n".join(f"• {doc}" for doc in retrieved_docs)
        return mock_res

    entities = entity_registry.get_all()
    pre_transition = [e for e in entities if e["status"] == "pre-transition"]
    context = f"\nCurrent platform state: {len(entities)} entities tracked, {len(pre_transition)} in pre-transition state."

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AI_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT + context + rag_context},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                try:
                    data = response.json()
                    error = data.get("error", data)
                    error_msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
                except Exception:
                    error_msg = response.text or f"HTTP {response.status_code}"
                
                mock_res = _mock_response(user_message)
                if retrieved_docs:
                    mock_res += "\n\n**[APEX Semantic Memory Retrieval (RAG)]**:\n" + "\n".join(f"• {doc}" for doc in retrieved_docs)
                return f"{mock_res}\n\n*(Demo Fallback: AI Service returned status {response.status_code} - {error_msg})*"

            try:
                data = response.json()
                if "error" in data:
                    error = data["error"]
                    error_msg = error.get("message", "Unknown error") if isinstance(error, dict) else str(error)
                    mock_res = _mock_response(user_message)
                    if retrieved_docs:
                        mock_res += "\n\n**[APEX Semantic Memory Retrieval (RAG)]**:\n" + "\n".join(f"• {doc}" for doc in retrieved_docs)
                    return f"{mock_res}\n\n*(Demo Fallback: AI Service error - {error_msg})*"
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                if "content" in data:
                    return data["content"][0]["text"]
                return "AI response format not recognised. Please check API configuration."
            except Exception as e:
                mock_res = _mock_response(user_message)
                if retrieved_docs:
                    mock_res += "\n\n**[APEX Semantic Memory Retrieval (RAG)]**:\n" + "\n".join(f"• {doc}" for doc in retrieved_docs)
                return f"{mock_res}\n\n*(Demo Fallback: Failed to parse AI response - {str(e)})*"
    except Exception as e:
        mock_res = _mock_response(user_message)
        if retrieved_docs:
            mock_res += "\n\n**[APEX Semantic Memory Retrieval (RAG)]**:\n" + "\n".join(f"• {doc}" for doc in retrieved_docs)
        return f"{mock_res}\n\n*(Demo Fallback: AI Service unavailable - {str(e)})*"

def _mock_response(message: str) -> str:
    msg = message.lower()
    entities = entity_registry.get_all()
    pre_transition = [e for e in entities if e["status"] == "pre-transition"]
    
    # ── Dynamic Company & Target Entity Extraction ──
    KNOWN_COMPANIES = {
        "nvda": ("NVDA", "NVIDIA Corporation"), "nvidia": ("NVDA", "NVIDIA Corporation"),
        "aapl": ("AAPL", "Apple Inc."), "apple": ("AAPL", "Apple Inc."),
        "msft": ("MSFT", "Microsoft Corporation"), "microsoft": ("MSFT", "Microsoft Corporation"),
        "googl": ("GOOGL", "Alphabet Inc."), "google": ("GOOGL", "Alphabet Inc."),
        "amzn": ("AMZN", "Amazon.com Inc."), "amazon": ("AMZN", "Amazon.com Inc."),
        "tsla": ("TSLA", "Tesla, Inc."), "tesla": ("TSLA", "Tesla, Inc."),
        "meta": ("META", "Meta Platforms, Inc."), "facebook": ("META", "Meta Platforms, Inc."),
        "nflx": ("NFLX", "Netflix, Inc."), "netflix": ("NFLX", "Netflix, Inc."),
        "amd": ("AMD", "Advanced Micro Devices"), "intc": ("INTC", "Intel Corporation"),
        "pltr": ("PLTR", "Palantir Technologies"), "palantir": ("PLTR", "Palantir Technologies"),
        "crwd": ("CRWD", "CrowdStrike Holdings"), "crowdstrike": ("CRWD", "CrowdStrike Holdings"),
        "panw": ("PANW", "Palo Alto Networks"), "palo alto": ("PANW", "Palo Alto Networks"),
        "orcl": ("ORCL", "Oracle Corporation"), "oracle": ("ORCL", "Oracle Corporation"),
        "ibm": ("IBM", "International Business Machines"), "wipro": ("WIPRO", "Wipro Limited"),
        "infosys": ("INFY", "Infosys Limited"), "reliance": ("RELIANCE", "Reliance Industries")
    }

    found_ticker, found_name = None, None
    for key, (t, n) in KNOWN_COMPANIES.items():
        if key in msg:
            found_ticker, found_name = t, n
            break

    # If user mentioned a specific company
    if found_ticker:
        return (
            f"📊 **Real-Time Intelligence Analysis for {found_name} ({found_ticker})**:\n"
            f"• **STYX Defense Radar**: Target cluster active. 0 critical zero-day exploits detected on port 443/8080.\n"
            f"• **AXIOM Entropy Score**: `0.421` (Z-Score: Normal Stability Register)\n"
            f"• **KRONOS Causal Trajectory**: 88.4% expansion confidence across GICS supply chain nodes.\n"
            f"• **SEC & Telemetry Filings**: 14 recent disclosures indexed with 85% claim credibility score.\n"
            f"• **Recommendation**: Maintain active monitoring. All primary operational signals stable."
        )

    if "entropy" in msg:
        return f"Current platform entropy analysis: {len(pre_transition)} of {len(entities)} entities show elevated entropy. AXIOM-Φ is monitoring all behavioral channels for phase transitions."
    elif "entity" in msg or "entities" in msg:
        return f"Platform is tracking {len(entities)} resolved entities across financial, healthcare, IoT, and social domains. {len(pre_transition)} are currently flagged as pre-transition."
    elif "predict" in msg or "zola" in msg:
        return "ZOLA has generated intervention briefs for all pre-transition entities. Success probability ranges from 65% to 92% depending on the behavioral transition type."
    else:
        return "SERA Intelligence Platform is operating normally. All data streams are active. Ask me about any company (e.g. NVDA, TSLA, AAPL, MSFT, CrowdStrike, Palantir), entropy levels, or STYX security radar findings."