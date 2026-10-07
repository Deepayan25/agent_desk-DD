import time
import pyautogui


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUGGER_ADDRESS = "127.0.0.1:9222"
MANAS_PROFILE = r"%TEMP%\MANAS-Chrome"

def launch_browser():
    """Launch the dedicated MANAS Chrome profile using PyAutoGUI."""
    try:
        pyautogui.hotkey("win", "r")
        time.sleep(1)

        pyautogui.write("cmd", interval=0.03)
        pyautogui.press("enter")
        time.sleep(1.5)

        command = (
            f'"{CHROME_PATH}" '
            f'--remote-debugging-port=9222 '
            f'--user-data-dir="{MANAS_PROFILE}"'
        )

        pyautogui.write(command, interval=0.01)
        pyautogui.press("enter")
        time.sleep(2)

        return {"success": True, "action": "launch_browser"}

    except Exception as e:
        return {
            "success": False,
            "reason": str(e),
            "action": "launch_browser",
        }