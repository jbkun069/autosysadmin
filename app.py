import streamlit as st
import ollama
import re
import json
import os
from tools import tool_registry
from prompts import get_system_prompt

# --- CONFIGURATION ---
MODEL_NAME = "phi3"
HISTORY_FILE = "chat_history.json"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Auto-SysAdmin AI", 
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Auto-SysAdmin Agent")
st.caption("A Local Neuro-Symbolic Agent | Clean Interface")

# --- 1. PERSISTENCE FUNCTIONS ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(st.session_state.messages, f)

# --- 2. SESSION STATE SETUP ---
if "messages" not in st.session_state:
    saved_msgs = load_history()
    if saved_msgs:
        st.session_state.messages = saved_msgs
    else:
        st.session_state.messages = [
            {"role": "system", "content": get_system_prompt()}
        ]

# --- 3. HELPER FUNCTIONS ---
def parse_action(ai_msg):
    match = re.search(r"Action:\s*(\w+)", ai_msg, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def run_react_loop(user_input):
    # 1. Add User Message & Save
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_history()
    
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Agent Loop
    with st.chat_message("assistant"):
        # The 'status_placeholder' and 'Agent is thinking' text have been removed.
        
        last_action = None
        
        for turn in range(5):
            # A. Generate Thought
            response = ollama.chat(model=MODEL_NAME, messages=st.session_state.messages)
            ai_msg = response['message']['content']
            
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            save_history()
            
            # B. Check Tools
            tool_name = parse_action(ai_msg)
            
            if tool_name:
                # Loop Breaker Logic
                if tool_name == last_action:
                    st.session_state.messages.append({"role": "user", "content": "Error: You are repeating. Answer now."})
                    break
                
                last_action = tool_name
                
                # We still show the action so the user knows why there is a pause
                st.info(f"🛠️ **Executing:** `{tool_name}`...")
                
                if tool_name in tool_registry:
                    try:
                        # C. Execute
                        tool_result = tool_registry[tool_name]()
                        st.success(f"✅ **Observation:**\n\n```\n{tool_result}\n```")
                        
                        # D. Feedback
                        st.session_state.messages.append({"role": "user", "content": f"Observation: {tool_result}"})
                        save_history()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        break
                else:
                    st.error(f"❌ Tool `{tool_name}` not found.")
                    st.session_state.messages.append({"role": "user", "content": f"Error: Tool {tool_name} not found."})
                    break
            else:
                # E. Final Answer
                st.markdown(ai_msg)
                break

# --- 4. RENDER HISTORY ---
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    
    if msg["role"] == "user":
        if "Observation:" in msg["content"]:
            with st.chat_message("assistant"):
                 st.success(f"✅ **System Check:**\n\n{msg['content']}")
        else:
             with st.chat_message("user"):
                st.markdown(msg["content"])
    
    elif msg["role"] == "assistant":
        if "Action:" in msg["content"]:
            match = re.search(r"Action:\s*(\w+)", msg["content"], re.IGNORECASE)
            tool_name = match.group(1) if match else "Unknown Tool"
            with st.chat_message("assistant"):
                st.info(f"🛠️ **Executing:** `{tool_name}`...")
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

# --- 5. INPUT ---
if prompt := st.chat_input("Ask your SysAdmin..."):
    run_react_loop(prompt)