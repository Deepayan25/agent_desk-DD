"""
Browser interactions — the actual things MANAS can do once a page is open.

Right now: scroll.
Coming later: read, click, type.
"""

import time

from .controller import get_driver


DEFAULT_SCROLL = 600


def _active_driver():
    """Fetch the currently attached MANAS Chrome driver, or None."""
    return get_driver()


def scroll(query="down", platform=None):
    """
    Scroll the current page.

    Accepts:
      "down"       → scroll down 600 (default)
      "up"         → scroll up 600
      "down 500"   → scroll down 500
      "up 300"     → scroll up 300
    """
    driver = _active_driver()
    if driver is None:
        return {"success": False, "reason": "No browser attached", "action": "scroll"}

    parts = (query or "down").strip().lower().split()

    direction = parts[0] if parts else "down"
    if direction not in ("down", "up"):
        return {"success": False, "reason": f"Unknown scroll direction: {direction}", "action": "scroll"}

    distance = DEFAULT_SCROLL
    if len(parts) > 1:
        try:
            distance = int(parts[1])
        except (TypeError, ValueError):
            return {"success": False, "reason": f"Invalid scroll distance: {parts[1]}", "action": "scroll"}

    pixels = distance if direction == "down" else -distance

    try:
        driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(0.3)
        return {"success": True, "action": "scroll", "direction": direction, "distance": distance}
    except Exception as e:
        return {"success": False, "reason": str(e), "action": "scroll"}