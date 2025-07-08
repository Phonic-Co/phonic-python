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

TODO: give an example of creating an agent and running an inbound or outbound call

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

# Cancel an active conversation
result = conversations.cancel(conversation_id)
# Returns: {"success": true} on success
# Returns: {"error": {"message": <error message>}} on error
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
    voice_id="grant",
    timezone="America/Los_Angeles",
    welcome_message="Hello! Welcome to our business. How can I help you today?",
    system_prompt="You are a helpful customer support agent for {{business_name}}. When addressing the customer, call them {{customer_name}}. Be friendly and concise.",
    template_variables={
        "customer_name": {"default_value": "valued customer"},
        "business_name": {"default_value": "our company"}
    },
    tools=["keypad_input","natural_conversation_ending"],
    boosted_keywords=["appointment", "booking", "cancel"],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    configuration_endpoint={
        "url": "https://api.example.com/config",
        "headers": {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json"
        },
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
    timezone="America/New_York",
    system_prompt="You are a helpful support agent. Address customers as {{customer_name}} and inform them our support hours are {{support_hours}}. Be concise.",
    voice_id="maya",
    template_variables={
        "customer_name": {"default_value": "dear customer"},
        "support_hours": {"default_value": "9 AM to 5 PM"}
    },
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
    endpoint_headers={
        "Authorization": "Bearer token123",
        "Content-Type": "application/json"
    }
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
  "voice_id": "grant",
  "timezone": "America/Los_Angeles",
  "audio_format": "pcm_44100",
  "welcome_message": "Hello! Welcome to our business. How can I help you today?",
  "system_prompt": "You are a helpful customer support agent for {{business_name}}. When addressing the customer, call them {{customer_name}}. Be friendly and concise.",
  "template_variables": {
    "customer_name": {"default_value": "valued customer"},
    "business_name": {"default_value": "our company"}
  },
  "tool_ids": ["keypad_input"],
  "no_input_poke_sec": 30,
  "no_input_poke_text": "Are you still there?", 
  "no_input_end_conversation_sec": 180,
  "boosted_keywords": ["appointment", "booking", "cancel"],
  "configuration_endpoint": {
    "url": "https://api.example.com/config",
    "headers": {
      "Authorization": "Bearer token123",
      "Content-Type": "application/json"
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
  "endpoint_headers": {
    "Authorization": "Bearer token123",
    "Content-Type": "application/json"
  },
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
