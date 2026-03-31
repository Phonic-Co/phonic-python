# Reference
## Agents
<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">list</a>(...) -> AgentsListResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">create</a>(...) -> AgentsCreateResponse</code></summary>
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
from phonic import Phonic, CreateAgentRequestTemplateVariablesValue, CreateAgentRequestConfigurationEndpoint
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.create(
    project="main",
    name="support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sabrina",
    audio_speed=1,
    background_noise_level=0,
    generate_welcome_message=False,
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": CreateAgentRequestTemplateVariablesValue(
            default_value="David",
        ),
        "subject": CreateAgentRequestTemplateVariablesValue(
            default_value="Chess",
        )
    },
    tools=[
        "keypad_input"
    ],
    generate_no_input_poke_text=False,
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    default_language="en",
    additional_languages=[
        "es"
    ],
    multilingual_mode="request",
    boosted_keywords=[
        "Load ID",
        "dispatch"
    ],
    min_words_to_interrupt=1,
    configuration_endpoint=CreateAgentRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={
            "Authorization": "Bearer token123"
        },
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

**request:** `CreateAgentRequest` 
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project to create the agent in.
    
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">upsert</a>(...) -> AgentsUpsertResponse</code></summary>
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
from phonic import Phonic, CreateAgentRequestTemplateVariablesValue, CreateAgentRequestConfigurationEndpoint
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.upsert(
    project="main",
    name="support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sabrina",
    audio_speed=1,
    background_noise_level=0,
    generate_welcome_message=False,
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": CreateAgentRequestTemplateVariablesValue(
            default_value="David",
        ),
        "subject": CreateAgentRequestTemplateVariablesValue(
            default_value="Chess",
        )
    },
    tools=[
        "keypad_input"
    ],
    generate_no_input_poke_text=False,
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    default_language="en",
    additional_languages=[
        "es"
    ],
    multilingual_mode="request",
    boosted_keywords=[
        "Load ID",
        "dispatch"
    ],
    min_words_to_interrupt=1,
    configuration_endpoint=CreateAgentRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={
            "Authorization": "Bearer token123"
        },
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

**phone_number:** `typing.Optional[CreateAgentRequestPhoneNumber]` — When set to `null`, the agent will not be associated with a phone number. When set to `"assign-automatically"`, the agent will be assigned a random phone number. When set to `"custom"`, you must provide `custom_phone_numbers`.
    
</dd>
</dl>

<dl>
<dd>

**custom_phone_number:** `typing.Optional[str]` — The custom phone number to use for the agent in E.164 format (e.g., +1234567890). This field is deprecated. Use `custom_phone_numbers` instead.
    
</dd>
</dl>

<dl>
<dd>

**custom_phone_numbers:** `typing.Optional[typing.List[str]]` — Array of custom phone numbers in E.164 format (e.g., ["+1234567890", "+0987654321"]). The agent will be able to receive phone calls on any of these numbers. Required when `phone_number` is set to `"custom"`. All phone numbers must be unique.
    
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

**background_noise_level:** `typing.Optional[float]` — The background noise level of the agent.
    
</dd>
</dl>

<dl>
<dd>

**background_noise:** `typing.Optional[CreateAgentRequestBackgroundNoise]` — The background noise type. Can be "office", "call-center", "coffee-shop", or null.
    
</dd>
</dl>

<dl>
<dd>

**generate_welcome_message:** `typing.Optional[bool]` — When `true`, the welcome message will be automatically generated and the `welcome_message` field will be ignored.
    
</dd>
</dl>

<dl>
<dd>

**welcome_message:** `typing.Optional[str]` — Message to play when the conversation starts. Can contain template variables like `{{customer_name}}`. Ignored when `generate_welcome_message` is `true`.
    
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

**tools:** `typing.Optional[typing.List[CreateAgentRequestToolsItem]]` — Array of built-in or custom tool names to use.
    
</dd>
</dl>

<dl>
<dd>

**tasks:** `typing.Optional[typing.List[Task]]` — Array of task objects with `name` and `description` fields.
    
</dd>
</dl>

<dl>
<dd>

**generate_no_input_poke_text:** `typing.Optional[bool]` — Whether to have the no-input poke text be generated by AI.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_sec:** `typing.Optional[int]` — Number of seconds of silence before sending a poke message. `null` disables the poke message.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_text:** `typing.Optional[str]` — The message to send after the specified silence. Ignored when generate_no_input_poke_text is true.
    
</dd>
</dl>

<dl>
<dd>

**no_input_end_conversation_sec:** `typing.Optional[int]` — Seconds of silence before ending the conversation.
    
</dd>
</dl>

<dl>
<dd>

**default_language:** `typing.Optional[LanguageCode]` — ISO 639-1 language code that sets the agent's default language to recognize and speak. Welcome message and no input poke text should be in this language.
    
</dd>
</dl>

<dl>
<dd>

**additional_languages:** `typing.Optional[typing.List[LanguageCode]]` — Array of additional ISO 639-1 language codes that the agent should be able to recognize and speak. Should not include `default_language`.
    
</dd>
</dl>

<dl>
<dd>

**languages:** `typing.Optional[typing.List[LanguageCode]]` — Array of ISO 639-1 language codes that the agent should be able to recognize. This field is deprecated. Use `default_language` and `additional_languages` instead.
    
</dd>
</dl>

<dl>
<dd>

**multilingual_mode:** `typing.Optional[CreateAgentRequestMultilingualMode]` — If `"auto"`, each user audio is automatically identified for the language to respond in. If `"request"`, user must request to change language (recommended).
    
</dd>
</dl>

<dl>
<dd>

**boosted_keywords:** `typing.Optional[typing.List[str]]` — These words, or short phrases, will be more accurately recognized by the agent.
    
</dd>
</dl>

<dl>
<dd>

**min_words_to_interrupt:** `typing.Optional[float]` — Minimum number of words required to interrupt the assistant.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[CreateAgentRequestConfigurationEndpoint]` — When not `null`, at the beginning of the conversation the agent will make a POST request to this endpoint to get configuration options.
    
</dd>
</dl>

<dl>
<dd>

**inbound_rollout:** `typing.Optional[float]` — Float between 0.0 and 1.0 representing the percentage of inbound calls handled by Agent. Defaults to `1.0`. Requires `phone_number` to be set when less than 1.0.
    
</dd>
</dl>

<dl>
<dd>

**inbound_rollout_forward_phone_number:** `typing.Optional[str]` — E.164 formatted phone number where non-agent calls will be forwarded. Required when `inbound_rollout < 1.0`, must be `null` when `inbound_rollout = 1.0`. Defaults to `null`.
    
</dd>
</dl>

<dl>
<dd>

**vad_prebuffer_duration_ms:** `typing.Optional[float]` — Voice activity detection prebuffer duration in milliseconds.
    
</dd>
</dl>

<dl>
<dd>

**vad_min_speech_duration_ms:** `typing.Optional[float]` — Minimum speech duration for voice activity detection in milliseconds.
    
</dd>
</dl>

<dl>
<dd>

**vad_min_silence_duration_ms:** `typing.Optional[float]` — Minimum silence duration for voice activity detection in milliseconds.
    
</dd>
</dl>

<dl>
<dd>

**vad_threshold:** `typing.Optional[float]` — Voice activity detection threshold.
    
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">get</a>(...) -> AgentsGetResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.get(
    name_or_id="nameOrId",
    project="main",
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">delete</a>(...) -> AgentsDeleteResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.delete(
    name_or_id="nameOrId",
    project="main",
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">update</a>(...) -> AgentsUpdateResponse</code></summary>
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
from phonic.environment import PhonicEnvironment
from phonic.agents import UpdateAgentRequestTemplateVariablesValue, UpdateAgentRequestConfigurationEndpoint

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.update(
    name_or_id="nameOrId",
    project="main",
    name="updated-support-agent",
    phone_number="assign-automatically",
    timezone="America/Los_Angeles",
    voice_id="sabrina",
    audio_speed=1,
    background_noise_level=0,
    generate_welcome_message=False,
    welcome_message="Hi {{customer_name}}. How can I help you today?",
    system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
    template_variables={
        "customer_name": UpdateAgentRequestTemplateVariablesValue(
            default_value="David",
        ),
        "subject": UpdateAgentRequestTemplateVariablesValue(
            default_value="Chess",
        )
    },
    tools=[
        "keypad_input"
    ],
    generate_no_input_poke_text=False,
    no_input_poke_sec=30,
    no_input_poke_text="Are you still there?",
    default_language="en",
    additional_languages=[
        "es"
    ],
    multilingual_mode="request",
    boosted_keywords=[
        "Load ID",
        "dispatch"
    ],
    min_words_to_interrupt=1,
    configuration_endpoint=UpdateAgentRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={
            "Authorization": "Bearer token123"
        },
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

**phone_number:** `typing.Optional[UpdateAgentRequestPhoneNumber]` — When set to `null`, the agent will not be associated with a phone number anymore. When set to `"assign-automatically"`, the agent will be assigned a random phone number if it doesn't have one yet. If the agent already has a phone number, `"assign-automatically"` has no effect. When set to `"custom"`, you must provide `custom_phone_numbers`.
    
</dd>
</dl>

<dl>
<dd>

**custom_phone_number:** `typing.Optional[str]` — The custom phone number to use for the agent in E.164 format (e.g., +1234567890). This field is deprecated. Use `custom_phone_numbers` instead.
    
</dd>
</dl>

<dl>
<dd>

**custom_phone_numbers:** `typing.Optional[typing.List[str]]` — Array of custom phone numbers in E.164 format (e.g., ["+1234567890", "+0987654321"]). The agent will be able to receive phone calls on any of these numbers. Required when `phone_number` is set to `"custom"`. All phone numbers must be unique.
    
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

**background_noise_level:** `typing.Optional[float]` — The background noise level of the agent.
    
</dd>
</dl>

<dl>
<dd>

**background_noise:** `typing.Optional[UpdateAgentRequestBackgroundNoise]` — The background noise type. Can be "office", "call-center", "coffee-shop", or null.
    
</dd>
</dl>

<dl>
<dd>

**generate_welcome_message:** `typing.Optional[bool]` — When `true`, the welcome message will be automatically generated and the `welcome_message` field will be ignored.
    
</dd>
</dl>

<dl>
<dd>

**welcome_message:** `typing.Optional[str]` — Message to play when the conversation starts. Can contain template variables like `{{customer_name}}`. Ignored when `generate_welcome_message` is `true`.
    
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

**tools:** `typing.Optional[typing.List[UpdateAgentRequestToolsItem]]` — Array of built-in or custom tool names to use.
    
</dd>
</dl>

<dl>
<dd>

**tasks:** `typing.Optional[typing.List[Task]]` — Array of task objects with `name` and `description` fields.
    
</dd>
</dl>

<dl>
<dd>

**generate_no_input_poke_text:** `typing.Optional[bool]` — Whether to have the no-input poke text be generated by AI.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_sec:** `typing.Optional[int]` — Number of seconds of silence before sending a poke message. `null` disables the poke message.
    
</dd>
</dl>

<dl>
<dd>

**no_input_poke_text:** `typing.Optional[str]` — The message to send after the specified silence. Ignored when generate_no_input_poke_text is true.
    
</dd>
</dl>

<dl>
<dd>

**no_input_end_conversation_sec:** `typing.Optional[int]` — Seconds of silence before ending the conversation.
    
</dd>
</dl>

<dl>
<dd>

**default_language:** `typing.Optional[LanguageCode]` — ISO 639-1 language code that sets the agent's default language to recognize and speak. Welcome message and no input poke text should be in this language.
    
</dd>
</dl>

<dl>
<dd>

**additional_languages:** `typing.Optional[typing.List[LanguageCode]]` — Array of additional ISO 639-1 language codes that the agent should be able to recognize and speak. Should not include `default_language`.
    
</dd>
</dl>

<dl>
<dd>

**languages:** `typing.Optional[typing.List[LanguageCode]]` — Array of ISO 639-1 language codes that the agent should be able to recognize. This field is deprecated. Use `default_language` and `additional_languages` instead.
    
</dd>
</dl>

<dl>
<dd>

**multilingual_mode:** `typing.Optional[UpdateAgentRequestMultilingualMode]` — If `"auto"`, each user audio is automatically identified for the language to respond in. If `"request"`, user must request to change language (recommended).
    
</dd>
</dl>

<dl>
<dd>

**boosted_keywords:** `typing.Optional[typing.List[str]]` — These words, or short phrases, will be more accurately recognized by the agent.
    
</dd>
</dl>

<dl>
<dd>

**min_words_to_interrupt:** `typing.Optional[float]` — Minimum number of words required to interrupt the assistant.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[UpdateAgentRequestConfigurationEndpoint]` — When not `null`, at the beginning of the conversation the agent will make a POST request to this endpoint to get configuration options.
    
</dd>
</dl>

<dl>
<dd>

**inbound_rollout:** `typing.Optional[float]` — Float between 0.0 and 1.0 representing the percentage of inbound calls handled by Agent. Requires `phone_number` to be set when less than 1.0.
    
</dd>
</dl>

<dl>
<dd>

**inbound_rollout_forward_phone_number:** `typing.Optional[str]` — E.164 formatted phone number where non-agent calls will be forwarded. Required when `inbound_rollout < 1.0`, must be `null` when `inbound_rollout = 1.0`.
    
</dd>
</dl>

<dl>
<dd>

**vad_prebuffer_duration_ms:** `typing.Optional[float]` — Voice activity detection prebuffer duration in milliseconds.
    
</dd>
</dl>

<dl>
<dd>

**vad_min_speech_duration_ms:** `typing.Optional[float]` — Minimum speech duration for voice activity detection in milliseconds.
    
</dd>
</dl>

<dl>
<dd>

**vad_min_silence_duration_ms:** `typing.Optional[float]` — Minimum silence duration for voice activity detection in milliseconds.
    
</dd>
</dl>

<dl>
<dd>

**vad_threshold:** `typing.Optional[float]` — Voice activity detection threshold.
    
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">add_custom_phone_number</a>(...) -> AgentsAddCustomPhoneNumberResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a custom phone number to an agent. The user must configure their SIP trunk to point to Phonic's SIP server.
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
from phonic.environment import PhonicEnvironment
from phonic.agents import AgentsAddCustomPhoneNumberRequestConfigurationEndpoint

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.add_custom_phone_number(
    name_or_id="nameOrId",
    project="main",
    phone_number="+15551234567",
    configuration_endpoint=AgentsAddCustomPhoneNumberRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={
            "Authorization": "Bearer token123"
        },
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

**name_or_id:** `str` — The name or the ID of the agent.
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `str` — The E.164 formatted phone number to add (e.g., "+15551234567").
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the agent. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**sip_address:** `typing.Optional[str]` — SIP address of the user's SIP trunk. Optional, but if provided, all three SIP headers (X-Sip-Address, X-Sip-Auth-Username, X-Sip-Auth-Password) must be provided. When these headers are provided, call transfers from the agent will use the provided SIP details.
    
</dd>
</dl>

<dl>
<dd>

**sip_auth_username:** `typing.Optional[str]` — SIP auth username. Optional, but if provided, all three SIP headers (X-Sip-Address, X-Sip-Auth-Username, X-Sip-Auth-Password) must be provided. When these headers are provided, call transfers from the agent will use the provided SIP details.
    
</dd>
</dl>

<dl>
<dd>

**sip_auth_password:** `typing.Optional[str]` — SIP auth password. Optional, but if provided, all three SIP headers (X-Sip-Address, X-Sip-Auth-Username, X-Sip-Auth-Password) must be provided. When these headers are provided, call transfers from the agent will use the provided SIP details.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[AgentsAddCustomPhoneNumberRequestConfigurationEndpoint]` — When not `null`, the agent will call this endpoint to get configuration options for calls on this phone number.
    
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">delete_custom_phone_number</a>(...) -> AgentsDeleteCustomPhoneNumberResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a custom phone number from an agent.
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.delete_custom_phone_number(
    name_or_id="nameOrId",
    project="main",
    phone_number="+15551234567",
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

**name_or_id:** `str` — The name or the ID of the agent.
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `str` — The E.164 formatted phone number to remove (e.g., "+15551234567").
    
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

<details><summary><code>client.agents.<a href="src/phonic/agents/client.py">update_phone_number</a>(...) -> AgentsUpdatePhoneNumberResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates a phone number on an agent.
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
from phonic.environment import PhonicEnvironment
from phonic.agents import AgentsUpdatePhoneNumberRequestConfigurationEndpoint

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.agents.update_phone_number(
    name_or_id="nameOrId",
    project="main",
    phone_number="+15551234567",
    configuration_endpoint=AgentsUpdatePhoneNumberRequestConfigurationEndpoint(
        url="https://api.example.com/config",
        headers={
            "Authorization": "Bearer token123"
        },
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

**name_or_id:** `str` — The name or the ID of the agent.
    
</dd>
</dl>

<dl>
<dd>

**phone_number:** `str` — The E.164 formatted phone number to add (e.g., "+15551234567").
    
</dd>
</dl>

<dl>
<dd>

**project:** `typing.Optional[str]` — The name of the project containing the agent. Only used when `nameOrId` is a name.
    
</dd>
</dl>

<dl>
<dd>

**configuration_endpoint:** `typing.Optional[AgentsUpdatePhoneNumberRequestConfigurationEndpoint]` — When not `null`, the agent will call this endpoint to get configuration options for calls on this phone number.
    
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

## Tools
<details><summary><code>client.tools.<a href="src/phonic/tools/client.py">list</a>(...) -> ToolsListResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.tools.list(
    project="main",
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

<details><summary><code>client.tools.<a href="src/phonic/tools/client.py">create</a>(...) -> ToolsCreateResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.tools.create(
    project="main",
    name="context_printer",
    description="Gets the specific context for fixing our printer",
    type="custom_context",
    execution_mode="sync",
    parameters=[
        ToolParameter(
            type="string",
            name="name",
            description="description",
            is_required=True,
        )
    ],
    require_speech_before_tool_call=False,
    forbid_speech_after_tool_call=False,
    allow_tool_chaining=True,
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

**parameters:** `typing.Optional[typing.List[ToolParameter]]` 

Array of parameter definitions.
For `custom_webhook` tools with POST method, each parameter must include a `location` field.
For `custom_webhook` tools with GET method, `location` defaults to `"query_string"` if not specified.
For `custom_websocket`, `built_in_transfer_to_phone_number`, and `built_in_transfer_to_agent` tools, `location` must not be specified.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_method:** `typing.Optional[CreateToolRequestEndpointMethod]` — Required for webhook tools. HTTP method for the webhook endpoint.
    
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

**phone_number:** `typing.Optional[str]` — The E.164 formatted phone number to transfer calls to. Set to null if the agent should determine the phone number.
    
</dd>
</dl>

<dl>
<dd>

**dtmf:** `typing.Optional[str]` — DTMF digits to send after the transfer connects (e.g., "1234"). Defaults to null.
    
</dd>
</dl>

<dl>
<dd>

**use_agent_phone_number:** `typing.Optional[bool]` — When true, Phonic will transfer the call using the agent's phone number. When false, Phonic will transfer the call using the phone number of the party to whom the agent is connected. This is only available for built_in_transfer_to_phone_number tools.
    
</dd>
</dl>

<dl>
<dd>

**detect_voicemail:** `typing.Optional[bool]` — When true, Phonic will listen in and tell the user if the transfer hits voicemail. This is only available for built_in_transfer_to_phone_number tools when use_agent_phone_number is true.
    
</dd>
</dl>

<dl>
<dd>

**agents_to_transfer_to:** `typing.Optional[typing.List[str]]` — Array of agent names that the LLM can choose from when transferring. Required for built_in_transfer_to_agent tools. All agents must exist in the same project as the tool.
    
</dd>
</dl>

<dl>
<dd>

**require_speech_before_tool_call:** `typing.Optional[bool]` — When true, forces the agent to speak before executing the tool.
    
</dd>
</dl>

<dl>
<dd>

**wait_for_speech_before_tool_call:** `typing.Optional[bool]` — If true, the agent will wait to finish speaking before executing the tool. This is only available for custom_webhook and custom_websocket tools.
    
</dd>
</dl>

<dl>
<dd>

**forbid_speech_after_tool_call:** `typing.Optional[bool]` — When true, forbids the agent from speaking after executing the tool. Available for custom_context, custom_webhook and custom_websocket tools.
    
</dd>
</dl>

<dl>
<dd>

**allow_tool_chaining:** `typing.Optional[bool]` — When true, allows the agent to chain and execute other tools after executing the tool. Available for custom_context, custom_webhook and custom_websocket tools.
    
</dd>
</dl>

<dl>
<dd>

**wait_for_response:** `typing.Optional[bool]` — The agent doesn't typically wait for the response of async custom_websocket tools. When true, makes the agent wait for a response, not call other tools and inform the user of the result. Only available for async custom_websocket tools.
    
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

<details><summary><code>client.tools.<a href="src/phonic/tools/client.py">get</a>(...) -> ToolsGetResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.tools.get(
    name_or_id="nameOrId",
    project="main",
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

<details><summary><code>client.tools.<a href="src/phonic/tools/client.py">delete</a>(...) -> ToolsDeleteResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.tools.delete(
    name_or_id="nameOrId",
    project="main",
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

<details><summary><code>client.tools.<a href="src/phonic/tools/client.py">update</a>(...) -> ToolsUpdateResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.tools.update(
    name_or_id="nameOrId",
    project="main",
    description="Updated description for booking appointments with enhanced features",
    endpoint_headers={
        "Authorization": "Bearer updated_token456"
    },
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

**parameters:** `typing.Optional[typing.List[ToolParameter]]` 

Array of parameter definitions.
When updating `type` or `endpoint_method`, all parameters must include explicit `location` values.
For `custom_webhook` tools: `location` is required for POST, defaults to `"query_string"` for GET.
For `custom_websocket`, `built_in_transfer_to_phone_number`, and `built_in_transfer_to_agent` tools: `location` must not be specified.
    
</dd>
</dl>

<dl>
<dd>

**endpoint_method:** `typing.Optional[UpdateToolRequestEndpointMethod]` — HTTP method for webhook tools. When changing this value, all parameters must include explicit `location` values.
    
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

**phone_number:** `typing.Optional[str]` — The E.164 formatted phone number to transfer calls to. Set to null if the agent should determine the phone number.
    
</dd>
</dl>

<dl>
<dd>

**dtmf:** `typing.Optional[str]` — DTMF digits to send after the transfer connects (e.g., "1234"). Can be set to null to remove DTMF.
    
</dd>
</dl>

<dl>
<dd>

**use_agent_phone_number:** `typing.Optional[bool]` — When true, Phonic will transfer the call using the agent's phone number. When false, Phonic will transfer the call using the phone number of the party to whom the agent is connected. This is only available for built_in_transfer_to_phone_number tools.
    
</dd>
</dl>

<dl>
<dd>

**detect_voicemail:** `typing.Optional[bool]` — When true, Phonic will listen in and tell the user if the transfer hits voicemail. This is only available for built_in_transfer_to_phone_number tools when use_agent_phone_number is true.
    
</dd>
</dl>

<dl>
<dd>

**agents_to_transfer_to:** `typing.Optional[typing.List[str]]` — Array of agent names that the LLM can choose from when transferring. All agents must exist in the same project as the tool.
    
</dd>
</dl>

<dl>
<dd>

**require_speech_before_tool_call:** `typing.Optional[bool]` — When true, forces the agent to speak before executing the tool.
    
</dd>
</dl>

<dl>
<dd>

**wait_for_speech_before_tool_call:** `typing.Optional[bool]` — If true, the agent will wait to finish speaking before executing the tool. This is only available for custom_webhook and custom_websocket tools.
    
</dd>
</dl>

<dl>
<dd>

**forbid_speech_after_tool_call:** `typing.Optional[bool]` — When true, forbids the agent from speaking after executing the tool. Available for custom_context, custom_webhook and custom_websocket tools.
    
</dd>
</dl>

<dl>
<dd>

**allow_tool_chaining:** `typing.Optional[bool]` — When true, allows the agent to chain and execute other tools after executing the tool. Available for custom_context, custom_webhook and custom_websocket tools.
    
</dd>
</dl>

<dl>
<dd>

**wait_for_response:** `typing.Optional[bool]` — The agent doesn't typically wait for the response of async custom_websocket tools. When true, makes the agent wait for a response, not call other tools and inform the user of the result. Only available for async custom_websocket tools.
    
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

## ExtractionSchemas
<details><summary><code>client.extraction_schemas.<a href="src/phonic/extraction_schemas/client.py">list</a>(...) -> ExtractionSchemasListResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.extraction_schemas.list(
    project="main",
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

<details><summary><code>client.extraction_schemas.<a href="src/phonic/extraction_schemas/client.py">create</a>(...) -> ExtractionSchemasCreateResponse</code></summary>
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
from phonic import Phonic, ExtractionField
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.extraction_schemas.create(
    project="main",
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
        )
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

**fields:** `typing.List[ExtractionField]` — Array of field definitions.
    
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

<details><summary><code>client.extraction_schemas.<a href="src/phonic/extraction_schemas/client.py">get</a>(...) -> ExtractionSchemasGetResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.extraction_schemas.get(
    name_or_id="nameOrId",
    project="main",
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

<details><summary><code>client.extraction_schemas.<a href="src/phonic/extraction_schemas/client.py">delete</a>(...) -> ExtractionSchemasDeleteResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.extraction_schemas.delete(
    name_or_id="nameOrId",
    project="main",
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

<details><summary><code>client.extraction_schemas.<a href="src/phonic/extraction_schemas/client.py">update</a>(...) -> ExtractionSchemasUpdateResponse</code></summary>
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
from phonic import Phonic, ExtractionField
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.extraction_schemas.update(
    name_or_id="nameOrId",
    project="main",
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
        )
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

**fields:** `typing.Optional[typing.List[ExtractionField]]` — Array of field definitions.
    
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

## Voices
<details><summary><code>client.voices.<a href="src/phonic/voices/client.py">list</a>(...) -> VoicesListResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.voices.list(
    model="merritt",
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

**model:** `typing.Literal` — The model to get voices for.
    
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

<details><summary><code>client.voices.<a href="src/phonic/voices/client.py">get</a>(...) -> VoicesGetResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.voices.get(
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

## Conversations
<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">list</a>(...) -> ConversationsListResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.list()

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

**before:** `typing.Optional[str]` — Cursor for backward pagination. Use a conversation ID from `pagination.prev_cursor` to fetch the previous page of conversations. Cannot be used with `after`.
    
</dd>
</dl>

<dl>
<dd>

**after:** `typing.Optional[str]` — Cursor for forward pagination. Use a conversation ID from `pagination.next_cursor` to fetch the next page of conversations. Cannot be used with `before`.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of conversations to return per page.
    
</dd>
</dl>

<dl>
<dd>

**audio_container:** `typing.Optional[ConversationsListRequestAudioContainer]` — Format of the presigned `audio_url` in each conversation in the response.
    
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">get</a>(...) -> ConversationsGetResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.get(
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

**audio_container:** `typing.Optional[ConversationsGetRequestAudioContainer]` — Format of the presigned `audio_url` in the response.
    
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">cancel</a>(...) -> ConversationsCancelResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.cancel(
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">get_analysis</a>(...) -> ConversationsGetAnalysisResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.get_analysis(
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">list_extractions</a>(...) -> ConversationsListExtractionsResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.list_extractions(
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">extract_data</a>(...) -> ConversationsExtractDataResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.extract_data(
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">list_evaluations</a>(...) -> ConversationsListEvaluationsResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.list_evaluations(
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">evaluate</a>(...) -> ConversationEvaluationResult</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.evaluate(
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">outbound_call</a>(...) -> ConversationsOutboundCallResponse</code></summary>
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
from phonic import Phonic, OutboundCallConfig
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.outbound_call(
    to_phone_number="+19189397081",
    config=OutboundCallConfig(
        agent="support-agent",
        welcome_message="Hi {{customer_name}}. How can I help you today?",
        system_prompt="You are an expert in {{subject}}. Be friendly, helpful and concise.",
        template_variables={
            "customer_name": "David",
            "subject": "Chess"
        },
        voice_id="sabrina",
        generate_no_input_poke_text=False,
        no_input_poke_sec=30,
        no_input_poke_text="Are you still there?",
        no_input_end_conversation_sec=180,
        default_language="en",
        additional_languages=[
            "es"
        ],
        multilingual_mode="request",
        boosted_keywords=[
            "Load ID",
            "dispatch"
        ],
        min_words_to_interrupt=1,
        tools=[
            "keypad_input"
        ],
    ),
    dry_run=False,
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

**dry_run:** `typing.Optional[bool]` — If true, validates the outbound call setup without placing a call. Returns HTTP 200 with `conversation_id` set to null.
    
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

<details><summary><code>client.conversations.<a href="src/phonic/conversations/client.py">sip_outbound_call</a>(...) -> ConversationsSipOutboundCallResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.conversations.sip_outbound_call(
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

**dry_run:** `typing.Optional[bool]` — If true, validates the outbound call setup without placing a call. Returns HTTP 200 with `conversation_id` and `twilio_call_sid` set to null.
    
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

## Auth
<details><summary><code>client.auth.<a href="src/phonic/auth/client.py">create_session_token</a>(...) -> AuthCreateSessionTokenResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a short-lived session token that can be used to authenticate WebSocket connections. Session tokens are useful for client-side applications where you don't want to expose your API key.
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.auth.create_session_token(
    ttl_seconds=300,
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

**ttl_seconds:** `typing.Optional[int]` — Time-to-live for the session token in seconds.
    
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
<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">list</a>() -> ProjectsListResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">create</a>(...) -> ProjectsCreateResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.projects.create(
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">get</a>(...) -> ProjectsGetResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">delete</a>(...) -> ProjectsDeleteResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">update</a>(...) -> ProjectsUpdateResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
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

**default_agent:** `typing.Optional[str]` — The name of the new project's default agent. Set to `null` to remove the default agent.
    
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">list_eval_prompts</a>(...) -> ProjectsListEvalPromptsResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.projects.list_eval_prompts(
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

<details><summary><code>client.projects.<a href="src/phonic/projects/client.py">create_eval_prompt</a>(...) -> ProjectsCreateEvalPromptResponse</code></summary>
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
from phonic.environment import PhonicEnvironment

client = Phonic(
    api_key="<token>",
    environment=PhonicEnvironment.DEFAULT,
)

client.projects.create_eval_prompt(
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

