# NEXUS OS — GitHub upload guide

This archive combines the NEXUS OS 1.1 desktop prototype with the GitHub repository starter files.

## What is included
- `nexus/nexus_desktop.py`: the PySide6 desktop prototype
- `run-nexus.sh`: Linux launch helper
- `requirements.txt`: Python dependencies
- `docs/`: installation, architecture, and local AI notes
- `.github/`: issue templates and a basic Python checks workflow
- Project governance files: README, MIT License, contributing guide, security policy, roadmap, and changelog

This is a prototype application for Linux, not a bootable operating-system ISO or a finished Linux distribution.

## Upload the files to GitHub
1. Open your repository on GitHub.
2. Select the **Code** tab (not the Issues tab).
3. Choose **Add file → Upload files**.
4. Extract this ZIP on your computer first.
5. Open the extracted `NEXUS_OS_GitHub_Upload` folder and select all files and folders inside it.
6. Drag them into GitHub's upload area. Keep the folder structure intact, including the hidden `.github` folder.
7. Enter a commit message such as `Add NEXUS OS 1.1 prototype and project documentation`.
8. Select **Commit changes**.

If GitHub's browser uploader does not show hidden folders, upload `.github` separately or use GitHub Desktop.

## Run the prototype on Fedora or another Linux desktop
Install Python 3 and pip, then from the extracted project folder run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python nexus/nexus_desktop.py
```

For local AI chat, install Ollama separately, start its service, and download a model, for example:

```bash
ollama pull llama3.2:3b
```

The AI page expects Ollama at `http://127.0.0.1:11434`. If Ollama is not installed or running, the rest of the desktop prototype can still be explored, but local chat will not respond.

## Before announcing a release
Test on the Linux distributions and hardware you intend to support. The included workflow checks Python syntax; it does not certify hardware compatibility, NVIDIA telemetry, installation, security, or production readiness.
