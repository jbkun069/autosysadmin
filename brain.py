import ollama # type: ignore
import time

MODEL = "phi3"  
def think(prompt):
    """
    Sends a prompt to the local LLM and returns the text response.
    """
    print(f"\n[Thinking] Sending query to {MODEL}...")
    start_time = time.time()
    
    response = ollama.chat(model=MODEL, messages=[
        {
            'role': 'user', 
            'content': prompt
        },
    ])
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"[Done] Inference took {duration:.2f} seconds.")
    
    return response['message']['content']

if __name__ == "__main__":
    user_query = "Explain the difference between RAM and ROM in one sentence."
    answer = think(user_query)
    
    print("-" * 50)
    print(f"AI: {answer}")
    print("-" * 50)