import base64
import requests
import os

os.makedirs("images", exist_ok=True)

diagrams = {
    "title": """graph TB
    classDef title_text fill:none,stroke:none,color:#2A2A2A,font-weight:bold,font-size:36px
    classDef sub_text fill:none,stroke:none,color:#555,font-size:24px
    classDef central fill:#1A365D,stroke:#0f2240,stroke-width:3px,color:#fff,font-weight:bold,font-size:20px
    classDef peripheral fill:#F3F4F6,stroke:#CBD5E1,stroke-width:2px,color:#1E293B
    T1[DefectRouter-AI]:::title_text
    T2[Multi-Agent Quality Control & Triaging]:::sub_text
    
    T1 --- T2
    T2 --- C((Message Bus)):::central
    
    C --- A1[Maintenance Agent]:::peripheral
    C --- A2[Quality Agent]:::peripheral
    C --- A3[Calibration Agent]:::peripheral
    
    style T1 stroke:none,fill:none
    style T2 stroke:none,fill:none
    """,
    
    "architecture": """graph LR
    classDef system fill:#0ea5e9,stroke:#0369a1,color:#fff,font-weight:bold
    classDef agent fill:#f59e0b,stroke:#b45309,color:#fff,font-weight:bold
    classDef db fill:#10b981,stroke:#047857,color:#fff,font-weight:bold
    
    S[(IoT Sensors)]:::system -->|Abnormal Sensor Payload| D[Diagnostic Agent]:::agent
    D -->|Updates State| MB[(Shared DefectState)]:::db
    D --> R{Router}
    R -->|Vibration > 5.0| M1[Maintenance Agent]:::agent
    R -->|Temp > 80| M2[Calibration Agent]:::agent
    R -->|Other| M3[Material Agent]:::agent
    
    M1 -.->|Appends Log| MB
    M2 -.->|Appends Log| MB
    M3 -.->|Appends Log| MB
    """,
    
    "sequence": """sequenceDiagram
    participant S as IoT Sensor
    participant DA as Diagnostic Agent
    participant BUS as Shared State (Bus)
    participant CA as Calibration Agent
    
    S->>DA: Send Anomaly (Temp=85, Vib=2)
    DA->>BUS: Log "Analyzing sensor data..."
    DA->>DA: Evaluate Thresholds/LLM
    DA->>BUS: Log "Diagnosis: Calibration (Medium Severity)"
    DA->>CA: Route to Calibration Agent
    CA->>BUS: Log "Initiating remote sequence..."
    CA->>CA: Adjust Thermal Offsets via MQTT
    CA->>BUS: Log "Resolved automatically."
    BUS-->>S: Resolution Acknowledged
    """,
    
    "flow": """flowchart TD
    classDef start fill:#10b981,stroke:#047857,color:#fff
    classDef process fill:#f3f4f6,stroke:#cbd5e1,color:#1e293b
    classDef endNode fill:#6b7280,stroke:#374151,color:#fff
    
    A[New Incident Detected]:::start --> B(Build LangGraph State)
    B --> C[Run Diagnostic Agent]:::process
    C --> D{Determine Defect Type?}
    
    D -->|Calibration| E[Calibration Agent]:::process
    D -->|Maintenance| F[Maintenance Agent]:::process
    D -->|Material| G[Material Agent]:::process
    
    E --> H[End Process]:::endNode
    F --> H
    G --> H
    """
}

for name, code in diagrams.items():
    print(f"Generating {name}_diagram.png...")
    # Wrap in mermaid syntax or use encoded directly
    encoded = base64.b64encode(code.encode()).decode()
    url = f"https://mermaid.ink/img/{encoded}?bgColor=ffffff"
    try:
        response = requests.get(url)
        response.raise_for_status()
        filepath = f"images/{name}_diagram.png"
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Saved {filepath}")
    except Exception as e:
        print(f"Failed to generate {name}_diagram.png: {e}")
        exit(1)

print("All diagrams generated successfully.")
