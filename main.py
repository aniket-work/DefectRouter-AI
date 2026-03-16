import time
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.graph import build_defect_router_graph

console = Console()

def print_header():
    console.print(Panel.fit(
        "[bold cyan]DefectRouter-AI[/bold cyan]\n"
        "[dim]Multi-Agent Manufacturing Quality Control & Triaging System[/dim]\n"
        "[dim italic]Powered by LangGraph and Advanced Communication Protocol (ACP)[/dim italic]",
        border_style="cyan"
    ))

def print_logs(log_history, seen_logs_count):
    agent_colors = {
        "Diagnostic Agent": "magenta",
        "Calibration Agent": "green",
        "Maintenance Agent": "red",
        "Material Agent": "yellow"
    }
    
    for entry in log_history[seen_logs_count:]:
        color = agent_colors.get(entry.agent, "white")
        console.print(f"[dim]{entry.timestamp}[/dim] [bold {color}]{entry.agent}[/bold {color}] ➜ {entry.message}")
        time.sleep(0.6)  # Simulate network latency/ACP processing
        
    return len(log_history)

def run_incident(incident_id: str, sensor_data: dict):
    print_header()
    console.print(f"\n[bold white]🚨 New Incident Detected: {incident_id}[/bold white]")
    console.print(f"[dim]Incoming Sensor Payload: {json.dumps(sensor_data)}[/dim]\n")
    
    app = build_defect_router_graph()
    state = {
        "incident_id": incident_id,
        "sensor_data": sensor_data,
        "defect_type": "Unknown",
        "severity": "Unknown",
        "assigned_team": "Unassigned",
        "resolution_plan": "Pending",
        "status": "New",
        "log_history": []
    }
    
    console.print("[bold blue][SYSTEM] Initialization Sequence Started...[/bold blue]")
    time.sleep(1)
    
    seen_logs_count = 0
    final_state = state
    
    for output in app.stream(state):
        for node_name, updated_state in output.items():
            final_state = updated_state
            if "log_history" in updated_state and updated_state["log_history"]:
                seen_logs_count = print_logs(updated_state["log_history"], seen_logs_count)

    console.print("\n[bold green]✅ Incident Processing Complete.[/bold green]\n")
    
    # ASCII Table Summary
    table = Table(title="Incident Summary Report", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim", width=20)
    table.add_column("Value")
    
    table.add_row("Incident ID", final_state["incident_id"])
    table.add_row("Defect Type", final_state["defect_type"])
    table.add_row("Severity", final_state["severity"])
    table.add_row("Assigned Team", final_state["assigned_team"])
    table.add_row("Final Status", final_state["status"])
    table.add_row("Resolution Plan", final_state["resolution_plan"])
    
    console.print(table)
    print("\n")

if __name__ == "__main__":
    test_incident = {
        "incident_id": "INC-88A92",
        "sensor_data": {
            "machine_id": "CNC-Milli-04",
            "vibration": 6.2,
            "temperature": 75,
            "acoustic_anomaly_score": 0.85
        }
    }
    run_incident(test_incident["incident_id"], test_incident["sensor_data"])
