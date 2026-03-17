# Opennet QA Engineer — WAP Test Framework

A scalable, maintainable **Selenium + pytest** test framework for validating Twitch's mobile web experience (WAP). Built with the Page Object Model pattern and Chrome's built-in mobile emulation.

---

## 📹 Test Running Locally

> **GIF to be recorded after first local run — see [Running Tests](#running-tests) below.**

---

## 🗂️ Project Structure

```
Opennet_QA_Engineer/
├── conftest.py               # Root pytest fixtures (driver, CLI options, logging)
├── pytest.ini                # pytest config (test paths, HTML report, logging)
├── requirements.txt          # Python dependencies
│
├── core/                     # Framework internals
│   ├── config.py             # Central config (URLs, timeouts, device name)
│   ├── driver.py             # WebDriver factory — Chrome mobile emulation
│   └── base_page.py          # Base Page Object with shared browser utilities
│
├── pages/                    # Page Object classes
│   ├── home_page.py          # Twitch home (navigate, cookie banner, search icon)
│   ├── search_page.py        # Search results (input, scroll, streamer selection)
│   └── streamer_page.py      # Channel page (load wait, popup handler, screenshot)
│
├── tests/                    # Test files
│   └── test_twitch_wap.py    # Main WAP scenario: StarCraft II streamer flow
│
├── utils/                    # Shared utilities
│   ├── screenshot.py         # Timestamped screenshot saver
│   └── wait_helpers.py       # Custom WebDriverWait conditions
│
├── screenshots/              # Auto-created — captured screenshots land here
└── reports/                  # Auto-created — HTML test reports land here
```

---

## ⚙️ Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.9 |
| Google Chrome | Latest stable |
| pip | ≥ 23 |

> **ChromeDriver** is managed automatically via `webdriver-manager` — no manual installation needed.

---

## 🚀 Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/Opennet_QA_Engineer.git
cd Opennet_QA_Engineer

# 2. Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Running Tests

### Run the full WAP suite (default: iPhone X emulation)

```bash
pytest
```

### Run with a different mobile device

```bash
pytest --device "Pixel 5"
pytest --device "Galaxy S9+"
```

> Any device name shown in Chrome DevTools → Device Toolbar is valid.

### Run headlessly (no visible browser window — great for CI)

```bash
pytest --headless
# or via environment variable:
HEADLESS=true pytest
```

### Run a specific test by name

```bash
pytest tests/test_twitch_wap.py::TestTwitchWAP::test_search_and_view_starcraft_streamer -v
```

### Run only WAP-marked tests

```bash
pytest -m wap
```

---

## 📊 Reports & Artifacts

| Artifact | Location | Notes |
|---|---|---|
| HTML Report | `reports/report.html` | Generated automatically after each run |
| Screenshots | `screenshots/` | Saved at the final step of each test |

Open the HTML report in any browser:

```bash
open reports/report.html      # macOS
xdg-open reports/report.html  # Linux
```

---

## 🏗️ Framework Design

### Why Page Object Model?

- **Maintainability**: UI changes require editing a single page class, not every test
- **Readability**: Tests read like plain English — `home.click_search_icon()`
- **Scalability**: New test scenarios reuse existing page objects

### Key design decisions

| Decision | Rationale |
|---|---|
| `core/config.py` | All magic values in one place — zero config scattered across tests |
| `DriverFactory` | Swapping browsers/devices is a one-line change, not a test rewrite |
| `BasePage` | Shared wait logic, JS fallbacks, and safe popup dismissal available to all pages |
| `try_dismiss()` | All popup handlers are no-ops when the element is absent — no flaky `NoSuchElement` crashes |
| Dual locators | Primary + fallback CSS/XPath for every critical element to handle Twitch markup changes |
| `--device` / `--headless` CLI | CI/CD friendly without code changes |

### Adding a new test scenario

1. Add a new method to an existing page object (or create a new `pages/new_page.py`)
2. Write a new test function in `tests/test_twitch_wap.py` (or a new `tests/test_*.py`)
3. Tag it with `@pytest.mark.<marker>` (see `pytest.ini` for available markers)

---

## 🔧 Configuration Reference

Edit `core/config.py` to change framework behaviour:

| Variable | Default | Description |
|---|---|---|
| `BASE_URL` | `https://www.twitch.tv` | Target application URL |
| `SEARCH_QUERY` | `StarCraft II` | Default search term |
| `SCROLL_COUNT` | `2` | Number of result-page scrolls |
| `MOBILE_DEVICE_NAME` | `iPhone X` | Chrome emulation device |
| `DEFAULT_TIMEOUT` | `20` | Max wait time (seconds) |
| `HEADLESS` | `false` | Override via `HEADLESS=true` env var |

---

## 📦 Dependencies

See [requirements.txt](requirements.txt) for pinned versions.

| Package | Purpose |
|---|---|
| `selenium` | Browser automation |
| `webdriver-manager` | Auto-downloads matching ChromeDriver |
| `pytest` | Test runner |
| `pytest-html` | HTML test reports |
| `pytest-xdist` | Parallel test execution (`-n auto`) |

---

## 🤝 Contributing

1. Fork the repo and create a feature branch
2. Follow the existing POM structure for new pages
3. Add markers in `pytest.ini` for new test categories
4. Ensure `pytest` passes before opening a PR
