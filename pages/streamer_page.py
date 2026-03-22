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

        Specifically waits for the video player and channel data to mount in the DOM,
        ensuring the live stream is actually loading before continuing.
        """
        logger.info("Waiting for streamer page to load …")

        # 1. Wait for the core page layout container
        if self.is_present(self._PAGE_CONTAINER, timeout=10):
            logger.info("Page skeleton loaded")
            
        # 2. Wait strictly for the actual Video Player to mount
        # (This is the most critical element to prove the stream is loading)
        if self.is_present(self._VIDEO_PLAYER, timeout=15):
            logger.info("Video player heavily mounted in DOM")
        else:
            logger.warning("Video player did not appear within timeout!")

        # 3. Wait for the Chat Room to load
        _CHAT_CONTAINER = (By.CSS_SELECTOR, ".scrollable-area, .chat-line__message, [data-a-target='chat-room']")
        if self.is_present(_CHAT_CONTAINER, timeout=10):
            logger.info("Chat room mounted in DOM")
        else:
            logger.warning("Chat room did not appear within timeout")

        # Allow lazy-loaded assets and the actual video stream blob to settle
        # (3 seconds is optimal here because the <video> tag appearing in DOM 
        # doesn't mean the first frame has rendered yet).
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
            time.sleep(0.5)

        if self.try_dismiss(self._START_WATCHING_BTN, timeout=3):
            logger.info("Dismissed 'Start Watching' gate")
            popup_handled = True
            time.sleep(0.5)

        if self.try_dismiss(self._CLOSE_MODAL_BTN, timeout=3):
            logger.info("Dismissed generic modal overlay")
            popup_handled = True
            time.sleep(0.5)

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
