from .controller import start_browser

def open_url(url, platform=None):
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

if __name__ == "__main__":
    print(open_url("https://www.youtube.com"))