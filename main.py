import actions as action_module
import intent as intent_module
import time
import re
print("Hi there! I'm AgentDesk, your personal desktop assistant. How can I help you today?")

def action_parser(command):
    if isinstance(command, dict):
        action = command.get("action")
        query = command.get("query", "")
        platform = command.get("platform")

        if query in action_module.aliases:
            query = action_module.aliases[query]
        print(f"Parsed intent - Action: {action}, Query: {query}, Platform: {platform}")
        if action in action_module.actions:
            if platform:
                action_module.actions[action](query, platform)
            else:
                action_module.actions[action](query)
        else:
            print(f"Unknown action: {action}")
        return
    
    words = command.split()
    if not words:
        return

    action = words[0]
    data = " ".join(words[1:]).strip()
    
    for key in action_module.aliases:
        if key in data:
           data = data.replace(key, action_module.aliases[key])

    if action in action_module.actions:
        action_module.actions[action](data)
    else:
        print(f"Unknown command: {action}")


while True:
    raw = input(">> ").strip().lower()

    if raw == "end":
        print("Goodbye! Have a great day!")
        break   

    if not raw:
        continue

    split_pattern = r'\band\b |\band then\b|\bthen\b|\bafter that\b'
    chunks = re.split(split_pattern, raw)
    
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        parsed = intent_module.parse_intent(chunk)
        if isinstance(parsed, list):
            for item in parsed:
                action_parser(item)
                time.sleep(3)
        elif parsed:
            action_parser(parsed)
            time.sleep(3)
        else:
            action_parser(chunk) 
            time.sleep(3)