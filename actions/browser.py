import time
import webbrowser

import pyautogui
from selenium import webdriver

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUGGER_ADDRESS = "127.0.0.1:9222"
MANAS_PROFILE = r"%TEMP%\MANAS-Chrome"

driver = None


def launch_browser():
    """Launch the dedicated MANAS Chrome profile using PyAutoGUI."""
    try:
        pyautogui.hotkey("win", "r")
        time.sleep(1)

        pyautogui.write("cmd", interval=0.03)
        pyautogui.press("enter")
        time.sleep(1.5)

        command = (
            f'"{CHROME_PATH}" '
            f'--remote-debugging-port=9222 '
            f'--user-data-dir="{MANAS_PROFILE}"'
        )

        pyautogui.write(command, interval=0.01)
        pyautogui.press("enter")
        time.sleep(2)

        return {"success": True, "action": "launch_browser"}

    except Exception as e:
        return {
            "success": False,
            "reason": str(e),
            "action": "launch_browser",
        }


def get_driver():
    """Attach Selenium to the already-running MANAS Chrome instance."""
    global driver

    if driver is not None:
        try:
            _ = driver.current_url
            return driver
        except Exception:
            driver = None

    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", DEBUGGER_ADDRESS)

        driver = webdriver.Chrome(options=options)
        return driver

    except Exception as e:
        print("Selenium could not attach to MANAS Chrome:", e)
        return None


def start_browser():
    """Launch MANAS Chrome if necessary, then attach Selenium to it."""
    global driver

    attached = get_driver()
    if attached is not None:
        return attached

    result = launch_browser()
    if not result["success"]:
        return None

    # Give Chrome time to expose the debugging endpoint.
    time.sleep(1)
    return get_driver()


def open_url(url, platform=None):
    """Open a URL in MANAS Chrome and keep Selenium in control of the tab."""
    if not url:
        return {"success": False, "reason": "No URL", "action": "open_url"}

    try:
        browser = start_browser()
        if browser is None:
            return {
                "success": False,
                "reason": "Could not start or connect to MANAS Chrome",
                "action": "open_url",
            }

        browser.get(url)
        return {"success": True, "action": "open_url"}

    except Exception as e:
        return {
            "success": False,
            "reason": str(e),
            "action": "open_url",
        }


def search_web(query, platform="google"):
    if not query:
        return {"success": False, "reason": "No query", "action": "search"}

    urls = {
        "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
    }

    url = urls.get(platform, urls["google"])
    return open_url(url)


def search_youtube(query, platform=None):
    if not query:
        return {"success": False, "reason": "No query", "action": "search_youtube"}

    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    return open_url(url)


KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "classroom": "https://classroom.google.com",
    "github": "https://www.github.com",
}


def navigate_to(site, platform=None):
    if not site:
        return {"success": False, "reason": "No site specified", "action": "navigate"}

    url = KNOWN_SITES.get(site.lower())

    if not url:
        url = f"https://www.{site}.com" if not site.startswith("http") else site

    return open_url(url)
