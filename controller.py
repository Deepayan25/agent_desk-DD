#Agent desk controller
# imported modules
import actions as action_module
import intent as intent_module
import time
import re

#parsing actions 
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
            return {"success": False, "reason": "Unknown action", "action": action}

    words = command.split()
    if not words:
        return {"success": False, "reason": "Empty command", "action": None}

    action = words[0]
    data = " ".join(words[1:]).strip()

    for key in action_module.aliases:
        if key in data:
            data = data.replace(key, action_module.aliases[key])

    if action in action_module.actions:
        return action_module.actions[action](data)
    else:
        print(f"Unknown command: {action}")
        return {"success": False, "reason": "Unknown command", "action": action}

#failure handler
def handle_failure(result):
    action = result.get("action")
    reason = result.get("reason")
    print(f"\nFailed: {action} — {reason}")
    print("Options: retry / skip / stop")
    choice = input(">> ").strip().lower()
    if choice == "retry":
        return "retry"
    elif choice == "skip":
        print("Skipping this step.")
        return "skip"
    elif choice == "stop":
        print("Stopping execution.")
        return "stop"
    else:
        print("Invalid choice. Skipping by default.")
        return "skip"

def run():  
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
    
#main loop
    while True:
        raw = input(">> ").strip()

        if raw == "end":
            print("Goodbye! Have a great day!")
            break

        if not raw:
            continue

        split_pattern = r'\band\b |\band then\b|\bthen\b|\bafter that\b'
        chunks = re.split(split_pattern, raw)
        chunks = [c.strip() for c in chunks if c.strip()]

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
        workflow_state["current_step"] = 0
        workflow_state["status"] = "running"

        stop_execution = False

        for item in execution_queue:
            if stop_execution:
                break

            result = action_parser(item)
            time.sleep(1)
            workflow_state["current_step"] += 1

            if result and result.get("success"):
                if isinstance(item, dict):
                    workflow_state["last_completed_action"] = item.get("action")
                    workflow_state["last_successful_step"] = workflow_state["current_step"]
                    if item.get("action") == "open":
                        workflow_state["current_app"] = item.get("query")
            else:
                workflow_state["failed_step"] = workflow_state["current_step"]
                workflow_state["failure_reason"] = f"Action '{item.get('action') if isinstance(item, dict) else item}' failed"
                workflow_state["status"] = "failed"

                choice = handle_failure(result)
                if choice == "retry":
                    result = action_parser(item)
                    workflow_state["retry_count"] += 1
                elif choice == "stop":
                    stop_execution = True

        if not stop_execution:
            workflow_state["status"] = "completed"    