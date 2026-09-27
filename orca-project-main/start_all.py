"""
ORCA Launcher - one command to start everything.
----------------------------------------------------
Instead of manually opening 3 terminals for Ollama, the scheduler, and
the orchestrator, this script:
  1. Checks if Ollama is already running - starts it in its own window
     if not (leaves it alone if it's already up, so it doesn't duplicate
     an existing instance).
  2. Starts scheduler.py in its own window (background data polling).
  3. Runs orchestrator.py in THIS window (the interactive menu you
     actually type into).

Run with: python start_all.py
"""

import subprocess
import sys
import time
import requests

OLLAMA_URL = "http://localhost:11434"


def is_ollama_running() -> bool:
    try:
        requests.get(OLLAMA_URL, timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False


def main():
    # 1. Ollama
    if is_ollama_running():
        print("Ollama is already running - leaving it as is.")
    else:
        print("Starting Ollama in a new window...")
        subprocess.Popen(
            ["ollama", "serve"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        print("Waiting a few seconds for Ollama to come up...")
        for _ in range(15):
            if is_ollama_running():
                break
            time.sleep(1)
        else:
            print("Warning: Ollama doesn't seem to have started yet - "
                  "orchestrator.py may fail if it's still not ready.")

    # 2. Scheduler (data polling, every 3 minutes, its own window)
    print("Starting scheduler.py in a new window...")
    subprocess.Popen(
        [sys.executable, "scheduler.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    # 3. Orchestrator (interactive, runs right here)
    print("\nAll set - launching orchestrator.py now.\n")
    time.sleep(1)
    subprocess.run([sys.executable, "orchestrator.py"])


if __name__ == "__main__":
    main()
