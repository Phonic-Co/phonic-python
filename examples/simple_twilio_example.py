# Simple Twilio Integration with Phonic
#
# This example demonstrates how to use Phonic's STS (Speech-to-Speech)
# API with Twilio's Programmable Voice Media Streams API.
#
# Prerequisites:
# - A Phonic API key (set in the PHONIC_API_KEY environment variable)
# - A Twilio account with a phone number
# - A publicly accessible server to host this application
#
# Setup steps:
# 1. Install required packages: pip install fastapi uvicorn loguru numpy websockets phonic-python
# 2. Run this script: python simple_twilio_example.py
# 3. Expose your local server to the internet (e.g., using ngrok)
# 4. Update the TwiML Stream URL in templates/twilio.xml with your public URL
# 5. Configure your Twilio phone number to use the /twiml endpoint as the webhook for incoming calls
#
# For more information, see:
# - Twilio Media Streams API: https://www.twilio.com/docs/voice/twiml/stream
# - Phonic API: https://phonic.co/api-keys

import asyncio
import base64
import json
import os
import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from loguru import logger
from pathlib import Path

from phonic.client import PhonicSTSClient, get_voices

# Create FastAPI app
app = FastAPI()

# Configuration - replace with your API key
PHONIC_API_KEY = os.environ.get("PHONIC_API_KEY", "your_phonic_api_key_here")
STS_URI = "wss://api.phonic.co/v1/sts/ws"
SYSTEM_PROMPT = "You are a helpful assistant. Keep responses brief and informative."
WELCOME_MESSAGE = "Hello! I'm your virtual assistant. How can I help you today?"
VOICE_ID = "greta"  # Update with your preferred voice


# Route for Twilio to handle incoming calls
@app.post("/twiml")
async def serve_twiml():
    """Serve TwiML XML template for Twilio"""
    file_path = Path("templates") / "twilio.xml"
    return FileResponse(path=file_path, media_type="text/xml")


@app.websocket("/sts")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for media streaming between Twilio and Phonic"""
    try:
        # Accept the WebSocket connection from Twilio
        await websocket.accept()
        logger.info("Twilio WebSocket connection accepted")

        # Initialize shared state
        shared_state = {"twilio_stream_sid": None}

        # Create Phonic client
        async with PhonicSTSClient(STS_URI, PHONIC_API_KEY) as client:
            # Setup Phonic STS stream
            sts_stream = client.sts(
                input_format="mulaw_8000",  # Twilio uses mulaw 8000Hz
                output_format="mulaw_8000",
                system_prompt=SYSTEM_PROMPT,
                welcome_message=WELCOME_MESSAGE,
                voice_id=VOICE_ID,
            )

            # Start both message processing tasks
            phonic_task = asyncio.create_task(
                process_phonic_messages(sts_stream, websocket, shared_state)
            )
            twilio_task = asyncio.create_task(
                process_twilio_messages(websocket, client, shared_state)
            )

            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [phonic_task, twilio_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel pending tasks
            for task in pending:
                task.cancel()

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up any pending tasks when the connection is closed
        logger.info("WebSocket connection closed")


async def process_phonic_messages(sts_stream, websocket, shared_state):
    """Process messages from Phonic and send to Twilio"""
    text_buffer = ""

    async for message in sts_stream:
        message_type = message.get("type")

        if message_type == "audio_chunk":
            # Get audio data
            audio = message["audio"]

            # Process text if available
            if text := message.get("text"):
                text_buffer += text
                if any(punc in text_buffer for punc in ".!?"):
                    logger.info(f"Assistant: {text_buffer}")
                    text_buffer = ""

            # Send audio to Twilio
            if shared_state["twilio_stream_sid"]:
                twilio_message = {
                    "event": "media",
                    "streamSid": shared_state["twilio_stream_sid"],
                    "media": {"payload": audio},
                }
                await websocket.send_json(twilio_message)

        elif message_type == "audio_finished":
            if text_buffer:
                logger.info(f"Assistant: {text_buffer}")
                text_buffer = ""

        elif message_type == "input_text":
            logger.info(f"User: {message['text']}")

        elif message_type == "interrupted_response":
            # Clear the current audio buffer
            if shared_state["twilio_stream_sid"]:
                twilio_message = {
                    "event": "clear",
                    "streamSid": shared_state["twilio_stream_sid"],
                }
                await websocket.send_json(twilio_message)
            logger.info("Response interrupted")


async def process_twilio_messages(websocket, client, shared_state):
    """Process messages from Twilio and send to Phonic"""
    while True:
        try:
            message = await websocket.receive_text()
            
            try:
                data = json.loads(message)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e} - Message: {message}")
                continue
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            break

        # Handle different Twilio message types
        if data["event"] == "connected":
            logger.info("Twilio connection established")

        elif data["event"] == "start":
            logger.info("Twilio stream started")

        elif (
            data["event"] == "media" and data.get("media", {}).get("track") == "inbound"
        ):
            # Store stream ID if not already stored
            if not shared_state["twilio_stream_sid"]:
                shared_state["twilio_stream_sid"] = data["streamSid"]

            # Process incoming audio
            audio_bytes = base64.b64decode(data["media"]["payload"])
            audio_np = np.frombuffer(
                audio_bytes, dtype=np.uint8
            )  # Twilio uses 8-bit audio

            # Send audio to Phonic
            await client.send_audio(audio_np)


# Create a TwiML file for Twilio
def create_twilio_xml():
    """Create a TwiML file for Twilio to connect to our WebSocket"""
    Path("templates").mkdir(exist_ok=True)

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="wss://your-server-domain.com/sts">
      <!-- Update this URL with your public server URL -->
    </Stream>
  </Connect>
</Response>"""

    xml_path = Path("templates") / "twilio.xml"
    with open(xml_path, "w") as f:
        f.write(xml_content)

    logger.info(f"Created TwiML template at {xml_path}")
    logger.info("IMPORTANT: Update the Stream URL with your public server URL")


# Run the application
if __name__ == "__main__":
    # Create TwiML template if it doesn't exist
    if not (Path("templates") / "twilio.xml").exists():
        create_twilio_xml()

    # Start the server
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    logger.info("To use with Twilio:")
    logger.info(
        f"1. Expose this server publicly (e.g., using ngrok: ngrok http {port})"
    )
    logger.info("2. Update the Stream URL in templates/twilio.xml with your public URL")
    logger.info(
        "3. Set up a Twilio phone number to use the /twiml endpoint as the webhook"
    )
    uvicorn.run(app, host="0.0.0.0", port=port)
