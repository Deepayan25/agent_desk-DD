import actions as action_module

print("AgentDesk started. Type 'exit' to stop.")

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
        print("Unknown command") 

while True:
    command = input(">> ").strip().lower()

    if command == "exit":
        print("AgentDesk shutting down...")
        break                               
    commands = command.replace(" and ", ",").split(",")
    commands = [cmd.strip() for cmd in commands if cmd.strip()]
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            action_parser(cmd, action_module.actions)
