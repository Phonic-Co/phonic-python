import os
import phonic

PHONIC_API_KEY = os.environ["PHONIC_API_KEY"]


def main():
    # Step 1: Build an agent
    phonic_agents_client = phonic.client.Agents(api_key=PHONIC_API_KEY)
    phonic_tools_client = phonic.client.Tools(api_key=PHONIC_API_KEY)
    agent_name = "weather-agent"
    tool_name = "check_weather"

    # For safety, if the agents and tools already exist, we will delete them
    try:
        phonic_agents_client.delete(agent_name)
    except ValueError as e:
        if "Agent not found" not in e.args[0]:
            raise e

    try:
        phonic_tools_client.delete(tool_name)
    except ValueError as e:
        if "Tool not found" not in e.args[0]:
            raise e

    # Create the agent
    agent = phonic_agents_client.create(
        name=agent_name,
        project="main",
        phone_number="assign-automatically",
        voice_id="grant",
        welcome_message="Hello! I can help you with weather information. What would you like to know?",
        tools=["natural_conversation_ending"],
        audio_format="mulaw_8000",
    )

    # Step 2: Create tools
    weather_endpoint_url = "https://api.open-meteo.com/v1/forecast?hourly=temperature_2m,apparent_temperature&forecast_days=1&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch"
    tool = phonic_tools_client.create(
        name=tool_name,
        description="Check the current weather in a specified location.",
        endpoint_url=weather_endpoint_url,
        endpoint_timeout_ms=1_000,
        parameters=[
            {
                "type": "number",
                "name": "latitude",
                "description": "Latitude of the location.",
                "is_required": True,
            },
            {
                "type": "number",
                "name": "longitude",
                "description": "Longitude of the location.",
                "is_required": True,
            },
        ],
    )

    # Add tool to agent
    agent = phonic_agents_client.get(agent["name"])
    agent = agent["agent"]
    phonic_agents_client.update(agent["name"], tools=agent["tools"] + [tool["name"]])
    agent = phonic_agents_client.get(agent["name"])
    agent = agent["agent"]

    # Inform about call
    input(
        f"Your agent has been created with phone number {agent['phone_number']}. To continue, please place a call to the agent. Press any key once the call is in progress,"
    )

    phonic_conversations_client = phonic.client.Conversations(api_key=PHONIC_API_KEY)
    conversations = phonic_conversations_client.list(project="main")
    conversation = conversations["conversations"][0]
    print(
        f"Your conversation is now streaming on the Phonic platform. To view it live, please follow this URL: https://phonic.co/conversations/{conversation['workspace']}/{conversation['project']['name']}/{conversation['id']}"
    )
    input(
        "Once your conversation has finished, press any key to start tearing down the agents."
    )

    # Teardown everything
    phonic_agents_client.delete(agent["name"])
    phonic_tools_client.delete(tool["name"])


if __name__ == "__main__":
    main()
