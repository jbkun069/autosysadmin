# Auto-SysAdmin: Local Agentic AI

An autonomous AI agent designed to investigate and diagnose local computer issues (CPU, RAM, Disk) by executing sandboxed Python scripts without requiring internet access.

## Technology Stack

*   **Core Language:** Python 3.10+
*   **Inference Engine:** **Ollama** (Local Inference Server)
*   **Model:** **Phi-3 Mini** (3.8B Parameters, 4-bit Quantized)
*   **System Tools:** `psutil` (Cross-platform system monitoring)
*   **Architecture:** **ReAct** (Reasoning + Acting) Loop

## Architecture Overview

This project implements a **Neuro-Symbolic** architecture, combining a probabilistic Large Language Model (the "Brain") with deterministic Python code (the "Hands"). The agent operates in a loop:

1.  **Reason:** The LLM analyzes a user query (e.g., "My PC is slow") and determines the next logical step.
2.  **Act:** It decides to use a specific tool by outputting a trigger string, such as `Action: check_ram`. The Python runtime intercepts this string, pauses the AI, and executes the corresponding function from a pre-approved list.
3.  **Observe:** The real system data returned from the tool is formatted and fed back into the AI's context window as an observation.
4.  **Synthesize:** The AI uses this new information to either continue the investigation with another tool or generate a final, data-grounded answer for the user.

## Key Features

*   **Offline Operation:** Runs entirely on a local consumer-grade CPU, requiring no GPU or paid cloud APIs.
*   **Grounding & Hallucination Resistance:** The agent is architected to rely on real-time data from system tools. It cannot invent system statistics; it must measure them.
*   **Autonomous Tool Use:** Implements a custom function-calling protocol using simple, reliable Regex parsing, allowing the LLM to trigger actions.
*   **Sandboxed Execution:** The agent's capabilities are strictly limited to the functions explicitly whitelisted in the `tool_registry`, ensuring it cannot perform unauthorized actions.

## Getting Started

### Prerequisites

*   Python 3.10 or newer.
*   [Ollama](https://ollama.com) installed and running.
*   The required model pulled via Ollama:
    ```bash
    ollama pull phi3
    ```

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/auto-sysadmin.git
    cd auto-sysadmin
    ```
2.  Create and activate a virtual environment:
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

The project includes two interfaces.

#### Web UI (Recommended)

Launch the Streamlit-based graphical interface for an interactive chat experience.
```bash
streamlit run app.py

Command-Line Interface
```bash
python main.py