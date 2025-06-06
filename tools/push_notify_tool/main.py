"""PushNotifyTool
Sends SMS or Email using Twilio SendGrid.
Requires environment variables TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
TWILIO_FROM_NUMBER, SENDGRID_API_KEY, SENDGRID_FROM_EMAIL.
"""
import os
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

from typing import Optional

try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None

try:
    import sendgrid
    from sendgrid.helpers.mail import Mail
except Exception:
    sendgrid = None


TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER")
SENDGRID_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM_EMAIL")


def send_sms(to_number: str, message: str) -> dict:
    if not TwilioClient or not TWILIO_SID:
        return {"error": "Twilio not configured"}
    client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
    sms = client.messages.create(body=message, from_=TWILIO_FROM, to=to_number)
    return {"sid": sms.sid}


def send_email(to_email: str, subject: str, message: str) -> dict:
    if not sendgrid or not SENDGRID_KEY:
        return {"error": "SendGrid not configured"}
    sg = sendgrid.SendGridAPIClient(SENDGRID_KEY)
    mail = Mail(from_email=SENDGRID_FROM, to_emails=to_email,
                subject=subject, plain_text_content=message)
    response = sg.send(mail)
    return {"status_code": response.status_code}

with gr.Blocks() as demo:
    gr.Markdown("# PushNotifyTool")
    with gr.Tab("Send SMS"):
        num = gr.Textbox(label="To Number")
        msg = gr.Textbox(label="Message")
        out = gr.JSON()
        btn = gr.Button("Send SMS")
        btn.click(send_sms, [num, msg], out)
    with gr.Tab("Send Email"):
        em = gr.Textbox(label="To Email")
        subj = gr.Textbox(label="Subject")
        body = gr.Textbox(label="Message")
        out_e = gr.JSON()
        btn_e = gr.Button("Send Email")
        btn_e.click(send_email, [em, subj, body], out_e)

if __name__ == "__main__":
    demo.launch(share=True, mcp_server=True, show_error=True)
