"""
WAP Test Suite — Twitch StarCraft II Streamer Flow

Tests the mobile (WAP) user journey:
    1. Open Twitch
    2. Click the search icon
    3. Search for "StarCraft II"
    4. Scroll search results twice
    5. Select the first live streamer
    6. Wait for the streamer page to load
    7. Handle any popup/modal
    8. Take a screenshot

This file is intentionally minimal — all browser interactions live in the
Page Objects; the test just orchestrates them in order.
"""

from __future__ import annotations

import logging

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from core import config
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.streamer_page import StreamerPage

logger = logging.getLogger(__name__)


class TestTwitchWAP:
    """
    WAP test suite for Twitch.

    Grouping tests in a class makes it easy to add setUp/tearDown hooks,
    share fixtures, or split into smaller scenario classes later.
    """

    def test_search_and_view_starcraft_streamer(self, driver: WebDriver) -> None:
        """
        Verify the complete StarCraft II streamer discovery flow on mobile.

        Steps
        -----
        1. Navigate to Twitch home
        2. Dismiss cookie/consent banner (if shown)
        3. Click the search icon
        4. Enter "StarCraft II" and submit
        5. Scroll search results twice
        6. Open the first streamer card
        7. Wait for the streamer page to fully load
        8. Dismiss any popup or modal (mature content gate, ads, etc.)
        9. Take and save a screenshot
        """
        # ── Step 1 & 2: Home page ────────────────────────────────────────
        logger.info("=== STEP 1: Navigate to Twitch ===")
        home = HomePage(driver)
        home.navigate()
        home.dismiss_cookie_banner()

        # ── Step 3: Open search ──────────────────────────────────────────
        logger.info("=== STEP 2: Click search icon ===")
        home.click_search_icon()

        # ── Step 4: Search ───────────────────────────────────────────────
        logger.info("=== STEP 3: Input '%s' ===", config.SEARCH_QUERY)
        search = SearchPage(driver)
        search.type_search_query(config.SEARCH_QUERY)

        # ── Step 5: Scroll ───────────────────────────────────────────────
        logger.info("=== STEP 4: Scroll results %d time(s) ===", config.SCROLL_COUNT)
        search.scroll_results(config.SCROLL_COUNT)

        # ── Step 6: Pick a streamer ──────────────────────────────────────
        logger.info("=== STEP 5: Select first streamer ===")
        search.select_first_streamer()

        # ── Step 7 & 8: Streamer page ────────────────────────────────────
        logger.info("=== STEP 6: Wait for streamer page to load ===")
        streamer = StreamerPage(driver)
        streamer.wait_until_loaded()
        streamer.dismiss_popup_if_present()

        # ── Step 9: Screenshot ───────────────────────────────────────────
        logger.info("=== STEP 6 (continued): Taking screenshot ===")
        screenshot_path = streamer.take_screenshot("starcraft_streamer")

        # Final assertions
        assert screenshot_path.endswith(".png"), (
            f"Expected a PNG screenshot path, got: {screenshot_path}"
        )
        assert driver.current_url != config.BASE_URL, (
            "Browser URL should have changed from the home page"
        )

        logger.info("✅ Test passed — screenshot at: %s", screenshot_path)
