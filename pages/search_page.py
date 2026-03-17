"""
Search Page Object — Twitch /directory (Browse & Search)

Handles query input, result scrolling, and streamer selection.

NOTE: On Twitch mobile the search lives at /directory.
- The search input uses class `tw-input` (confirmed by live DOM inspection)
- Search results are `button.tw-link` elements (not anchor tags)
- We can optionally click the "Channels" tab (a[href*='type=channels'])
  to filter results to live streamers only.
"""

from __future__ import annotations

import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from core import config
from core.base_page import BasePage

logger = logging.getLogger(__name__)


class SearchPage(BasePage):
    """Models the Twitch search / directory page for WAP."""

    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    # Search input — confirmed by live DOM inspection on m.twitch.tv/directory
    _SEARCH_INPUT = (By.CSS_SELECTOR, "input.tw-input")
    _SEARCH_INPUT_ALT2 = (By.CSS_SELECTOR, "input[data-a-target='tw-input']")
    _SEARCH_INPUT_ALT3 = (By.CSS_SELECTOR, "input[type='search']")

    # "Channels" tab in search results to filter to live streamers
    _CHANNELS_TAB = (By.CSS_SELECTOR, "a[href*='type=channels']")
    _CHANNELS_TAB_ALT = (By.XPATH, "//a[contains(@href, 'type=channel')]")

    # Streamer result items — confirmed as button.tw-link on mobile Twitch
    _STREAMER_CARD = (By.CSS_SELECTOR, "button.tw-link")
    # Broader fallback: any ScCoreLink button
    _STREAMER_CARD_ALT = (By.CSS_SELECTOR, "button[class*='ScCoreLink'], button[class*='tw-link']")
    # Anchor fallback for alternate page layouts
    _STREAMER_CARD_ANCHOR = (By.CSS_SELECTOR, "a[data-a-target='preview-card-image-link'], a[data-a-target='preview-card-channel-link']")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def type_search_query(self, query: str = config.SEARCH_QUERY) -> None:
        """
        Enter the search term in the directory search input and submit.

        Navigates directly to the mobile directory URL for reliability,
        then clicks the search input before typing.

        Args:
            query: The text to search for (defaults to config value).
        """
        logger.info("Searching for: %s", query)

        # Navigate directly to the mobile directory / search page for reliability
        self.open(f"{config.BASE_URL}/directory")
        time.sleep(2)

        # Dismiss "Open in App" banner if it appears here to prevent accidental clicks
        _OPEN_IN_APP_BANNER = (By.CSS_SELECTOR, "a[href*='top_nav_open_in_app'], [data-a-target='open-app-banner-dismiss']")
        self.try_dismiss(_OPEN_IN_APP_BANNER, timeout=3)

        # Try selectors in order; click element first to focus it, then type
        search_input = None
        for locator in (self._SEARCH_INPUT, self._SEARCH_INPUT_ALT2, self._SEARCH_INPUT_ALT3):
            if self.is_present(locator, timeout=10):
                search_input = self.find_clickable(locator)
                logger.info("Search input found via: %s", locator)
                break

        if search_input is None:
            # Fall back to direct URL search
            logger.warning("Search input not found — navigating via URL")
            encoded = query.replace(" ", "+")
            self.open(f"{config.BASE_URL}/search?term={encoded}")
            time.sleep(3)
            return

        # Use JS click to avoid accidentally clicking overlapping Open App banners
        self.driver.execute_script("arguments[0].click();", search_input)
        time.sleep(0.5)
        search_input.clear()
        search_input.send_keys(query)
        time.sleep(0.5)
        search_input.send_keys(Keys.RETURN)

        # Allow results to render
        time.sleep(3)

        # Fallback: if Keys.RETURN didn't trigger navigation, force URL
        if "/directory" in self.driver.current_url and "/search" not in self.driver.current_url:
            logger.warning("Keys.RETURN failed to trigger search — navigating via URL fallback")
            encoded = query.replace(" ", "+")
            self.open(f"{config.BASE_URL}/search?term={encoded}")
            time.sleep(3)

    def scroll_results(self, times: int = config.SCROLL_COUNT) -> None:
        """
        Scroll the search results page down *times* times.

        Args:
            times: Number of scroll actions to perform.
        """
        for i in range(times):
            logger.info("Scrolling down (%d/%d)", i + 1, times)
            self.scroll_down(pixels=800)
            time.sleep(config.SCROLL_PAUSE)

    def select_first_streamer(self) -> None:
        """
        Click the first live streamer card visible in the results.

        Twitch mobile uses button.tw-link for streamer result items,
        with fallbacks for alternate layouts.
        """
        logger.info("Selecting first streamer from search results")

        cards = []
        for locator in (self._STREAMER_CARD, self._STREAMER_CARD_ALT, self._STREAMER_CARD_ANCHOR):
            if self.is_present(locator, timeout=8):
                candidates = self.find_all(locator)
                if candidates:
                    cards = candidates
                    logger.info(
                        "Found %d card(s) via %s, clicking first",
                        len(cards), locator,
                    )
                    break

        if not cards:
            raise AssertionError(
                f"No streamer cards found on results page. "
                f"Current URL: {self.driver.current_url}"
            )

        # JS click avoids intercepted-click from overlapping elements
        self.driver.execute_script("arguments[0].click();", cards[0])
        time.sleep(2)
