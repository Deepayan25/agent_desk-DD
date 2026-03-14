import subprocess
import actions

print("AgentDesk started. Type 'exit' to stop.")

def action_parser(command, actions):
    words = command.split()

    if not words:
        return

    action = words[0]
    data = " ".join(words[1:])

    if action in actions:
        actions[action](data)
    else:
        print("Unknown command") 



while True:
    command = input(">> ").strip().lower()

    if command == "exit":
        print("AgentDesk shutting down...")
        break

    action_parser(command, actions.actions)

    