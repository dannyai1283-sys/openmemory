"""
Example: OpenMemory with OpenClaw

This example shows how to integrate OpenMemory into an OpenClaw agent.
"""

from openmemory import OpenMemory, MemoryConfig


def openclaw_agent_example():
    """Example OpenClaw agent with memory"""
    
    # Initialize memory
    config = MemoryConfig(
        base_path="~/.openclaw/memory",
        use_vector=True,
        auto_extract=True
    )
    
    mem = OpenMemory(
        user_id="user_123",
        agent_id="assistant",
        config=config
    )
    
    # Simulate conversation
    conversation = [
        {"role": "user", "content": "My name is Alice and I'm a software engineer."},
        {"role": "assistant", "content": "Nice to meet you, Alice! I'll remember that."},
        {"role": "user", "content": "I prefer Python over JavaScript."},
        {"role": "assistant", "content": "Got it! You prefer Python."}
    ]
    
    # Extract memories automatically
    print("📝 Extracting memories from conversation...")
    memories = mem.extract_from_conversation(conversation)
    print(f"✅ Extracted {len(memories)} memories:")
    for m in memories:
        print(f"  - [{m.category}] {m.content}")
    
    # New message from user
    new_message = "What language should I use for my project?"
    
    # Retrieve relevant context
    print("\n🔍 Retrieving relevant context...")
    context = mem.get_context(max_tokens=500)
    print(f"Context:\n{context}\n")
    
    # Build prompt with context
    prompt = f"""
You are a helpful assistant. Use the following context about the user:

{context}

User: {new_message}
Assistant:
"""
    
    print("💬 Generated prompt with memory context:")
    print(prompt)
    
    # In production, this would call your LLM
    # response = llm.generate(prompt)


def standalone_example():
    """Standalone usage example"""
    
    print("=" * 50)
    print("OpenMemory Standalone Example")
    print("=" * 50)
    
    # Initialize
    mem = OpenMemory(user_id="demo")
    
    # Add preferences
    mem.add("I like concise answers", category="preference")
    mem.add("I work best in the morning", category="preference", importance=0.8)
    
    # Add facts
    mem.add("I'm allergic to peanuts", category="fact", importance=0.95)
    mem.add("I live in San Francisco", category="fact")
    
    # Search
    print("\n🔍 Search: 'dietary restrictions'")
    results = mem.search("dietary restrictions")
    for r in results:
        print(f"  - {r['content']} (score: {r.get('score', 'N/A')})")
    
    print("\n🔍 Search: 'when work best'")
    results = mem.search("when work best")
    for r in results:
        print(f"  - {r['content']}")


if __name__ == "__main__":
    standalone_example()
    print("\n" + "=" * 50)
    openclaw_agent_example()
