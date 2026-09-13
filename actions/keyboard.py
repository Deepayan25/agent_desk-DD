try:
    import pyautogui
except ModuleNotFoundError:
    pyautogui = None
import time


def require_pyautogui(action_name):
    if pyautogui is None:
        return {
            "success": False,
            "reason": "pyautogui is not installed",
            "action": action_name,
        }
    return None

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
