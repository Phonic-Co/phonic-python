"""
Shared fixtures for the live-API integration suite.

These tests exercise the generated SDK against a real Phonic backend. By default they
target the test environment (``api.test.phonic.ai``) and expect ``PHONIC_API_KEY`` to be
a *test* key. Their purpose is to catch breakage introduced by Fern regeneration or by the
hand-maintained files listed in ``.fernignore`` — not to test the backend itself.

The target host is controlled by ``PHONIC_HOST`` (default ``api.test.phonic.ai``); both the
REST base and the websocket host are derived from it, so the whole suite — including the
websocket handshake — follows the same environment. Point it at prod by setting
``PHONIC_HOST=api.phonic.ai`` (with a prod key).

If ``PHONIC_API_KEY`` is not set (e.g. the default unit-test CI job, or a fork PR with
no access to secrets) every test here is skipped rather than failed, so the suite is
safe to collect everywhere.
"""

import os
import uuid

import pytest

from phonic import AsyncPhonic, Phonic
from phonic.environment import PhonicEnvironment

API_KEY = os.getenv("PHONIC_API_KEY")

# Host the suite runs against. Defaults to the test environment; `or` (not a getenv default)
# so an empty CI variable still falls back instead of producing a broken host.
HOST = os.getenv("PHONIC_HOST") or "api.test.phonic.ai"

requires_api_key = pytest.mark.skipif(
    not API_KEY,
    reason="PHONIC_API_KEY not set; skipping live-API integration tests.",
)


def unique_name(prefix: str) -> str:
    """A name that is valid for Phonic resources (lowercase, digits, hyphens) and unique per run."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _environment() -> PhonicEnvironment:
    # Mirrors the shape of PhonicEnvironment.DEFAULT: REST base has the /v1 path, the
    # websocket host is the bare wss:// origin (the SDK appends /v1/sts/ws itself).
    return PhonicEnvironment(base=f"https://{HOST}/v1", production=f"wss://{HOST}")


def _client_kwargs() -> dict:
    return {"api_key": API_KEY, "environment": _environment()}


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
