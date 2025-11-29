import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import litreview_agent.agent...")
    from litreview_agent.agent import root_agent
    print("Successfully imported root_agent!")
    print(f"Root agent type: {type(root_agent)}")
    print(f"Root agent name: {root_agent.name}")
except Exception as e:
    print(f"FAILED to load agent: {e}")
    import traceback
    traceback.print_exc()
