# 🎧 Phonic Python Client

The official Python library for the Phonic API.

- [📦 Installation](#-installation)
- [⚙️ Setup](#️-setup)
- [🤖 Agents](#-agents)
  - [Create Agent](#create-agent)
  - [List Agents](#list-agents)
  - [Get Agent](#get-agent)
  - [Update Agent](#update-agent)
  - [Delete Agent](#delete-agent)
- [🛠️ Tools](#️-tools)
  - [Create Tool](#create-tool)
    - [Create webhook tool](#create-webhook-tool)
    - [Create WebSocket tool](#create-websocket-tool)
  - [List Tools](#list-tools)
  - [Get Tool](#get-tool)
  - [Update Tool](#update-tool)
  - [Delete Tool](#delete-tool)
- [🎤 Voices](#-voices)
- [💬 Conversations](#-conversations)
  - [List Conversations](#list-conversations)
  - [Get Conversation by ID](#get-conversation-by-id)
  - [Get Conversation by External ID](#get-conversation-by-external-id)
  - [📞 Outbound Calls](#-outbound-calls)
  - [📄 Pagination](#-pagination)
  - [📝 Evaluation Prompts](#-evaluation-prompts)
  - [📋 Summaries](#-summaries)
  - [❌ Cancel Conversations](#-cancel-conversations)
- [📊 Extraction Schemas](#-extraction-schemas)
- [🐛 Troubleshooting](#-troubleshooting)

## 📦 Installation
```
pip install phonic-python
```

## ⚙️ Setup

To obtain an API key, you must be invited to the Phonic platform.

After you have been invited, you can generate an API key by visiting the [Phonic API Key page](https://phonic.co/api-keys).

Please set it to the environment variable `PHONIC_API_KEY`.

### Basic Imports

```python
from phonic.client import (
    Agents,
    Conversations,
    ExtractionSchemas,
    Tools,
    PhonicSTSClient,
    get_voices
)
```

## 🤖 Agents

### Create Agent

```python
from phonic.client import Agents

agents = Agents(api_key=API_KEY)

# Create a new agent
agent = agents.create(
    "booking-support-agent",
    project="main",
    phone_number="assign-automatically",
    voice_id="grant",
    timezone="America/Los_Angeles",
    welcome_message="Hello! Welcome to {{business_name}}. How can I help you today?",
    system_prompt="You are a helpful customer support agent for {{business_name}}. When addressing the customer, call them {{customer_name}}. Be friendly and concise.",
    template_variables={
        "customer_name": {"default_value": "valued customer"},
        "business_name": {"default_value": "Tech Support Corporation"}
    },
    tools=["keypad_input"],
    boosted_keywords=["appointment", "booking", "cancel"],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    configuration_endpoint={
        "url": "https://myapp.com/webhooks/phonic-config",
        "headers": {
            "Authorization": "Bearer 123"
        },
        "timeout_ms": 10000
    }
)
```

#### Response Format

```json
{
  "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
  "name": "booking-support-agent"
}
```

### List Agents

```python
from phonic.client import Agents

agents = Agents(api_key=API_KEY)

# List all agents in the "main" project
agents_list = agents.list(project="main")
```

#### Response Format

```json
{
  "agents": [
    {
      "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
      "name": "booking-support-agent",
      "project": {
        "id": "proj_ad0334f1-2404-4155-9df3-bfd8129b29ad",
        "name": "main"
      },
      "voice_id": "grant",
      "timezone": "America/Los_Angeles",
      "audio_format": "mulaw_8000",
      "welcome_message": "Hello! Welcome to {{business_name}}. How can I help you today?",
      "system_prompt": "You are a helpful customer support agent for {{business_name}}. When addressing the customer, call them {{customer_name}}. Be friendly and concise.",
      "template_variables": {
        "customer_name": {"default_value": "valued customer"},
        "business_name": {"default_value": "Tech Support Corporation"}
      },
      "tool_ids": ["keypad_input"],
      "no_input_poke_sec": 30,
      "no_input_poke_text": "Are you still there?",
      "no_input_end_conversation_sec": 180,
      "boosted_keywords": ["appointment", "booking", "cancel"],
      "phone_number": "+1234567890"
    }
  ]
}
```

### Get Agent

```python
from phonic.client import Agents

agents = Agents(api_key=API_KEY)

# Get agent by ID
agent = agents.get("agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")

# Get agent by name
agent = agents.get("booking-support-agent", project="main")
```

#### Response Format

```json
{
  "agent": {
    "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
    "name": "booking-support-agent",
    "timezone": "America/Los_Angeles",
    "project": {
      "id": "proj_ad0334f1-2404-4155-9df3-bfd8129b29ad",
      "name": "main"
    },
    "phone_number": "+1234567890",
    "voice_id": "grant",
    "audio_format": "mulaw_8000",
    "welcome_message": "Hello! Welcome to {{business_name}}. How can I help you today?",
    "system_prompt": "You are a helpful customer support agent for {{business_name}}. When addressing the customer, call them {{customer_name}}. Be friendly and concise.",
    "template_variables": {
      "customer_name": {"default_value": "valued customer"},
      "business_name": {"default_value": "Tech Support Corporation"}
    },
    "tools": ["keypad_input"],
    "no_input_poke_sec": 30,
    "no_input_poke_text": "Are you still there?",
    "no_input_end_conversation_sec": 180,
    "boosted_keywords": ["appointment", "booking", "cancel"],
    "configuration_endpoint": {
      "url": "https://myapp.com/webhooks/phonic-config",
      "headers": {
        "Authorization": "Bearer 123"
      },
      "timeout_ms": 10000
    },
    "supervisor": null,
    "llm_settings": null,
    "vad_prebuffer_duration_ms": 2000,
    "vad_min_speech_duration_ms": 25,
    "vad_min_silence_duration_ms": 200,
    "vad_threshold": 0.5,
    "downstream_websocket_url": null,
    "experimental_params": null
  }
}
```

### Update Agent

```python
from phonic.client import Agents

agents = Agents(api_key=API_KEY)

# Update agent by name
agents.update(
    "booking-support-agent",
    project="main",
    timezone="America/New_York",
    system_prompt="You are a helpful support agent. Address customers as {{customer_name}} and inform them our support hours are {{support_hours}}. Be concise.",
    voice_id="sarah",
    template_variables={
        "customer_name": {"default_value": "dear customer"},
        "support_hours": {"default_value": "9 AM to 5 PM"}
    },
    tools=["keypad_input", "natural_conversation_ending"],
    no_input_poke_sec=45
)

# Update agent by ID
agents.update(
    "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
    voice_id="sarah",
    welcome_message="Hello! How can I assist you today?"
)
```

### Delete Agent

```python
from phonic.client import Agents

agents = Agents(api_key=API_KEY)

# Delete agent by ID
agents.delete("agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")

# Delete agent by name
agents.delete("booking-support-agent", project="main")
```

## 🛠️ Tools

### Create Tool

Tools can be either webhook-based (HTTP endpoints) or WebSocket-based.

#### Create webhook tool

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

webhook_tool = tools.create(
    name="next_invoice",
    description="Returns the next invoice of the given user",
    type="custom_webhook",
    execution_mode="sync",  # Only "sync" is supported for webhook tools
    project="main",  # Optional, defaults to server default ("main")
    endpoint_method="POST",
    endpoint_url="https://myapp.com/webhooks/next-invoice",
    endpoint_headers={
        "Authorization": "Bearer 123",
        "Content-Type": "application/json"
    },
    endpoint_timeout_ms=20000,  # Optional, defaults to 15000
    parameters=[
        {
            "type": "string",
            "name": "user",
            "description": "Full name of the user to get the invoice for",
            "is_required": True
        },
        {
            "type": "array",
            "item_type": "string",
            "name": "invoice_items",
            "description": "List of invoice items",
            "is_required": False
        },
        {
            "type": "number",
            "name": "invoice_total",
            "description": "Total invoice amount in USD",
            "is_required": True
        }
    ]
)
```

#### Create WebSocket tool

WebSocket tools allow you to handle tool execution on the client side through the WebSocket connection. When the assistant calls a WebSocket tool, you'll receive a `tool_call` message and must respond with the result.

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

websocket_tool = tools.create(
    name="get_product_recommendations",
    description="Gets personalized product recommendations",
    type="custom_websocket",
    execution_mode="async",
    project="main",  # Optional, defaults to server default ("main")
    tool_call_output_timeout_ms=5000,  # Optional, defaults to 15000
    parameters=[
        {
            "type": "string",
            "name": "category",
            "description": "Product category (e.g., 'handbags', 'shoes', 'electronics')",
            "is_required": True
        }
    ]
)
```

To use this tool in a conversation, add it to your agent:

```python
from phonic.client import Agents, PhonicSTSClient

# When creating an agent
agent = agents.create(
    name="shopping-assistant",
    tools=["get_product_recommendations"],
    # ... other config
)

# Handle the tool call when it's invoked
client = PhonicSTSClient(api_key=API_KEY)

async def handle_messages():
    async for message in client.sts(
        agent="shopping-assistant",
        tools=["get_product_recommendations"]
    ):
        if message["type"] == "tool_call" and message["tool_name"] == "get_product_recommendations":
            category = message["parameters"]["category"]
            
            # Execute your business logic
            recommendations = await fetch_recommendations(category)
            
            # Send the result back
            await client.send_tool_call_output(
                tool_call_id=message["tool_call_id"],
                output={
                    "products": recommendations,
                    "total": len(recommendations)
                }
            )
```

#### Response Format

```json
{
  "id": "tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
  "name": "next_invoice"
}
```

### List Tools

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

# List all tools for the default project ("main")
tools_list = tools.list()

# List tools for a specific project
tools_list = tools.list(project="customer-support")
```

#### Response Format

```json
{
  "tools": [
    {
      "id": "tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
      "project": {
        "id": "proj_fc86489d-fa2d-4921-8f14-7b95a926d481",
        "name": "main"
      },
      "name": "next_invoice",
      "description": "Returns the next invoice of the given user",
      "type": "custom_webhook",
      "execution_mode": "sync",
      "endpoint_url": "https://myapp.com/webhooks/next-invoice",
      "endpoint_method": "POST",
      "endpoint_headers": {
        "Authorization": "Bearer 123",
        "Content-Type": "application/json"
      },
      "endpoint_timeout_ms": 20000,
      "parameters": [
        {
          "type": "string",
          "name": "user",
          "description": "Full name of the user to get the invoice for",
          "is_required": true
        },
        {
          "type": "array",
          "item_type": "string",
          "name": "invoice_items",
          "description": "List of invoice items",
          "is_required": false
        },
        {
          "type": "number",
          "name": "invoice_total",
          "description": "Total invoice amount in USD",
          "is_required": true
        }
      ]
    }
  ]
}
```

### Get Tool

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

# Get tool by ID (works across all projects)
tool = tools.get("tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")

# Get tool by name (uses default project)
tool = tools.get("next_invoice")

# Get tool by name in specific project
tool = tools.get("next_invoice", project="customer-support")
```

#### Response Format

```json
{
  "tool": {
    "id": "tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
    "project": {
      "id": "proj_fc86489d-fa2d-4921-8f14-7b95a926d481",
      "name": "main"
    },
    "name": "next_invoice",
    "description": "Returns the next invoice of the given user",
    "type": "custom_webhook",
    "execution_mode": "sync",
    "endpoint_url": "https://myapp.com/webhooks/next-invoice",
    "endpoint_method": "POST",
    "endpoint_headers": {
      "Authorization": "Bearer 123",
      "Content-Type": "application/json"
    },
    "endpoint_timeout_ms": 20000,
    "parameters": [
      {
        "type": "string",
        "name": "user",
        "description": "Full name of the user to get the invoice for",
        "is_required": true
      },
      {
        "type": "array",
        "item_type": "string",
        "name": "invoice_items",
        "description": "List of invoice items",
        "is_required": false
      },
      {
        "type": "number",
        "name": "invoice_total",
        "description": "Total invoice amount in USD",
        "is_required": true
      }
    ]
  }
}
```

### Update Tool

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

# Update webhook tool by name (uses default project)
tools.update(
    "next_invoice",
    name="next_invoice_updated",
    description="Updated description",
    type="custom_webhook",
    execution_mode="sync",
    endpoint_method="POST",
    endpoint_url="https://myapp.com/webhooks/next-invoice-updated",
    endpoint_headers={
        "Authorization": "Bearer 456"
    },
    endpoint_timeout_ms=30000,
    parameters=[
        {
            "type": "string",
            "name": "user",
            "description": "Full name of the user to get the invoice for",
            "is_required": True
        },
        {
            "type": "array",
            "item_type": "string",
            "name": "invoice_items",
            "description": "List of invoice items",
            "is_required": True
        },
        {
            "type": "number",
            "name": "invoice_total",
            "description": "Total invoice amount in USD",
            "is_required": True
        }
    ]
)

# Update tool by name in specific project
tools.update(
    "next_invoice",
    project="customer-support",
    description="Updated description for customer support project"
)

# For WebSocket tools, use tool_call_output_timeout_ms instead of endpoint fields
tools.update(
    "get_product_recommendations",
    description="Updated product recommendation tool",
    tool_call_output_timeout_ms=7000
)
```

### Delete Tool

Deletes a tool by ID or name.

```python
from phonic.client import Tools

tools = Tools(api_key=API_KEY)

# Delete tool by ID (works across all projects)
tools.delete("tool_12cf6e88-c254-4d3e-a149-ddf1bdd2254c")

# Delete tool by name (uses default project)
tools.delete("next_invoice")

# Delete tool by name in specific project
tools.delete("next_invoice", project="customer-support")
```

## 🎤 Voices

```python
from phonic.client import get_voices

voices = get_voices(api_key=API_KEY)
```

### Response Format

```json
[
  {
    "id": "grant",
    "name": "Grant",
    "description": null
  }
]
```

## 💬 Conversations

### List Conversations

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# List conversations with filters
results = conversations.list(
    project="main",
    duration_min=10,  # seconds
    duration_max=20,  # seconds
    started_at_min="2025-04-17",  # 00:00:00 UTC time is assumed
    started_at_max="2025-09-05T10:30:00.000Z"
)
```

#### Response Format

```json
{
  "conversations": [
    {
      "id": "conv_b1804883-5be4-42fe-b1cf-aa84450d5c84",
      "external_id": "CAdb9c032c809fec7feb932ea4c96d71e1",
      "project": {
        "id": "proj_f640a76e-a649-4232-a8eb-c97f3f9cb3f8",
        "name": "main"
      },
      "agent": {
        "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
        "name": "booking-support-agent"
      },
      "status": "completed",
      "started_at": "2025-04-20T14:30:00.000Z",
      "ended_at": "2025-04-20T14:30:15.000Z",
      "duration": 15,
      "phone_number": "+12345678901",
      "summary": "Customer inquiry about appointment booking"
    }
  ],
  "pagination": {
    "next_cursor": "eyJzdGFydGVkX2F0IjoiMjAyNS0wNC0yMFQxNDozMDowMC4wMDBaIn0=",
    "prev_cursor": null
  }
}
```

### Get Conversation by ID

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# Get conversation by ID
conversation = conversations.get("conv_b1804883-5be4-42fe-b1cf-aa84450d5c84")
```

#### Response Format

```json
{
  "conversation": {
    "id": "conv_b1804883-5be4-42fe-b1cf-aa84450d5c84",
    "external_id": "CAdb9c032c809fec7feb932ea4c96d71e1",
    "project": {
      "id": "proj_f640a76e-a649-4232-a8eb-c97f3f9cb3f8",
      "name": "main"
    },
    "agent": {
      "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
      "name": "booking-support-agent"
    },
    "status": "completed",
    "started_at": "2025-04-20T14:30:00.000Z",
    "ended_at": "2025-04-20T14:30:15.000Z",
    "duration": 15,
    "phone_number": "+12345678901",
    "summary": "Customer inquiry about appointment booking",
    "transcript": [
      {
        "speaker": "agent",
        "text": "Hello! How can I help you today?",
        "timestamp": "2025-04-20T14:30:02.000Z"
      },
      {
        "speaker": "user",
        "text": "I'd like to book an appointment",
        "timestamp": "2025-04-20T14:30:05.000Z"
      }
    ]
  }
}
```

### Get Conversation by External ID

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# Get conversation by external ID
conversation = conversations.get_by_external_id("CAdb9c032c809fec7feb932ea4c96d71e1", project="main")
```

#### Response Format

```json
{
  "conversation": {
    "id": "conv_b1804883-5be4-42fe-b1cf-aa84450d5c84",
    "external_id": "CAdb9c032c809fec7feb932ea4c96d71e1",
    "project": {
      "id": "proj_f640a76e-a649-4232-a8eb-c97f3f9cb3f8",
      "name": "main"
    },
    "agent": {
      "id": "agent_12cf6e88-c254-4d3e-a149-ddf1bdd2254c",
      "name": "booking-support-agent"
    },
    "status": "completed",
    "started_at": "2025-04-20T14:30:00.000Z",
    "ended_at": "2025-04-20T14:30:15.000Z",
    "duration": 15,
    "phone_number": "+12345678901",
    "summary": "Customer inquiry about appointment booking",
    "transcript": [
      {
        "speaker": "agent",
        "text": "Hello! How can I help you today?",
        "timestamp": "2025-04-20T14:30:02.000Z"
      },
      {
        "speaker": "user",
        "text": "I'd like to book an appointment",
        "timestamp": "2025-04-20T14:30:05.000Z"
      }
    ]
  }
}
```

### 📞 Outbound Calls

You can initiate outbound calls programmatically using the `outbound_call` method:

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# Basic outbound call
result = conversations.outbound_call(
    to_phone_number="+12345678901",
    system_prompt="You are calling to confirm an appointment scheduled for tomorrow at 2 PM.",
    welcome_message="Hello, this is a confirmation call from ABC Medical Center."
)

# Make an outbound call using an existing agent
result = conversations.outbound_call(
    to_phone_number="+12345678901",
    agent="booking-support-agent",
    template_variables={
        "customer_name": "John Smith",
        "business_name": "ABC Medical Center"
    }
)
```

#### Response Format

```json
{
  "conversation_id": "conv_b1804883-5be4-42fe-b1cf-aa84450d5c84"
}
```

### 📄 Pagination

Handle pagination when listing conversations:

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# Handle pagination manually
results = conversations.list(
    project="main",
    started_at_min="2025-01-01",
    started_at_max="2025-03-01",
    duration_min=0,
    duration_max=120,
    limit=50
)

next_cursor = results.get('pagination')['next_cursor']
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
```

### 📝 Evaluation Prompts

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# List evaluation prompts for a project
prompts = conversations.list_evaluation_prompts(project="main")

# Create a new evaluation prompt
new_prompt = conversations.create_evaluation_prompt(
    project="main",
    name="customer_issue_resolved",
    prompt="Did the agent resolve the customer's issue?"
)

# Execute an evaluation on a conversation
evaluation = conversations.execute_evaluation(
    conversation_id=conversation_id,
    prompt_id=prompt_id
)
```

### 📋 Summaries

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# Generate a summary of the conversation
summary = conversations.summarize_conversation(conversation_id)
```

### 📊 Extraction Schemas

The Phonic API provides extraction capabilities to automatically extract structured data from conversations. You can define custom extraction schemas with specific fields and data types, then apply them to conversations to extract relevant information.

```python
from phonic.client import Conversations, ExtractionSchemas

conversations = Conversations(api_key=API_KEY)
extraction_schemas = ExtractionSchemas(api_key=API_KEY)

# List extraction schemas for a project
schemas = extraction_schemas.list(project="main")

# Create a new extraction schema
new_schema = extraction_schemas.create(
    project="main",
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

# Get a specific extraction schema by ID or name
schema = extraction_schemas.get("booking_details", project="main")
# Or by ID
schema = extraction_schemas.get("conv_extract_schema_12345")

# Update an extraction schema by ID or name
extraction_schemas.update(
    identifier="conv_extract_schema_12345",  # Schema ID
    project="main",
    name="updated_booking_details",
    prompt="Updated prompt for extracting booking information",
    fields=[
        {
            "name": "appointment_date",
            "type": "string",
            "description": "The date of the appointment in YYYY-MM-DD format",
        },
        {
            "name": "copay_amount",
            "type": "float",
            "description": "Amount of money the patient pays for the appointment",
        },
        {
            "name": "confirmed",
            "type": "bool",
            "description": "Whether the appointment was confirmed",
        },
    ]
)

# Update schema by name (partial update)
extraction_schemas.update(
    identifier="booking_details",  # Schema name
    project="main",
    prompt="Updated prompt only - fields remain unchanged"
)

# Delete an extraction schema by ID or name
extraction_schemas.delete(
    identifier="conv_extract_schema_12345",  # Schema ID
    project="main"
)

# Delete schema by name
extraction_schemas.delete(
    identifier="booking_details",  # Schema name
    project="main"
)

# Create an extraction using a schema
extraction = conversations.create_extraction(
    conversation_id=conversation_id,
    schema_id=new_schema["id"]
)

# List all extractions for a conversation
extractions_list = conversations.list_extractions(conversation_id)
```

#### Supported Field Types

Extraction schemas support the following field types:
- `string` - Text values
- `int` - Integer numbers
- `float` - Decimal numbers
- `bool` - Boolean values (true/false)
- `string[]` - Array of text values
- `int[]` - Array of integers
- `float[]` - Array of decimal numbers
- `bool[]` - Array of boolean values

### ❌ Cancel Conversations

```python
from phonic.client import Conversations

conversations = Conversations(api_key=API_KEY)

# Cancel an active conversation
result = conversations.cancel(conversation_id)
# Returns: {"success": true} on success
# Returns: {"error": {"message": <error message>}} on error
```

## 🐛 Troubleshooting

- `pyaudio` installation has a known issue where the `portaudio.h` file cannot be found. See [Stack Overflow](https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include) for OS-specific advice.
- Sometimes, when running the example speech-to-speech code for the first time, you may see a certificate verification failure. A solution for this is also documented in [Stack Overflow](https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate).
