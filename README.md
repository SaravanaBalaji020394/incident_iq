# Incident IQ - Multi-Agent SRE Engine

Incident IQ is an automated incident response pipeline built using FastAPI, LangGraph, and ChromaDB. It accepts production alerts via a JSON webhook payload, automatically categorizes the incident severity, retrieves the matching standard operating procedure or runbook using semantic search, and executes targeted mock remediation steps for critical infrastructure events.

The system features a strict short-circuit logic rule: high-severity events (P1/P2) trigger active automated recovery mechanisms, while low-severity warnings (P3/P4) bypass tools entirely to protect infrastructure from unnecessary script executions.

## Project Architecture

The core orchestration engine handles messages sequentially across five decoupled functional blocks:

1. FastAPI Gateway: Ingests the raw incident webhook data and strictly validates input layout properties using Pydantic schemas.
2. Triage Node: Runs a structured LLM prompt to classify the category, extract entities, assign severity, and document its logic.
3. Knowledge Base Node: Queries a local vector database index via ChromaDB using semantic lookup to extract matching recovery manuals.
4. Programmatic Router: Evaluates state properties in standard code to decide whether to push to the remediation tool or short-circuit.
5. Notifier Node: Compiles the full chronological transaction history into a structured Markdown summary ledger.

## Setup Instructions

1. Clone this repository locally:
git clone https://github.com/yourusername/incident_iq.git
cd incident_iq

2. Create and activate a clean virtual environment:
python -m venv .venv
.venv\Scripts\activate

3. Install the required project dependencies:
pip install -r requirements.txt

4. Configure your environmental access keys in your terminal session:
set OPENAI_API_KEY=your_actual_openai_api_key_here

## Execution Guide

To initialize the ASGI server engine with live reloading capabilities enabled, run the module execution command from the root folder directory:

python -m src.main

Once the terminal outputs confirmation that Uvicorn is successfully running, open your web browser and navigate directly to the automated documentation sandbox interface:

http://127.0.0.1:8000/docs

## Sample Payloads For Testing

### Scenario A: High Severity Outage (Triggers Active Tool Execution)
{
  "incident_id": "INC-99112",
  "service_name": "payment-gateway",
  "error_message": "DatabaseConnectionError: Connection timeout after 30000ms. Critical pool exhaustion detected on primary cluster.",
  "timestamp": "2026-06-18T08:00:00Z"
}

### Scenario B: Low Severity Warning (Triggers Safety Short-Circuit)
{
  "incident_id": "INC-77211",
  "service_name": "checkout-ui",
  "error_message": "Warning: CDN returning 404 load error for non-breaking static legacy asset asset_old.css",
  "timestamp": "2026-06-18T01:00:00Z"
}
