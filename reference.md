# Reference
<details><summary><code>client.<a href="src/phonic/client.py">create</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.create(
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

## Agents
<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">list</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.agents.list()

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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">create</a>(...)</code></summary>
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
from phonic import Phonic
from phonic.agents import (
    CreateAgentRequestConfigurationEndpoint,
    CreateAgentRequestTemplateVariablesValue,
)

client = Phonic(
    token="YOUR_TOKEN",
)
client.agents.create(
    name="support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sarah",
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">upsert</a>(...)</code></summary>
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
from phonic import Phonic
from phonic.agents import (
    UpsertAgentRequestConfigurationEndpoint,
    UpsertAgentRequestTemplateVariablesValue,
)

client = Phonic(
    token="YOUR_TOKEN",
)
client.agents.upsert(
    name="support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sarah",
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": UpsertAgentRequestTemplateVariablesValue(),
        "subject": UpsertAgentRequestTemplateVariablesValue(
            default_value="Chess",
        ),
    },
    tools=[],
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    boosted_keywords=["Load ID", "dispatch"],
    configuration_endpoint=UpsertAgentRequestConfigurationEndpoint(
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

**project:** `typing.Optional[str]` — The name of the project containing the agent.
    
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

**audio_format:** `typing.Optional[UpsertAgentRequestAudioFormat]` — The audio format of the agent.
    
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

**template_variables:** `typing.Optional[typing.Dict[str, UpsertAgentRequestTemplateVariablesValue]]` — Variables that can be used in the welcome message and the system prompt.
    
</dd>
</dl>

<dl>
<dd>

**tools:** `typing.Optional[typing.Sequence[UpsertAgentRequestToolsItem]]` — Array of built-in or custom tool names to use.
    
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

**configuration_endpoint:** `typing.Optional[UpsertAgentRequestConfigurationEndpoint]` — When not `null`, at the beginning of the conversation the agent will make a POST request to this endpoint when to get configuration options.
    
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">get</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.agents.get(
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">delete</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.agents.delete(
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">update</a>(...)</code></summary>
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
from phonic import Phonic
from phonic.agents import (
    UpdateAgentRequestConfigurationEndpoint,
    UpdateAgentRequestTemplateVariablesValue,
)

client = Phonic(
    token="YOUR_TOKEN",
)
client.agents.update(
    name_or_id="nameOrId",
    name="updated-support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sarah",
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

## Conversations
<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">outbound_call</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Initiates a call to a given phone number.
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
    token="YOUR_TOKEN",
)
client.conversations.outbound_call(
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

## Projects
<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">list</a>()</code></summary>
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
    token="YOUR_TOKEN",
)
client.projects.list()

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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">get</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.projects.get(
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">delete</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.projects.delete(
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">update</a>(...)</code></summary>
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
    token="YOUR_TOKEN",
)
client.projects.update(
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

