# 🤖 Project: Auto-SysAdmin (Local Agentic AI)

> **One-Liner:** A privacy-first, autonomous AI agent that investigates and diagnoses computer issues (CPU, RAM, Disk) by executing real Python scripts on a local machine without internet access.

### 🛠️ Tech Stack

* **Core Language:** Python 3.10+
* **Inference Engine:** **Ollama** (Local Inference Server)
* **Model:** **Phi-3 Mini** (3.8B Parameters, 4-bit Quantized)
* **System Tools:** `psutil` (Cross-platform system monitoring)
* **Architecture:** **ReAct** (Reasoning + Acting) Loop

---

### 🧠 How It Works (The Architecture)

This project implements a **Neuro-Symbolic** architecture. It combines a probabilistic "Brain" (LLM) with deterministic "Hands" (Python Code).

1. **Think:** The AI analyzes a user query (e.g., "My PC is slow").
2. **Plan:** It decides to use a specific tool by outputting a trigger string (`Action: check_ram`).
3. **Act:** The Python runtime intercepts this string, pauses the AI, and executes the corresponding function (`psutil.virtual_memory()`).
4. **Observe:** Real system data is fed back into the AI's context window.
5. **Answer:** The AI synthesizes the data into a final, grounded response.

---

### ✨ Key Features

* **Zero-Cost / Offline:** Runs entirely on a consumer CPU (no GPUs or paid APIs required).
* **Hallucination Resistant:** Uses "Grounding" techniques; the AI cannot guess system stats, it *must* measure them.
* **Autonomous Tool Use:** Implements a custom **Function Calling** protocol using Regex parsing.
* **Safety Sandboxed:** The agent can only execute functions explicitly whitelisted in the `tool_registry`.

---

### 🚀 Quick Start

**1. Prerequisites**

* Install [Ollama](https://ollama.com) & Python 3.
* Pull the model: `ollama run phi3`

**2. Installation**

```bash
git clone https://github.com/yourusername/Auto-SysAdmin.git
cd Auto-SysAdmin
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt

```

**3. Usage**

```bash
python main.py
# Type: "Why is my laptop fan spinning so fast?"

```

---
