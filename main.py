import actions as action_module
import intent as intent_module
print("Hi there! I'm AgentDesk, your personal desktop assistant. How can I help you today?")

def action_parser(command, actions):
    words = command.split()

    if not words:
        return

    action = words[0]
    data = " ".join(words[1:]).strip()
    
    if data in action_module.aliases:
        data= action_module.aliases[data]

    if action in action_module.actions:
        action_module.actions[action](data)
    else:
        print(f"Unknown command: {action}")

while True:
    command = input(">> ").strip().lower()

    if command == "end":
        print("Goodbye! Have a great day!")
        break   

    parsed = intent_module.parse_intent(command)
    if parsed:
        command = parsed
    else:
        print("Could not understand the command. Please try again.")
        continue

    commands = command.replace(" and ", ",").split(",")
    commands = [cmd.strip() for cmd in commands if cmd.strip()]
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            action_parser(cmd, action_module.actions)
