import streamlit as st # type: ignore
import re
import json
import os
from dotenv import load_dotenv

from google import genai # type: ignore
from google.genai import types # type: ignore

from tools import tool_registry, parse_action
from prompts import get_system_prompt
from config import MODEL_NAME, HISTORY_FILE, MAX_TURNS

load_dotenv()

st.set_page_config(
    page_title="Auto-SysAdmin AI",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Auto-SysAdmin Agent")
st.caption("A Local Neuro-Symbolic Agent (Powered by Gemini)")


with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🗑️ Reset Memory", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": get_system_prompt()}
        ]
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.success("Memory cleared!")
        st.rerun()

    st.divider()
    st.markdown(f"**Model:** `{MODEL_NAME}`")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
                return []
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.messages, f)
    except IOError:
        pass

if "messages" not in st.session_state:
    saved_msgs = load_history()
    if saved_msgs:
        st.session_state.messages = saved_msgs
    else:
        st.session_state.messages = [
            {"role": "system", "content": get_system_prompt()}
        ]

def call_model():
    """Wraps Gemini API with error handling."""
    try:
        client = genai.Client(http_options={'api_version': 'v1beta'})
        gemini_history = []
        for msg in st.session_state.messages:
            if msg["role"] == "system":
                continue 
            
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append(
                types.Content(
                    role=role, 
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=gemini_history,
            config=types.GenerateContentConfig(
                system_instruction=get_system_prompt(),
                temperature=0.1 
            )
        )
        return response.text, None

    except Exception as e:
        return None, f"Gemini API Error: {e}"

def run_react_loop(user_input):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_history()

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        last_action = None

        for _ in range(MAX_TURNS):
            with st.spinner("Thinking..."):
                ai_msg, error = call_model()

            if error:
                st.error(f"❌ {error}")
                st.session_state.messages.pop()
                save_history()
                break

            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            save_history()

            tool_name = parse_action(ai_msg) if ai_msg else None

            if tool_name:
                if tool_name == last_action:
                    st.session_state.messages.append(
                        {"role": "user", "content": "Error: You are repeating. Provide your final answer now based on the data you already have."}
                    )
                    save_history()
                    ai_msg, error = call_model()
                    if ai_msg and not parse_action(ai_msg):
                        st.session_state.messages.append({"role": "assistant", "content": ai_msg})
                        save_history()
                        st.markdown(ai_msg)
                    break

                last_action = tool_name

                st.info(f"🛠️ **Executing:** `{tool_name}`...")

                if tool_name in tool_registry:
                    try:
                       
                        tool_result = tool_registry[tool_name]()
                        st.success(f"✅ **Observation:**\n\n```\n{tool_result}\n```")

                        st.session_state.messages.append(
                            {"role": "user", "content": f"Observation: {tool_result}"}
                        )
                        save_history()

                    except Exception as e:
                        error_msg = f"Tool execution failed: {e}"
                        st.error(f"❌ {error_msg}")
                        st.session_state.messages.append(
                            {"role": "user", "content": f"Error: {error_msg}"}
                        )
                        save_history()
                        break
                else:
                    st.error(f"❌ Tool `{tool_name}` not found. Available: {', '.join(tool_registry.keys())}")
                    st.session_state.messages.append(
                        {"role": "user", "content": f"Error: Tool '{tool_name}' does not exist. Available tools are: {', '.join(tool_registry.keys())}. Please use one of these exact names."}
                    )
                    save_history()
                    continue
            else:
                
                st.markdown(ai_msg)
                break

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    if msg["role"] == "user":
        if msg["content"].startswith("Observation:"):
            with st.chat_message("assistant"):
                st.success(f"✅ **System Check:**\n\n{msg['content']}")
        elif msg["content"].startswith("Error:"):
            continue
        else:
            with st.chat_message("user"):
                st.markdown(msg["content"])

    elif msg["role"] == "assistant":
        if parse_action(msg["content"]):
            match = re.search(r"Action:\s*(\w+)", msg["content"], re.IGNORECASE)
            tool_name = match.group(1) if match else "Unknown Tool"
            with st.chat_message("assistant"):
                st.info(f"🛠️ **Executing:** `{tool_name}`...")
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

if prompt := st.chat_input("Ask your SysAdmin..."):
    if prompt.strip():
        run_react_loop(prompt)
    else:
        st.toast("Please enter a message.", icon="⚠️")