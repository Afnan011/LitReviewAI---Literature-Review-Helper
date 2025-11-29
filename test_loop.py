import asyncio
from google.adk.agents import LoopAgent, LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import Gemini
from google.genai import types

# Mock model that returns predictable responses
class MockModel:
    def __init__(self):
        self.counter = 0
        
    async def generate_content(self, prompt, **kwargs):
        self.counter += 1
        if "Evaluate" in prompt:
            if self.counter < 4: # Fail first time
                return types.GenerateContentResponse(
                    candidates=[types.Candidate(
                        content=types.Content(parts=[types.Part(text="Score: 5\nFeedback: Needs improvement.")])
                    )]
                )
            else: # Pass second time
                return types.GenerateContentResponse(
                    candidates=[types.Candidate(
                        content=types.Content(parts=[types.Part(text="Score: 9\nFeedback: Good job.")])
                    )]
                )
        else: # Synthesis
            return types.GenerateContentResponse(
                candidates=[types.Candidate(
                    content=types.Content(parts=[types.Part(text="Draft Review Content")])
                )]
            )

async def run_test():
    # synthesis = LlmAgent(name="Synthesis", model=MockModel(), instruction="Write review")
    # evaluation = LlmAgent(name="Evaluation", model=MockModel(), instruction="Evaluate review")
    
    # Since I can't easily mock the model in ADK's strict typing, I'll inspect the LoopAgent condition mechanism dynamically
    # instead of running a full mock.
    
    from google.adk.agents import LoopAgent
    print("Inspecting LoopAgent condition...")
    
    # Define a condition function
    def my_condition(agent, context):
        print(f"Condition check. Agent: {agent.name}")
        # Check last event?
        return False # Continue loop
        
    loop_agent = LoopAgent(
        name="TestLoop",
        sub_agents=[],
        condition=my_condition,
        max_iterations=2
    )
    
    print(f"LoopAgent created with condition: {loop_agent.condition}")
    print("Test successful if no error on creation.")

if __name__ == "__main__":
    asyncio.run(run_test())
