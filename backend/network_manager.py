import time
from typing import Callable, Optional

import requests


DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def is_online(test_url: str = "https://www.google.com", timeout: int = 5) -> bool:
    """Check whether the device can reach the internet."""
    try:
        requests.get(test_url, timeout=timeout)
        return True
    except requests.RequestException:
        return False


def request_with_retry(
    method: str,
    url: str,
    *,
    retries: int = DEFAULT_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
    **kwargs,
):
    """Make an HTTP request with a small retry policy."""
    last_error = None

    for attempt in range(retries):
        try:
            response = requests.request(
                method,
                url,
                timeout=timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response

        except requests.RequestException as exc:
            last_error = exc

            if attempt < retries - 1:
                time.sleep(RETRY_DELAY_SECONDS)

    raise last_error


def get_network_status() -> dict:
    """Return a simple online/offline status."""
    online = is_online()

    return {
        "online": online,
        "status": "online" if online else "offline",
    }


class NetworkManager:
    """Track network state and notify the app when it changes."""

    def __init__(self, on_status_change: Optional[Callable[[bool], None]] = None):
        self.online = is_online()
        self.on_status_change = on_status_change

    def check(self) -> bool:
        """Check connectivity and notify when the network state changes."""
        previous_status = self.online
        current_status = is_online()

        if current_status != previous_status:
            self.online = current_status

            if self.on_status_change:
                self.on_status_change(current_status)

        return self.online