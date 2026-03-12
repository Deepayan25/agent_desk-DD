import subprocess


def open_app(target):
    try:
        subprocess.Popen(["cmd", "/c", "start", target])
    except Exception as e:
        print("Could not open:", target)


def type_text(text):
    pass


def search_web(query):
    pass


actions = {
    "open": open_app,
    "type": type_text,
    "search": search_web
}