from .system import open_app, wait, show_help
from .keyboard import focus_search, type_text, press_enter, backspace, prev_line
from .browser_tools import open_url, search_web, search_youtube, navigate_to, scroll
from .pywinauto import get_notepad, type_text as pywinauto_type_text, press_key as pywinauto_press_key
actions = {
    "open": open_app,
    "wait": wait,
    "help": show_help,
    "focus": focus_search,
    "type": type_text,
    "enter": press_enter,
    "del": backspace,
    "prevline": prev_line,
    "search": search_web,
    "play": search_youtube,
    "nav": navigate_to,
    "openurl": open_url,
    "scroll": scroll
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