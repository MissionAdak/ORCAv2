"""Weather Agent - wind, waves, alerts (IMD)"""

from langchain_ollama import ChatOllama
from data_layer import get_imd_weather

llm = ChatOllama(model="llama3.1:8b")


def weather_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")
    raw_data = get_imd_weather(location)

    prompt = (
        f"You are a maritime weather assistant. Given this raw IMD data for "
        f"{location}: {raw_data}\n"
        f"Write a short, plain-language weather summary (wind, waves, any alerts) "
        f"for a fisherman. If the data has an error/note instead of real values, "
        f"say weather data isn't available yet rather than making numbers up."
    )
    result = llm.invoke(prompt)

    return {"weather_data": {"raw": raw_data, "summary": result.content}}
