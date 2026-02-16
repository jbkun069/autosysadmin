import ollama # type: ignore
import re
from tools import tool_registry
from prompts import get_system_prompt

# --- CONFIGURATION ---
MODEL_NAME = "phi3"  

def think_and_act(history):
    """
    The core function that runs ONE turn of the conversation.
    Returns: (text_response, stop_signal)
    """
    print("\n[Brain] Thinking...")
    
    response = ollama.chat(model=MODEL_NAME, messages=history)
    ai_msg = response['message']['content']
    
    return ai_msg

def parse_action(ai_msg):
    """
    Scans the AI message for 'Action: tool_name'.
    Returns the tool name if found, otherwise None.
    """
    
    match = re.search(r"Action:\s*(\w+)", ai_msg, re.IGNORECASE)
    if match:
        return match.group(1) 
    return None

def run():
    print("--- AUTO-SYSADMIN AGENT ONLINE ---")
    print("Type 'exit' to quit.\n")


    conversation_history = [
        {'role': 'system', 'content': get_system_prompt()}
    ]

    while True:
       
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Shutting down agent.")
            break
            
       
        conversation_history.append({'role': 'user', 'content': user_input})

        last_action = None
      
        for turn in range(5):
            
            
            ai_msg = think_and_act(conversation_history)
            
            tool_name = parse_action(ai_msg)
            
            if tool_name:
                
                if tool_name == last_action:
                    error_msg = "Error: You are repeating the same action. Please provide a final answer based on the data you already have."
                    conversation_history.append({'role': 'assitant', 'content': ai_msg})
                    conversation_history.append({'role': 'user', 'content': error_msg})
                    print("[System] Loop detected. Forcing AI to stop.")
                    continue
                
                last_action = tool_name
                
                print(f"[Agent] Decided to run: {tool_name}")
                
                if tool_name in tool_registry:
                    try:
                        tool_output = tool_registry[tool_name]()
                        print(f"[Tool Output] {tool_output}")
                        
                        conversation_history.append({'role': 'assistant', 'content': ai_msg})
                        conversation_history.append({'role': 'user', 'content': f"Observation: {tool_output}"})
                        continue 
                    except Exception as e:
                        conversation_history.append({'role': 'user', 'content': f"Error: Tool failed with {e}"})
                else:
                    
                    msg = f"Error: Tool '{tool_name}' does not exist. Do not try to use it again. Answer based on your knowledge or ask for help."
                    conversation_history.append({'role': 'user', 'content': msg})
                    print(f"[Error] AI hallucinated tool: {tool_name}")
            else:
               
                conversation_history.append({'role': 'assistant', 'content': ai_msg})
                print(f"\n[AI] {ai_msg}")
                break

if __name__ == "__main__":
    run()