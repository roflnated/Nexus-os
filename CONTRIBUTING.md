# Contributing

Thanks for helping improve NEXUS OS.

- Search existing issues before opening a new one.
- For large changes, discuss the idea in an issue first.
- State how you tested your change and on which Linux distribution/version.
- Include screenshots for UI changes.
- Do not add telemetry, cloud dependencies, or privileged operations without
  explicit design discussion and user consent.
- Never commit passwords, API keys, private keys, or personal data.

Development setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python nexus/nexus_desktop.py
```

Keep pull requests focused and document known limitations.
