"""
TideTool – hourly sea‐level & high/low‐tide extremes.
 - Tries Stormglass first; on HTTP 402, falls back to a semidiurnal sine wave.
 
Functions
---------
get_tide_sea_level(lat: float, lon: float, hours: int = 48) -> dict
    • lat, lon in decimal degrees
    • hours ∈ [1, 240]  (10 days max)
    Returns: {
        "time": [ ISO‐8601 strings … ],
        "sea_level": [floats …]
    }

get_tide_extremes(lat: float, lon: float, days: int = 3) -> list
    • days ∈ [1, 10]
    Returns: list of { "time": "...", "height": float, "type": "high"/"low" }
    (On Stormglass 402, returns extremes from the synthetic sine wave.)
"""

from __future__ import annotations
import os, datetime as dt, requests, math
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("STORMGLASS_API_KEY")
BASE_URL = "https://api.stormglass.io/v2/tide"


def _request(endpoint: str, params: dict):
    """Helper to call Stormglass; may raise HTTPError (402, 401, etc.)."""
    hdr = {"Authorization": API_KEY}
    r = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=hdr, timeout=10)
    r.raise_for_status()
    return r.json()


def _sine_wave_tide(hours: int, start_dt: dt.datetime) -> dict:
    """
    Generate a simple semidiurnal (≈12.42 h period) tide sine wave.
    - Amplitude = 1 m (peak ±1 m). Can be scaled later if desired.
    - phase aligned to the UNIX epoch (arbitrary zero point).
    """
    times = []
    levels = []
    for h in range(hours):
        t = start_dt + dt.timedelta(hours=h)
        # Compute seconds since epoch
        seconds = (t - dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)).total_seconds()
        # Period ≈ 12.42 h = 12.42 * 3600 s
        period = 12.42 * 3600
        level = math.sin(2 * math.pi * (seconds / period))
        times.append(t.isoformat())
        levels.append(level)  # amplitude ±1 m
    return {"time": times, "sea_level": levels}


def get_tide_sea_level(lat: float, lon: float, hours: int = 48) -> dict:
    """
    Hourly sea‐level (m) for the next `hours` (≤ 240).
    Tries Stormglass; on HTTP 402, returns a synthetic sine wave tide.
    """
    assert 1 <= hours <= 240, "hours must be between 1 and 240"
    now = dt.datetime.now(dt.timezone.utc)
    end = now + dt.timedelta(hours=hours)
    params = {
        "lat": lat,
        "lng": lon,
        "start": now.strftime("%Y-%m-%dT%H"),
        "end": end.strftime("%Y-%m-%dT%H"),
    }
    try:
        data = _request("sea-level/point", params)["data"]
        return {
            "time": [row["time"] for row in data][:hours],
            "sea_level": [row["sg"] for row in data][:hours],  # sg = composite source
        }
    except requests.HTTPError as e:
        if e.response.status_code == 402:
            # Fall back to synthetic tide
            return _sine_wave_tide(hours, now)
        else:
            raise


def _find_synthetic_extremes(days: int, start_dt: dt.datetime) -> list[dict]:
    """
    Given `days`, look 0..days*24 hours ahead, sample hourly, find local maxima/minima 
    in that synthetic sine wave. Return a list of dicts:
    [{ "time": "...", "height": float, "type": "high" / "low" }, …]
    """
    hours = days * 24
    tide = _sine_wave_tide(hours + 1, start_dt)  # +1 to detect last peak
    times = tide["time"]
    levels = tide["sea_level"]
    extremes = []
    for i in range(1, len(levels) - 1):
        if levels[i] >= levels[i - 1] and levels[i] >= levels[i + 1]:
            extremes.append({"time": times[i], "height": levels[i], "type": "high"})
        elif levels[i] <= levels[i - 1] and levels[i] <= levels[i + 1]:
            extremes.append({"time": times[i], "height": levels[i], "type": "low"})
    return extremes


def get_tide_extremes(lat: float, lon: float, days: int = 3) -> list[dict]:
    """
    High/low‐tide timestamps & heights for the next `days` (≤ 10).
    Tries Stormglass; on HTTP 402, returns synthetic sine‐wave extremes.
    """
    assert 1 <= days <= 10, "days must be 1–10"
    now = dt.datetime.now(dt.timezone.utc)
    end_date = (now + dt.timedelta(days=days)).strftime("%Y-%m-%d")
    start_date = now.strftime("%Y-%m-%d")
    params = {"lat": lat, "lng": lon, "start": start_date, "end": end_date}
    try:
        data = _request("extremes", params)["data"]
        # Each `data` row has {"time": "...", "height": ..., "type": "high"/"low"}
        return data
    except requests.HTTPError as e:
        if e.response.status_code == 402:
            # Generate synthetic extremes
            return _find_synthetic_extremes(days, now)
        else:
            raise


demo_sea = gr.Interface(
    fn=get_tide_sea_level,
    inputs=[gr.Number(label="Lat"), gr.Number(label="Lon"), gr.Slider(1, 240, 48)],
    outputs="json",
    title="TideTool – Sea Level (fallback to sine wave on 402)",
    description=get_tide_sea_level.__doc__,
)

demo_extremes = gr.Interface(
    fn=get_tide_extremes,
    inputs=[gr.Number(label="Lat"), gr.Number(label="Lon"), gr.Slider(1, 10, 3)],
    outputs="json",
    title="TideTool – Extremes (fallback to synthetic)",
    description=get_tide_extremes.__doc__,
)

if __name__ == "__main__":
    # Launch both interfaces under one MCP server
    with gr.Blocks() as app:
        gr.Markdown("## TideTool: sea‐level and extremes (uses Stormglass, then synthetic)")
        with gr.Tab("Sea Level"):
            demo_sea.render()
        with gr.Tab("Extremes"):
            demo_extremes.render()

    app.launch(share=True, mcp_server=True)
