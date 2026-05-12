import subprocess
import time
import pyautogui
import webbrowser

def open_app(target, platform=None):
    if not target:
        print("No app mentioned to open.")
        return
    try:
        subprocess.Popen(["cmd", "/c", "start", target])
        time.sleep(2)  
    except Exception as e:
        print("Could not open:", target)
        return False
    return True

def type_text(text, platform=None):
    if not text:
        print("No text provided to type.")
        return
    try:
        pyautogui.write(text, interval=0.05)
    except Exception as e:
        print("Typing failed:", e)
        return False
    return True

def press_enter(_):
    try:
        pyautogui.press('enter')
    except Exception as e:
        print("Failed to press enter:", e)
        return False
    return True

def backspace(data, platform=None):
    try:
        if not data:
            pyautogui.hotkey("ctrl", "backspace")
        elif data.isdigit():
            pyautogui.press("backspace", presses=int(data))
        else:
            pyautogui.hotkey("ctrl", "backspace")
    except Exception as e:
        print("Failed to press backspace:", e)
        return False
    return True

def wait(sec, platform=None):
    try:
        seconds = int(sec) if sec and sec.isdigit() else 1
        time.sleep(seconds)
    except Exception as e:
        print("Wait failed:", e)
        return False
    return True

def focus_search(_, platform=None):
    try:
        screen_w, screen_h = pyautogui.size()
        pyautogui.click(screen_w // 2, screen_h // 2)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'l') 
    except Exception as e:
        print("Failed to focus search bar:", e)
        return False
    return True

def search_web(query, platform="google"):
    if not query:
        print("No search query provided.")
        return
    try:
        platform_urls = {
            "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
            "youtube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "notepad": None
        }
        url = platform_urls.get(platform, platform_urls["google"])
        if url:
            webbrowser.open(url)
        else:
            print(f"Search not supported on {platform}")
    except Exception as e:
        print("Search failed:", e)
        return False
    return True

def play_on_youtube(query, platform="youtube"):
    if not query:
        print("No query provided.")
        return
    try:
        platform_urls = {
            "youtube": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}",
            "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
        }
        url = platform_urls.get(platform, platform_urls["youtube"])
        webbrowser.open(url)
    except Exception as e:
        print("Play failed:", e)
        return False
    return True

actions = {
    "open": open_app,
    "type": type_text,
    "wait": wait,   
    "enter": press_enter,
    "del": backspace,
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