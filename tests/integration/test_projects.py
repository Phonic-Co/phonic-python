"""CRUD lifecycle for projects."""

from .conftest import requires_api_key, unique_name

from phonic import Phonic


@requires_api_key
def test_project_crud(client: Phonic) -> None:
    name = unique_name("sdk-it-proj")

    created = client.projects.create(name=name)
    assert created.id
    assert created.name == name

    try:
        # get by id and by name both resolve the same project
        assert client.projects.get(name_or_id=created.id).project.id == created.id
        assert client.projects.get(name_or_id=name).project.id == created.id

        # appears in the list
        listing = client.projects.list()
        assert any(p.id == created.id for p in listing.projects)

        # update: rename, then read it back
        new_name = unique_name("sdk-it-proj")
        assert client.projects.update(name_or_id=created.id, name=new_name).success
        assert client.projects.get(name_or_id=created.id).project.name == new_name
    finally:
        client.projects.delete(name_or_id=created.id)

    # confirm it's gone
    assert all(p.id != created.id for p in client.projects.list().projects)
