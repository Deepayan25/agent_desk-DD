"""
MANAS Chrome launcher.

Launches a dedicated Chrome instance with the remote debugging port
open, so Selenium can attach to it. No Win+R, no CMD, no focus stealing.
"""

import subprocess

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUGGER_ADDRESS = "127.0.0.1:9222"
MANAS_PROFILE = r"C:\MANAS-Chrome-Profile"


def launch_browser():
    """Launch the dedicated MANAS Chrome profile with the debug port open."""
    try:
        subprocess.Popen(
            [
                CHROME_PATH,
                "--remote-debugging-port=9222",
                f"--user-data-dir={MANAS_PROFILE}",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {"success": True, "action": "launch_browser"}

    except FileNotFoundError:
        return {
            "success": False,
            "reason": f"Chrome not found at {CHROME_PATH}",
            "action": "launch_browser",
        }
    except Exception as e:
        return {
            "success": False,
            "reason": str(e),
            "action": "launch_browser",
        }