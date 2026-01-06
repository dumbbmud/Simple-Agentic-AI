from google.adk.tools.tool_context import ToolContext

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

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized not in mock_weather_db:
        return {"status": "error", "error_message": f"No data for {city}"}

    temp_c = mock_weather_db[city_normalized]["temp_c"]
    condition = mock_weather_db[city_normalized]["condition"]

    if preferred_unit == "Fahrenheit":
        temp = (temp_c * 9/5) + 32
        unit = "°F"
    else:
        temp = temp_c
        unit = "°C"

    tool_context.state["last_city_checked_stateful"] = city

    return {
        "status": "success",
        "report": f"The weather in {city.capitalize()} is {condition} with a temperature of {temp:.0f}{unit}."
    }
