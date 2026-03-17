"""
Root conftest.py — pytest fixtures for the WAP test framework.

This file is discovered automatically by pytest and provides:
  - A 'driver' fixture (scoped to function) that spins up and tears down
    a Chrome mobile WebDriver for each test.
  - A '--device' CLI option to override the mobile emulation device at runtime.
  - A '--headless' CLI option to run Chrome in headless mode.
"""

from __future__ import annotations

import logging

import pytest

from core.driver import DriverFactory
from core import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CLI options
# ---------------------------------------------------------------------------

def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command-line arguments for the test suite."""
    parser.addoption(
        "--device",
        action="store",
        default=config.MOBILE_DEVICE_NAME,
        help=(
            "Chrome DevTools mobile device name to emulate. "
            f"Default: '{config.MOBILE_DEVICE_NAME}'"
        ),
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run Chrome in headless mode (no visible browser window).",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def driver(request: pytest.FixtureRequest):
    """
    Provide a Chrome WebDriver configured for mobile emulation.

    Scope: function — each test gets a fresh, isolated browser session.

    Yields:
        selenium.webdriver.Chrome: Ready-to-use mobile-emulated WebDriver.

    Teardown:
        Quits the browser after the test, regardless of pass/fail.
    """
    device = request.config.getoption("--device")
    headless = request.config.getoption("--headless")

    logger.info("Launching Chrome (device=%s, headless=%s)", device, headless)
    _driver = DriverFactory.create_chrome_mobile(
        device_name=device,
        headless=headless,
    )

    yield _driver

    logger.info("Quitting browser")
    _driver.quit()


@pytest.fixture(scope="session", autouse=True)
def configure_logging() -> None:
    """Set up framework-level logging for the entire test session."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )
