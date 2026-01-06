from typing import Optional
from google.adk.agents import Agent
from config.models import MODEL_GEMINI_2_0_FLASH


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


def create_greeting_agent():
    greeting_agent = Agent(
        model = MODEL_GEMINI_2_0_FLASH,
        name = "greeting_agent",
        instruction = "You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                    "Use the 'say_hello' tool to generate the greeting. "
                    "If the user provides their name, make sure to pass it to the tool. "
                    "Do not engage in any other conversation or tasks.",
        description = "Handles simple greetings and hellos using the 'say_hello' tool.",
        tools = [say_hello],
    )
    print(f"✅ Agent '{greeting_agent.name}' created using model '{greeting_agent.model}'.")

    return greeting_agent

def create_farewell_agent():
    farewell_agent = Agent(
        model = MODEL_GEMINI_2_0_FLASH,
        name = "farewell_agent",
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                    "Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools = [say_goodbye],
    )
    print(f"✅ Agent '{farewell_agent.name}' created using model '{farewell_agent.model}'.")
    return farewell_agent
