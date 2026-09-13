import webbrowser 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = None

def get_driver():
    global driver
    if driver is None:
        options = webdriver.ChromeOptions()
        # options.add_argument(r"--user-data-dir=C:\Users\Deepayan\AppData\Local\Google\Chrome\User Data")
        # options.add_argument("--profile-directory=Default")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    return driver

def open_url(url, platform=None):
    try:
        webbrowser.open(url)
        return {"success": True, "action": "open_url"}
    except Exception as e:
        return {"success": False, "reason": str(e), "action": "open_url"}
    
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
