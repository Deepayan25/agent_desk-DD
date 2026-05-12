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
                return action_module.actions[action](query, platform)
            else:
                return action_module.actions[action](query)
        else:
            print(f"Unknown action: {action}")
        return False
    
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

workflow_state = {
    "current_step": 0,
    "total_steps": 0,
    "status": "idle",
    "last_completed_action": None,
    "last_successful_step": None,
    "failed_step": None,
    "failure_reason": None,
    "current_app": None,
    "retry_count": 0
}

while True:
    raw = input(">> ").strip().lower()

    if raw == "end":
        print("Goodbye! Have a great day!")
        break   

    if not raw:
        continue

    split_pattern = r'\band\b |\band then\b|\bthen\b|\bafter that\b'
    chunks = re.split(split_pattern, raw)
    chunks = [c.strip() for c in chunks if c.strip()]
    workflow_state["total_steps"] = len(chunks)
    workflow_state["current_step"] = 0
    workflow_state["status"] = "running"
    
    execution_queue = []
    for chunk in chunks:
        parsed = intent_module.parse_intent(chunk)
        if isinstance(parsed, list):
            execution_queue.extend(parsed)
        elif parsed:
            execution_queue.append(parsed)
        else:
            execution_queue.append(chunk)

    workflow_state["total_steps"] = len(execution_queue)

    for chunk in execution_queue:
        if isinstance(chunk, str):
            chunk = chunk.strip()
            if not chunk:
                continue
            parsed = intent_module.parse_intent(chunk)
        else:
            parsed = chunk
        if isinstance(parsed, list):
            for item in parsed:
                result = action_parser(item)
                time.sleep(3)
                workflow_state["current_step"] += 1
                if result:
                    workflow_state["last_completed_action"] = item.get("action")
                    workflow_state["last_successful_step"] = workflow_state["current_step"]
                    if item.get("action") == "open":
                        workflow_state["current_app"] = item.get("query")
                else:
                    workflow_state["failed_step"] = workflow_state["current_step"]
                    workflow_state["failure_reason"] = f"Action '{item.get('action')}' failed"
                    workflow_state["status"] = "failed"
                    print(f"Step {workflow_state['current_step']} failed: {workflow_state['failure_reason']}")
        elif parsed:
            result = action_parser(parsed)
            time.sleep(3)
            workflow_state["current_step"] += 1 
            if result:
                workflow_state["last_completed_action"] = parsed.get("action")
                workflow_state["last_successful_step"] = workflow_state["current_step"]
                if parsed.get("action") == "open":
                    workflow_state["current_app"] = parsed.get("query")
            else:
                workflow_state["failed_step"] = workflow_state["current_step"]
                workflow_state["failure_reason"] = f"Action '{parsed.get('action')}' failed"
                workflow_state["status"] = "failed"
                print(f"Step {workflow_state['current_step']} failed: {workflow_state['failure_reason']}")        
    workflow_state["status"] = "completed"
    print(workflow_state)