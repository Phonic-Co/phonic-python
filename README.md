# Phonic Python Client 

## Get an API Key

To obtain an API key, you must be invited to the Phonic platform.

After you have been invited, you can generate an API key by visiting the [Phonic API Key page](https://phonic.co/api-keys). 

Please set it to the environment variable `PHONIC_API_KEY`.

## Installation
```
pip install phonic-python
```

## Speech-to-Speech Usage

```python
import asyncio
import os

from loguru import logger

from phonic.audio_interface import PyaudioContinuousAudioInterface
from phonic.client import PhonicSTSClient, get_voices


async def main():
    STS_URI = "wss://api.phonic.co/v1/sts/ws"
    API_KEY = os.environ["PHONIC_API_KEY"]
    SAMPLE_RATE = 44_100

    voices = get_voices(API_KEY)
    voice_ids = [voice["id"] for voice in voices]
    logger.info(f"Available voices: {voice_ids}")
    voice_selected = "katherine"

    try:
        async with PhonicSTSClient(STS_URI, API_KEY) as client:
            audio_streamer = PyaudioContinuousAudioInterface(
                client, sample_rate=SAMPLE_RATE
            )

            sts_stream = client.sts(
                input_format="pcm_44100",
                output_format="pcm_44100",
                system_prompt="You are a helpful voice assistant. Respond conversationally.",
                # welcome_message="Hello! I'm your voice assistant. How can I help you today?",
                voice_id=voice_selected,
            )

            await audio_streamer.start()

            logger.info(f"Starting STS conversation with voice {voice_selected}...")
            print("Starting conversation... (Ctrl+C to exit)")
            print("Streaming all audio continuously to the server. Start talking!")

            # Process messages from STS
            async for message in sts_stream:
                message_type = message.get("type")
                if message_type == "audio_chunk":
                    audio_streamer.add_audio_to_playback(message["audio"])
                    if text := message.get("text"):
                        logger.info(f"Assistant: {text}")
                elif message_type == "input_text":
                    logger.info(f"You: {message['text']}")

    except KeyboardInterrupt:
        logger.info("Conversation stopped by user")
        if "audio_streamer" in locals():
            audio_streamer.stop()
    except Exception as e:
        logger.error(f"Error in conversation: {e}")
        if "audio_streamer" in locals():
            audio_streamer.stop()
        raise e


if __name__ == "__main__":
    print("Starting continuous Speech-to-Speech conversation...")
    print("Audio streaming will begin automatically when connected.")
    print("Press Ctrl+C to exit")
    asyncio.run(main())
```

### Managing Conversations

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

conversation = conversations.get_conversation("conv_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")
print(conversation)

# List conversations
results = conversations.list(
    duration_min=10,
    started_at_min="2023-01-01"
)

# Run an evaluation on a conversation
evaluation = conversations.execute_evaluation(
    conversation_id="conv_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
    prompt_id="conv_eval_prompt_d7cfe45d-35db-4ef6-a254-81ab1da76ce0"
)

# Generate a summary of the conversation
summary = conversations.summarize_conversation("conv_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")

# Extract structured data from a conversation
data = conversations.extract_data(
    "conv_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
    instructions="Extract booking details from this conversation",
    fields={
        "customer_name": {"type": "string", "description": "Customer's full name"},
        "appointment_date": {"type": "string", "description": "Requested appointment date"}
    }
)
```