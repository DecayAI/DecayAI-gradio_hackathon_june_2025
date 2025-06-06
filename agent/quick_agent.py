# agent/quick_agent.py

from langchain.tools import Tool
from gradio_client import Client

def test_it():
    """
    A simple smoke-test that calls each MCP tool endpoint
    and prints out their JSON responses at a sample location.
    """
    # 1) Point each Client at the local URL where you launched the tool
    weather_client = Client("http://127.0.0.1:7860/")
    tide_client    = Client("http://127.0.0.1:7861/")
    spots_client   = Client("http://127.0.0.1:7862/")

    # 2) Wrap them as LangChain Tools (this is just for consistent naming)
    tools = [
        Tool(
            name="WindForecast", 
            func=lambda T: weather_client.predict(T["lat"], T["lon"], T["hours"]),
            description="Fetch wind for a given lat/lon; args: (lat, lon, hours)"
        ),
        Tool(
            name="TideSeaLevel", 
            func=lambda T: tide_client.predict(T["lat"], T["lon"], T["hours"], api_name="/predict"),
            description="Fetch tide sea-level data; args: (lat, lon, hours)"
        ),
        Tool(
            name="FindSpots",    
            func=lambda T: spots_client.predict(T["lat"], T["lon"], T["max_km"]),
            description="Fetch nearby kite spots; args: (lat, lon, max_km)"
        ),
    ]

    # 3) Pick a sample location (e.g., Copenhagen airport coordinates)
    sample_lat = 55.66
    sample_lon = 12.56

    # 4) Call each tool and print its JSON response
    print("\n=== Calling WindForecast(lat=55.66, lon=12.56, hours=5) ===")
    wind_json = tools[0].func({"lat": sample_lat, "lon": sample_lon, "hours": 5})
    print(wind_json)

    print("\n=== Calling TideSeaLevel(lat=55.66, lon=12.56, hours=5) ===")
    tide_json = tools[1].func({"lat": sample_lat, "lon": sample_lon, "hours": 5})
    print(tide_json)

    print("\n=== Calling FindSpots(lat=55.66, lon=12.56, max_km=50) ===")
    spots_json = tools[2].func({"lat": sample_lat, "lon": sample_lon, "max_km": 50})
    print(spots_json)


if __name__ == "__main__":
    test_it()