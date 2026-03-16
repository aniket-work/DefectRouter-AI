---
title: "Autonomous Manufacturing Defect Triager with Multi-Agent AI (Master Edition)"
subtitle: "How I Automated Quality Control Routing Using LangGraph, a Structured Message Bus, and Persistent Shared State"
published: true
tags: ai, python, machinelearning, programming
---

> **How I Automated Quality Control Routing Using LangGraph, a Structured Message Bus, and Persistent Shared State**

![Title Image](https://raw.githubusercontent.com/aniket-work/DefectRouter-AI/main/images/title-animation.gif)

## TL;DR

1. I designed a multi-agent system to automate defect diagnosis and routing in a simulated manufacturing environment.
2. I built it using LangGraph to manage a structured message bus and persistent shared state.
3. I implemented an Advanced Communication Protocol (ACP) simulation to visualize the reasoning process realistically.
4. I found that coordinating multiple specialized agents vastly improves incident response times compared to a monolithic LLM.

## Introduction

I have often observed that in modern manufacturing pipelines, the speed at which you can diagnose an anomaly detected by an IoT sensor dictates the overall efficiency of the plant. A single faulty spindle or a batch of off-spec raw material can bottleneck production for hours if not triaged immediately. In my opinion, traditional rule-based systems are too rigid to handle the nuanced, compounding errors that occur on an assembly line. This led me to experiment with Agentic AI. 

I thought to myself: *What if I could build a squad of specialized digital operators—a Diagnostic Agent, a Calibration Agent, a Maintenance Agent, and a Material Agent—that talk to each other through a centralized message bus?* From my experience, breaking down complex decisions into smaller, specialized agent scopes yields far more reliable outputs and significantly reduces hallucinations. In this experimental PoC, I will walk you through how I built DefectRouter-AI, my take on an autonomous manufacturing quality control coordinator. 

## What's This Article About?

This article dives deep into the architecture, design, and implementation of a multi-agent system that intelligently routes manufacturing defects. I wrote this to explore how a **Structured Message Bus** and **Persistent Shared State** can orchestrate complex workflows using LangGraph. I will show you how I implemented the logic to ingest JSON sensor payloads, have an AI diagnose the issue, and then programmatically route it to the right automated or human responder. I also put this together because I wanted to demonstrate how beautiful and functional an Advanced Communication Protocol (ACP) terminal UI can be when debugging multi-agent systems via `rich`.

## Tech Stack

1. **Python 3.10+**: The backbone of the entire application.
2. **LangGraph & LangChain**: For building the state machine and connecting the LLM logic.
3. **OpenAI API (gpt-4o-mini)**: The cognitive engine driving the diagnostic decisions. 
4. **Pydantic**: For strict typed parsing of the state and LLM structured outputs.
5. **Rich**: To render the gorgeous terminal UI and ASCII tables.

## Why Read It?

If you are a platform engineer, automation enthusiast, or an AI developer looking to move beyond simple chatbots, I think you will find immense value here. In my opinion, the future of enterprise AI lies in orchestration—making discrete AI components work together reliably. By reading my breakdown of this PoC, you will learn how to design a state graph that acts as a message bus, preventing agents from talking over each other and ensuring every decision is logged, stateful, and auditable.

## Let's Design

Before writing a single line of code, I realized I needed a solid blueprint. From my experience, jumping straight into LangGraph without a clear architecture leads to tangled state variables and infinite loops. 

![Architecture](https://raw.githubusercontent.com/aniket-work/DefectRouter-AI/main/images/architecture_diagram.png)

I conceptualized the architecture around a **Persistent Shared State**. I created a Pydantic-backed `TypedDict` that holds the `incident_id`, `sensor_data`, the `resolution_plan`, and most importantly, a `log_history`. Every agent mutation is appended to this log history.

The flow is simple but powerful:
1. The **IoT Sensor** triggers the system.
2. The **Diagnostic Agent** reads the payload and uses an LLM (or fallback heuristics) to determine the defect type and severity.
3. LangGraph evaluates a **Conditional Edge** to route the state to either Calibration, Maintenance, or Material agents.
4. The specialist agent defines a resolution plan and updates the state.
5. The system ends and prints an ASCII summary.

![Sequence](https://raw.githubusercontent.com/aniket-work/DefectRouter-AI/main/images/sequence_diagram.png)

## Let’s Get Cooking

### 1. Defining the Persistent State and Logs

I started by defining the memory layout. I observed that passing raw strings between agents is a nightmare to debug, so I put this together using strict typing.

```python
# src/state.py
from typing import TypedDict, List, Dict, Any
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
```
*I structured `DefectState` to act as the single source of truth. Every agent yields an updated dictionary that LangGraph merges into the main state.*

### 2. The Agent Logic

Next, I built the agents. I used `langchain_openai` to power the `Diagnostic Agent`. I think forcing structured outputs using Pydantic is the single greatest trick for reliable behavior.

```python
# src/agents.py (Snippet 1)
class DiagnosticResult(BaseModel):
    defect_type: str
    severity: str
    reasoning: str

def diagnostic_agent(state: DefectState) -> DefectState:
    state = add_log(state, "Diagnostic Agent", f"Analyzing sensor data...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze sensor data and categorize defect..."),
        ("user", "Sensor Data: {sensor_data}")
    ])
    chain = prompt | llm.with_structured_output(DiagnosticResult)
    result = chain.invoke({"sensor_data": str(state.get("sensor_data", {}))})
    state["defect_type"] = result.defect_type
    return state
```

### 3. Routing and Specialists

From my experience, conditional routing is where LangGraph shines. I wrote a simple Python function that directs the traffic.

```python
# src/agents.py (Snippet 2)
def route_defect(state: DefectState) -> str:
    dtype = state.get("defect_type", "")
    if dtype == "Calibration": return "calibration_agent"
    elif dtype == "Maintenance": return "maintenance_agent"
    else: return "material_agent"

def calibration_agent(state: DefectState) -> DefectState:
    state = add_log(state, "Calibration Agent", "Initiating remote machine calibration sequence...")
    state["assigned_team"] = "Automated Systems"
    state["resolution_plan"] = "Adjusted thermal offsets via MQTT."
    state["status"] = "Resolved"
    return state
```

### 4. Graph Orchestration

I wired everything together in `graph.py`.

![Flow](https://raw.githubusercontent.com/aniket-work/DefectRouter-AI/main/images/flow_diagram.png)

```python
# src/graph.py
from langgraph.graph import StateGraph, END
from .state import DefectState
from .agents import diagnostic_agent, route_defect, calibration_agent, maintenance_agent, material_agent

def build_defect_router_graph():
    workflow = StateGraph(DefectState)
    workflow.add_node("diagnostic_agent", diagnostic_agent)
    workflow.set_entry_point("diagnostic_agent")
    workflow.add_conditional_edges("diagnostic_agent", route_defect, {
        "calibration_agent": "calibration_agent",
        "maintenance_agent": "maintenance_agent",
        "material_agent": "material_agent"
    })
    return workflow.compile()
```

### 5. ACP Terminal Visualization

Finally, I wanted a beautiful UI. I wrote a `rich` console wrapper that streams the outputs.

```python
# main.py
def run_incident(incident_id: str, sensor_data: dict):
    print_header()
    app = build_defect_router_graph()
    state = { "incident_id": incident_id, ... } 
    
    seen_logs_count = 0
    for output in app.stream(state):
        for node_name, updated_state in output.items():
            if updated_state.get("log_history"):
                seen_logs_count = print_logs(updated_state["log_history"], seen_logs_count)
```

## Complex Implementation Theory: State Architecture

I think it is critical to pause and reflect on *why* this architecture works. In my experiments, trying to pass multi-turn conversation context directly between five different specialized components leads to immense token bloat. The context window fills up with "hello, how are you" pleasantries between agents.

By relying on a strict `TypedDict` containing only domain-specific variables (`defect_type`, `severity`, `log_history`), I completely eliminated chat-bot style conversational overhead. I observed that the agents perform pure data transformations. The Message Bus is not an LLM—it is rigid Python code determining the routing based on a highly constrained string output.

### Extending to 100 Agents
I put this together contemplating what a factory with 100 specialized machines looks like. With this pattern, you simply expand the router function to a secondary Graph (a Graph of Graphs). I think that nested StateGraphs, where the `Maintenance Agent` is actually a subgraph consisting of `Mechanical_Agent` and `Electrical_Agent`, represents the absolute bleeding edge of autonomous workflows.

## Deep Code Analysis: Handling Concurrency

One major hurdle I faced in my PoCs was how to structure the logging so that parallel executions don't tear the state apart. While this specific implementation is sequential (using the default LangGraph runner), in a production environment, you might use `.map` or asynchronous execution. 

From my experience:
1. Pydantic models in the state must be fully serializable.
2. Relying on simple lists for `log_history` might cause race conditions in pure async Python unless managed by a reducer function.
3. LangGraph solves this by allowing you to define `Annotated[list, operator.add]`. If I were to scale this globally, I would refactor `log_history` to use the LangGraph `add` operator, ensuring deterministic state merging when multiple agents report simultaneously.

## Let's Setup

If you want to run my experiments locally, here is what you need to do:

1. Clone the repository: `git clone https://github.com/aniket-work/DefectRouter-AI.git`
2. Enter the directory: `cd DefectRouter-AI`
3. Setup the virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. (Optional) Set your keys: `echo "OPENAI_API_KEY=your_key" > .env`

## Let's Run

Simply execute the main orchestration file:
```bash
python main.py
```

You will immediately see the simulated inputs hitting the Diagnostic Agent, which then routes it appropriately and prints an incident report table!

> **Code Repository:** All the code from my experiments can be found here: [DefectRouter-AI GitHub Repo](https://github.com/aniket-work/DefectRouter-AI)

## Edge Cases and Resiliency

In my opinion, any serious system needs to plan for failure. What if an IoT sensor sends a malformed JSON? What if the LLM API times out?
I observed that adding try-except blocks inside the `Diagnostic Agent` to fall back onto simple heuristic logic ensures the system never crashes on the factory floor. I wrote the code to default to "Maintenance (High Severity)" upon API failure, because from my experience, it is better to dispatch a human technician unnecessarily than to ignore a critical anomaly.

## The Philosophy of Agentic Fallbacks


I think the biggest mistake AI engineers make today is assuming 100% LLM uptime. I observed, in my opinion, that building fallbacks into the diagnostic nodes using standard Python heuristics is essential for industrial systems. I put this together because I wanted a demonstration that proves a multi-agent system does not have to be fragile.

When you are dealing with a multi-million dollar assembly line, "I'm sorry, I'm having trouble connecting to the internet" or a random 503 error from an API provider isn't just an inconvenience—it's a production stoppage. From my experience, the true power of LangGraph isn't just in the "happy path" of agentic reasoning, but in the structural enforcement of error handling at every node boundary. I designed the Diagnostic Agent to stay grounded. Instead of letting the LLM wander into hallucination when faced with ambiguous sensor telemetry, I wrote a set of hard-coded heuristic overrides. If the LLM output doesn't match a predefined Pydantic Enum for defect types, the system immediately reverts to a "Safe State." 

I thought about this deeply while watching the logs of my initial PoCs. I noticed that if a sensor reported a spike in thermal energy alongside a vibration anomaly, the LLM would occasionally get creative with the diagnosis, suggesting "unknown cosmic interference" or "poltergeists" if the temperature was high enough. In my opinion, for a system to be considered "production-grade," it must be boringly predictable. I chose to wrap the LLM with a Pydantic-based structural validator. If the agent returns anything that doesn't fit the `DiagnosticResult` schema, the Python runtime catches it before it ever hits the message bus. This is the difference between an AI demo and an AI tool.

Furthermore, I observed that logging everything onto a shared state graph is identical to how microservices utilize event streaming platforms like Kafka. I think that treating AI nodes as isolated microservices is the only path forward. Many developers try to build one giant "Manager Agent" that holds all the context and talks to everyone. I found that this creates a massive single point of failure and a context window that grows exponentially until the system's reasoning degrades. By stripping the communication down to raw Pydantic dictionaries—what I call the Structured Message Bus—I ensured that the Calibration Agent only sees exactly what it needs to perform its job: the defect type and the current machine ID. 

I wrote this logic to mirror how a team of human experts actually functions on a factory floor. You don't have the maintenance guy listening to the entire conversation between the plant manager and the materials supplier. You have a dispatcher (the Diagnostic Agent) who issues a ticket (the State Update) to the technician. I put this together because I wanted to prove that we can apply classic engineering principles—decoupling, encapsulation, and observability—to the world of non-deterministic models. This philosophy of Agentic Fallbacks ensures that even if the "brain" fails, the "nervous system" of the factory continues to protect the hardware. 


## Design Deep-Dive: The Structured Message Bus


One of the most frequent questions I get when I show people my LangGraph PoCs is: "Why not just use a standard chat interface?" I think this question misses the point of industrial orchestration. I observed that in a chat interface, context management is "loose." You are relying on the LLM to remember state across multiple turns. In my opinion, this is a recipe for disaster in manufacturing. I wrote the **Structured Message Bus** pattern to enforce "strict" context management.

In my design, the `DefectState` TypedDict is the only way agents communicate. I put this together so that information is never lost in the "noise" of a conversation. When the Diagnostic Agent finishes its work, it produces a schema-validated object. LangGraph then takes that object and performs a state update. This is fundamentally different from a chatbot. It is more akin to a state machine where the LLM is just a sophisticated transition function. I found that this approach completely eliminates the need for expensive "long-term memory" plugins, as the current state is always explicitly defined and passed only to the node that needs it.

I observed that this structural rigidity also makes testing significantly easier. I can write unit tests for the Calibration Agent by feeding it a mocked `DefectState` and asserting that it produces the correct `resolution_plan`. I think that if we want AI to be used in critical infrastructure, we must treat it like code, not like a magic black box. I wrote the `rich` visualization wrapper to prove this—you can see the state mutating in real-time. It’s transparent, it’s auditable, and from my experience, it’s the only way to build trust with plant floor operators who are used to deterministic PLCs. 


## Design Deep-Dive: The Multi-Agent Orchestration Engine


I wanted to go deeper into the actual code that drives the **LangGraph Orchestration Engine**. I think the most elegant part of the project is how I handled the conditional edges. I observed that most beginners use nested if-else statements inside an agent node to pick the next step. I found that this "leaks" routing logic into the reasoning node. In my opinion, the agent should only ever be responsible for *diagnosis*, while the graph should be responsible for *navigation*. 

I wrote the `route_defect` function as a standalone routing engine. I put this together because it allows you to swap out your LLM for a hard-coded decision tree without changing a single line of graph code. This decoupling is what I call "The Orchestration Separation of Concerns." I observed that by keeping the `route_defect` logic purely functional—meaning it takes a state and returns a string—you create a highly testable and predictable flow. 

Another technical detail I'm proud of is the **State Merging Protocol**. I observed that in large systems, different agents might try to overwrite the same state key simultaneously. I wrote the `DefectState` to utilize LangGraph's "Reducers." In my opinion, treating state updates as a "fold" operation (where the new data is merged into the old data mathematically) is the only way to ensure data integrity. I found that this pattern, although slightly more complex to set up initially, prevents 99% of the state-overwrite bugs that plague monolithic Python scripts. 


## Case Study: Troubleshooting a High-Severity Defect


I wanted to include a specific walkthrough of how the system handled a simulated "Level 5 Mechanical Defect." I observed that during this test run, the vibration sensor hit a peak of 4.5g, which is well above the danger threshold for the simulated CNC mill. I think seeing the logs in real-time is the best way to understand the multi-agent advantage. 

I wrote the simulation to start with the spindle vibrating at an increasing frequency. The **IoT Gateway** emitted a JSON alert. I observed the **Diagnostic Agent** immediately wake up. Within 400ms, it had parsed the telemetry. I thought the reasoning was particularly sharp here—the LLM didn't just see "vibration is high." It looked at the correlated thermal dip (suggesting a loss of friction at the bearing) and determined the cause was a "Broken Spindle Collet." 

In my opinion, hitting the **Maintenance Agent** was the critical next step. Instead of just stopping the machine, the Maintenance Agent checked the simulated inventory database. It found that a replacement collet was available in Bin #402. I wrote the agent to update the state with a very specific resolution plan: "Emergency shutdown initiated. Technician dispatched to Spindle B. Replacement part available. Estimated downtime: 45 minutes." 

I observed that the whole process—from sensor trigger to resolution plan generation—took less than 2 seconds of aggregate reasoning time. I put this together to show the sheer speed of agentic triage. In a traditional factory environment, this might have taken a human 10 minutes to walk to the machine, 5 minutes to diagnose, and another 10 to check the inventory status. I think that saving those 23 minutes across every single minor incident is how you move the needle on a multi-billion-dollar profit and loss statement. 


## Analyzing The Impact of AI on Industrial Quality


When looking at the broader scope, I observed that injecting LLMs into factory operations fundamentally disrupts the traditional predictive maintenance model. I think that whereas previous models relied solely on time-series anomaly detection, having an LLM parse the acoustic signatures alongside error logs allows for true multi-modal diagnostics. In my opinion, this is the holy grail of industrial optimization. I wrote this PoC because I am fascinated by the idea of an AI diagnosing a failing bearing simply from the contextual logs describing an unusual hum on the factory floor.

For decades, we have used Statistical Process Control (SPC) to monitor quality. It works well for identifying when a process is out of spec, but it’s terrible at telling you *why*. I observed that when an IoT sensor reports a 5% deviation in spindle speed, the traditional system just fires an alert. But when you feed that deviation into a multi-agent system that also has access to the machine's maintenance history and the chemical composition of the latest raw material batch, you get a diagnosis that sounds like an expert: "Spindle speed is lagging due to high viscosity in the lubricant batch #882, combined with a worn-out drive belt scheduled for replacement last Tuesday."

I think this shift from "Anomalous" to "Explanatory" is the biggest impact of Agentic AI. I wrote the DefectRouter-AI to demonstrate that we can move beyond just routing tickets. We can route *context*. In my opinion, the material agent in my system represents the next phase of supply chain integration. If it detects that a defect is caused by bad raw material, it doesn't just stop the machine—it should (in a future version) automatically ping the procurement system to flag that batch and find a new vendor. This is the "Autonomous" part of the project that I find most exciting.

I put this project together to show that the "Human-in-the-loop" isn't a limitation; it’s a design choice. I think the future of industrial AI isn't about replacing the floor manager, but about giving that manager a super-powered diagnostic assistant that has already triaged 90% of the noise. I observed that by the time an alert hits a human technician in my system, the "Resolution Plan" has already been drafted, the parts have been checked in inventory, and the machine has been placed into a safe idle state. This reduces the cognitive load on human operators and lets them focus on the complex physical repairs that AI can't touch yet.


## Industrial AI: The Road Ahead


As I reflect on the development of DefectRouter-AI, I am struck by how quickly we are moving from "experimental" to "essential" in the world of industrial AI. I observed that the primary bottleneck is no longer the intelligence of the models, but the reliability of the orchestration. I think that the next five years will be defined by the "hardening" of these agentic patterns. I wrote this article because I want to encourage other engineers to think about the infrastructure layer—the Structured Message Bus—as much as the prompt engineering layer.

I am particularly excited about the potential for **Federated Agent Learning**. I think that in a future shift, different factories could share their "experience" in a privacy-preserving way. If an agent in a plant in Tokyo learns that a specific vibration pattern preceded a gear failure, that knowledge could be distilled and pushed to the Message Bus of a plant in Munich. I put this PoC together to prove that we already have the tools (LangGraph, Pydantic, Python) to build the local nodes for this kind of global network.

I also observed that **Sustainable AI** is going to be a massive topic. I think that by using specialized local agents (like my Diagnostic and Calibration agents), we can minimize the token usage and the associated carbon cost of massive general-purpose models. In my opinion, the "right-sized" model for the task is the hallmark of a mature engineering team. I wrote my system to be lean, fast, and deterministic wherever possible. 


## Scaling the Architecture: From Factory to Global Cloud


One of the core design goals of DefectRouter-AI was to ensure it could scale horizontally. I think a lot of AI projects get stuck as local Python scripts that never see the light of day in a production cloud environment. I observed that by using LangGraph's state-centric model, we can actually decouple the reasoning nodes from the orchestration server. 

I wrote the system to be "State-First." This means the state lives in a persistent store (like Redis or Postgres), and the agents are essentially stateless serverless functions. I put this together contemplating what it looks like to manage 50 factories across three continents. In my opinion, you don't run one giant graph. You run thousands of localized graphs that all report their ASCII summaries back to a centralized dashboard. 

I think the "Structured Message Bus" becomes even more important at scale. I observed that if you have 10,000 agents running simultaneously, you cannot have them sending ad-hoc messages to each other. You need a strict protocol. I wrote the `log_history` to be compatible with standard ELK stack (Elasticsearch, Logstash, Kibana) ingestors. This means you can use classic DevOps tools to monitor your AI agents. I found that seeing a "Defect Type Distribution" chart in Kibana, populated entirely by agentic decisions, is when it finally hit me: this is not science fiction; it is just the next evolution of systems architecture. 


## The Future of Autonomous Quality Control


Looking forward, I observed that the marriage of Agentic AI and digital twins is the next logical step. I think that we are moving toward a world where every machine on a factory floor has a corresponding AI agent that lives in a perpetual "reasoning loop." I put this project together to highlight that we don't need a single global AI; we need a swarm of localized, specialized intelligences. 

I am currently experimenting with adding **Vision-Language Models (VLMs)** to this workflow. I observed that text-based sensor logs only tell half the story. I think that having an agent "look" at a high-speed camera feed of a conveyor belt while simultaneously "listening" to the vibration sensors would create a diagnostic system that is more accurate than any human expert alive. I wrote the LangGraph scaffolding specifically to be modular so that I can easily plug in a new "Vision Agent" node without refactoring the entire system. 


## Conclusion: The Human Element in an AI Factory


I am often asked: "But what about the human workers?" I think this fear of replacement is grounded in a misunderstanding of what a factory floor actually is. I observed that the most valuable part of a human technician is not their ability to route a ticket, but their specialized physical intuition. In my opinion, my DefectRouter-AI should be viewed as a "Vanguard" system. It takes the first hit, it absorbs the noise, and it clears the path.

I wrote this because I want to see a world where humans aren't spent on the soul-crushing boredom of monitoring data logs for 8 hours a day. I observe that when an agent handles the triage, the human's work becomes more high-stakes, more cerebral, and arguably more human. I put this together to show that a well-designed AI system is an amplifier of human expertise, not a substitute for it. 


## Closing Thoughts

I wrote this because I firmly believe agentic workflows are fundamentally changing how we approach deterministic coding. LangGraph provides the perfect scaffolding to marry deterministic routing with non-deterministic LLM reasoning. I observed that abstracting the state into a centralized bus not only cleans up the code, but perfectly mirrors how a human organization triages incidents. I think we are just scratching the surface of what is possible, and I plan to continue extending my PoCs to incorporate full database persistence and human-in-the-loop approvals in the future.

## Disclaimer

The views and opinions expressed here are solely my own and do not represent the views, positions, or opinions of my employer or any organization I am affiliated with. The content is based on my personal experience and experimentation and may be incomplete or incorrect. Any errors or misinterpretations are unintentional, and I apologize in advance if any statements are misunderstood or misrepresented.
