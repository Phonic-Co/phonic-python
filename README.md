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
    SAMPLE_RATE = 44100

    voices = get_voices(API_KEY)
    voice_ids = [voice["id"] for voice in voices]
    logger.info(f"Available voices: {voice_ids}")
    voice_selected = "greta"

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
            text_buffer = ""
            async for message in sts_stream:
                message_type = message.get("type")
                match message_type:
                    case "audio_chunk":
                        audio_streamer.add_audio_to_playback(message["audio"])
                        if text := message.get("text"):
                            text_buffer += text
                            if any(punc in text_buffer for punc in ".!?"):
                                logger.info(f"Assistant: {text_buffer}")
                                text_buffer = ""
                    case "audio_finished":
                        if len(text_buffer) > 0:
                            logger.info(f"Assistant: {text_buffer}")
                            text_buffer = ""
                    case "input_text":
                        logger.info(f"You: {message['text']}")
                    case "interrupted_response":
                        audio_streamer.interrupt_playback()
                        logger.info("Response interrupted")

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

conversation_id = "conv_12cf6e88-c254-4d3e-a149-ddf1bdd2254c"
conversations = Conversations(api_key=API_KEY)

# Get conversation
result = conversations.get_conversation(conversation_id)

# Get conversation by external ID
result = conversations.get_by_external_id(external_id)

# List conversations with pagination
results = conversations.list(
    started_at_min="2025-01-01",
    started_at_max="2025-03-01",
    duration_min=0,
    duration_max=120,
    limit=50  # Get up to 50 conversations per request
)

# Pagination - get the next page
next_cursor = results["pagination"]["nextPageCursor"]
if next_cursor:
    next_page = conversations.list(
        started_at_min="2025-01-01",
        started_at_max="2025-03-01",
        after=next_cursor,
        limit=50
    )

# Pagination - get the previous page
prev_cursor = results["pagination"]["previousPageCursor"]
if prev_cursor:
    prev_page = conversations.list(
        started_at_min="2025-01-01",
        started_at_max="2025-03-01",
        before=prev_cursor,
        limit=50
    )

# Scroll through all conversations automatically
# This handles pagination for you
for conversation in conversations.scroll(
    max_items=250,  # Total conversations to retrieve
    started_at_min="2025-01-01",
    started_at_max="2025-03-01",
    duration_min=0,
    duration_max=120,
):
    print(conversation["id"])
    # Process each conversation

# List evaluation prompts for a project
prompts = conversations.list_evaluation_prompts(project_id)

# Create a new evaluation prompt
new_prompt = conversations.create_evaluation_prompt(
    project_id=project_id,
    name="customer_issue_resolved",
    prompt="Did the agent resolve the customer's issue?"
)

# Execute an evaluation on a conversation
evaluation = conversations.execute_evaluation(
    conversation_id=conversation_id,
    prompt_id=prompt_id
)

# Generate a summary of the conversation
summary = conversations.summarize_conversation(conversation_id)

# List extraction schemas for a project
schemas = conversations.list_extraction_schemas(project_id)

# Create a new extraction schema
new_schema = conversations.create_extraction_schema(
    project_id=project_id,
    name="booking_details",
    prompt="Extract booking details from this conversation",
    schema={
        "customer_name": {"type": "string", "description": "Customer's full name"},
        "appointment_date": {"type": "string", "description": "Requested appointment date"}
    }
)

# Create an extraction using a schema
extraction = conversations.create_extraction(
    conversation_id=conversation_id,
    schema_id=new_schema["id"]
)

# List all extractions for a conversation
extractions = conversations.list_extractions(conversation_id)
```

## Troubleshooting

- `pyaudio` installation has a known issue where the `portaudio.h` file cannot be found. See [Stack Overflow](https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include) for OS-specific advice.
- Sometimes, when running the example speech-to-speech code for the first time, you may see a certificate verification failure. A solution for this is also documented in [Stack Overflow](https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate).
