# MANAS

> **A local-first Personal AI Operating System built in Python.**

MANAS is an open-source AI desktop assistant designed to bridge natural language and real desktop automation. It aims to become an intelligent local companion capable of understanding human instructions, reasoning about workflows, and interacting with applications just like a human user.

Unlike traditional voice assistants, MANAS is being built as a desktop operating layer — combining automation, natural language understanding, local AI models, and an evolving graphical interface into a single system.

> **Current Status:** Active Development (v0.6.2)

---

# Features

### Natural Language Commands

Control your computer using plain English.

Examples:

```text
open notepad
play lofi music
search python on google
nav youtube
scroll down 500
```

---

### Intent Understanding

MANAS converts natural language into structured executable actions.

Current capabilities include:

- Intent parsing
- Sequential command execution
- Platform detection
- Alias handling
- Question-to-search conversion
- Workflow state tracking

---

### Desktop Automation

Current support:

- Application launching
- Keyboard automation
- Mouse automation
- Web search
- Multi-step workflows
- Selenium-based browser automation (CDP attach mode)
- Page scrolling (direction + distance)

Upcoming:

- PyWinAuto desktop automation
- Page reading, clicking, and typing via `interactions.py`
- Browser command loop ("what to do, sir?")
- Natural language browser commands

---

### Desktop Interface

Current UI includes:

- PyQt6 desktop application
- Background worker thread (QThread-based)
- Two-queue worker pattern (commands + responses)
- Floating console
- Draggable interface components
- Foundation for future dashboard

The UI is being developed progressively alongside new capabilities rather than all at once.

---

### Interactive Codebase Visualizer

Generate an interactive graph of the entire project.

```
python visualize_codebase.py
```

Visualizes:

- Modules
- Functions
- Imports
- Call relationships

Useful for understanding project architecture and onboarding contributors.

---

# Architecture

```
MANAS

├── main.py
│   Application entry point
│
├── UI.py
│   PyQt6 interface + background worker thread
│
├── executor.py
│   Command execution pipeline and workflow state
│
├── intent.py
│   Natural language understanding
│
├── actions/
│   ├── __init__.py
│   │   Action registry + alias map
│   │
│   ├── system.py
│   │   App launching, wait, help
│   │
│   ├── keyboard.py
│   │   Keyboard automation (type, enter, del, focus)
│   │
│   ├── pywinauto.py
│   │   Window-scoped automation (Notepad-focused for now)
│   │
│   └── browser_tools/
│       ├── launcher.py
│       │   Launches dedicated MANAS Chrome with debug port
│       │
│       ├── controller.py
│       │   Attaches Selenium to MANAS Chrome
│       │
│       ├── navigation.py
│       │   URL opening, web search, YouTube search
│       │
│       └── interactions.py
│           Page-level actions (scroll, and eventually read/click/type)
│
└── visualize_codebase.py
    Interactive architecture visualizer
```

The browser layer was extracted from a single `browser.py` file into the modular `browser_tools/` package. Each module has one job: launch, attach, navigate, or interact.

---

# Installation

Clone the repository

```
git clone https://github.com/<your-username>/agent_desk-DD.git
cd agent_desk-DD
```

Install dependencies

```
pip install -r requirements.txt
```

Run MANAS

```
python main.py
```

---

# Current Roadmap

## v0.6 — Browser Foundation *(in progress)*

- ✅ Selenium integration (CDP attach mode)
- ✅ Dedicated MANAS Chrome profile
- ✅ URL navigation, web search, YouTube search
- ✅ Page scrolling
- ⏳ Browser command loop ("what to do, sir?")
- ⏳ Read, click, type interactions
- ⏳ PyWinAuto integration

## v0.7

- Memory system
- Context awareness
- Improved reasoning

## v0.8

- Local LLM integration (Qwen / Gemma)
- Streaming responses
- AI conversation
- Strict-schema planner mode

## v0.9

- Autonomous workflows
- Agent improvements
- Plugin architecture

## v1.0

First public beta of the MANAS Personal AI Operating System.

---

# Version History

### v0.1

- Interactive command loop
- Application launcher

### v0.2

- Text typing
- Web search
- Modular action system

### v0.2.1

- Sequential command execution
- Multiple commands

### v0.3

- Intent parsing
- Stopword filtering
- Platform detection

### v0.4

- Structured intent pipeline
- Workflow execution improvements
- Alias mapping
- Sequential command parsing

### v0.4.1

- Stability fixes
- Regex improvements
- Empty input handling

### v0.5

Major architectural update.

- MVC-style project organization
- Workflow state tracking
- Execution queue
- Failure detection and recovery
- PyQt6 desktop interface
- QThread-based background execution
- Floating console prototype
- Interactive codebase visualization improvements

### v0.6

Browser automation arrives.

- Selenium attached to a dedicated MANAS Chrome instance (CDP on port 9222)
- Modular `browser_tools/` package replacing the old `browser.py`
- URL navigation, web search, YouTube search
- Page scrolling (`scroll down`, `scroll up`, `scroll down 500`)
- Two-queue worker pattern in `UI.py` (commands + responses) for future interactive loops
- Rewritten `open_app` (fire-and-forget, no more timeouts)
- Clean launch path — no Win+R, no CMD flashing

### v0.6.2

- Fixed 60-second Selenium attach delay (port check before driver call)
- `scroll` interaction added to `browser_tools/interactions.py`
- Retired `browser.py`

---

# Contributing

Contributions are welcome.

If you'd like to improve MANAS, feel free to open an issue or submit a pull request.

---

# Vision

The long-term goal of MANAS is to become a fully local AI operating system that can:

- Understand natural language
- Automate desktop applications
- Interact with browsers
- Execute complex workflows
- Integrate local language models
- Remember context across sessions
- Assist developers and everyday users through a modern desktop interface

Built with Python.
Designed for learning.
Built in public.