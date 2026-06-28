import subprocess, sys, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Restarter(FileSystemEventHandler):
    def __init__(self):
        self.proc = self.start()
    
    def start(self):
        return subprocess.Popen([sys.executable, "main.py"])
    
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("Change detected, restarting...")
            self.proc.kill()
            time.sleep(0.3)
            self.proc = self.start()

handler = Restarter()
obs = Observer()
obs.schedule(handler, path=".", recursive=False)
obs.start()
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    obs.stop()