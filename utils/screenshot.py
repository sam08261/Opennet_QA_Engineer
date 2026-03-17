"""
Screenshot utility.

Provides a single function to capture and save timestamped screenshots.
All tests that need screenshots should use this instead of calling
driver.save_screenshot() directly — keeps naming consistent.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from core.config import SCREENSHOTS_DIR

logger = logging.getLogger(__name__)


def save_screenshot(driver: WebDriver, name: str = "screenshot") -> str:
    """
    Capture a screenshot and save it with a timestamp.

    Args:
        driver: Active WebDriver instance.
        name:   Base name used in the filename (spaces replaced with underscores).

    Returns:
        Absolute path string of the saved PNG file.

    Example:
        >>> path = save_screenshot(driver, "starcraft_streamer")
        # → screenshots/starcraft_streamer_2024-03-15_12-30-45.png
    """
    safe_name = name.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{safe_name}_{timestamp}.png"
    filepath = Path(SCREENSHOTS_DIR) / filename

    filepath.parent.mkdir(parents=True, exist_ok=True)

    if driver.save_screenshot(str(filepath)):
        logger.info("Screenshot saved → %s", filepath)
    else:
        logger.warning("Screenshot may not have saved correctly → %s", filepath)

    return str(filepath)
