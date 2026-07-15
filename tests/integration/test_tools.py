"""CRUD lifecycle for tools, scoped to a throwaway project."""

from .conftest import requires_api_key, unique_name

from phonic import Phonic


@requires_api_key
def test_tool_crud(client: Phonic, project) -> None:
    # A custom_context tool is the simplest valid type: it only needs a static `context`
    # string and no endpoint/parameter wiring.
    name = unique_name("sdk_it_tool").replace("-", "_")  # tool names are snake_case

    created = client.tools.create(
        name=name,
        description="A test tool created by the SDK integration suite.",
        type="custom_context",
        execution_mode="sync",
        context="The sky is blue.",
        project=project.name,
    )
    assert created.id
    assert created.name == name

    try:
        # get by id resolves the tool
        got = client.tools.get(name_or_id=created.id)
        assert got.tool.id == created.id
        assert got.tool.name == name

        # appears in the project's tool list
        listing = client.tools.list(project=project.name)
        assert any(t.id == created.id for t in listing.tools)

        # update a field and read it back
        new_description = "An updated test tool."
        assert client.tools.update(name_or_id=created.id, description=new_description).success
        assert client.tools.get(name_or_id=created.id).tool.description == new_description
    finally:
        client.tools.delete(name_or_id=created.id)

    # confirm it's gone from the project
    assert all(t.id != created.id for t in client.tools.list(project=project.name).tools)
