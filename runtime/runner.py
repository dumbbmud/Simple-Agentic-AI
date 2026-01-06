from google.genai import types
from google.adk.runners import Runner


# async def call_agent_async(query: str, runner, user_id: str, session_id: str):
def create_runner(root_agent, app_name, session_service):    
    runner = Runner( # Or use InMemoryRunner
            agent=root_agent,
            app_name=app_name,
            session_service=session_service
        )
    print(f"Runner created for agent '{root_agent.name}'.")
    return runner

async def call_agent_async(query: str, runner, user_id, session_id):
    print(f"\n>>> User Query:{query}")

    #prepares the user's message in ADK Format
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    #Default message
    final_response_text = "Agent did not produce a final response."

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
            #assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: #handle potential errors and escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    print(f"<<<Agent Response: {final_response_text}")

