try:
    from google.adk.agents import SequentialAgent
    print("SequentialAgent found in google.adk.agents")
except ImportError:
    print("SequentialAgent NOT found in google.adk.agents")
    try:
        from google.adk.agents.sequential_agent import SequentialAgent
        print("SequentialAgent found in google.adk.agents.sequential_agent")
    except ImportError as e:
        print(f"SequentialAgent not found at all: {e}")
