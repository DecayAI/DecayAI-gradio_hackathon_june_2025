# tools/spot_db_tool/main.py
import os, gradio as gr
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL   = os.getenv("SUPABASE_URL")
SUPABASE_ANON  = os.getenv("SUPABASE_ANON_KEY")
sb = create_client(SUPABASE_URL, SUPABASE_ANON)

def get_spots_near(lat: float, lon: float, max_km: int = 150):
    """Return spots within `max_km` of lat/lon, sorted by distance."""
    params = {
        'p_lat': lat,
        'p_lon': lon,
        'p_max_km': max_km
    }
    data = sb.rpc('get_spots_near', params).execute().data
    return data

demo = gr.Interface(
    fn=get_spots_near,
    inputs=[gr.Number(label="Lat"), gr.Number(label="Lon"), gr.Slider(10,250,100)],
    outputs="json",
    title="SpotDBTool – nearby spots",
)
if __name__ == "__main__":
    demo.launch(share=True, mcp_server=True, show_error=True)
