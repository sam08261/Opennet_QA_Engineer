"""
WebDriver factory.

Centralises browser creation so tests never instantiate drivers directly.
Adding a new browser or emulation profile is a one-file change.
"""

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from core import config


class DriverFactory:
    """Factory that creates fully-configured WebDriver instances."""

    @staticmethod
    def create_chrome_mobile(
        device_name: str = config.MOBILE_DEVICE_NAME,
        headless: bool = config.HEADLESS,
    ) -> webdriver.Chrome:
        """
        Return a Chrome WebDriver configured for mobile emulation.

        Args:
            device_name: Chrome DevTools device name (e.g. "iPhone X").
            headless: Run Chrome without a visible window when True.

        Returns:
            A ready-to-use ``webdriver.Chrome`` instance.
        """
        options = _build_mobile_options(device_name, headless)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        return driver


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_mobile_options(device_name: str, headless: bool) -> Options:
    """Compose ChromeOptions for mobile emulation."""
    options = Options()

    # Mobile emulation via named device profile
    options.add_experimental_option(
        "mobileEmulation", {"deviceName": device_name}
    )

    if headless:
        options.add_argument("--headless=new")

    # Stability / CI-friendly flags
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")

    # Prevent "Chrome is being controlled by automated software" banner
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Block external protocol handers (prevents App Store / native app redirects)
    prefs = {
        "protocol_handler.excluded_schemes.itms-apps": False,
        "protocol_handler.excluded_schemes.twitch": False,
        "protocol_handler.excluded_schemes.intent": False,
    }
    options.add_experimental_option("prefs", prefs)

    return options
