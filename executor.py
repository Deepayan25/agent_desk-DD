import re
import time

import actions
import intent as intent_module

workflow_state = {
    "current_step": 0,
    "total_steps": 0,
    "status": "idle",
    "last_completed_action": None,
    "last_successful_step": None,
    "failed_step": None,
    "failure_reason": None,
    "current_app": None,
    "retry_count": 0,
}

def normalize_aliases(text):
    if not isinstance(text, str) or not text:
        return text

    words = text.split()

    return " ".join(actions.aliases.get(word, word) for word in words)

def dispatch_action(action, query="", platform=None):
    if action not in actions.actions:
        print(f"Unknown action: {action}")
        return {"success": False, "reason": "Unknown action", "action": action}

    handler = actions   .actions[action]
    if platform is not None:
        return handler(query, platform)
    return handler(query)

def action_parser(command):
    if isinstance(command, list):
        return [action_parser(item) for item in command]

    if isinstance(command, dict):
        action = command.get("action")
        query = normalize_aliases(command.get("query", ""))
        platform = command.get("platform")
        if isinstance(platform, str):
            platform = actions.aliases.get(platform, platform)
        print(f"Parsed intent - Action: {action}, Query: {query}, Platform: {platform}")
        return dispatch_action(action, query, platform)

    if isinstance(command, str):
        words = command.split()
        if not words:
            return {"success": False, "reason": "Empty command", "action": None}

        action = words[0]
        data = normalize_aliases(" ".join(words[1:]).strip())
        return dispatch_action(action, data)

    return {"success": False, "reason": "Unsupported command type", "action": None}

def handle_failure(result):
    if not result:
        result = {"action": None, "reason": "Unknown failure"}

    return {
        "action": result.get("action"),
        "reason": result.get("reason"),
        "options": ["retry", "skip", "stop"]
    }

def split_commands(raw):
    split_pattern = r"\band then\b|\bafter that\b|\bthen\b|\band\b"
    chunks = re.split(split_pattern, raw)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def build_execution_queue(raw):
    execution_queue = []
    for chunk in split_commands(raw):
        parsed = intent_module.parse_intent(chunk)
        if isinstance(parsed, list):
            execution_queue.extend(parsed)
        elif parsed:
            execution_queue.append(parsed)
        else:
            execution_queue.append(chunk)
    return execution_queue

def execute_raw_command(raw):
    results = []
    for item in build_execution_queue(raw):
        result = action_parser(item)
        if isinstance(result, list):
            results.extend(result)
        else:
            results.append(result)
        time.sleep(1)
    return results

def execution_workflow(raw):
    global workflow_state
    results = []

    workflow_state["status"] = "idle"
    workflow_state["retry_count"] = 0
    workflow_state = {
            "current_step": 0,
            "total_steps": 0,
            "status": "idle",
            "last_completed_action": None,
            "last_successful_step": None,
            "failed_step": None,
            "failure_reason": None,
             "current_app": None,
            "retry_count": 0,
    }
    execution_queue = build_execution_queue(raw)
    workflow_state["total_steps"] = len(execution_queue)
    workflow_state["current_step"] = 0
    workflow_state["status"] = "running"
    workflow_state["failed_step"] = None
    workflow_state["failure_reason"] = None

    stop_execution = False
    for item in execution_queue:
            if stop_execution:
                break

            result = action_parser(item)

            if isinstance(result, list):
                results.extend(result)
            else:
                results.append(result)  
            time.sleep(1)
            

            if result and result.get("success"):
                if isinstance(item, dict):
                    workflow_state["last_completed_action"] = item.get("action")
                    workflow_state["last_successful_step"] = workflow_state["current_step"]
                    if item.get("action") == "open":
                        workflow_state["current_app"] = item.get("query")
            else:
                workflow_state["failed_step"] = workflow_state["current_step"] + 1 
                workflow_state["failure_reason"] = (
                    f"Action '{item.get('action') if isinstance(item, dict) else item}' failed"
                )
                workflow_state["status"] = "failed"

                failure = handle_failure(result)

                workflow_state["status"] = "waiting"

                return results + [{
                    "success": False,
                    "waiting_for_user": True,
                    "failure": failure
                }]
            workflow_state["current_step"] += 1

    if not stop_execution:
            workflow_state["status"] = "completed"

    return results


def run_CLI():
    
    while True:
        raw = input(">> ").strip()

        if raw == "end":
            print("Goodbye! Have a great day!")
            break

        if not raw:
            continue

        execution_workflow(raw)