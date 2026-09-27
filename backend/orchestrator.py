"""
ORCA Orchestrator
------------------
Routes a user query through Weather / Ocean / Geo / Risk agents (based on
what the query needs), then always finishes at the Visualization agent.
Mirrors the layered diagram: UI -> Orchestrator -> specialist agents ->
Data layer -> Visualization -> Response.
"""

import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

from weather_agent import weather_agent
from ocean_agent import ocean_agent
from geo_agent import geo_agent
from risk_agent import risk_agent
from viz_agent import viz_agent

llm = ChatOllama(model="llama3.1:8b")


class OrcaState(TypedDict, total=False):
    query: str
    location: str
    needed_agents: List[str]
    weather_data: dict
    ocean_data: dict
    geo_data: dict
    risk_data: dict
    response: str


def route_intent(state: OrcaState) -> OrcaState:
    """Orchestrator / planner node: decide which specialist agents this
    query needs, and pull out a location if mentioned."""
    query = state["query"]

    prompt = (
        "You are an intent router for a maritime assistant. Given the user "
        "query below, respond with ONLY a JSON object (no other text) with "
        "two keys:\n"
        '  "location": the place mentioned in the query, or "unspecified"\n'
        '  "agents": a list containing any of "weather", "ocean", "geo", "risk" '
        "that are relevant to answering the query. Include \"risk\" whenever "
        "safety is being asked about.\n\n"
        f"Query: {query}\n\n"
        "JSON:"
    )
    result = llm.invoke(prompt)

    try:
        parsed = json.loads(result.content.strip())
        location = parsed.get("location", "unspecified")
        needed_agents = parsed.get("agents", ["weather", "ocean", "geo", "risk"])
    except (json.JSONDecodeError, AttributeError):
        # If the model didn't return clean JSON, fail safe: run everything.
        location = "unspecified"
        needed_agents = ["weather", "ocean", "geo", "risk"]

    # HARD RULE, decided in code: weather and risk always run, regardless
    # of what the LLM router decided. This is a safety tool - we don't
    # want a missed classification to silently skip the risk assessment.
    for required in ("weather", "risk"):
        if required not in needed_agents:
            needed_agents.append(required)

    return {"location": location, "needed_agents": needed_agents}


def route_decision(state: OrcaState) -> List[str]:
    """Conditional edge function: returns the list of next node names."""
    return state.get("needed_agents", ["weather", "ocean", "geo", "risk"])


def build_graph():
    graph = StateGraph(OrcaState)

    graph.add_node("orchestrator", route_intent)
    graph.add_node("weather", weather_agent)
    graph.add_node("ocean", ocean_agent)
    graph.add_node("geo", geo_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("visualization", viz_agent)

    graph.set_entry_point("orchestrator")

    # Fan out from orchestrator to whichever agents are needed
    graph.add_conditional_edges(
        "orchestrator",
        route_decision,
        {
            "weather": "weather",
            "ocean": "ocean",
            "geo": "geo",
            "risk": "risk",
        },
    )

    # Every specialist agent feeds into visualization
    graph.add_edge("weather", "visualization")
    graph.add_edge("ocean", "visualization")
    graph.add_edge("geo", "visualization")
    graph.add_edge("risk", "visualization")

    graph.add_edge("visualization", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    test_query = "Is it safe to fish near Kochi tomorrow?"
    initial_state: OrcaState = {"query": test_query}

    final_state = app.invoke(initial_state)

    print("=" * 60)
    print("QUERY:", test_query)
    print("=" * 60)
    print(final_state.get("response", "No response generated."))
