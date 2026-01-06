import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from config.env import setup_env
from agents.root_team_agent import create_root_agent
from runtime.sessions import init_session
from runtime.runner import create_runner, call_agent_async

setup_env()

root_agent = create_root_agent()

async def run_team_conversation():
    print("\n--- Testing Agent Team Delegation ---")
    session_service = InMemorySessionService()
    APP_NAME = "weather_tutorial_agent_team"
    USER_ID = "user_1_agent_team"
    SESSION_ID = "session_001_agent_team"

    session = await init_session(session_service, APP_NAME, USER_ID, SESSION_ID)
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    root_agent = globals()['root_agent']
    runner_agent_team = create_runner(root_agent, APP_NAME, session_service)
    # print(f"Runner created for agent '{root_agent.name}'.")

    # --- Interactions using await (correct within async def) ---
    await call_agent_async(query = "Hello there!",
                            runner=runner_agent_team,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "What is the weather in New York?",
                            runner=runner_agent_team,
                            user_id=USER_ID,
                            session_id=SESSION_ID)
    await call_agent_async(query = "Thanks, bye!",
                            runner=runner_agent_team,
                            user_id=USER_ID,
                            session_id=SESSION_ID)

async def test_individual_agents():
    """Test each agent individually to ensure they work correctly"""
    print("\n=== Testing Individual Agents ===\n")
    
    session_service = InMemorySessionService()
    
    # Test greeting agent
    print("--- Testing Greeting Agent ---")
    greeting_agent = create_greeting_agent()
    greeting_runner = create_runner(greeting_agent, "test_greeting", session_service)
    session = await init_session(session_service, "test_greeting", "test_user", "session_greeting")
    await call_agent_async("Hello there!", greeting_runner, "test_user", "session_greeting")
    
    print("\n--- Testing Weather Root (Direct) ---")
    # Test root agent with weather query (without going through team)
    root = create_root_agent()
    root_runner = create_runner(root, "test_root", session_service)
    session2 = await init_session(session_service, "test_root", "test_user2", "session_root")
    await call_agent_async("What is the weather in New York?", root_runner, "test_user2", "session_root")

if __name__ == "__main__": # Ensures this runs only when script is executed directly
    print("Executing using 'asyncio.run()' (for standard Python scripts)...")
    try:
        # This creates an event loop, runs your async function, and closes the loop.
        asyncio.run(run_team_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")

else:
     # This message prints if the root agent variable wasn't found earlier
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")
