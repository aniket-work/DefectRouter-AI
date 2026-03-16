from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel

class LogEntry(BaseModel):
    agent: str
    message: str
    timestamp: str

class DefectState(TypedDict):
    incident_id: str
    sensor_data: Dict[str, Any]
    defect_type: str
    severity: str
    assigned_team: str
    resolution_plan: str
    status: str
    log_history: List[LogEntry]
