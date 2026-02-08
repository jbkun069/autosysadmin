import streamlit as st # type: ignore
import ollama # type: ignore
import re
from tools import tool_registry
from prompts import get_system_prompt

MODEL_NAME = "phi3"

st.set_page_config(page_title="Auto-SysAdmin AI", page_icon="🤖")
st.title("🤖 Auto-SysAdmin Agent")
st.caption("A Local Neuro-Symbolic Agent running on Phi-3")

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
        with st.status("🧠 Agent is thinking...", expanded=True) as status:
            for turn in range(5):
                status.write("Generating thought...")
                response = ollama.chat(model=MODEL_NAME, messages=st.session_state.messages)
                ai_msg = response['message']['content']
                
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                
                tool_name = parse_action(ai_msg)
                
                if tool_name:
                    status.write(f"🛠️ Agent wants to use: **{tool_name}**")
                    
                    if tool_name in tool_registry:
                        try:
                            tool_result = tool_registry[tool_name]()
                            status.write(f"✅ Tool Output: {tool_result}")
                            st.session_state.messages.append(
                                {"role": "user", "content": f"Observation: {tool_result}"}
                            )
                        except Exception as e:
                            status.write(f"❌ Error: {e}")
                            st.session_state.messages.append(
                                {"role": "user", "content": f"Error: {e}"}
                            )
                            break
                    else:
                        status.write(f"❌ Error: Tool {tool_name} not found.")
                        break
                else:
                    status.update(label="✅ Answer Ready", state="complete", expanded=False)
                    st.markdown(ai_msg)
                    break

if prompt := st.chat_input("Ask about your computer (e.g., 'Check RAM')..."):
    run_react_loop(prompt)
