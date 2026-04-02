from google import genai # type: ignore
from google.genai import types # type: ignore
from tools import tool_registry, parse_action
from prompts import get_system_prompt
from config import MODEL_NAME, MAX_TURNS

client = genai.Client(http_options={'api_version': 'v1beta'})

def run():
    print("AUTO-SYSADMIN ONLINE")
    print("Type 'exit' to quit.\n")

    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=get_system_prompt(),
            temperature=0.1 
        )
    )

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        current_input = user_input
        
        for turn in range(MAX_TURNS):
            print(f"[Turn {turn + 1}/{MAX_TURNS}] Thinking...")
            
            try:
                response = chat.send_message(current_input)
                ai_msg = response.text
            except Exception as e:
                print(f"[Error] API Call Failed: {e}")
                break

            tool_name = parse_action(ai_msg)
            
            if tool_name and tool_name in tool_registry:
                print(f"[Agent] Action: {tool_name}")
                result = tool_registry[tool_name]()
                print(f"[Tool] Result: {result}")
                
                current_input = f"Observation: {result}"
                continue
            else:
                print(f"\n[AI] {ai_msg}")
                break

if __name__ == "__main__":
    run()