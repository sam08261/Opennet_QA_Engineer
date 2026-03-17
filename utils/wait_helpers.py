"""
Custom wait helpers.

Reusable WebDriverWait conditions and utility functions that complement
Selenium's built-in expected_conditions for WAP-specific scenarios.
"""

from __future__ import annotations

import logging
from typing import Sequence, Tuple

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import DEFAULT_TIMEOUT, POLL_FREQUENCY

logger = logging.getLogger(__name__)

# Type alias for Selenium (By, value) tuples
Locator = Tuple[str, str]


def wait_for_url_change(driver: WebDriver, original_url: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """
    Block until the browser URL changes from *original_url*.

    Args:
        driver:       WebDriver instance.
        original_url: URL at the time of calling (the one we expect to leave).
        timeout:      Maximum seconds to wait.

    Returns:
        True if URL changed, False if timed out.
    """
    try:
        WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(
            lambda d: d.current_url != original_url
        )
        logger.debug("URL changed from %s → %s", original_url, driver.current_url)
        return True
    except TimeoutException:
        logger.warning("URL did not change within %ds (still: %s)", timeout, driver.current_url)
        return False


def wait_for_any_element(
    driver: WebDriver,
    locators: Sequence[Locator],
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """
    Return True as soon as *any* of the given locators becomes present in DOM.

    Useful for detecting whichever popup variant Twitch decides to show.

    Args:
        driver:   WebDriver instance.
        locators: Iterable of (By, value) tuples to check.
        timeout:  Maximum seconds to wait overall.

    Returns:
        True if any element was found, False if none appeared within *timeout*.
    """
    def _any_present(d: WebDriver) -> bool:
        return any(
            len(d.find_elements(*loc)) > 0
            for loc in locators
        )

    try:
        WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(_any_present)
        return True
    except TimeoutException:
        return False


def wait_for_element_count_gte(
    driver: WebDriver,
    locator: Locator,
    count: int,
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """
    Block until at least *count* elements matching *locator* are present.

    Useful for waiting until search results finish loading.

    Args:
        driver:  WebDriver instance.
        locator: (By, value) tuple.
        count:   Minimum element count to wait for.
        timeout: Maximum seconds to wait.

    Returns:
        True if count was reached, False if timed out.
    """
    try:
        WebDriverWait(driver, timeout, poll_frequency=POLL_FREQUENCY).until(
            lambda d: len(d.find_elements(*locator)) >= count
        )
        return True
    except TimeoutException:
        logger.warning(
            "Expected >= %d elements for %s, timed out after %ds", count, locator, timeout
        )
        return False
