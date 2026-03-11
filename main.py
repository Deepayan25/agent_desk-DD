import subprocess

def open_app(app_name):
    try:
        subprocess.Popen("cmd /c start " + app_name, shell=True)
    except Exception as e:
        print("Could not open:", app_name)

print("AgentDesk started. Type 'exit' to stop.")

while True:
    command = input(">> ").strip().lower()

    if command == "exit":
        print("AgentDesk shutting down...")
        break

    if command.startswith("open "):
        app = command.split("open ", 1)[1]
        open_app(app)
    else:
        print("Unknown command") 