"""
Home Page Object — https://www.twitch.tv

Handles initial navigation, cookie/consent banners, open-in-app banners,
and the search entry point (Browse tab in the bottom navigation bar).

NOTE: On Twitch mobile (WAP), the search is accessed via the Browse tab
in the bottom navigation bar (`a[href="/directory"]`), not a dedicated
search icon. The search input itself lives on the /directory page.
"""

from __future__ import annotations

import logging
import time

from selenium.webdriver.common.by import By

from core import config
from core.base_page import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Models the Twitch home page for mobile (WAP) viewpoint."""

    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------
    # Cookie / GDPR consent banner
    _COOKIE_ACCEPT = (By.CSS_SELECTOR, "button[data-a-target='consent-banner-accept']")
    _COOKIE_DECLINE = (By.CSS_SELECTOR, "button[data-a-target='consent-banner-decline']")

    # Bottom nav "Browse" tab — this is the search entry point on mobile Twitch
    _BROWSE_TAB = (By.CSS_SELECTOR, "a[href='/directory']")
    # Fallback: any bottom-nav link containing "Browse" text
    _BROWSE_TAB_ALT = (By.XPATH, "//a[contains(@href, '/directory')]")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def navigate(self) -> None:
        """Open Twitch home page and wait for it to settle."""
        self.open(config.BASE_URL)
        logger.info("Twitch home page loaded")
        # Allow initial JS to render the bottom nav
        time.sleep(2)

    def dismiss_cookie_banner(self) -> None:
        """
        Dismiss the GDPR / cookie consent banner if shown.
        Silently skipped when absent (region-dependent).
        """
        if self.try_dismiss(self._COOKIE_ACCEPT, timeout=8):
            logger.info("Accepted cookie consent banner")
            return
        if self.try_dismiss(self._COOKIE_DECLINE, timeout=3):
            logger.info("Declined cookie consent banner")

    def click_search_icon(self) -> None:
        """
        Navigate to the search/directory page.

        On Twitch mobile the 'search' entry point is the Browse tab in the
        bottom navigation bar (href="/directory"), which hosts the search input.
        Falls back to direct URL navigation if the tab element is not found.
        """
        logger.info("Clicking Browse tab to trigger search overlay (mobile)")

        # Dismiss open-in-app banner if present so it doesn't block the nav.
        # Target the CLOSE button specifically.
        _DISMISS_BTN = (By.CSS_SELECTOR, "button[data-a-target='open-app-banner-dismiss'], .open-app-banner button[aria-label='Close']")
        self.try_dismiss(_DISMISS_BTN, timeout=4)

        if self.is_present(self._BROWSE_TAB, timeout=8):
            self.js_click(self._BROWSE_TAB)
        elif self.is_present(self._BROWSE_TAB_ALT, timeout=5):
            self.js_click(self._BROWSE_TAB_ALT)
        else:
            # Last resort: navigate directly to the directory/search page
            logger.warning("Browse tab not found — navigating directly to /directory")
            self.open(f"{config.BASE_URL}/directory")

        # Wait for the directory/search page to load
        time.sleep(2)
