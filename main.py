import actions
import time

print("AgentDesk started. Type 'exit' to stop.")

def action_parser(command, actions):
    words = command.split()

    if not words:
        return

    action = words[0]
    data = " ".join(words[1:]).strip()

    if action in actions:
        actions[action](data)
    else:
        print("Unknown command") 

while True:
    command = input(">> ").strip().lower()

    if command == "exit":
        print("AgentDesk shutting down...")
        break

    commands = command.split("and")
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            action_parser(cmd, actions.actions)
            time.sleep(1)
