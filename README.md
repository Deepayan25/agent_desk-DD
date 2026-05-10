# AgentDesk

AgentDesk is a command-activated desktop automation agent written in Python.
The goal of the project is to build a local AI assistant capable of executing system commands, automating tasks, and eventually understanding natural language instructions.

## v0.1 Features

- Interactive command loop
- Open desktop applications through commands
- Runs continuously until the user exits

Example usage:
open notepad
open chrome
exit

## v0.2 features ( date : 14 - 03 - 2026 )

- Continuous command loop
- Application launcher (open apps)
- Text typing automation
- Web search command
- Modular action system (actions.py)
- Command parser for routing actions

## v0.2.1 features ( date : 18 - 03 - 2026 )

- Multiple command running
- Sequential command running

Example Commands:
open notepad
open notepad and type hello world
search python threading
exit

## v0.3 features ( date : 13 - 04 - 2026 )

- Basic intent parsing (natural language to commands)
- Stopword filtering for cleaner input processing
- Keyword-based action detection (play, search, watch, etc.)
- Dynamic query extraction from user input
- Default platform handling (e.g., YouTube for media queries)
- Integration of intent layer with command execution pipeline

## v0.4 features ( date : 25 - 04 - 2026 )

- Structured intent output (dict-based pipeline)
- Multi-intent sequential splitting (`then`, `and then`, `after that`)
- Platform modifier extraction (`in youtube`, `on google`)
- Question patterns mapped to search (`what is`, `how to`, `who is`, etc.)
- Noise word stripping (`while coding`, `during work`)
- Compound action handling (`type X in notepad` → open then type)
- Alias mapping restored and integrated into dict pipeline
- Auto-wait between sequential commands for stable execution

Example Commands:
search python in youtube
what is machine learning
play lofi while i work
open notepad then type hello world
type hello in np
i want to search django then play lofi music

## Project Goal

Future versions of AgentDesk will include:

* Context-aware stateful command execution
* Smart auto-wait based on app load detection
* Multi-platform search routing
* Full natural language understanding
* Workflow automation
* Permission-based application control

## How to Run

1. Clone the repository
2. Install dependencies
pip install pyautogui
3. Run the agent

## Codebase Graph Viewer

To generate an interactive graph of the current Python codebase:

```bash
python visualize_codebase.py
```

This creates `codebase_graph.html` in the project root.

The viewer shows:
- modules
- top-level functions
- local import relationships
- external dependencies
- call references collected from the Python AST

You can open the generated HTML file in a browser and:
- drag nodes
- zoom and pan
- filter node and edge types
- inspect neighbors of a selected node
