"""WindWizard Agent
Simple demo agent that calls MCP tools to compute a stoke score
and recommend gear based on current conditions.
"""

from gradio_client import Client
import gradio as gr
from statistics import mean

# URLs where the tool servers run locally
WEATHER_URL = "http://127.0.0.1:7860/"
TIDE_URL = "http://127.0.0.1:7861/"
SPOT_URL = "http://127.0.0.1:7862/"
PROFILE_URL = "http://127.0.0.1:7863/"
NOTIFY_URL = "http://127.0.0.1:7864/"

weather_client = Client(WEATHER_URL)
tide_client = Client(TIDE_URL)
spot_client = Client(SPOT_URL)
profile_client = Client(PROFILE_URL)
notify_client = Client(NOTIFY_URL)


def compute_stoke(user_id: str, lat: float, lon: float, hours: int = 6, alert: bool = False):
    # Convert hours to integer to ensure proper slicing in tools
    hours = int(hours)
    
    # Fetch profile
    profile = profile_client.predict(user_id, api_name="//Get Profile")
    weight = profile.get("weight", 80)
    skill = profile.get("skill", "intermediate")

    weather = weather_client.predict(lat, lon, hours)
    wind = weather["windspeed_10m"]
    avg_wind = mean(wind)

    tide = tide_client.predict(lat, lon, hours, api_name="/predict")
    tide_level = tide["sea_level"]
    avg_tide = mean(tide_level)

    # naive stoke score formula
    score = min(100, max(0, int(avg_wind * 4 + avg_tide * 10)))

    # simple kite size recommendation
    if avg_wind < 10:
        kite = "Too little wind"
    elif avg_wind < 15:
        kite = "12m kite"
    elif avg_wind < 20:
        kite = "9m kite"
    else:
        kite = "7m kite"

    msg = f"Avg wind {avg_wind:.1f} kt, tide {avg_tide:.2f}m. Stoke {score}/100. Use {kite}."

    if alert and score >= 60:
        notify_client.predict(profile.get("phone", ""), msg, api_name="//Send SMS")

    return {"profile": profile, "stoke": score, "kite": kite, "message": msg}


def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# WindWizard Demo")
        user = gr.Textbox(label="User ID")
        lat = gr.Number(label="Latitude", value=55.66)
        lon = gr.Number(label="Longitude", value=12.56)
        hours = gr.Slider(1, 24, value=6, label="Hours ahead")
        alert = gr.Checkbox(label="Send SMS alert if stoke >=60")
        out = gr.JSON()
        btn = gr.Button("Compute Stoke")
        btn.click(compute_stoke, [user, lat, lon, hours, alert], out)
    return demo


if __name__ == "__main__":
    build_ui().launch(share=True, show_error=True)
