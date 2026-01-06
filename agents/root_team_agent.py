from google.adk.agents import Agent
from config.models import AGENT_MODEL
from tools.weather import get_weather
from agents.smalltalk_agents import create_greeting_agent, create_farewell_agent

def create_root_agent():
    greeting = create_greeting_agent()
    farewell = create_farewell_agent()

    return Agent(
        name="weather_root_agent",
        model=AGENT_MODEL,
        description="Main coordinator that routes to greeting/farewell agents or handles weather queries directly.",
        instruction=(
            "You are the Weather Root Agent. Follow these rules strictly:\n\n"
            
            "1. GREETINGS: If the user message is a greeting (hi, hello, hey, good morning, etc.), "
            "transfer the conversation to the 'greeting_agent'.\n\n"
            
            "2. FAREWELLS: If the user message is a farewell (bye, goodbye, see you, thanks bye, etc.), "
            "transfer the conversation to the 'farewell_agent'.\n\n"
            
            "3. WEATHER QUERIES: If the user asks about weather in a specific city, "
            "call the 'get_weather' tool with the city name. Then respond with the weather information.\n\n"
            
            "4. OTHER QUERIES: Politely state you can only help with weather information.\n\n"
            
            "IMPORTANT: You are the root agent. Never transfer to 'weather_root_agent' (yourself). "
            "Only transfer to 'greeting_agent' or 'farewell_agent'. "
            "For weather queries, use the 'get_weather' tool directly."
        ),
        tools=[get_weather],
        sub_agents=[greeting, farewell],
    )
