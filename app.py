import streamlit as st # type: ignore
import ollama # type: ignore
import re
import json
import os
from tools import tool_registry
from prompts import get_system_prompt

MODEL_NAME = "phi3"
HISTORY_FILE = "chat_history.json"

st.set_page_config(page_title="Auto-SysAdmin AI", page_icon="🤖")
st.title("🤖 Auto-SysAdmin Agent")
st.caption("A Local Neuro-Symbolic Agent running on Phi-3")

def load_history():
    """Loads chat history from a local JSON file if it exists."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return [] 
    return []

def save_history():
    """Saves the current session state to a local JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(st.session_state.messages, f)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": get_system_prompt()}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def parse_action(ai_msg):
    match = re.search(r"Action:\s*(\w+)", ai_msg, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def run_react_loop(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🧠 *Agent is thinking...*")

        for turn in range(5):
            response = ollama.chat(model=MODEL_NAME, messages=st.session_state.messages)
            ai_msg = response['message']['content']
            
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            
            tool_name = parse_action(ai_msg)
            
            if tool_name:
                message_placeholder.empty()
                st.info(f"🛠️ **Agent Decision:** Executing `{tool_name}`...")
                
                if tool_name in tool_registry:
                    try:
                        tool_result = tool_registry[tool_name]()
                        st.success(f"✅ **Observation:**\n\n```\n{tool_result}\n```")
                        st.session_state.messages.append({"role": "user", "content": f"Observation: {tool_result}"})
                        message_placeholder = st.empty()
                        message_placeholder.markdown("🧠 *Analyzing data...*")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        st.session_state.messages.append({"role": "user", "content": f"Error: {e}"})
                        break
                else:
                    st.error(f"❌ Error: Tool {tool_name} not found.")
                    break
            else:
                message_placeholder.empty()
                st.markdown(ai_msg)
                break


if prompt := st.chat_input("Ask about your computer (e.g., 'Check RAM')..."):
    run_react_loop(prompt)
