"""
Base Page Object.

All page-specific classes inherit from BasePage to gain a consistent set of
low-level browser interactions.  This keeps test readability high and reduces
duplication when interacting with elements.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core import config

logger = logging.getLogger(__name__)


class BasePage:
    """
    Abstract base for all Page Objects.

    Subclasses describe *what* the page can do (business actions).
    BasePage provides *how* to do generic browser interactions.
    """

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self._wait = WebDriverWait(
            driver,
            timeout=config.DEFAULT_TIMEOUT,
            poll_frequency=config.POLL_FREQUENCY,
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def open(self, url: str) -> None:
        """Navigate to an absolute URL."""
        logger.info("Navigating to %s", url)
        self.driver.get(url)

    # ------------------------------------------------------------------
    # Element queries
    # ------------------------------------------------------------------

    def find(self, locator: tuple) -> WebElement:
        """Return element, raising TimeoutException when not visible."""
        return self._wait.until(EC.visibility_of_element_located(locator))

    def find_clickable(self, locator: tuple) -> WebElement:
        """Return element only when it is clickable."""
        return self._wait.until(EC.element_to_be_clickable(locator))

    def find_all(self, locator: tuple) -> List[WebElement]:
        """Return all matching elements (no wait — caller guards if needed)."""
        return self.driver.find_elements(*locator)

    def is_present(self, locator: tuple, timeout: int = 5) -> bool:
        """Return True if the element appears within *timeout* seconds."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def click(self, locator: tuple) -> None:
        """Wait for element to be clickable, then click it."""
        element = self.find_clickable(locator)
        logger.debug("Clicking %s", locator)
        element.click()

    def type_text(self, locator: tuple, text: str, clear: bool = True) -> None:
        """Type text into an input field."""
        element = self.find(locator)
        if clear:
            element.clear()
        logger.debug("Typing '%s' into %s", text, locator)
        element.send_keys(text)

    def scroll_down(self, pixels: int = 800) -> None:
        """Scroll the page down by *pixels* using JavaScript."""
        logger.debug("Scrolling down %dpx", pixels)
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")

    # ------------------------------------------------------------------
    # Waits
    # ------------------------------------------------------------------

    def wait_for_url_contains(self, partial: str, timeout: Optional[int] = None) -> None:
        """Block until the current URL contains *partial*."""
        t = timeout or config.DEFAULT_TIMEOUT
        WebDriverWait(self.driver, t).until(EC.url_contains(partial))

    def wait_for_element_invisible(self, locator: tuple) -> None:
        """Block until element is invisible or gone from DOM."""
        self._wait.until(EC.invisibility_of_element_located(locator))

    def try_dismiss(self, locator: tuple, timeout: int = 5) -> bool:
        """
        Attempt to click a dismissal element (close button, overlay, etc.).

        Returns True if the element was found and clicked, False otherwise.
        Safe to call even when the element is absent.
        """
        if self.is_present(locator, timeout=timeout):
            try:
                self.find_clickable(locator).click()
                logger.info("Dismissed element: %s", locator)
                return True
            except Exception as exc:  # noqa: BLE001
                logger.debug("Could not dismiss %s: %s", locator, exc)
        return False

    # ------------------------------------------------------------------
    # JavaScript helpers
    # ------------------------------------------------------------------

    def js_click(self, locator: tuple) -> None:
        """Click an element via JavaScript (useful when overlays block it)."""
        element = self.find(locator)
        self.driver.execute_script("arguments[0].click();", element)
