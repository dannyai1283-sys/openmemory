"""Core memory interface for OC-Mem"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

from .config import MemoryConfig


@dataclass
class Memory:
    """Represents a single memory"""
    id: str
    content: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    category: str = "general"
    importance: float = 0.5
    created_at: str = None
    updated_at: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.metadata is None:
            self.metadata = {}
        if self.id is None:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique memory ID"""
        data = f"{self.content}:{self.user_id}:{self.created_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Memory":
        return cls(**data)


class OpenClawMemory:
    """Main memory interface for OpenClaw"""
    
    def __init__(self, user_id: str = None, agent_id: str = None, config: MemoryConfig = None):
        self.user_id = user_id
        self.agent_id = agent_id
        self.config = config or MemoryConfig()
        
        # Initialize backends
        self._init_backends()
    
    def _init_backends(self):
        """Initialize storage backends"""
        from ..backends.sqlite_backend import SQLiteBackend
        from ..backends.vector_backend import VectorBackend
        
        self.long_term = SQLiteBackend(self.config.long_term_path)
        self.vector_store = VectorBackend(self.config.vector_path) if self.config.use_vector else None
    
    def add(
        self,
        content: str,
        category: str = "general",
        importance: float = 0.5,
        session_id: str = None,
        metadata: Dict = None,
        merge_similar: bool = True
    ) -> Memory:
        """
        Add a new memory
        
        Args:
            content: The memory content
            category: Memory category (preference, fact, task, etc.)
            importance: Importance score (0-1)
            session_id: Optional session ID
            metadata: Additional metadata
            merge_similar: Whether to merge with similar existing memories
        
        Returns:
            Memory object
        """
        memory = Memory(
            id=None,
            content=content,
            user_id=self.user_id,
            agent_id=self.agent_id,
            session_id=session_id,
            category=category,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Check for similar memories if merge enabled
        if merge_similar:
            similar = self._find_similar(content, threshold=0.85)
            if similar:
                # Update existing memory
                existing = similar[0]
                existing.content = content  # Update with new info
                existing.importance = max(existing.importance, importance)
                existing.updated_at = datetime.now().isoformat()
                self.long_term.update(existing)
                return existing
        
        # Store in long-term memory
        self.long_term.add(memory)
        
        # Store in vector store if enabled
        if self.vector_store:
            self.vector_store.add(memory)
        
        return memory
    
    def search(
        self,
        query: str,
        category: str = None,
        limit: int = 5,
        semantic: bool = True,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Search memories
        
        Args:
            query: Search query
            category: Filter by category
            limit: Max results
            semantic: Use semantic search (requires vector store)
            threshold: Minimum similarity score
        
        Returns:
            List of matching memories with scores
        """
        results = []
        
        # Semantic search if enabled
        if semantic and self.vector_store:
            vector_results = self.vector_store.search(
                query, 
                user_id=self.user_id,
                limit=limit,
                threshold=threshold
            )
            results.extend(vector_results)
        
        # Keyword search fallback
        if not results:
            keyword_results = self.long_term.search(
                query,
                user_id=self.user_id,
                category=category,
                limit=limit
            )
            results.extend(keyword_results)
        
        # Sort by importance and recency
        results.sort(key=lambda x: (x.get("importance", 0.5), x.get("created_at", "")), reverse=True)
        
        return results[:limit]
    
    def get_context(
        self,
        session_id: str = None,
        max_tokens: int = 2000,
        categories: List[str] = None
    ) -> str:
        """
        Get relevant context for current session
        
        Args:
            session_id: Current session ID
            max_tokens: Maximum context tokens
            categories: Specific categories to include
        
        Returns:
            Formatted context string
        """
        # Get recent session memories
        memories = self.long_term.get_recent(
            user_id=self.user_id,
            session_id=session_id,
            limit=20
        )
        
        # Get high-importance user preferences
        preferences = self.long_term.get_by_category(
            user_id=self.user_id,
            category="preference",
            min_importance=0.7,
            limit=10
        )
        
        # Combine and deduplicate
        all_memories = {m.id: m for m in preferences + memories}
        sorted_memories = sorted(
            all_memories.values(),
            key=lambda m: (m.importance, m.updated_at),
            reverse=True
        )
        
        # Format as context string
        context_parts = []
        current_tokens = 0
        
        for mem in sorted_memories:
            mem_str = f"[{mem.category}] {mem.content}"
            # Rough token estimate
            mem_tokens = len(mem_str.split()) * 1.3
            
            if current_tokens + mem_tokens > max_tokens:
                break
            
            context_parts.append(mem_str)
            current_tokens += mem_tokens
        
        return "\n".join(context_parts) if context_parts else ""
    
    def extract_from_conversation(
        self,
        messages: List[Dict[str, str]],
        extract_preferences: bool = True,
        extract_facts: bool = True,
        extract_tasks: bool = True
    ) -> List[Memory]:
        """
        Extract memories from conversation using LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            extract_preferences: Extract user preferences
            extract_facts: Extract factual information
            extract_tasks: Extract tasks/action items
        
        Returns:
            List of extracted memories
        """
        from ..extractors.llm_extractor import LLMMemoryExtractor
        
        extractor = LLMMemoryExtractor()
        extracted = extractor.extract(
            messages,
            extract_preferences=extract_preferences,
            extract_facts=extract_facts,
            extract_tasks=extract_tasks
        )
        
        # Add extracted memories
        memories = []
        for item in extracted:
            mem = self.add(
                content=item["content"],
                category=item["category"],
                importance=item.get("importance", 0.5),
                metadata=item.get("metadata", {})
            )
            memories.append(mem)
        
        return memories
    
    def update(self, memory_id: str, content: str = None, metadata: Dict = None) -> Optional[Memory]:
        """Update an existing memory"""
        memory = self.long_term.get(memory_id)
        if not memory:
            return None
        
        if content:
            memory.content = content
        if metadata:
            memory.metadata.update(metadata)
        
        memory.updated_at = datetime.now().isoformat()
        self.long_term.update(memory)
        
        return memory
    
    def delete(self, memory_id: str = None, filters: Dict = None) -> int:
        """Delete memories by ID or filters"""
        if memory_id:
            return self.long_term.delete(memory_id)
        elif filters:
            return self.long_term.delete_by_filters(filters)
        return 0
    
    def _find_similar(self, content: str, threshold: float = 0.85) -> List[Memory]:
        """Find similar existing memories"""
        if not self.vector_store:
            return []
        
        results = self.vector_store.search(
            content,
            user_id=self.user_id,
            limit=1,
            threshold=threshold
        )
        
        similar = []
        for r in results:
            mem = self.long_term.get(r["id"])
            if mem:
                similar.append(mem)
        
        return similar
