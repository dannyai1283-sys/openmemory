"""
Example usage of OC-Mem with OpenClaw
"""

from ocmem import OpenClawMemory, MemoryConfig


def main():
    """Demo OC-Mem capabilities"""
    
    # Initialize memory system
    print("🧠 Initializing OC-Mem...")
    mem = OpenClawMemory(
        user_id="demo_user",
        agent_id="assistant"
    )
    
    # Add various types of memories
    print("\n💾 Adding memories...")
    
    # Preferences
    mem.add("I prefer concise answers", category="preference", importance=0.7)
    mem.add("I like Python over JavaScript", category="preference")
    
    # Critical facts
    mem.add("I'm allergic to peanuts", category="fact", importance=0.95)
    mem.add("I work as a software engineer", category="fact", importance=0.8)
    
    # Tasks
    mem.add("Finish the project proposal by Friday", category="task", importance=0.9)
    
    print("✅ Memories stored")
    
    # Search for relevant memories
    print("\n🔍 Searching: 'dietary restrictions'")
    results = mem.search("dietary restrictions", limit=3)
    for r in results:
        print(f"  - {r['content']} (score: {r.get('score', 'N/A'):.2f})")
    
    # Get context for LLM
    print("\n📄 Getting context for LLM...")
    context = mem.get_context(max_tokens=500)
    print(f"Context:\n{context}")
    
    # Extract from conversation
    print("\n📝 Extracting from conversation...")
    conversation = [
        {"role": "user", "content": "I need to prepare for my presentation next Monday."},
        {"role": "assistant", "content": "I'll help you prepare. What's the topic?"},
        {"role": "user", "content": "It's about AI agents. I prefer to practice in the morning."}
    ]
    
    extracted = mem.extract_from_conversation(conversation)
    print(f"Extracted {len(extracted)} memories:")
    for e in extracted:
        print(f"  - [{e['category']}] {e['content']} (importance: {e['importance']})")
    
    print("\n✨ Demo complete!")


if __name__ == "__main__":
    main()
