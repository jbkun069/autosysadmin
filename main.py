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

      
        for turn in range(5):
            
            
            ai_msg = think_and_act(conversation_history)
            
            
            conversation_history.append({'role': 'assistant', 'content': ai_msg})
            
           
            tool_name = parse_action(ai_msg)
            
            if tool_name:
                print(f"[Agent] Decided to run: {tool_name}")
                
                if tool_name in tool_registry:
                    try:
                        
                        tool_output = tool_registry[tool_name]()
                        print(f"[Tool Output] {tool_output}")
                        
                        observation_msg = f"Observation: {tool_output}"
                        conversation_history.append({'role': 'user', 'content': observation_msg})
                        
                        continue 
                        
                    except Exception as e:
                        print(f"[Error] Tool failed: {e}")
                        conversation_history.append({'role': 'user', 'content': f"Error: {e}"})
                else:
                    print(f"[Error] Tool '{tool_name}' not found in registry.")
                    conversation_history.append({'role': 'user', 'content': f"Error: Tool {tool_name} does not exist."})
            
            else:
                print(f"\n[AI] {ai_msg}")
                break

if __name__ == "__main__":
    run()