"""LLM-based memory extraction"""

import json
from typing import List, Dict


EXTRACTION_PROMPT = """You are a memory extraction system for an AI agent.
Your task is to analyze the conversation and extract important information that should be remembered.

Extract the following types of memories:
1. **Preferences**: What the user likes/dislikes, their style, choices
2. **Facts**: Objective information about the user, their work, their situation
3. **Tasks**: Action items, goals, things the user wants to accomplish

For each memory, provide:
- content: The specific information to remember
- category: One of [preference, fact, task, general]
- importance: Score 0.0-1.0 (how important is this to remember)
- confidence: Score 0.0-1.0 (how certain are you about this)

Conversation:
{conversation}

Respond in JSON format:
{
  "memories": [
    {
      "content": "...",
      "category": "preference|fact|task|general",
      "importance": 0.8,
      "confidence": 0.9
    }
  ]
}"""


class LLMMemoryExtractor:
    """Extract memories from conversation using LLM"""
    
    def __init__(self, model=None):
        self.model = model
    
    def extract(
        self,
        messages: List[Dict[str, str]],
        extract_preferences: bool = True,
        extract_facts: bool = True,
        extract_tasks: bool = True
    ) -> List[Dict]:
        """
        Extract memories from conversation
        
        Args:
            messages: List of {"role": "user|assistant", "content": "..."}
            extract_preferences: Whether to extract preferences
            extract_facts: Whether to extract facts
            extract_tasks: Whether to extract tasks
        
        Returns:
            List of extracted memory dicts
        """
        # Format conversation
        conversation = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in messages
        ])
        
        # Build prompt
        prompt = EXTRACTION_PROMPT.format(conversation=conversation)
        
        # Call LLM (simplified - in production use proper API)
        try:
            response = self._call_llm(prompt)
            parsed = json.loads(response)
            memories = parsed.get("memories", [])
            
            # Filter by requested types
            if not extract_preferences:
                memories = [m for m in memories if m.get("category") != "preference"]
            if not extract_facts:
                memories = [m for m in memories if m.get("category") != "fact"]
            if not extract_tasks:
                memories = [m for m in memories if m.get("category") != "task"]
            
            # Filter low confidence
            memories = [m for m in memories if m.get("confidence", 0) > 0.6]
            
            return memories
            
        except Exception as e:
            print(f"Memory extraction error: {e}")
            return []
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM for extraction"""
        # In production, this would call OpenAI, Claude, or local model
        # For now, return a simple mock response
        
        # This is a placeholder - real implementation would use actual LLM
        return json.dumps({
            "memories": [
                {
                    "content": "User prefers detailed explanations",
                    "category": "preference",
                    "importance": 0.7,
                    "confidence": 0.8
                }
            ]
        })


# Simple rule-based extractor for fallback
class RuleBasedExtractor:
    """Rule-based memory extraction (no LLM required)"""
    
    PREFERENCE_PATTERNS = [
        "i like", "i love", "i prefer", "i enjoy",
        "i don't like", "i hate", "i dislike"
    ]
    
    FACT_PATTERNS = [
        "i am a", "i work as", "i live in",
        "my name is", "i have"
    ]
    
    TASK_PATTERNS = [
        "i need to", "i should", "i must",
        "remind me to", "don't forget"
    ]
    
    def extract(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """Extract using simple patterns"""
        memories = []
        
        for msg in messages:
            if msg["role"] != "user":
                continue
            
            content = msg["content"].lower()
            original = msg["content"]
            
            # Check for preferences
            for pattern in self.PREFERENCE_PATTERNS:
                if pattern in content:
                    memories.append({
                        "content": original,
                        "category": "preference",
                        "importance": 0.6,
                        "confidence": 0.7
                    })
                    break
            
            # Check for facts
            for pattern in self.FACT_PATTERNS:
                if pattern in content:
                    memories.append({
                        "content": original,
                        "category": "fact",
                        "importance": 0.7,
                        "confidence": 0.8
                    })
                    break
            
            # Check for tasks
            for pattern in self.TASK_PATTERNS:
                if pattern in content:
                    memories.append({
                        "content": original,
                        "category": "task",
                        "importance": 0.8,
                        "confidence": 0.9
                    })
                    break
        
        return memories
