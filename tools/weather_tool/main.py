"""
WeatherTool: fast wind forecast for kitesurf agents.

Tool signature
--------------
get_wind_forecast(lat: float, lon: float, hours: int = 48) -> dict
    • lat, lon in decimal degrees
    • hours ∈ [1, 168]  (7 days max)
Returns:
    { "time": [...], "windspeed_10m": [...], "winddirection_10m": [...] }
All arrays are ISO-8601-aligned and truncated to `hours` length.
"""

from __future__ import annotations
import requests, datetime as dt
import gradio as gr

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_wind_forecast(
    lat: float,
    lon: float,
    hours: int = 48,
) -> dict:
    """
    Get wind forecast from Open-Meteo.

    Args:
        lat: latitude in decimal degrees
        lon: longitude in decimal degrees
        hours: number of future hours to return (1-168)

    Returns:
        Dictionary with 'time', 'windspeed_10m', 'winddirection_10m' lists.
    """
    assert 1 <= hours <= 168, "hours must be 1-168"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "windspeed_10m,winddirection_10m",
        "timezone": "auto",
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    hourly = resp.json()["hourly"]

    return {
        "time": hourly["time"][:hours],
        "windspeed_10m": hourly["windspeed_10m"][:hours],
        "winddirection_10m": hourly["winddirection_10m"][:hours],
    }


demo = gr.Interface(
    fn=get_wind_forecast,
    inputs=[
        gr.Number(label="Latitude"),
        gr.Number(label="Longitude"),
        gr.Slider(1, 168, value=48, step=1, label="Hours ahead"),
    ],
    outputs="json",
    title="WeatherTool – Wind Forecast",
    description=get_wind_forecast.__doc__,
)

if __name__ == "__main__":
    # share=True = public link for judges; mcp_server=True = exposes the tool
    demo.launch(share=True, mcp_server=True, show_error=True)