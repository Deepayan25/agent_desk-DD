# MANAS (formerly AgentDesk)

> **A local-first Personal AI Operating System built in Python.**

MANAS is an open-source AI desktop assistant designed to bridge natural language and real desktop automation. It aims to become an intelligent local companion capable of understanding human instructions, reasoning about workflows, and interacting with applications just like a human user.

Unlike traditional voice assistants, MANAS is being built as a desktop operating layer—combining automation, natural language understanding, local AI models, and an evolving graphical interface into a single system.

> **Current Status:** Active Development (v0.6.1)

---

# Features

### Natural Language Commands

Control your computer using plain English.

Examples:

```text
open notepad
search python in youtube
play lofi music
what is reinforcement learning
open notepad then type hello world
```

---

### Intent Understanding

MANAS converts natural language into structured executable actions.

Current capabilities include:

* Intent parsing
* Sequential command execution
* Platform detection
* Alias handling
* Question-to-search conversion
* Workflow state tracking

---

### Desktop Automation

Current support:

* Application launching
* Keyboard automation
* Mouse automation
* Web search
* Multi-step workflows
* Selenium browser automation prototype

upcoming:

* PyWinAuto desktop automation

---

### Desktop Interface

Current UI includes:

* PyQt6 desktop application
* Background worker thread
* Floating console prototype
* Draggable interface components
* Foundation for future dashboard

The UI is being developed progressively alongside new capabilities rather than all at once.

---

### Interactive Codebase Visualizer

Generate an interactive graph of the entire project.

```bash
python visualize_codebase.py
```

Visualizes:

* Modules
* Functions
* Imports
* Call relationships

Useful for understanding project architecture and onboarding contributors.

---

# Architecture

```
MANAS

├── main.py
│   Application entry point
│
├── controller.py
│   Command execution pipeline
│
├── intent.py
│   Natural language understanding
│
├── actions/
|    |- keyboard.py
|    |- browser.py
|    |- _init_.py
|.   |- system.py
│
├── UI.py
│   PyQt6 desktop interface
│
├── visualize_codebase.py
│   Interactive architecture visualizer
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/agent_desk-DD.git
cd agent_desk-DD
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run MANAS

```bash
python main.py
```

---

# Current Roadmap

## v0.6

* Selenium integration
* PyWinAuto integration
* Browser automation
* Expanded UI

## v0.7

* Memory system
* Context awareness
* Improved reasoning

## v0.8

* Local LLM integration (Qwen)
* Streaming responses
* AI conversation

## v0.9

* Autonomous workflows
* Agent improvements
* Plugin architecture

## v1.0

First public beta of the MANAS Personal AI Operating System.

---

# Version History

### v0.1

* Interactive command loop
* Application launcher

### v0.2

* Text typing
* Web search
* Modular action system

### v0.2.1

* Sequential command execution
* Multiple commands

### v0.3

* Intent parsing
* Stopword filtering
* Platform detection

### v0.4

* Structured intent pipeline
* Workflow execution improvements
* Alias mapping
* Sequential command parsing

### v0.4.1

* Stability fixes
* Regex improvements
* Empty input handling

### v0.5

Major architectural update.

Highlights:

* MVC-style project organization
* Workflow state tracking
* Execution queue
* Failure detection and recovery
* PyQt6 desktop interface
* QThread-based background execution
* Floating console prototype
* Interactive codebase visualization improvements

---

# Contributing

Contributions are welcome.

If you'd like to improve MANAS, feel free to open an issue or submit a pull request.

---

# Vision

The long-term goal of MANAS is to become a fully local AI operating system that can:

* Understand natural language
* Automate desktop applications
* Interact with browsers
* Execute complex workflows
* Integrate local language models
* Remember context across sessions
* Assist developers and everyday users through a modern desktop interface

Built with Python.
Designed for learning.
Built in public.
