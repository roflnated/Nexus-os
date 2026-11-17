# NEXUS OS 1.1 — Minimal Desktop Prototype

A practical next milestone for NEXUS ONE: minimal desktop shell, animated startup
screen, system overview, and local text AI integration.

## Requirements

- Fedora KDE or another Linux desktop
- Python 3.10+
- PySide6
- psutil
- Optional: Ollama installed and running locally

## Install dependencies

On Fedora:
```bash
sudo dnf install python3 python3-pip python3-psutil
python3 -m venv ~/.venvs/nexus
source ~/.venvs/nexus/bin/activate
pip install PySide6 psutil
```

Run:
```bash
python nexus/nexus_desktop.py
```

## Enable local AI

Install Ollama using its official instructions, start the service, then pull a
model appropriate for your memory and GPU:

```bash
ollama pull llama3.2:3b
ollama serve
```

If Ollama is already running as a service, you usually do not need to run
`ollama serve` in a second terminal. In NEXUS AI, select `llama3.2:3b` and chat.

The app sends requests only to `http://127.0.0.1:11434/api/chat`. It does not
connect to a cloud model provider. Model availability and resource needs depend
on the model you download.

## What's implemented

- Minimal overview, AI and system pages
- NEXUS midnight palette
- Startup splash with staged status labels and progress animation
- Fade-in transition to desktop
- CPU, RAM and root filesystem status
- Ollama chat via background worker (UI remains responsive)
- Editable local model selection
- Clear local-service error messaging

## Limitations

This is a desktop application prototype, not a complete desktop environment or
bootable ISO. It does not yet replace KDE's shell, manage GPU overclocking,
control fans, install drivers, or provide a privileged AI agent. GPU telemetry,
notifications, settings persistence, accessibility review, packaging, signing,
and automated tests are future milestones.
