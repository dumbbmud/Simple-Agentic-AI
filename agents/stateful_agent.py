from google.adk.agents import Agent
from config.models import MODEL_GEMINI_2_0_FLASH
from tools.weather import get_weather_stateful
from agents.smalltalk_agents import create_greeting_agent, create_farewell_agent

def create_stateful_root_agent():
    return Agent(
        name="weather_agent_stateful",
        model=MODEL_GEMINI_2_0_FLASH,
        instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                    "The tool will format the temperature based on user preference stored in state. "
                    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather requests, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[create_greeting_agent(), create_farewell_agent()],
        output_key="last_weather_report"
    )
