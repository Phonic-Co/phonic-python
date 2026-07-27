"""CRUD lifecycle for agents, scoped to a throwaway project."""

from .conftest import requires_api_key, unique_name

from phonic import Phonic


@requires_api_key
def test_agent_crud(client: Phonic, project) -> None:
    name = unique_name("sdk-it-agent")

    created = client.agents.create(
        name=name,
        project=project.name,
        system_prompt="You are a test agent. Be brief.",
        welcome_message="Hi, this is a test.",
    )
    assert created.id
    assert created.name == name

    try:
        # get by id resolves the agent
        got = client.agents.get(name_or_id=created.id)
        assert got.agent.id == created.id
        assert got.agent.name == name

        # appears in the project's agent list
        listing = client.agents.list(project=project.name)
        assert any(a.id == created.id for a in listing.agents)

        # update a field and read it back
        new_prompt = "You are an updated test agent."
        updated = client.agents.update(name_or_id=created.id, system_prompt=new_prompt)
        assert updated.success
        assert updated.agent.system_prompt == new_prompt
    finally:
        client.agents.delete(name_or_id=created.id)

    # confirm it's gone from the project
    assert all(a.id != created.id for a in client.agents.list(project=project.name).agents)
