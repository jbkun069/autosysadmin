from tools import tool_registry

print("--- DIAGNOSTIC TEST START ---")

for name, func in tool_registry.items():
    print(f"\n[Testing Tool]: {name}")
    try:
        result = func()
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"!!! ERROR !!! Tool {name} failed: {e}")

print("\n--- DIAGNOSTIC TEST END ---")