import sys
import os
import inspect

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from google.adk.agents import LoopAgent
    print("Successfully imported LoopAgent")
    
    # Try Pydantic v2
    if hasattr(LoopAgent, 'model_fields'):
        print(f"Model Fields (v2): {LoopAgent.model_fields.keys()}")
    # Try Pydantic v1
    elif hasattr(LoopAgent, '__fields__'):
        print(f"Model Fields (v1): {LoopAgent.__fields__.keys()}")
    
except Exception as e:
    print(f"FAILED to inspect LoopAgent: {e}")
