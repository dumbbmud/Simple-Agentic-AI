from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from config.models import *
from tools.weather import get_weather

def create_weather_agent():
    return Agent(
        name="weather_agent",
        model=LiteLlm(model=AGENT_MODEL),
        instruction="Use get_weather for city weather requests.",
        tools=[get_weather],
    )
