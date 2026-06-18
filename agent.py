import os
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Import state schemas and structured outputs
from src.schemas import AgenticState, TriageResult, ActionTaken

load_dotenv()

# =====================================================================
# 1. CORE AGENT COMPONENT INITIALIZATIONS
# =====================================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# Helper function to safely extract values whether state is a dict or an object
def get_state_val(state, key):
    if isinstance(state, dict):
        return state.get(key)
    return getattr(state, key, None)

# =====================================================================
# 2. DEFINE SYSTEM AGENT NODES
# =====================================================================

def triage_node(state: AgenticState) -> dict:
    """Triage Agent: Extracts entities and determines event severity."""
    payload = get_state_val(state, "payload")
    print(f"🕵️ [Triage Agent] Classifying incident: {payload.incident_id}")
    
    structured_llm = llm.with_structured_output(TriageResult)
    
    system_prompt = (
        "You are an expert SRE Triage Agent. Analyze the incident payload error logs.\n"
        "Classify severity precisely (P1, P2, P3, or P4).\n"
        "Categorize into: database, network, application, or infra."
    )
    
    user_content = f"Service: {payload.service_name}\nError: {payload.error_message}"
    result: TriageResult = structured_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ])
    
    return {"triage": result}


def knowledge_node(state: AgenticState) -> dict:
    """Knowledge Agent: Executes semantic RAG lookup over the seeded corpus."""
    print(f"📖 [Knowledge Agent] Querying RAG corpus for context...")
    payload = get_state_val(state, "payload")
    
    query = f"{payload.service_name} {payload.error_message}"
    docs = vector_db.similarity_search(query, k=1)
    
    runbook_text = docs[0].page_content if docs else "No matching runbook found."
    return {"retrieved_runbook": runbook_text}


def remediation_node(state: AgenticState) -> dict:
    """Remediation Agent: Fires automation tools ONLY for high-severity issues."""
    triage = get_state_val(state, "triage")
    severity = triage.severity if triage else "P4"
    
    if severity not in ["P1", "P2"]:
        print(f"🛑 [Remediation Guard] Bypassing tool execution for low severity: {severity}")
        return {"actions_executed": []}
        
    print(f"⚡ [Remediation Agent] High Severity ({severity}) confirmed. Triggering DevOps engine...")
    runbook = get_state_val(state, "retrieved_runbook") or ""
    
    tool_log = ActionTaken(
        tool_name="Mock-DevOps-Automation-Engine",
        status="SUCCESS",
        output=f"Automated action triggered based on instructions: '{runbook[:60]}...'"
    )
    
    return {"actions_executed": [tool_log]}


def notifier_node(state: AgenticState) -> dict:
    """Notifier Agent: Compiles crisp corporate Markdown summary."""
    print(f"📢 [Notifier Agent] Compiling final summary notification block...")
    payload = get_state_val(state, "payload")
    triage = get_state_val(state, "triage")
    actions = get_state_val(state, "actions_executed") or []
    
    action_text = f"✅ Automated action taken: {actions[0].output}" if actions else "⚠️ No automated tooling required (Bypassed due to low severity routing specifications)."
    
    summary_prompt = (
        "You are an SRE Notifier Agent. Review the technical context and compile a concise, "
        "executive markdown summary details sheet listing triage results, actions taken (or why they were skipped), and clear conclusions."
    )
    
    context_data = (
        f"Incident: {payload.incident_id}\n"
        f"Severity: {triage.severity if triage else 'N/A'}\n"
        f"Category: {triage.root_cause_category if triage else 'N/A'}\n"
        f"Action Log: {action_text}"
    )
    
    response = llm.invoke([
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": context_data}
    ])
    
    return {"final_summary": response.content}

# =====================================================================
# 3. DYNAMIC ROUTING GOVERNOR
# =====================================================================

def routing_governor(state: AgenticState) -> Literal["execute_tools", "skip_tools"]:
    """
    Orchestration Router: Directs traffic paths based on triage severity.
    """
    triage = get_state_val(state, "triage")
    severity = triage.severity if triage else "P4"
    
    if severity in ["P1", "P2"]:
        print(f"🔀 [Orchestrator] High Severity ({severity}) flagged. Routing to Remediation Agent.")
        return "execute_tools"
    else:
        print(f"🔀 [Orchestrator] Low Severity ({severity}) flagged. Direct-routing to Notifier.")
        return "skip_tools"

# =====================================================================
# 4. WIRE THE LANGGRAPH STATE MACHINE
# =====================================================================

workflow = StateGraph(AgenticState)

# Add nodes matching graph specs
workflow.add_node("triage_node", triage_node)
workflow.add_node("knowledge_node", knowledge_node)
workflow.add_node("remediation_node", remediation_node)
workflow.add_node("notifier_node", notifier_node)

# Map edge connections
workflow.set_entry_point("triage_node")
workflow.add_edge("triage_node", "knowledge_node")

# Inject clear conditional routing edge keys
workflow.add_conditional_edges(
    "knowledge_node",
    routing_governor,
    {
        "execute_tools": "remediation_node",
        "skip_tools": "notifier_node"
    }
)

workflow.add_edge("remediation_node", "notifier_node")
workflow.add_edge("notifier_node", END)

agent_app = workflow.compile()