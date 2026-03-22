"""
Central configuration for the WAP test framework.

All tuneable values live here so tests never contain magic strings or numbers.
To run against a different device, query, or URL, change this file only.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent.parent
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"
REPORTS_DIR = ROOT_DIR / "reports"

# Ensure directories exist at import time
SCREENSHOTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
BASE_URL: str = "https://www.twitch.tv"

# ---------------------------------------------------------------------------
# Search configuration
# ---------------------------------------------------------------------------
SEARCH_QUERY: str = "StarCraft II"
SCROLL_COUNT: int = 2          # Number of page scrolls on the search results page

# ---------------------------------------------------------------------------
# Mobile emulation
# ---------------------------------------------------------------------------
# Any device name listed in Chrome DevTools' device list is valid here.
# Examples: "iPhone X", "Pixel 7", "Galaxy S9+", "iPhone 14 Pro Max"
MOBILE_DEVICE_NAME: str = os.getenv("MOBILE_DEVICE", "iPhone X")

# ---------------------------------------------------------------------------
# Timeouts (seconds)
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT: int = 20       # General explicit-wait ceiling
PAGE_LOAD_TIMEOUT: int = 45     # driver.set_page_load_timeout
POLL_FREQUENCY: float = 0.5    # How often WebDriverWait re-checks condition
SCROLL_PAUSE: float = 1.0      # Pause between programmatic scrolls

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------
HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
