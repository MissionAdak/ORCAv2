"""Geospatial Agent - routing, geofencing"""

from langchain_ollama import ChatOllama
from data_layer import get_gis_boundaries

llm = ChatOllama(model="llama3.1:8b")


def geo_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")
    boundary_data = get_gis_boundaries(location)

    # Real geofencing example (once you have a boundaries.geojson file):
    #
    # import geopandas as gpd
    # from shapely.geometry import Point
    #
    # boundaries = gpd.read_file("boundaries.geojson")
    # point = Point(longitude, latitude)
    # inside_zone = boundaries[boundaries.contains(point)]
    #
    # This tells you if a given lat/lon falls inside a restricted or
    # international-boundary zone - critical for fisherman safety alerts.

    prompt = (
        f"You are a maritime geospatial assistant. Given this boundary data "
        f"for {location}: {boundary_data}\n"
        f"Write a short note on any relevant maritime boundaries or geofencing "
        f"considerations. If no real boundary data is loaded yet, say so plainly."
    )
    result = llm.invoke(prompt)

    return {"geo_data": {"raw": boundary_data, "summary": result.content}}
