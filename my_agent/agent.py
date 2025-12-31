import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 

import warnings
warnings.filterwarnings("ignore") #ignores all warnings

import logging
logging.basicConfig(level=logging.ERROR)

from dotenv import load_dotenv
load_dotenv()

MODEL_GEMINI_2_0_FLASH = "gemini-2.5-flash"


# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='Answer user questions to the best of your knowledge',
# )

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # Starting with Gemini
MODEL_GROQ_LLAMA_INSTANT = "groq/llama-3.1-8b-instant"


weather_agent = Agent(
    name="weather_agent_v1",
    model=MODEL_GROQ_LLAMA_INSTANT, 
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_weather], # Pass the function directly
)

session_service = InMemorySessionService()

APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

async def init_session(session_service, app_name:str,user_id:str,session_id:str) -> InMemorySessionService:
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session

session = asyncio.run(init_session(session_service, APP_NAME,USER_ID,SESSION_ID))

# --- Runner ---
# Key Concept: Runner orchestrates the agent execution loop.
runner = Runner(
    agent=weather_agent, # The agent we want to run
    app_name=APP_NAME,   # Associates runs with our app
    session_service=session_service # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")

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


# We need an async function to await our interaction helper
async def run_conversation():
    await call_agent_async("What is the weather like in London?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # Expecting the tool's error message

    await call_agent_async("Tell me the weather in New York",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")

weather_agent_groq = None
runner_groq = None

MODEL_GROQ_LLAMA_INSTANT = "groq/llama-3.1-8b-instant"

try:
    weather_agent_groq = Agent(
        name="weather_agent_groq",
        model = LiteLlm(model=MODEL_GROQ_LLAMA_INSTANT),
        description="Provide weather information using Groq.",
        instruction="You are a helpful weather assistant powered by llama-3.1-8b-instant. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Clearly present successful reports or polite error messages based on the tool's output status. ",
        tools=[get_weather], 
    )
    print(f"Agent '{weather_agent_groq.name}' created using model llama-3.1-8b-instant.")

    session_service_groq = InMemorySessionService()

    APP_NAME_GROQ = "weather_tutorial_app_groq"
    USER_ID_GROQ = "user_1_groq"
    SESSION_ID_GROQ = "session_001_groq"

    session_groq = asyncio.run(init_session(session_service_groq, APP_NAME_GROQ,USER_ID_GROQ,SESSION_ID_GROQ))

    runner_groq = Runner(
        agent = weather_agent_groq,
        app_name=APP_NAME_GROQ,
        session_service= session_service_groq
    )

    print(f"Runner created for agent '{runner_groq.agent.name}'.")

    print("\n--- Testing GROQ Agent ---")

    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "What's the weather in Tokyo?",
    #                      runner=runner_groq,
    #                       user_id=USER_ID_GROQ,
    #                       session_id=SESSION_ID_GROQ))
    #     except Exception as e:
    #         print(f"An error occurred: {e}")


except Exception as e:
    print(f"❌ Could not create or run Groq agent 'llama-3.1-8b-instant'. Check API Key and model name. Error: {e}")

weather_agent_HF = None
runner_HF = None

MODEL_GROQ_LLAMA_VERSATILE = "groq/llama-3.3-70b-versatile"


#NOT HF BUT GROQ DIFFERENT MODEL!!
try:
    weather_agent_HF = Agent(
        name="weather_agent_HF",
        model=LiteLlm(model=MODEL_GROQ_LLAMA_VERSATILE),
        description="Provide weather information using hf. ",
        instruction="You are a helpful weather assistant powered by HuggingFace. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "DO NOT include step-by-step instructions. "
                    "When the user asks for the weather, call the get_weather tool and **ONLY return the weather report in plain text** or give polite error messages based on the tool's output status. ",
        tools=[get_weather], 
    )
    print(f"Agent '{weather_agent_HF.name}' created using model hf")

    session_service_HF = InMemorySessionService()

    APP_NAME_HF = "weather_tutorial_app_HF"
    USER_ID_HF = "user_1_HF"
    SESSION_ID_HF = "session_001_HF"

    session_HF= asyncio.run(init_session(session_service_HF, APP_NAME_HF,USER_ID_HF,SESSION_ID_HF))

    runner_HF = Runner(
        agent = weather_agent_HF,
        app_name=APP_NAME_HF,
        session_service= session_service_HF
    )

    print(f"Runner created for agent '{runner_HF.agent.name}'.")

    print("\n--- Testing HF Agent ---")

    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "What's the weather in Tokyo?",
    #                      runner=runner_HF,
    #                       user_id=USER_ID_HF,
    #                       session_id=SESSION_ID_HF))
    #     except Exception as e:
    #         print(f"An error occurred: {e}")


except Exception as e:
    print(f"❌ Could not create or run huggingFace agent huggingface/mistralai/Mistral-7B-Instruct-v0.2. Check API Key and model name. Error: {e}")

from typing import Optional 

def say_hello(name: Optional[str] = None) -> str:
    """Provides a simple greeting. If a name is provided, it will be used.

    Args:
        name (str, optional): The name of the person to greet. Defaults to a generic greeting if not provided.

    Returns:
        str: A friendly greeting message.
    """

    if name:
        greeting = f"Hello, {name}!"
        print(f"---Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!"
        print(f"--- TOol: say_hello called without a specific name (name_arg_value: {name}) ---")
    
    return greeting


def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

print("Greeting and Farewell tools defined.")


greeting_agent = None

try:
    greeting_agent = Agent(
        model = MODEL_GROQ_LLAMA_INSTANT,
        name = "greeting_agent",
        instruction = "You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description = "Handles simple greetings and hellos using the 'say_hello' tool.",
        tools = [say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")

except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({greeting_agent.model}). Error: {e}")


#---Farewell Agent

farewell_agent = None

try:
    farewell_agent = Agent(
        model = MODEL_GROQ_LLAMA_INSTANT,
        name = "farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools = [say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create Farewell agent. Check API Key ({farewell_agent.model}). Error: {e}")

root_agent = None
root_runner = None

if greeting_agent and farewell_agent and 'get_weather' in globals():
    root_agent_model = MODEL_GROQ_LLAMA_INSTANT

    weather_agent_team = Agent(
        name = "weather_agent_v2",
        model = root_agent_model,
        description="The main coordinator agent. Handles weather requests and delegates greetings/farewells to specialists.",
        instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                    "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                    "You have specialized sub-agents: "
                    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                    "If it's a weather request, handle it yourself using 'get_weather'. "
                    "For anything else, respond appropriately or state you cannot handle it.",
        tools=[get_weather],
        sub_agents=[farewell_agent, greeting_agent]
    )
    print(f"✅ Root Agent '{weather_agent_team.name}' created using model '{root_agent_model}' with sub-agents: {[sa.name for sa in weather_agent_team.sub_agents]}")

else:
    print("❌ Cannot create root agent because one or more sub-agents failed to initialize or 'get_weather' tool is missing.")
    if not greeting_agent: print(" - Greeting Agent is missing.")
    if not farewell_agent: print(" - Farewell Agent is missing.")
    if 'get_weather' not in globals(): print(" - get_weather function is missing.")

root_agent_var_name = 'root_agent' # Default name from Step 3 guide
if 'weather_agent_team' in globals(): # Check if user used this name instead
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ Root agent ('root_agent' or 'weather_agent_team') not found. Cannot define run_team_conversation.")
    # Assign a dummy value to prevent NameError later if the code block runs anyway
    root_agent = None # Or set a flag to prevent execution

# Only define and run if the root agent exists
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # Define the main async function for the conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_team_conversation():
        print("\n--- Testing Agent Team Delegation ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # Or use InMemoryRunner
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{actual_root_agent.name}'.")

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

    # if __name__ == "__main__": # Ensures this runs only when script is executed directly
    #     print("Executing using 'asyncio.run()' (for standard Python scripts)...")
    #     try:
    #         # This creates an event loop, runs your async function, and closes the loop.
    #         asyncio.run(run_team_conversation())
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

else:
     # This message prints if the root agent variable wasn't found earlier
    print("\n⚠️ Skipping agent team conversation execution as the root agent was not successfully defined in a previous step.")



session_service_stateful = InMemorySessionService()
print("✅ New InMemorySessionService created for state demonstration.")


SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

async def init_session_stateful(session_service, app_name:str,user_id:str,session_id:str, initial_state) -> InMemorySessionService:
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=initial_state
    )
    print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session

session_stateful = asyncio.run(init_session_stateful(session_service_stateful, APP_NAME, USER_ID_STATEFUL, SESSION_ID_STATEFUL, initial_state))

print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

async def check_session(app_name, user_id_stateful, session_id_stateful):
    retrived_session = await session_service_stateful.get_session(app_name=app_name,
                                                         user_id=user_id_stateful,
                                                         session_id = session_id_stateful)
 
    return retrived_session

retrived_session = asyncio.run(check_session(APP_NAME, USER_ID_STATEFUL, SESSION_ID_STATEFUL))

if retrived_session:
    print(retrived_session.state)

else:
    print("Error: Could not retrieve session")

from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: get_weather_stateful called for {city} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")


# --- Redefine Greeting Agent (from Step 3) ---
greeting_agent = None
try:
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent",
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Error: {e}")

# --- Redefine Farewell Agent (from Step 3) ---
farewell_agent = None
try:
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Error: {e}")

# --- Define the Updated Root Agent ---
root_agent_stateful = None
runner_root_stateful = None # Initialize runner

# Check prerequisites before creating the root agent
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # Choose orchestration model

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # New version name
        model=root_agent_model,
        description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful], # Use the state-aware tool
        sub_agents=[greeting_agent, farewell_agent], # Include sub-agents
        output_key="last_weather_report" # <<< Auto-save agent's final weather response
    )
    print(f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key.")

    # --- Create Runner for this Root Agent & NEW Session Service ---
    runner_root_stateful = Runner(
        agent=root_agent_stateful,
        app_name=APP_NAME,
        session_service=session_service_stateful # Use the NEW stateful session service
    )
    print(f"✅ Runner created for stateful root agent '{runner_root_stateful.agent.name}' using stateful session service.")

else:
    print("❌ Cannot create stateful root agent. Prerequisites missing.")
    if not greeting_agent: print(" - greeting_agent definition missing.")
    if not farewell_agent: print(" - farewell_agent definition missing.")
    if 'get_weather_stateful' not in globals(): print(" - get_weather_stateful tool missing.")


if 'runner_root_stateful' in globals() and runner_root_stateful:
    # Define the main async function for the stateful conversation logic.
    # The 'await' keywords INSIDE this function are necessary for async operations.
    async def run_stateful_conversation():
        print("\n--- Testing State: Temp Unit Conversion & output_key ---")

        # 1. Check weather (Uses initial state: Celsius)
        print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
        await call_agent_async(query= "What's the weather in London?",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
        print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
        try:
            # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
            # NOTE: In production with persistent services (Database, VertexAI), you would
            # typically update state via agent actions or specific service APIs if available,
            # not by direct manipulation of internal storage.
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # Optional: You might want to update the timestamp as well if any logic depends on it
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state.get('user_preference_temperature_unit', 'Not Set')} ---") # Added .get for safety
        except KeyError:
            print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
        except Exception as e:
             print(f"--- Error updating internal session state: {e} ---")

        # 3. Check weather again (Tool should now use Fahrenheit)
        # This will also update 'last_weather_report' via output_key
        print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
        await call_agent_async(query= "Tell me the weather in New York.",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. Test basic delegation (should still work)
        # This will update 'last_weather_report' again, overwriting the NY weather report
        print("\n--- Turn 3: Sending a greeting ---")
        await call_agent_async(query= "Hi!",
                                runner=runner_root_stateful,
                                user_id=USER_ID_STATEFUL,
                                session_id=SESSION_ID_STATEFUL
                                )

    if __name__ == "__main__": # Ensures this runs only when script is executed directly
        print("Executing using 'asyncio.run()' (for standard Python scripts)...")
        try:
            # This creates an event loop, runs your async function, and closes the loop.
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"An error occurred: {e}")
    

    print("\n--- Inspecting Final Session State ---")
    final_session = asyncio.run(check_session(APP_NAME, USER_ID_STATEFUL, SESSION_ID_STATEFUL))
    if final_session:
        # Use .get() for safer access to potentially missing keys
        print(f"Final Preference: {final_session.state.get('user_preference_temperature_unit', 'Not Set')}")
        print(f"Final Last Weather Report (from output_key): {final_session.state.get('last_weather_report', 'Not Set')}")
        print(f"Final Last City Checked (by tool): {final_session.state.get('last_city_checked_stateful', 'Not Set')}")
        # Print full state for detailed view
        # print(f"Full State Dict: {final_session.state}") # For detailed view
    else:
        print("\n❌ Error: Could not retrieve final session state.")

else:
    print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")
    

