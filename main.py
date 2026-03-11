import subprocess

command = input("Enter a command: ")

if command == "hello":
    print("agent: Hello! How can I assist you today?")

if command == "open notepad":
    print("agent: Opening Notepad for you...")
    subprocess.run(["notepad"]) 