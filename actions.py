import subprocess
import time
import pyautogui
import webbrowser

def open_app(target):
    try:
        subprocess.Popen(["cmd", "/c", "start", target])
        time.sleep(2)  
    except Exception as e:
        print("Could not open:", target)
    
def type_text(text):
    try:
        pyautogui.write(text, interval=0.05)
        if not text:
           print("No text provided to type.")
    except Exception as e:
        print("Typing failed:", e)

def press_enter(_):
    try:
        pyautogui.press('enter')
    except Exception as e:
        print("Failed to press enter:", e)

def backspace(data):
    try:
        if not data:
            pyautogui.hotkey("ctrl", "backspace")
        elif data.isdigit():
            pyautogui.press("backspace", presses=int(data))
        else:
            pyautogui.hotkey("ctrl", "backspace")
    except Exception as e:
        print("Failed to press backspace:", e)

def wait(sec):
    try:
        if not sec:
            seconds = 1
        elif not sec.isdigit():
            print("Invalid wait time")
            return
        else:
            seconds = int(sec)
        time.sleep(seconds)

    except Exception as e:
        print("Wait failed:", e)

def focus_search(_):
    try:
        pyautogui.click(500,300)
        pyautogui.press('/')
    except Exception as e:
        print("Failed to focus search bar:", e)        

actions = {
    "open": open_app,
    "type": type_text,
    "wait": wait,   
    "enter": press_enter,
    "del": backspace,
    "focus": focus_search

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