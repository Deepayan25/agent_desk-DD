import subprocess
import time
import webbrowser

try:
    import pyautogui
except ModuleNotFoundError:
    pyautogui = None

def require_pyautogui(action_name):
    if pyautogui is None:
        return {
            "success": False,
            "reason": "pyautogui is not installed",
            "action": action_name,
        }
    return None


def open_app(target, platform=None):
    if not target:
        print("No app mentioned to open.")
        return {"success": False, "reason": "No target specified", "action": "open"}
    try:
        result = subprocess.run(
            ["cmd", "/c", "start", "", target],
            capture_output=True,
            timeout=5,
        )
        if result.returncode != 0:
            print(f"Failed to open {target}")
            return {"success": False, "reason": f"App not found: {target}", "action": "open"}
        time.sleep(2)
        return {"success": True, "action": "open"}
    except Exception as e:
        return {"success": False, "reason": str(e), "action": "open"}


def type_text(text, platform=None):
    if not text:
        print("No text provided to type.")
        return {"success": False, "reason": "No text provided", "action": "type"}
    dependency_error = require_pyautogui("type")
    if dependency_error:
        return dependency_error
    try:
        pyautogui.write(text, interval=0.05)
    except Exception as e:
        print("Typing failed:", e)
        return {"success": False, "reason": "Failed to type text", "action": "type"}
    return {"success": True, "action": "type"}


def press_enter(_, platform=None):
    dependency_error = require_pyautogui("enter")
    if dependency_error:
        return dependency_error
    try:
        pyautogui.press("enter")
    except Exception as e:
        print("Failed to press enter:", e)
        return {"success": False, "reason": "Failed to press enter", "action": "enter"}
    return {"success": True, "action": "enter"}


def backspace(data, platform=None):
    dependency_error = require_pyautogui("del")
    if dependency_error:
        return dependency_error
    try:
        if not data:
            pyautogui.hotkey("ctrl", "backspace")
        elif data == "line":
            pyautogui.hotkey("shift", "home")
            pyautogui.press("delete")
        elif data.isdigit():
            pyautogui.press("backspace", presses=int(data))
        else:
            pyautogui.hotkey("ctrl", "backspace")
    except Exception as e:
        print("Failed to press backspace:", e)
        return {"success": False, "reason": str(e), "action": "del"}
    return {"success": True, "action": "del"}


def prev_line(data, platform=None):
    dependency_error = require_pyautogui("prevline")
    if dependency_error:
        return dependency_error
    try:
        pyautogui.press("end")
        pyautogui.hotkey("shift", "up")
        pyautogui.hotkey("shift", "end")
        return {"success": True, "action": "prevline"}
    except Exception as e:
        return {"success": False, "reason": str(e), "action": "prevline"}


def wait(sec, platform=None):
    try:
        seconds = int(sec) if sec and sec.isdigit() else 1
        time.sleep(seconds)
    except Exception as e:
        print("Wait failed:", e)
        return {"success": False, "reason": "Failed to wait", "action": "wait"}
    return {"success": True, "action": "wait"}


def focus_search(_, platform=None):
    dependency_error = require_pyautogui("focus")
    if dependency_error:
        return dependency_error
    try:
        screen_w, screen_h = pyautogui.size()
        pyautogui.click(screen_w // 2, screen_h // 2)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "l")
    except Exception as e:
        print("Failed to focus search bar:", e)
        return {"success": False, "reason": "Failed to focus search bar", "action": "focus"}
    return {"success": True, "action": "focus"}


def search_web(query, platform="google"):
    if not query:
        print("No search query provided.")
        return {"success": False, "reason": "No search query provided", "action": "search"}
    try:
        platform_urls = {
            "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
            "youtube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "notepad": None,
        }
        url = platform_urls.get(platform, platform_urls["google"])
        if url:
            webbrowser.open(url)
        else:
            print(f"Search not supported on {platform}")
    except Exception as e:
        print("Search failed:", e)
        return {"success": False, "reason": "Failed to search", "action": "search"}
    return {"success": True, "action": "search"}


def play_on_youtube(query, platform="youtube"):
    if not query:
        print("No query provided.")
        return {"success": False, "reason": "No query provided", "action": "play"}
    try:
        platform_urls = {
            "youtube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
        }
        url = platform_urls.get(platform, platform_urls["youtube"])
        webbrowser.open(url)
    except Exception as e:
        print("Play failed:", e)
        return {"success": False, "reason": "Failed to play on YouTube", "action": "play"}
    return {"success": True, "action": "play"}

def show_help(data=None, platform=None):
    print("\n===== AGENTDESK HELP =====")
    print("open <app>")
    print("search <query>")
    print("search <query> in youtube")
    print("play <query>")
    print("type <text>")
    print("wait <seconds>")
    print("enter")
    print("del")
    print("focus")
    print("prevline")
    print("help")
    print("exit")
    print("==========================")

    return {"success": True, "action": "help"}

actions = {
    "open": open_app,
    "type": type_text,
    "wait": wait,
    "enter": press_enter,
    "del": backspace,
    "prevline": prev_line,
    "focus": focus_search,
    "search": search_web,
    "play": play_on_youtube
}


aliases = {
    "ggl": "chrome",
    "np": "notepad",
    "cal": "calculator",
    "vscode": "code",
    "word": "winword",
    "xl": "excel",
    "gpt": "chatgpt",
    "ppt": "powerpnt",
}