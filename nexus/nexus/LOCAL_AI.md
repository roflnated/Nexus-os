# Local AI

Install Ollama using its official documentation, start its local service, and
download a model such as `ollama pull llama3.2:3b`. In NEXUS AI, enter the exact
installed model name.

The prototype sends requests to `127.0.0.1:11434`. It does not require an API
key or cloud account. Model speed depends on model size and available RAM/VRAM.
Do not expose the Ollama service publicly without appropriate security.
