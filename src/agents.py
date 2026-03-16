import os
import time
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from .state import DefectState, LogEntry

# Initialize LLM. Fallback to None if API key not found, making logic robust for terminal generation.
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini") if os.getenv("OPENAI_API_KEY") else None

class DiagnosticResult(BaseModel):
    defect_type: str = Field(description="Category of defect: 'Calibration', 'Maintenance', or 'Material'.")
    severity: str = Field(description="Severity level: 'Low', 'Medium', or 'High'")
    reasoning: str = Field(description="Brief explanation of diagnosis.")

def add_log(state: DefectState, agent_name: str, message: str) -> DefectState:
    entry = LogEntry(
        agent=agent_name,
        message=message,
        timestamp=datetime.now().strftime("%H:%M:%S")
    )
    if not state.get("log_history"):
        state["log_history"] = []
    
    # Needs a copy to trigger update in LangGraph state usually, but list append is fine if handled.
    new_history = state["log_history"].copy()
    new_history.append(entry)
    state["log_history"] = new_history
    return state

def diagnostic_agent(state: DefectState) -> DefectState:
    state = add_log(state, "Diagnostic Agent", f"Analyzing sensor data for incident {state.get('incident_id', 'N/A')}...")
    time.sleep(1.2) # simulate thinking
    
    if llm:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert diagnostic AI for a manufacturing plant. Analyze sensor data and categorize the defect into 'Calibration', 'Maintenance', or 'Material'. Output High/Medium/Low severity."),
                ("user", "Sensor Data: {sensor_data}")
            ])
            chain = prompt | llm.with_structured_output(DiagnosticResult)
            result = chain.invoke({"sensor_data": str(state.get("sensor_data", {}))})
            
            state["defect_type"] = result.defect_type
            state["severity"] = result.severity
            state = add_log(state, "Diagnostic Agent", f"Diagnosis complete. Determined defect type: {result.defect_type} (Severity: {result.severity})")
        except Exception as e:
            # Fallback on error
            state["defect_type"] = "Maintenance"
            state["severity"] = "High"
            state = add_log(state, "Diagnostic Agent", f"Fallback diagnosis. Determined defect type: {state['defect_type']}")
    else:
        # Predictable mock logic for consistent terminal GIF generation
        data = state.get("sensor_data", {})
        if data.get("vibration", 0) > 5.0:
            state["defect_type"] = "Maintenance"
            state["severity"] = "High"
            reason = "High vibration indicative of bearing wear."
        elif data.get("temperature", 0) > 80:
            state["defect_type"] = "Calibration"
            state["severity"] = "Medium"
            reason = "Thermal thresholds exceeded; requires offset tuning."
        else:
            state["defect_type"] = "Material"
            state["severity"] = "Low"
            reason = "Acoustic or visual anomaly suggests material flaw."
            
        time.sleep(1.5)
        state = add_log(state, "Diagnostic Agent", f"Evaluated heuristics. Reason: {reason}")
        state = add_log(state, "Diagnostic Agent", f"Diagnosis complete. Determined defect type: {state['defect_type']} (Severity: {state['severity']})")
        
    state["status"] = "Triaged"
    return state
    
def route_defect(state: DefectState) -> str:
    dtype = state.get("defect_type", "")
    if dtype == "Calibration":
        return "calibration_agent"
    elif dtype == "Maintenance":
        return "maintenance_agent"
    else:
        return "material_agent"

def calibration_agent(state: DefectState) -> DefectState:
    state = add_log(state, "Calibration Agent", "Initiating remote machine calibration sequence...")
    time.sleep(1.2) 
    state["assigned_team"] = "Automated Systems"
    state["resolution_plan"] = "Adjusted thermal offsets and reset sensor thresholds via MQTT."
    state["status"] = "Resolved"
    state = add_log(state, "Calibration Agent", "Calibration successful. Defect resolved automatically.")
    return state

def maintenance_agent(state: DefectState) -> DefectState:
    state = add_log(state, "Maintenance Agent", "High wear detected. Generating work order for physical inspection...")
    time.sleep(1.3)
    state["assigned_team"] = "Floor Technicians (Tier 2)"
    state["resolution_plan"] = "Dispatching technician to inspect spindle bearings and replace."
    state["status"] = "Pending_Human_Action"
    state = add_log(state, "Maintenance Agent", "Work order #992 generated. Escalated to human technicians.")
    return state

def material_agent(state: DefectState) -> DefectState:
    state = add_log(state, "Material Agent", "Anomaly in raw material specs. Flagging supplier batch...")
    time.sleep(1.4)
    state["assigned_team"] = "Quality Control"
    state["resolution_plan"] = "Quarantining batch B-772 and notifying supplier QA team."
    state["status"] = "In_Progress"
    state = add_log(state, "Material Agent", "Batch quarantined. Awaiting QA review.")
    return state
