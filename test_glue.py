import ollama # type: ignore
from prompts import get_system_prompt

sys_prompt = get_system_prompt()

print("--- TESTING PROMPT COMPLIANCE ---")
print("Target Model: Phi-3 (Local)")

#Defining a test case that REQUIRES a tool
test_query = "I think my CPU is overheating. Can you check the usage?"
print(f"\nUser Query: {test_query}")

response = ollama.chat(model='phi3', messages=[
    {'role': 'system', 'content': sys_prompt},
    {'role': 'user', 'content': test_query}
])

answer = response['message']['content']

print(f"\nAI Response:\n{answer}")

print("\n--- DIAGNOSIS ---")
if "Action: check_cpu" in answer:
    print("SUCCESS: The AI attempted to use a tool.")
else:
    print("FAILURE: The AI just chatted instead of using a tool.")