from pywinauto import Desktop
from pywinauto.keyboard import send_keys


def get_notepad():
    try:
        window = Desktop(backend="uia").window(title_re=".*Notepad.*")
        window.wait("visible", timeout=5)
        return window
    except Exception:
        return None


def type_text(text):
    window = get_notepad()

    if not window:
        return {
            "success": False,
            "reason": "Notepad is not open",
            "action": "type"
        }

    try:
        window.set_focus()
        send_keys(text, with_spaces=True)

        return {"success": True, "action": "type"}

    except Exception as e:
        return {
            "success": False,
            "reason": str(e),
            "action": "type"
        }


def copy():
    return press_key("^c")


def paste():
    return press_key("^v")


def cut():
    return press_key("^x")


def backspace():
    return press_key("{BACKSPACE}")


def delete():
    return press_key("{DELETE}")


def select_all():
    return press_key("^a")


def press_key(key):
    window = get_notepad()

    if not window:
        return {
            "success": False,
            "reason": "Notepad is not open",
            "action": key
        }

    try:
        window.set_focus()
        send_keys(key)

        return {"success": True, "action": key}

    except Exception as e:
        return {
            "success": False,
            "reason": str(e),
            "action": key
        }