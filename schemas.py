from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class SeverityLevel(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class IncidentPayload(BaseModel):
    incident_id: str = Field(..., description="Unique identifier for the incoming alert")
    service_name: str = Field(..., description="The microservice or system component throwing the error")
    error_message: str = Field(..., description="The raw error log or exception stack trace")
    timestamp: str = Field(..., description="ISO timestamp of when the event occurred")

class TriageResult(BaseModel):
    severity: SeverityLevel = Field(..., description="Assigned incident priority")
    root_cause_category: str = Field(..., description="Categorization (e.g., Database, Network, OOM)")
    extracted_entities: List[str] = Field(default_factory=list, description="Targeted keywords like pod names, error codes")
    justification: str = Field(..., description="Brief rationale behind the triage assessment")

class ActionTaken(BaseModel):
    tool_name: str = Field(..., description="The mocked recovery tool invoked")
    status: str = Field(..., description="Outcome of the tool execution (e.g., SUCCESS, FAILED)")
    output: str = Field(..., description="Terminal output or logs from the tool")

class AgenticState(BaseModel):
    payload: IncidentPayload
    triage: Optional[TriageResult] = None
    retrieved_runbook: Optional[str] = None
    actions_executed: List[ActionTaken] = Field(default_factory=list)
    final_summary: Optional[str] = None