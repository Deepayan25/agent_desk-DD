# AgentDesk

AgentDesk is a command-activated desktop automation agent written in Python.
The goal of the project is to build a local AI assistant capable of executing system commands, automating tasks, and eventually understanding natural language instructions.

## v0.1 Features

* Interactive command loop
* Open desktop applications through commands
* Runs continuously until the user exits

Example usage:

```
open notepad
open chrome
exit
```

## v0.2features ( date : 14 - 03 - 2026 )

Current Features
- Continuous command loop
- Application launcher (open apps)
- Text typing automation
- Web search command
- Modular action system (actions.py)
- Command parser for routing actions

## v0.2.1 features ( date : 18 - 03 - 2026 )

- multiple command running
- sequential comman running

Example Commands

open notepad
open notepad and type hello world
search python threading
exit

## v0.3 features ( date : 13 - 04 - 2026 )

- basic intent parsing (natural language to commands)
- stopword filtering for cleaner input processing
- keyword-based action detection (play, search, watch, etc.)
- dynamic query extraction from user input
- default platform handling (e.g., YouTube for media queries)
- integration of intent layer with command execution pipeline


## Project Goal

Future versions of AgentDesk will include:

* natural language understanding
* workflow automation
* reinforcement learning based decisions
* permission-based application control

## How to Run

1. Clone the repository
2. Run the agent

```
python main.py
```
