"""UserProfileTool
Simple profile store for kitesurfers.
Exposes get_profile(user_id) and set_profile(user_id, profile_json).
This is a naive in-memory store for demo purposes.
"""

import json
import gradio as gr
from pathlib import Path

STORE_PATH = Path("profiles.json")

if STORE_PATH.exists():
    profiles = json.loads(STORE_PATH.read_text())
else:
    profiles = {}

def get_profile(user_id: str) -> dict:
    """Return stored profile or empty dict."""
    return profiles.get(user_id, {})

def set_profile(user_id: str, profile: dict) -> dict:
    """Update profile and persist to disk."""
    profiles[user_id] = profile
    STORE_PATH.write_text(json.dumps(profiles))
    return {"status": "ok"}

with gr.Blocks() as demo:
    gr.Markdown("# UserProfileTool")
    with gr.Tab("Get Profile"):
        inp = gr.Textbox(label="User ID")
        out = gr.JSON(label="Profile")
        btn = gr.Button("Get")
        btn.click(get_profile, inp, out, api_name="/Get Profile")
    with gr.Tab("Set Profile"):
        inp_id = gr.Textbox(label="User ID")
        inp_profile = gr.JSON(label="Profile JSON")
        out_save = gr.JSON(label="Result")
        btn_save = gr.Button("Save")
        btn_save.click(set_profile, [inp_id, inp_profile], out_save, api_name="/Set Profile")

if __name__ == "__main__":
    demo.launch(server_port=7863, share=True, mcp_server=True, show_error=True)
