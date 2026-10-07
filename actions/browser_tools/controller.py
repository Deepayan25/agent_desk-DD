import time
from . import launcher
from selenium import webdriver

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

def start_browser():
    """Launch MANAS Chrome if necessary, then attach Selenium to it."""
    global driver

    attached = get_driver()
    if attached is not None:
        return attached

    result = launcher.launch_browser()
    if not result["success"]:
        return None

    # Give Chrome time to expose the debugging endpoint.
    time.sleep(1)
    return get_driver()

if __name__ == "__main__":
    print(launcher.launch_browser())
