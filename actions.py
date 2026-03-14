import subprocess
import time
import pyautogui
import webbrowser

def open_app(target):
    try:
        subprocess.Popen(["cmd", "/c", "start", target])
    except Exception as e:
        print("Could not open:", target)


def type_text(text):
    try:
        time.sleep(3)  
        pyautogui.write(text, interval=0.05)
    except Exception as e:
        print("Typing failed:", e)



def search_web(query):
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
    except Exception as e:
        print("Web search failed:", e)


actions = {
    "open": open_app,
    "type": type_text,
    "search": search_web
}