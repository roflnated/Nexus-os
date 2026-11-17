# Local AI setup

NEXUS AI uses Ollama's local HTTP API on `127.0.0.1:11434`.

1. Install Ollama using the official instructions for your distribution.
2. Start its system service or run `ollama serve`.
3. Download a model, e.g. `ollama pull llama3.2:3b`.
4. Open NEXUS OS → NEXUS AI and enter the same model identifier.

No API key is required. The model runs locally, but it uses system RAM/VRAM and
can be slow if the model is too large. Do not expose the Ollama port to your LAN
or the public internet unless you understand and secure that configuration.
