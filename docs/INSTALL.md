# Installation Guide

## Quick Install

### Option 1: pip install (Recommended)

```bash
pip install openmemory
```

### Option 2: OpenClaw Plugin Install

```bash
# In OpenClaw directory
openclaw skill install openmemory

# Or manually
git clone https://github.com/openmemory/openmemory.git ~/.openclaw/skills/openmemory
cd ~/.openclaw/skills/openmemory
pip install -e .
```

### Option 3: From Source

```bash
git clone https://github.com/openmemory/openmemory.git
cd openmemory
pip install -r requirements.txt
pip install -e .
```

## OpenClaw Configuration

Add to your `~/.openclaw/config.json`:

```json
{
  "skills": {
    "openmemory": {
      "enabled": true,
      "config": {
        "base_path": "~/.openclaw/memory",
        "use_vector": true,
        "auto_extract": true
      }
    }
  },
  "memory": {
    "provider": "openmemory",
    "hooks": {
      "onMessage": ["openmemory.extract"],
      "beforeReply": ["openmemory.inject_context"]
    }
  }
}
```

## Verify Installation

```python
from openmemory import OpenMemory

mem = OpenMemory(user_id="test")
mem.add("Test memory", category="test")
results = mem.search("test")
print(f"Found {len(results)} memories")
```

## Troubleshooting

### ImportError: No module named 'faiss'

```bash
# macOS
brew install faiss

# Linux
sudo apt-get install libfaiss-dev

# Or use conda
conda install -c pytorch faiss-cpu
```

### Permission Denied

```bash
# Install with user flag
pip install --user openmemory
```

## Uninstall

```bash
pip uninstall openmemory
```
