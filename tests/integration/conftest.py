"""
Shared fixtures for the live-API integration suite.

These tests exercise the generated SDK against a real Phonic backend (a dedicated
test workspace, selected by the API key in ``PHONIC_API_KEY``). Their purpose is to
catch breakage introduced by Fern regeneration or by the hand-maintained files listed
in ``.fernignore`` — not to test the backend itself.

If ``PHONIC_API_KEY`` is not set (e.g. the default unit-test CI job, or a fork PR with
no access to secrets) every test here is skipped rather than failed, so the suite is
safe to collect everywhere.
"""

import os
import uuid

import pytest

from phonic import AsyncPhonic, Phonic

API_KEY = os.getenv("PHONIC_API_KEY")

# Optional base-URL override so the suite can be pointed at a non-prod backend without
# code changes. When unset the SDK's default (https://api.phonic.ai) is used.
BASE_URL = os.getenv("PHONIC_BASE_URL")

requires_api_key = pytest.mark.skipif(
    not API_KEY,
    reason="PHONIC_API_KEY not set; skipping live-API integration tests.",
)


def unique_name(prefix: str) -> str:
    """A name that is valid for Phonic resources (lowercase, digits, hyphens) and unique per run."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _client_kwargs() -> dict:
    kwargs: dict = {"api_key": API_KEY}
    if BASE_URL:
        # PhonicEnvironment carries both the REST base and the websocket host; only the
        # REST base is overridable via env here. Tests that need the ws host should rely
        # on the default environment.
        from phonic.environment import PhonicEnvironment

        kwargs["environment"] = PhonicEnvironment(base=BASE_URL, production=PhonicEnvironment.DEFAULT.production)
    return kwargs


@pytest.fixture(scope="session")
def client() -> Phonic:
    if not API_KEY:
        pytest.skip("PHONIC_API_KEY not set; skipping live-API integration tests.")
    return Phonic(**_client_kwargs())


@pytest.fixture(scope="session")
def async_client() -> AsyncPhonic:
    if not API_KEY:
        pytest.skip("PHONIC_API_KEY not set; skipping live-API integration tests.")
    return AsyncPhonic(**_client_kwargs())


@pytest.fixture
def project(client: Phonic):
    """Create a throwaway project for a test and delete it on teardown."""
    created = client.projects.create(name=unique_name("sdk-it"))
    try:
        yield created
    finally:
        try:
            client.projects.delete(name_or_id=created.id)
        except Exception:
            # Best-effort cleanup; a failed delete shouldn't mask the test result.
            pass
