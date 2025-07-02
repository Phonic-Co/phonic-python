import re

import requests
from loguru import logger

DEFAULT_HTTP_TIMEOUT = 30
INSUFFICIENT_CAPACITY_AVAILABLE_ERROR_CODE = 4004

# UUID regex pattern for validation
UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_uuid(string: str) -> bool:
    """Check if a string is a valid UUID."""
    return UUID_REGEX.match(string) is not None


def ends_with_uuid(string: str) -> bool:
    """Check if a string ends with a valid UUID."""
    if len(string) < 36:
        return False
    return is_uuid(string[-36:])


def is_agent_id(identifier: str) -> bool:
    """Check if an identifier is an agent ID (starts with 'agent_' followed by UUID)."""
    return (
        identifier.startswith("agent_")
        and ends_with_uuid(identifier)
        and len(identifier) == 42
    )


class InsufficientCapacityError(Exception):
    """Raised when the server returns a 4004 error code, indicating insufficient capacity."""

    def __init__(self):
        super().__init__("Insufficient capacity available. Please try again later.")


class PhonicHTTPClient:
    """Base HTTP client for Phonic API requests."""

    def __init__(
        self,
        api_key: str,
        additional_headers: dict | None = None,
        base_url: str = "https://api.phonic.co/v1",
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.additional_headers = additional_headers or {}

    def _get(self, path: str, params: dict | None = None) -> dict:
        """Make a GET request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        response = requests.get(
            f"{self.base_url}{path}",
            headers=headers,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in GET request: {response.status_code} {response.text}"
            )

    def _post(
        self, path: str, data: dict | None = None, params: dict | None = None
    ) -> dict:
        """Make a POST request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        data = data or {}

        response = requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            json=data,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code in (200, 201):
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in POST request: {response.status_code} {response.text}"
            )

    def _delete(self, path: str, params: dict | None = None) -> dict:
        """Make a DELETE request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        response = requests.delete(
            f"{self.base_url}{path}",
            headers=headers,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in DELETE request: {response.status_code} {response.text}"
            )

    def _patch(
        self, path: str, data: dict | None = None, params: dict | None = None
    ) -> dict:
        """Make a PATCH request to the Phonic API."""
        headers = {"Authorization": f"Bearer {self.api_key}", **self.additional_headers}

        response = requests.patch(
            f"{self.base_url}{path}",
            headers=headers,
            json=data,
            params=params,
            timeout=DEFAULT_HTTP_TIMEOUT,
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error: {response.status_code}")
            logger.error(response.text)
            raise ValueError(
                f"Error in PATCH request: {response.status_code} {response.text}"
            )
