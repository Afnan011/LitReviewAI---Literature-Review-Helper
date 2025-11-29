from google.adk.agents import Agent

root_agent = Agent(
    name="MyAgent",
    instruction="You are a helpful assistant.",
    model="gemini-2.5-flash-lite"
)
