# Phonic Python Client

The official Python client for [Phonic](https://phonic.co) - build voice AI applications with real-time speech-to-speech capabilities.

## Quick Start

### Get an API Key

To obtain an API key, you must be invited to the Phonic platform.

After you have been invited, you can generate an API key by visiting the [Phonic API Key page](https://phonic.co/api-keys).

Please set it to the environment variable `PHONIC_API_KEY`.

### Installation
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

### Getting Available Voices

```python
from phonic.client import get_voices

voices = get_voices(api_key=API_KEY)
voice_ids = [voice["id"] for voice in voices]
print(f"Available voices: {voice_ids}")
```

### Managing Conversations

```python
from phonic.client import Conversations

conversation_id = "conv_12cf6e88-c254-4d3e-a149-ddf1bdd2254c"
conversations = Conversations(api_key=API_KEY)

# Get conversation by ID
result = conversations.get(conversation_id)

# Get conversation by external ID
conversation = conversations.get_by_external_id("external-123", project="main")

# List conversations with filters and pagination
results = conversations.list(
    project="main",
    started_at_min="2025-01-01",
    started_at_max="2025-03-01",
    duration_min=0,
    duration_max=120,
    limit=50

# Handle pagination manually
next_cursor = results.get['pagination']['next_cursor']
if next_cursor:
    next_page = conversations.list(
        started_at_min="2025-01-01",
        started_at_max="2025-03-01",
        after=next_cursor,
        limit=50
    )

# Pagination - get the previous page
prev_cursor = results["pagination"]["prev_cursor"]
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
    project="main",
    max_items=250,
    started_at_min="2025-01-01",
    started_at_max="2025-03-01",
    duration_min=0,
    duration_max=120,
):
    print(conversation["id"])

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
    fields=[
        {
            "name": "Date",
            "type": "string",
            "description": "The date of the appointment",
        },
        {
            "name": "Copay",
            "type": "string",
            "description": "Amount of money the patient pays for the appointment",
        },
    ]
)

# Create an extraction using a schema
extraction = conversations.create_extraction(
    conversation_id=conversation_id,
    schema_id=new_schema["id"]
)

# List all extractions for a conversation
extractions = conversations.list_extractions(conversation_id)
```

### Managing Agents

```python
from phonic.client import Agents

agents = Agents(api_key=API_KEY)

# Create a new agent
agent = agents.create(
    "booking-support-agent",
    project="customer-support",
    phone_number="assign-automatically",
    voice_id="meredith",
    welcome_message="Hello! How can I help you today?",
    system_prompt="You are a helpful customer support agent. Be friendly and concise.",
    tools=["keypad_input","natural_conversation_ending"],
    boosted_keywords=["appointment", "booking", "cancel"],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    configuration_endpoint={
        "url": "https://api.example.com/config",
        "headers": {"Authorization": "Bearer token123"},
        "timeout_ms": 2000
    }
)

# List all agents in a project
agents_list = agents.list(project="customer-support")

# Get an agent
agent = agents.get("agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")
agent = agents.get("booking-support-agent", project="customer-support")  # by name

# Update an agent
agents.update(
    "booking-support-agent",
    project="customer-support",
    system_prompt="You are a helpful support agent. Be concise.",
    voice_id="maya",
    tools=["keypad_input","natural_conversation_ending"]
)

# Delete an agent
agents.delete("agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")
agents.delete("booking-support-agent", project="customer-support")  # by name
```

### Managing Tools

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

# Create a new tool
tool = tools.create(
    name="book_appointment",
    description="Books an appointment in the calendar system",
    endpoint_url="https://api.example.com/book-appointment",
    endpoint_timeout_ms=5000,
    parameters=[
        {
            "type": "string",
            "name": "date",
            "description": "The date for the appointment in YYYY-MM-DD format",
            "is_required": True
        },
        {
            "type": "string",
            "name": "time", 
            "description": "The time for the appointment in HH:MM format",
            "is_required": True
        },
        {
            "type": "array",
            "item_type": "string",
            "name": "service_types",
            "description": "List of services requested",
            "is_required": False
        }
    ],
    endpoint_headers=[
        {"name": "Authorization", "value": "Bearer token123"},
        {"name": "Content-Type", "value": "application/json"}
    ]
)

# List all tools for the organization
tools_list = tools.list()

# Get a tool by ID or name
tool = tools.get("tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")
tool = tools.get("book_appointment")  # by name

# Update a tool
tools.update(
    "book_appointment",
    description="Updated booking tool with enhanced features",
    endpoint_timeout_ms=7000,
    parameters=[
        {
            "type": "string",
            "name": "customer_name",
            "description": "Name of the customer",
            "is_required": True
        }
    ]
)

# Delete a tool
tools.delete("tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")
tools.delete("book_appointment")  # by name
```

## Response Formats

### Agent Creation Response
When you create an agent, the response contains:
```json
{
  "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
  "name": "booking-support-agent"
}
```

### Agent Details Response
When you get or list agents, each agent object contains:
```json
{
  "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
  "name": "booking-support-agent",
  "project": {
    "id": "proj_ad0334f1-2404-4155-9df3-bfd8129b29ad",
    "name": "customer-support"
  },
  "voice_id": "meredith",
  "audio_format": "pcm_44100",
  "welcome_message": "Hello! How can I help you today?",
  "system_prompt": "You are a helpful customer support agent. Be friendly and concise.",
  "tool_ids": ["keypad_input"],
  "no_input_poke_sec": 30,
  "no_input_poke_text": "Are you still there?", 
  "no_input_end_conversation_sec": 180,
  "boosted_keywords": ["appointment", "booking", "cancel"],
  "configuration_endpoint": {
    "url": "https://api.example.com/config",
    "headers": {
      "Authorization": "Bearer token123"
    },
    "timeout_ms": 2000
  },
  "phone_number": "+1234567890"
}
```

### Tool Creation Response
When you create a tool, the response contains:
```json
{
  "id": "tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
  "name": "book_appointment"
}
```

### Tool Details Response
When you get or list tools, each tool object contains:
```json
{
  "id": "tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
  "name": "book_appointment",
  "description": "Books an appointment in the calendar system",
  "endpoint_url": "https://api.example.com/book-appointment",
  "endpoint_headers": [
    {
      "name": "Authorization",
      "value": "Bearer token123"
    }
  ],
  "endpoint_timeout_ms": 5000,
  "parameters": [
    {
      "type": "string",
      "name": "date",
      "description": "The date for the appointment in YYYY-MM-DD format",
      "is_required": true
    },
    {
      "type": "string",
      "name": "customer_name",
      "description": "The name of the customer booking the appointment",
      "is_required": true
    }
  ]
}
```

## Troubleshooting

- `pyaudio` installation has a known issue where the `portaudio.h` file cannot be found. See [Stack Overflow](https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include) for OS-specific advice.
- Sometimes, when running the example speech-to-speech code for the first time, you may see a certificate verification failure. A solution for this is also documented in [Stack Overflow](https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate).