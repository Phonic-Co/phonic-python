# Reference
<details><summary><code>client.<a href="src/phonic/client.py">get_agents</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all agents in a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_agents()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to list agents for.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_agents</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new agent in a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import (
    CreateAgentRequestConfigurationEndpoint,
    CreateAgentRequestTemplateVariablesValue,
    Phonic,
)

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_agents(
    name="support-agent",
    timezone="America/Los_Angeles",
    voice_id="sarah",
    audio_speed=1.0,
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": CreateAgentRequestTemplateVariablesValue(),
        "subject": CreateAgentRequestTemplateVariablesValue(
            default_value="Chess",
        ),
    },
    tools=[],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    boosted_keywords=["Load ID", "dispatch"],
    configuration_endpoint=CreateAgentRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={"Authorization": "Bearer token123"},
        timeout_ms=7000,
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — The name of the agent. Can only contain lowercase letters, numbers and hyphens. Must be unique within the project.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to create the agent in.
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `typing.Optional[typing.Literal["assign-automatically"]]` 
    
</dd>
</dl>

<dl>
<dd>

**timezone:** `typing.Optional[str]` — The timezone of the agent. Used to format system variables like `{{system_time}}`.
    
</dd>
</dl>

<dl>
<dd>

**voice_id:** `typing.Optional[str]` — The voice ID to use.
    
</dd>
</dl>

<dl>
<dd>

**audio_format:** `typing.Optional[CreateAgentRequestAudioFormat]` — The audio format of the agent.
    
</dd>
</dl>

<dl>
<dd>

**audio_speed:** `typing.Optional[float]` — The audio speed of the agent.
    
</dd>
</dl>

<dl>
<dd>

**welcome_message:** `typing.Optional[str]` — Message to play when the conversation starts. Can contain template variables like `{{customer_name}}`.
    
</dd>
</dl>

<dl>
<dd>

**system_prompt:** `typing.Optional[str]` — Instructions for the conversation. Can contain template variables like `{{subject}}`.
    
</dd>
</dl>

<dl>
<dd>

**template_variables:** `typing.Optional[typing.Dict[str, CreateAgentRequestTemplateVariablesValue]]` — Variables that can be used in the welcome message and the system prompt.
    
</dd>
</dl>

<dl>
<dd>

**tools:** `typing.Optional[typing.Sequence[CreateAgentRequestToolsItem]]` — Array of built-in or custom tool names to use.
    
</dd>
</dl>

<dl>
<dd>

**tasks:** `typing.Optional[typing.Sequence[Task]]` — Array of task objects with `name` and `description` fields.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_sec:** `typing.Optional[int]` — Number of seconds of silence before sending a poke message. `null` disables the poke message.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_text:** `typing.Optional[str]` — The message to send after the specified silence.
    
</dd>
</dl>

<dl>
<dd>

**no_input_end_conversation_sec:** `typing.Optional[int]` — Seconds of silence before ending the conversation.
    
</dd>
</dl>

<dl>
<dd>

**boosted_keywords:** `typing.Optional[typing.Sequence[str]]` — These words, or short phrases, will be more accurately recognized by the agent.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[CreateAgentRequestConfigurationEndpoint]` — When not `null`, at the beginning of the conversation the agent will make a POST request to this endpoint when to get configuration options.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">put_agents_upsert</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Upserts an agent by name. If an agent with the same name already exists, it will be updated. Otherwise, it will be created.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import (
    CreateAgentRequestConfigurationEndpoint,
    CreateAgentRequestTemplateVariablesValue,
    Phonic,
)

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.put_agents_upsert(
    name="support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sarah",
    audio_speed=1.0,
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": CreateAgentRequestTemplateVariablesValue(),
        "subject": CreateAgentRequestTemplateVariablesValue(
            default_value="Chess",
        ),
    },
    tools=[],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    boosted_keywords=["Load ID", "dispatch"],
    configuration_endpoint=CreateAgentRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={"Authorization": "Bearer token123"},
        timeout_ms=7000,
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — The name of the agent. Can only contain lowercase letters, numbers and hyphens. Must be unique within the project.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the agent.
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `typing.Optional[typing.Literal["assign-automatically"]]` 
    
</dd>
</dl>

<dl>
<dd>

**timezone:** `typing.Optional[str]` — The timezone of the agent. Used to format system variables like `{{system_time}}`.
    
</dd>
</dl>

<dl>
<dd>

**voice_id:** `typing.Optional[str]` — The voice ID to use.
    
</dd>
</dl>

<dl>
<dd>

**audio_format:** `typing.Optional[CreateAgentRequestAudioFormat]` — The audio format of the agent.
    
</dd>
</dl>

<dl>
<dd>

**audio_speed:** `typing.Optional[float]` — The audio speed of the agent.
    
</dd>
</dl>

<dl>
<dd>

**welcome_message:** `typing.Optional[str]` — Message to play when the conversation starts. Can contain template variables like `{{customer_name}}`.
    
</dd>
</dl>

<dl>
<dd>

**system_prompt:** `typing.Optional[str]` — Instructions for the conversation. Can contain template variables like `{{subject}}`.
    
</dd>
</dl>

<dl>
<dd>

**template_variables:** `typing.Optional[typing.Dict[str, CreateAgentRequestTemplateVariablesValue]]` — Variables that can be used in the welcome message and the system prompt.
    
</dd>
</dl>

<dl>
<dd>

**tools:** `typing.Optional[typing.Sequence[CreateAgentRequestToolsItem]]` — Array of built-in or custom tool names to use.
    
</dd>
</dl>

<dl>
<dd>

**tasks:** `typing.Optional[typing.Sequence[Task]]` — Array of task objects with `name` and `description` fields.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_sec:** `typing.Optional[int]` — Number of seconds of silence before sending a poke message. `null` disables the poke message.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_text:** `typing.Optional[str]` — The message to send after the specified silence.
    
</dd>
</dl>

<dl>
<dd>

**no_input_end_conversation_sec:** `typing.Optional[int]` — Seconds of silence before ending the conversation.
    
</dd>
</dl>

<dl>
<dd>

**boosted_keywords:** `typing.Optional[typing.Sequence[str]]` — These words, or short phrases, will be more accurately recognized by the agent.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[CreateAgentRequestConfigurationEndpoint]` — When not `null`, at the beginning of the conversation the agent will make a POST request to this endpoint when to get configuration options.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_agents_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns an agent by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_agents_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the agent to get.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the agent. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">delete_agents_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes an agent by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.delete_agents_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the agent to delete.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the agent. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">patch_agents_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates an agent by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import (
    Phonic,
    UpdateAgentRequestConfigurationEndpoint,
    UpdateAgentRequestTemplateVariablesValue,
)

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.patch_agents_name_or_id(
    name_or_id="nameOrId",
    name="updated-support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sarah",
    audio_speed=1.0,
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": UpdateAgentRequestTemplateVariablesValue(),
        "subject": UpdateAgentRequestTemplateVariablesValue(
            default_value="Chess",
        ),
    },
    tools=[],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    boosted_keywords=["Load ID", "dispatch"],
    configuration_endpoint=UpdateAgentRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={"Authorization": "Bearer token123"},
        timeout_ms=7000,
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the agent to update.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the agent. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — The name of the agent. Can only contain lowercase letters, numbers and hyphens. Must be unique within the project.
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `typing.Optional[typing.Literal["assign-automatically"]]` 
    
</dd>
</dl>

<dl>
<dd>

**timezone:** `typing.Optional[str]` — The timezone of the agent. Used to format system variables like `{{system_time}}`.
    
</dd>
</dl>

<dl>
<dd>

**voice_id:** `typing.Optional[str]` — The voice ID to use.
    
</dd>
</dl>

<dl>
<dd>

**audio_format:** `typing.Optional[UpdateAgentRequestAudioFormat]` — The audio format of the agent.
    
</dd>
</dl>

<dl>
<dd>

**audio_speed:** `typing.Optional[float]` — The audio speed of the agent.
    
</dd>
</dl>

<dl>
<dd>

**welcome_message:** `typing.Optional[str]` — Message to play when the conversation starts. Can contain template variables like `{{customer_name}}`.
    
</dd>
</dl>

<dl>
<dd>

**system_prompt:** `typing.Optional[str]` — Instructions for the conversation. Can contain template variables like `{{subject}}`.
    
</dd>
</dl>

<dl>
<dd>

**template_variables:** `typing.Optional[typing.Dict[str, UpdateAgentRequestTemplateVariablesValue]]` — Variables that can be used in the welcome message and the system prompt.
    
</dd>
</dl>

<dl>
<dd>

**tools:** `typing.Optional[typing.Sequence[UpdateAgentRequestToolsItem]]` — Array of built-in or custom tool names to use.
    
</dd>
</dl>

<dl>
<dd>

**tasks:** `typing.Optional[typing.Sequence[Task]]` — Array of task objects with `name` and `description` fields.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_sec:** `typing.Optional[int]` — Number of seconds of silence before sending a poke message. `null` disables the poke message.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_text:** `typing.Optional[str]` — The message to send after the specified silence.
    
</dd>
</dl>

<dl>
<dd>

**no_input_end_conversation_sec:** `typing.Optional[int]` — Seconds of silence before ending the conversation.
    
</dd>
</dl>

<dl>
<dd>

**boosted_keywords:** `typing.Optional[typing.Sequence[str]]` — These words, or short phrases, will be more accurately recognized by the agent.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[UpdateAgentRequestConfigurationEndpoint]` — When not `null`, at the beginning of the conversation the agent will make a POST request to this endpoint when to get configuration options.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_tools</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all custom tools for the organization.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_tools()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to list tools for.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_tools</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new tool in a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic, ToolParameter

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_tools(
    name="check_inventory",
    description="Checks product inventory levels",
    type="custom_websocket",
    execution_mode="async",
    parameters=[
        ToolParameter(
            type="string",
            name="product_id",
            description="The product ID to check",
            is_required=True,
        )
    ],
    tool_call_output_timeout_ms=5000,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — The name of the tool. Must be snake_case and unique within the organization.
    
</dd>
</dl>

<dl>
<dd>

**description:** `str` — A description of what the tool does.
    
</dd>
</dl>

<dl>
<dd>

**type:** `CreateToolRequestType` — The type of tool.
    
</dd>
</dl>

<dl>
<dd>

**execution_mode:** `CreateToolRequestExecutionMode` — Mode of operation.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to create the tool in.
    
</dd>
</dl>

<dl>
<dd>

**parameters:** `typing.Optional[typing.Sequence[ToolParameter]]` — Array of parameter definitions.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_method:** `typing.Optional[typing.Literal["POST"]]` — Required for webhook tools.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_url:** `typing.Optional[str]` — Required for webhook tools.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_headers:** `typing.Optional[typing.Dict[str, str]]` — Optional headers for webhook tools.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_timeout_ms:** `typing.Optional[int]` — Timeout for webhook tools.
    
</dd>
</dl>

<dl>
<dd>

**tool_call_output_timeout_ms:** `typing.Optional[int]` — Timeout for WebSocket tool responses.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_tools_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a tool by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_tools_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the tool to get.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the tool. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">delete_tools_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a tool by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.delete_tools_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the tool to delete.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the tool. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">patch_tools_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates a tool by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.patch_tools_name_or_id(
    name_or_id="nameOrId",
    description="Updated description for booking appointments with enhanced features",
    endpoint_headers={"Authorization": "Bearer updated_token456"},
    endpoint_timeout_ms=7000,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the tool to update.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the tool. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — The name of the tool. Must be snake_case and unique within the organization.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — A description of what the tool does.
    
</dd>
</dl>

<dl>
<dd>

**type:** `typing.Optional[UpdateToolRequestType]` — The type of tool.
    
</dd>
</dl>

<dl>
<dd>

**execution_mode:** `typing.Optional[UpdateToolRequestExecutionMode]` — Mode of operation.
    
</dd>
</dl>

<dl>
<dd>

**parameters:** `typing.Optional[typing.Sequence[ToolParameter]]` — Array of parameter definitions.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_method:** `typing.Optional[typing.Literal["POST"]]` 
    
</dd>
</dl>

<dl>
<dd>

**endpoint_url:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**endpoint_headers:** `typing.Optional[typing.Dict[str, str]]` 
    
</dd>
</dl>

<dl>
<dd>

**endpoint_timeout_ms:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**tool_call_output_timeout_ms:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_extraction_schemas</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all extraction schemas in a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_extraction_schemas()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to list extraction schemas for.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_extraction_schemas</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new extraction schema in a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import ExtractionField, Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_extraction_schemas(
    name="Appointment details",
    prompt="Dates should be in `9 Apr 2025` format. Prices should be in $150.00 format.",
    fields=[
        ExtractionField(
            name="Date",
            type="string",
            description="The date of the appointment",
        ),
        ExtractionField(
            name="Copay",
            type="string",
            description="Amount of money the patient pays for the appointment",
        ),
        ExtractionField(
            name="Confirmed as booked",
            type="bool",
            description="Is the appointment confirmed as booked?",
        ),
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — A name for the extraction schema.
    
</dd>
</dl>

<dl>
<dd>

**prompt:** `str` — Instructions for how to extract data from conversations.
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Sequence[ExtractionField]` — Array of field definitions.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to create the extraction schema in.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_extraction_schemas_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns an extraction schema by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_extraction_schemas_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the extraction schema to get.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the extraction schema. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">delete_extraction_schemas_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes an extraction schema by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.delete_extraction_schemas_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the extraction schema to delete.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the extraction schema. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">patch_extraction_schemas_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates an extraction schema by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import ExtractionField, Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.patch_extraction_schemas_name_or_id(
    name_or_id="nameOrId",
    name="Updated appointment details",
    prompt="Updated extraction instructions. Dates should be in `9 Apr 2025` format.",
    fields=[
        ExtractionField(
            name="Date",
            type="string",
            description="The date of the appointment",
        ),
        ExtractionField(
            name="Time",
            type="string",
            description="The time of the appointment",
        ),
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the extraction schema to update.
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the extraction schema. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — A name for the extraction schema.
    
</dd>
</dl>

<dl>
<dd>

**prompt:** `typing.Optional[str]` — Instructions for how to extract data from conversations.
    
</dd>
</dl>

<dl>
<dd>

**fields:** `typing.Optional[typing.Sequence[ExtractionField]]` — Array of field definitions.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_voices</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all available voices for a model.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_voices()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_voices_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a voice by ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_voices_id(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the voice to get.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_conversations</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns conversations with optional filtering.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_conversations()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to list conversations for.
    
</dd>
</dl>

<dl>
<dd>

**external_id:** `typing.Optional[str]` — Filter by external ID to get a specific conversation.
    
</dd>
</dl>

<dl>
<dd>

**duration_min:** `typing.Optional[int]` — Minimum duration in seconds.
    
</dd>
</dl>

<dl>
<dd>

**duration_max:** `typing.Optional[int]` — Maximum duration in seconds.
    
</dd>
</dl>

<dl>
<dd>

**started_at_min:** `typing.Optional[str]` — Minimum start date/time. Valid examples: `2025-04-17`, `2025-04-17T02:48:52.708Z`
    
</dd>
</dl>

<dl>
<dd>

**started_at_max:** `typing.Optional[str]` — Maximum start date/time. Valid examples: `2025-04-17`, `2025-04-17T02:48:52.708Z`
    
</dd>
</dl>

<dl>
<dd>

**before:** `typing.Optional[str]` — Cursor for pagination (before).
    
</dd>
</dl>

<dl>
<dd>

**after:** `typing.Optional[str]` — Cursor for pagination (after).
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of conversations to return.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_conversations_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a conversation by ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_conversations_id(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to get.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_conversations_id_cancel</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Cancels an active conversation.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_conversations_id_cancel(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to cancel.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_conversations_id_analysis</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns an analysis of the specified conversation.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_conversations_id_analysis(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to analyze.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_conversations_id_extractions</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all extractions for a conversation.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_conversations_id_extractions(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to get extractions for.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_conversations_id_extractions</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Extracts data from a conversation using a schema.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_conversations_id_extractions(
    id="id",
    schema_id="conv_extract_schema_6458e4ac-533c-4bdf-8e6d-c2f06f87fd5c",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to extract data from.
    
</dd>
</dl>

<dl>
<dd>

**schema_id:** `str` — ID of the extraction schema to use.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_conversations_id_evals</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all evaluations for a conversation.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_conversations_id_evals(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to get evaluations for.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_conversations_id_evals</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Evaluates a conversation using an evaluation prompt.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_conversations_id_evals(
    id="id",
    prompt_id="conv_eval_prompt_d7cfe45d-35db-4ef6-a254-81ab1da76ce0",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the conversation to evaluate.
    
</dd>
</dl>

<dl>
<dd>

**prompt_id:** `str` — ID of the evaluation prompt to use.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_conversations_outbound_call</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Initiates a call to a given phone number using Phonic's Twilio account.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import OutboundCallConfig, Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_conversations_outbound_call(
    to_phone_number="+19189397081",
    config=OutboundCallConfig(
        agent="support-agent",
        welcome_message="Hi {{customer_name}}. How can I help you today?",
        system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
        template_variables={"customer_name": "David", "subject": "Chess"},
        voice_id="sarah",
        no_input_poke_sec=30,
        no_input_poke_text="Are you still there?",
        no_input_end_conversation_sec=180,
        boosted_keywords=["Load ID", "dispatch"],
        tools=[],
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**to_phone_number:** `str` — The phone number to call in E.164 format.
    
</dd>
</dl>

<dl>
<dd>

**config:** `typing.Optional[OutboundCallConfig]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_conversations_sip_outbound_call</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Initiates a SIP outbound call using user-supplied SIP credentials in headers.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_conversations_sip_outbound_call(
    sip_address="X-Sip-Address",
    from_phone_number="from_phone_number",
    to_phone_number="to_phone_number",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**sip_address:** `str` — SIP address of the user's SIP trunk. Required.
    
</dd>
</dl>

<dl>
<dd>

**from_phone_number:** `str` — Caller ID phone number in E.164 format.
    
</dd>
</dl>

<dl>
<dd>

**to_phone_number:** `str` — Destination phone number in E.164 format.
    
</dd>
</dl>

<dl>
<dd>

**token:** `typing.Optional[str]` — Optional session token used for STS authorization.
    
</dd>
</dl>

<dl>
<dd>

**downstream_websocket_url:** `typing.Optional[str]` — Optional downstream STS WebSocket URL to override the default.
    
</dd>
</dl>

<dl>
<dd>

**sip_auth_username:** `typing.Optional[str]` — SIP auth username, if your provider requires it.
    
</dd>
</dl>

<dl>
<dd>

**sip_auth_password:** `typing.Optional[str]` — SIP auth password, if your provider requires it.
    
</dd>
</dl>

<dl>
<dd>

**config:** `typing.Optional[OutboundCallConfig]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_projects</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all projects in a workspace.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_projects()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_projects</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new project in a workspace.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_projects(
    name="customer-support",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — The name of the project. Can only contain lowercase letters, numbers and hyphens. Must be unique within the workspace.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_projects_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a project by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_projects_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the project to get.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">delete_projects_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a project by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.delete_projects_name_or_id(
    name_or_id="nameOrId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the project to delete.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">patch_projects_name_or_id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates a project by name or ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.patch_projects_name_or_id(
    name_or_id="nameOrId",
    name="updated-customer-support",
    default_agent="another-agent",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name_or_id:** `str` — The name or the ID of the project to update.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — The name of the project. Can only contain lowercase letters, numbers and hyphens. Must be unique within the workspace.
    
</dd>
</dl>

<dl>
<dd>

**default_agent:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">get_projects_id_conversation_eval_prompts</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all conversation evaluation prompts for a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.get_projects_id_conversation_eval_prompts(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/phonic/client.py">post_projects_id_conversation_eval_prompts</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new conversation evaluation prompt for a project.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from phonic import Phonic

client = Phonic(
    api_key="YOUR_API_KEY",
)
client.post_projects_id_conversation_eval_prompts(
    id="id",
    name="test_prompt",
    prompt="The assistant used the word chocolate in the conversation",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the project.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — A useful name for referring to this prompt.
    
</dd>
</dl>

<dl>
<dd>

**prompt:** `str` — Actual evaluation prompt text to evaluate conversations with.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

