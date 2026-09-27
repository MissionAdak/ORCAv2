"""Ocean Analytics Agent - SST, chlorophyll, PFZ (INCOIS, MOSDAC)"""

from langchain_ollama import ChatOllama
from data_layer import get_incois_pfz, get_mosdac_eo

llm = ChatOllama(model="llama3.1:8b")


def ocean_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")
    pfz_data = get_incois_pfz(location)
    eo_data = get_mosdac_eo(location)

    prompt = (
        f"You are an ocean conditions assistant. Given this data for {location}:\n"
        f"PFZ/INCOIS data: {pfz_data}\n"
        f"Earth observation (SST/chlorophyll) data: {eo_data}\n"
        f"Write a short, plain-language summary of ocean conditions and whether "
        f"there's a favorable fishing zone nearby. If the data has an error/note "
        f"instead of real values, say ocean data isn't available yet rather than "
        f"making numbers up."
    )
    result = llm.invoke(prompt)

    return {"ocean_data": {"pfz": pfz_data, "eo": eo_data, "summary": result.content}}
