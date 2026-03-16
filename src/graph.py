from langgraph.graph import StateGraph, END
from .state import DefectState
from .agents import diagnostic_agent, route_defect, calibration_agent, maintenance_agent, material_agent

def build_defect_router_graph():
    workflow = StateGraph(DefectState)
    
    # Add nodes
    workflow.add_node("diagnostic_agent", diagnostic_agent)
    workflow.add_node("calibration_agent", calibration_agent)
    workflow.add_node("maintenance_agent", maintenance_agent)
    workflow.add_node("material_agent", material_agent)
    
    # Set entry point
    workflow.set_entry_point("diagnostic_agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "diagnostic_agent",
        route_defect,
        {
            "calibration_agent": "calibration_agent",
            "maintenance_agent": "maintenance_agent",
            "material_agent": "material_agent"
        }
    )
    
    # Add edges to END
    workflow.add_edge("calibration_agent", END)
    workflow.add_edge("maintenance_agent", END)
    workflow.add_edge("material_agent", END)
    
    return workflow.compile()
