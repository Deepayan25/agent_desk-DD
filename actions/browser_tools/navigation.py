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