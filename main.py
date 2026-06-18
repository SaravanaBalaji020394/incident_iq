from fastapi import FastAPI, HTTPException
from src.schemas import IncidentPayload
from src.agent import agent_app

# Initialize FastAPI with metadata matching standard API specs
app = FastAPI(
    title="Incident IQ Automated SRE Engine",
    version="1.0.0",
    description="Agentic incident triaging and runbook remediation system using LangGraph and ChromaDB"
)

# --- ENDPOINT 1: HEALTH CHECK ---
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Verifies that the API server is up and responsive.
    """
    return {"status": "healthy", "service": "incident_iq"}

# --- ENDPOINT 2: INCIDENT PROCESSING PIPELINE ---
@app.post("/process", tags=["Core Pipeline"])
async def process_incident(payload: IncidentPayload):
    """
    Ingests an incident log, triages it using gpt-4o-mini,
    queries the local ChromaDB vector store for matching runbooks,
    simulates corrective action, and returns an end-to-end journey ledger.
    """
    try:
        print(f"\n🚀 [FastAPI] Processing incident event: {payload.incident_id} for service: {payload.service_name}")
        
        # FIX: Define the initial state as a native dictionary so LangGraph can subscript it []
        initial_state = {
            "payload": payload,
            "triage": None,
            "retrieved_runbook": "",
            "actions_executed": [],
            "final_summary": ""
        }
        
        # Execute the compilation graph synchronously
        final_output_state = agent_app.invoke(initial_state)
        
        return final_output_state
        
    except Exception as e:
        print(f" [FastAPI Structural Error] Pipeline execution failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal agent pipeline execution failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)