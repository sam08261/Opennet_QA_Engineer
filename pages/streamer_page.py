"""
Streamer Page Object — individual channel / stream page

Handles page load detection, popup/modal dismissal, and screenshots.
"""

from __future__ import annotations

import logging
import time

from selenium.webdriver.common.by import By

from core import config
from core.base_page import BasePage
from utils.screenshot import save_screenshot

logger = logging.getLogger(__name__)


class StreamerPage(BasePage):
    """Models a Twitch streamer's channel page for WAP."""

    # ------------------------------------------------------------------
    # Locators — page content signals
    # ------------------------------------------------------------------
    _CHANNEL_NAME = (By.CSS_SELECTOR, "h1[data-a-target='stream-title'], h1.tw-title, h1")
    _VIDEO_PLAYER = (By.CSS_SELECTOR, "video, [data-a-target='video-player']")
    _PAGE_CONTAINER = (By.CSS_SELECTOR, "main, [data-a-target='page-main-content']")

    # ------------------------------------------------------------------
    # Locators — popup / modal variants
    # ------------------------------------------------------------------
    # Mature content / age restriction overlay
    _MATURE_CONTENT_BTN = (
        By.CSS_SELECTOR,
        "button[data-a-target='player-overlay-mature-accept']",
    )
    # Generic "close" button (X) on overlays / modals
    _CLOSE_MODAL_BTN = (
        By.XPATH,
        "//button[@aria-label='Close' or @aria-label='close' "
        "or @data-a-target='modal-close-button']",
    )
    # "Start Watching" button on some regional / content gates
    _START_WATCHING_BTN = (
        By.XPATH,
        "//button[.//span[contains(text(), 'Start Watching') "
        "or contains(text(), 'start watching')]]",
    )
    # Cookie / GDPR late-appearing banner
    _COOKIE_ACCEPT = (By.CSS_SELECTOR, "button[data-a-target='consent-banner-accept']")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def wait_until_loaded(self) -> None:
        """
        Wait for meaningful page content to be visible.

        Strategy: wait for *any* of the known content signals to appear,
        then add a short stabilisation sleep for assets (video, images) to settle.
        """
        logger.info("Waiting for streamer page to load …")

        # Try the most reliable signals in order
        for locator in (self._PAGE_CONTAINER, self._CHANNEL_NAME, self._VIDEO_PLAYER):
            if self.is_present(locator, timeout=config.DEFAULT_TIMEOUT):
                logger.info("Page content detected via: %s", locator)
                break
        else:
            logger.warning(
                "None of the expected page signals found — proceeding anyway"
            )

        # Allow lazy-loaded assets and video to settle
        time.sleep(3)
        logger.info("Streamer page considered fully loaded")

    def dismiss_popup_if_present(self) -> None:
        """
        Attempt to dismiss any popup/modal that may block the streamer view.

        Handles (in order of priority):
        1. Mature content / age-gate overlay
        2. "Start Watching" content gate
        3. Generic close-button overlay
        4. Late-appearing cookie consent banner

        Each dismissal is a no-op when the element is absent — safe to always call.
        """
        popup_handled = False

        if self.try_dismiss(self._MATURE_CONTENT_BTN, timeout=5):
            logger.info("Dismissed mature content overlay")
            popup_handled = True
            time.sleep(1)

        if self.try_dismiss(self._START_WATCHING_BTN, timeout=3):
            logger.info("Dismissed 'Start Watching' gate")
            popup_handled = True
            time.sleep(1)

        if self.try_dismiss(self._CLOSE_MODAL_BTN, timeout=3):
            logger.info("Dismissed generic modal overlay")
            popup_handled = True
            time.sleep(1)

        if self.try_dismiss(self._COOKIE_ACCEPT, timeout=3):
            logger.info("Dismissed late cookie banner on streamer page")
            popup_handled = True

        if not popup_handled:
            logger.info("No popups detected — continuing")

    def take_screenshot(self, name: str = "streamer_page") -> str:
        """
        Capture and save a screenshot of the current page state.

        Args:
            name: Base filename (timestamp is appended automatically).

        Returns:
            Absolute path to the saved PNG file.
        """
        path = save_screenshot(self.driver, name)
        logger.info("Screenshot saved: %s", path)
        return path
