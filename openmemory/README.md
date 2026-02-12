# OpenClaw Memory System (OC-Mem)

> A mem0-inspired memory layer for OpenClaw AI Agents

## Overview

OC-Mem provides intelligent memory management for AI agents, enabling:

- **Multi-level memory**: Ephemeral, short-term, long-term, and shared knowledge
- **Semantic search**: Find relevant memories using embeddings
- **Auto-extraction**: LLM-powered memory extraction from conversations
- **Smart deduplication**: Merge similar memories automatically
- **Importance scoring**: Prioritize critical information

## Installation

```bash
# Clone and install
cd /Volumes/M2Sata/DannyAI/ocmem
pip install -e .

# Or install dependencies directly
pip install faiss-cpu sentence-transformers sqlite3
```

## Quick Start

```python
from ocmem import OpenClawMemory

# Initialize
mem = OpenClawMemory(
    user_id="danny",
    agent_id="main"
)

# Add memories
mem.add("I prefer working in the morning", category="preference")
mem.add("I'm allergic to peanuts", category="fact", importance=0.95)
mem.add("Review the quarterly report by Friday", category="task")

# Search
results = mem.search("when do I work best?")
# Returns: [{"content": "prefers working in morning", "score": 0.92}]

# Get context for current session
context = mem.get_context(max_tokens=1000)
# Returns formatted context string
```

## Architecture

```
┌─────────────────────────────────────┐
│         OpenClawMemory              │
│  (High-level interface)             │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼─────┐ ┌──▼──────┐
│Short  │ │ Long    │ │ Vector  │
│Term   │ │ Term    │ │ Store   │
│(Redis)│ │ (SQLite)│ │ (FAISS) │
└───────┘ └─────────┘ └─────────┘
```

## Configuration

```python
from ocmem import MemoryConfig

config = MemoryConfig(
    base_path="~/.openclaw/ocmem",
    use_vector=True,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    auto_extract=True
)

mem = OpenClawMemory(config=config)
```

## Features

### 1. Automatic Memory Extraction

```python
messages = [
    {"role": "user", "content": "I'm a vegetarian and allergic to nuts."},
    {"role": "assistant", "content": "Got it! I'll remember your dietary preferences."}
]

memories = mem.extract_from_conversation(messages)
# Automatically extracts and stores:
# - "User is vegetarian" (category: preference)
# - "User is allergic to nuts" (category: fact, importance: 0.95)
```

### 2. Semantic Search

```python
# Find relevant memories even with different wording
results = mem.search("user dietary restrictions")
# Finds: "User is vegetarian", "User is allergic to nuts"
```

### 3. Smart Deduplication

```python
# Similar memories are automatically merged
mem.add("I like pizza")
mem.add("I really enjoy pizza")  # Merged with existing
```

### 4. Context Injection

```python
# Get formatted context for LLM prompts
context = mem.get_context(max_tokens=2000)

prompt = f"""
Relevant context:
{context}

User: {user_message}
"""
```

## Memory Categories

- `preference` - User likes/dislikes
- `fact` - Objective information
- `task` - Action items and goals
- `context` - Session-specific info
- `skill` - Learned patterns
- `goal` - User objectives

## Comparison with mem0

| Feature | mem0 | OC-Mem |
|---------|------|--------|
| Multi-level memory | ✅ | ✅ |
| Semantic search | ✅ | ✅ |
| Auto-extraction | ✅ | ✅ |
| Self-hosted | OSS | ✅ |
| OpenClaw integration | ❌ | ✅ |
| Local embeddings | ❌ | ✅ |

## Roadmap

- [x] Core memory interface
- [x] SQLite backend
- [x] Vector search (FAISS)
- [x] LLM extraction
- [ ] Redis short-term cache
- [ ] OpenClaw hooks integration
- [ ] Memory visualization UI
- [ ] Import from MEMORY.md

## License

MIT
