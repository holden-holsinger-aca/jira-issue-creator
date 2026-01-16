# LLM Ticket Generator Setup Guide

## Overview

This document explains how to set up your environment to generate JIRA-style tickets using a local LLM via Ollama—no API keys or cloud services required.

## 1. System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.9+ (works with 3.13 as well)
- **Disk Space**: At least 3–8 GB free (for models and outputs)
- **Network**: Only needed once to download Ollama and the model. After that, usage can be fully offline.

## 2. Repository Files (Expected)

```
/project
  ├─ ticket_generator.py
  ├─ template.txt
  ├─ script.py
  └─ documentation/
      ├─ README-generator_setup.md
      └─ README-usage.txt
```

## 3. Dependencies

### Python Packages

- **ollama** - Python client to talk to the local Ollama server

### Installation

**Windows (PowerShell)**
```powershell
py -m pip install --upgrade pip
py -m pip install ollama
```

**macOS / Linux**
```bash
python3 -m pip install --upgrade pip
python3 -m pip install ollama
```

### Verify Installation

```bash
python -c "import ollama; print('ollama python client OK')"
```

### External Application

- **Ollama** (app/daemon) — the local runtime that executes LLMs on your machine.

## 4. Install Ollama (Local LLM Runtime)

> **Important**: Ollama is a standalone app—not a Python module. You run it from your system terminal, and your Python script talks to it via `http://localhost:11434`.

### Windows

1. Download & install Ollama for Windows from: https://ollama.com/download
2. After install, open a new PowerShell window so your PATH is refreshed.
3. Verify:
   ```powershell
   ollama --version
   ```
   If you get "not recognized": sign out/in or reboot so PATH updates.

### macOS

```bash
brew install ollama
# Or download the app from https://ollama.com/download
ollama --version
```

### Linux

Refer to: https://ollama.com/download for your distro's instructions.

## 5. Pull a Lightweight Model

For fast, high-quality ticket generation, `phi3` is the default model. You will have to update the code for another model.

```bash
ollama pull phi3
```

### Other Choices (Optional)

- **llama3.2 (3B)**: `ollama pull llama3.2`
- **mistral**: `ollama pull mistral`

You can switch models later by changing the `OLLAMA_MODEL` environment variable or updating the script.

## 6. Test Your Ollama Installation

```bash
ollama run phi3 "Say 'Ollama is ready'."
```

You should see a response in the terminal. If this works, the Ollama server is running and reachable.

## 7. Confirm Python ↔ Ollama Connectivity

Create a quick test script (`test_ollama.py`):

```python
from ollama import Client
c = Client()
resp = c.chat(
    model="phi3",
    messages=[
        {"role": "user", "content": "Hello"},
        {"role": "system", "content": "You are concise."}
    ]
)
print(resp["message"]["content"])
```

Run it:
```bash
python test_ollama.py
```

If you see a model response, you're all set.

## 8. Troubleshooting

### "ollama: command not found" / "not recognized"
- Open a new terminal after installation, or sign out/in.
- Verify PATH:
  - **Windows**: `where ollama`
  - **macOS/Linux**: `which ollama`

### Model download slow or fails
- Check your connection. You only need to pull once.

### Python script can't connect
- Ensure the Ollama service is running. A simple `ollama run phi3 "hi"` validates it.

### Insufficient VRAM/RAM
- Try a smaller model like `qwen2.5:1.5b` or `phi3` (both can run on CPU if needed, but slower).

### Corporate device restrictions
- If network blocks downloads, ask IT to allow ollama.com or download the model externally and import (advanced).

## 9. Security & Privacy Notes

- Everything runs locally. No API keys or external LLM endpoints are required.
- Data stays on your machine unless you opt into any cloud feature (not required for this workflow).

## 10. You're Ready!

Proceed to [README.md](README.md) to run the script and generate tickets.
