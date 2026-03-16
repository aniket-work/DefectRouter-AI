# 🏭 DefectRouter-AI
**Autonomous Manufacturing Quality Control & Triaging System**

<div align="center">
  <img src="https://raw.githubusercontent.com/username/repo/main/images/title-animation.gif" alt="DefectRouter-AI Terminal Animation" width="900"/>
</div>

---

## 📌 Overview

**DefectRouter-AI** is an advanced, production-grade multi-agent system designed to handle real-world manufacturing anomalies. Built on **LangGraph**, it serves as an autonomous quality control coordinator for smart factory floors. When IoT sensors detect acoustic, thermal, or vibration anomalies on the assembly line, the system rapidly diagnoses the root cause and dynamically routes the issue to specialized agents using a **Structured Message Bus** and **Persistent Shared State**.

This experimental Proof-of-Concept highlights how modern AI agent orchestration can solve complex predictive maintenance and quality assurance challenges.

## 🏗️ System Architecture

<div align="center">
  <img src="https://raw.githubusercontent.com/username/repo/main/images/architecture_diagram.png" alt="Architecture Diagram" width="800"/>
</div>

The system features an **Advanced Communication Protocol (ACP)** simulation, providing a hyper-realistic terminal interface to visualize the inter-agent reasoning and routing processes.

## 🚀 Key Features

- **Multi-Agent Coordination:** A central Diagnostic Agent assesses incoming IoT payload streams and routes incidents to specialist agents (Maintenance, Calibration, Material).
- **Persistent Shared State:** All agents read from and mutate a centralized `DefectState` graph memory, tracking incident progress without disjointed communications.
- **Structured Message Bus:** Implements LangGraph edge routing to enforce a strict message and state update protocol.
- **ACP Logging Console:** Uses the `rich` library to beautifully visualize agent logic sequences, simulated API delays, and action resolutions.

## 🛠️ Tech Stack

- **Framework:** [LangGraph](https://python.langchain.com/v0.2/docs/langgraph/) & [LangChain](https://python.langchain.com/)
- **Language Model:** OpenAI (`gpt-4o-mini`)
- **State Management:** Pydantic `TypedDict` and BaseModel
- **Terminal UI:** [Rich](https://rich.readthedocs.io/en/stable/)

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/username/repo.git
   cd repo
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure the environment:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   *Note: DefectRouter-AI includes a fallback mock logic module if the API key is not provided, allowing you to view the ACP terminal simulation locally regardless.*

4. **Run the Agentic Simulation:**
   ```bash
   python main.py
   ```

## 🔄 How It Works

1. **Intake:** The system listens for an incoming sensor payload (e.g., `INC-88A92` with vibration/temp metrics).
2. **Diagnosis:** The `Diagnostic Agent` evaluates the metrics against heuristic thresholds or an LLM prompt.
3. **Routing:** Depending on the defect type (e.g., High Vibration), the incident is dispatched via the message bus securely.
4. **Resolution:** The `Maintenance Agent` kicks in, escalates a work order for physical inspection, updates the `DefectState`, and prints an ASCII summary report.

## 📜 Disclaimer

The views and opinions expressed in this project are solely my own and do not represent the views, positions, or opinions of my employer or any organization I am affiliated with. The content is based on my personal experience and experimentation and may be incomplete or incorrect. Any errors or misinterpretations are unintentional, and I apologize in advance if any statements are misunderstood or misrepresented. 

This repository is strictly an experimental PoC and not intended as production guidance.
