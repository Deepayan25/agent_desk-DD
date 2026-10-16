import subprocess
import time

def open_app(target, platform=None):
    if not target:
        print("No app mentioned to open.")
        return {"success": False, "reason": "No target specified", "action": "open"}
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)
        return {"success": True, "action": "open"}
    except Exception as e:
        return {"success": False, "reason": str(e), "action": "open"}

def wait(sec, platform=None):
    try:
        seconds = int(sec) if sec and sec.isdigit() else 1
        time.sleep(seconds)
    except Exception as e:
        print("Wait failed:", e)
        return {"success": False, "reason": "Failed to wait", "action": "wait"}
    return {"success": True, "action": "wait"}

def show_help(data=None, platform=None):
    help_text = """
╔══════════════════════════════════════╗
║           AGENTDESK HELP             ║
╠══════════════════════════════════════╣
║  BROWSER                             ║
║  play <song> on youtube              ║
║  search <query>                      ║
║  search <query> on google            ║
║                                      ║
║  SYSTEM                              ║
║  open <app>  (np, xl, word, cal)     ║
║  wait <seconds>                      ║
║                                      ║
║  KEYBOARD                            ║
║  type <text>                         ║
║  enter                               ║
║  del / del line / del <n>            ║
║  prevline                            ║
║  focus                               ║
║                                      ║
║  CHAINING                            ║
║  open np and write hello manas       ║
║  search cats then open youtube       ║
║                                      ║
║  OTHER                               ║
║  help                                ║
║  end                                 ║
╚══════════════════════════════════════╝
"""
    print(help_text)
    return {"success": True, "action": "help"}