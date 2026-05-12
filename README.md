# AgentDesk

AgentDesk is a natural language desktop automation agent built in Python.
It converts plain English commands into executable desktop actions — opening apps, typing text, searching the web, and more.

---

## How to Run

```bash
# Install dependencies
pip install pyautogui

# Run the agent
python main.py
```

---

## Project Architecture

```
main.py       — input loop, sequential splitting, execution queue, workflow state
intent.py     — natural language → structured intent (dict)
actions.py    — actual execution of each action
```

---

## Version History

### v0.1
- Interactive command loop
- Open desktop applications
- Runs until user types `exit`

### v0.2 — 14 Mar 2026
- Text typing automation
- Web search command
- Modular action system via `actions.py`

### v0.2.1 — 18 Mar 2026
- Sequential command execution
- Multiple commands in one input

### v0.3 — 13 Apr 2026
- Basic intent parsing (natural language → commands)
- Stopword filtering
- Keyword-based action detection
- Default platform handling (e.g. YouTube for media queries)

### v0.4 — 25 Apr 2026
- Structured dict-based intent pipeline
- Sequential splitting via `then`, `and then`, `after that`
- Platform modifier extraction (`in youtube`, `on google`)
- Question patterns mapped to search (`what is`, `how to`, etc.)
- Noise word stripping (`while coding`, `during work`)
- Compound action handling (`type X in notepad` → open, then type)
- Alias mapping (`np` → notepad, `ggl` → chrome, etc.)
- Auto-wait between sequential commands

### v0.4.1 — 11 May 2026
- Fixed crash on empty input (guard order fix)
- Fixed `\band` regex matching inside words
- Added missing stopwords (`on`, `at`, `from`)

### v0.5a — 12 May 2026
- Workflow state tracking (`workflow_state` dict)
- Execution queue — all intents parsed and flattened before execution
- `total_steps` and `current_step` tracked accurately
- Success/failure detection across all actions
- Agent now knows what it did, what succeeded, and what failed

---

## Example Commands

```
open notepad
search python in youtube
what is machine learning
play lofi while i work
open notepad then type hello world
type hello in np
i want to search django then play lofi music
```

---

## Codebase Visualizer

```bash
python visualize_codebase.py
```

Generates `codebase_graph.html` — an interactive graph showing modules, functions, imports, and call references. Open in any browser.

---

## Project Goal

Building toward a fully local, natural language desktop agent with:
- Context-aware stateful execution
- Failure recovery with alternative paths
- Smart auto-wait based on app load detection
- Full NLU pipeline
- Desktop UI (no terminal required)