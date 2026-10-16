import time
import socket
from . import launcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

driver = None

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
        options.add_experimental_option("debuggerAddress", launcher.DEBUGGER_ADDRESS)

        driver = webdriver.Chrome(options=options)
        return driver

    except Exception as e:
        print("Selenium could not attach to MANAS Chrome:", e)
        return None

def _port_is_open(host="127.0.0.1", port=9222, timeout=0.3):
    """Cheap check — is something listening on the debug port yet?"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def start_browser():
    """Launch MANAS Chrome if necessary, then attach Selenium to it."""
    global driver

    # Already attached? Reuse.
    if driver is not None:
        try:
            _ = driver.current_url
            return driver
        except Exception:
            driver = None

    # Port already open? Attach fast.
    if _port_is_open():
        return get_driver()

    # Nothing running — launch Chrome, wait for the port, then attach.
    result = launcher.launch_browser()
    if not result["success"]:
        return None

    for _ in range(60):                 # up to 30 seconds
        if _port_is_open():
            break
        time.sleep(0.5)
    else:
        return None

    return get_driver()